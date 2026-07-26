#!/bin/bash
# FSD Agent Team - 초기 세팅 스크립트
#
# 대상 프로젝트 경로를 지시문 파일에 반영한다.
# 재실행 가능(idempotent): 이전에 설정한 경로를 .fsd-team.conf 에 기억해두고,
# 다시 실행하면 '이전 경로 → 새 경로' 로 치환한다.

set -euo pipefail

TEAM_DIR="$(cd "$(dirname "$0")" && pwd)"
PLACEHOLDER="__PROJECT_PATH__"
CONF="$TEAM_DIR/.fsd-team.conf"
DRY_RUN=0

# 치환 대상 — 지시문 파일만. plans/(과거 산출물), README.md(범용 문서),
# .omc/(런타임 상태), tools/(벤더링된 도구)는 건드리지 않는다.
TARGET_DIRS=(".claude/rules" ".claude/skills" "docs/agents")
TARGET_FILES=("CLAUDE.md")

usage() {
  cat <<EOF
사용법: ./init.sh [경로] [--dry-run]

  경로        대상 프로젝트 경로 (생략하면 대화형 입력)
  --dry-run   실제로 바꾸지 않고 변경될 파일만 출력
  --show      현재 설정된 경로 확인
  --reset     설정된 경로를 $PLACEHOLDER 로 되돌린다 (커밋 전에 실행)

커밋 전에는 --reset 을 실행하세요. 개인 경로가 박힌 상태로 커밋하면
다른 사람이 clone 했을 때 치환할 플레이스홀더가 없어 세팅이 불가능합니다.
EOF
}

PROJECT_PATH_ARG=""
RESET=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --reset) RESET=1 ;;
    --show)
      if [ -f "$CONF" ]; then
        echo "현재 설정: $(cat "$CONF")"
      else
        echo "아직 설정되지 않았습니다 (플레이스홀더 상태)."
      fi
      exit 0
      ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "❌ 알 수 없는 옵션: $arg"; usage; exit 1 ;;
    *) PROJECT_PATH_ARG="$arg" ;;
  esac
done

# 대상 파일 수집 — 지시문 파일만
collect_files() {
  for dir in "${TARGET_DIRS[@]}"; do
    [ -d "$TEAM_DIR/$dir" ] && find "$TEAM_DIR/$dir" -type f -name "*.md" -print
  done
  for file in "${TARGET_FILES[@]}"; do
    [ -f "$TEAM_DIR/$file" ] && echo "$TEAM_DIR/$file"
  done
}

# $1 을 $2 로 치환 (BSD/GNU sed 양쪽 호환)
substitute() {
  local from="$1" to="$2" file
  case "$from$to" in
    *"|"*) echo "❌ 경로에 '|' 문자가 있어 처리할 수 없습니다."; exit 1 ;;
  esac
  while IFS= read -r file; do
    grep -qF "$from" "$file" 2>/dev/null || continue
    if sed --version >/dev/null 2>&1; then
      sed -i "s|$from|$to|g" "$file"    # GNU
    else
      sed -i '' "s|$from|$to|g" "$file" # BSD (macOS)
    fi
  done < <(collect_files)
}

echo ""
echo "🏗️  FSD Agent Team 초기 세팅"
echo "================================"
echo ""

# 이전 설정 확인 → 이게 재실행을 가능하게 하는 핵심
CURRENT=""
if [ -f "$CONF" ]; then
  CURRENT="$(cat "$CONF")"
  echo "📌 현재 설정된 경로: $CURRENT"
  echo ""
fi

# --reset: 커밋 전에 플레이스홀더로 되돌린다
if [ "$RESET" -eq 1 ]; then
  if [ -z "$CURRENT" ]; then
    echo "이미 플레이스홀더 상태입니다. 되돌릴 것이 없습니다."
    exit 0
  fi
  COUNT=0
  while IFS= read -r file; do
    grep -qF "$CURRENT" "$file" 2>/dev/null && COUNT=$((COUNT + 1))
  done < <(collect_files)

  echo "🔙 $CURRENT"
  echo "   → $PLACEHOLDER  ($COUNT 개 파일)"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo ""
    echo "🔍 --dry-run: 실제로 변경하지 않았습니다."
    exit 0
  fi

  substitute "$CURRENT" "$PLACEHOLDER"
  rm -f "$CONF"
  echo ""
  echo "✅ 플레이스홀더로 복원했습니다. 이제 커밋해도 안전합니다."
  echo "   작업을 이어가려면: ./init.sh $CURRENT"
  echo ""
  exit 0
fi

# 경로 입력
if [ -n "$PROJECT_PATH_ARG" ]; then
  PROJECT_PATH="$PROJECT_PATH_ARG"
else
  read -r -p "대상 프로젝트 경로를 입력하세요: " PROJECT_PATH
fi

# 경로 유효성 검사
PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"
if ! PROJECT_PATH="$(cd "$PROJECT_PATH" 2>/dev/null && pwd)"; then
  echo "❌ 존재하지 않는 경로입니다: $PROJECT_PATH"
  exit 1
fi

if [ "$PROJECT_PATH" = "$TEAM_DIR" ]; then
  echo "❌ 팀 워크스페이스 자신을 대상으로 지정할 수 없습니다."
  exit 1
fi

if [ "$PROJECT_PATH" = "$CURRENT" ]; then
  echo "✅ 이미 이 경로로 설정되어 있습니다. 변경 없음."
  exit 0
fi

if [ ! -d "$PROJECT_PATH/src" ] && [ "$DRY_RUN" -eq 0 ]; then
  echo "⚠️  src/ 폴더가 없습니다. FSD 구조가 아직 없을 수 있습니다."
  if [ -t 0 ]; then
    read -r -p "계속 진행할까요? (y/n): " CONFIRM
    if [ "$CONFIRM" != "y" ]; then
      echo "취소되었습니다."
      exit 0
    fi
  else
    echo "   (비대화형 실행 — 계속 진행합니다)"
  fi
fi

# 무엇을 무엇으로 바꿀지 결정
if [ -n "$CURRENT" ]; then
  FROM="$CURRENT"
  echo ""
  echo "🔄 경로 변경: $CURRENT"
  echo "           → $PROJECT_PATH"
else
  FROM="$PLACEHOLDER"
  echo ""
  echo "📂 대상 프로젝트: $PROJECT_PATH"
fi
echo ""

MATCHED=()
while IFS= read -r file; do
  if grep -qF "$FROM" "$file" 2>/dev/null; then
    MATCHED+=("$file")
  fi
done < <(collect_files)

if [ ${#MATCHED[@]} -eq 0 ]; then
  echo "⚠️  '$FROM' 를 포함한 파일이 없습니다."
  if [ -z "$CURRENT" ]; then
    echo "   이미 다른 경로로 설정되었을 수 있습니다. ./init.sh --show 로 확인하세요."
  fi
  exit 1
fi

echo "🔧 변경 대상 ${#MATCHED[@]}개 파일:"
for file in "${MATCHED[@]}"; do
  echo "   - ${file#"$TEAM_DIR"/}  ($(grep -cF "$FROM" "$file") 곳)"
done
echo ""

if [ "$DRY_RUN" -eq 1 ]; then
  echo "🔍 --dry-run: 실제로 변경하지 않았습니다."
  exit 0
fi

substitute "$FROM" "$PROJECT_PATH"

echo "$PROJECT_PATH" > "$CONF"

echo "✅ 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. cd $TEAM_DIR"
echo "  2. claude"
echo "  3. /plan [작업 내용]"
echo ""
echo "경로를 다시 바꾸려면 ./init.sh 를 재실행하면 됩니다."
echo ""
