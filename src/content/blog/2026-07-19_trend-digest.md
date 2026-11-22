---
title: '[Trend] 2026-07-19: Claude Code, Supabase 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-07-19T00:00:00Z'
description: 2026-07-19 수집된 simstudioai/sim, lisqq1/openclaw, Yeachan-Heo/claw-code 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- supabase
- stripe
- langgraph
draft: false
---

2026-07-19 수집된 오픈소스 저장소들에서는 Claude Code, Supabase, Stripe, LangGraph 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `simstudioai/sim`, `lisqq1/openclaw`, `MachuEngine/bunpil` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 시스템 런타임·타입 안전 백엔드 및 컨테이너 인프라 | `Yeachan-Heo/claw-code`, `COMRADEART/virtual-brain-engine`, `jgyy/world-of-claudecraft` | 정적 타입 계약 기반 런타임 분리 및 빌드·검증 파이프라인, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Claude Code 기반 `bun run check:api-validation` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`simstudioai/sim`)

- **출처**: [`simstudioai/sim`](https://github.com/simstudioai/sim) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `LangGraph`, `CrewAI`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/sim/app/(landing)/CLAUDE.md` 발췌본을 기반으로 확인되는 `simstudioai/sim` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `bun run check:api-validation` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`core/utils/with-route-handler`, `apps/sim/lib/content`, `apps/sim/lib/blog`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`bun run check:api-validation`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `simstudioai/sim`(TO-BE)에서는 `CLAUDE.md`, `apps/sim/app/(landing)/CLAUDE.md`, `bun run check:api-validation` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`lisqq1/openclaw`)

- **출처**: [`lisqq1/openclaw`](https://github.com/lisqq1/openclaw) · **핵심 스택**: `TypeScript`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `agents/skills/autoreview/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `lisqq1/openclaw` 저장소는 TypeScript, Claude Code, Stripe 스택 위에서 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/autoreview`, `src/index.ts`)를 분리해 구성하며 `agents/skills/autoreview/CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm docs:list`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `lisqq1/openclaw`(TO-BE)에서는 `agents/skills/autoreview/CLAUDE.md`, `CLAUDE.md`, `pnpm docs:list` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.3 FastAPI 기반 `limit_request_size` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`MachuEngine/bunpil`)

- **출처**: [`MachuEngine/bunpil`](https://github.com/MachuEngine/bunpil) · **핵심 스택**: `FastAPI`, `Next.js`, `React`, `Python`, `Claude Code`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `app/main.py` 발췌본을 기반으로 확인되는 `MachuEngine/bunpil` 저장소는 FastAPI, Next.js, React 스택 위에서 FastAPI 기반 `limit_request_size` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`limit_request_size`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`CLAUDE.md — 분필 (사회 교사용 AI 어시스턴트)`, `프로젝트 한 줄`, `핵심 컨벤션`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `MachuEngine/bunpil`(TO-BE)에서는 `CLAUDE.md`, `app/main.py`, `limit_request_size` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 시스템 런타임·타입 안전 백엔드 및 컨테이너 인프라

### 3.1 Python 기반 `build_parser` 중심의 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계 (`Yeachan-Heo/claw-code`)

- **출처**: [`Yeachan-Heo/claw-code`](https://github.com/Yeachan-Heo/claw-code) · **핵심 스택**: `Python`, `Rust`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/main.py` 발췌본을 기반으로 확인되는 `Yeachan-Heo/claw-code` 저장소는 Python, Rust, Claude Code 스택 위에서 Python 기반 `build_parser` 중심의 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`build_parser`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`cargo test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 고빈도 입출력이나 프로세스 체크포인팅, 동시성 처리를 동적 스크립트 단일 계층으로만 처리하면 런타임 오류와 메모리·지연 시간 병목을 조기에 통제하기 어렵습니다. 반면 `Yeachan-Heo/claw-code`(TO-BE)에서는 `CLAUDE.md`, `src/main.py`, `cargo test` 등 명시적 아티팩트를 기준으로 핵심 실행 경로와 상태 덤프·복원 또는 API 계약을 시스템 언어와 벤치마크 도구로 격리하고 재현 가능한 측정·빌드 절차를 문서에 고정하여 런타임 신뢰성을 높입니다. 다만 커널·네이티브 의존성이나 다중 언어 툴체인 유지에 따른 환경 제약이 존재하므로 컨테이너 격리와 플랫폼별 호환성 검증을 선행해야 합니다.

---

### 3.2 FastAPI 기반 `api/perceive` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`COMRADEART/virtual-brain-engine`)

- **출처**: [`COMRADEART/virtual-brain-engine`](https://github.com/COMRADEART/virtual-brain-engine) · **핵심 스택**: `FastAPI`, `React`, `TypeScript`, `Python`, `Rust`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `worker/main.py` 발췌본을 기반으로 확인되는 `COMRADEART/virtual-brain-engine` 저장소는 FastAPI, React, TypeScript 스택 위에서 FastAPI 기반 `api/perceive` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/perceive`)를 분리해 구성하며 문서 내 주요 섹션(`Repo layout`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `COMRADEART/virtual-brain-engine`(TO-BE)에서는 `CLAUDE.md`, `worker/main.py`, `api/perceive` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.3 TypeScript 기반 `npm run bot` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`jgyy/world-of-claudecraft`)

- **출처**: [`jgyy/world-of-claudecraft`](https://github.com/jgyy/world-of-claudecraft) · **핵심 스택**: `TypeScript`, `Claude Code`, `Stripe`, `PostgreSQL`, `OpenAI SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `bot/CLAUDE.md` 발췌본을 기반으로 확인되는 `jgyy/world-of-claudecraft` 저장소는 TypeScript, Claude Code, Stripe 스택 위에서 TypeScript 기반 `npm run bot` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/sim`, `src/render`, `src/admin`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run bot`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `jgyy/world-of-claudecraft`(TO-BE)에서는 `CLAUDE.md`, `bot/CLAUDE.md`, `npm run bot` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `simstudioai/sim`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `lisqq1/openclaw`의 `agents/skills/autoreview/CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Yeachan-Heo/claw-code`의 `CLAUDE.md` 구성처럼 정적 타입 계약 기반 런타임 분리 및 빌드·검증 파이프라인 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-19 수집 시점의 공개 저장소 `CLAUDE.md`, `agents/skills/autoreview/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
