---
title: "[Trend] 2026-02-08: AWS CDK GPU 큐 오케스트레이션과 매니페스트 CLI"
pubDatetime: 2026-02-08T00:00:00Z
description: "SQS·DynamoDB·Lambda 기반 GPU 작업 오케스트레이션, 분산 추론 타임아웃 제어, JSON 매니페스트 에이전트 CLI, 풀스택 모노레포 구조를 살핍니다."
category: trend
tags:
  - trend
  - aws-cdk
  - distributed-inference
  - pydantic-ai
  - monorepo
draft: false
---

AI 서비스가 프로토타입을 넘어 실제 GPU/CPU 작업 큐와 분산 추론 노드를 제어하기 시작하면서, 인프라 오케스트레이션(AWS CDK)과 에이전트 실행 설정(Manifest/Timeout)을 코드로 명세하는 흐름이 두드러집니다. 이번 일자에서는 인프라·분산 런타임 제어 패턴과 에이전트·풀스택 모노레포 모듈화 사례를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| GPU 큐 오케스트레이션 및 분산 런타임 | `CurvatureX/short-drama`, `celesrenata/exo` | ECS(CI/CD)와 SQS·유휴 람다 CDK 분리, 다중 노드 러너 타임아웃·재시도 환경변수 제어 |
| 매니페스트 CLI 및 풀스택 모듈 구조 | `zby/llm-do`, `itskai-dev/openclaw` (`robjsp/openclaw`), `looovely/lobe-chat` | `project.json` 매니페스트 기반 `pydantic_ai` CLI, `src/` 기능별 배선 및 `packages/@lobechat/*` 계층화 |

---

## 2. GPU 큐 오케스트레이션 및 분산 런타임

### 2.1 ECS 애플리케이션 배포와 CDK 상태·유휴 자원 스택 분리 (`CurvatureX/short-drama`)

- **출처**: [`CurvatureX/short-drama`](https://github.com/CurvatureX/short-drama) · **핵심 스택**: `Next.js`, `FastAPI`, `AWS CDK (Python)`, `SQS/DynamoDB`, `Supabase/S3` · **적용 판단**: `Trial`
- **기술 개요**: Next.js 프론트엔드(`3000`)와 FastAPI 마이크로서비스(Studio `8200`, Orchestrator `8080`, Storyboard `8100`)로 AI 숏폼 영상을 생성하며, `backend/infra/app.py`의 AWS CDK로 `gpu_tasks_queue`/`cpu_tasks_queue`(DLQ 포함), `task_store`(DynamoDB), 자동 종료 Lambda 및 30분 유휴 CloudWatch 알람을 관리하는 구조입니다.

**실무 적용 해설**: GPU 기반 이미지·영상 생성 작업을 웹 API 서버가 동기 처리하거나 단일 인프라 스크립트에 앱 배포와 큐 스택을 엮으면(AS-IS) 작업 적체 시 API가 멈추고 유휴 GPU 비용이 누적됩니다. `short-drama`처럼 애플리케이션 ECS 서비스는 GitHub Actions로 빠르게 배포하고, SQS(DLQ)·DynamoDB·30분 유휴 알람 기반 자동 종료 Lambda만 AWS CDK 스택으로 분리(TO-BE)하면 배포 속도와 GPU 비용 통제를 함께 얻을 수 있습니다. 다만 웹 API(Supabase PostgreSQL)와 작업 상태(DynamoDB `task_store`) 간 이원화된 저장소의 상태 동기화 실패 시나리오를 DLQ 재처리 로직으로 보완해야 합니다.

### 2.2 다중 노드 분산 추론의 타임아웃·순수 함수 규약 (`celesrenata/exo`)

- **출처**: [`celesrenata/exo`](https://github.com/celesrenata/exo) · **핵심 스택**: `Python (anyio, multiprocessing)`, `Distributed Inference` · **적용 판단**: `Trial`
- **기술 개요**: 분산 추론 시스템의 엔트리포인트 `src/exo/main.py`에서 다중 노드 경쟁 상태(Race Condition)를 막기 위해 종료(`60.0s`), 헬스체크(`30.0s`), 시작(`30.0s`), 정리(`15.0s`), 최대 재시도(`3`) 환경변수를 명시적으로 노출하고, `.cursorrules`에서 참조 투명성과 순수 함수 기반 상태 격리를 요구한 사례입니다.

**실무 적용 해설**: 여러 워커 프로세스나 분산 노드가 모델 샤드를 나누어 실행할 때 고정된 기본 타임아웃에 의존(AS-IS)하면 네트워크 지연이나 대형 모델 로딩 중 오탐 장애 복구가 연쇄 발생합니다. `EXO_RUNNER_SHUTDOWN_TIMEOUT`, `EXO_RUNNER_HEALTH_CHECK_INTERVAL`, `EXO_RUNNER_MAX_STARTUP_RETRIES`처럼 수명주기 단계별 타임아웃을 환경변수로 세분화하고, 핵심 상태 전이는 부수 효과를 격리한 순수 함수로 작성(TO-BE)하면 다중 노드 경합 버그를 재현·조정하기 쉬워집니다. 반면 설정 가능한 타임아웃 키가 늘어날수록 `startup < shutdown` 같은 일관성 불변식이 깨질 수 있으므로 기동 시 설정 값 교차 검증이 필요합니다.

---

## 3. 매니페스트 CLI 및 풀스택 모듈 구조

### 3.1 `project.json` 매니페스트 기반 에이전트 CLI와 Git 실행 안전성 (`zby/llm-do`)

- **출처**: [`zby/llm-do`](https://github.com/zby/llm-do) · **핵심 스택**: `Python`, `pydantic_ai`, `CLI`, `JSON Manifest` · **적용 판단**: `Trial`
- **기술 개요**: `ProjectManifest`(`project.json`)로 런타임 설정·엔트리·경로를 선언하고 CLI 인자(`--input-json`)로 `entry.args`를 오버라이드하며 `HeadlessDisplayBackend`와 `pydantic_ai`의 `ModelMessagesTypeAdapter`를 연결한 에이전트 CLI입니다. `CLAUDE.md`에서는 승인 규칙 복잡화를 막기 위해 `git -C <path>` 사용을 금지하고 경량 라이브 모델(`claude-haiku-4-5`, `gpt-4o-mini`) 예시를 지정했습니다.

**실무 적용 해설**: 에이전트 CLI를 실행할 때마다 Python 진입 스크립트 내부에 모델명, 입력 스키마, UI 백엔드를 하드코딩(AS-IS)하면 헤드리스 배치 실행과 인터랙티브 실행을 분리하기 어렵습니다. `llm_do/cli/main.py`처럼 `ProjectManifest`로 프로젝트 계약을 고정하되 CLI 플래그로 진입 인자만 덮어쓰고, 에이전트 승인 훅이 경로를 오판하지 않도록 `git -C` 대신 작업 디렉터리 직접 실행을 강제(TO-BE)하면 자동화 스크립트의 예측 가능성이 높아집니다. 또한 문서 예시에 저비용 라이브 모델 실행을 기본값으로 둔 점은 개발 중 테스트 토큰 비용을 제어하는 실용적 규칙입니다.

### 3.2 `src/` 도메인 배선과 환경변수 기반 스킬 API 서버 (`itskai-dev/openclaw`, `robjsp/openclaw`)

- **출처**: [`itskai-dev/openclaw`](https://github.com/itskai-dev/openclaw) · [`robjsp/openclaw`](https://github.com/robjsp/openclaw) · **핵심 스택**: `TypeScript`, `FastAPI`, `CLI/Media Pipeline` · **적용 판단**: `Assess`
- **기술 개요**: 동일 업스트림 계열에서 수집된 두 저장소로, 코어 로직을 `src/cli`, `src/commands`, `src/provider-web.ts`, `src/infra`, `src/media`로 역할 분할해 `*.test.ts`를 동일 위치에 배치하고, `CLAUDE.md`에 GitHub 코멘트 개행 안전 플래그(`-F - <<'EOF'`)를, `local_places/main.py`에 `OPENAPI_SERVER_URL` 환경변수 분기를 둔 구조입니다.

**실무 적용 해설**: 에이전트 플랫폼이 CLI 배선, 웹 프로바이더, 미디어 파이프라인을 동시에 품으면서 테스트가 별도 루트 `tests/` 트리에 떨어져 있으면(AS-IS) 모듈 리팩토링 시 대응 테스트를 누락하기 쉽습니다. `src/` 하위 도메인 디렉터리와 `*.test.ts`를 1:1 인접 배치(colocation)하고, 자동화 도구가 PR 코멘트 작성 시 `\n` 리터럴 문자열을 이스케이프해 서식이 깨지는 문제를 `-F - <<'EOF'` 멀티라인 입력 규약으로 차단(TO-BE)하면 일상적인 협업 마찰이 줄어듭니다. 단 `local_places/main.py`처럼 로컬 개발 호스트명 기본값이 남아 있는 환경변수는 컨테이너 배포 시 반드시 외부 URL로 오버라이드해야 합니다.

### 3.3 하이브리드 SPA와 `@lobechat/*` 공유 패키지 계층화 (`looovely/lobe-chat`)

- **출처**: [`looovely/lobe-chat`](https://github.com/looovely/lobe-chat) · **핵심 스택**: `Next.js 16`, `React 19`, `react-router-dom`, `tRPC`, `Drizzle ORM`, `Zustand` · **적용 판단**: `Trial`
- **기술 개요**: Next.js 16 App Router 내부에서 `react-router-dom` 기반 SPA를 구동하고 Electron 데스크톱 앱(`apps/desktop`)과 공유 패키지(`@lobechat/database`, `@lobechat/agent-runtime`)를 분리하며, `tRPC` + `SWR` + `Zustand` + `Drizzle ORM`(PostgreSQL)으로 데이터 흐름을 계층화한 풀스택 구조입니다.

**실무 적용 해설**: 웹 앱과 데스크톱(Electron) 클라이언트를 별도 코드베이스로 관리하거나 Next.js 라우트 핸들러 안에 DB 쿼리와 에이전트 런타임을 직접 작성하면(AS-IS) 플랫폼 간 비즈니스 로직 중복이 급격히 늘어납니다. `@lobechat/database`와 `@lobechat/agent-runtime`을 독립 패키지로 추출하고 서버-클라이언트 간 계약을 `tRPC`와 `Drizzle` 스키마로 묶는 구조(TO-BE)를 취하면 웹과 데스크톱 모두에서 타입 안전한 에이전트 실행 계층을 공유할 수 있습니다. 다만 Next.js App Router 내부에 `react-router-dom` SPA를 중첩하는 하이브리드 라우팅은 SSR/하이드레이션 경계 디버깅 복잡도를 높이므로 명확한 클라이언트 전용 영역 분리가 필요합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - GPU 추론 백엔드는 웹 API와 작업 큐(SQS+DLQ)·유휴 종료 알람 스택을 분리해 비용 누수를 차단합니다.
  - 분산 추론 런타임의 기동·헬스체크·종료 타임아웃은 코드 상수가 아닌 환경변수로 외부화하고 상호 크기 제약을 검증합니다.
  - 모노레포 내 공통 에이전트 런타임과 DB 스키마(`Drizzle` 등)는 `packages/`로 분리해 웹·데스크톱 클라이언트 간 중복을 제거합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-08 수집 시점의 `CLAUDE.md`, `.cursorrules` 및 엔트리 파일 최대 1,000자 발췌본에 근거합니다. 당일 중복 발췌된 `openclaw` 포크 2건(`itskai-dev`, `robjsp`)은 단일 아키텍처 항목으로 통합해 기술했습니다.
