---
title: '[Trend] 2026-08-04: Python, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-08-04T00:00:00Z'
description: 2026-08-04 수집된 OTHROPIC/open_deep_research, akto-api-security/akto, deepxfinance/deepx-sdk-py 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- mcp
- claude-md
- langgraph
draft: false
---

2026-08-04 수집된 오픈소스 저장소들에서는 Python, MCP, Claude Code, LangGraph 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `OTHROPIC/open_deep_research`, `deepxfinance/deepx-sdk-py`, `pouriaetab/quantdesk`, `billcarroll/davinci-resolve-mcp` | MCP 도구 스키마 분리 및 런타임 세션 격리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `akto-api-security/akto`, `trimcrae/Rare-cancers` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 `src/open_deep_research` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`OTHROPIC/open_deep_research`)

- **출처**: [`OTHROPIC/open_deep_research`](https://github.com/OTHROPIC/open_deep_research) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `LangGraph`, `uv` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/legacy/CLAUDE.md` 발췌본을 기반으로 확인되는 `OTHROPIC/open_deep_research` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `src/open_deep_research` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/open_deep_research`)를 분리해 구성하며 문서 내 주요 섹션(`Open Deep Research Repository Overview`, `Project Description`, `Repository Structure`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `OTHROPIC/open_deep_research`(TO-BE)에서는 `CLAUDE.md`, `src/legacy/CLAUDE.md`, `src/open_deep_research` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`deepxfinance/deepx-sdk-py`)

- **출처**: [`deepxfinance/deepx-sdk-py`](https://github.com/deepxfinance/deepx-sdk-py) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `bot/main.py` 발췌본을 기반으로 확인되는 `deepxfinance/deepx-sdk-py` 저장소는 Python, Claude Code 스택 위에서 Python 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`deepx-sdk-py — development notes`, `Layout`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `deepxfinance/deepx-sdk-py`(TO-BE)에서는 `CLAUDE.md`, `bot/main.py` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.3 FastAPI 기반 `log_re` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`pouriaetab/quantdesk`)

- **출처**: [`pouriaetab/quantdesk`](https://github.com/pouriaetab/quantdesk) · **핵심 스택**: `FastAPI`, `React`, `Python`, `Claude Code`, `pnpm`, `Tailwind CSS` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `pouriaetab/quantdesk` 저장소는 FastAPI, React, Python 스택 위에서 FastAPI 기반 `log_re` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/v1`, `src/components`)를 분리해 구성하며 핵심 심볼(`log_re`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`QuantDesk`, `Tech Stack`, `Architecture`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `pouriaetab/quantdesk`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `log_re` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.4 Python 기반 `scripts/agent-rules/generate.mjs` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`billcarroll/davinci-resolve-mcp`)

- **출처**: [`billcarroll/davinci-resolve-mcp`](https://github.com/billcarroll/davinci-resolve-mcp) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `Cursor Rules` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `billcarroll/davinci-resolve-mcp` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `scripts/agent-rules/generate.mjs` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/agent-rules/generate.mjs`, `docs/SKILL.md`, `docs/kernels`)를 분리해 구성하며 문서 내 주요 섹션(`DaVinci Resolve MCP — agent rules`, `Domain routing`, `Claude Code Instructions`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `billcarroll/davinci-resolve-mcp`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md`, `scripts/agent-rules/generate.mjs` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 FastAPI 기반 `_startup_self_check_enabled` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`akto-api-security/akto`)

- **출처**: [`akto-api-security/akto`](https://github.com/akto-api-security/akto) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Redis`, `Docker`, `Kubernetes` · **적용 판단**: `Trial`
- **기술 개요**: `apps/agent-guard/python-service/worker-py/src/app.py`, `apps/threat-detection/CLAUDE.md` 발췌본을 기반으로 확인되는 `akto-api-security/akto` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `_startup_self_check_enabled` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 핵심 심볼(`_startup_self_check_enabled`, `ScanRequest`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Optional separate system prompt. When given, the intent pref`, `only to build/retrieve a cached per-agent capability profile`, `threat-detection`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `akto-api-security/akto`(TO-BE)에서는 `apps/agent-guard/python-service/worker-py/src/app.py`, `apps/threat-detection/CLAUDE.md`, `_startup_self_check_enabled` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 Python 기반 `_config_lines` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`trimcrae/Rare-cancers`)

- **출처**: [`trimcrae/Rare-cancers`](https://github.com/trimcrae/Rare-cancers) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `research/modalities/tests/test_lanes_run_from_main.py` 발췌본을 기반으로 확인되는 `trimcrae/Rare-cancers` 저장소는 Python, Claude Code 스택 위에서 Python 기반 `_config_lines` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 핵심 심볼(`_config_lines`)을 중심으로 실행 흐름을 정의하고 저장소 발췌본(`CLAUDE.md`, `research/modalities/tests/test_lanes_run_from_main.py`)을 통해 컴포넌트 책임과 실행 구성을 정의합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `trimcrae/Rare-cancers`(TO-BE)에서는 `CLAUDE.md`, `research/modalities/tests/test_lanes_run_from_main.py`, `_config_lines` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `OTHROPIC/open_deep_research`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `akto-api-security/akto`의 `apps/agent-guard/python-service/worker-py/src/app.py` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `deepxfinance/deepx-sdk-py`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-08-04 수집 시점의 공개 저장소 `CLAUDE.md`, `apps/agent-guard/python-service/worker-py/src/app.py` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
