import unittest
from unittest.mock import patch

from agent_39_extract_page import (
    HttpResponse,
    PageExtraction,
    extract_page,
    to_page_evidence,
)


DEMO_HTML = """
<!doctype html>
<html>
  <head><title>Python (programming language) - Wikipedia</title></head>
  <body>
    <nav class="site-nav">Home | Search | Menu | Search | Menu</nav>
    <footer class="page-footer">Copyright 2026 Example</footer>
    <div class="ad-banner">Buy cheap python courses</div>
    <main>
      <h1>Python (programming language)</h1>
      <p>Python is a high-level, general-purpose programming language
         that emphasizes code readability and simplicity.</p>
      <p>As of 2026, Python 3.14.6 is the latest stable release.</p>
    </main>
  </body>
</html>
"""


class ExtractPageTests(unittest.TestCase):
    def _fake_transport(self, body: str, status: int = 200, content_type: str = "text/html; charset=UTF-8"):
        def transport(url: str, timeout: float, max_bytes: int) -> HttpResponse:
            return HttpResponse(status, content_type, body)

        return transport

    def test_success_extracts_cleaned_body(self) -> None:
        result = extract_page(
            {"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"},
            transport=self._fake_transport(DEMO_HTML),
        )
        self.assertEqual(result.status, "success")
        self.assertEqual(result.title, "Python (programming language) - Wikipedia")
        self.assertIn("Python is a high-level", result.body_text or "")
        self.assertNotIn("Buy cheap python courses", result.body_text or "")
        self.assertNotIn("Copyright 2026", result.body_text or "")
        self.assertEqual(result.source_type, "web")
        self.assertEqual(result.http_status, 200)

    def test_search_snippet_is_never_treated_as_body(self) -> None:
        search_result = {
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "snippet": "This snippet is only a search summary and must not enter body_text.",
        }
        result = extract_page(search_result, transport=self._fake_transport(DEMO_HTML))
        self.assertEqual(result.status, "success")
        self.assertNotIn("This snippet is only a search summary", result.body_text or "")

    def test_invalid_url_is_rejected(self) -> None:
        result = extract_page(
            {"url": "file:///etc/passwd"},
            transport=self._fake_transport(DEMO_HTML),
        )
        self.assertEqual(result.status, "invalid_url")

    def test_timeout_has_explicit_status(self) -> None:
        def transport(url: str, timeout: float, max_bytes: int) -> HttpResponse:
            raise TimeoutError("timeout")

        result = extract_page({"url": "https://example.com/page"}, transport=transport)
        self.assertEqual(result.status, "timeout")

    def test_http_error_has_explicit_status(self) -> None:
        def transport(url: str, timeout: float, max_bytes: int) -> HttpResponse:
            raise OSError("connection refused")

        result = extract_page({"url": "https://example.com/page"}, transport=transport)
        self.assertEqual(result.status, "http_error")

    def test_non_2xx_status_has_explicit_status(self) -> None:
        result = extract_page(
            {"url": "https://example.com/missing"},
            transport=self._fake_transport("not found", status=404),
        )
        self.assertEqual(result.status, "http_error")
        self.assertEqual(result.http_status, 404)

    def test_empty_body_has_explicit_status(self) -> None:
        result = extract_page(
            {"url": "https://example.com/empty"},
            transport=self._fake_transport(""),
        )
        self.assertEqual(result.status, "empty")

    def test_non_html_has_explicit_status(self) -> None:
        result = extract_page(
            {"url": "https://example.com/data.json"},
            transport=self._fake_transport('{"ok": true}', content_type="application/json"),
        )
        self.assertEqual(result.status, "not_html")

    def test_parse_error_has_explicit_status(self) -> None:
        def transport(url: str, timeout: float, max_bytes: int) -> HttpResponse:
            return HttpResponse(200, "text/html; charset=UTF-8", "<html><body>")

        with patch("agent_39_extract_page.BeautifulSoup", side_effect=ValueError("bad markup")):
            result = extract_page({"url": "https://example.com/bad"}, transport=transport)
        self.assertEqual(result.status, "parse_error")

    def test_success_can_become_page_evidence(self) -> None:
        extraction = extract_page(
            {"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"},
            transport=self._fake_transport(DEMO_HTML),
        )
        evidence = to_page_evidence(
            extraction,
            evidence_id="demo",
            source_quality="reference",
            published_at="2026-01-01",
            claim="python latest release",
            extracted_at="2026-08-05",
        )
        self.assertEqual(evidence.evidence_id, "demo")
        self.assertEqual(evidence.url, extraction.url)
        self.assertEqual(evidence.extracted_at, "2026-08-05")

    def test_failed_extraction_cannot_become_evidence(self) -> None:
        failed = PageExtraction("timeout", "https://example.com")
        with self.assertRaises(ValueError):
            to_page_evidence(failed)


if __name__ == "__main__":
    unittest.main()
