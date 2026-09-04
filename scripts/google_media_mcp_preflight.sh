#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG_FILE=".mcp.json"
OBSERVED=()
BLOCKERS=()
ACTIONS=()

add_observed() { OBSERVED+=("$1"); }
add_blocker() { BLOCKERS+=("$1"); }
add_action() { ACTIONS+=("$1"); }

report_failure() {
  printf 'OBSERVED\n'
  printf -- '- %s\n' "${OBSERVED[@]}"
  printf 'BLOCKER\n'
  printf -- '- %s\n' "${BLOCKERS[@]}"
  printf 'REQUIRED ACTION\n'
  printf -- '- %s\n' "${ACTIONS[@]}"
}

if ! command -v python3 >/dev/null 2>&1; then
  add_observed "python3 is unavailable in the current Claude Code environment."
  add_blocker "Local preflight prerequisite is missing."
  add_action "Use a Claude Code environment with python3 available; do not recreate Google Cloud resources."
  report_failure
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  add_observed "curl is unavailable in the current Claude Code environment."
  add_blocker "Network preflight cannot run from this environment."
  add_action "Use a Claude Code environment with curl available; do not change the MCP server or token."
  report_failure
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  add_observed ".mcp.json is not present in the checked-out repository root."
  add_blocker "Claude Code is not running from the expected 50plus checkout or the current main was not fetched."
  add_action "Fetch current oosaka0123-sudo/50plus main and run this script from that checkout; do not recreate .mcp.json."
  report_failure
  exit 1
fi

RAW_MCP_URL="$(python3 - <<'PY'
import json
from pathlib import Path

try:
    data = json.loads(Path('.mcp.json').read_text(encoding='utf-8'))
    server = data['mcpServers']['google-media']
    if server.get('type') != 'http':
        raise ValueError('google-media is not configured as type=http')
    url = server.get('url')
    if not isinstance(url, str) or not url:
        raise ValueError('google-media url is missing')
    headers = server.get('headers') or {}
    auth = headers.get('Authorization', '')
    if '${GOOGLE_MEDIA_MCP_TOKEN}' not in auth:
        raise ValueError('Authorization header is not environment-variable backed')
    print(url)
except Exception as exc:
    raise SystemExit(str(exc))
PY
)" 2>/tmp/50plus-google-media-config.err
CONFIG_RC=$?

if [[ $CONFIG_RC -ne 0 ]]; then
  add_observed ".mcp.json exists but the google-media entry did not pass structural validation."
  add_blocker "MCP configuration is not recognizable by the preflight."
  add_action "Inspect current main and the existing google-media entry. Do not replace .mcp.json or rerun onboarding automatically."
  rm -f /tmp/50plus-google-media-config.err
  report_failure
  exit 1
fi
rm -f /tmp/50plus-google-media-config.err
add_observed ".mcp.json contains a structurally valid google-media HTTP MCP entry."

MCP_URL="$(RAW_MCP_URL="$RAW_MCP_URL" python3 - <<'PY'
import os, re
raw = os.environ['RAW_MCP_URL']
override = os.environ.get('GOOGLE_MEDIA_MCP_URL')
if override:
    print(override)
else:
    match = re.fullmatch(r'\$\{GOOGLE_MEDIA_MCP_URL:-([^}]+)\}', raw)
    print(match.group(1) if match else raw)
PY
)"

if [[ "$MCP_URL" != http://* && "$MCP_URL" != https://* ]]; then
  add_observed "The resolved google-media URL is not HTTP(S)."
  add_blocker "MCP endpoint resolution failed."
  add_action "Inspect GOOGLE_MEDIA_MCP_URL only if an override was intentionally set; otherwise keep the URL from current .mcp.json."
  report_failure
  exit 1
fi

add_observed "google-media endpoint URL resolved from the existing configuration."

if [[ -n "${GOOGLE_MEDIA_MCP_TOKEN:-}" ]]; then
  add_observed "GOOGLE_MEDIA_MCP_TOKEN is present in the current Claude Code environment (value not displayed)."
else
  add_observed "GOOGLE_MEDIA_MCP_TOKEN is not present in the current Claude Code environment."
  add_blocker "Client bearer token is missing."
  add_action "Set GOOGLE_MEDIA_MCP_TOKEN in the Claude Code execution environment without printing, committing, or logging its value."
fi

BASE_URL="${MCP_URL%/}"
if [[ "$BASE_URL" == */mcp ]]; then
  BASE_URL="${BASE_URL%/mcp}"
fi

probe_endpoint() {
  local name="$1"
  local url="$2"
  local body_file err_file http_code curl_rc
  body_file="$(mktemp)"
  err_file="$(mktemp)"

  http_code="$(curl --silent --show-error \
    --connect-timeout 5 --max-time 15 \
    --output "$body_file" --write-out '%{http_code}' \
    "$url" 2>"$err_file")"
  curl_rc=$?

  if [[ $curl_rc -ne 0 ]]; then
    add_observed "$name could not be reached from the current execution environment (curl exit $curl_rc)."
    add_blocker "Network/DNS/TLS egress to the existing Cloud Run endpoint failed before a usable HTTP response was received."
    add_action "Verify Claude Code network egress/DNS/TLS access to the existing Cloud Run hostname. Do not redeploy Cloud Run or rotate the token based only on this result."
    rm -f "$body_file" "$err_file"
    return 1
  fi

  add_observed "$name returned HTTP $http_code."

  case "$http_code" in
    2??)
      if [[ "$name" == "/readyz" ]]; then
        if python3 - "$body_file" <<'PY' >/dev/null 2>&1
import json, sys
with open(sys.argv[1], encoding='utf-8') as fh:
    data = json.load(fh)
raise SystemExit(0 if data.get('ready') is True else 1)
PY
        then
          add_observed "/readyz reports ready=true."
        else
          add_blocker "Cloud Run answered /readyz but did not report ready=true."
          add_action "Inspect the existing Cloud Run service's server-side readiness configuration, service account, Vertex AI/GCS environment, and logs; do not create a new Google Cloud project or service."
          rm -f "$body_file" "$err_file"
          return 1
        fi
      fi
      ;;
    401|403)
      add_blocker "Cloud Run or the application rejected the unauthenticated health/readiness probe."
      add_action "Confirm the existing Cloud Run ingress/IAM policy matches the documented MCP design. Keep GOOGLE_MEDIA_MCP_TOKEN separate from Google IAM credentials."
      rm -f "$body_file" "$err_file"
      return 1
      ;;
    421)
      add_blocker "Cloud Run reached the MCP application but the request host was rejected."
      add_action "Verify GOOGLE_MEDIA_MCP_ALLOWED_HOSTS on the existing Cloud Run service includes its current run.app hostname."
      rm -f "$body_file" "$err_file"
      return 1
      ;;
    404)
      add_blocker "The Cloud Run hostname answered but the expected health/readiness route was not found."
      add_action "Verify the existing deployed service revision and endpoint paths; do not create a replacement service."
      rm -f "$body_file" "$err_file"
      return 1
      ;;
    503)
      add_blocker "Cloud Run is reachable but the service is not ready."
      add_action "Inspect the existing service's readiness details, Google Cloud environment variables, attached service account, Vertex AI access, GCS access, and logs."
      rm -f "$body_file" "$err_file"
      return 1
      ;;
    *)
      add_blocker "Cloud Run returned an unexpected HTTP status for the health/readiness probe."
      add_action "Inspect the existing Cloud Run request/application logs for this status before changing configuration."
      rm -f "$body_file" "$err_file"
      return 1
      ;;
  esac

  rm -f "$body_file" "$err_file"
  return 0
}

HEALTH_OK=0
READY_OK=0
probe_endpoint "/healthz" "$BASE_URL/healthz" && HEALTH_OK=1
probe_endpoint "/readyz" "$BASE_URL/readyz" && READY_OK=1

if [[ ${#BLOCKERS[@]} -gt 0 ]]; then
  report_failure
  exit 1
fi

printf 'OBSERVED\n'
printf -- '- %s\n' "${OBSERVED[@]}"
printf 'RESULT\n'
printf -- '- Google Media MCP client configuration, token presence, network reachability, /healthz, and /readyz preflight passed.\n'
printf 'NEXT\n'
printf -- '- In Claude Code, confirm the google-media MCP server is recognized, list its tools, run one minimal generate_image call, and only after image success run one minimal generate_video call.\n'
