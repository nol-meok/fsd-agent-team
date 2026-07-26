# ui-ux-pro-max

UI/UX 스타일 가이드 CSV 위에 BM25 검색을 얹은 디자인 시스템 추천 엔진.
이 워크스페이스에 **벤더링된(복사해 들여온) 서드파티 코드**입니다.

---

## 출처 및 라이선스

| 항목 | 값 |
|------|-----|
| 출처 | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| 원본 설명 | "An AI SKILL that provide design intelligence for building professional UI/UX multiple platforms" |
| 저작권자 | Next Level Builder (2024) |
| 라이선스 | **MIT** — 전문은 이 디렉토리의 [LICENSE](./LICENSE) |
| 버전 | 원본 저장소 기준 v2.0 계열 (정확한 커밋 해시 미기록) |
| 가져온 날짜 | 2026-07-26 이전 (정확한 시점 미기록) |
| 로컬 수정 | 없음 — 원본 그대로 벤더링 |

MIT 라이선스이므로 재배포·수정이 가능합니다. 단 **저작권 표시와 라이선스 전문을
함께 배포해야 하므로 `LICENSE` 파일을 삭제하지 마세요.**

### 업스트림과 동기화할 때

- 로컬 수정이 없으므로 현재는 원본을 그대로 덮어써도 됩니다
- 수정하게 되면 이 표의 "로컬 수정" 항목에 내용을 기록하세요
- CSV 스키마가 바뀌면 `python3 validate_data.py` 로 먼저 검사하고,
  `.claude/skills/plan/SKILL.md` 4단계의 도메인 목록도 함께 확인하세요

---

## 구성 (실측)

| 항목 | 값 |
|------|-----|
| Python 소스 | 4개 파일, 2,111줄 |
| 데이터 | CSV 35개, 약 4,232행 |
| 외부 의존성 | **없음** — 표준 라이브러리만 (`csv`, `re`, `math`, `json`, `pathlib` 등) |
| 필요 런타임 | Python 3 |

```
core.py            검색 엔진 (BM25), 도메인/스택 설정
design_system.py   검색 결과 종합 → 디자인 시스템 생성 + 영속화
search.py          CLI 진입점
validate_data.py   CSV 무결성 검사 (stdlib only, pytest 불필요)
data/*.csv         도메인별 데이터
data/stacks/*.csv  스택별 가이드라인
```

## 사용법

항상 이 디렉토리에서 실행합니다 (CSV 경로가 상대 경로).

```bash
cd tools/ui-ux-pro-max

# 도메인 검색
python3 search.py "<쿼리>" --domain <도메인> --json -n 3

# 스택 가이드라인
python3 search.py "<쿼리>" --stack nextjs --json -n 5

# 종합 디자인 시스템 생성
python3 search.py "<프로젝트 키워드>" --design-system --json

# 데이터 무결성 검사
python3 validate_data.py
```

주요 옵션: `--json`(기계 판독), `-n/--max-results`(기본 3), `--full`(값 잘라내지 않음),
`--persist`/`--output-dir`/`--page`(design-system 파일로 저장),
`--variance`/`--motion`/`--density`(1~10 디자인 다이얼).

### 도메인 12개

| 도메인 | CSV | 용도 |
|--------|-----|------|
| `style` | styles.csv | UI 스타일 + **Implementation Checklist** (구체 수치) |
| `color` | colors.csv | 제품 유형별 팔레트 (16 토큰, WCAG 조정값 포함) |
| `typography` | typography.csv | 폰트 페어링 |
| `google-fonts` | google-fonts.csv | 폰트 메타데이터 (한글 폰트 포함) |
| `icons` | icons.csv | 아이콘 글리프 + import 코드 |
| `gsap` | motion.csv | 모션 프리셋 (duration/easing/snippet/framework notes) |
| `ux` | ux-guidelines.csv | UX Do/Don't + severity |
| `landing` | landing.csv | 랜딩 섹션 순서 / CTA 전략 |
| `product` | products.csv | 제품 UI 패턴 |
| `chart` | charts.csv | 데이터 시각화 가이드 |
| `react` | react-performance.csv | React 성능 |
| `web` | app-interface.csv | 웹 앱 인터페이스 |

### 스택 22개

`react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `nuxt-ui`, `html-tailwind`, `shadcn`,
`react-native`, `flutter`, `swiftui`, `jetpack-compose`, `threejs`, `angular`, `laravel`,
`javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`

## 이 워크스페이스에서의 역할

`/plan` 4단계(디자인 시스템 생성)가 이 도구를 호출합니다.
`.claude/skills/plan/SKILL.md` 의 4-1 ~ 4-9 참고.

추출한 값은 계획서 `PLAN.design` 에 실려 `/code` 로 전달됩니다.
특히 `style` 도메인의 **Implementation Checklist**(`48px+ gaps`, `32px+ type` 등)가
`design.checklist` → HTML 체크리스트 → 코드 CSS 값으로 이어집니다.

## 알려진 데이터 공백

DB 수록 범위가 균일하지 않습니다. **매칭 0건이면 조용히 기본값으로 넘어가지 말고
그 사실을 계획서에 명시하세요** (도구 자체도 0건일 때 그렇게 안내합니다).

- `icons.csv` 는 라이브러리가 **Phosphor 계열뿐**이고 글리프도 100여 개 표본입니다.
  날씨 글리프(`sun cloud rain snow wind`) 검색은 **0건**입니다.
- `landing.csv` 는 랜딩 페이지 기준이라 인앱 페이지 패턴과는 어긋날 수 있습니다.
- `style` 결과는 쿼리에 따라 모바일/핀테크 편향이 나올 수 있으니 도메인에 맞는지 확인하세요.
