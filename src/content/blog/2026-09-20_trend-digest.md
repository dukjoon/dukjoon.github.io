---
title: '[Trend] 2026-09-20: FastAPI, Python 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-09-20T00:00:00Z'
description: 2026-09-20 수집된 SignalBoost/signalboost-live, deepaihealth/expert-work, analistasistemas-bit/gtinmktplace 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- fastapi
- python
- claude-md
- supabase
draft: false
---

2026-09-20 수집된 오픈소스 저장소들에서는 FastAPI, Python, Claude Code, Supabase 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `SignalBoost/signalboost-live`, `deepaihealth/expert-work`, `analistasistemas-bit/gtinmktplace`, `ksarma/romp` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임 | `jreinach-alt/hakuX`, `zuaf-mc-movic/engineering-metrics-dashboard` | 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 FastAPI 기반 `EmbeddingRequest` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`SignalBoost/signalboost-live`)

- **출처**: [`SignalBoost/signalboost-live`](https://github.com/SignalBoost/signalboost-live) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Supabase`, `Stripe`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `runpod/serverless-embedding/app.py` 발췌본을 기반으로 확인되는 `SignalBoost/signalboost-live` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `EmbeddingRequest` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/HANDOFF-2026-08-13.md`, `docs/HANDOFF-COS-ACTIVE-LEARNING-2026-08-13.md`, `docs/portables/self-healing-monitoring-current-`)를 분리해 구성하며 핵심 심볼(`EmbeddingRequest`, `ping`, `embeddings`)을 중심으로 실행 흐름을 정의하고 저장소 발췌본(`CLAUDE.md`, `runpod/serverless-embedding/app.py`)을 통해 컴포넌트 책임과 실행 구성을 정의합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `SignalBoost/signalboost-live`(TO-BE)에서는 `CLAUDE.md`, `runpod/serverless-embedding/app.py`, `EmbeddingRequest` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `_amain` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`deepaihealth/expert-work`)

- **출처**: [`deepaihealth/expert-work`](https://github.com/deepaihealth/expert-work) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `uv` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `services/audit-backup-worker/src/audit_backup_worker/main.py` 발췌본을 기반으로 확인되는 `deepaihealth/expert-work` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `_amain` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`_amain`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`uv run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `deepaihealth/expert-work`(TO-BE)에서는 `CLAUDE.md`, `services/audit-backup-worker/src/audit_backup_worker/main.py`, `uv run` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.3 Claude Code 기반 `scripts/maestri-fase.sh` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`analistasistemas-bit/gtinmktplace`)

- **출처**: [`analistasistemas-bit/gtinmktplace`](https://github.com/analistasistemas-bit/gtinmktplace) · **핵심 스택**: `Claude Code`, `Supabase`, `OpenAI SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `maestri/roles/02b0ae9d-2cc7-49b6-b596-db6d55313677/CLAUDE.md`, `maestri/roles/1701a316-d674-4f25-8de3-04acf172f2f7/CLAUDE.md` 발췌본을 기반으로 확인되는 `analistasistemas-bit/gtinmktplace` 저장소는 Claude Code, Supabase, OpenAI SDK 스택 위에서 Claude Code 기반 `scripts/maestri-fase.sh` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/maestri-fase.sh`)를 분리해 구성하며 저장소 발췌본(`maestri/roles/02b0ae9d-2cc7-49b6-b596-db6d55313677/CLAUDE.md`, `maestri/roles/1701a316-d674-4f25-8de3-04acf172f2f7/CLAUDE.md`)을 통해 컴포넌트 책임과 실행 구성을 정의합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `analistasistemas-bit/gtinmktplace`(TO-BE)에서는 `maestri/roles/02b0ae9d-2cc7-49b6-b596-db6d55313677/CLAUDE.md`, `maestri/roles/1701a316-d674-4f25-8de3-04acf172f2f7/CLAUDE.md`, `scripts/maestri-fase.sh` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.4 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`ksarma/romp`)

- **출처**: [`ksarma/romp`](https://github.com/ksarma/romp) · **핵심 스택**: `Python`, `Claude Code`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `tests/test_kernel_installable_app.py` 발췌본을 기반으로 확인되는 `ksarma/romp` 저장소는 Python, Claude Code, Anthropic SDK 스택 위에서 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`romp — repo instructions`, `Philosophy`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `ksarma/romp`(TO-BE)에서는 `CLAUDE.md`, `tests/test_kernel_installable_app.py` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임

### 3.1 Python 기반 `DBusDescription` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`jreinach-alt/hakuX`)

- **출처**: [`jreinach-alt/hakuX`](https://github.com/jreinach-alt/hakuX) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docs/sphinx/dbusdomain.py` 발췌본을 기반으로 확인되는 `jreinach-alt/hakuX` 저장소는 Python, Claude Code 스택 위에서 Python 기반 `DBusDescription` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 핵심 심볼(`DBusDescription`, `for`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`D-Bus sphinx domain extension`, `Copyright (C) 2021, Red Hat Inc`, `SPDX-License-Identifier: LGPL-2.1-or-later`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `jreinach-alt/hakuX`(TO-BE)에서는 `CLAUDE.md`, `docs/sphinx/dbusdomain.py`, `DBusDescription` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.2 Python 기반 `inject_template_globals` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`zuaf-mc-movic/engineering-metrics-dashboard`)

- **출처**: [`zuaf-mc-movic/engineering-metrics-dashboard`](https://github.com/zuaf-mc-movic/engineering-metrics-dashboard) · **핵심 스택**: `Python`, `Claude Code`, `Flask` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/dashboard/app.py` 발췌본을 기반으로 확인되는 `zuaf-mc-movic/engineering-metrics-dashboard` 저장소는 Python, Claude Code, Flask 스택 위에서 Python 기반 `inject_template_globals` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 핵심 심볼(`inject_template_globals`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Development Commands`, `Setup`, `Create virtual environment`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `zuaf-mc-movic/engineering-metrics-dashboard`(TO-BE)에서는 `CLAUDE.md`, `src/dashboard/app.py`, `inject_template_globals` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `SignalBoost/signalboost-live`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `deepaihealth/expert-work`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `analistasistemas-bit/gtinmktplace`의 `maestri/roles/02b0ae9d-2cc7-49b6-b596-db6d55313677/CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-09-20 수집 시점의 공개 저장소 `CLAUDE.md`, `maestri/roles/02b0ae9d-2cc7-49b6-b596-db6d55313677/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
