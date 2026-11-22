---
title: '[Trend] 2026-07-26: Python, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-07-26T00:00:00Z'
description: 2026-07-26 수집된 jussray/founder-control-room, psw2025-cmd/Genesis_System3, Solizardking/solana-clawd 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- mcp
- claude-md
- supabase
draft: false
---

2026-07-26 수집된 오픈소스 저장소들에서는 Python, MCP, Claude Code, Supabase 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `jussray/founder-control-room`, `psw2025-cmd/Genesis_System3`, `Solizardking/solana-clawd`, `JakeKJakeK/teaching-hub` | MCP 도구 스키마 분리 및 런타임 세션 격리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `ugobe007/Ready_For_Robots`, `Paradispartiet/History-Go` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 `read_database_url` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`jussray/founder-control-room`)

- **출처**: [`jussray/founder-control-room`](https://github.com/jussray/founder-control-room) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `Supabase`, `PostgreSQL`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `jussray/founder-control-room` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `read_database_url` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/unified-growth-inbo`)를 분리해 구성하며 핵심 심볼(`read_database_url`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Claude Operating Contract — founder-control-room`, `5W1H — Required Before Every Nontrivial Action`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `jussray/founder-control-room`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `read_database_url` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`psw2025-cmd/Genesis_System3`)

- **출처**: [`psw2025-cmd/Genesis_System3`](https://github.com/psw2025-cmd/Genesis_System3) · **핵심 스택**: `Python`, `Cursor Rules`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `dashboard/app.py` 발췌본을 기반으로 확인되는 `psw2025-cmd/Genesis_System3` 저장소는 Python, Cursor Rules, Gemini SDK 스택 위에서 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Genesis System3 – Cursor Agent Rules`, `Response standard (production-grade answers always)`, `Absolute rules`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `psw2025-cmd/Genesis_System3`(TO-BE)에서는 `.cursorrules`, `dashboard/app.py` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 MCP 기반 `npm run generate` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`Solizardking/solana-clawd`)

- **출처**: [`Solizardking/solana-clawd`](https://github.com/Solizardking/solana-clawd) · **핵심 스택**: `MCP`, `Claude Code`, `Supabase`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `clawd-code/CLAUDE.md`, `library/CLAUDE.md` 발췌본을 기반으로 확인되는 `Solizardking/solana-clawd` 저장소는 MCP, Claude Code, Supabase 스택 위에서 MCP 기반 `npm run generate` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. `clawd-code/CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run generate`, `npm run build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `Solizardking/solana-clawd`(TO-BE)에서는 `clawd-code/CLAUDE.md`, `library/CLAUDE.md`, `npm run generate` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.4 TypeScript 기반 `skills/impeccable` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`JakeKJakeK/teaching-hub`)

- **출처**: [`JakeKJakeK/teaching-hub`](https://github.com/JakeKJakeK/teaching-hub) · **핵심 스택**: `TypeScript`, `Claude Code`, `Supabase`, `Docker`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/components/CLAUDE.md` 발췌본을 기반으로 확인되는 `JakeKJakeK/teaching-hub` 저장소는 TypeScript, Claude Code, Supabase 스택 위에서 TypeScript 기반 `skills/impeccable` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/impeccable`, `src/components/flex/slides`, `src/curriculum`)를 분리해 구성하며 문서 내 주요 섹션(`Teaching Hub — Root Rules`, `Design-skill boundary (impeccable) — WHERE IT MAY AND MAY NO`, `Components — Rules`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `JakeKJakeK/teaching-hub`(TO-BE)에서는 `CLAUDE.md`, `src/components/CLAUDE.md`, `skills/impeccable` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Claude Code 기반 `docs/product_market_fit.md` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`ugobe007/Ready_For_Robots`)

- **출처**: [`ugobe007/Ready_For_Robots`](https://github.com/ugobe007/Ready_For_Robots) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `PostgreSQL`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `agents/skills/supabase-postgres-best-practices/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `ugobe007/Ready_For_Robots` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `docs/product_market_fit.md` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/product_market_fit.md`, `docs/competitive_positioning.md`, `docs/value_first_principle.md`)를 분리해 구성하며 문서 내 주요 섹션(`Supabase Postgres Best Practices`, `Structure`, `Usage`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `ugobe007/Ready_For_Robots`(TO-BE)에서는 `agents/skills/supabase-postgres-best-practices/CLAUDE.md`, `CLAUDE.md`, `docs/product_market_fit.md` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `lifespan` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`Paradispartiet/History-Go`)

- **출처**: [`Paradispartiet/History-Go`](https://github.com/Paradispartiet/History-Go) · **핵심 스택**: `FastAPI`, `TypeScript`, `Python`, `Claude Code`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `Paradispartiet/History-Go` 저장소는 FastAPI, TypeScript, Python 스택 위에서 FastAPI 기반 `lifespan` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/typescript-migration-pla`)를 분리해 구성하며 핵심 심볼(`lifespan`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`What this is`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `Paradispartiet/History-Go`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `lifespan` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `jussray/founder-control-room`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `psw2025-cmd/Genesis_System3`의 `.cursorrules` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Solizardking/solana-clawd`의 `clawd-code/CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-26 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules`, `clawd-code/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
