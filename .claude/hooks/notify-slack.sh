#!/usr/bin/env bash
# Claude Code hook -> Slack 모바일 알림 (프로젝트 전용 버전)
#
# Notification(permission_prompt)과 Stop 이벤트만 골라서 Slack Incoming
# Webhook으로 전송한다. hook 실패가 Claude Code 진행을 막으면 안 되므로
# 어떤 경우에도 exit 0으로 끝낸다.
#
# 웹훅 URL은 이 저장소에 커밋되지 않는 .claude/hooks/.env에서 읽는다
# (.claude/hooks/.env.example 참고). CLAUDE_PROJECT_DIR은 Claude Code가
# hook 프로세스에 자동으로 넘겨주는 환경변수다.

set -uo pipefail

ENV_FILE="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/hooks/.env"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

# 웹훅이 아직 설정 안 됐으면 조용히 종료 (에러로 흐름을 막지 않는다).
if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
  exit 0
fi

input=$(cat)
event=$(echo "$input" | jq -r '.hook_event_name // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')
project=$(basename "${cwd:-unknown}")

status=""

case "$event" in
  Notification)
    ntype=$(echo "$input" | jq -r '.notification_type // empty')
    # 권한 요청 알림만 보낸다 — idle_prompt/auth_success 등은 무시.
    if [ "$ntype" = "permission_prompt" ]; then
      msg=$(echo "$input" | jq -r '.message // "권한 요청이 발생했습니다."')
      status="🔐 $msg"
    fi
    ;;
  Stop)
    # 대화 내용이 Slack으로 새어나가지 않도록 완료 사실만 알린다.
    status="✅ 완료됨"
    ;;
esac

# 보낼 내용이 없으면(관심 없는 이벤트) 그냥 종료.
if [ -z "$status" ]; then
  exit 0
fi

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
text=$(printf '프로젝트: %s\n상태: %s\n시간: %s' "$project" "$status" "$timestamp")

payload=$(jq -n --arg text "$text" '{text: $text}')
curl -s -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL" > /dev/null || true

exit 0
