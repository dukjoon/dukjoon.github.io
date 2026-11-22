---
title: '[Trend] 2026-10-21: Claude Code, Supabase 기반 멀티 LLM 어댑터 추상화와 모듈형 런타임'
pubDatetime: '2026-10-21T00:00:00Z'
description: 2026-10-21 수집된 thomaspryor/Broadwayscore, Duncan-Haywood/oss-monorepo, oneiron-dev/oneiron 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- supabase
- openai
- anthropic
draft: false
---

2026-10-21 수집된 오픈소스 저장소들에서는 Claude Code, Supabase, OpenAI SDK, Anthropic SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 멀티 모델 에이전트 오케스트레이션 및 컨텍스트 규율 | `thomaspryor/Broadwayscore`, `oneiron-dev/oneiron`, `rodrigue11111/minebackfill` | 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `Duncan-Haywood/oss-monorepo`, `mastermindx-market-intelligence/macro`, `eLCerto/klimabot` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, Ray 기반 분산 오케스트레이션 및 학습·추론 엔진 계층화 |

---

## 2. 멀티 모델 에이전트 오케스트레이션 및 컨텍스트 규율

### 2.1 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`thomaspryor/Broadwayscore`)

- **출처**: [`thomaspryor/Broadwayscore`](https://github.com/thomaspryor/Broadwayscore) · **핵심 스택**: `Claude Code`, `Supabase`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.github/workflows/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `thomaspryor/Broadwayscore` 저장소는 Claude Code, Supabase, OpenAI SDK 스택 위에서 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`GitHub Actions Workflow Reference`, `Failure Notifications`, `Broadway Scorecard Project Context`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `thomaspryor/Broadwayscore`(TO-BE)에서는 `.github/workflows/CLAUDE.md`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.2 Rust 기반 `src/loro.rs` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`oneiron-dev/oneiron`)

- **출처**: [`oneiron-dev/oneiron`](https://github.com/oneiron-dev/oneiron) · **핵심 스택**: `Rust`, `Claude Code`, `LangGraph`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `crates/loro/vendor/loro-internal-1.16.2/CLAUDE.md` 발췌본을 기반으로 확인되는 `oneiron-dev/oneiron` 저장소는 Rust, Claude Code, LangGraph 스택 위에서 Rust 기반 `src/loro.rs` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/loro.rs`, `src/encoding.rs`, `src/encoding`)를 분리해 구성하며 문서 내 주요 섹션(`Oneiron — agent instructions`, `Consumer boundary — the rule that keeps this repo generic`, `loro-internal Guidelines`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `oneiron-dev/oneiron`(TO-BE)에서는 `CLAUDE.md`, `crates/loro/vendor/loro-internal-1.16.2/CLAUDE.md`, `src/loro.rs` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.3 FastAPI 기반 `valeur_invalide_handler` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`rodrigue11111/minebackfill`)

- **출처**: [`rodrigue11111/minebackfill`](https://github.com/rodrigue11111/minebackfill) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `rodrigue11111/minebackfill` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `valeur_invalide_handler` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/MAINTENANCE.md`, `docs/HISTORIQUE_EXTENSIBILITE.md`, `backend/app/tests/excel_twin`)를 분리해 구성하며 핵심 심볼(`valeur_invalide_handler`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Instructions pour l'IA mainteneuse (Claude Code)`, `À lire avant toute modification (dans cet ordre)`, `Règles absolues`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `rodrigue11111/minebackfill`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `valeur_invalide_handler` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Claude Code 기반 `make you` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`Duncan-Haywood/oss-monorepo`)

- **출처**: [`Duncan-Haywood/oss-monorepo`](https://github.com/Duncan-Haywood/oss-monorepo) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `platform/business-template/template/CLAUDE.md` 발췌본을 기반으로 확인되는 `Duncan-Haywood/oss-monorepo` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `make you` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`make you`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `Duncan-Haywood/oss-monorepo`(TO-BE)에서는 `CLAUDE.md`, `platform/business-template/template/CLAUDE.md`, `make you` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `api/ask` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`mastermindx-market-intelligence/macro`)

- **출처**: [`mastermindx-market-intelligence/macro`](https://github.com/mastermindx-market-intelligence/macro) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Supabase`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `app/main.py` 발췌본을 기반으로 확인되는 `mastermindx-market-intelligence/macro` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `api/ask` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/ask`, `api/ask/stream`)를 분리해 구성하며 문서 내 주요 섹션(`Macro Dashboard — agent instructions`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `mastermindx-market-intelligence/macro`(TO-BE)에서는 `CLAUDE.md`, `app/main.py`, `api/ask` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.3 Python 기반 `log` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리 (`eLCerto/klimabot`)

- **출처**: [`eLCerto/klimabot`](https://github.com/eLCerto/klimabot) · **핵심 스택**: `Python`, `Claude Code`, `Docker`, `Flask`, `PyTorch` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `eLCerto/klimabot` 저장소는 Python, Claude Code, Docker 스택 위에서 Python 기반 `log` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`log`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make build`, `make web`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 언어모델의 강화학습(RL)이나 고속 추론 서버에서 롤아웃 생성, 보상 계산, 가중치 동기화를 단일 스크립트로 묶으면 GPU 유휴 시간과 체크포인트 병목이 심각해집니다. 반면 `eLCerto/klimabot`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `make build` 등 명시적 아티팩트를 기준으로 오케스트레이션 코어, 추론 엔진(SGLang/vLLM), 학습 백엔드(Megatron), 분산 체크포인트 서비스를 계층별로 분리하고 게이트웨이 어댑터로 실험 프로토콜을 표준화합니다. 다만 다중 노드 클러스터와 GPU 메모리 토폴로지에 민감하므로 단위 컴포넌트 모킹 테스트와 실제 분산 환경의 가중치 변환 회귀 테스트를 이원화해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `thomaspryor/Broadwayscore`의 `.github/workflows/CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Duncan-Haywood/oss-monorepo`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `oneiron-dev/oneiron`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-10-21 수집 시점의 공개 저장소 `.github/workflows/CLAUDE.md`, `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
