"""Gates and the ranking rubric, both versioned and both showing their work.

Two separate decisions, deliberately not blended. The **gates** are mandatory
and binary: in scope, readable, tested, not a duplicate. A high score does not
buy a way past them — popularity in particular cannot, which is the whole reason
adoption is worth ten points out of a hundred and sits behind a logarithm.

The **rubric** then ranks what survived, on inspection value rather than
popularity. Every awarded point carries the anchor that awarded it, so a
shortlist can be argued with afterwards. The weights are in `policy.json` with a
version, because they are starting assumptions and the calibration step exists to
change them.

The third outcome is the one that makes this honest: `deferred`. Evidence that is
incomplete is not evidence that is negative, so a truncated tree, an exhausted
budget or a failed request produces a deferral with a retry date, never a
rejection.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from evidence import (
    ABSENT, FILES_ONLY, MEMORY_SPECIFIC, MENTION_ONLY, PASSING, SUBSTANTIVE, UNKNOWN,
    ScopeEvidence, SubstanceEvidence, TestEvidence,
)
from util import loads, parse_iso, utc_now

# The atlas's own seven marks, as vocabulary to look for in inspected code. A
# term here is a *lead*, never a finding: the report is what decides whether a
# mechanism is really there, and this only decides whether it is worth reading.
RARE_MARKS = {
    "tombstone": r"\btombstone|\brejected[_ ]value|\bdeny[_ ]?list.*hash|\bcontent_hash.*reject",
    "bitemporal": r"\bvalid[_ ]?(from|to|time)\b|\bbitemporal\b|\bas[_ ]of\b|\bsystem[_ ]time\b",
    "trust_state": r"\b(candidate|verified|rejected|provisional|disputed)[_ ]?(state|status)\b"
                   r"|\btrust[_ ]?(state|level|score)\b",
    "human_review": r"\bapprove[ds]?[_ ]?by\b|\bhuman[_ ]?(review|in[_ ]the[_ ]loop|approval)\b"
                    r"|\breviewer[_ ]?id\b|\bawaiting[_ ]approval\b",
    "negative_eval": r"\bassert[_ ].*not[_ ]in\b|\bnot_?retrieved\b|\bexcluded[_ ]from[_ ]results\b"
                     r"|\bassertNotIn\b|\bshould[_ ]not[_ ](contain|retrieve|return)\b",
}
COMMON_MARKS = {
    # The first rules asked for `scope_id` and friends and missed a plain `scope`
    # column filtered in a WHERE clause, which is the ordinary way to write it.
    "scope_enforced": r"\b(tenant|workspace|namespace|scope)[_ ]?(id|key|filter)\b"
                      r"|\bowner[_ ]key\b|\bWHERE\b[^;\n]{0,80}\b(scope|namespace|tenant_id|"
                      r"user_id|workspace_id|owner)\s*=",
    "audit_log": r"\baudit[_ ]?(log|trail|entry)\b|\bappend[_ ]only\b|\bmutation[_ ]log\b"
                 r"|\bmemory_history\b|\bhistory\s+table\b",
    # Correction without a tombstone: soft deletion, supersession, expiry,
    # versioning. The shape most small memory systems actually have, and the
    # lead that tells the full analysis where to look for a tombstone's absence.
    "correction": r"\bdeleted_at\b|\bsuperseded?_by\b|\bsupersedes\b|\bvalid_until\b"
                  r"|\bexpires?_at\b|\binvalidated(_at)?\b|\brevoked(_at)?\b|\barchived_at\b"
                  r"|\bversion\s+INTEGER\b|\bforget_memory\b|\bdelete_memory\b",
}


@dataclass
class Policy:
    version: str
    minimum_score: int
    components: dict[str, Any]
    reassessment_days: dict[str, int]
    new_account_days: int

    @classmethod
    def load(cls, path: Path) -> "Policy":
        raw = loads(path.read_text(encoding="utf-8"))
        return cls(
            version=raw["version"],
            minimum_score=int(raw["minimum_score"]),
            components=raw["components"],
            reassessment_days=raw["reassessment_days"],
            new_account_days=int(raw.get("new_account_days", 30)),
        )

    def anchor(self, component: str, name: str) -> int:
        return int(self.components[component]["anchors"][name])

    def cap(self, component: str) -> int:
        return int(self.components[component]["max"])


@dataclass
class Award:
    component: str
    points: int
    anchor: str
    because: str


@dataclass
class Decision:
    outcome: str                     # eligible | rejected | deferred
    score: int | None = None
    components: dict[str, int] = field(default_factory=dict)
    awards: list[dict[str, Any]] = field(default_factory=list)
    gates: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    reassess_in_days: int | None = None
    reassessment_condition: str | None = None


def _days_since(timestamp: str | None) -> float | None:
    if not timestamp:
        return None
    try:
        return (utc_now() - parse_iso(timestamp.replace("Z", "+00:00"))).total_seconds() / 86400
    except ValueError:
        return None


def mechanism_terms(blob_texts: dict[str, str]) -> tuple[list[str], list[str]]:
    """Which of the atlas's marks have vocabulary in the code that was read.

    README text is excluded on purpose. A project can name every mechanism in its
    documentation; the question here is whether the words appear where the
    behaviour would have to be.
    """
    rare, common = [], []
    body = "\n".join(
        text for path, text in blob_texts.items()
        if not path.lower().startswith("readme") and not path.lower().endswith(".md")
    )
    for mark, pattern in RARE_MARKS.items():
        if re.search(pattern, body, re.IGNORECASE):
            rare.append(mark)
    for mark, pattern in COMMON_MARKS.items():
        if re.search(pattern, body, re.IGNORECASE):
            common.append(mark)
    return rare, common


def gates(*, scope: ScopeEvidence, substance: SubstanceEvidence, tests: TestEvidence,
          duplicate: str | None) -> dict[str, Any]:
    return {
        "in_scope": {"value": scope.in_scope, "basis": scope.basis,
                     "why": "; ".join(scope.reasons)},
        "readable_implementation": {"value": substance.readable,
                                    "why": "; ".join(substance.reasons)},
        "test_evidence": {"value": tests.level in PASSING if tests.level != UNKNOWN else None,
                          "level": tests.level, "why": tests.reason},
        "not_duplicate": {"value": duplicate is None, "why": duplicate or "no existing report or open selection"},
    }


def decide(policy: Policy, *, scope: ScopeEvidence, substance: SubstanceEvidence,
           tests: TestEvidence, facts: dict[str, Any], coverage: dict[str, str],
           blob_texts: dict[str, str], duplicate: str | None,
           corpus_loaded: bool) -> Decision:
    decision = Decision(outcome="deferred")
    decision.gates = gates(scope=scope, substance=substance, tests=tests, duplicate=duplicate)

    # --- mandatory gates, in the order that costs least to explain
    if duplicate is not None:
        decision.outcome = "rejected"
        decision.reasons.append(duplicate)
        decision.reassessment_condition = (
            "excluded while the existing report stands; reopening is the atlas's "
            "separate reanalysis policy, not this program's"
        )
        return decision

    unknown_gates = [
        name for name, gate in decision.gates.items() if gate["value"] is None
    ]
    failed_gates = [
        name for name, gate in decision.gates.items() if gate["value"] is False
    ]

    if unknown_gates:
        decision.outcome = "deferred"
        decision.reasons.extend(
            f"{name}: {decision.gates[name]['why']}" for name in unknown_gates
        )
        gaps = [key for key, value in coverage.items()
                if value in ("unavailable", "budget_exceeded", "sampled")]
        decision.reassess_in_days = policy.reassessment_days["incomplete_evidence"]
        decision.reassessment_condition = (
            "retry when the missing evidence can be collected"
            + (f" (incomplete: {', '.join(sorted(gaps))})" if gaps else "")
        )
        return decision

    if failed_gates:
        decision.outcome = "rejected"
        decision.reasons.extend(
            f"{name}: {decision.gates[name]['why']}" for name in failed_gates
        )
        if "test_evidence" in failed_gates:
            decision.reassess_in_days = policy.reassessment_days["weak_tests"]
            decision.reassessment_condition = (
                f"reassess after {policy.reassessment_days['weak_tests']} days, or sooner if the "
                f"default branch gains committed tests with assertions. Rejected at "
                f"{facts.get('head_commit') or 'the assessed commit'}, not in general."
            )
        else:
            decision.reassess_in_days = policy.reassessment_days["below_minimum_score"]
            decision.reassessment_condition = "reassess on a new default-branch commit"
        return decision

    # --- rubric
    awards: list[Award] = []
    awards += _score_tests(policy, tests)
    awards += _score_substance(policy, substance, scope)
    awards += _score_contribution(policy, facts, coverage, decision)
    awards += _score_atlas_value(policy, blob_texts, corpus_loaded, decision)
    awards += _score_adoption(policy, facts, decision)

    totals: dict[str, int] = {}
    for award in awards:
        totals[award.component] = totals.get(award.component, 0) + award.points
    for component in policy.components:
        totals[component] = min(totals.get(component, 0), policy.cap(component))

    decision.components = totals
    decision.awards = [
        {"component": a.component, "points": a.points, "anchor": a.anchor, "because": a.because}
        for a in awards
    ]
    decision.score = sum(totals.values())

    if decision.score < policy.minimum_score:
        decision.outcome = "rejected"
        decision.reasons.append(
            f"scored {decision.score} against a minimum of {policy.minimum_score}"
        )
        decision.reassess_in_days = policy.reassessment_days["below_minimum_score"]
        decision.reassessment_condition = (
            f"reassess after {policy.reassessment_days['below_minimum_score']} days or on a new "
            f"default-branch commit; the gates passed, the rank did not clear the bar"
        )
        return decision

    decision.outcome = "eligible"
    decision.reasons.append(
        f"passed all four gates and scored {decision.score}/{policy.minimum_score} minimum"
    )
    return decision


def _score_tests(policy: Policy, tests: TestEvidence) -> list[Award]:
    awards = []
    level_anchor = {
        MEMORY_SPECIFIC: "level_memory_specific",
        SUBSTANTIVE: "level_substantive",
        FILES_ONLY: "level_files_only",
        MENTION_ONLY: "level_mention_only",
        ABSENT: "level_absent",
        UNKNOWN: "level_unknown",
    }[tests.level]
    awards.append(Award("test_evidence", policy.anchor("test_evidence", level_anchor),
                        level_anchor, tests.reason))
    if tests.ci_configured:
        awards.append(Award(
            "test_evidence", policy.anchor("test_evidence", "ci_configured"), "ci_configured",
            f"{tests.ci_workflow} configures a test runner. This says the tests are set up to "
            f"run; no run outcome was observed, and none is claimed.",
        ))
    if tests.assertion_files >= 3:
        awards.append(Award(
            "test_evidence", policy.anchor("test_evidence", "three_or_more_asserting_files"),
            "three_or_more_asserting_files", f"{tests.assertion_files} inspected files assert",
        ))
    return awards


def _score_substance(policy: Policy, substance: SubstanceEvidence,
                     scope: ScopeEvidence) -> list[Award]:
    awards = []
    for threshold, anchor in ((60, "code_files_60"), (20, "code_files_20"), (5, "code_files_5")):
        if substance.code_files >= threshold:
            awards.append(Award("implementation_substance",
                                policy.anchor("implementation_substance", anchor), anchor,
                                f"{substance.code_files} implementation files listed"))
            break
    if scope.persistence_paths:
        awards.append(Award(
            "implementation_substance",
            policy.anchor("implementation_substance", "store_written_in_read_code"),
            "store_written_in_read_code",
            "store writes in " + ", ".join(scope.persistence_paths[:3]),
        ))
    if scope.memory_paths:
        awards.append(Award(
            "implementation_substance",
            policy.anchor("implementation_substance", "memory_named_implementation_paths"),
            "memory_named_implementation_paths",
            "memory-named paths: " + ", ".join(scope.memory_paths[:3]),
        ))
    return awards


def _score_contribution(policy: Policy, facts: dict[str, Any], coverage: dict[str, str],
                        decision: Decision) -> list[Award]:
    awards = []
    people = facts.get("contributors_apparently_non_bot")
    if people is None:
        decision.limitations.append(
            f"contributor count {coverage.get('contributors', 'unavailable')}; no "
            f"participation points awarded rather than assuming zero"
        )
    else:
        bots = facts.get("contributors_bot") or 0
        note = (f"{people} apparently non-bot contributor(s) in the sampled page"
                + (f", {bots} known bot account(s) counted separately" if bots else "")
                + ". GitHub's account type does not prove a person, so this is "
                  "'apparently non-bot', not 'human'.")
        for threshold, anchor in ((4, "four_apparently_non_bot_contributors"),
                                  (2, "two_apparently_non_bot_contributors")):
            if people >= threshold:
                awards.append(Award("contribution_maintenance",
                                    policy.anchor("contribution_maintenance", anchor),
                                    anchor, note))
                break

    external = facts.get("merged_external_pulls")
    if external:
        for threshold, anchor in ((3, "three_merged_external_pulls"),
                                  (1, "one_merged_external_pull")):
            if external >= threshold:
                awards.append(Award(
                    "contribution_maintenance",
                    policy.anchor("contribution_maintenance", anchor), anchor,
                    f"{external} merged pull request(s) from outside the owner account in the "
                    f"{facts.get('closed_pulls_sampled')}-PR sample",
                ))
                break

    newest, oldest = facts.get("commit_sample_newest"), facts.get("commit_sample_oldest")
    if newest and oldest:
        span = (_days_since(oldest) or 0) - (_days_since(newest) or 0)
        if span >= 60:
            awards.append(Award(
                "contribution_maintenance",
                policy.anchor("contribution_maintenance", "commit_sample_spans_60_days"),
                "commit_sample_spans_60_days",
                f"the {facts.get('commit_sample')}-commit sample spans {span:.0f} days",
            ))
    pushed = _days_since(facts.get("pushed_at"))
    if pushed is not None and pushed <= 180:
        awards.append(Award(
            "contribution_maintenance",
            policy.anchor("contribution_maintenance", "pushed_within_180_days"),
            "pushed_within_180_days", f"last push {pushed:.0f} days ago",
        ))
    return awards


def _score_atlas_value(policy: Policy, blob_texts: dict[str, str], corpus_loaded: bool,
                       decision: Decision) -> list[Award]:
    if not corpus_loaded:
        decision.limitations.append(
            "the atlas corpus could not be loaded, so no novelty or coverage-gap points were "
            "awarded. An unknown novelty is not a distinctive mechanism."
        )
        return []
    rare, common = mechanism_terms(blob_texts)
    awards = []
    found = rare + common
    if found:
        per = policy.anchor("atlas_value", "per_mechanism_term")
        cap = policy.anchor("atlas_value", "mechanism_terms_cap")
        awards.append(Award(
            "atlas_value", min(per * len(found), cap), "per_mechanism_term",
            "vocabulary for " + ", ".join(found) + " appears in inspected implementation code. "
            "This is a lead worth reading, not a finding that the mechanism is implemented.",
        ))
    if rare:
        awards.append(Award(
            "atlas_value", policy.anchor("atlas_value", "rare_mark_vocabulary"),
            "rare_mark_vocabulary",
            "including " + ", ".join(rare) + ", which few systems in the corpus carry",
        ))
    elif common:
        awards.append(Award(
            "atlas_value", policy.anchor("atlas_value", "common_mark_vocabulary_only"),
            "common_mark_vocabulary_only", "scope or audit vocabulary only",
        ))
    return awards


def _score_adoption(policy: Policy, facts: dict[str, Any], decision: Decision) -> list[Award]:
    awards = []
    cap = policy.cap("adoption")
    account_age = _days_since(facts.get("owner_created_at"))
    new_account = account_age is not None and account_age < policy.new_account_days
    if new_account:
        cap = policy.anchor("adoption", "new_account_cap")
        decision.cautions.append(
            f"the owner account is {account_age:.0f} days old, so the public track-record score is "
            f"capped at {cap}. This is a caution about what can be observed, not a spam label: "
            f"strong code and tests outweigh a sparse public profile, and private history is "
            f"unavailable rather than absent."
        )

    stars = facts.get("stars")
    if stars is not None:
        points = min(
            int(round(math.log10(stars + 1) * policy.anchor("adoption", "stars_log_multiplier"))),
            policy.anchor("adoption", "stars_cap"),
        )
        if points:
            awards.append(Award("adoption", points, "stars_log_multiplier",
                                f"{stars} stars, logarithmically capped at "
                                f"{policy.anchor('adoption', 'stars_cap')} of 100 total points"))
    forks = facts.get("forks")
    if forks is not None and forks >= 5:
        awards.append(Award("adoption", policy.anchor("adoption", "five_or_more_forks"),
                            "five_or_more_forks", f"{forks} forks"))
    repos = facts.get("owner_public_repos")
    if repos is not None and repos >= 3 and account_age is not None and account_age >= 180:
        awards.append(Award(
            "adoption", policy.anchor("adoption", "established_owner"), "established_owner",
            f"the owner account is {account_age:.0f} days old with {repos} public repositories. "
            f"Account age measures the account, not developer experience, and public repository "
            f"ownership is not the same as contributing elsewhere.",
        ))

    total = sum(award.points for award in awards)
    if total > cap:
        scale = cap / total
        for award in awards:
            award.points = int(award.points * scale)
    return awards
