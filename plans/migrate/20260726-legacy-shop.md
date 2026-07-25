# 레거시 쇼핑몰 FSD 마이그레이션

## 1. 개요
- 작업 유형: migrate
- 요청 사항: 기존 Next.js 쇼핑몰 프로젝트를 FSD 아키텍처로 전환
- 현재 구조: pages 기반 + components/ 플랫 구조 + 로직/UI 혼재

## 2. 현재 상태 분석

### 현재 디렉토리 구조
```
src/
├── pages/
│   ├── index.tsx
│   ├── products/[id].tsx
│   ├── cart.tsx
│   └── checkout.tsx
├── components/
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── ProductCard.tsx
│   ├── ProductList.tsx
│   ├── CartItem.tsx
│   ├── CartSummary.tsx
│   ├── CheckoutForm.tsx
│   ├── SearchBar.tsx
│   └── StarRating.tsx
├── hooks/
│   ├── useCart.ts
│   ├── useProducts.ts
│   └── useAuth.ts
├── types/
│   ├── product.ts
│   ├── cart.ts
│   └── user.ts
├── api/
│   ├── productApi.ts
│   ├── cartApi.ts
│   └── authApi.ts
├── utils/
│   ├── formatPrice.ts
│   └── formatDate.ts
└── styles/
    ├── globals.css
    ├── ProductCard.module.css
    └── Header.module.css
```

### 발견된 문제
- components/에 모든 컴포넌트가 플랫하게 나열 (역할 구분 없음)
- hooks/에 비즈니스 로직 + 서버 상태 + UI 상태 혼재
- ProductCard에서 직접 cartApi 호출 (표시 컴포넌트에 로직 혼재)
- SearchBar에서 직접 productApi 호출
- types/가 별도 폴더에 분리되어 관련 코드와 멀리 떨어져 있음

## 3. FSD 레이어 배치

### 파일 이동 매핑

| 현재 경로 | 이동 경로 | 레이어 | 이유 |
|-----------|-----------|--------|------|
| `types/product.ts` | `entities/product/model/types.ts` | entities | 도메인 데이터 타입 |
| `types/cart.ts` | `entities/cart/model/types.ts` | entities | 도메인 데이터 타입 |
| `types/user.ts` | `entities/user/model/types.ts` | entities | 도메인 데이터 타입 |
| `api/productApi.ts` | `entities/product/api/productApi.ts` | entities | 데이터 CRUD API |
| `api/cartApi.ts` | `entities/cart/api/cartApi.ts` | entities | 데이터 CRUD API |
| `api/authApi.ts` | `entities/user/api/authApi.ts` | entities | 데이터 CRUD API |
| `hooks/useProducts.ts` | `entities/product/model/useProducts.ts` | entities | 서버 상태 (React Query) |
| `hooks/useCart.ts` | `features/cart/model/useCart.ts` | features | 장바구니 조작 로직 |
| `hooks/useAuth.ts` | `features/auth/model/useAuth.ts` | features | 인증 로직 |
| `components/SearchBar.tsx` | `features/search/ui/SearchBar.tsx` | features | 사용자 액션 (검색하기) |
| `components/CheckoutForm.tsx` | `features/checkout/ui/CheckoutForm.tsx` | features | 사용자 액션 (결제하기) |
| `components/Header.tsx` | `widgets/header/ui/Header.tsx` | widgets | 페이지 공통 섹션 |
| `components/Footer.tsx` | `widgets/footer/ui/Footer.tsx` | widgets | 페이지 공통 섹션 |
| `components/ProductList.tsx` | `widgets/product-list/ui/ProductList.tsx` | widgets | 페이지 섹션 (조합) |
| `components/ProductCard.tsx` | `widgets/product-list/ui/ProductCard.tsx` | widgets | 위젯 내부 컴포넌트 |
| `components/CartItem.tsx` | `widgets/cart-view/ui/CartItem.tsx` | widgets | 위젯 내부 컴포넌트 |
| `components/CartSummary.tsx` | `widgets/cart-view/ui/CartSummary.tsx` | widgets | 위젯 내부 컴포넌트 |
| `components/StarRating.tsx` | `shared/ui/StarRating/StarRating.tsx` | shared | 범용 UI (어디서든 사용) |
| `utils/formatPrice.ts` | `shared/lib/utils/formatPrice.ts` | shared | 범용 유틸 |
| `utils/formatDate.ts` | `shared/lib/utils/formatDate.ts` | shared | 범용 유틸 |
| `styles/globals.css` | `shared/config/globals.scss` | shared | 전역 스타일 |

## 4. 작업 순서

Phase별로 순차 실행. 매 Phase마다 빌드 확인.

## 5. Import 의존성 (마이그레이션 후)

```
app/ → widgets/header + widgets/footer + widgets/product-list + widgets/cart-view
widgets/product-list → entities/product + features/cart + features/search
widgets/cart-view → entities/cart + features/checkout
features/cart → entities/cart + entities/product
features/search → entities/product
features/auth → entities/user
```

## 6. 위험 요소
- pages/ → app/ 전환 시 라우팅 깨질 수 있음 (App Router 마이그레이션 동반)
- ProductCard에서 cartApi 직접 호출하던 부분 → features/cart로 분리 필요
- import 경로 일괄 변경 필요 (모든 파일 영향)
- 기존 테스트가 있다면 경로 변경으로 깨질 수 있음

## 7. FSD 검증 체크리스트
- ✅ 단방향 의존성: app → widgets → features → entities → shared
- ✅ entities에 UI 없음 (타입 + API만)
- ✅ shared에 도메인 코드 없음 (StarRating, formatPrice만)
- ✅ features끼리 교차 import 없음
- ✅ 각 슬라이스 index.ts public API
