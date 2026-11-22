---
title: "[Trend] 2026-02-13: 선언형 워크플로우 그래프와 워크트리·ASGI 분리 설계"
pubDatetime: 2026-02-13T00:00:00Z
description: "YAML 선언형 LangGraph 파이프라인, n8n 원격 Python 태스크 러너, Serena 다중 언어 MCP 및 Litestar 팩토리 구조를 정리합니다."
category: trend
tags:
  - trend
  - langgraph
  - mcp-server
  - litestar
  - git-worktree
draft: false
---

에이전트 워크플로우가 고도화되면서 제어 흐름을 코드 대신 선언형 YAML로 분리하거나, 언어별 태스크 러너와 심볼릭 편집 도구를 별도 프로세스·MCP 서버로 떼어내는 경향이 뚜렷합니다. 아울러 대규모 모노레포와 데스크톱 GUI 도구에서는 빌드 로그 리다이렉션, 단일 인스턴스 잠금, 명시적 테스트 게이트를 통해 에이전트 작업의 예측 가능성을 높이고 있습니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 선언형 에이전트 파이프라인과 원격 태스크 실행기 | `sheikkinen/yamlgraph`, `twcctz200/n8n`, `oraios/serena` | YAML 그래프 상태 재개, 토큰 기반 원격 태스크 브로커, 언어 마커별 MCP 검증 |
| 워크트리 GUI·ASGI 팩토리 및 테스트 게이트 설계 | `tatargabor/wt-tools`, `engels74/zondarr`, `motto1/gist` | `fcntl` 단일 실행 잠금과 명시적 GUI 테스트, Litestar DI 팩토리, Electron+PySide6 분리 |

---

## 2. 선언형 에이전트 파이프라인과 원격 태스크 실행기

### 2.1 YAML 선언형 그래프와 인터럽트 재개 API (`sheikkinen/yamlgraph`)

- **출처**: [`sheikkinen/yamlgraph`](https://github.com/sheikkinen/yamlgraph) · **핵심 스택**: `Python`, `LangGraph`, `FastAPI`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: AI 워크플로우의 `60-80%`를 파이썬 코드 대신 YAML(그래프·프롬프트·스키마)로 정의하는 LangGraph 기반 프레임워크이며, `examples/booking/api/app.py`는 `create_app(db, graph)` 팩토리와 인터럽트 이후 실행을 이어가는 `ResumeRequest` 스키마를 제공합니다.

**실무 적용 해설**: 상태 전이가 많은 에이전트 흐름을 파이썬 함수 호출로만 하드코딩(AS-IS)하면 프롬프트와 분기 조건을 수정할 때마다 비즈니스 API 코드까지 함께 배포해야 합니다. 그래프 구조와 입출력 스키마를 YAML로 선언하고 FastAPI 진입점에서는 `ChatRequest`와 `ResumeRequest`로 인터럽트 중단 지점의 사용자 응답만 주입(TO-BE)하면 휴먼 인 더 루프(HITL) 워크플로우와 웹 API 계층을 깔끔하게 분리할 수 있습니다. 다만 YAML 선언 비중이 커질수록 정적 타입 검사가 약해지므로 CI 단계에서 그래프 스키마 유효성 검증 테스트를 별도로 두어야 합니다.

---

### 2.2 토큰 기반 원격 태스크 브로커와 빌드 로그 절감 (`twcctz200/n8n`)

- **출처**: [`twcctz200/n8n`](https://github.com/twcctz200/n8n) · **핵심 스택**: `TypeScript`, `pnpm`, `Python asyncio`, `PostHog` · **적용 판단**: `Trial`
- **기술 개요**: `pnpm build > build.log 2>&1` 로그 파일 리다이렉션으로 코딩 에이전트의 컨텍스트 낭비를 막고, `packages/@n8n/task-runner-python/src/main.py`에서 `ENV_TASK_BROKER_URI`와 `ENV_GRANT_TOKEN` 기반 비동기 태스크 러너를 별도 프로세스로 구동합니다.

**실무 적용 해설**: Node.js 기반 워크플로우 엔진 내부에서 사용자 정의 Python 코드를 직접 스폰(AS-IS)하면 메모리 격리와 권한 통제가 어렵고, 모노레포 전체 빌드 로그가 에이전트 콘텍스트를 가득 채우는 문제가 생깁니다. Python 실행기를 `TaskRunner` 비동기 클라이언트로 떼어내 브로커 URI와 그랜트 토큰(`ENV_GRANT_TOKEN`) 검증 없이는 기동조차 거부하게 설계(TO-BE)하면 런타임 경계가 명확해집니다. 빌드 출력을 파일로 돌린 뒤 마지막 몇 줄만 확인하는 규칙 역시 대규모 모노레포에서 토큰 소비를 줄이는 데 바로 적용할 수 있는 실무 패턴입니다.

---

### 2.3 다중 언어 심볼릭 편집 MCP와 `poe` 명령 고정 (`oraios/serena`)

- **출처**: [`oraios/serena`](https://github.com/oraios/serena) · **핵심 스택**: `Python`, `uv`, `poethepoet`, `pytest`, `MCP` · **적용 판단**: `Trial`
- **기술 개요**: `uv run serena-mcp-server`로 심볼릭 코드 편집 MCP 서버를 제공하며, `CLAUDE.md`에서 `uv run poe format`(Black+Ruff)과 `uv run poe type-check`(mypy)만 공식 검증 명령으로 허용하고 17개 이상 언어별 pytest 마커를 분리했습니다.

**실무 적용 해설**: 다국어 코드베이스를 지원하는 MCP 서버에서 에이전트가 임의의 린터나 전체 테스트 스위트를 실행(AS-IS)하면 미설치 언어 툴체인(Java, Rust 등) 때문에 매번 검증이 실패합니다. `poe` 태스크 러너로 포맷·타입 검사 진입점을 단일화하고 `pytest -m "python or go"`처럼 변경 영역에 맞는 마커와 `snapshot` 마커만 선택 실행(TO-BE)하면 피드백 루프를 일정하게 유지할 수 있습니다. 반면 언어별 마커가 많아질수록 각 언어 런타임의 테스트 픽스처 유지 비용이 커지므로 CI 기본 제외 목록과 로컬 검증 범위를 명확히 문서화해야 합니다.

---

## 3. 워크트리 GUI·ASGI 팩토리 및 테스트 게이트 설계

### 3.1 `fcntl` 단일 잠금 워크트리 GUI와 수동 테스트 트리거 (`tatargabor/wt-tools`)

- **출처**: [`tatargabor/wt-tools`](https://github.com/tatargabor/wt-tools) · **핵심 스택**: `Python`, `PySide6`, `git worktree`, `pytest` · **적용 판단**: `Assess`
- **기술 개요**: 약 4,880줄의 단일 GUI 파일을 `widgets/`, `dialogs/`, `workers/`, `control_center/` 믹스인으로 분해하고 `/tmp/wt-control-gui.lock`에 `fcntl` 잠금을 적용했으며, `CLAUDE.md`에 사용자 명시 요청 시에만 GUI 테스트를 실행하는 규정을 두었습니다.

**실무 적용 해설**: Git 워크트리와 백그라운드 워커를 관리하는 데스크톱 제어 도구가 여러 인스턴스로 중복 실행(AS-IS)되면 동일 워크트리 상태 파일이 경합하고, 매 수정마다 PySide6 GUI 테스트가 자동 실행되어 작업 흐름이 끊깁니다. `fcntl` 파일 잠금으로 단일 인스턴스를 보장하고 `_MenuCapture` 패턴과 `test_11_ralph_loop.py` 같은 모듈별 픽스처를 준비하되 실행은 명시적 트리거에만 묶어 두면(TO-BE) 개발 속도와 상태 안정성을 함께 확보할 수 있습니다. 단, `/opsx:apply` 이후 자동 커밋 규칙은 리뷰 전 불완전한 변경이 커밋될 수 있으므로 브랜치 보호와 병행해야 합니다.

---

### 3.2 Litestar DI 팩토리와 Granian ASGI·Hypothesis 검증 (`engels74/zondarr`)

- **출처**: [`engels74/zondarr`](https://github.com/engels74/zondarr) · **핵심 스택**: `Python`, `Litestar`, `Granian`, `Svelte 5`, `Hypothesis` · **적용 판단**: `Trial`
- **기술 개요**: `uv run python -m dev_cli start`로 백엔드·프론트엔드를 통합 구동하며, `backend/src/zondarr/app.py`의 `create_app()` 팩토리를 통해 Granian 프로덕션 서빙과 테스트용 `settings` 주입을 분리하고 Hypothesis 속성 기반 테스트를 수행합니다.

**실무 적용 해설**: 웹 프레임워크 앱 인스턴스를 모듈 전역 설정에 고정(AS-IS)하면 테스트마다 환경 변수를 패치해야 하고 병렬 테스트(`pytest -n auto`)에서 상태가 섞입니다. Litestar `Provide` 의존성 주입과 `create_app(settings=test_settings)` 팩토리 패턴을 결합하고, 초대 코드 길이·생성 규칙 같은 불변식은 예시 기반 단위 테스트 대신 Hypothesis 속성 테스트(`tests/property/`)로 검증(TO-BE)하면 경계 조건 결함을 조기에 드러낼 수 있습니다. 또한 FastAPI 외 대안으로 Litestar + Structlog + Granian 조합의 구조적 OpenAPI(Scalar/Swagger) 구성을 참고할 가치가 있습니다.

---

### 3.3 Electron + Yarn 4 모노레포와 PySide6 보조 앱 결합 (`motto1/gist`)

- **출처**: [`motto1/gist`](https://github.com/motto1/gist) · **핵심 스택**: `Electron`, `Node.js 22`, `Yarn 4.9.1`, `Biome`, `PySide6` · **적용 판단**: `Assess`
- **기술 개요**: Electron 데스크톱 앱에 Corepack 기반 Yarn 4.9.1, Vitest, Playwright E2E, Biome 포맷터를 표준화하면서, `resources/gist-video/backend/app/main.py`는 독립 실행 가능한 PySide6 `QApplication` 윈도우 엔트리포인트로 분리했습니다.

**실무 적용 해설**: 데스크톱 클라이언트와 미디어 처리 보조 UI가 단일 Node/Python 빌드 스크립트에 얽혀 있으면(AS-IS) 렌더러 의존성(`yarn add -D`)과 네이티브 Python UI 의존성 충돌을 진단하기 어렵습니다. Node 측 품질 게이트(`yarn typecheck`, `yarn lint`, `yarn test:e2e`)와 `resources/` 하위의 독립 PySide6 엔트리포인트를 명확히 가르면(TO-BE) 패키징 단계에서 각 런타임의 책임을 격리할 수 있습니다. 다만 두 런타임 간 IPC나 프로세스 수명주기 관리가 누락되면 종료 시 좀비 프로세스가 남을 수 있어 배포 전 프로세스 정리 테스트가 필요합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `pnpm build > build.log 2>&1`처럼 대용량 빌드 로그를 파일로 리다이렉트해 에이전트 컨텍스트 소비 억제.
  - FastAPI/Litestar 앱에서 전역 싱글턴 대신 `create_app(settings=...)` 팩토리를 도입해 `pytest -n auto` 병렬 테스트 안전성 확보.
  - 다국어·GUI 저장소에서 에이전트가 실행할 테스트 마커(`pytest -m`)와 명시적 실행 조건을 `CLAUDE.md`에 고정.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-13 수집 시점의 공개 저장소 `CLAUDE.md` 및 주요 앱 엔트리 파일 발췌본(최대 1,000자)에 근거하며, 전체 모듈의 성능 벤치마크와 프로덕션 운영 지표는 확인되지 않았습니다.
