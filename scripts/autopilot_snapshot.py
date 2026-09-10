#!/usr/bin/env python3
"""Builds a GitHub-state snapshot for scripts/autopilot_status.py.

`autopilot_status.py` computes the single deterministic next action from a
GitHub-shaped snapshot (issues/PRs/checks/deployments), but something has to
turn actual `gh` CLI output into that shape first. That is this script's only
job: it is pure data transformation, calls no LLM, and makes no merge/deploy/
branch/secret decision of its own — it only maps evidence GitHub already
recorded into the resolver's input schema (see COUNCIL.md and
.github/autopilot-policy.json).

Two modes:
  python3 scripts/autopilot_snapshot.py --repo OWNER/NAME   # live fetch via `gh`
  python3 scripts/autopilot_snapshot.py --self-test          # pure-logic tests, no network

`live_verification` is intentionally left empty by this script: production
live-verification is a human/PR-evidence step per COUNCIL.md, not something
inferred from Issue/PR/check/deploy metadata alone. Because this snapshot
never has live-verification evidence of its own, a merged PR that is done
(deployed and live-verified) must be labeled `status:done` on GitHub once
that verification happens (PM/implementer responsibility, per COUNCIL.md's
`live-verify` -> `done` transition); this script only carries a merged PR
forward into the snapshot when it still carries one of the unfinished
autopilot status labels (`status:merge`/`status:deploy`/`status:live-verify`/
`status:retry`/`status:blocked`). A merged PR labeled `status:done`, or with
no autopilot status label at all (e.g. historical PRs that predate this
labeling convention), is excluded so old merged work cannot get stuck
looking permanently unfinished and block new work from being picked up.

Issue Form dropdown/checkbox values (Priority, Risk, Council checkpoint,
Human-only condition) live in the rendered Issue body, not as labels, unless
someone also applies the matching label by hand. This script parses those
body sections deterministically; an explicit label on the Issue always
overrides the body value for that field, since labels are the more visible,
more easily audited signal once someone has taken the time to apply one.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "autopilot-policy.json"

DEFAULT_POLICY: dict[str, Any] = {
    "risk_labels": {"low": "risk:low", "medium": "risk:medium", "high": "risk:high"},
    "priority_labels": {"high": "priority:high", "medium": "priority:medium", "low": "priority:low"},
    "priority_order": ["high", "medium", "low"],
    "status_labels": {"review_unavailable": "review-unavailable"},
}

RISK_ORDER = ["high", "medium", "low"]

# Merged PRs are only carried forward into the snapshot while one of these
# states is still unfinished; see build_snapshot()'s merged-PR filter and the
# module docstring.
MERGED_PR_UNFINISHED_STATES = ("merge", "deploy", "live-verify", "retry", "blocked")

PR_JSON_FIELDS = (
    "number,title,labels,updatedAt,createdAt,body,url,state,files,"
    "reviewDecision,statusCheckRollup,mergeCommit"
)
ISSUE_JSON_FIELDS = "number,title,labels,updatedAt,createdAt,body,url,state"

CLOSING_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s*#(\d+)", re.IGNORECASE)
DEPENDENCIES_SECTION_RE = re.compile(
    r"###\s*Dependencies\s*\n+([^\n]*)", re.IGNORECASE
)
CHECKED_BOX_RE = re.compile(r"-\s*\[[xX]\]")


def _section_re(heading: str) -> re.Pattern[str]:
    # Matches the rendered Issue Form body block for `heading` up to (but not
    # including) the next "### " heading or end of body.
    return re.compile(rf"###\s*{re.escape(heading)}\s*\n+(.*?)(?=\n###\s|\Z)", re.IGNORECASE | re.DOTALL)


def parse_body_dropdown(body: str | None, heading: str, valid_values: set[str]) -> str | None:
    if not body:
        return None
    match = _section_re(heading).search(body)
    if not match:
        return None
    lines = [ln.strip() for ln in match.group(1).strip().splitlines() if ln.strip()]
    if not lines:
        return None
    value = lines[0].lower()
    return value if value in valid_values else None


def parse_body_checkbox(body: str | None, heading: str) -> bool:
    if not body:
        return False
    match = _section_re(heading).search(body)
    if not match:
        return False
    return bool(CHECKED_BOX_RE.search(match.group(1)))


def has_any_label(names: list[str], label_map: dict[str, str]) -> bool:
    return any(label in names for label in label_map.values())


def load_policy() -> dict[str, Any]:
    if POLICY_PATH.exists():
        try:
            return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return DEFAULT_POLICY


def label_names(entity: dict[str, Any]) -> list[str]:
    return [l["name"] for l in entity.get("labels", []) if isinstance(l, dict) and "name" in l]


def pick_from_label_map(names: list[str], label_map: dict[str, str], order: list[str], default: str) -> str:
    reverse = {v: k for k, v in label_map.items()}
    present = {reverse[n] for n in names if n in reverse}
    for tier in order:
        if tier in present:
            return tier
    return default


def merged_pr_carries_unfinished_status(raw: dict[str, Any], policy: dict[str, Any]) -> bool:
    """True if a merged PR still carries one of MERGED_PR_UNFINISHED_STATES's labels.

    A merged PR labeled status:done (verification complete) or with no
    autopilot status label at all (historical PRs predating this labeling
    convention) is not carried forward, so old merged work cannot get stuck
    looking permanently unfinished and block new work from being picked up.
    """
    names = label_names(raw)
    status_labels = policy.get("status_labels", {})
    unfinished_labels = {status_labels.get(state, f"status:{state}") for state in MERGED_PR_UNFINISHED_STATES}
    return any(name in unfinished_labels for name in names)


def stronger_risk(a: str, b: str) -> str:
    """Return whichever of two risk tiers is more severe (RISK_ORDER: high > medium > low)."""
    rank_a = RISK_ORDER.index(a) if a in RISK_ORDER else len(RISK_ORDER)
    rank_b = RISK_ORDER.index(b) if b in RISK_ORDER else len(RISK_ORDER)
    return a if rank_a <= rank_b else b


def parse_linked_issue(body: str | None) -> int | None:
    if not body:
        return None
    match = CLOSING_RE.search(body)
    return int(match.group(1)) if match else None


def parse_dependencies(body: str | None) -> list[int]:
    if not body:
        return []
    match = DEPENDENCIES_SECTION_RE.search(body)
    if not match:
        return []
    line = match.group(1).strip()
    if not line or line.lower() == "_no response_":
        return []
    return [int(n) for n in re.findall(r"\d+", line)]


def normalize_review_status(pr: dict[str, Any], names: list[str], policy: dict[str, Any]) -> str:
    unavailable_label = policy.get("status_labels", {}).get("review_unavailable", "review-unavailable")
    if unavailable_label in names:
        return "unavailable"
    decision = (pr.get("reviewDecision") or "").upper()
    return {
        "APPROVED": "approved",
        "CHANGES_REQUESTED": "changes_requested",
        "REVIEW_REQUIRED": "requested",
    }.get(decision, "none")


def normalize_checks(rollup: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    checks = []
    for item in rollup or []:
        if "state" in item and "status" not in item:
            # StatusContext (e.g. an external status check).
            state = (item.get("state") or "").upper()
            status = "completed" if state in ("SUCCESS", "FAILURE", "ERROR") else "in_progress"
            conclusion = {"SUCCESS": "success", "FAILURE": "failure", "ERROR": "failure"}.get(state)
        else:
            # CheckRun.
            status = "completed" if (item.get("status") or "").upper() == "COMPLETED" else "in_progress"
            conclusion_raw = (item.get("conclusion") or "").lower()
            conclusion = conclusion_raw or None
        checks.append({
            "name": item.get("name") or item.get("context") or "unknown",
            "status": status,
            "conclusion": conclusion,
        })
    return checks


def normalize_deployment_state(state: str | None) -> str:
    state = (state or "").lower()
    if state == "success":
        return "success"
    if state in ("failure", "error"):
        return "failure"
    return "in_progress"


def build_issue(raw: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    names = label_names(raw)
    body = raw.get("body")

    priority_labels = policy.get("priority_labels", {})
    if has_any_label(names, priority_labels):
        priority = pick_from_label_map(
            names, priority_labels, policy.get("priority_order", RISK_ORDER[::-1]), "low"
        )
    else:
        priority = parse_body_dropdown(body, "Priority", set(priority_labels)) or "low"

    risk_labels = policy.get("risk_labels", {})
    if has_any_label(names, risk_labels):
        risk = pick_from_label_map(names, risk_labels, RISK_ORDER, "low")
    else:
        risk = parse_body_dropdown(body, "Risk", set(risk_labels)) or "low"

    council_required = parse_body_checkbox(body, "Council checkpoint")
    human_only = parse_body_checkbox(body, "Human-only condition")

    needs_human_label = policy.get("status_labels", {}).get("needs-human", "status:needs-human")
    if human_only and needs_human_label not in names:
        # Synthetic label: the body checkbox is the human-authored signal, but
        # autopilot_status.decide()'s needs-human step only looks at labels, so
        # this makes the checkbox visible to it without requiring a human to
        # also apply the GitHub label by hand.
        names = [*names, needs_human_label]

    return {
        "number": raw["number"],
        "state": (raw.get("state") or "open").lower(),
        "labels": names,
        "priority": priority,
        "risk": risk,
        "council_required": council_required,
        "dependencies": parse_dependencies(body),
        "created_at": raw.get("createdAt"),
        "updated_at": raw.get("updatedAt"),
    }


def build_pull_request(
    raw: dict[str, Any],
    policy: dict[str, Any],
    deployments_by_sha: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    names = label_names(raw)
    merged = bool((raw.get("mergeCommit") or {}).get("oid")) and (raw.get("state") or "").upper() == "MERGED"
    entry: dict[str, Any] = {
        "number": raw["number"],
        "issue_number": parse_linked_issue(raw.get("body")),
        "state": "open" if (raw.get("state") or "").upper() == "OPEN" else "closed",
        "merged": merged,
        "labels": names,
        "risk": pick_from_label_map(names, policy.get("risk_labels", {}), RISK_ORDER, "low"),
        "changed_files": [f.get("path") for f in raw.get("files", []) if f.get("path")],
        "checks": normalize_checks(raw.get("statusCheckRollup")),
        "retry_count": 0,
        "review_status": normalize_review_status(raw, names, policy),
        "created_at": raw.get("createdAt"),
        "updated_at": raw.get("updatedAt"),
    }

    if merged:
        sha = (raw.get("mergeCommit") or {}).get("oid")
        matches = sorted(deployments_by_sha.get(sha, []), key=lambda d: d.get("created_at") or "")
        if matches:
            latest = matches[-1]
            entry["_deployment"] = {
                "pr_number": raw["number"],
                "status": normalize_deployment_state(latest.get("state")),
                "sha": sha,
                "_created_at": latest.get("created_at"),
            }
    return entry


def build_snapshot(
    issues_raw: list[dict[str, Any]],
    open_prs_raw: list[dict[str, Any]],
    merged_prs_raw: list[dict[str, Any]],
    deployments_raw: list[dict[str, Any]],
    now_iso: str,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_policy()

    deployments_by_sha: dict[str, list[dict[str, Any]]] = {}
    for d in deployments_raw:
        sha = d.get("sha")
        if not sha:
            continue
        deployments_by_sha.setdefault(sha, []).append(d)

    issues = [build_issue(i, policy) for i in issues_raw]
    issue_risk_by_number = {i["number"]: i["risk"] for i in issues}

    relevant_merged_prs_raw = [
        p for p in merged_prs_raw if merged_pr_carries_unfinished_status(p, policy)
    ]
    pull_requests_with_meta = [
        build_pull_request(p, policy, deployments_by_sha) for p in open_prs_raw + relevant_merged_prs_raw
    ]
    for pr in pull_requests_with_meta:
        issue_risk = issue_risk_by_number.get(pr.get("issue_number"))
        if issue_risk is not None:
            # A PR's own explicit risk label only wins here if it is already at
            # least as severe as its linked Issue's risk; otherwise the Issue's
            # risk propagates so a low-labeled (or unlabeled) PR under a
            # medium/high-risk Issue still gets that Issue's council/review
            # requirements.
            pr["risk"] = stronger_risk(pr["risk"], issue_risk)

    deployments: list[dict[str, Any]] = []
    for pr in pull_requests_with_meta:
        dep = pr.pop("_deployment", None)
        if dep is not None:
            deployments.append(dep)
    # Deterministic order: oldest first, so autopilot_status.py's "last wins"
    # most-recent-status lookup picks the actual latest deployment.
    deployments.sort(key=lambda d: d.pop("_created_at", "") or "")

    return {
        "now": now_iso,
        "issues": issues,
        "pull_requests": pull_requests_with_meta,
        "deployments": deployments,
        "live_verification": {},
    }


# ---------------------------------------------------------------------------
# Live fetch (network via `gh`) — thin wiring, not unit-tested.
# ---------------------------------------------------------------------------

def _gh_json(args: list[str]) -> Any:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def fetch_raw(repo: str) -> tuple[list[Any], list[Any], list[Any], list[Any]]:
    issues_raw = _gh_json([
        "issue", "list", "--repo", repo, "--state", "open", "--limit", "200",
        "--json", ISSUE_JSON_FIELDS,
    ])
    open_prs_raw = _gh_json([
        "pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
        "--json", PR_JSON_FIELDS,
    ])
    merged_prs_raw = _gh_json([
        "pr", "list", "--repo", repo, "--state", "merged", "--limit", "50",
        "--json", PR_JSON_FIELDS,
    ])

    deployments_raw: list[dict[str, Any]] = []
    try:
        deployments = _gh_json([
            "api", f"repos/{repo}/deployments", "-X", "GET",
            "-f", "environment=github-pages", "-f", "per_page=30",
        ])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        deployments = []
    for d in deployments:
        try:
            statuses = _gh_json([
                "api", f"repos/{repo}/deployments/{d['id']}/statuses", "-f", "per_page=10",
            ])
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            statuses = []
        latest_state = None
        latest_created = ""
        for s in statuses:
            created = s.get("created_at") or ""
            if created >= latest_created:
                latest_created = created
                latest_state = s.get("state")
        deployments_raw.append({
            "sha": d.get("sha"),
            "state": latest_state,
            "created_at": d.get("created_at"),
        })
    return issues_raw, open_prs_raw, merged_prs_raw, deployments_raw


def run_live_fetch(repo: str) -> int:
    issues_raw, open_prs_raw, merged_prs_raw, deployments_raw = fetch_raw(repo)
    now_iso = datetime.now(timezone.utc).isoformat()
    snapshot = build_snapshot(issues_raw, open_prs_raw, merged_prs_raw, deployments_raw, now_iso)
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Self-test scenarios (pure logic, no network)
# ---------------------------------------------------------------------------

def _lbl(*names: str) -> list[dict[str, str]]:
    return [{"name": n} for n in names]


def run_self_test() -> int:
    policy = load_policy()
    failures = 0
    checks: list[tuple[str, Any, Any]] = []

    checks.append(("dependencies_comma_list", parse_dependencies(
        "### Description\n\nsomething\n\n### Dependencies\n\n70, 71\n\n### Acceptance\n\n- [ ] x\n"
    ), [70, 71]))
    checks.append(("dependencies_no_response", parse_dependencies(
        "### Dependencies\n\n_No response_\n"
    ), []))
    checks.append(("dependencies_missing_body", parse_dependencies(None), []))
    checks.append(("dependencies_no_section", parse_dependencies("### Description\n\nsomething\n"), []))

    checks.append(("linked_issue_closes", parse_linked_issue("Closes #42\n\nDetails."), 42))
    checks.append(("linked_issue_fixes_colon", parse_linked_issue("Fixes: #7"), 7))
    checks.append(("linked_issue_none", parse_linked_issue("No reference here."), None))
    checks.append(("linked_issue_empty_body", parse_linked_issue(None), None))

    checks.append(("priority_high_selected", pick_from_label_map(
        ["priority:high", "status:ready"], policy["priority_labels"], policy["priority_order"], "low"
    ), "high"))
    checks.append(("priority_default_low", pick_from_label_map(
        ["status:ready"], policy["priority_labels"], policy["priority_order"], "low"
    ), "low"))
    checks.append(("risk_medium_selected", pick_from_label_map(
        ["risk:medium"], policy["risk_labels"], RISK_ORDER, "low"
    ), "medium"))
    checks.append(("risk_highest_of_multiple_wins", pick_from_label_map(
        ["risk:low", "risk:high"], policy["risk_labels"], RISK_ORDER, "low"
    ), "high"))

    checks.append(("review_status_approved", normalize_review_status(
        {"reviewDecision": "APPROVED"}, [], policy
    ), "approved"))
    checks.append(("review_status_changes_requested", normalize_review_status(
        {"reviewDecision": "CHANGES_REQUESTED"}, [], policy
    ), "changes_requested"))
    checks.append(("review_status_none_when_null", normalize_review_status(
        {"reviewDecision": None}, [], policy
    ), "none"))
    checks.append(("review_status_unavailable_label_overrides", normalize_review_status(
        {"reviewDecision": "APPROVED"}, ["review-unavailable"], policy
    ), "unavailable"))

    checks.append(("checks_check_run_success", normalize_checks([
        {"name": "PR checks", "status": "COMPLETED", "conclusion": "SUCCESS"},
    ]), [{"name": "PR checks", "status": "completed", "conclusion": "success"}]))
    checks.append(("checks_check_run_in_progress", normalize_checks([
        {"name": "PR checks", "status": "IN_PROGRESS", "conclusion": None},
    ]), [{"name": "PR checks", "status": "in_progress", "conclusion": None}]))
    checks.append(("checks_status_context_failure", normalize_checks([
        {"context": "ext/check", "state": "FAILURE"},
    ]), [{"name": "ext/check", "status": "completed", "conclusion": "failure"}]))
    checks.append(("checks_status_context_pending", normalize_checks([
        {"context": "ext/check", "state": "PENDING"},
    ]), [{"name": "ext/check", "status": "in_progress", "conclusion": None}]))
    checks.append(("checks_empty", normalize_checks(None), []))

    checks.append(("deployment_state_success", normalize_deployment_state("success"), "success"))
    checks.append(("deployment_state_error_maps_failure", normalize_deployment_state("error"), "failure"))
    checks.append(("deployment_state_queued_in_progress", normalize_deployment_state("queued"), "in_progress"))

    # merged_pr_carries_unfinished_status() unit checks: no autopilot status
    # label at all (historical PR predating the labeling convention) must be
    # excluded, while an unfinished status label must be included.
    checks.append(("merged_pr_no_status_label_excluded", merged_pr_carries_unfinished_status(
        {"labels": _lbl()}, policy
    ), False))
    checks.append(("merged_pr_done_status_excluded", merged_pr_carries_unfinished_status(
        {"labels": _lbl("status:done")}, policy
    ), False))
    checks.append(("merged_pr_unfinished_status_included", merged_pr_carries_unfinished_status(
        {"labels": _lbl("status:deploy")}, policy
    ), True))

    # End-to-end: build a snapshot and confirm the shape decide() expects,
    # including deployment correlation via merge-commit sha, "last wins"
    # most-recent-status ordering, historical-merged-PR exclusion, and
    # Issue-risk propagation onto its linked PR.
    issues_raw = [{
        "number": 80, "state": "open", "labels": _lbl("status:merge"),
        "createdAt": "2026-09-01T00:00:00Z", "updatedAt": "2026-09-05T00:00:00Z",
        "body": "### Description\n\nx\n\n### Priority\n\nhigh\n\n### Risk\n\nhigh\n\n"
                "### Dependencies\n\n_No response_\n",
    }]
    merged_prs_raw = [
        {
            # Still awaiting live-verify: must be carried forward.
            "number": 90, "state": "MERGED", "labels": _lbl("status:live-verify"),
            "createdAt": "2026-09-02T00:00:00Z", "updatedAt": "2026-09-03T00:00:00Z",
            "body": "Closes #80", "files": [{"path": "index.html"}],
            "reviewDecision": "APPROVED", "statusCheckRollup": [],
            "mergeCommit": {"oid": "sha-abc"},
        },
        {
            # Historical PR predating the labeling convention: must be excluded.
            "number": 91, "state": "MERGED", "labels": _lbl(),
            "createdAt": "2026-08-01T00:00:00Z", "updatedAt": "2026-08-02T00:00:00Z",
            "body": "Closes #80", "files": [{"path": "index.html"}],
            "reviewDecision": "APPROVED", "statusCheckRollup": [],
            "mergeCommit": {"oid": "sha-old"},
        },
    ]
    deployments_raw = [
        {"sha": "sha-abc", "state": "in_progress", "created_at": "2026-09-03T01:00:00Z"},
        {"sha": "sha-abc", "state": "success", "created_at": "2026-09-03T02:00:00Z"},
    ]
    snapshot = build_snapshot(issues_raw, [], merged_prs_raw, deployments_raw, "2026-09-10T12:00:00Z")
    checks.append(("snapshot_issue_priority_from_labels", snapshot["issues"][0]["priority"], "high"))
    checks.append(("snapshot_issue_risk_from_body", snapshot["issues"][0]["risk"], "high"))
    checks.append(("snapshot_issue_dependencies_empty", snapshot["issues"][0]["dependencies"], []))
    checks.append(("snapshot_historical_merged_pr_excluded", len(snapshot["pull_requests"]), 1))
    checks.append(("snapshot_pr_issue_number_linked", snapshot["pull_requests"][0]["issue_number"], 80))
    checks.append(("snapshot_pr_merged_true", snapshot["pull_requests"][0]["merged"], True))
    checks.append(("snapshot_pr_risk_propagated_from_issue", snapshot["pull_requests"][0]["risk"], "high"))
    checks.append(("snapshot_deployment_latest_status_wins", snapshot["deployments"][-1]["status"], "success"))
    checks.append(("snapshot_deployment_pr_number", snapshot["deployments"][-1]["pr_number"], 90))
    checks.append(("snapshot_live_verification_empty", snapshot["live_verification"], {}))

    # decide() from autopilot_status.py must be able to consume this snapshot
    # end-to-end without a schema mismatch. A merged PR with a successful
    # deployment and no recorded live-verification must resolve to
    # verify_live_production, not verify_deploy.
    sys.path.insert(0, str(ROOT / "scripts"))
    import autopilot_status  # noqa: E402

    result = autopilot_status.decide(snapshot, autopilot_status.load_policy())
    checks.append(("snapshot_feeds_decide_verify_live_production", result["action"], "verify_live_production"))

    for name, got, expected in checks:
        status = "PASS" if got == expected else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {name}: expected={expected!r} got={got!r}")

    print(f"\n{len(checks) - failures}/{len(checks)} scenarios passed.")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="OWNER/NAME to fetch live state for via `gh`.")
    parser.add_argument("--self-test", action="store_true", help="Run pure-logic scenarios (no network).")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if not args.repo:
        parser.error("--repo OWNER/NAME is required unless --self-test is given")
    return run_live_fetch(args.repo)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
