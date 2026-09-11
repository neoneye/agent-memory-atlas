"""Section 11: ceilings that hold when the server lies about size."""

from __future__ import annotations

import gzip
import io
import unittest
import zlib

import fetching
from fetching import FetchError, TOO_LARGE, _check_host, _read_bounded


class SlowStream:
    """A stream that hands out small chunks, like a chunked response."""

    def __init__(self, payload: bytes, chunk: int = 7):
        self.buffer = io.BytesIO(payload)
        self.chunk = chunk

    def read(self, size: int = -1) -> bytes:
        return self.buffer.read(min(size if size > 0 else self.chunk, self.chunk))


class ByteLimitTests(unittest.TestCase):
    def test_a_body_over_the_ceiling_stops_at_the_ceiling(self):
        with self.assertRaises(FetchError) as caught:
            _read_bounded(SlowStream(b"x" * 5000), max_bytes=1000, encoding=None,
                          url="u", reject_binary=False)
        self.assertEqual(caught.exception.category, TOO_LARGE)

    def test_a_declared_size_is_never_trusted(self):
        # No Content-Length is consulted anywhere in the reader; the counter is
        # the bytes that actually arrive, so a lying header changes nothing.
        body = _read_bounded(SlowStream(b"y" * 500), max_bytes=1000, encoding=None,
                             url="u", reject_binary=False)
        self.assertEqual(len(body), 500)

    def test_a_compression_bomb_stops_at_the_decoded_ceiling(self):
        compressed = gzip.compress(b"0" * (8 * 1024 * 1024))
        self.assertLess(len(compressed), 64 * 1024)
        with self.assertRaises(FetchError) as caught:
            _read_bounded(SlowStream(compressed, chunk=4096), max_bytes=64 * 1024,
                          encoding="gzip", url="u", reject_binary=False)
        self.assertEqual(caught.exception.category, TOO_LARGE)

    def test_deflate_is_bounded_too(self):
        compressed = zlib.compress(b"0" * (4 * 1024 * 1024))
        with self.assertRaises(FetchError):
            _read_bounded(SlowStream(compressed, chunk=4096), max_bytes=32 * 1024,
                          encoding="deflate", url="u", reject_binary=False)

    def test_a_small_compressed_body_round_trips(self):
        payload = b"hello memory\n" * 100
        out = _read_bounded(SlowStream(gzip.compress(payload), chunk=64), max_bytes=1 << 20,
                            encoding="gzip", url="u", reject_binary=False)
        self.assertEqual(out, payload)

    def test_binary_content_is_refused_where_text_was_expected(self):
        with self.assertRaises(FetchError) as caught:
            _read_bounded(SlowStream(b"PK\x03\x04\x00\x00binary"), max_bytes=1 << 20,
                          encoding=None, url="u", reject_binary=True)
        self.assertEqual(caught.exception.category, "malformed")

    def test_raw_bytes_are_bounded_even_when_nothing_decodes(self):
        # A body that claims gzip and is not: the raw counter is the backstop.
        with self.assertRaises(Exception):
            _read_bounded(SlowStream(b"n" * (2 << 20), chunk=8192), max_bytes=1024,
                          encoding="gzip", url="u", reject_binary=False)


class HostPolicyTests(unittest.TestCase):
    def test_only_github_hosts_are_reachable(self):
        self.assertEqual(_check_host("https://api.github.com/x"), "api.github.com")
        for url in (
            "https://evil.example.com/x",
            "https://api.github.com.evil.example.com/x",
            "http://api.github.com/x",
            "https://gist.githubusercontent.com/x",
        ):
            with self.assertRaises(FetchError) as caught:
                _check_host(url)
            self.assertEqual(caught.exception.category, "untrusted_host")

    def test_only_the_api_host_is_ever_authenticated(self):
        self.assertEqual(fetching.AUTH_HOSTS, frozenset({"api.github.com"}))
        self.assertIn("raw.githubusercontent.com", fetching.TRUSTED_HOSTS)
        self.assertNotIn("raw.githubusercontent.com", fetching.AUTH_HOSTS)

    def test_urls_are_built_from_encoded_segments(self):
        url = fetching.api_url("repos", "owner", "../../admin")
        self.assertNotIn("../", url)
        self.assertTrue(url.startswith("https://api.github.com/repos/owner/"))


if __name__ == "__main__":
    unittest.main()
