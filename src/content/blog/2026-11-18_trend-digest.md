---
title: '[Trend] 2026-11-18: TypeScript, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-11-18T00:00:00Z'
description: 2026-11-18 수집된 speakeasy-api/gram, ldbumble/taskuary, SaibboRiginal/Hestia 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- typescript
- mcp
- claude-md
- supabase
draft: false
---

2026-11-18 수집된 오픈소스 저장소들에서는 TypeScript, MCP, Claude Code, Supabase 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `speakeasy-api/gram`, `CherryHQ/cherry-studio`, `MaiChiLe113/AutonomousUAVforPotholeDetection` | MCP 도구 스키마 분리 및 런타임 세션 격리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `ldbumble/taskuary`, `SaibboRiginal/Hestia`, `Defuera/opengym` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 TypeScript 기반 `npm run build` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`speakeasy-api/gram`)

- **출처**: [`speakeasy-api/gram`](https://github.com/speakeasy-api/gram) · **핵심 스택**: `TypeScript`, `MCP`, `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/clickhouse/CLAUDE.md` 발췌본을 기반으로 확인되는 `speakeasy-api/gram` 저장소는 TypeScript, MCP, Claude Code 스택 위에서 TypeScript 기반 `npm run build` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/ai-control-plane/mcp-gateway/building-servers`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `speakeasy-api/gram`(TO-BE)에서는 `CLAUDE.md`, `examples/clickhouse/CLAUDE.md`, `npm run build` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 TypeScript 기반 `pnpm generate` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`CherryHQ/cherry-studio`)

- **출처**: [`CherryHQ/cherry-studio`](https://github.com/CherryHQ/cherry-studio) · **핵심 스택**: `TypeScript`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK`, `pnpm` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/provider-registry/CLAUDE.md` 발췌본을 기반으로 확인되는 `CherryHQ/cherry-studio` 저장소는 TypeScript, Claude Code, OpenAI SDK 스택 위에서 TypeScript 기반 `pnpm generate` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/creators`, `src/providers`, `scripts/generate-catalog.ts`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm generate`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `CherryHQ/cherry-studio`(TO-BE)에서는 `CLAUDE.md`, `packages/provider-registry/CLAUDE.md`, `pnpm generate` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 FastAPI 기반 `_build_detector` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`MaiChiLe113/AutonomousUAVforPotholeDetection`)

- **출처**: [`MaiChiLe113/AutonomousUAVforPotholeDetection`](https://github.com/MaiChiLe113/AutonomousUAVforPotholeDetection) · **핵심 스택**: `FastAPI`, `Next.js`, `TypeScript`, `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `MaiChiLe113/AutonomousUAVforPotholeDetection` 저장소는 FastAPI, Next.js, TypeScript 스택 위에서 FastAPI 기반 `_build_detector` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/agent-teams.md`, `backend/config.py`, `frontend/lib/config.ts`)를 분리해 구성하며 핵심 심볼(`_build_detector`, `lifespan`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Layout`, `Rules`, `Checks`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `MaiChiLe113/AutonomousUAVforPotholeDetection`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `_build_detector` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Python 기반 `ago` 중심의 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`ldbumble/taskuary`)

- **출처**: [`ldbumble/taskuary`](https://github.com/ldbumble/taskuary) · **핵심 스택**: `Python`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `tests/test_assistant_whole_app.py` 발췌본을 기반으로 확인되는 `ldbumble/taskuary` 저장소는 Python, Claude Code, Stripe 스택 위에서 Python 기반 `ago` 중심의 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 핵심 심볼(`ago`, `store`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Working in this repository`, `Never commit the owner's own data`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `ldbumble/taskuary`(TO-BE)에서는 `CLAUDE.md`, `tests/test_assistant_whole_app.py`, `ago` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `docs/AI-GUIDE.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`SaibboRiginal/Hestia`)

- **출처**: [`SaibboRiginal/Hestia`](https://github.com/SaibboRiginal/Hestia) · **핵심 스택**: `FastAPI`, `Python`, `MCP`, `Claude Code`, `Docker`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `Hestia-Aphrodite/app/main.py` 발췌본을 기반으로 확인되는 `SaibboRiginal/Hestia` 저장소는 FastAPI, Python, MCP 스택 위에서 FastAPI 기반 `docs/AI-GUIDE.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/AI-GUIDE.md`, `docs/REGOLE-DI-MARKO.md`, `frontend/DESIGN-SYSTEM.md`)를 분리해 구성하며 문서 내 주요 섹션(`CLAUDE.md — read first (Claude Code, Forge, any AI working o`, `Work protocol — MANDATORY for every task (human or AI)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `SaibboRiginal/Hestia`(TO-BE)에서는 `CLAUDE.md`, `Hestia-Aphrodite/app/main.py`, `docs/AI-GUIDE.md` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.3 Next.js 기반 `apps/web` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`Defuera/opengym`)

- **출처**: [`Defuera/opengym`](https://github.com/Defuera/opengym) · **핵심 스택**: `Next.js`, `TypeScript`, `Claude Code`, `SQLite`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/web/CLAUDE.md` 발췌본을 기반으로 확인되는 `Defuera/opengym` 저장소는 Next.js, TypeScript, Claude Code 스택 위에서 Next.js 기반 `apps/web` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/web`, `src/app`, `src/app/page.tsx`)를 분리해 구성하며 문서 내 주요 섹션(`Gym Days (OpenGym) — Agent Guide`, `What this is`, `Repo map`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `Defuera/opengym`(TO-BE)에서는 `CLAUDE.md`, `apps/web/CLAUDE.md`, `apps/web` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `speakeasy-api/gram`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `ldbumble/taskuary`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `SaibboRiginal/Hestia`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-11-18 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
