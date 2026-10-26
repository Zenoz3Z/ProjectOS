"""Pure final selection over a closed, already category-filtered payload.

No corpus, model, metadata-file or evaluator access. The trusted adapter injects
the unchanged production baseline function before entering the worker boundary.
"""
from __future__ import annotations

import math
import re


SECTIONS = frozenset((
    "current_intention", "changes_and_reasons", "current_vs_superseded",
    "relevant_feedback", "unresolved_tensions", "possible_next_action",
))
STATES = frozenset((
    "current_snapshot", "final_snapshot", "closure_record",
    "historical_record", "undated_record", "unknown",
))
SNAPSHOTS = frozenset(("current_snapshot", "final_snapshot", "closure_record"))
UNCHANGED = frozenset(("changes_and_reasons", "relevant_feedback", "possible_next_action"))


def validate_payload(payload):
    """Reject extra fields at every boundary, including complete metadata."""
    if type(payload) is not dict or set(payload) != {
        "section_id", "ordered_eligible_candidates", "eligible_record_states"
    }:
        raise ValueError("Only the frozen selector input fields are permitted")
    if payload["section_id"] not in SECTIONS:
        raise ValueError("Unknown section")
    queries = payload["ordered_eligible_candidates"]
    states = payload["eligible_record_states"]
    if type(queries) is not list or len(queries) != 2 or type(states) is not dict:
        raise ValueError("Exactly two ordered query lists and a state mapping are required")
    ids, chunk_records = set(), {}
    for query in queries:
        if type(query) is not list:
            raise ValueError("Query candidates must be an array")
        for row in query:
            if type(row) is not dict or set(row) != {"chunk_id", "record_id", "score"}:
                raise ValueError("Candidate fields must be chunk_id, record_id and score only")
            cid, rid, score = row["chunk_id"], row["record_id"], row["score"]
            if not isinstance(cid, str) or not cid or not isinstance(rid, str) or not re.fullmatch(r"[A-Z]{2}-R[0-9]{2}", rid):
                raise ValueError("Invalid candidate identity")
            if type(score) not in (int, float) or not math.isfinite(score):
                raise ValueError("Score must be a finite number")
            if cid in chunk_records and chunk_records[cid] != rid:
                raise ValueError("A chunk cannot belong to multiple records")
            chunk_records[cid] = rid
            ids.add(rid)
    if set(states) != ids:
        raise ValueError("The state projection must cover exactly the candidate records")
    if any(type(value) is not str or value not in STATES for value in states.values()):
        raise ValueError("State values must be enum strings, never metadata objects")


class StateAwareSelector:
    """The callable dependency is trusted code, not part of the JSON interface."""

    def __init__(self, production_baseline):
        self._baseline = production_baseline

    def select(self, payload):
        validate_payload(payload)
        section = payload["section_id"]
        queries = payload["ordered_eligible_candidates"]
        states = payload["eligible_record_states"]

        def baseline():
            return self._baseline(section, queries)

        def snapshot(row):
            return states[row["record_id"]] in SNAPSHOTS

        if section in UNCHANGED:
            selected = baseline()
        elif section == "current_vs_superseded":
            first = next((row for row in queries[0] if snapshot(row)), None)
            second = next((row for row in queries[1]
                           if states[row["record_id"]] == "historical_record"
                           and first is not None and row["record_id"] != first["record_id"]), None)
            selected = [first["chunk_id"], second["chunk_id"]] if first and second else baseline()
        elif not any(snapshot(row) for query in queries for row in query):
            selected = baseline()
        else:
            # Union representative: highest original score; equal-score ties
            # retain first occurrence. Dict insertion order preserves fill ties.
            best = {}
            for query in queries:
                for row in query:
                    cid = row["chunk_id"]
                    if cid not in best or row["score"] > best[cid]["score"]:
                        best[cid] = row
            selected = []
            for query in queries:
                preferred = [row for row in query if snapshot(row)]
                others = [row for row in query if not snapshot(row)]
                row = next((row for row in preferred + others if row["chunk_id"] not in selected), None)
                if row is not None:
                    selected.append(row["chunk_id"])
            if len(selected) < 2:
                union = sorted(best.values(), key=lambda row: row["score"], reverse=True)
                fill = [row for row in union if snapshot(row)] + [row for row in union if not snapshot(row)]
                for row in fill:
                    if len(selected) == 2:
                        break
                    if row["chunk_id"] not in selected:
                        selected.append(row["chunk_id"])

        pool = {row["chunk_id"] for query in queries for row in query}
        if len(selected) > 2 or len(set(selected)) != len(selected) or not set(selected) <= pool:
            raise ValueError("Selection escaped the original candidate pool")
        return list(selected)
