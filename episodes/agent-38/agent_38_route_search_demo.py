import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for episode_name in ("agent-33", "agent-36", "agent-37", "agent-38"):
    sys.path.insert(0, str(ROOT / episode_name))

from agent_33_document_chunks import chunks_from_pdf, retrieve_chunks
from agent_36_end_to_end_pdf_qa import normalize_question
from agent_37_choose_source import SourceRoute, choose_source
from agent_38_web_search import SearchResponse, normalize_search_query, web_search


def _route_to_dict(route: SourceRoute) -> dict[str, object]:
    return {
        "source": route.source,
        "reason": route.reason,
        "query": route.query,
        "local_match_count": route.local_match_count,
        "requires_freshness": route.requires_freshness,
    }


def _search_to_dict(response: SearchResponse) -> dict[str, object]:
    return {
        "status": response.status,
        "message": response.message,
        "results": [asdict(item) for item in response.results],
    }


def run_route_search_demo(
    sample_pdf: Path,
    web_search_fn=web_search,
) -> dict[str, object]:
    """Run the fixed local and web demos used by the video."""
    chunks = chunks_from_pdf(sample_pdf)

    local_question = "Agent 为什么要在回答里保留页码？"
    local_results = retrieve_chunks(normalize_question(local_question), chunks, top_k=5)
    local_route = choose_source(local_question, local_results, False)
    if local_route.source != "local":
        raise AssertionError(f"Expected local route, got {local_route.source}")

    web_question = "Python 的最新稳定版本是什么？"
    web_route = choose_source(web_question, [], None)
    if web_route.source != "web":
        raise AssertionError(f"Expected web route, got {web_route.source}")
    search_response = web_search_fn(normalize_search_query(web_question))
    if search_response.status != "success":
        raise AssertionError(
            f"Expected successful search, got {search_response.status}: {search_response.message}"
        )
    if not search_response.results:
        raise AssertionError("Expected at least one search result.")

    return {
        "local_route": _route_to_dict(local_route),
        "local_results": [asdict(item) for item in local_results],
        "web_route": _route_to_dict(web_route),
        "search_query": normalize_search_query(web_question),
        "web_search": _search_to_dict(search_response),
    }


if __name__ == "__main__":
    sample = ROOT / "agent-36" / "samples" / "sample_qa.pdf"
    if not sample.exists():
        from build_qa_samples import build_samples

        build_samples(ROOT / "agent-36" / "samples")
    result = run_route_search_demo(sample)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(result, ensure_ascii=False, indent=2))
