import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Literal

from bs4 import BeautifulSoup


USER_AGENT = "MarcialAgentLab/0.1 (educational demo)"
ExtractionStatus = Literal[
    "success",
    "invalid_url",
    "timeout",
    "http_error",
    "empty",
    "not_html",
    "parse_error",
]
Transport = Callable[[str, float, int], "HttpResponse"]

NOISE_TAGS = (
    "script",
    "style",
    "noscript",
    "nav",
    "footer",
    "aside",
    "iframe",
    "form",
    "svg",
)
NOISE_KEYWORDS = (
    "nav",
    "menu",
    "footer",
    "ad",
    "banner",
    "cookie",
    "sidebar",
    "comment",
    "promo",
    "sponsor",
    "related",
    "recommend",
    "toc",
    "catlinks",
    "reflist",
    "references",
)


@dataclass(frozen=True)
class HttpResponse:
    status: int
    content_type: str
    body: str


@dataclass(frozen=True)
class PageExtraction:
    status: ExtractionStatus
    url: str
    title: str | None = None
    summary: str | None = None
    body_text: str | None = None
    source_type: Literal["web"] = "web"
    http_status: int | None = None
    content_type: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class PageEvidence:
    evidence_id: str
    title: str
    url: str
    summary: str
    body_text: str
    source_type: Literal["web"] = "web"
    source_quality: str = "unknown"
    published_at: str | None = None
    claim: str | None = None
    extracted_at: str | None = None


def default_transport(url: str, timeout_seconds: float, max_bytes: int) -> HttpResponse:
    """Fetch one public page with an identifying User-Agent."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        content_type = response.headers.get("Content-Type", "") or ""
        body = response.read(max_bytes).decode("utf-8", errors="replace")
        return HttpResponse(response.status, content_type, body)


def _get_url(search_result: object) -> str | None:
    if hasattr(search_result, "url"):
        url = getattr(search_result, "url")
    elif isinstance(search_result, dict):
        url = search_result.get("url")
    else:
        url = None
    return url if isinstance(url, str) and url.strip() else None


def _valid_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _strip_noise(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name in ("html", "body", "head"):
            continue
        attrs = tag.attrs or {}
        classes = " ".join(attrs.get("class") or []).lower()
        tag_id = str(attrs.get("id") or "").lower()
        if any(keyword in classes or keyword in tag_id for keyword in NOISE_KEYWORDS):
            tag.decompose()


def _select_main(soup: BeautifulSoup) -> object:
    return (
        soup.select_one(
            "main, article, [role=main], #content, #mw-content-text, .mw-parser-output"
        )
        or soup.body
    )


def _extract_body_text(main: object) -> str:
    blocks: list[str] = []
    for tag in main.find_all(["h1", "h2", "h3", "h4", "p", "pre", "blockquote"]):
        text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()
        if len(text) >= 20:
            blocks.append(text)
    return "\n".join(blocks)


def _make_summary(body_text: str) -> str:
    clean = re.sub(r"\s+", " ", body_text).strip()
    return clean[:300] + ("..." if len(clean) > 300 else "")


def extract_page(
    search_result: object,
    transport: Transport = default_transport,
    timeout_seconds: float = 8,
    max_bytes: int = 2_000_000,
) -> PageExtraction:
    """Fetch and clean a page referenced by a P038 SearchResult."""
    url = _get_url(search_result)
    if not url or not _valid_url(url):
        return PageExtraction("invalid_url", url or "", message="URL 必须是 http/https。")

    try:
        response = transport(url, float(timeout_seconds), int(max_bytes))
    except (TimeoutError, socket.timeout):
        return PageExtraction("timeout", url, message=f"请求超过 {timeout_seconds} 秒。")
    except urllib.error.HTTPError as error:
        return PageExtraction("http_error", url, message=f"页面返回 HTTP {error.code}。")
    except (urllib.error.URLError, OSError) as error:
        return PageExtraction("http_error", url, message=f"页面请求失败：{error}。")
    except ValueError as error:
        return PageExtraction("parse_error", url, message=str(error))

    if not isinstance(response, HttpResponse):
        return PageExtraction("parse_error", url, message="transport 返回类型非法。")
    if not 200 <= response.status < 300:
        return PageExtraction(
            "http_error",
            url,
            http_status=response.status,
            content_type=response.content_type,
            message=f"页面返回 HTTP {response.status}。",
        )

    content_type = response.content_type.lower()
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return PageExtraction(
            "not_html",
            url,
            http_status=response.status,
            content_type=response.content_type,
            message="页面不是可处理的 HTML。",
        )
    if not response.body.strip():
        return PageExtraction(
            "empty",
            url,
            http_status=response.status,
            content_type=response.content_type,
            message="页面正文为空。",
        )

    try:
        soup = BeautifulSoup(response.body, "html.parser")
        _strip_noise(soup)
        main = _select_main(soup)
        body_text = _extract_body_text(main)
    except Exception as error:
        return PageExtraction(
            "parse_error",
            url,
            http_status=response.status,
            content_type=response.content_type,
            message=f"页面无法解析：{error}。",
        )

    if not body_text.strip():
        return PageExtraction(
            "empty",
            url,
            http_status=response.status,
            content_type=response.content_type,
            message="清洗后没有可提取正文。",
        )

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return PageExtraction(
        status="success",
        url=url,
        title=title,
        summary=_make_summary(body_text),
        body_text=body_text,
        source_type="web",
        http_status=response.status,
        content_type=response.content_type,
    )


def to_page_evidence(
    extraction: PageExtraction,
    evidence_id: str | None = None,
    source_quality: str = "unknown",
    published_at: str | None = None,
    claim: str | None = None,
    extracted_at: str | None = None,
) -> PageEvidence:
    """Convert a successful extraction into the stable evidence object."""
    if extraction.status != "success":
        raise ValueError(f"只有 success 可以转为 PageEvidence，当前为 {extraction.status}。")
    return PageEvidence(
        evidence_id=evidence_id or extraction.url,
        title=extraction.title or "",
        url=extraction.url,
        summary=extraction.summary or "",
        body_text=extraction.body_text or "",
        source_type="web",
        source_quality=source_quality,
        published_at=published_at,
        claim=claim,
        extracted_at=extracted_at or date.today().isoformat(),
    )


def run_smoke_test() -> PageExtraction:
    """One real-network extraction used only as demo evidence."""
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "agent-38"))
    from agent_38_web_search import SearchResult

    fixed_result = SearchResult(
        title="Python (programming language)",
        url="https://en.wikipedia.org/wiki/Python_(programming_language)",
        snippet="As of May 2026, Python 3.14.6 is the latest stable release.",
        source_type="web",
        rank=1,
    )
    extraction = extract_page(fixed_result, timeout_seconds=15)
    if extraction.status != "success":
        raise SystemExit(f"提取失败：{extraction.status} {extraction.message}")

    print(
        json.dumps(
            {
                "requested_at": date.today().isoformat(),
                "search_result_title": fixed_result.title,
                "url": extraction.url,
                "http_status": extraction.http_status,
                "content_type": extraction.content_type,
                "title": extraction.title,
                "summary": extraction.summary,
                "body_length": len(extraction.body_text or ""),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return extraction


if __name__ == "__main__":
    run_smoke_test()
