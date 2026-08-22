#!/usr/bin/env python3
"""Tests for the MS Learn transcript fetcher."""

import io
import unittest
import urllib.error
from unittest import mock

import fetch_transcript


class Response:
    """Minimal context-managed HTTP response for fetch tests."""

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.payload


class FetchJsonTests(unittest.TestCase):
    def test_retries_timeout_then_returns_json(self):
        with (
            mock.patch.object(
                fetch_transcript.urllib.request,
                "urlopen",
                side_effect=[
                    TimeoutError("timed out"),
                    Response(b'{"status": "ok"}'),
                ],
            ) as urlopen,
            mock.patch.object(fetch_transcript.time, "sleep") as sleep,
        ):
            result = fetch_transcript.fetch_json("https://example.com/data")

        self.assertEqual({"status": "ok"}, result)
        self.assertEqual(2, urlopen.call_count)
        sleep.assert_called_once_with(fetch_transcript.RETRY_DELAY_SECONDS)

    def test_does_not_retry_non_transient_http_error(self):
        error = urllib.error.HTTPError(
            "https://example.com/data",
            404,
            "Not Found",
            {},
            io.BytesIO(),
        )
        with (
            mock.patch.object(
                fetch_transcript.urllib.request,
                "urlopen",
                side_effect=error,
            ) as urlopen,
            mock.patch.object(fetch_transcript.time, "sleep") as sleep,
            self.assertRaises(urllib.error.HTTPError),
        ):
            fetch_transcript.fetch_json("https://example.com/data")

        urlopen.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
