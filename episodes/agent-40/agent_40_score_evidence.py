import json
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Literal, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-39"))
from agent_39_extract_page import PageEvidence


ConflictStatus = Literal[
    "no_conflict",
    "conflict",
    "undetermined",
    "insufficient_evidence",
]

SOURCE_QUALITY_SCORES = {
    "official": 1.0,
    "reference": 0.7,
    "general": 0.4,
    "unknown": 0.0,
}

WEIGHTS = {
    "source_quality": 0.4,
    "freshness": 0.3,
    "task_relevance": 0.3,
}


@dataclass(frozen=True)
class ScoredEvidence:
    evidence_id: str
    source_url: str
    source_quality: float
    freshness: float
    task_relevance: float
    score: float
    reason: str
    status: Literal["success", "invalid"]


@dataclass(frozen=True)
class EvidenceScoringResponse:
    status: Literal["success", "invalid"]
    evidence: tuple[ScoredEvidence, ...] = ()
    conflict_status: ConflictStatus | None = None
    message: str | None = None


def _source_quality_score(value: str) -> float:
    return SOURCE_QUALITY_SCORES.get(str(value).strip().lower(), 0.0)


def _parse_published_at(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _freshness_score(published_at: str | None, reference_date: date) -> tuple[float, str]:
    parsed = _parse_published_at(published_at)
    if parsed is None:
        return 0.0, "published_at_missing_or_invalid"
    age_days = (reference_date - parsed).days
    if age_days < 0:
        return 0.0, "published_at_in_future"
    if age_days <= 365:
        return 1.0, f"age_days={age_days}<=365"
    if age_days <= 1095:
        return 0.5, f"age_days={age_days}<=1095"
    return 0.2, f"age_days={age_days}>1095"


def _task_relevance_score(
    body_text: str, summary: str, task_terms: Sequence[str]
) -> tuple[float, str]:
    terms = [str(term).strip().lower() for term in task_terms if str(term).strip()]
    haystack = f"{summary}\n{body_text}".lower()
    if not terms:
        return 0.2, "task_terms_missing"
    matches = sum(1 for term in terms if term in haystack)
    if matches == len(terms):
        return 1.0, "all_terms_match"
    if matches > 0:
        return 0.6, "any_term_matches"
    return 0.2, "no_term_matches"


def _as_page_evidence(item: object) -> PageEvidence:
    if isinstance(item, PageEvidence):
        return item
    if isinstance(item, dict):
        return PageEvidence(
            evidence_id=str(item.get("evidence_id", "")),
            title=str(item.get("title", "")),
            url=str(item.get("url", "")),
            summary=str(item.get("summary", "")),
            body_text=str(item.get("body_text", "")),
            source_type="web",
            source_quality=str(item.get("source_quality", "unknown")),
            published_at=item.get("published_at"),
            claim=item.get("claim"),
            extracted_at=item.get("extracted_at"),
        )
    raise ValueError("证据必须是 PageEvidence 或包含相同字段的 dict。")


def detect_conflict(evidence: Sequence[PageEvidence]) -> ConflictStatus:
    """Compare claims only; missing claims are never silently ignored."""
    if len(evidence) < 2:
        return "insufficient_evidence"
    claims = [str(item.claim).strip().lower() if item.claim else "" for item in evidence]
    if any(not claim for claim in claims):
        return "undetermined"
    if len(set(claims)) > 1:
        return "conflict"
    return "no_conflict"


def score_evidence(
    evidence_list: Sequence[object],
    task_terms: Sequence[str],
    reference_date: str | date | None = None,
) -> EvidenceScoringResponse:
    """Score evidence deterministically and preserve any detected conflict."""
    if not evidence_list:
        return EvidenceScoringResponse(
            "invalid",
            conflict_status="insufficient_evidence",
            message="没有证据输入。",
        )
    if not isinstance(task_terms, (list, tuple)):
        return EvidenceScoringResponse(
            "invalid",
            conflict_status="undetermined",
            message="task_terms 必须是列表或元组。",
        )

    reference = reference_date if isinstance(reference_date, date) else date.fromisoformat(str(reference_date or date.today()))
    scored: list[ScoredEvidence] = []
    normalized: list[PageEvidence] = []

    for index, raw in enumerate(evidence_list):
        try:
            evidence = _as_page_evidence(raw)
        except (ValueError, TypeError) as error:
            return EvidenceScoringResponse(
                "invalid",
                conflict_status="undetermined",
                message=f"第 {index + 1} 条证据非法：{error}",
            )
        normalized.append(evidence)
        quality = _source_quality_score(evidence.source_quality)
        freshness, freshness_reason = _freshness_score(evidence.published_at, reference)
        relevance, relevance_reason = _task_relevance_score(
            evidence.body_text, evidence.summary, task_terms
        )
        score = round(
            WEIGHTS["source_quality"] * quality
            + WEIGHTS["freshness"] * freshness
            + WEIGHTS["task_relevance"] * relevance,
            2,
        )
        reason = (
            f"source_quality={evidence.source_quality}({quality}); "
            f"freshness={freshness}({freshness_reason}); "
            f"task_relevance={relevance}({relevance_reason})"
        )
        scored.append(
            ScoredEvidence(
                evidence_id=evidence.evidence_id,
                source_url=evidence.url,
                source_quality=quality,
                freshness=freshness,
                task_relevance=relevance,
                score=score,
                reason=reason,
                status="success",
            )
        )

    conflict_status = detect_conflict(normalized)
    messages = {
        "no_conflict": "未检测到证据冲突。",
        "conflict": "检测到冲突，保留全部证据，不做静默覆盖。",
        "undetermined": "存在缺失或不可比较的 claim，无法判断冲突。",
        "insufficient_evidence": "证据不足，无法判断冲突。",
    }
    return EvidenceScoringResponse(
        "success",
        tuple(scored),
        conflict_status,
        messages[conflict_status],
    )


def run_evidence_demo() -> EvidenceScoringResponse:
    """Run the fixed conflict demo used by the video."""
    evidence = [
        PageEvidence(
            evidence_id="fixture-a",
            title="Python datetime date.today official",
            url="https://fixtures.local/agent-40/source-a",
            summary="datetime.date.today() returns the current local date.",
            body_text="datetime.date.today() returns the current local date.",
            source_type="web",
            source_quality="official",
            published_at="2026-01-01",
            claim="local",
            extracted_at="2026-08-05",
        ),
        PageEvidence(
            evidence_id="fixture-b",
            title="Python datetime date.today tutorial",
            url="https://fixtures.local/agent-40/source-b",
            summary="A tutorial claims date.today() returns the current UTC date instead of local date.",
            body_text="A tutorial claims date.today() returns the current UTC date instead of local date.",
            source_type="web",
            source_quality="general",
            published_at=None,
            claim="utc",
            extracted_at="2026-08-05",
        ),
    ]
    response = score_evidence(
        evidence,
        task_terms=["date", "today", "local"],
        reference_date="2026-08-05",
    )
    print(
        json.dumps(
            {
                "status": response.status,
                "conflict_status": response.conflict_status,
                "message": response.message,
                "evidence": [asdict(item) for item in response.evidence],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return response


if __name__ == "__main__":
    run_evidence_demo()
