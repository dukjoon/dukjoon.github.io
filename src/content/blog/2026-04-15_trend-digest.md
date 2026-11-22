---
title: "[Trend] 2026-04-15: 계층형 AGENTS.md, 컨테이너 격리 및 CDK 드리프트 체크리스트"
pubDatetime: 2026-04-15T00:00:00Z
description: "MCP 연합 게이트웨이의 하위 AGENTS.md 분리, Breeze 컨테이너 강제, Alembic 마이그레이션 규율, AWS CDK 드리프트 방지 및 Keychain 시크릿 로더를 정리합니다."
category: trend
tags:
  - trend
  - mcp
  - airflow
  - fastapi
  - aws-cdk
  - devops
draft: false
---

2026-04-15 수집 데이터에서는 저장소 규모가 커질수록 에이전트 지침을 루트 파일 하나에 몰아넣지 않고 하위 디렉터리별 `AGENTS.md`로 분할하거나, 호스트 직접 실행을 막고 전용 컨테이너(`breeze`)만 허용하는 개발 환경 표준화 패턴이 두드러졌습니다. 또한 멀티테넌트 FastAPI 백엔드, `ARCHITECTURE.org` 기반 드리프트 체크리스트를 결합한 AWS CDK 인프라, 그리고 macOS Keychain 기반 시크릿 단일 진실 원천(SSOT) 관리 사례도 함께 확인되었습니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 연합 게이트웨이와 컨테이너 격리 | `forterro/mcp-context-forge`, `boost-entropy-python/airflow` | 하위 디렉터리 `AGENTS.md` 분업화 및 호스트 실행 금지·Breeze 컨테이너 강제 |
| 멀티테넌트 백엔드와 아키텍처 드리프트 제어 | `ProjectTech4DevAI/kaapi-backend`, `iganza/steam-pulse` | Alembic 순차 리비전 규율 및 `ARCHITECTURE.org` 시퀀스·드리프트 사전 검증 |
| 경량 크론 모니터링과 키체인 시크릿 | `faustost/pageChangeApp`, `Ahjan108/phoenix_omega_v4.8` | GitHub Actions JSON 스냅샷 diff와 `--dry-run` 및 Keychain 기반 환경변수 적재 |

---

## 2. 에이전트 게이트웨이 및 컨테이너 기반 개발 워크플로우

### 2.1 하위 AGENTS.md 계층화와 MCP/A2A 연합 게이트웨이 (`forterro/mcp-context-forge`)

- **출처**: [`forterro/mcp-context-forge`](https://github.com/forterro/mcp-context-forge) · **핵심 스택**: `Python`, `FastAPI`, `HTMX`, `Rust MCP Runtime`, `Helm`, `JSON-RPC/SSE/WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: MCP, A2A, REST/gRPC API를 중앙에서 등록·연합(federation)하고 JWT/RBAC·속도 제한·가상 서버·다중 트랜스포트(JSON-RPC, SSE, WebSocket)를 제공하는 FastAPI 및 HTMX Admin UI 기반 게이트웨이입니다. 루트 지침은 `tests/`, `plugins/`, `charts/`, `docs/`, `mcp-servers/`, `tools_rust/mcp_runtime/DEVELOPING.md`로 세부 지침을 위임하며, 최종 사용자 런타임용 `llms/` 문서와 코드 에이전트용 지침을 명확히 구분합니다.

**실무 적용 해설**: 다양한 프로토콜(MCP, A2A, REST)과 언어(Python, Rust, Helm)가 공존하는 게이트웨이 저장소에서 단일 루트 문서에 모든 빌드·테스트 규칙을 적으면(AS-IS) 컨텍스트가 비대해지고 코드 에이전트가 최종 사용자용 설명서까지 규칙으로 오인하는 혼선이 생깁니다. 영역별 하위 `AGENTS.md`로 지침을 분산하고 `llms/` 디렉터리의 용도를 명시적으로 분리(TO-BE)하면 작업 도메인에 맞는 최소 컨텍스트만 정확히 로드할 수 있습니다. 다만 진입점인 `mcpgateway/main.py`가 게이트웨이 수명주기와 다수 라우터를 함께 관장하므로, 플러그인 추가 시 기동·종료 훅의 순서 의존성을 통합 테스트로 관리해야 합니다.

---

### 2.2 호스트 실행 금지와 Breeze 컨테이너 전용 테스트 규율 (`boost-entropy-python/airflow`)

- **출처**: [`boost-entropy-python/airflow`](https://github.com/boost-entropy-python/airflow) · **핵심 스택**: `Python`, `uv`, `FastAPI`, `AsyncExitStack`, `Breeze`, `prek` · **적용 판단**: `Trial`
- **기술 개요**: `airflow-core/src/airflow/api_fastapi/app.py`를 통해 FastAPI 기반 코어 API와 `AsyncExitStack` 수명주기를 운영하는 대형 데이터 오케스트레이션 저장소입니다. `CLAUDE.md`에서는 `uv tool install prek`로 커밋 훅을 강제하고, 호스트 머신에서 직접 `pytest`, `python`, `airflow`를 실행하는 행위를 전면 금지하며 오직 `breeze` 컨테이너 내부와 `dev/`(`/opt/airflow/dev/`) 마운트 경로만 사용하도록 규정합니다.

**실무 적용 해설**: 거대한 Python 프로젝트에서 개발자나 에이전트가 호스트 로컬 가상환경으로 테스트를 돌리면(AS-IS) OS 라이브러리, 데이터베이스 드라이버, 시스템 패키지 차이로 인해 CI에서만 실패하는 환경 드리프트가 반복됩니다. `uv run --project <PROJECT>`로 패키지 단위를 좁히되 실행 환경 자체를 `breeze` 컨테이너로 강제 고정(TO-BE)하면 로컬과 CI의 재현성을 일치시킬 수 있습니다. 컨테이너 기반 워크플로우는 초기 이미지 풀과 기동 지연이 동반되므로, `dev/` 마운트 경로와 단일 테스트 타겟팅(`TestClass::test_method -xvs`)을 병용해 반복 피드백 시간을 줄이는 운영 요령이 필요합니다.

---

## 3. 멀티테넌트 FastAPI 백엔드와 운영 자동화 파이프라인

### 3.1 계층형 AI 백엔드와 Alembic 리비전 규율 (`ProjectTech4DevAI/kaapi-backend`)

- **출처**: [`ProjectTech4DevAI/kaapi-backend`](https://github.com/ProjectTech4DevAI/kaapi-backend) · **핵심 스택**: `FastAPI`, `PostgreSQL`, `Alembic`, `uv`, `Docker`, `OpenAI API` · **적용 판단**: `Trial`
- **기술 개요**: OpenAI Assistants/Threads/Responses, 파인튜닝, 문서 변환 작업(`doc_transformation_job`), 모델 평가(`model_evaluation`), 조직·프로젝트 멀티테넌시(`organization`, `project`, `user_project`)를 라우터 단위로 구성한 FastAPI 백엔드입니다. `CLAUDE.md`에서는 `.env.test` 기반 테스트(`uv run bash scripts/tests-start.sh`)와 함께 Alembic 마이그레이션 생성 시 직전 리비전 ID에 1을 더한 `--rev-id`를 수동 지정하도록 규율합니다.

**실무 적용 해설**: 여러 기능이 동시에 개발되는 FastAPI + PostgreSQL 백엔드(AS-IS)에서는 Alembic의 기본 랜덤 해시 리비전 ID가 병합 시 브랜치 충돌을 일으키거나 순서 파악을 어렵게 만듭니다. 순차적 숫자 리비전(`--rev-id 040` 등) 규칙과 사전 커밋 훅(`uv run pre-commit run --all-files`), 테스트 전용 환경파일(`.env.test`)을 결합(TO-BE)하면 스키마 이력을 선형적으로 추적하고 테스트 DB 오염을 방지할 수 있습니다. 다만 순차 ID 방식은 병렬 PR이 동시에 마이그레이션을 추가할 때 번호 충돌을 유발하므로, 머지 직전 리비전 번호 재검증 단계를 PR 체크에 두는 것이 좋습니다.

---

### 3.2 ARCHITECTURE.org 드리프트 체크리스트와 CDK 스택 격리 (`iganza/steam-pulse`)

- **출처**: [`iganza/steam-pulse`](https://github.com/iganza/steam-pulse) · **핵심 스택**: `AWS CDK (Python)`, `OpenNext`, `ApplicationStage`, `MonitoringStack`, `Poetry` · **적용 판단**: `Trial`
- **기술 개요**: Steam 게임 리뷰 AI 분석 플랫폼으로, `infra/app.py`에서 `ApplicationStage`를 이용해 `SteamPulse-Staging`과 `SteamPulse-Production` 스택을 분리 배포하며 `OpenNext` 프론트엔드를 결합합니다. 특히 `CLAUDE.md`는 핸들러·서비스·큐·SNS 토픽을 수정하기 전 반드시 루트의 `ARCHITECTURE.org`를 읽고 각 흐름의 불변 조건(invariant)과 드리프트 체크리스트(drift checklist)를 검증하며, 신규 상호작용 추가 시 시퀀스 다이어그램을 먼저 작성하도록 요구합니다.

**실무 적용 해설**: 이벤트 기반 AWS 서버리스/CDK 시스템(AS-IS)에서는 코드 변경이 큐·SNS 토픽·모니터링 스택의 계약을 깨뜨려도 배포 후 장애로 이어지기 전까지 설계 불일치를 알아차리기 어렵습니다. 모든 컴포넌트 정의와 불변 조건을 `ARCHITECTURE.org`에 집약하고 코드 수정 전 드리프트 체크리스트 검증을 선행(TO-BE)하면 문서와 실제 CDK 인프라(`ApplicationStage`, `MonitoringStack`) 간의 괴리를 크게 줄일 수 있습니다. 또한 파이프라인 없이 직접 `cdk deploy 'SteamPulse-Staging-*'`로 스테이징 검증 후 프로덕션으로 승격하는 구조는 배포 속도가 빠른 반면, 실수로 프로덕션 타겟을 지정하지 않도록 CLI 래퍼 스크립트(`./scripts/deploy.sh --env`)의 안전장치가 중요합니다.

---

## 4. 경량 스케줄러 기반 모니터링 및 키체인 시크릿 관리

### 4.1 GitHub Actions 크론과 JSON 스냅샷 기반 페이지 변경 감시 (`faustost/pageChangeApp`)

- **출처**: [`faustost/pageChangeApp`](https://github.com/faustost/pageChangeApp) · **핵심 스택**: `Python`, `GitHub Actions`, `Telegram Bot API`, `JSON Storage` · **적용 판단**: `Trial`
- **기술 개요**: 별도 상주 서버 없이 GitHub Actions의 매시간 스케줄로 웹페이지를 수집해 HTML 파싱 및 변경분(diff)을 계산하고 텔레그램 봇으로 알림을 보내는 경량 모니터링 도구입니다. `src/config.py`, `src/monitor.py`, `src/notify.py`, `src/storage.py`로 책임을 분리했고 `data/pages.json`과 `snapshots.json`으로 상태를 저장하며, 알림 발송 없이 검증하는 `--dry-run` 모드를 기본 지원합니다.

**실무 적용 해설**: 단순 웹 변경 알림을 위해 별도 데이터베이스와 클라우드 인스턴스를 상시 띄우면(AS-IS) 유지 비용과 인프라 관리 부담이 과도해집니다. GitHub Actions 크론과 JSON 스냅샷 영속화, 그리고 로컬 검증용 `--dry-run` 플래그 조합(TO-BE)은 운영 비용 없이도 신뢰할 수 있는 주기적 감시 파이프라인을 제공합니다. 단, GitHub Actions 스케줄러는 트래픽 혼잡 시 실행 시각이 지연될 수 있고 JSON 스냅샷 커밋이 잦아질 경우 저장소 이력이 커지므로, 대상 페이지 수와 보관 주기에 맞춘 이력 정리 전략이 필요합니다.

---

### 4.2 macOS Keychain SSOT 로더와 퍼널 SQLite 영속화 (`Ahjan108/phoenix_omega_v4.8`)

- **출처**: [`Ahjan108/phoenix_omega_v4.8`](https://github.com/Ahjan108/phoenix_omega_v4.8) · **핵심 스택**: `Python`, `Flask`, `SQLite`, `APScheduler`, `macOS Keychain`, `Brevo/GHL` · **적용 판단**: `Assess`
- **기술 개요**: 다중 AI 및 마케팅 자동화 서비스(`DashScope`, `RunComfy`, `ElevenLabs`, `GHL`, `Brevo SMTP`)를 연동하는 운영 저장소입니다. `CLAUDE.md`는 추적 대상 통합 키 목록을 `scripts/ci/integration_env_registry.py`로 단일화해 macOS Keychain에서 일괄 로드(`load_integration_env_from_keychain.py`)하도록 규정하며, `funnel/burnout_reset/app.py`는 JSONL 파일 대신 SQLite와 APScheduler jobstore를 사용해 리드 상태와 5단계 이메일 시퀀스를 영속화합니다.

**실무 적용 해설**: 여러 외부 API 키를 `.env` 평문 파일에 복제해 관리하면(AS-IS) 리전 엔드포인트 혼동이나 키 유출, 환경 간 누락이 발생하기 쉽고, JSONL 로그에 리드 상태를 쌓으면 중복 발송이나 수신 거부(`is_unsubscribed`) 처리 시 동시성 오류가 납니다. 키 레지스트리 스크립트를 단일 진실 원천으로 삼아 Keychain에서 환경변수를 주입하고, 퍼널 상태를 SQLite 트랜잭션과 APScheduler jobstore로 통합(TO-BE)하면 보안성과 상태 정합성을 모두 높일 수 있습니다. 다만 macOS Keychain 기반 로더는 Linux CI/서버 환경에서 그대로 동작하지 않으므로 CI 환경용 시크릿 백엔드 분기 처리가 필수입니다.

---

## 5. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - 다중 언어·도메인 모노레포라면 루트 `CLAUDE.md`/`AGENTS.md`를 슬림하게 유지하고 서브시스템별 규칙을 하위 `AGENTS.md`로 분할했는지 점검합니다.
  - 로컬 테스트가 호스트 환경에 오염되지 않도록 `breeze` 같은 컨테이너 래퍼나 `.env.test` 격리 구성을 갖추었는지 확인합니다.
  - 분산 큐·SNS·인프라 스택을 함께 다루는 프로젝트에 불변 조건과 드리프트 체크리스트 문서(`ARCHITECTURE.org` 등)를 PR 리뷰 기준에 포함합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-04-15 수집 시점의 공개 저장소 `CLAUDE.md` 및 주요 코드 발췌본에 근거하며, 각 프로젝트의 실제 프로덕션 트래픽 규모나 배포 지연·비용 수치는 별도 검증이 필요합니다.
