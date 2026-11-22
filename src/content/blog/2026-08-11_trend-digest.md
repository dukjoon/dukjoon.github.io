---
title: '[Trend] 2026-08-11: Python, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-08-11T00:00:00Z'
description: 2026-08-11 수집된 ChristianV997/MarketOS, openclaw/openclaw, likecoin/likecoin-api-public 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- mcp
- claude-md
- supabase
draft: false
---

2026-08-11 수집된 오픈소스 저장소들에서는 Python, MCP, Claude Code, Supabase 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `ChristianV997/MarketOS`, `openclaw/openclaw`, `gscheinman/kalshi-rt`, `johnmn3/mmllm` | MCP 도구 스키마 분리 및 런타임 세션 격리, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `likecoin/likecoin-api-public`, `awaiswork/frank` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 `docs/ai/CANONICAL_ARCHITECTURE.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`ChristianV997/MarketOS`)

- **출처**: [`ChristianV997/MarketOS`](https://github.com/ChristianV997/MarketOS) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/main.py` 발췌본을 기반으로 확인되는 `ChristianV997/MarketOS` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `docs/ai/CANONICAL_ARCHITECTURE.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/ai/CANONICAL_ARCHITECTURE.md`, `docs/ai/CANONICAL_PATHS.md`, `scripts/ai/check_dev_stack.py`)를 분리해 구성하며 문서 내 주요 섹션(`AI Development Policy`, `Token-efficient workflow`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `ChristianV997/MarketOS`(TO-BE)에서는 `CLAUDE.md`, `backend/main.py`, `docs/ai/CANONICAL_ARCHITECTURE.md` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`openclaw/openclaw`)

- **출처**: [`openclaw/openclaw`](https://github.com/openclaw/openclaw) · **핵심 스택**: `TypeScript`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `agents/skills/autoreview/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `openclaw/openclaw` 저장소는 TypeScript, Claude Code, Stripe 스택 위에서 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/autoreview`, `src/index.ts`)를 분리해 구성하며 `agents/skills/autoreview/CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm docs:list`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `openclaw/openclaw`(TO-BE)에서는 `agents/skills/autoreview/CLAUDE.md`, `CLAUDE.md`, `pnpm docs:list` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.3 Python 기반 `dashboard` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`gscheinman/kalshi-rt`)

- **출처**: [`gscheinman/kalshi-rt`](https://github.com/gscheinman/kalshi-rt) · **핵심 스택**: `Python`, `Claude Code`, `Flask` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `web/app.py` 발췌본을 기반으로 확인되는 `gscheinman/kalshi-rt` 저장소는 Python, Claude Code, Flask 스택 위에서 Python 기반 `dashboard` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`dashboard`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Kalshi RT Trading Algorithm`, `Honest framing (read this every time)`, `Disable browser caching so JS changes land immediately on ne`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `gscheinman/kalshi-rt`(TO-BE)에서는 `CLAUDE.md`, `web/app.py`, `dashboard` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.4 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`johnmn3/mmllm`)

- **출처**: [`johnmn3/mmllm`](https://github.com/johnmn3/mmllm) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `modal_app.py` 발췌본을 기반으로 확인되는 `johnmn3/mmllm` 저장소는 Python, Claude Code 스택 위에서 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Working notes for Claude on this repo`, `Baseline conduct`, `Reporting discipline (post-it note)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `johnmn3/mmllm`(TO-BE)에서는 `CLAUDE.md`, `modal_app.py` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 TypeScript 기반 `src/util/firebase` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`likecoin/likecoin-api-public`)

- **출처**: [`likecoin/likecoin-api-public`](https://github.com/likecoin/likecoin-api-public) · **핵심 스택**: `TypeScript`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Vitest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `test/CLAUDE.md` 발췌본을 기반으로 확인되는 `likecoin/likecoin-api-public` 저장소는 TypeScript, Claude Code, Stripe 스택 위에서 TypeScript 기반 `src/util/firebase` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/util/firebase`, `src/util/cosmos/api`, `src/util/api/likernft/likePrice`)를 분리해 구성하며 문서 내 주요 섹션(`Repository`, `Commands`, `Build pipeline gotchas`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `likecoin/likecoin-api-public`(TO-BE)에서는 `CLAUDE.md`, `test/CLAUDE.md`, `src/util/firebase` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `_configure_logging` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`awaiswork/frank`)

- **출처**: [`awaiswork/frank`](https://github.com/awaiswork/frank) · **핵심 스택**: `FastAPI`, `React`, `TypeScript`, `Python`, `Claude Code`, `PostgreSQL` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `awaiswork/frank` 저장소는 FastAPI, React, TypeScript 스택 위에서 FastAPI 기반 `_configure_logging` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`backend/Dockerfile`)를 분리해 구성하며 핵심 심볼(`_configure_logging`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`CLAUDE.md — Frankly`, `What this is`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `awaiswork/frank`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `_configure_logging` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `ChristianV997/MarketOS`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `openclaw/openclaw`의 `agents/skills/autoreview/CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `likecoin/likecoin-api-public`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-08-11 수집 시점의 공개 저장소 `CLAUDE.md`, `agents/skills/autoreview/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
