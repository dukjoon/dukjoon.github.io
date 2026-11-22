---
title: '[Trend] 2026-07-31: Python, Claude Code 기반 DDD 기반 API·워커 분리와 모듈형 런타임'
pubDatetime: '2026-07-31T00:00:00Z'
description: 2026-07-31 수집된 ClickHouse/ClickHouse, Aeovy/ragflow_dev, bcgov/ai-adoption-document-intelligence 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- stripe
draft: false
---

2026-07-31 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진 | `ClickHouse/ClickHouse`, `bcgov/ai-adoption-document-intelligence`, `FoodBreakPedro/GigaClaw` | DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `Aeovy/ragflow_dev`, `biriyani0141/turnover-detector`, `m2lines/Samudra` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조, Ray 기반 분산 오케스트레이션 및 학습·추론 엔진 계층화 |

---

## 2. 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진

### 2.1 Python 기반 `_get_raw_body` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`ClickHouse/ClickHouse`)

- **출처**: [`ClickHouse/ClickHouse`](https://github.com/ClickHouse/ClickHouse) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `Pydantic`, `LangGraph` · **적용 판단**: `Trial`
- **기술 개요**: `.claude/CLAUDE.md`, `ci/praktika/infrastructure/native/lambda_slack_app.py` 발췌본을 기반으로 확인되는 `ClickHouse/ClickHouse` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `_get_raw_body` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`_get_raw_body`, `verify_slack_request`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`API Gateway may change header casing`, `Replay protection: reject if older than 5 minutes`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `ClickHouse/ClickHouse`(TO-BE)에서는 `.claude/CLAUDE.md`, `ci/praktika/infrastructure/native/lambda_slack_app.py`, `_get_raw_body` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.2 Python 기반 `denoise` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`bcgov/ai-adoption-document-intelligence`)

- **출처**: [`bcgov/ai-adoption-document-intelligence`](https://github.com/bcgov/ai-adoption-document-intelligence) · **핵심 스택**: `Python`, `Claude Code`, `Prisma` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/image-service/main.py` 발췌본을 기반으로 확인되는 `bcgov/ai-adoption-document-intelligence` 저장소는 Python, Claude Code, Prisma 스택 위에서 Python 기반 `denoise` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/backend-services`, `apps/temporal/src`)를 분리해 구성하며 핵심 심볼(`denoise`, `deskew`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make assumptions`, `npm run db:generate`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `bcgov/ai-adoption-document-intelligence`(TO-BE)에서는 `CLAUDE.md`, `apps/image-service/main.py`, `make assumptions` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 Claude Code 기반 `api/docs` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`FoodBreakPedro/GigaClaw`)

- **출처**: [`FoodBreakPedro/GigaClaw`](https://github.com/FoodBreakPedro/GigaClaw) · **핵심 스택**: `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `ProjectTemplate/CLAUDE.md` 발췌본을 기반으로 확인되는 `FoodBreakPedro/GigaClaw` 저장소는 Claude Code, Gemini SDK 스택 위에서 Claude Code 기반 `api/docs` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/docs`)를 분리해 구성하며 문서 내 주요 섹션(`GigaClaw — Claude guide`, `Run`, `→ http://localhost:5230`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `FoodBreakPedro/GigaClaw`(TO-BE)에서는 `CLAUDE.md`, `ProjectTemplate/CLAUDE.md`, `api/docs` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`Aeovy/ragflow_dev`)

- **출처**: [`Aeovy/ragflow_dev`](https://github.com/Aeovy/ragflow_dev) · **핵심 스택**: `FastAPI`, `React`, `TypeScript`, `Python`, `Claude Code`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `agent/sandbox/executor_manager/main.py` 발췌본을 기반으로 확인되는 `Aeovy/ragflow_dev` 저장소는 FastAPI, React, TypeScript 스택 위에서 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`RAGFlow Instructions`, `Core Stance`, `Current stack`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `Aeovy/ragflow_dev`(TO-BE)에서는 `CLAUDE.md`, `agent/sandbox/executor_manager/main.py` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 Next.js 기반 `is_jp_business_day` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`biriyani0141/turnover-detector`)

- **출처**: [`biriyani0141/turnover-detector`](https://github.com/biriyani0141/turnover-detector) · **핵심 스택**: `Next.js`, `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `biriyani0141/turnover-detector` 저장소는 Next.js, Python, Claude Code 스택 위에서 Next.js 기반 `is_jp_business_day` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/decision-log.md`, `docs/architecture.md`, `docs/state.md`)를 분리해 구성하며 핵심 심볼(`is_jp_business_day`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`CLAUDE.md — turnover-detector`, `プロジェクト概要`, `役割分担`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `biriyani0141/turnover-detector`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `is_jp_business_day` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

### 3.3 Python 기반 `InferenceEvaluatorAggregator` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리 (`m2lines/Samudra`)

- **출처**: [`m2lines/Samudra`](https://github.com/m2lines/Samudra) · **핵심 스택**: `Python`, `Claude Code`, `PyTorch` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/samudra/aggregator/inference/main.py` 발췌본을 기반으로 확인되는 `m2lines/Samudra` 저장소는 Python, Claude Code, PyTorch 스택 위에서 Python 기반 `InferenceEvaluatorAggregator` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`InferenceEvaluatorAggregator`, `__init__`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`SPDX-FileCopyrightText: 2024 Allen Institute for Artificial `, `SPDX-FileCopyrightText: 2026 Samudra Authors`, `SPDX-License-Identifier: Apache-2.0`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 언어모델의 강화학습(RL)이나 고속 추론 서버에서 롤아웃 생성, 보상 계산, 가중치 동기화를 단일 스크립트로 묶으면 GPU 유휴 시간과 체크포인트 병목이 심각해집니다. 반면 `m2lines/Samudra`(TO-BE)에서는 `CLAUDE.md`, `src/samudra/aggregator/inference/main.py`, `InferenceEvaluatorAggregator` 등 명시적 아티팩트를 기준으로 오케스트레이션 코어, 추론 엔진(SGLang/vLLM), 학습 백엔드(Megatron), 분산 체크포인트 서비스를 계층별로 분리하고 게이트웨이 어댑터로 실험 프로토콜을 표준화합니다. 다만 다중 노드 클러스터와 GPU 메모리 토폴로지에 민감하므로 단위 컴포넌트 모킹 테스트와 실제 분산 환경의 가중치 변환 회귀 테스트를 이원화해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `ClickHouse/ClickHouse`의 `.claude/CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Aeovy/ragflow_dev`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `bcgov/ai-adoption-document-intelligence`의 `CLAUDE.md` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-31 수집 시점의 공개 저장소 `.claude/CLAUDE.md`, `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
