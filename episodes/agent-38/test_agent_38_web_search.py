import unittest

from agent_38_web_search import (
    SearchResult,
    build_search_url,
    clean_snippet,
    normalize_search_query,
    web_search,
)


class WebSearchTests(unittest.TestCase):
    def test_success_payload_is_standardized(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            self.assertIn("action=query", url)
            self.assertIn("srlimit=5", url)
            return {
                "query": {
                    "search": [
                        {
                            "title": "Python (programming language)",
                            "snippet": '<span class="searchmatch">Python</span> 3.14.6',
                        }
                    ]
                }
            }

        response = web_search("Python latest stable release", transport=fake_transport)
        self.assertEqual(response.status, "success")
        self.assertEqual(len(response.results), 1)
        result = response.results[0]
        self.assertEqual(result.title, "Python (programming language)")
        self.assertEqual(result.url, "https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.assertEqual(result.snippet, "Python 3.14.6")
        self.assertEqual(result.source_type, "web")
        self.assertEqual(result.rank, 1)

    def test_timeout_has_explicit_status(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            raise TimeoutError("timeout")

        response = web_search("query", transport=fake_transport)
        self.assertEqual(response.status, "timeout")

    def test_http_error_has_explicit_status(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            raise OSError("connection refused")

        response = web_search("query", transport=fake_transport)
        self.assertEqual(response.status, "http_error")

    def test_empty_result_has_explicit_status(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            return {"query": {"search": []}}

        response = web_search("query", transport=fake_transport)
        self.assertEqual(response.status, "empty")

    def test_missing_title_is_invalid(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            return {"query": {"search": [{"snippet": "no title"}]}}

        response = web_search("query", transport=fake_transport)
        self.assertEqual(response.status, "invalid")
        self.assertIn("title", response.message or "")

    def test_missing_snippet_is_invalid(self) -> None:
        def fake_transport(url: str, timeout: float) -> object:
            return {"query": {"search": [{"title": "Only title"}]}}

        response = web_search("query", transport=fake_transport)
        self.assertEqual(response.status, "invalid")
        self.assertIn("snippet", response.message or "")

    def test_top_k_is_bounded(self) -> None:
        url = build_search_url("query", top_k=99)
        self.assertIn("srlimit=10", url)

    def test_clean_snippet_strips_html_and_entities(self) -> None:
        self.assertEqual(clean_snippet("A <b>B</b> &amp; C"), "A B & C")

    def test_fixed_question_maps_to_stable_query(self) -> None:
        self.assertEqual(
            normalize_search_query("Python 的最新稳定版本是什么？"),
            "Python latest stable release",
        )

    def test_invalid_top_k_returns_invalid(self) -> None:
        response = web_search("query", top_k="bad")
        self.assertEqual(response.status, "invalid")


if __name__ == "__main__":
    unittest.main()
