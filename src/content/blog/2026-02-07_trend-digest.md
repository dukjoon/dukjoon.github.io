---
title: "[Trend] 2026-02-07: 프롬프트·하니스 분리와 E2E 경험 기준선"
pubDatetime: 2026-02-07T00:00:00Z
description: "에이전트 정의와 실행 하니스 분리, 동적 deprecation 심(shim), npm/jiti 플러그인 의존성 격리, @journey/@P0 E2E 기준선 전략을 다룹니다."
category: trend
tags:
  - trend
  - ai-agent
  - monorepo
  - e2e-testing
  - python
draft: false
---

에이전트 프레임워크와 대형 모노레포가 성숙하면서, 모델에 독립적인 실행 하니스(Harness) 분리와 레거시 임포트 호환성 유지, 그리고 사용자 여정 기반 E2E 회귀 방어선이 주요 엔지니어링 과제로 나타나고 있습니다. 이번 일자에서는 런타임·하니스 아키텍처와 모노레포 품질·테스트 체계를 중심으로 핵심 패턴을 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 에이전트 하니스 및 플러그인 경계 | `weakincentives/weakincentives`, `AmirulAndalib/openclaw` | 프롬프트 정의와 하니스 분리·리듀서 상태 관리, `workspace:*` 배제 및 `jiti` 플러그인 로딩 |
| 모노레포 호환성 및 검증 체계 | `rpatil524/langchain`, `PrakrutR/genhub-v2`, `AudiusProject/apps`, `aliavni/incubator-superset` | 동적 deprecation 임포터, `@journey`/`@P0` E2E 태그, 디렉터리 스코프 실행 및 `pre-commit` 게이트 |

---

## 2. 에이전트 하니스 및 플러그인 경계

### 2.1 프롬프트 정의-실행 하니스 분리와 불변 이벤트 리듀서 (`weakincentives/weakincentives`)

- **출처**: [`weakincentives/weakincentives`](https://github.com/weakincentives/weakincentives) · **핵심 스택**: `Python`, `FastAPI`, `SQLite`, `OpenAI / LiteLLM / Claude Agent SDK` · **적용 판단**: `Trial`
- **기술 개요**: 프롬프트와 도구를 계층적 문서로 묶는 에이전트 정의(Definition)와 샌드박스·재시도·크래시 복구를 담당하는 실행 하니스(Harness)를 분리하고, 타입드 이벤트 기반 순수 리듀서로 상태를 스냅샷화하며 `debug_app.py`에서 SQLite 캐시 기반 디버그 번들 웹 뷰어를 제공합니다.

**실무 적용 해설**: 에이전트 루프 안에 프롬프트 조립, LLM API 재시도, 상태 변이가 뒤섞여 있으면(AS-IS) 모델 프로바이더를 바꾸거나 장애 시점을 재현하기가 매우 어렵습니다. `weakincentives`처럼 상태 변경을 순수 리듀서와 불변 스냅샷으로 제한하고 하니스 계층이 타임아웃·스로틀링을 전담하며, 디버그 번들(`.zip`)을 `wink query`와 동일한 SQLite 캐시 계층(`debug_app.py`)으로 조회(TO-BE)하면 재현성과 프로바이더 이식성을 동시에 확보할 수 있습니다. 다만 도구 레지스트리를 프롬프트 문서 내부에 통합하는 구조는 도구 수가 수십 개를 넘을 때 프롬프트 길이가 급증할 수 있으므로 토큰 예산 관리가 필요합니다.

### 2.2 확장 패키지 의존성 격리와 FastAPI 스킬 검증 핸들러 (`AmirulAndalib/openclaw`)

- **출처**: [`AmirulAndalib/openclaw`](https://github.com/AmirulAndalib/openclaw) · **핵심 스택**: `TypeScript`, `Node.js (jiti)`, `Python FastAPI` · **적용 판단**: `Trial`
- **기술 개요**: `extensions/*` 플러그인 전용 의존성을 루트 `package.json`에 올리지 않고 `npm install --omit=dev` 호환성을 위해 `dependencies` 내 `workspace:*` 사용을 금지(`openclaw`는 `peerDependencies`/`devDependencies`로 두고 런타임에 `jiti`로 `openclaw/plugin-sdk` 해석)하며, Python 스킬(`local_places/main.py`)에 `RequestValidationError` 커스텀 로깅 핸들러를 둔 구조입니다.

**실무 적용 해설**: 모노레포 확장 플러그인을 배포할 때 `workspace:*` 프로토콜을 런타임 `dependencies`에 그대로 두면(AS-IS) 외부 환경에서 `npm install --omit=dev` 설치 시 패키지 해석 오류가 발생합니다. 플러그인별 의존성을 개별 `package.json`에 가두고 코어 SDK는 `peerDependencies`와 런타임 에일리어스(`jiti`)로 연결하며, 스킬 마이크로서비스(`FastAPI`)의 입력 검증 오류를 전역 예외 핸들러로 구조화 로깅(TO-BE)하면 배포 실패와 디버깅 맹점을 함께 줄일 수 있습니다. 단 `jiti` 기반 런타임 해석은 TypeScript 컴파일 시점 검사를 우회할 수 있으므로 플러그인 단위 테스트(`*.test.ts`)에서 SDK 계약을 검증해야 합니다.

---

## 3. 모노레포 호환성 및 검증 체계

### 3.1 `uv` 패키지 분할과 동적 Deprecation 심(Shim) (`rpatil524/langchain`)

- **출처**: [`rpatil524/langchain`](https://github.com/rpatil524/langchain) · **핵심 스택**: `Python`, `uv Monorepo`, `langchain-core / v1 / classic` · **적용 판단**: `Trial`
- **기술 개요**: `libs/core`, `libs/langchain`(레거시 `langchain-classic`), `libs/langchain_v1`, `libs/partners/*`, `libs/standard-tests`로 독립 버전 패키지를 분리하고, `whatsapp.py` 등에서 `create_importer`와 `__getattr__` 기반 `DEPRECATED_LOOKUP`으로 구 경로 임포트를 `langchain_community`로 동적 위임하는 구조입니다.

**실무 적용 해설**: 대규모 라이브러리에서 패키지를 쪼개고 모듈 경로를 개편할 때 구 임포트 경로를 일괄 삭제하면(AS-IS) 하위 호환성이 깨져 사용자 업그레이드가 중단되고, 반대로 전 모듈을 정적 re-export하면 순환 참조와 기동 시간 증가가 발생합니다. `DEPRECATED_LOOKUP`과 모듈 레벨 `__getattr__` 및 `TYPE_CHECKING` 분기를 결합한 `create_importer` 패턴(TO-BE)을 쓰면 IDE 정적 타입 추론은 유지하면서도 실제 런타임 접근 시점에만 지연 로딩과 deprecation 경고를 출력할 수 있습니다. 또한 `libs/standard-tests`처럼 서드파티 파트너 통합이 공통으로 통과해야 할 표준 테스트 스위트를 분리해 둔 점도 생태계 품질 유지에 유효합니다.

### 3.2 `@journey`·`@P0` 태그 기반 경험 주도 E2E 기준선 (`PrakrutR/genhub-v2`)

- **출처**: [`PrakrutR/genhub-v2`](https://github.com/PrakrutR/genhub-v2) · **핵심 스택**: `Cucumber`, `Playwright`, `LobeChat Architecture` · **적용 판단**: `Trial`
- **기술 개요**: LobeChat 계열 저장소의 `e2e/CLAUDE.md`에서 사용자 여정 검증을 위한 `@journey`, `@smoke`, `@regression` 및 우선순위 태그(`@P0` CI 필수, `@P1` 야간 배치, `@P2` 릴리스 전)와 모듈별(`@agent`, `@agent-group`) 커버리지 매트릭스를 정의한 사례입니다.

**실무 적용 해설**: 기능 단위 컴포넌트 테스트만 존재하고 통합 E2E 테스트가 우선순위 없이 쌓이면(AS-IS) CI 실행 시간이 폭증해 개발자가 테스트 스위트를 우회하거나 회귀를 놓치게 됩니다. 핵심 사용자 여정을 `@journey`와 `@P0` 태그로 선별해 PR 머지 게이트에 묶고, 보조 시나리오는 `@P1`(Nightly)과 `@P2`(Release)로 주기를 차등화(TO-BE)하면 리팩토링 안전망과 CI 피드백 속도의 균형을 맞출 수 있습니다. 단 Gherkin/Cucumber 계층은 스텝 정의 유지보수 비용이 따르므로 핵심 비즈니스 플로우(`@P0`)에 집중해 비대화를 경계해야 합니다.

### 3.3 디렉터리 스코프 실행과 로컬 프로토콜 스택 (`AudiusProject/apps`)

- **출처**: [`AudiusProject/apps`](https://github.com/AudiusProject/apps) · **핵심 스택**: `React + Vite`, `React Native`, `Docker`, `Ethereum/Solana`, `Python pandas` · **적용 판단**: `Assess`
- **기술 개요**: 웹/모바일/백엔드/스마트컨트랙트를 아우르는 모노레포에서 변경 디렉터리 내부에서만 빌드·개발 명령(`web:dev`, `web:stage`, `web:prod`)을 실행하도록 제한하고, `npm run protocol`과 `audius-compose connect`로 로컬 Docker 프로토콜 스택을 연결하며 `track-cid-backfill/python/main.py` 같은 운영 데이터 보정 스크립트를 함께 관리합니다.

**실무 적용 해설**: 웹 클라이언트, 노드 서비스, 블록체인 컨트랙트가 한 저장소에 섞여 있을 때 루트에서 전체 워크스페이스 빌드를 매번 돌리면(AS-IS) 무관한 체인 툴체인 오류로 로컬 작업이 막힙니다. `CLAUDE.md`에 "루트가 아닌 변경 대상 디렉터리에서만 명령을 실행하라"는 원칙과 스테이지별 환경(`local`/`stage`/`prod`) 타깃을 분리해 두고 로컬 스택은 `audius-compose`로 추상화(TO-BE)하면 클라이언트 개발자의 로컬 셋업 부담을 낮출 수 있습니다. 반면 운영 백필 스크립트(`track-cid-backfill`)처럼 `Unnamed: 0` CSV 컬럼을 수동 제거하는 일회성 코드가 방치되면 경로 하드코딩 오류가 나기 쉬우므로 인자화·테스트 격리가 필요합니다.

### 3.4 `pre-commit` 필수 게이트와 레거시 JS 차단 (`aliavni/incubator-superset`)

- **출처**: [`aliavni/incubator-superset`](https://github.com/aliavni/incubator-superset) · **핵심 스택**: `Python (Flask)`, `React/TypeScript`, `Docusaurus 3`, `pre-commit` · **적용 판단**: `Trial`
- **기술 개요**: 커밋 푸시 전 `pre-commit run --all-files`(Black, Prettier, ESLint, MyPy, Ruff, Pylint) 실행을 강제하고, 프론트엔드 현대화 중 `any` 타입과 신규 `.js` 파일 생성을 금지하며 `/docs` 하위 작업은 `docs/DOCS_CLAUDE.md`(Docusaurus 3)로 맥락을 격리한 사례입니다.

**실무 적용 해설**: 대규모 오픈소스 프로젝트에서 에이전트가 자동 포매팅과 타입 검사를 거치지 않고 커밋을 올리면(AS-IS) CI 린트 단계에서 반복 실패해 리뷰 주기가 길어집니다. 푸시 전 `pre-commit run --all-files`와 자동 수정 재스테이징 절차를 워크플로우로 고정하고, 진행 중인 TypeScript 전환 방향(`NO any`, `NO JS`)을 명시(TO-BE)하면 CI 반려율을 크게 낮출 수 있습니다. 다만 `all-files` 훅은 대형 저장소에서 실행 시간이 길어질 수 있으므로 스테이징 파일 대상 훅과 전체 검사를 상황에 맞게 병행하는 전략이 필요합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - 확장 플러그인 아키텍처에서는 `workspace:*` 대신 `peerDependencies`와 런타임 SDK 해석을 검증해 `npm install --omit=dev` 배포 호환성을 확보합니다.
  - E2E 테스트 스위트는 `@P0`(PR 게이트), `@P1`(야간), `@P2`(배포 전)로 계층화해 핵심 사용자 여정의 회귀만 빠르게 차단합니다.
  - 레거시 모듈 이전 시에는 `__getattr__` + `TYPE_CHECKING` 기반 동적 deprecation 심으로 정적 타입 검사와 하위 호환성을 동시에 유지합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-07 수집 시점의 `CLAUDE.md` 및 대표 소스 파일 최대 1,000자 발췌본에 근거합니다. `langchain`, `openclaw`, `genhub-v2`, `incubator-superset` 등 포크 기반 저장소는 업스트림 최신 커밋과 차이가 있을 수 있습니다.
