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

| 옵션 | 용도 |
| ---------------- | ----------------------------------- |
| `./init.sh <경로>` | 대화형 입력 없이 바로 설정 |
| `./init.sh --show` | 현재 설정된 경로 확인 |
| `./init.sh --dry-run` | 변경될 파일만 미리 보기 |
| `./init.sh --reset` | 경로를 `__PROJECT_PATH__` 로 되돌리기 (**커밋 전 필수**) |

재실행 가능합니다. 다시 실행하면 이전 경로를 새 경로로 바꿉니다.

> ⚠️ `init.sh` 는 추적 중인 지시문 파일 15개에 경로를 직접 써넣습니다.
> **커밋 전에 `./init.sh --reset` 을 실행하세요.** 개인 경로가 박힌 상태로 커밋하면
> 플레이스홀더가 사라져 다른 사람이 clone 했을 때 세팅이 불가능합니다.
> 커밋 후 `./init.sh <경로>` 로 다시 적용하면 됩니다.

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

### 요구사항

- Claude Code
- **Python 3** — 계획서 HTML 빌더(`scripts/`)와 디자인 시스템 도구(`tools/`)에 필요
- Node.js — FSD 린터(`scripts/lint-fsd.ts`)를 `npx tsx` 로 실행할 때

> `tools/ui-ux-pro-max` 는 [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
> (MIT, © 2024 Next Level Builder) 을 벤더링한 것입니다.
> 자세한 내용은 [tools/ui-ux-pro-max/README.md](tools/ui-ux-pro-max/README.md) 참고.

---

## 팀 구성

| 팀원 | 역할 | slash command |
| ------------ | ------------------------------- | -------------- |
| **Planner** | 요구사항 분석, HTML 계획서 작성 | `/plan` |
| **Coder** | FSD 규칙에 따라 코드 작성 | `/code` |
| **Reviewer** | FSD 구조/컨벤션 검수 | `/review-fsd` |
| **Tester** | 레이어별 테스트 작성 | `/test` |
| **Refactor** | 코드 중복/구조 개선 | `/refactor` |
| **Migrator** | 기존 프로젝트 FSD 변환 | `/migrate-fsd` |

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
- **결정 콘솔** (옵션 선택 → 프롬프트 복사 → 확정 시 잠금)
- **디자인 시스템** (색상 스와치, 폰트 미리보기, UX/모션/스택 규칙)
- **문제 분석** (critical/warning/info 카드, migrate 시)
- **Before → After** 좌우 비교 (migrate 시)

### 생성 방법

계획서 HTML은 `docs/plan-template.html`(단일 소스)에 PLAN 데이터를 주입해 만듭니다.
템플릿을 복사해 직접 치환하지 않고, **반드시 빌더를 씁니다.**

```bash
# 생성
python3 scripts/build-plan-html.py plans/feature/20260727-제목.md --data plan.json

# 기존 산출물 점검
python3 scripts/build-plan-html.py plans/feature/20260727-제목.html --verify-only
```

빌더는 쓰기 전에 검증하고, 실패하면 파일을 남기지 않습니다.
PLAN 스키마와 md 섹션 규약은 [docs/plan-template.md](docs/plan-template.md) 참고.

### 예시

| 유형 | 파일 |
| ------------ | ---------------------------------------------------------------------------------- |
| 신규 기능 | [plans/feature/20260726-review.html](plans/feature/20260726-review.html) |
| 마이그레이션 | [plans/migrate/20260726-legacy-shop.html](plans/migrate/20260726-legacy-shop.html) |

---

## FSD 아키텍처 가이드

[docs/fsd-guide.html](docs/fsd-guide.html) — 인터랙티브 FSD 가이드
([온라인](https://nol-meok.github.io/fsd-agent-team/fsd-guide.html))

- Agent Pipeline, FSD Layers, Dependencies, Slice 구조
- 코드 컨벤션, Anti-Patterns, 배치 가이드
- 실전 워크플로우, Commands 레퍼런스

---

## 디렉토리 구조

```
fsd-agent-team/
├── CLAUDE.md                    # Team Lead 핵심 지침
├── init.sh                      # 초기 세팅 (재실행 가능)
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
├── scripts/
│   ├── build-plan-html.py       # 계획서 HTML 빌더 (+ 검증)
│   └── lint-fsd.ts              # FSD 구조 자동 검사 (대상 프로젝트에 복사해 사용)
├── tools/
│   └── ui-ux-pro-max/           # 디자인 시스템 추천 엔진 (/plan 이 사용)
├── docs/
│   ├── fsd-guide.html           # FSD 아키텍처 가이드 (인터랙티브)
│   ├── plan-template.html       # 계획서 HTML 단일 소스 (빌더 전용)
│   ├── plan-template.md         # md 템플릿 + PLAN 스키마
│   └── agents/                  # 팀원 프로필 + 프롬프트 템플릿
│       ├── planner.md
│       ├── coder.md
│       ├── reviewer.md
│       ├── tester.md
│       ├── refactor.md
│       └── migrator.md
├── plans/                       # 계획서 (승인 대상)
│   ├── feature/                 #   신규 기능
│   └── migrate/                 #   마이그레이션
└── reports/                     # 결과 리포트
    ├── review/                  #   FSD 검수
    └── refactor/                #   리팩토링 분석
```

---

## 다른 프로젝트에 적용

```bash
cd fsd-agent-team
./init.sh /path/to/other/project
claude
```

기존 프로젝트(FSD가 아닌)에 적용하려면:

```
/migrate-fsd
```
