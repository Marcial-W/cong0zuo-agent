import unittest

from agent_40_score_evidence import (
    PageEvidence,
    detect_conflict,
    score_evidence,
)


def make_evidence(
    evidence_id: str,
    source_quality: str,
    published_at: str | None,
    claim: str,
    body_text: str = "datetime date today local current calendar",
) -> PageEvidence:
    return PageEvidence(
        evidence_id=evidence_id,
        title=f"{evidence_id} page",
        url=f"https://fixtures.local/{evidence_id}",
        summary=body_text[:120],
        body_text=body_text,
        source_type="web",
        source_quality=source_quality,
        published_at=published_at,
        claim=claim,
        extracted_at="2026-08-05",
    )


class ScoreEvidenceTests(unittest.TestCase):
    def test_fixed_fixture_scores_are_repeatable(self) -> None:
        evidence = [
            make_evidence("fixture-a", "official", "2026-01-01", "local"),
            make_evidence("fixture-b", "general", None, "utc"),
        ]
        first = score_evidence(evidence, ["date", "today", "local"], "2026-08-05")
        second = score_evidence(evidence, ["date", "today", "local"], "2026-08-05")
        self.assertEqual(first.evidence[0].score, second.evidence[0].score)
        self.assertEqual(first.evidence[1].score, second.evidence[1].score)
        self.assertEqual(first, second)

    def test_official_with_date_scores_higher_than_general_without_date(self) -> None:
        response = score_evidence(
            [
                make_evidence("fixture-a", "official", "2026-01-01", "local"),
                make_evidence("fixture-b", "general", None, "utc"),
            ],
            ["date", "today", "local"],
            "2026-08-05",
        )
        self.assertEqual(response.status, "success")
        self.assertEqual(response.evidence[0].score, 1.0)
        self.assertEqual(response.evidence[1].score, 0.46)
        self.assertEqual(response.conflict_status, "conflict")

    def test_missing_published_at_has_explicit_freshness_zero(self) -> None:
        response = score_evidence(
            [make_evidence("fixture-b", "general", None, "utc")],
            ["date"],
            "2026-08-05",
        )
        self.assertEqual(response.evidence[0].freshness, 0.0)
        self.assertIn("published_at_missing_or_invalid", response.evidence[0].reason)

    def test_conflict_retains_both_evidence_and_does_not_override(self) -> None:
        response = score_evidence(
            [
                make_evidence("a", "official", "2026-01-01", "local"),
                make_evidence("b", "general", None, "utc"),
            ],
            ["date"],
            "2026-08-05",
        )
        self.assertEqual(response.conflict_status, "conflict")
        self.assertEqual(len(response.evidence), 2)
        self.assertEqual(response.evidence[0].evidence_id, "a")
        self.assertEqual(response.evidence[1].evidence_id, "b")

    def test_same_claim_is_no_conflict(self) -> None:
        response = score_evidence(
            [
                make_evidence("a", "official", "2026-01-01", "local"),
                make_evidence("b", "reference", "2026-06-01", "local"),
            ],
            ["date"],
            "2026-08-05",
        )
        self.assertEqual(response.conflict_status, "no_conflict")

    def test_missing_claim_is_undetermined(self) -> None:
        response = score_evidence(
            [
                make_evidence("a", "official", "2026-01-01", "local"),
                make_evidence("b", "general", None, ""),
            ],
            ["date"],
            "2026-08-05",
        )
        self.assertEqual(response.conflict_status, "undetermined")

    def test_single_evidence_is_insufficient(self) -> None:
        response = score_evidence(
            [make_evidence("a", "official", "2026-01-01", "local")],
            ["date"],
            "2026-08-05",
        )
        self.assertEqual(response.conflict_status, "insufficient_evidence")

    def test_empty_evidence_is_invalid_and_insufficient(self) -> None:
        response = score_evidence([], ["date"], "2026-08-05")
        self.assertEqual(response.status, "invalid")
        self.assertEqual(response.conflict_status, "insufficient_evidence")

    def test_task_relevance_changes_score(self) -> None:
        evidence = [
            make_evidence("a", "official", "2026-01-01", "local"),
            make_evidence("b", "general", None, "utc"),
        ]
        relevant = score_evidence(evidence, ["date", "today", "local"], "2026-08-05")
        irrelevant = score_evidence(evidence, ["quantum", "physics"], "2026-08-05")
        self.assertGreater(relevant.evidence[0].score, irrelevant.evidence[0].score)

    def test_score_reason_never_claims_fact_verification(self) -> None:
        response = score_evidence(
            [make_evidence("a", "official", "2026-01-01", "local")],
            ["date"],
            "2026-08-05",
        )
        self.assertNotIn("verified", response.evidence[0].reason.lower())
        self.assertNotIn("true", response.evidence[0].reason.lower())

    def test_detect_conflict_statuses(self) -> None:
        self.assertEqual(
            detect_conflict(
                [
                    make_evidence("a", "official", "2026-01-01", "local"),
                    make_evidence("b", "general", None, "utc"),
                ]
            ),
            "conflict",
        )
        self.assertEqual(
            detect_conflict([make_evidence("a", "official", "2026-01-01", "local")]),
            "insufficient_evidence",
        )


if __name__ == "__main__":
    unittest.main()
