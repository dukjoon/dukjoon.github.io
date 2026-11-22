---
title: '[Trend] 2026-09-27: Python, Claude Code 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-09-27T00:00:00Z'
description: 2026-09-27 수집된 armanisadeghi/ai-matrx, kortix-ai/suna, jjjh7401/AI-Lighting_Console 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- stripe
draft: false
---

2026-09-27 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `armanisadeghi/ai-matrx`, `rustycoder/tosich_azoogi_new`, `joshgk00/vanjaro-cli`, `brianporeilly/home-ops` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `kortix-ai/suna`, `jjjh7401/AI-Lighting_Console` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Python 기반 `make a` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`armanisadeghi/ai-matrx`)

- **출처**: [`armanisadeghi/ai-matrx`](https://github.com/armanisadeghi/ai-matrx) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `scripts/sync-main.py` 발췌본을 기반으로 확인되는 `armanisadeghi/ai-matrx` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `make a` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/policies/the-nine-laws.md`, `scripts/sync_skills.py`, `skills/campaign-pattern/SKILL.md`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make a`, `make this`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `armanisadeghi/ai-matrx`(TO-BE)에서는 `CLAUDE.md`, `scripts/sync-main.py`, `make a` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`rustycoder/tosich_azoogi_new`)

- **출처**: [`rustycoder/tosich_azoogi_new`](https://github.com/rustycoder/tosich_azoogi_new) · **핵심 스택**: `Python`, `Claude Code`, `Flask` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `airtable_json_uploader/airtable_json_uploader/app.py` 발췌본을 기반으로 확인되는 `rustycoder/tosich_azoogi_new` 저장소는 Python, Claude Code, Flask 스택 위에서 Python 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Laravel Boost Guidelines`, `Foundational Context`, `Skills Activation`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `rustycoder/tosich_azoogi_new`(TO-BE)에서는 `CLAUDE.md`, `airtable_json_uploader/airtable_json_uploader/app.py` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.3 Python 기반 `pytest` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`joshgk00/vanjaro-cli`)

- **출처**: [`joshgk00/vanjaro-cli`](https://github.com/joshgk00/vanjaro-cli) · **핵심 스택**: `Python`, `Claude Code`, `Pydantic`, `OpenAI SDK`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `tests/CLAUDE.md` 발췌본을 기반으로 확인되는 `joshgk00/vanjaro-cli` 저장소는 Python, Claude Code, Pydantic 스택 위에서 Python 기반 `pytest` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest`, `pytest -m`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `joshgk00/vanjaro-cli`(TO-BE)에서는 `CLAUDE.md`, `tests/CLAUDE.md`, `pytest` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.4 Python 기반 `parse_volume` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`brianporeilly/home-ops`)

- **출처**: [`brianporeilly/home-ops`](https://github.com/brianporeilly/home-ops) · **핵심 스택**: `Python`, `Claude Code`, `Kubernetes` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `scripts/new-app.py` 발췌본을 기반으로 확인되는 `brianporeilly/home-ops` 저장소는 Python, Claude Code, Kubernetes 스택 위에서 Python 기반 `parse_volume` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`parse_volume`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`home-ops: FluxCD/Kubernetes GitOps Repository`, `Directory Structure`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `brianporeilly/home-ops`(TO-BE)에서는 `CLAUDE.md`, `scripts/new-app.py`, `parse_volume` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Claude Code 기반 `pnpm install` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`kortix-ai/suna`)

- **출처**: [`kortix-ai/suna`](https://github.com/kortix-ai/suna) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `deepsec/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `kortix-ai/suna` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `pnpm install` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/writing-matchers.md`)를 분리해 구성하며 `deepsec/CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm install`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `kortix-ai/suna`(TO-BE)에서는 `deepsec/CLAUDE.md`, `CLAUDE.md`, `pnpm install` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `core/moai-constitution.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`jjjh7401/AI-Lighting_Console`)

- **출처**: [`jjjh7401/AI-Lighting_Console`](https://github.com/jjjh7401/AI-Lighting_Console) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Anthropic SDK`, `Gemini SDK`, `WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `server/tests/test_web_app.py` 발췌본을 기반으로 확인되는 `jjjh7401/AI-Lighting_Console` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `core/moai-constitution.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`core/moai-constitution.md`, `core/zone-registry.md`, `core/moai-constitu`)를 분리해 구성하며 문서 내 주요 섹션(`MoAI Execution Directive`, `1. Core Identity`, `HARD Rules (Mandatory)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `jjjh7401/AI-Lighting_Console`(TO-BE)에서는 `CLAUDE.md`, `server/tests/test_web_app.py`, `core/moai-constitution.md` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `armanisadeghi/ai-matrx`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `kortix-ai/suna`의 `deepsec/CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `jjjh7401/AI-Lighting_Console`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-09-27 수집 시점의 공개 저장소 `CLAUDE.md`, `deepsec/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
