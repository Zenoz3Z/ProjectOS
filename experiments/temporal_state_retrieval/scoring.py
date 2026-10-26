"""Frozen-protocol evidence scoring; no retrieval, model or source-file access."""
from __future__ import annotations

from fractions import Fraction
import math
import statistics


def normalise(text):
    return " ".join(text.split())


def _span_visible(span, source, item):
    return (
        item["source"] == source
        and item["start_char"] <= span["start_char"]
        and span["end_char"] <= item["end_char"]
        and normalise(span["quote"]) in normalise(item["excerpt"])
    )


def matched_ids(case, passages, items, require_context=True):
    found = set()
    for passage in passages.values():
        if passage["context_id"] != case["context_id"]:
            continue
        span = dict(passage["locator"], quote=passage["quote"])
        if not any(_span_visible(span, passage["source"], item) for item in items):
            continue
        if require_context and passage["passage_id"] in case["required_context_passages"]:
            if not all(
                any(_span_visible(context, passage["source"], item) for item in items)
                for context in passage["context_spans"]
            ):
                continue
        found.add(passage["passage_id"])
    return found


def eligible_roles(case, passage):
    if passage["passage_id"] not in case["acceptable_gold_passages"]:
        return set()
    roles = {
        role for role in passage["evidence_role"]
        if role in case["role_temporal_requirements"]
        and passage["temporal_status"] in case["role_temporal_requirements"][role]
    }
    if case["case_id"] not in passage["inapplicability_case_ids"]:
        roles.discard("closure_or_inapplicability")
    return roles


def fully_annotated(case, passages, item):
    """Conservative judgment: never infer labels for uncovered source words.

    Complete, case-context annotations must cover every non-whitespace visible
    character. A fragment of a labelled assertion is not a full judgment.
    """
    ids = matched_ids(case, passages, [item], require_context=False)
    intervals = sorted(
        (passages[pid]["locator"]["start_char"], passages[pid]["locator"]["end_char"])
        for pid in ids
    )
    for start, end in item["visible_token_spans"]:
        point = start
        for left, right in intervals:
            if left <= point < right:
                point = max(point, right)
        if point < end:
            return False, ids
    # Identical/overlapping assertions with incompatible temporal labels need
    # explicit case scope; accepted/excluded/boundary references provide it.
    scoped = set(case["acceptable_gold_passages"]) | set(case["boundary_passages"])
    scoped |= {x["passage_id"] for x in case["excluded_or_misleading_passages"]}
    relevant = ids & scoped
    for first in relevant:
        for second in relevant:
            a, b = passages[first], passages[second]
            if (
                first != second and a["locator"] == b["locator"]
                and set(a["evidence_role"]) & set(b["evidence_role"])
                and a["temporal_status"] != b["temporal_status"]
            ):
                return False, ids
    return bool(item["visible_token_spans"]), relevant or ids


def score_case(case, passages, trace):
    ordered, selected = trace["ordered_evidence"], trace["selected_evidence"]
    gold = set(case["acceptable_gold_passages"])
    supported = case["expected_support_status"] == "supported"

    def positive(k):
        ids = matched_ids(case, passages, ordered[:k])
        return {pid for pid in ids & gold if eligible_roles(case, passages[pid])}

    top_two = matched_ids(case, passages, selected)
    roles = set().union(*(eligible_roles(case, passages[p]) for p in top_two))
    first_rank = next((k for k in range(1, len(ordered) + 1) if positive(k)), None)
    requirements = set(case["required_evidence_roles"])
    closure_ids = {
        p for p in top_two
        if "closure_or_inapplicability" in eligible_roles(case, passages[p])
    }
    closure_first = {
        p for p in matched_ids(case, passages, selected[:1])
        if "closure_or_inapplicability" in eligible_roles(case, passages[p])
    }
    temporal = None
    temporal_reason = "empty selected evidence"
    if selected:
        fully, focal = fully_annotated(case, passages, selected[0])
        temporal_reason = "unjudged or incompletely annotated top-1"
        if fully:
            temporal_reason = ""
            mismatch = False
            unknown = False
            for pid in focal:
                p = passages[pid]
                if eligible_roles(case, p):
                    continue
                if p["temporal_status"] == "unknown":
                    unknown = True
                    continue
                relevant = set(p["evidence_role"]) & requirements
                if relevant:
                    mismatch |= any(
                        p["temporal_status"] not in case["role_temporal_requirements"][role]
                        for role in relevant
                    )
                else:
                    mismatch |= p["temporal_status"] not in case["expected_temporal_status"]
            if unknown:
                temporal_reason = "unknown temporal attribution"
            else:
                temporal = int(mismatch)

    excluded = {x["passage_id"] for x in case["excluded_or_misleading_passages"]}
    known_excluded = top_two & excluded
    risk_states = {"historical", "superseded", "completed", "future_conditional"}
    risk_ids = set()
    if case["current_claim_roles"]:
        for pid in top_two:
            p = passages[pid]
            if eligible_roles(case, p):  # approved historical pair partners exempt
                continue
            if p["temporal_status"] in risk_states and (
                pid in excluded or set(p["evidence_role"]) & set(case["current_claim_roles"])
            ):
                risk_ids.add(pid)
    all_judged = bool(selected) and all(fully_annotated(case, passages, e)[0] for e in selected)
    unknown_selected = any(passages[p]["temporal_status"] == "unknown" for p in top_two)
    risk_value = None
    risk_reason = "case makes no affirmative current claim"
    if case["current_claim_roles"]:
        risk_value = int(bool(risk_ids)) if all_judged and not unknown_selected else None
        risk_reason = "" if risk_value is not None else "unjudged, unknown or empty selected evidence"

    app = None
    if case["section_applicability"] != "unclear":
        app = int(any(set(group) <= top_two for group in case["applicability_evidence_sets"]))
    pair = None
    if case["acceptable_pair_sets"]:
        pair = int(any(set(group) <= top_two for group in case["acceptable_pair_sets"]))
    insufficient_detail = None
    if not supported:
        insufficient_detail = {
            "classification_accuracy": "not measurable at retrieval-only baseline",
            "empty": not selected,
            "boundary_passages": sorted(top_two & set(case["boundary_passages"])),
            "excluded_passages": sorted(known_excluded),
            "unjudged_selected": not all_judged if selected else False,
        }
    negative = {pid for pid in top_two if "closure_or_inapplicability" in passages[pid]["evidence_role"]}
    wrong_negative = negative - closure_ids
    contingency = None
    if not supported or case["section_applicability"] == "not_applicable":
        if selected and not all_judged:
            contingency = "unjudged"
        elif closure_ids:
            contingency = "valid scoped closure"
        elif wrong_negative:
            contingency = "only wrong-scope/excluded negative evidence"
        else:
            contingency = "no closure"
    metrics = {
        "hit_at_1": int(bool(positive(1))) if supported else None,
        "hit_at_3": int(bool(positive(3))) if supported else None,
        "mrr": float(Fraction(1, first_rank)) if supported and first_rank else (0.0 if supported else None),
        "role_coverage_at_2": len(roles & requirements) / len(requirements) if supported else None,
        "all_required_roles_at_2": int(requirements <= roles) if supported else None,
        "pair_coverage_at_2": pair,
        "temporal_mismatch": temporal,
        "false_current_judged": risk_value,
        "applicability_evidence_at_2": app,
        "closure_at_1": int(bool(closure_first)) if case["section_applicability"] == "not_applicable" else None,
        "closure_at_2": int(bool(closure_ids)) if case["section_applicability"] == "not_applicable" else None,
    }
    reasons = {
        "hit_at_1": "insufficient case has no affirmative gold",
        "hit_at_3": "insufficient case has no affirmative gold",
        "mrr": "insufficient case has no affirmative gold",
        "role_coverage_at_2": "insufficient case has no affirmative gold",
        "all_required_roles_at_2": "insufficient case has no affirmative gold",
        "pair_coverage_at_2": "case has no required direction pair",
        "temporal_mismatch": temporal_reason,
        "false_current_judged": risk_reason,
        "applicability_evidence_at_2": "unclear applicability is outside denominator",
        "closure_at_1": "not an explicit inapplicability case",
        "closure_at_2": "not an explicit inapplicability case",
    }
    if case["expected_support_status"] == "supported":
        coverage_status = "pass" if metrics["all_required_roles_at_2"] and (pair is None or pair) else "fail"
    else:
        coverage_status = "not a support-classification test"
    return {
        "case_id": case["case_id"], "project_id": case["project_id"],
        "benchmark_tier": case["benchmark_tier"], "section_id": case["section_id"],
        "expected_support_status": case["expected_support_status"],
        "section_applicability": case["section_applicability"],
        "current_claim": bool(case["current_claim_roles"]),
        "metrics": metrics, "exclusion_reasons": reasons,
        "reciprocal_rank_exact": str(Fraction(1, first_rank)) if supported and first_rank else ("0" if supported else None),
        "first_gold_rank": first_rank,
        "ordered_list_length": len(ordered),
        "matched_gold_top2": sorted(top_two & gold),
        "matched_passages_top2": sorted(top_two),
        "roles_covered": sorted(roles & requirements),
        "required_role_count": len(requirements),
        "known_false_current_exposure": bool(risk_ids),
        "false_current_passages": sorted(risk_ids),
        "all_selected_fully_annotated": all_judged,
        "unknown_selected": unknown_selected,
        "insufficient_detail": insufficient_detail,
        "closure_contingency": contingency,
        "misleading_negative_exposure": bool(wrong_negative),
        "evidence_coverage_status": coverage_status,
    }


def aggregate(results, tier, private_ids=frozenset()):
    rows = [r for r in results if r["benchmark_tier"] == tier]
    assert rows
    metrics = {}
    for name in rows[0]["metrics"]:
        included = [r for r in rows if r["metrics"][name] is not None]
        omitted = [r for r in rows if r["metrics"][name] is None]
        numerator = sum(r["metrics"][name] for r in included)
        excluded = {}
        for r in omitted:
            reason = r["exclusion_reasons"][name]
            slot = excluded.setdefault(reason, {"public_case_ids": [], "private_case_count": 0})
            if r["case_id"] in private_ids:
                slot["private_case_count"] += 1
            else:
                slot["public_case_ids"].append(r["case_id"])
        metrics[name] = {
            "numerator": numerator, "denominator": len(included),
            "value": numerator / len(included) if included else None,
            "status": "measured" if included else "not measurable at retrieval-only baseline",
            "eligible_public_case_ids": [r["case_id"] for r in included if r["case_id"] not in private_ids],
            "eligible_private_case_count": sum(r["case_id"] in private_ids for r in included),
            "excluded": excluded,
        }
        if name == "mrr":
            metrics[name]["numerator_exact"] = str(sum((Fraction(r["reciprocal_rank_exact"]) for r in included), Fraction()))
        if name == "role_coverage_at_2":
            metrics[name]["interpretation"] = "macro mean of per-case role fractions; not a count of cases"
            metrics[name]["covered_roles_total"] = sum(len(r["roles_covered"]) for r in included)
            metrics[name]["required_roles_total"] = sum(r["required_role_count"] for r in included)
    current = [r for r in rows if r["current_claim"]]
    metrics["false_current_all_case_lower_bound"] = {
        "numerator": sum(r["known_false_current_exposure"] for r in current),
        "denominator": len(current),
        "value": sum(r["known_false_current_exposure"] for r in current) / len(current) if current else None,
        "status": "known annotated exposure lower bound; unjudged cases are not safe negatives",
        "eligible_public_case_ids": [r["case_id"] for r in current if r["case_id"] not in private_ids],
        "eligible_private_case_count": sum(r["case_id"] in private_ids for r in current),
        "excluded": {"not a current-claim case": {"count": len(rows)-len(current)}},
        "unjudged_or_unknown_count": sum(r["metrics"]["false_current_judged"] is None for r in current),
    }
    metrics["insufficient_preservation_accuracy"] = {
        "numerator": None, "denominator": None, "value": None,
        "status": "not measurable at retrieval-only baseline",
        "scope_case_count": sum(r["expected_support_status"] == "insufficient" for r in rows),
        "excluded": {"all cases": {"reason": "no final support/abstention decision layer is evaluated"}},
    }
    return {"tier": tier, "case_count": len(rows), "metrics": metrics}


def latency_stats(samples):
    if not samples:
        return {"numerator": None, "denominator": 0, "value": None, "sample_count": 0}
    ordered = sorted(samples)
    pos = .95 * (len(ordered)-1)
    low, high = math.floor(pos), math.ceil(pos)
    p95 = ordered[low] + (ordered[high]-ordered[low]) * (pos-low)
    return {
        "numerator": None, "denominator": len(samples), "value": statistics.median(samples),
        "median_ms": statistics.median(samples), "minimum_ms": min(samples),
        "maximum_ms": max(samples), "p95_ms": p95, "sample_count": len(samples),
        "interpretation": "median duration, not a numerator/denominator accuracy",
    }
