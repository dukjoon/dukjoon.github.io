---
title: '[Trend] 2026-09-04: FastAPI, Python 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-09-04T00:00:00Z'
description: 2026-09-04 수집된 Actvee/chann-crm-ai, iberi22/gastronomic-open-standard-GOS, simokitafresh/multi-agent-shogun 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- fastapi
- python
- claude-md
- redis
draft: false
---

2026-09-04 수집된 오픈소스 저장소들에서는 FastAPI, Python, Claude Code, Redis 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `Actvee/chann-crm-ai`, `iberi22/gastronomic-open-standard-GOS`, `simokitafresh/multi-agent-shogun`, `bhardwajRahul/nanobot` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, MCP 도구 스키마 분리 및 런타임 세션 격리 |
| 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화 | `wujun728/jun_api_service` | 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 FastAPI 기반 `health` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`Actvee/chann-crm-ai`)

- **출처**: [`Actvee/chann-crm-ai`](https://github.com/Actvee/chann-crm-ai) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Redis`, `SQLAlchemy` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `application/chann_app/main.py` 발췌본을 기반으로 확인되는 `Actvee/chann-crm-ai` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `health` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/SESSION_HANDOFF.md`, `docs/AI_HANDOFF_START_PROMPT.md`, `docs/PLAN_3OA.md`)를 분리해 구성하며 핵심 심볼(`health`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Chann CRM AI — Instructions for Claude Code / Coding Agent`, `-1. อ่านสิ่งนี้ก่อน — สภาพจริง ณ 3 ก.ย. 2569 (ส่วนนี้ทับทุกอ`, `เอกสารที่ต้องอ่านเป็นอันดับแรก (ตามลำดับ)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `Actvee/chann-crm-ai`(TO-BE)에서는 `CLAUDE.md`, `application/chann_app/main.py`, `health` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `scripts/build_graph` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`iberi22/gastronomic-open-standard-GOS`)

- **출처**: [`iberi22/gastronomic-open-standard-GOS`](https://github.com/iberi22/gastronomic-open-standard-GOS) · **핵심 스택**: `Python`, `Claude Code`, `Cursor Rules`, `Gemini SDK`, `Tailwind CSS` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `iberi22/gastronomic-open-standard-GOS` 저장소는 Python, Claude Code, Cursor Rules 스택 위에서 Python 기반 `scripts/build_graph` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/build_graph`)를 분리해 구성하며 문서 내 주요 섹션(`AI Git-Core Protocol Rules`, `FORBIDDEN ACTIONS (HARD RULES)`, `Task/State Management`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `iberi22/gastronomic-open-standard-GOS`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md`, `scripts/build_graph` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`simokitafresh/multi-agent-shogun`)

- **출처**: [`simokitafresh/multi-agent-shogun`](https://github.com/simokitafresh/multi-agent-shogun) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `scripts/gates/gate_report_autofix_main.py` 발췌본을 기반으로 확인되는 `simokitafresh/multi-agent-shogun` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`multi-agent-shogun System Configuration`, `═══ Session Start (自律実行必須) ═══`, `このファイル読込=セッション開始。ユーザー入力を待たず即座に以下を実行せよ`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `simokitafresh/multi-agent-shogun`(TO-BE)에서는 `CLAUDE.md`, `scripts/gates/gate_report_autofix_main.py` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.4 Python 기반 `_make_channel` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`bhardwajRahul/nanobot`)

- **출처**: [`bhardwajRahul/nanobot`](https://github.com/bhardwajRahul/nanobot) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `nanobot/channels/feishu/tests/test_feishu_domain.py` 발췌본을 기반으로 확인되는 `bhardwajRahul/nanobot` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `_make_channel` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`_make_channel`, `TestFeishuConfigDomain`, `test_domain_default_is_feishu`)을 중심으로 실행 흐름을 정의하고 저장소 발췌본(`CLAUDE.md`, `nanobot/channels/feishu/tests/test_feishu_domain.py`)을 통해 컴포넌트 책임과 실행 구성을 정의합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `bhardwajRahul/nanobot`(TO-BE)에서는 `CLAUDE.md`, `nanobot/channels/feishu/tests/test_feishu_domain.py`, `_make_channel` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

## 3. 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화

### 3.1 Python 기반 `parse_args` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`wujun728/jun_api_service`)

- **출처**: [`wujun728/jun_api_service`](https://github.com/wujun728/jun_api_service) · **핵심 스택**: `Python`, `Claude Code`, `Anthropic SDK` · **적용 판단**: `Assess`
- **기술 개요**: `CLAUDE.md`, `long-running-agent/main.py` 발췌본을 기반으로 확인되는 `wujun728/jun_api_service` 저장소는 Python, Claude Code, Anthropic SDK 스택 위에서 Python 기반 `parse_args` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 핵심 심볼(`parse_args`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`仓库概述`, `本仓库目录与职责`, `Windows 控制台 UTF-8 支持`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `wujun728/jun_api_service`(TO-BE)에서는 `CLAUDE.md`, `long-running-agent/main.py`, `parse_args` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `Actvee/chann-crm-ai`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `iberi22/gastronomic-open-standard-GOS`의 `.cursorrules` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `simokitafresh/multi-agent-shogun`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-09-04 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
