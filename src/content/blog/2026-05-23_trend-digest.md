---
title: '[Trend] 2026-05-23: Python, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-05-23T00:00:00Z'
description: 2026-05-23 수집된 Jia-520-only/Miya, polysemic/Subumbra, kfriede/amplihack 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- mcp
- claude-md
- openai
draft: false
---

2026-05-23 수집된 오픈소스 저장소들에서는 Python, MCP, Claude Code, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `Jia-520-only/Miya`, `polysemic/Subumbra`, `kfriede/amplihack` | MCP 도구 스키마 분리 및 런타임 세션 격리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화 | `onur-tech/KongTradeBot`, `boringstack-xyz/api-template`, `ALIYILD/DeepSynaps-Protocol-Studio` | 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`Jia-520-only/Miya`)

- **출처**: [`Jia-520-only/Miya`](https://github.com/Jia-520-only/Miya) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `astrbot/main.py` 발췌본을 기반으로 확인되는 `Jia-520-only/Miya` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`弥娅 (MIYA) - AI 虚拟化身`, `重要规则`, `行为准则`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `Jia-520-only/Miya`(TO-BE)에서는 `CLAUDE.md`, `astrbot/main.py` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 `docs/apps/litellm` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`polysemic/Subumbra`)

- **출처**: [`polysemic/Subumbra`](https://github.com/polysemic/Subumbra) · **핵심 스택**: `Python`, `Claude Code`, `Docker`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `subumbra-keys/app.py` 발췌본을 기반으로 확인되는 `polysemic/Subumbra` 저장소는 Python, Claude Code, Docker 스택 위에서 Python 기반 `docs/apps/litellm` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/apps/litellm`)를 분리해 구성하며 문서 내 주요 섹션(`Subumbra — Universal Zero-Trust Secret Broker`, `Project Purpose`, `Architecture`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `polysemic/Subumbra`(TO-BE)에서는 `CLAUDE.md`, `subumbra-keys/app.py`, `docs/apps/litellm` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`kfriede/amplihack`)

- **출처**: [`kfriede/amplihack`](https://github.com/kfriede/amplihack) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.github/scripts/pr_triage_main.py`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `kfriede/amplihack` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Add scripts directory to path for imports`, `Get PR number from environment`, `Create validator`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `kfriede/amplihack`(TO-BE)에서는 `.github/scripts/pr_triage_main.py`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화

### 3.1 Python 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`onur-tech/KongTradeBot`)

- **출처**: [`onur-tech/KongTradeBot`](https://github.com/onur-tech/KongTradeBot) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `onur-tech/KongTradeBot` 저장소는 Python, Claude Code 스택 위에서 Python 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Running the Bot`, `Install dependencies (one-time)`, `Dry-run (default — simulates trades, no real money)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `onur-tech/KongTradeBot`(TO-BE)에서는 `CLAUDE.md`, `main.py` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

### 3.2 TypeScript 기반 `bun run validate` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`boringstack-xyz/api-template`)

- **출처**: [`boringstack-xyz/api-template`](https://github.com/boringstack-xyz/api-template) · **핵심 스택**: `TypeScript`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Bun` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/api/accounts/CLAUDE.md` 발췌본을 기반으로 확인되는 `boringstack-xyz/api-template` 저장소는 TypeScript, Claude Code, Stripe 스택 위에서 TypeScript 기반 `bun run validate` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/api/accounts/invitations.service.test.ts`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`bun run validate`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `boringstack-xyz/api-template`(TO-BE)에서는 `CLAUDE.md`, `src/api/accounts/CLAUDE.md`, `bun run validate` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.3 FastAPI 기반 `scripts/deploy-preview.sh` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`ALIYILD/DeepSynaps-Protocol-Studio`)

- **출처**: [`ALIYILD/DeepSynaps-Protocol-Studio`](https://github.com/ALIYILD/DeepSynaps-Protocol-Studio) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Stripe` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/api/app/main.py` 발췌본을 기반으로 확인되는 `ALIYILD/DeepSynaps-Protocol-Studio` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `scripts/deploy-preview.sh` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/deploy-preview.sh`, `scripts/deploy-via-hook.sh`)를 분리해 구성하며 문서 내 주요 섹션(`DeepSynaps Protocol Studio — session notes for Claude Code`, `Preview deploy (run at end of a task)`, `Phase-8 DX: validate required env vars BEFORE any DB / route`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `ALIYILD/DeepSynaps-Protocol-Studio`(TO-BE)에서는 `CLAUDE.md`, `apps/api/app/main.py`, `scripts/deploy-preview.sh` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `Jia-520-only/Miya`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `polysemic/Subumbra`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `kfriede/amplihack`의 `.github/scripts/pr_triage_main.py` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-05-23 수집 시점의 공개 저장소 `CLAUDE.md`, `.github/scripts/pr_triage_main.py` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
