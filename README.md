# FSD Agent Team

Claude Code 기반의 **FSD(Feature-Sliced Design) AI 에이전트 팀 워크스페이스**입니다.
어떤 프로젝트든 경로만 설정하면, AI 팀원이 FSD 규칙에 맞춰 개발을 수행합니다.

---

## 빠른 시작

### 1. clone

```bash
git clone https://github.com/nol-meok/fsd-agent-team.git
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
| **Refactor** | 코드 중복/구조 개선 | `/refactor` |
| **Migrate** | 기존 프로젝트 FSD 변환 | `/migrate-fsd` |

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

## HTML 계획서

`/plan` 또는 `/migrate-fsd` 실행 시 인터랙티브 HTML 계획서가 생성됩니다.

- **다크모드** UI
- **파일트리** (devicon 아이콘, 폴더 접기)
- **타임라인** (작업 순서 시각화)
- **결정 콘솔** (옵션 선택 → 프롬프트 복사)
- **Before → After** 좌우 비교 (migrate 시, 클릭 하이라이트)
- **문제 분석** (critical/warning/info 카드)

### 예시

| 유형 | 파일 |
|------|------|
| 신규 기능 | [plans/feature/20260726-review.html](plans/feature/20260726-review.html) |
| 마이그레이션 | [plans/migrate/20260726-legacy-shop.html](plans/migrate/20260726-legacy-shop.html) |

---

## FSD 아키텍처 가이드

[docs/fsd-guide.html](docs/fsd-guide.html) — 인터랙티브 FSD 가이드

- Agent Pipeline, FSD Layers, Dependencies, Slice 구조
- 코드 컨벤션, Anti-Patterns, 배치 가이드
- 실전 워크플로우, Commands 레퍼런스

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
│   ├── fsd-guide.html           # FSD 아키텍처 가이드 (인터랙티브)
│   ├── plan-template.md         # 계획서 md 템플릿
│   ├── plan-template.html       # 계획서 html 템플릿 (결정 콘솔)
│   └── agents/                  # 팀원 프로필 + 프롬프트 템플릿
│       ├── planner.md
│       ├── coder.md
│       ├── reviewer.md
│       └── tester.md
└── plans/                       # 생성된 계획서 보관
    ├── feature/                 #   신규 기능 계획서
    └── migrate/                 #   마이그레이션 계획서
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
