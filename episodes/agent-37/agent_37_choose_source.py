from dataclasses import dataclass
from typing import Literal


SourceType = Literal["local", "web", "error"]

FRESHNESS_WORDS = (
    "最新",
    "latest",
    "current",
    "now",
    "目前",
    "现在的",
)


@dataclass(frozen=True)
class SourceRoute:
    """Structured routing decision that tests and UI can read directly."""

    source: SourceType
    reason: str
    query: str
    local_match_count: int
    requires_freshness: bool


def detect_freshness_request(question: str) -> bool:
    """Return True when the question explicitly asks for current information."""
    lowered = question.lower()
    return any(word in lowered for word in FRESHNESS_WORDS)


def _safe_local_count(local_results: object) -> int | None:
    if local_results is None:
        return None
    if not isinstance(local_results, (list, tuple)):
        return None
    return len(local_results)


def choose_source(
    question: str,
    local_results: object,
    requires_freshness: bool | None = None,
) -> SourceRoute:
    """Route a question to local or web using explicit, testable rules."""
    query = question.strip()
    if not query:
        return SourceRoute("error", "question_empty", question, 0, False)

    if requires_freshness is None:
        requires_freshness = detect_freshness_request(query)

    local_count = _safe_local_count(local_results)
    if local_count is None:
        return SourceRoute("error", "route_config_invalid", query, 0, requires_freshness)

    if requires_freshness:
        return SourceRoute(
            source="web",
            reason="requires_freshness=true",
            query=query,
            local_match_count=local_count,
            requires_freshness=True,
        )

    if local_count > 0:
        return SourceRoute(
            source="local",
            reason="local_match_count>=1 and not requires_freshness",
            query=query,
            local_match_count=local_count,
            requires_freshness=False,
        )

    return SourceRoute(
        source="web",
        reason="local_match_count=0",
        query=query,
        local_match_count=0,
        requires_freshness=False,
    )


if __name__ == "__main__":
    print(choose_source("本地资料里有答案吗", [{"text": "答案"}], False))
    print(choose_source("Python 的最新稳定版本是什么？", [], True))
