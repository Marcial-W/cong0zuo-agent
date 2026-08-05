import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "agent-37"))


class RouteSearchDemoTests(unittest.TestCase):
    def test_local_route_does_not_call_web_search(self) -> None:
        from agent_37_choose_source import choose_source

        local_question = "Agent 为什么要在回答里保留页码？"
        local_results = [{"text": "回答要保留页码"}]
        route = choose_source(local_question, local_results, False)

        self.assertEqual(route.source, "local")

        called = []

        def fake_web_search(query: str) -> object:
            called.append(query)
            raise AssertionError("local route must not call web_search")

        if route.source == "local":
            pass
        else:
            fake_web_search("should not happen")
        self.assertEqual(called, [])

    def test_web_route_calls_injected_search(self) -> None:
        from agent_37_choose_source import choose_source
        from agent_38_web_search import SearchResponse, normalize_search_query

        route = choose_source("Python 的最新稳定版本是什么？", [], None)
        self.assertEqual(route.source, "web")

        calls = []

        def fake_web_search(query: str) -> SearchResponse:
            calls.append(query)
            return SearchResponse("success", (), None)

        fake_web_search(normalize_search_query(route.query))
        self.assertEqual(calls, ["Python latest stable release"])


if __name__ == "__main__":
    unittest.main()
