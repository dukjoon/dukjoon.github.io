---
title: "[Trend] 2026-04-23: 에러 전파·심 금지 규율과 멀티테넌트·CAD 워크트리 통합"
pubDatetime: 2026-04-23T00:00:00Z
description: "Zed·ZenithGrid의 패닉·심 배제 규율, LangChain 지연 임포트, atom-ops RLS·Mintlify 규칙, vcad·naver 아키텍처를 정리합니다."
category: trend
tags:
  - trend
  - rust
  - multi-tenant
  - monorepo
  - electron
draft: false
---

2026-04-23 수집 저장소에서는 AI 에이전트가 코드를 수정하거나 리팩터링할 때 흔히 남기는 침묵하는 오류 처리, 무의미한 하위호환 래퍼, 과도한 파일 쪼개기를 `CLAUDE.md` 수준에서 원천 금지하는 흐름이 뚜렷합니다. 아울러 멀티테넌트 SaaS의 Row-Level Security(RLS) 강제, 형제 저장소와 `.claude/worktrees`를 아우르는 Rust/WASM CAD 빌드 규약, 1만 줄대 Electron 렌더러 분해 전략도 함께 확인됩니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 엄격한 엔지니어링 규율과 레거시 하위호환 관리 | `zed-industries/zed`, `lromero74/ZenithGrid`, `guangtouwangba/langchain` | Rust `unwrap()`/`let _ =` 금지, 리팩터링 시 심(shim) 금지 및 `git diff` 검증, `__getattr__` 지연 임포트 |
| 멀티테넌트 SaaS와 하이브리드 앱·CAD 통합 | `projectdeathstar61/atom-ops`, `ecto/vcad`, `cd000242-sudo/naver` | 전 테이블 `business_id` + RLS 강제, `.claude/worktrees` `npm ci` 부트스트랩, Electron 모듈 및 셀렉터 중앙화 |

---

## 2. 엄격한 엔지니어링 규율과 레거시 하위호환 관리

### 2.1 Rust 패닉 금지와 "Why" 중심 주석 규율 (`zed-industries/zed`)

- **출처**: [`zed-industries/zed`](https://github.com/zed-industries/zed) · **핵심 스택**: Rust, Python (`typer`, `requests`, `pytz`) · **적용 판단**: `Trial`
- **기술 개요**: Rust 기반 에디터 저장소의 `CLAUDE.md`는 조기 최적화보다 정확성과 명료성을 우선하고, `unwrap()` 패닉 호출과 `let _ =` 형태의 침묵하는 에러 폐기를 금지하며 `?`, `.log_err()`, 명시적 `match` 사용을 요구합니다. 함께 포함된 `script/update_top_ranking_issues/main.py`는 `typer`와 `pytz`(`America/New_York` 시간대)를 이용해 GitHub 상위 이슈를 집계합니다.

**실무 적용 해설**: 대규모 Rust 프로젝트에 AI 코딩 에이전트를 활용하면 컴파일을 빠르게 통과시키려고 `unwrap()`을 남발하거나 `let _ =`로 에러를 삼키고, 코드 동작만 반복 설명하는 주석과 잘게 쪼갠 소형 파일을 양산하는 문제가 발생합니다. AS-IS의 일반 린트 사후 점검에 의존하던 방식에서 벗어나 `CLAUDE.md`로 에러 전파(`?`)·관측(`.log_err()`)·기존 파일 우선 확장을 명문화한 TO-BE 규율은 런타임 패닉과 코드 파편화를 사전에 막아줍니다. 다만 기존 파일에 기능을 계속 추가하라는 원칙은 파일이 지나치게 비대해지는 부작용을 부를 수 있으므로, 논리적 컴포넌트 분리 기준을 리뷰 체크리스트에 함께 두는 균형이 필요합니다.

### 2.2 하위호환 심(Shim) 금지와 `git diff` 선확인 원칙 (`lromero74/ZenithGrid`)

- **출처**: [`lromero74/ZenithGrid`](https://github.com/lromero74/ZenithGrid) · **핵심 스택**: Python FastAPI, WebSockets, Starlette `BaseHTTPMiddleware` · **적용 판단**: `Assess`
- **기술 개요**: 트레이딩·봇 모니터링 백엔드(`backend/app/main.py`)로 `PublicEndpointRateLimiter`, `IntrusionDetector`, `MultiBotMonitor`와 계정·포지션 라우터를 결합했습니다. `CLAUDE.md`는 KISS·YAGNI·Fail-Fast 원칙과 함께 리팩터링 시 재내보내기 심(shim)이나 프록시 모듈 생성을 금지하고, 스테이징 전 `git diff`로 의도치 않은 로직 삭제를 반드시 검수하도록 규정합니다.

**실무 적용 해설**: 모듈 경로나 심볼을 옮길 때 AI 에이전트는 기존 호출부를 모두 고치는 대신 이전 경로에 재내보내기 래퍼(re-export shim)를 남겨 테스트만 통과시키거나, 반대로 편집 중 기존 보안·검증 로직을 조용히 지워버리는 실수를 저지릅니다. AS-IS처럼 임시 호환 래퍼를 방치하면 데드코드가 쌓이고 보안 미들웨어(`IntrusionDetector` 등) 경로 추적이 어려워집니다. TO-BE처럼 심 금지, 모든 호출부 직접 갱신, `git diff` 선확인을 강제하면 코드베이스가 단정하게 유지되지만, 외부 공개 API를 제공하는 라이브러리라면 메이저 버전 경계 외에는 브레이킹 변경을 신중히 통제해야 합니다.

### 2.3 모노레포 세대 공존과 지연 Deprecation 임포트 (`guangtouwangba/langchain`)

- **출처**: [`guangtouwangba/langchain`](https://github.com/guangtouwangba/langchain) · **핵심 스택**: Python (`uv` monorepo), `langchain-core`, `langchain_v1`, `langchain_classic`, `standard-tests` · **적용 판단**: `Assess`
- **기술 개요**: 독립 버저닝되는 `uv` 모노레포로, 핵심 추상화(`libs/core`), 레거시 동결 패키지(`libs/langchain`, `langchain-classic`), 현행 패키지(`libs/langchain_v1`), 서드파티 파트너 패키지(`openai`, `anthropic`, `ollama`), 공용 검증 스위트(`libs/standard-tests`)를 분리 운영합니다. `chat_loaders/whatsapp.py`는 `TYPE_CHECKING` 분기와 모듈 레벨 `__getattr__` + `create_importer`로 구식 임포트 경로의 지연 조회와 deprecation 경고를 처리합니다.

**실무 적용 해설**: 생태계 사용자가 많은 프레임워크에서 `v1` 세대 교체를 단행할 때 기존 패키지 구조를 한꺼번에 제거하면 하위 프로젝트가 전면 중단되는 병목이 생깁니다. AS-IS의 단일 패키지 내 강결합 구조에서 벗어나 `langchain_classic`과 `langchain_v1`을 별도 패키지로 격리하고 `standard-tests`로 파트너 통합 품질을 일원화하며 `__getattr__` 기반 지연 임포트 프록시(`create_importer`)를 둔 TO-BE 전략은 점진적 마이그레이션 경로를 열어줍니다. 그러나 `__getattr__` 동적 조회는 정적 타입 체커와 IDE 점프 기능을 약화시키므로 `TYPE_CHECKING` 블록을 병기해야 하며, 신규 애플리케이션 코드보다는 하위호환 유지가 필수인 SDK 계층에 한정해 적용해야 합니다.

---

## 3. 멀티테넌트 SaaS, 하이브리드 데스크톱 및 CAD 워크트리 통합

### 3.1 전 테이블 RLS 강제와 Mintlify 문서 앵커 규율 (`projectdeathstar61/atom-ops`)

- **출처**: [`projectdeathstar61/atom-ops`](https://github.com/projectdeathstar61/atom-ops) · **핵심 스택**: Next.js 16, React 19, TypeScript strict, Tailwind v4, `shadcn/ui`, Supabase (Postgres RLS), Drizzle ORM, Mintlify · **적용 판단**: `Assess`
- **기술 개요**: 멀티테넌트 운영 SaaS로, `CLAUDE.md`에서 모든 테이블에 `business_id` 컬럼과 Postgres Row-Level Security(RLS) 적용 및 환경변수 누락 시 안전한 빈 상태 렌더링을 강제합니다. 또한 `docs/CLAUDE.md`는 Mintlify 문서 링크를 `.md`/`.mdx` 확장자 없는 루트 상대경로로 통일하고 앵커 파손을 유발하는 em-dash와 아포스트로피 제목 사용을 금지합니다.

**실무 적용 해설**: B2B SaaS를 빠르게 구축할 때 애플리케이션 쿼리의 `WHERE` 절에만 테넌트 격리를 의존하면 단일 API 누락으로 타사 데이터가 노출되는 치명적 위험이 따릅니다. AS-IS의 앱 레벨 필터링 대신 Drizzle + Supabase 조합에서 전 테이블 `business_id`와 DB 차원의 RLS 정책을 강제하고, 정적 문서(`docs/CLAUDE.md`)까지 링크·제목 문법 규칙을 명시한 TO-BE 패턴은 데이터 격리와 문서 빌드 무결성을 함께 지킵니다. 다만 `CLAUDE.md`에 `--no-verify` 커밋 지시가 포함된 점은 로컬 훅 병목을 피하려는 의도라도 CI 단계의 린트·타입·마이그레이션 게이트가 엄격히 작동할 때만 허용되어야 합니다.

### 3.2 형제 워크스페이스와 `.claude/worktrees` 부트스트랩 (`ecto/vcad`)

- **출처**: [`ecto/vcad`](https://github.com/ecto/vcad) · **핵심 스택**: Rust (BRep CAD kernel), TypeScript, React, Three.js, Tauri, WASM, MCP, Python/Gradio (`Qwen2.5-Coder-7B-Instruct` 4-bit) · **적용 판단**: `Assess`
- **기술 개요**: Rust BRep 커널과 React/Three.js 웹 앱, Tauri 데스크톱, MCP 인터페이스를 갖춘 파라메트릭 CAD 시스템(`vcad.io`)입니다. `CLAUDE.md`는 `../tang` 형제 디렉터리 클론 의존성과 `.claude/worktrees/*` 신규 워크트리 생성 시 `node_modules` 부재에 따른 `npm ci` 선행 실행을 안내하며, `packages/hf-space/app.py`는 `BitsAndBytesConfig` 4-bit 양자화 모델로 프롬프트를 `VCode`로 생성해 WASM으로 렌더링합니다.

**실무 적용 해설**: 여러 Git 워크트리를 띄워 병렬 에이전트 작업을 진행할 때 Rust의 형제 경로 의존성(`../tang/crates/*`)이나 비어 있는 `node_modules` 상태를 모른 채 빌드를 돌리면 즉각 실패합니다. AS-IS의 단일 루트 체크아웃 가정에서 벗어나 `CLAUDE.md`에 형제 저장소 위치와 워크트리별 `npm ci` 및 전역 `cargo-tauri` 호출 규칙을 명시한 TO-BE 구성은 병렬 에이전트 환경의 초기 실패율을 크게 낮춥니다. 물론 상대경로 `../tang` 결합은 CI 러너와 컨테이너 마운트 경로 설계를 까다롭게 만드는 트레이드오프가 있으므로, 팀 규모가 커지면 Cargo git/workspace 오버라이드 설정과 함께 관리하는 편이 안정적입니다.

### 3.3 1만 3천 줄 Electron 렌더러 분할과 중앙 셀렉터 레지스트리 (`cd000242-sudo/naver`)

- **출처**: [`cd000242-sudo/naver`](https://github.com/cd000242-sudo/naver) · **핵심 스택**: Electron v31, TypeScript, Puppeteer, Playwright (stealth), MongoDB (Mongoose), Redis, Sharp, Zod · **적용 판단**: `Assess`
- **기술 개요**: Electron v31 기반 콘텐츠 자동화 데스크톱 앱으로 `src/main/` IPC 계층, 13,000줄 이상이던 `renderer.ts`를 45개 모듈로 분할한 `src/renderer/modules/`, 중앙 셀렉터 레지스트리 `src/automation/selectors/`로 구조를 재편했습니다. `examples/CLAUDE.md`는 파일당 200~400줄 권장(최대 800줄), 불변성 유지, Zod 입력 검증, 파라미터화 쿼리 원칙을 담고 있습니다.

**실무 적용 해설**: 1만 줄이 넘는 단일 UI 파일과 코드 곳곳에 흩어진 웹 자동화 CSS/XPath 셀렉터는 AI 에이전트가 한 기능을 고칠 때 다른 화면을 망가뜨리는 주된 원인입니다. AS-IS의 모놀리식 렌더러 및 하드코딩된 셀렉터 분산에서 45개 기능 모듈 분할과 중앙 셀렉터 레지스트리, 파일 크기 상한 규율로 전환한 TO-BE 아키텍처는 에이전트의 컨텍스트 로딩 단위를 작고 안전하게 유지합니다. 다만 외부 웹 페이지 DOM 구조가 수시로 바뀌는 브라우저 자동화 특성상, 셀렉터 레지스트리 분리에 그치지 않고 타깃 DOM 변경을 조기에 감지하는 스모크 검증 루틴을 결합해야 유지보수 부담을 줄일 수 있습니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - Rust 또는 백엔드 프로젝트 지침에 `unwrap()`, 빈 `catch`/`let _ =`, 리팩터링용 임시 심(shim) 생성 금지 항목과 `git diff` 선확인 절차를 명시합니다.
  - `.claude/worktrees`처럼 격리된 Git 워크트리로 병렬 작업을 수행하는 저장소는 형제 디렉터리 의존성과 `npm ci` 부트스트랩 조건을 `CLAUDE.md` 상단에 기록합니다.
  - 멀티테넌트 SaaS에서는 앱 쿼리 필터와 별개로 DB RLS 적용 여부를 점검하고, 정적 문서 앵커 규칙을 린트 대상에 포함합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-04-23 수집 시점의 공개 저장소 `CLAUDE.md` 및 일부 모듈 발췌본을 근거로 하며, 각 저장소의 실제 프로덕션 트래픽 규모나 전체 통합 테스트 통과 여부는 확인되지 않았습니다.
