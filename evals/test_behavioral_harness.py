"""Tests for the deterministic high-risk workflow evaluator."""

from evals.behavioral_harness import evaluate_sync


def test_all_high_risk_policy_cases_pass() -> None:
    result = evaluate_sync(evaluated_at="2026-07-13T00:00:00Z")

    assert result["result"] == "passed"
    assert result["summary"]["cases"] == 5
    assert result["summary"]["passed"] == 5
    assert result["source_evidence"]["passed"] is True


def test_each_unsafe_trace_mutation_is_rejected() -> None:
    result = evaluate_sync(evaluated_at="2026-07-13T00:00:00Z")

    assert result["summary"]["unsafe_mutations"] == 5
    assert result["summary"]["unsafe_mutations_rejected"] == 5
    assert all(item["rejected"] for item in result["grader_sensitivity"])


def test_evaluation_is_reproducible_at_a_fixed_timestamp() -> None:
    first = evaluate_sync(evaluated_at="2026-07-13T00:00:00Z")
    second = evaluate_sync(evaluated_at="2026-07-13T00:00:00Z")

    assert first == second
