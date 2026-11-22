---
title: '[Trend] 2026-07-13: Claude Code, OpenAI SDK 기반 독립 스킬 디렉터리 격리와 모듈형 런타임'
pubDatetime: '2026-07-13T00:00:00Z'
description: 2026-07-13 수집된 barkleesanders/claude-code-starter, barrygee/Sentinel, JDonaghy/claude-coordinator 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- openai
- gemini
- fastapi
draft: false
---

2026-07-13 수집된 오픈소스 저장소들에서는 Claude Code, OpenAI SDK, Gemini SDK, FastAPI 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트 | `barkleesanders/claude-code-starter`, `JDonaghy/claude-coordinator`, `RyanMKrol/LocalJobs` | 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, MCP 도구 스키마 분리 및 런타임 세션 격리 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `barrygee/Sentinel`, `procarepharmacies-ops/ProCare-OS`, `SJParthi/bruteX` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조, 정적 타입 계약 기반 런타임 분리 및 빌드·검증 파이프라인 |

---

## 2. 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트

### 2.1 Claude Code 기반 `skills/hooks/pre-edit-check.sh` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`barkleesanders/claude-code-starter`)

- **출처**: [`barkleesanders/claude-code-starter`](https://github.com/barkleesanders/claude-code-starter) · **핵심 스택**: `Claude Code`, `OpenAI SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `skills/app-onboarding-questionnaire/CLAUDE.md` 발췌본을 기반으로 확인되는 `barkleesanders/claude-code-starter` 저장소는 Claude Code, OpenAI SDK, Gemini SDK 스택 위에서 Claude Code 기반 `skills/hooks/pre-edit-check.sh` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/hooks/pre-edit-check.sh`, `skills/hooks/track-file-reads.sh`)를 분리해 구성하며 문서 내 주요 섹션(`Global Claude Code Configuration`, `Read-Before-Edit Rule (MANDATORY for agents)`, `What This Is`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `barkleesanders/claude-code-starter`(TO-BE)에서는 `CLAUDE.md`, `skills/app-onboarding-questionnaire/CLAUDE.md`, `skills/hooks/pre-edit-check.sh` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.2 Python 기반 `_installed_version` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`JDonaghy/claude-coordinator`)

- **출처**: [`JDonaghy/claude-coordinator`](https://github.com/JDonaghy/claude-coordinator) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `coord/agent_app.py` 발췌본을 기반으로 확인되는 `JDonaghy/claude-coordinator` 저장소는 Python, Claude Code 스택 위에서 Python 기반 `_installed_version` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`_installed_version`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`claude-coordinator`, `Current Goal — read first`, `Codebase navigation — query the graph first`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `JDonaghy/claude-coordinator`(TO-BE)에서는 `CLAUDE.md`, `coord/agent_app.py`, `_installed_version` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 Claude Code 기반 `docs/HARNESS.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`RyanMKrol/LocalJobs`)

- **출처**: [`RyanMKrol/LocalJobs`](https://github.com/RyanMKrol/LocalJobs) · **핵심 스택**: `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `harness/CLAUDE.md`, `harness/custom/CLAUDE.md` 발췌본을 기반으로 확인되는 `RyanMKrol/LocalJobs` 저장소는 Claude Code, Gemini SDK 스택 위에서 Claude Code 기반 `docs/HARNESS.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/HARNESS.md`, `docs/designs`)를 분리해 구성하며 문서 내 주요 섹션(`harness/CLAUDE.md — rules for working inside the build harne`, `️ STOP before editing any .harness/ file in place — customiz`, `harness/custom/CLAUDE.md — your project-specific harness ins`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `RyanMKrol/LocalJobs`(TO-BE)에서는 `harness/CLAUDE.md`, `harness/custom/CLAUDE.md`, `docs/HARNESS.md` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 FastAPI 기반 `_daily_cleanup_loop` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`barrygee/Sentinel`)

- **출처**: [`barrygee/Sentinel`](https://github.com/barrygee/Sentinel) · **핵심 스택**: `FastAPI`, `TypeScript`, `Python`, `Claude Code`, `Docker`, `uv` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/main.py` 발췌본을 기반으로 확인되는 `barrygee/Sentinel` 저장소는 FastAPI, TypeScript, Python 스택 위에서 FastAPI 기반 `_daily_cleanup_loop` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`frontend/vue`, `frontend/vue/vite.config.ts`)를 분리해 구성하며 핵심 심볼(`_daily_cleanup_loop`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`docker compose up`, `uv run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `barrygee/Sentinel`(TO-BE)에서는 `CLAUDE.md`, `backend/main.py`, `docker compose up` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 FastAPI 기반 `npm run dev` 워크플로우 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`procarepharmacies-ops/ProCare-OS`)

- **출처**: [`procarepharmacies-ops/ProCare-OS`](https://github.com/procarepharmacies-ops/ProCare-OS) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `SQLite`, `Docker` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/backend/app/main.py` 발췌본을 기반으로 확인되는 `procarepharmacies-ops/ProCare-OS` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `npm run dev` 워크플로우 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/backend`, `src/frontend`, `api/health`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run dev`, `docker compose up`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `procarepharmacies-ops/ProCare-OS`(TO-BE)에서는 `CLAUDE.md`, `src/backend/app/main.py`, `npm run dev` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

### 3.3 FastAPI 기반 `api/v1/state` 모듈 분리와 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계 (`SJParthi/bruteX`)

- **출처**: [`SJParthi/bruteX`](https://github.com/SJParthi/bruteX) · **핵심 스택**: `FastAPI`, `Python`, `Rust`, `Claude Code`, `WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `brutex/dashboard/app.py` 발췌본을 기반으로 확인되는 `SJParthi/bruteX` 저장소는 FastAPI, Python, Rust 스택 위에서 FastAPI 기반 `api/v1/state` 모듈 분리와 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/v1/state`, `api/v1/events`)를 분리해 구성하며 문서 내 주요 섹션(`BruteX — Claude Code Project Rules`, `Design`, `Endpoints`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 고빈도 입출력이나 프로세스 체크포인팅, 동시성 처리를 동적 스크립트 단일 계층으로만 처리하면 런타임 오류와 메모리·지연 시간 병목을 조기에 통제하기 어렵습니다. 반면 `SJParthi/bruteX`(TO-BE)에서는 `CLAUDE.md`, `brutex/dashboard/app.py`, `api/v1/state` 등 명시적 아티팩트를 기준으로 핵심 실행 경로와 상태 덤프·복원 또는 API 계약을 시스템 언어와 벤치마크 도구로 격리하고 재현 가능한 측정·빌드 절차를 문서에 고정하여 런타임 신뢰성을 높입니다. 다만 커널·네이티브 의존성이나 다중 언어 툴체인 유지에 따른 환경 제약이 존재하므로 컨테이너 격리와 플랫폼별 호환성 검증을 선행해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `barkleesanders/claude-code-starter`의 `CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `barrygee/Sentinel`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `JDonaghy/claude-coordinator`의 `CLAUDE.md` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-13 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
