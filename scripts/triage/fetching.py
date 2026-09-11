"""Read-only HTTP against GitHub, with the byte ceilings enforced at the socket.

Named `fetching` rather than `http` on purpose: this directory is `sys.path[0]`
when the CLI runs, and a module called `http` here would shadow the standard
library package that `urllib` itself imports.

Three properties this module exists to hold:

* **Nothing is trusted about size.** `Content-Length` is a claim by the server.
  The reader counts the bytes it actually reads and stops, and counts the bytes
  that come *out* of the decompressor separately, so a small compressed body
  cannot expand past the decoded ceiling.
* **Credentials do not travel.** The token goes to `api.github.com` and nowhere
  else. Redirects are not followed automatically; each hop is re-validated
  against the host allow-list and the header is dropped if the host changes.
* **Exhausted budgets persist.** A rate-limit window is written to the database
  with its retry time, so the next run waits rather than rediscovering the limit
  by spending more requests on it.
"""

from __future__ import annotations

import gzip
import socket
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import zlib
from dataclasses import dataclass, field
from typing import Any

from config import Config
from db import budget_used, spend
from util import dumps, iso, loads, parse_iso, plus, sha256_hex, utc_now

# Everything else is refused, including hosts that a feed record might name.
TRUSTED_HOSTS = frozenset({
    "api.github.com",
    "raw.githubusercontent.com",
    "objects.githubusercontent.com",
    "codeload.github.com",
})
AUTH_HOSTS = frozenset({"api.github.com"})

RATE_LIMIT = "rate_limit"
NOT_FOUND = "not_found"
FORBIDDEN = "forbidden"
TRANSIENT = "transient"
TOO_LARGE = "too_large"
MALFORMED = "malformed"
UNAVAILABLE = "unavailable"
BUDGET = "budget_exceeded"
UNTRUSTED = "untrusted_host"


class FetchError(RuntimeError):
    """A failure with a category, because the categories mean different things.

    A 404 is not evidence that an author is a spammer. A 429 is not evidence
    that a project is poor. Only the caller that knows which question it asked
    can decide what a category means, so the category travels with the error.
    """

    def __init__(self, category: str, message: str, *, retry_at: str | None = None,
                 status: int | None = None):
        super().__init__(message)
        self.category = category
        self.retry_at = retry_at
        self.status = status


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str
    from_cache: bool = False

    def json(self) -> Any:
        try:
            return loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise FetchError(MALFORMED, f"{self.url}: not JSON ({error})") from error

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass
class RepoBudget:
    """Per-repository ceilings. One of these per assessment; when it is spent the
    assessment ends with whatever coverage it reached, which is a finding of
    `unknown`, not a finding of absence."""

    requests: int = 0
    response_bytes: int = 0
    source_bytes: int = 0
    blobs: int = 0
    notes: list[str] = field(default_factory=list)

    def exhausted(self, limits) -> str | None:
        if self.requests >= limits.requests_per_repo:
            return "per-repository request ceiling"
        if self.response_bytes >= limits.response_bytes_per_repo:
            return "per-repository response-byte ceiling"
        return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Hand the redirect back to the caller instead of following it silently."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        raise _Redirect(newurl, code)


class _Redirect(Exception):
    def __init__(self, location: str, code: int):
        super().__init__(location)
        self.location = location
        self.code = code


def _check_host(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https":
        raise FetchError(UNTRUSTED, f"refusing non-https URL: {url}")
    host = (parsed.hostname or "").lower()
    if host not in TRUSTED_HOSTS:
        raise FetchError(UNTRUSTED, f"refusing host outside the GitHub allow-list: {host}")
    return host


def _read_bounded(stream, *, max_bytes: int, encoding: str | None, url: str,
                  reject_binary: bool) -> bytes:
    """Read with two counters: raw bytes off the wire and decoded bytes out.

    Chunked transfer, a missing `Content-Length`, a lying one, and a compression
    bomb all land on the same ceiling because neither counter comes from a header.
    """
    raw_limit = max_bytes * 8 if encoding else max_bytes
    decoder = None
    if encoding == "gzip":
        decoder = zlib.decompressobj(zlib.MAX_WBITS | 16)
    elif encoding == "deflate":
        decoder = zlib.decompressobj()

    out = bytearray()
    raw_total = 0
    while True:
        chunk = stream.read(64 * 1024)
        if not chunk:
            break
        raw_total += len(chunk)
        if raw_total > raw_limit:
            raise FetchError(TOO_LARGE, f"{url}: exceeded {raw_limit} raw bytes")
        piece = decoder.decompress(chunk, max_bytes + 1 - len(out)) if decoder else chunk
        out += piece
        if len(out) > max_bytes:
            raise FetchError(TOO_LARGE, f"{url}: exceeded {max_bytes} decoded bytes")
        if reject_binary and b"\x00" in out[:8192]:
            raise FetchError(MALFORMED, f"{url}: binary content where text was expected")
    if decoder is not None:
        tail = decoder.flush()
        out += tail
        if len(out) > max_bytes:
            raise FetchError(TOO_LARGE, f"{url}: exceeded {max_bytes} decoded bytes after flush")
    return bytes(out)


class Client:
    """A bounded GitHub reader tied to one database connection and one civil day."""

    def __init__(self, config: Config, connection: sqlite3.Connection, day: str,
                 log=None):
        self.config = config
        self.connection = connection
        self.day = day
        self.limits = config.limits
        self.log = log or (lambda *_args, **_kwargs: None)
        self.opener = urllib.request.build_opener(_NoRedirect)
        self.opener.addheaders = []

    # --- rate limits ------------------------------------------------------
    def _blocked_until(self, host: str) -> str | None:
        row = self.connection.execute(
            "SELECT retry_at FROM rate_limit WHERE host = ?", (host,)
        ).fetchone()
        if row is None:
            return None
        if parse_iso(row["retry_at"]) > utc_now():
            return row["retry_at"]
        self.connection.execute("DELETE FROM rate_limit WHERE host = ?", (host,))
        return None

    def _record_limit(self, host: str, retry_at: str, reason: str) -> None:
        self.connection.execute(
            "INSERT INTO rate_limit(host, retry_at, reason, recorded_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(host) DO UPDATE SET retry_at = excluded.retry_at, "
            "reason = excluded.reason, recorded_at = excluded.recorded_at",
            (host, retry_at, reason, iso(utc_now())),
        )

    @staticmethod
    def _retry_at(headers: dict[str, str]) -> str:
        now = utc_now()
        after = headers.get("retry-after")
        if after:
            try:
                return iso(plus(now, seconds=min(float(after), 24 * 3600)))
            except ValueError:
                pass
        reset = headers.get("x-ratelimit-reset")
        if reset:
            try:
                from datetime import datetime, timezone as _tz
                return iso(datetime.fromtimestamp(int(reset), _tz.utc))
            except (ValueError, OverflowError, OSError):
                pass
        return iso(plus(now, seconds=900))

    # --- the one request path --------------------------------------------
    def get(self, url: str, *, accept: str = "application/vnd.github+json",
            max_bytes: int | None = None, cache: bool = False,
            reject_binary: bool = False, repo_budget: RepoBudget | None = None,
            hops: int = 0) -> Response:
        limit = max_bytes if max_bytes is not None else self.limits.blob_bytes
        host = _check_host(url)

        blocked = self._blocked_until(host)
        if blocked:
            raise FetchError(RATE_LIMIT, f"{host} rate-limited until {blocked}", retry_at=blocked)

        if cache:
            hit = self._cache_get(url)
            if hit is not None:
                return hit

        used = budget_used(self.connection, self.day, "github_requests")
        if used >= self.limits.requests_per_day:
            raise FetchError(BUDGET, f"daily GitHub request ceiling reached ({used})")
        if repo_budget is not None:
            reason = repo_budget.exhausted(self.limits)
            if reason:
                raise FetchError(BUDGET, reason)

        request = urllib.request.Request(url, method="GET")
        request.add_header("Accept", accept)
        request.add_header("User-Agent", self.config.user_agent)
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        request.add_header("Accept-Encoding", "gzip")
        if self.config.github_token and host in AUTH_HOSTS:
            request.add_header("Authorization", f"Bearer {self.config.github_token}")

        # A failed request still cost a request. Budgets that only count
        # successes are budgets a failing endpoint can spend without limit.
        spend(self.connection, self.day, "github_requests", 1)
        if repo_budget is not None:
            repo_budget.requests += 1

        stream = None
        try:
            stream = self.opener.open(
                request, timeout=self.limits.read_timeout
            )
            headers = {key.lower(): value for key, value in stream.headers.items()}
            body = _read_bounded(
                stream,
                max_bytes=limit,
                encoding=headers.get("content-encoding", "").lower() or None,
                url=url,
                reject_binary=reject_binary,
            )
            response = Response(stream.status, headers, body, url)
        except _Redirect as redirect:
            if hops >= 3:
                raise FetchError(TRANSIENT, f"{url}: too many redirects") from None
            target = urllib.parse.urljoin(url, redirect.location)
            # Re-validated from scratch, and the Authorization header is simply
            # not carried across: it is rebuilt above only for AUTH_HOSTS.
            return self.get(
                target, accept=accept, max_bytes=max_bytes, cache=cache,
                reject_binary=reject_binary, repo_budget=repo_budget, hops=hops + 1,
            )
        except urllib.error.HTTPError as error:
            headers = {key.lower(): value for key, value in (error.headers or {}).items()}
            try:
                error.read()   # drain so the connection is not left half-open
            except Exception:  # noqa: BLE001 - draining is best effort
                pass
            finally:
                error.close()
            status = error.code
            if status in (403, 429):
                remaining = headers.get("x-ratelimit-remaining")
                secondary = "secondary rate limit" in (error.reason or "").lower()
                if remaining == "0" or "retry-after" in headers or status == 429 or secondary:
                    retry_at = self._retry_at(headers)
                    self._record_limit(host, retry_at, f"HTTP {status}")
                    raise FetchError(RATE_LIMIT, f"{url}: HTTP {status}", retry_at=retry_at,
                                     status=status) from None
                raise FetchError(FORBIDDEN, f"{url}: HTTP 403 (permissions)", status=403) from None
            if status == 404:
                raise FetchError(NOT_FOUND, f"{url}: HTTP 404", status=404) from None
            if status == 409:
                raise FetchError(UNAVAILABLE, f"{url}: HTTP 409 (empty repository)",
                                 status=409) from None
            if status in (451,):
                raise FetchError(UNAVAILABLE, f"{url}: HTTP 451", status=451) from None
            raise FetchError(TRANSIENT, f"{url}: HTTP {status}", status=status) from None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError,
                gzip.BadGzipFile, zlib.error) as error:
            raise FetchError(TRANSIENT, f"{url}: {error}") from None
        finally:
            if stream is not None:
                stream.close()

        if repo_budget is not None:
            repo_budget.response_bytes += len(response.body)
        if cache:
            self._cache_put(response)
        return response

    # --- metadata-only cache ---------------------------------------------
    #
    # Source blobs are deliberately not cached. They are read, assessed, and
    # dropped; what survives an assessment is paths, hashes and short excerpts.

    def _cache_get(self, url: str) -> Response | None:
        key = sha256_hex(url.encode("utf-8"))
        row = self.connection.execute(
            "SELECT * FROM http_cache WHERE url_hash = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        age_days = (utc_now() - parse_iso(row["fetched_at"])).total_seconds() / 86400
        if age_days > self.limits.cache_ttl_days:
            self.connection.execute("DELETE FROM http_cache WHERE url_hash = ?", (key,))
            return None
        return Response(int(row["status"]), {"x-cache": "hit"}, row["body"], url, from_cache=True)

    def _cache_put(self, response: Response) -> None:
        if len(response.body) > 1024 * 1024:
            return
        self.connection.execute(
            "INSERT OR REPLACE INTO http_cache(url_hash, url, etag, fetched_at, status, bytes, body) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                sha256_hex(response.url.encode("utf-8")),
                response.url,
                response.headers.get("etag"),
                iso(utc_now()),
                response.status,
                len(response.body),
                response.body,
            ),
        )


def api_url(*segments: str, **query: Any) -> str:
    """Build an api.github.com URL from validated pieces.

    Segments are percent-encoded here rather than interpolated, so a name that
    slipped past validation still cannot add a path or a host.
    """
    path = "/".join(urllib.parse.quote(str(segment), safe="") for segment in segments)
    url = f"https://api.github.com/{path}"
    filtered = {key: value for key, value in query.items() if value is not None}
    if filtered:
        url += "?" + urllib.parse.urlencode(filtered)
    return url


def raw_url(repo: str, ref: str, path: str) -> str:
    owner, name = repo.split("/", 1)
    pieces = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return (
        f"https://raw.githubusercontent.com/"
        f"{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(name, safe='')}/"
        f"{urllib.parse.quote(ref, safe='')}/{pieces}"
    )
