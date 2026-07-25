# FSD Agent Team

Claude Code 기반의 **FSD(Feature-Sliced Design) AI 에이전트 팀 워크스페이스**입니다.
어떤 프로젝트든 경로만 설정하면, 4명의 AI 팀원이 FSD 규칙에 맞춰 개발을 수행합니다.

---

## 빠른 시작

### 1. clone

```bash
git clone <이 레포 URL>
cd fsd-agent-team
```

### 2. 초기 세팅

```bash
./init.sh
# 대상 프로젝트 경로 입력: /path/to/your/project
```

### 3. 실행

```bash
claude
```

### 4. 작업

```
/plan 리뷰 작성 기능 만들어줘
→ HTML 계획서 확인 → 승인
→ 자동 코딩 → FSD 검수
```

---

## 팀 구성

| 팀원 | 역할 | slash command |
|------|------|-------------|
| **Planner** | 요구사항 분석, HTML 계획서 작성 | `/plan` |
| **Coder** | FSD 규칙에 따라 코드 작성 | `/code` |
| **Reviewer** | FSD 구조/컨벤션 검수 | `/review-fsd` |
| **Tester** | 레이어별 테스트 작성 | `/test` |

추가 명령: `/refactor`, `/migrate-fsd`

---

## 작업 흐름

```
사용자 요청
    ↓
Team Lead (요구사항 분석)
    ↓
📄 HTML 계획서 → 브라우저에서 리뷰 → 승인
    ↓
Coder (FSD 규칙에 따라 코딩)
    ↓
Reviewer + Tester (검증)
    ↓
📄 HTML 리포트 → 결과 확인
```

---

## 디렉토리 구조

```
fsd-agent-team/
├── CLAUDE.md                    # Team Lead 핵심 지침
├── init.sh                      # 초기 세팅 (프로젝트 경로 설정)
├── .claude/
│   ├── rules/                   # 자동 로드 규칙
│   │   ├── fsd-architecture.md  #   FSD 레이어/의존성 규칙
│   │   ├── coding-standards.md  #   코드 스타일 규칙
│   │   └── dispatch-protocol.md #   팀원 디스패치 프로토콜
│   └── skills/                  # Slash commands
│       ├── plan/SKILL.md
│       ├── code/SKILL.md
│       ├── review-fsd/SKILL.md
│       ├── test/SKILL.md
│       ├── refactor/SKILL.md
│       └── migrate-fsd/SKILL.md
├── docs/
│   ├── plan-template.md         # 계획서 md 템플릿
│   ├── plan-template.html       # 계획서 html 템플릿 (결정 콘솔)
│   └── agents/                  # 팀원 프로필 + 프롬프트 템플릿
│       ├── planner.md
│       ├── coder.md
│       ├── reviewer.md
│       └── tester.md
└── plans/                       # 생성된 계획서 보관
```

---

## 다른 프로젝트에 적용

```bash
cd fsd-agent-team
./init.sh
# 새 프로젝트 경로 입력
claude
```

기존 프로젝트(FSD가 아닌)에 적용하려면:
```
/migrate-fsd
```
