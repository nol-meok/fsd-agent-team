#!/bin/bash
# FSD Agent Team - 초기 세팅 스크립트

set -e

TEAM_DIR="$(cd "$(dirname "$0")" && pwd)"
PLACEHOLDER="__PROJECT_PATH__"

echo ""
echo "🏗️  FSD Agent Team 초기 세팅"
echo "================================"
echo ""

# 프로젝트 경로 입력
read -p "대상 프로젝트 경로를 입력하세요: " PROJECT_PATH

# 경로 유효성 검사
PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"
PROJECT_PATH="$(cd "$PROJECT_PATH" 2>/dev/null && pwd)" || {
  echo "❌ 존재하지 않는 경로입니다: $PROJECT_PATH"
  exit 1
}

if [ ! -d "$PROJECT_PATH/src" ]; then
  echo "⚠️  src/ 폴더가 없습니다. FSD 구조가 아직 없을 수 있습니다."
  read -p "계속 진행할까요? (y/n): " CONFIRM
  if [ "$CONFIRM" != "y" ]; then
    echo "취소되었습니다."
    exit 0
  fi
fi

echo ""
echo "📂 대상 프로젝트: $PROJECT_PATH"
echo ""

# 모든 설정 파일에서 플레이스홀더 치환
echo "🔧 설정 파일에 경로 반영 중..."

find "$TEAM_DIR" -type f \( -name "*.md" -o -name "*.json" \) \
  -not -path "*/.git/*" \
  -not -path "*/node_modules/*" \
  -exec sed -i '' "s|$PLACEHOLDER|$PROJECT_PATH|g" {} +

echo "✅ 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. cd $TEAM_DIR"
echo "  2. claude"
echo "  3. /plan [작업 내용]"
echo ""
