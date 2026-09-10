#!/usr/bin/env python3
"""Deterministic next-action resolver for the 50PLUS 3-agent council autopilot.

Reads a JSON snapshot of GitHub state (open issues, open PRs, checks and
deployments) and emits exactly one JSON object describing the single next
action, following the resume precedence defined in COUNCIL.md and
.github/autopilot-policy.json.

This script makes no network calls and calls no LLM. It is pure stdlib and
is safe to run in CI or a scheduled workflow. It never decides to merge,
delete a branch, or touch secrets/billing/DNS/permissions; those remain
human-only actions (see needs-human handling below).

Usage:
    python3 scripts/autopilot_status.py <snapshot.json>
    cat snapshot.json | python3 scripts/autopilot_status.py -
    python3 scripts/autopilot_status.py --self-test
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "autopilot-policy.json"

DEFAULT_POLICY: dict[str, Any] = {
    "retry_limit": 3,
    "stale_ttl_hours": 48,
    "human_only_path_patterns": [
        "*secret*",
        "*credential*",
        "*.env",
        "*.pem",
        "*.key",
        "CNAME",
    ],
    "risk_elevating_path_patterns": [
        {"pattern": ".github/workflows/*", "min_risk": "high"},
        {"pattern": ".github/autopilot-policy.json", "min_risk": "high"},
        {"pattern": "scripts/*preflight*", "min_risk": "medium"},
        {"pattern": "robots.txt", "min_risk": "medium"},
        {"pattern": "sitemap.xml", "min_risk": "medium"},
    ],
    "council_checkpoints": {
        "pre_implementation_required_for_risk": ["medium", "high"],
        "pre_merge_review_required_for_risk": ["medium", "high"],
        "low_risk_review_unavailable_may_proceed": True,
    },
    "status_labels": {
        "needs-human": "status:needs-human",
    },
    "priority_order": ["high", "medium", "low"],
}


def load_policy() -> dict[str, Any]:
    if POLICY_PATH.exists():
        try:
            return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return DEFAULT_POLICY


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


RISK_RANK = {"low": 0, "medium": 1, "high": 2}


def touches_human_only_path(changed_files: list[str], patterns: list[str]) -> str | None:
    """Return the first changed file that matches a genuinely human-only path pattern.

    These patterns are restricted to paths that are unambiguously one of the
    human-only categories in COUNCIL.md (secrets/credentials, DNS ownership),
    so a match here forces needs-human directly. Ordinary CI/workflow/content
    paths must NOT be in this list; use risk_elevating_path_patterns instead.
    """
    for path in changed_files:
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                return path
    return None


def elevated_risk(changed_files: list[str], base_risk: str,
                   risk_elevating_patterns: list[dict[str, Any]]) -> tuple[str, str | None]:
    """Return (effective_risk, matched_pattern_or_None).

    Paths matching risk_elevating_path_patterns raise the PR's risk tier (and
    therefore trigger the existing council-review requirement for medium/high
    risk) but do not by themselves force human-only escalation.
    """
    best_risk = base_risk
    best_pattern: str | None = None
    for entry in risk_elevating_patterns:
        pattern = entry.get("pattern")
        min_risk = entry.get("min_risk", "low")
        if not pattern:
            continue
        for path in changed_files:
            if fnmatch.fnmatch(path, pattern):
                if RISK_RANK.get(min_risk, 0) > RISK_RANK.get(best_risk, 0):
                    best_risk = min_risk
                    best_pattern = pattern
                break
    return best_risk, best_pattern


def action(action_name: str, reason: str, state: str, target: dict[str, Any] | None = None,
           risk: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "action": action_name,
        "state": state,
        "reason": reason,
    }
    if target is not None:
        result["target"] = target
    if risk is not None:
        result["risk"] = risk
    return result


def issue_priority_rank(issue: dict[str, Any], priority_order: list[str]) -> int:
    priority = issue.get("priority", "low")
    if priority not in priority_order:
        priority = "low"
    return priority_order.index(priority)


def has_label(entity: dict[str, Any], label: str) -> bool:
    return label in entity.get("labels", [])


def open_prs_for_issue(prs: list[dict[str, Any]], issue_number: int) -> list[dict[str, Any]]:
    return [p for p in prs if p.get("state") == "open" and p.get("issue_number") == issue_number]


def pr_checks_summary(pr: dict[str, Any]) -> str:
    """Return 'failure', 'pending', or 'success' for a PR's check runs."""
    checks = pr.get("checks", [])
    if not checks:
        return "pending"
    if any(c.get("conclusion") == "failure" for c in checks):
        return "failure"
    if any(c.get("status") != "completed" for c in checks):
        return "pending"
    if all(c.get("conclusion") == "success" for c in checks):
        return "success"
    return "pending"


def deployment_for_pr(deployments: list[dict[str, Any]], pr_number: int) -> dict[str, Any] | None:
    matches = [d for d in deployments if d.get("pr_number") == pr_number]
    if not matches:
        return None
    # Deterministic: most recent by 'sha' order in the list (last wins).
    return matches[-1]


def live_verified_for_pr(live_verification: dict[str, Any], pr_number: int) -> bool:
    entry = live_verification.get(str(pr_number)) or live_verification.get(pr_number)
    if not entry:
        return False
    return bool(entry.get("verified"))


def resolve_pr_action(pr: dict[str, Any], policy: dict[str, Any],
                       deployments: list[dict[str, Any]],
                       live_verification: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve the action for a single open-or-merged, not-yet-done PR.

    Returns None if this PR is already fully done (merged, deployed, live-verified).
    """
    number = pr.get("number")
    issue_number = pr.get("issue_number")
    target_base = {"type": "pull_request", "number": number, "issue_number": issue_number}

    # Explicit human-only flag (set by PM/implementer when a change is genuinely
    # one of the COUNCIL.md human-only categories) always wins, regardless of path.
    human_only_reason = pr.get("human_only_reason")
    if human_only_reason:
        return action(
            "await_human",
            f"PR #{number} is explicitly flagged human-only ({human_only_reason}); "
            "no autonomous action until a human resolves it.",
            "needs-human",
            target_base,
            risk="high",
        )

    # Genuinely unambiguous human-only paths (secrets/credentials/DNS ownership
    # files) also force needs-human directly.
    human_only_patterns = policy.get("human_only_path_patterns", [])
    hit = touches_human_only_path(pr.get("changed_files", []), human_only_patterns)
    if hit:
        return action(
            "await_human",
            f"PR #{number} changes human-only path '{hit}'; human-only escalation required before proceeding.",
            "needs-human",
            target_base,
            risk="high",
        )

    # Ordinary CI/workflow/content paths only elevate the risk tier, which
    # feeds the existing council-review requirement below; they do not by
    # themselves stop autonomous progress.
    risk_elevating_patterns = policy.get("risk_elevating_path_patterns", [])
    risk, elevating_pattern = elevated_risk(
        pr.get("changed_files", []), pr.get("risk", "low"), risk_elevating_patterns
    )

    if not pr.get("merged", False):
        checks_state = pr_checks_summary(pr)
        retry_count = pr.get("retry_count", 0)
        retry_limit = policy.get("retry_limit", 3)

        if checks_state == "failure":
            if retry_count >= retry_limit:
                return action(
                    "flag_blocked_retry_exhausted",
                    f"PR #{number} has failing checks and exhausted its retry budget "
                    f"({retry_count}/{retry_limit}); same owner must escalate, not keep retrying.",
                    "blocked",
                    target_base,
                    risk=risk,
                )
            return action(
                "resume_pr_fix_ci",
                f"PR #{number} has failing checks with retry budget remaining "
                f"({retry_count}/{retry_limit}); the same owner must fix CI before any new task starts.",
                "ci" if retry_count == 0 else "retry",
                target_base,
                risk=risk,
            )

        if checks_state == "pending":
            return action(
                "wait_for_ci",
                f"PR #{number} checks are still running; wait for completion before other action.",
                "ci",
                target_base,
                risk=risk,
            )

        # checks_state == "success"
        review_status = pr.get("review_status", "none")
        review_required = risk in policy["council_checkpoints"]["pre_merge_review_required_for_risk"]

        if review_status == "changes_requested":
            return action(
                "address_review_feedback",
                f"PR #{number} has requested changes from review; the same owner must address them.",
                "review",
                target_base,
                risk=risk,
            )

        if review_status in ("none", "requested") and review_required:
            elevation_note = (
                f" (elevated by path '{elevating_pattern}')" if elevating_pattern else ""
            )
            return action(
                "resume_pr_request_review",
                f"PR #{number} is risk:{risk}{elevation_note} and requires recorded council review before merge.",
                "review",
                target_base,
                risk=risk,
            )

        if review_status == "unavailable":
            if review_required:
                return action(
                    "flag_blocked_reviewer_unavailable",
                    f"PR #{number} is risk:{risk} and cannot merge without review; "
                    "reviewer is recorded unavailable, so this is blocked, not merged.",
                    "blocked",
                    target_base,
                    risk=risk,
                )
            if not policy["council_checkpoints"].get("low_risk_review_unavailable_may_proceed", True):
                return action(
                    "resume_pr_request_review",
                    f"PR #{number} review is unavailable and policy requires review regardless of risk.",
                    "review",
                    target_base,
                    risk=risk,
                )
            # low risk + recorded unavailable review: allowed to proceed to merge readiness.

        if review_status in ("none",) and not review_required:
            # Low risk with no review recorded yet and not explicitly marked unavailable:
            # still worth requesting, but does not block merge readiness reporting.
            return action(
                "resume_pr_request_review",
                f"PR #{number} is risk:{risk}; requesting review before confirming merge readiness.",
                "review",
                target_base,
                risk=risk,
            )

        return action(
            "resume_pr_confirm_merge_ready",
            f"PR #{number} checks pass and review is satisfied or recorded unavailable at low risk; "
            "ready for a human to merge.",
            "merge",
            target_base,
            risk=risk,
        )

    # PR is merged: track deploy and live-verify.
    deployment = deployment_for_pr(deployments, number)
    if deployment is None or deployment.get("status") == "in_progress":
        return action(
            "verify_deploy",
            f"PR #{number} is merged; deploy status is not yet confirmed successful.",
            "deploy",
            target_base,
            risk=risk,
        )
    if deployment.get("status") == "failure":
        return action(
            "flag_blocked_deploy_failed",
            f"PR #{number} merged but the deploy workflow failed; needs same-owner investigation.",
            "blocked",
            target_base,
            risk=risk,
        )
    # deployment succeeded
    if not live_verified_for_pr(live_verification, number):
        return action(
            "verify_live_production",
            f"PR #{number} deployed successfully; production has not yet been live-verified.",
            "live-verify",
            target_base,
            risk=risk,
        )

    return None  # fully done


def detect_duplicate_active(prs: list[dict[str, Any]]) -> dict[str, Any] | None:
    by_issue: dict[int, list[dict[str, Any]]] = {}
    for pr in prs:
        if pr.get("state") != "open":
            continue
        issue_number = pr.get("issue_number")
        by_issue.setdefault(issue_number, []).append(pr)
    for issue_number in sorted(k for k in by_issue if k is not None):
        group = by_issue[issue_number]
        if len(group) > 1:
            numbers = sorted(p["number"] for p in group)
            return action(
                "flag_duplicate_active",
                f"Issue #{issue_number} has {len(group)} open PRs {numbers}; "
                "duplicate active implementation must be flagged, not silently merged.",
                "needs-human",
                {"type": "issue", "number": issue_number, "duplicate_prs": numbers},
                risk="high",
            )
    return None


def detect_stale(issues: list[dict[str, Any]], prs: list[dict[str, Any]],
                  now: datetime, ttl_hours: int) -> dict[str, Any] | None:
    active_status_labels = {"status:active", "status:ci", "status:review", "status:merge"}
    candidates: list[tuple[str, int, datetime]] = []

    for issue in issues:
        if issue.get("state") != "open":
            continue
        if not any(lbl in active_status_labels for lbl in issue.get("labels", [])):
            continue
        if open_prs_for_issue(prs, issue["number"]):
            continue  # progress is tracked via the PR instead
        updated = parse_time(issue.get("updated_at"))
        if updated is not None:
            candidates.append(("issue", issue["number"], updated))

    for pr in prs:
        if pr.get("state") != "open":
            continue
        updated = parse_time(pr.get("updated_at"))
        if updated is not None:
            candidates.append(("pull_request", pr["number"], updated))

    for kind, number, updated in sorted(candidates, key=lambda c: (c[2], c[1])):
        age_hours = (now - updated).total_seconds() / 3600.0
        if age_hours >= ttl_hours:
            return action(
                "flag_stale_active",
                f"{kind} #{number} has had no update for {age_hours:.1f}h "
                f"(TTL {ttl_hours}h); must be surfaced before other work proceeds on it.",
                "needs-human",
                {"type": kind, "number": number, "age_hours": round(age_hours, 1)},
                risk="medium",
            )
    return None


def decide(snapshot: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    issues = snapshot.get("issues", [])
    prs = snapshot.get("pull_requests", [])
    deployments = snapshot.get("deployments", [])
    live_verification = snapshot.get("live_verification", {})
    now = parse_time(snapshot.get("now")) or datetime.now(timezone.utc)

    needs_human_label = policy.get("status_labels", {}).get("needs-human", "status:needs-human")

    open_issues = [i for i in issues if i.get("state") == "open"]
    open_prs = [p for p in prs if p.get("state") == "open"]
    all_relevant_prs = [p for p in prs if p.get("state") == "open" or p.get("merged")]

    # Step 1: anything already explicitly flagged needs-human wins outright.
    flagged = sorted(
        [e for e in open_issues + open_prs if has_label(e, needs_human_label)],
        key=lambda e: (0 if "issue_number" not in e else 1, e.get("number", 0)),
    )
    if flagged:
        entity = flagged[0]
        kind = "pull_request" if "issue_number" in entity else "issue"
        return action(
            "await_human",
            f"{kind} #{entity['number']} is already labeled {needs_human_label}; "
            "no autonomous action until a human resolves it.",
            "needs-human",
            {"type": kind, "number": entity["number"]},
            risk="high",
        )

    # Step 2: unfinished PRs always outrank starting new ready-issue work,
    # EXCEPT PRs belonging to an Issue that currently has more than one open
    # PR. Resolving any single one of those PRs here would mean silently
    # picking a winner among duplicates, which the single-owner rule in
    # COUNCIL.md forbids. Those PRs are deliberately left unresolved here so
    # step 3's duplicate detection is the one that surfaces them.
    open_pr_counts_by_issue: dict[int, int] = {}
    for pr in open_prs:
        issue_number = pr.get("issue_number")
        open_pr_counts_by_issue[issue_number] = open_pr_counts_by_issue.get(issue_number, 0) + 1
    duplicate_issue_numbers = {k for k, v in open_pr_counts_by_issue.items() if v > 1}

    unfinished_results = []
    for pr in sorted(all_relevant_prs, key=lambda p: p.get("number", 0)):
        if pr.get("state") == "open" and pr.get("issue_number") in duplicate_issue_numbers:
            continue
        result = resolve_pr_action(pr, policy, deployments, live_verification)
        if result is not None:
            unfinished_results.append(result)
    if unfinished_results:
        # needs-human results (e.g. sensitive path) outrank ordinary resume actions.
        human = [r for r in unfinished_results if r["state"] == "needs-human"]
        if human:
            return human[0]
        return unfinished_results[0]

    # Step 3: duplicate / stale active work must be surfaced before new work.
    dup = detect_duplicate_active(prs)
    if dup:
        return dup
    stale = detect_stale(issues, prs, now, policy.get("stale_ttl_hours", 48))
    if stale:
        return stale

    # Step 4: resume issues whose blocker has resolved.
    for issue in sorted(open_issues, key=lambda i: i.get("number", 0)):
        if not has_label(issue, "status:blocked"):
            continue
        deps = issue.get("dependencies", [])
        open_issue_numbers = {i["number"] for i in open_issues}
        unresolved = [d for d in deps if d in open_issue_numbers]
        if not unresolved:
            return action(
                "resume_blocked_issue",
                f"Issue #{issue['number']} was blocked on dependencies {deps}, now resolved; resume it.",
                "ready",
                {"type": "issue", "number": issue["number"]},
                risk=issue.get("risk", "low"),
            )

    # Step 5: pick the next ready issue by priority, then dependency-free, then oldest.
    priority_order = policy.get("priority_order", ["high", "medium", "low"])
    open_issue_numbers = {i["number"] for i in open_issues}
    ready_candidates = []
    for issue in open_issues:
        if not has_label(issue, "status:ready"):
            continue
        deps = issue.get("dependencies", [])
        if any(d in open_issue_numbers for d in deps):
            continue  # dependency still open; cannot start
        ready_candidates.append(issue)

    if ready_candidates:
        ready_candidates.sort(
            key=lambda i: (
                issue_priority_rank(i, priority_order),
                parse_time(i.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
                i.get("number", 0),
            )
        )
        chosen = ready_candidates[0]
        risk = chosen.get("risk", "low")
        council_required = chosen.get("council_required", False) or risk in policy["council_checkpoints"][
            "pre_implementation_required_for_risk"
        ]
        if council_required:
            return action(
                "start_council",
                f"Issue #{chosen['number']} is risk:{risk} (or explicitly marked council_required); "
                "pre-implementation council checkpoint is required before coding starts.",
                "council",
                {"type": "issue", "number": chosen["number"]},
                risk=risk,
            )
        return action(
            "start_active",
            f"Issue #{chosen['number']} is risk:{risk}, ready, and has no unmet dependencies; "
            "the implementer may start a dedicated branch.",
            "active",
            {"type": "issue", "number": chosen["number"]},
            risk=risk,
        )

    return action(
        "no_action_clean",
        "No unfinished PR, no flagged issue, no stale/duplicate work, and no ready issue with met "
        "dependencies. Nothing to do.",
        "done",
    )


# ---------------------------------------------------------------------------
# Self-test scenarios
# ---------------------------------------------------------------------------

def _scenarios() -> list[tuple[str, dict[str, Any], str]]:
    now = "2026-09-10T12:00:00Z"

    def base_issue(number: int, **overrides: Any) -> dict[str, Any]:
        issue = {
            "number": number,
            "state": "open",
            "labels": ["status:ready"],
            "priority": "medium",
            "risk": "low",
            "dependencies": [],
            "created_at": "2026-09-01T00:00:00Z",
            "updated_at": "2026-09-01T00:00:00Z",
        }
        issue.update(overrides)
        return issue

    def base_pr(number: int, issue_number: int, **overrides: Any) -> dict[str, Any]:
        pr = {
            "number": number,
            "issue_number": issue_number,
            "state": "open",
            "merged": False,
            "labels": [],
            "risk": "low",
            "changed_files": ["index.html"],
            "checks": [{"name": "PR checks", "status": "completed", "conclusion": "success"}],
            "retry_count": 0,
            "review_status": "none",
            "created_at": "2026-09-05T00:00:00Z",
            "updated_at": "2026-09-05T00:00:00Z",
        }
        pr.update(overrides)
        return pr

    scenarios: list[tuple[str, dict[str, Any], str]] = []

    scenarios.append((
        "empty_snapshot_clean",
        {"now": now, "issues": [], "pull_requests": [], "deployments": [], "live_verification": {}},
        "no_action_clean",
    ))

    scenarios.append((
        "needs_human_flagged_issue_wins",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:needs-human"])],
            "pull_requests": [],
        },
        "await_human",
    ))

    scenarios.append((
        "unfinished_pr_outranks_new_ready_issue",
        {
            "now": now,
            "issues": [
                base_issue(80, labels=["status:active"]),
                base_issue(81, labels=["status:ready"], priority="high"),
            ],
            "pull_requests": [base_pr(90, 80, checks=[
                {"name": "PR checks", "status": "completed", "conclusion": "failure"}
            ])],
        },
        "resume_pr_fix_ci",
    ))

    scenarios.append((
        "ci_failure_within_retry_budget",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, retry_count=1, checks=[
                {"name": "PR checks", "status": "completed", "conclusion": "failure"}
            ])],
        },
        "resume_pr_fix_ci",
    ))

    scenarios.append((
        "ci_failure_retry_exhausted",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, retry_count=3, checks=[
                {"name": "PR checks", "status": "completed", "conclusion": "failure"}
            ])],
        },
        "flag_blocked_retry_exhausted",
    ))

    scenarios.append((
        "checks_pending_wait",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, checks=[
                {"name": "PR checks", "status": "in_progress", "conclusion": None}
            ])],
        },
        "wait_for_ci",
    ))

    scenarios.append((
        "medium_risk_requires_review",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"], risk="medium")],
            "pull_requests": [base_pr(90, 80, risk="medium")],
        },
        "resume_pr_request_review",
    ))

    scenarios.append((
        "medium_risk_review_unavailable_blocks",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"], risk="medium")],
            "pull_requests": [base_pr(90, 80, risk="medium", review_status="unavailable")],
        },
        "flag_blocked_reviewer_unavailable",
    ))

    scenarios.append((
        "low_risk_review_unavailable_proceeds_to_merge",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"], risk="low")],
            "pull_requests": [base_pr(90, 80, risk="low", review_status="unavailable")],
        },
        "resume_pr_confirm_merge_ready",
    ))

    scenarios.append((
        "approved_pr_ready_for_human_merge",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, review_status="approved")],
        },
        "resume_pr_confirm_merge_ready",
    ))

    scenarios.append((
        "merged_pr_needs_deploy_verification",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:merge"])],
            "pull_requests": [base_pr(90, 80, merged=True, review_status="approved")],
            "deployments": [],
        },
        "verify_deploy",
    ))

    scenarios.append((
        "deployed_pr_needs_live_verification",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:deploy"])],
            "pull_requests": [base_pr(90, 80, merged=True, review_status="approved")],
            "deployments": [{"pr_number": 90, "status": "success", "sha": "abc123"}],
            "live_verification": {},
        },
        "verify_live_production",
    ))

    scenarios.append((
        "fully_done_pr_falls_through_to_clean",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:done"], state="closed")],
            "pull_requests": [base_pr(90, 80, merged=True, state="closed", review_status="approved")],
            "deployments": [{"pr_number": 90, "status": "success", "sha": "abc123"}],
            "live_verification": {"90": {"verified": True}},
        },
        "no_action_clean",
    ))

    scenarios.append((
        "workflow_path_elevates_risk_not_human_only",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, changed_files=[".github/workflows/deploy-pages.yml"])],
        },
        "resume_pr_request_review",
    ))

    scenarios.append((
        "robots_txt_change_elevates_risk_not_human_only",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, changed_files=["robots.txt"])],
        },
        "resume_pr_request_review",
    ))

    scenarios.append((
        "human_only_path_forces_needs_human",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(90, 80, changed_files=["CNAME"])],
        },
        "await_human",
    ))

    scenarios.append((
        "explicit_human_only_reason_forces_needs_human",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [base_pr(
                90, 80,
                changed_files=["index.html"],
                human_only_reason="billing_or_paid_usage_configuration",
            )],
        },
        "await_human",
    ))

    scenarios.append((
        "duplicate_active_prs_flagged",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:active"])],
            "pull_requests": [
                base_pr(90, 80, checks=[]),
                base_pr(91, 80, checks=[]),
            ],
        },
        "flag_duplicate_active",
    ))

    scenarios.append((
        "stale_active_issue_without_pr_flagged",
        {
            "now": now,
            "issues": [base_issue(
                80, labels=["status:active"],
                updated_at="2026-09-01T00:00:00Z",
            )],
            "pull_requests": [],
        },
        "flag_stale_active",
    ))

    scenarios.append((
        "blocked_issue_resumes_when_dependency_closed",
        {
            "now": now,
            "issues": [
                base_issue(79, labels=["status:done"], state="closed"),
                base_issue(80, labels=["status:blocked"], dependencies=[79]),
            ],
            "pull_requests": [],
        },
        "resume_blocked_issue",
    ))

    scenarios.append((
        "ready_issue_with_open_dependency_is_skipped",
        {
            "now": now,
            "issues": [
                base_issue(79, labels=["status:ready"], priority="high"),
                base_issue(80, labels=["status:ready"], priority="high", dependencies=[79]),
            ],
            "pull_requests": [],
        },
        "start_active",
    ))

    scenarios.append((
        "highest_priority_ready_issue_chosen",
        {
            "now": now,
            "issues": [
                base_issue(79, labels=["status:ready"], priority="low"),
                base_issue(80, labels=["status:ready"], priority="high"),
            ],
            "pull_requests": [],
        },
        "start_active",
    ))

    scenarios.append((
        "medium_risk_ready_issue_requires_council",
        {
            "now": now,
            "issues": [base_issue(80, labels=["status:ready"], risk="medium")],
            "pull_requests": [],
        },
        "start_council",
    ))

    return scenarios


def run_self_test() -> int:
    policy = load_policy()
    failures = 0
    scenarios = _scenarios()
    for name, snapshot, expected_action in scenarios:
        result = decide(snapshot, policy)
        got = result.get("action")
        status = "PASS" if got == expected_action else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {name}: expected={expected_action} got={got}")

    print(f"\n{len(scenarios) - failures}/{len(scenarios)} scenarios passed.")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", help="Path to a JSON snapshot file, or '-' for stdin.")
    parser.add_argument("--self-test", action="store_true", help="Run embedded deterministic scenarios.")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if not args.snapshot:
        parser.error("snapshot path (or '-') is required unless --self-test is given")

    if args.snapshot == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.snapshot).read_text(encoding="utf-8")

    snapshot = json.loads(raw)
    policy = load_policy()
    result = decide(snapshot, policy)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
