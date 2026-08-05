import unittest

from agent_37_choose_source import choose_source, detect_freshness_request


class ChooseSourceTests(unittest.TestCase):
    def test_local_match_and_no_freshness_route_to_local(self) -> None:
        route = choose_source(
            "Agent 为什么要在回答里保留页码？",
            [{"text": "回答要保留页码"}],
            False,
        )
        self.assertEqual(route.source, "local")
        self.assertEqual(route.reason, "local_match_count>=1 and not requires_freshness")
        self.assertEqual(route.local_match_count, 1)
        self.assertFalse(route.requires_freshness)

    def test_no_local_match_routes_to_web(self) -> None:
        route = choose_source("Python 是什么？", [], False)
        self.assertEqual(route.source, "web")
        self.assertEqual(route.reason, "local_match_count=0")

    def test_freshness_request_routes_to_web_even_with_local_match(self) -> None:
        route = choose_source("Python 的最新稳定版本是什么？", [{"text": "旧资料"}], None)
        self.assertEqual(route.source, "web")
        self.assertEqual(route.reason, "requires_freshness=true")
        self.assertTrue(route.requires_freshness)
        self.assertEqual(route.local_match_count, 1)

    def test_empty_question_is_rejected_with_error_status(self) -> None:
        route = choose_source("   ", [], False)
        self.assertEqual(route.source, "error")
        self.assertEqual(route.reason, "question_empty")

    def test_invalid_local_results_returns_config_error(self) -> None:
        route = choose_source("问题", None, False)
        self.assertEqual(route.source, "error")
        self.assertEqual(route.reason, "route_config_invalid")

    def test_freshness_detector_recognizes_chinese_marker(self) -> None:
        self.assertTrue(detect_freshness_request("Python 的最新稳定版本是什么？"))
        self.assertFalse(detect_freshness_request("Agent 为什么保留页码？"))


if __name__ == "__main__":
    unittest.main()
