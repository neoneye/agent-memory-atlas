"""Fixtures: a temporary state directory, a fake GitHub, and a repository builder.

No test in this suite touches the network. The fake client answers from a route
table and accounts for budgets exactly as the real one does, so the capacity and
budget tests exercise the same bookkeeping. The genuine byte-limit enforcement is
tested directly against the reader in `fetching`, where the sockets are.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import db
from config import Config, Limits
from fetching import BUDGET, Client, FetchError, NOT_FOUND, Response, api_url, raw_url
from db import budget_used, spend


class Harness:
    """A state directory, a config, and a database, cleaned up on teardown."""

    def __init__(self, *, atlas_repo: Path | None = None, **overrides):
        self.root = Path(tempfile.mkdtemp(prefix="triage-test-"))
        self.atlas_repo = atlas_repo or self._fake_atlas()
        self.config = Config(
            state_dir=self.root / "state",
            output_dir=self.root / "out",
            atlas_repo=self.atlas_repo,
            source_kind="file",
            source_file=self.root / "candidates.jsonl",
            policy_file=Path(__file__).resolve().parents[1] / "policy.json",
            limits=Limits(),
        )
        for key, value in overrides.items():
            setattr(self.config, key, value)
        self.connection = db.connect(self.config.db_path, create=True)

    def _fake_atlas(self) -> Path:
        root = self.root / "atlas"
        (root / "content" / "systems").mkdir(parents=True)
        (root / "content" / "systems" / "already-read.md").write_text(
            "---\n"
            'title: "Already Read"\n'
            'source_name: "someone/already-read"\n'
            "source_url: https://github.com/someone/already-read\n"
            "revision: 0123456789abcdef0123456789abcdef01234567\n"
            "analyzed_at: 2026-08-01\n"
            "---\n\nbody\n",
            encoding="utf-8",
        )
        return root

    def feed(self, records: list[dict]) -> Path:
        path = self.config.source_file
        path.write_text("\n".join(json.dumps(record) for record in records) + "\n",
                        encoding="utf-8")
        return path

    def close(self) -> None:
        try:
            self.connection.close()
        finally:
            shutil.rmtree(self.root, ignore_errors=True)


class FakeClient(Client):
    """A `Client` whose transport is a dictionary.

    Budget accounting, per-repository ceilings and the daily request ceiling run
    exactly as they do against the real API; only the socket is replaced.
    """

    def __init__(self, config, connection, day, routes: dict[str, object] | None = None):
        super().__init__(config, connection, day)
        self.routes: dict[str, object] = routes or {}
        self.calls: list[str] = []

    def route(self, url: str, payload, *, headers: dict[str, str] | None = None,
              accept: str | None = None) -> None:
        """Answer `url`; with `accept`, only requests sending that Accept header.
        The feed fetch asks one Contents URL twice — once for JSON metadata, once
        raw — so the two must be routable apart."""
        self.routes[(url, accept) if accept else url] = (payload, headers or {})

    def get(self, url, *, accept="application/vnd.github+json", max_bytes=None, cache=False,
            reject_binary=False, repo_budget=None, hops=0) -> Response:
        limit = max_bytes if max_bytes is not None else self.limits.blob_bytes
        self.calls.append(url)

        used = budget_used(self.connection, self.day, "github_requests")
        if used >= self.limits.requests_per_day:
            raise FetchError(BUDGET, f"daily GitHub request ceiling reached ({used})")
        if repo_budget is not None:
            reason = repo_budget.exhausted(self.limits)
            if reason:
                raise FetchError(BUDGET, reason)
        spend(self.connection, self.day, "github_requests", 1)
        if repo_budget is not None:
            repo_budget.requests += 1

        key = (url, accept) if (url, accept) in self.routes else url
        if key not in self.routes:
            raise FetchError(NOT_FOUND, f"{url}: HTTP 404 (no route)", status=404)
        payload, headers = self.routes[key]
        if isinstance(payload, FetchError):
            raise payload
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        if len(body) > limit:
            raise FetchError("too_large", f"{url}: exceeded {limit} decoded bytes")
        if reject_binary and b"\x00" in body[:8192]:
            raise FetchError("malformed", f"{url}: binary content")
        if repo_budget is not None:
            repo_budget.response_bytes += len(body)
        return Response(200, headers, body, url)


def repo_routes(client: FakeClient, name: str, *, commit: str, files: dict[str, str],
                stars: int = 12, contributors: list[dict] | None = None,
                pushed_at: str = "2026-09-01T00:00:00Z",
                created_at: str = "2024-01-01T00:00:00Z",
                owner_created_at: str = "2019-01-01T00:00:00Z",
                repo_id: int = 1000, truncated: bool = False,
                full_name: str | None = None, extra_paths: list[str] | None = None) -> None:
    """Wire one repository into the fake GitHub: metadata, tree and blobs."""
    owner, short = name.split("/", 1)
    full = full_name or name
    client.route(api_url("repos", owner, short), {
        "id": repo_id, "full_name": full, "default_branch": "main",
        "description": "a memory for agents", "language": "Python", "topics": ["memory", "agent"],
        "stargazers_count": stars, "forks_count": 3, "subscribers_count": 2,
        "open_issues_count": 7, "size": 900, "created_at": created_at, "pushed_at": pushed_at,
        "updated_at": pushed_at, "archived": False, "disabled": False, "fork": False,
        "license": {"spdx_id": "MIT"}, "has_issues": True,
        "owner": {"login": owner, "type": "User"},
    })
    client.route(api_url("repos", owner, short, "pulls", state="open", per_page=1), [{"id": 1}])
    client.route(
        api_url("repos", owner, short, "contributors", per_page=100, anon="0"),
        contributors if contributors is not None else [
            {"login": "alice", "type": "User", "contributions": 80},
            {"login": "bob", "type": "User", "contributions": 30},
            {"login": "dependabot[bot]", "type": "Bot", "contributions": 44},
        ],
    )
    client.route(api_url("repos", owner, short, "commits", sha="main", per_page=100), [
        {"sha": commit, "commit": {"author": {"date": "2026-09-01T00:00:00Z"}},
         "author": {"login": "alice"}},
        {"sha": "b" * 40, "commit": {"author": {"date": "2026-05-01T00:00:00Z"}},
         "author": {"login": "bob"}},
    ])
    client.route(
        api_url("repos", owner, short, "pulls", state="closed", per_page=30, sort="updated",
                direction="desc"),
        [{"merged_at": "2026-08-01T00:00:00Z", "user": {"login": "carol", "type": "User"}}],
    )
    client.route(api_url("users", owner), {
        "login": owner, "type": "User", "created_at": owner_created_at,
        "public_repos": 12, "followers": 30,
    })
    paths = list(files) + list(extra_paths or [])
    client.route(
        api_url("repos", owner, short, "git", "trees", commit, recursive="1"),
        {"sha": commit, "truncated": truncated,
         "tree": [{"path": path, "type": "blob"} for path in paths]},
    )
    for path, text in files.items():
        client.route(raw_url(name, commit, path), text.encode("utf-8"))
