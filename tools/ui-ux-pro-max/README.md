# ui-ux-pro-max

UI/UX 스타일 가이드 CSV 위에 BM25 검색을 얹은 디자인 시스템 추천 엔진.
이 워크스페이스에 **벤더링된(복사해 들여온) 서드파티 코드**입니다.

---

## ⚠️ 출처 및 라이선스 — 미확인

**이 코드의 출처와 라이선스를 확인하지 못했습니다.** 아래를 모두 조사했으나 단서가 없었습니다.

| 조사 항목 | 결과 |
|-----------|------|
| `LICENSE` / `COPYING` 파일 | 없음 |
| 소스 내 저작권·저자·라이선스 주석 | 없음 (4개 `.py` 전체 검사) |
| 소스 내 저장소 URL / 홈페이지 | 없음 |
| `package.json` / `pyproject.toml` 등 패키지 메타데이터 | 없음 |
| git 이력 | 없음 (이 레포에 처음 커밋될 때 이미 파일만 존재) |
| 머신 내 원본 사본 | 없음 |

### 채워주세요

원본을 아는 분이 아래를 확정해야 합니다. **그 전에는 이 레포를 공개 배포하지 마세요.**

```
출처:      (예: https://github.com/<owner>/<repo>)
버전/커밋: (예: v1.2.0 / abc1234)
라이선스:  (예: MIT — 원문을 이 디렉토리에 LICENSE 로 함께 두기)
가져온 날짜: 2026-07-26 이전 (정확한 시점 미확인)
로컬 수정: (원본 대비 수정한 내용이 있으면 기록)
```

라이선스가 재배포를 허용하지 않거나 확인이 불가능하면, 이 디렉토리를 커밋에서 빼고
설치 스크립트로 각자 받아오게 하는 방식을 검토하세요. 다만 `/plan` 4단계가 이 도구에
전적으로 의존하므로, 빼는 경우 **README 요구사항에 설치 절차를 명시**해야 합니다
(도구 없이 clone 하면 `/plan` 의 디자인 시스템 단계가 동작하지 않습니다).

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
