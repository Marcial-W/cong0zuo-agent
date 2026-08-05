import html
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Callable, Literal


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "MarcialAgentLab/0.1 (educational demo)"
MAX_TOP_K = 10

SearchStatus = Literal["success", "timeout", "http_error", "empty", "invalid"]
Transport = Callable[[str, float], object]


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    source_type: Literal["web"] = "web"
    rank: int = 0


@dataclass(frozen=True)
class SearchResponse:
    status: SearchStatus
    results: tuple[SearchResult, ...] = ()
    message: str | None = None


def normalize_search_query(question: str) -> str:
    """Map the fixed Chinese demo question to a stable English search query."""
    aliases = {
        "Python 的最新稳定版本是什么？": "Python latest stable release",
        "Python 的最新版本是什么？": "Python latest stable release",
    }
    stripped = question.strip()
    return aliases.get(stripped, stripped)


def _clamp_top_k(top_k: int | None) -> int:
    if top_k is None:
        return 5
    return max(1, min(int(top_k), MAX_TOP_K))


def build_search_url(query: str, top_k: int = 5) -> str:
    params = {
        "action": "query",
        "list": "search",
        "format": "json",
        "utf8": "1",
        "srsearch": query,
        "srlimit": str(_clamp_top_k(top_k)),
    }
    return f"{WIKIPEDIA_API}?{urllib.parse.urlencode(params)}"


def default_transport(url: str, timeout_seconds: float) -> object:
    """Call the Wikipedia Search API with an identifying User-Agent."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_snippet(raw: str) -> str:
    """Strip HTML highlighting and decode entities from the API snippet."""
    without_tags = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(without_tags).strip()


def build_result_url(title: str) -> str:
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="/():._-")
    return f"https://en.wikipedia.org/wiki/{encoded}"


def _valid_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _parse_results(payload: object) -> SearchResponse:
    if not isinstance(payload, dict):
        return SearchResponse("invalid", message="搜索服务返回的不是 JSON 对象。")

    query = payload.get("query")
    if not isinstance(query, dict) or not isinstance(query.get("search"), list):
        return SearchResponse("invalid", message="搜索返回缺少 query.search 列表。")

    results: list[SearchResult] = []
    for rank, raw in enumerate(query["search"], start=1):
        if not isinstance(raw, dict):
            return SearchResponse("invalid", message=f"第 {rank} 条结果不是对象。")

        title = raw.get("title")
        snippet = raw.get("snippet")
        if not isinstance(title, str) or not title.strip():
            return SearchResponse("invalid", message=f"第 {rank} 条结果缺少 title。")
        if not isinstance(snippet, str) or not snippet.strip():
            return SearchResponse("invalid", message=f"第 {rank} 条结果缺少 snippet。")

        url = build_result_url(title)
        if not _valid_url(url):
            return SearchResponse("invalid", message=f"第 {rank} 条结果生成非法 URL。")

        results.append(
            SearchResult(
                title=title.strip(),
                url=url,
                snippet=clean_snippet(snippet),
                source_type="web",
                rank=rank,
            )
        )

    if not results:
        return SearchResponse("empty", message="搜索没有返回结果。")
    return SearchResponse("success", tuple(results))


def web_search(
    query: str,
    transport: Transport = default_transport,
    top_k: int = 5,
    timeout_seconds: float = 8,
) -> SearchResponse:
    """Search the live Wikipedia API and normalize the response."""
    clean_query = query.strip()
    if not clean_query:
        return SearchResponse("invalid", message="搜索查询不能为空。")

    try:
        top_k = _clamp_top_k(top_k)
    except (TypeError, ValueError):
        return SearchResponse("invalid", message="top_k 必须是 1-10 的整数。")

    url = build_search_url(clean_query, top_k)
    try:
        payload = transport(url, float(timeout_seconds))
    except (TimeoutError, socket.timeout):
        return SearchResponse("timeout", message=f"搜索超过 {timeout_seconds} 秒。")
    except urllib.error.HTTPError as error:
        return SearchResponse("http_error", message=f"搜索接口返回 HTTP {error.code}。")
    except (urllib.error.URLError, OSError) as error:
        return SearchResponse("http_error", message=f"搜索接口请求失败：{error}。")
    except json.JSONDecodeError:
        return SearchResponse("invalid", message="搜索接口返回了非法 JSON。")

    try:
        return _parse_results(payload)
    except ValueError as error:
        return SearchResponse("invalid", message=str(error))


def run_smoke_test(query: str = "Python latest stable release") -> SearchResponse:
    """One explicit real-network call used only for demo evidence."""
    response = web_search(query, timeout_seconds=15)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(
        json.dumps(
            {
                "status": response.status,
                "message": response.message,
                "results": [asdict(item) for item in response.results],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return response


if __name__ == "__main__":
    run_smoke_test()
