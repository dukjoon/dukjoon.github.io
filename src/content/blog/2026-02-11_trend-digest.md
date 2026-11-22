---
title: "[Trend] 2026-02-11: 도메인 캐시 경계 분리와 에이전트 샌드박스 실행 격리"
pubDatetime: 2026-02-11T00:00:00Z
description: "커널·서비스 계층 캐시 분리, FastAPI 에이전트 샌드박스 속도 제한, Hub-and-Spoke CLI 및 Gravitino MCP 서버 연동 패턴을 정리합니다."
category: trend
tags:
  - trend
  - multi-agent
  - rag-architecture
  - mcp-server
  - monorepo
draft: false
---

멀티 에이전트와 RAG 백엔드가 복잡해지면서 커널 추상화와 상위 도메인 서비스의 의존성 방향을 엄격히 분리하고, 에이전트 코드 실행과 메타데이터 접근을 별도 샌드박스와 MCP 프로세스로 격리하는 설계가 두드러집니다. 동시에 대규모 모노레포에서는 `CLAUDE.md`를 패키지 단위로 쪼개 탐색 범위와 프론트엔드 검증 규칙을 강제하는 흐름이 뚜렷합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 멀티 에이전트 런타임 격리와 추상화 경계 | `nexi-lab/nexus`, `jeremyspofford/nova-ai-platform`, `BulloRosso/etienne` | 저수준 캐시 드라이버와 도메인 캐시 분리, Hub CLI 및 워크스페이스 볼륨 격리 |
| 모노레포 규칙, RAG 샌드박스 및 메타데이터 MCP 연동 | `mastra-ai/mastra`, `felix-qiu/ragflow`, `diqiu50/gravitino` | 패키지별 `CLAUDE.md` 범위 제한, FastAPI 샌드박스 분리, MCP 설정 주입 구조 |

---

## 2. 멀티 에이전트 런타임 격리와 추상화 경계

### 2.1 드라이버 비종속 도메인 캐시 계층 분리 (`nexi-lab/nexus`)

- **출처**: [`nexi-lab/nexus`](https://github.com/nexi-lab/nexus) · **핵심 스택**: `Python 3.11`, `CacheStoreABC`, `Dragonfly` · **적용 판단**: `Trial`
- **기술 개요**: 저수준 KV·PubSub 추상화인 `CacheStoreABC` 위에 `PermissionCache`, `TigerCache`, `ResourceMapCache`, `EmbeddingCache`를 구현하고, 커널(`NexusFS`)이 도메인 캐시를 직접 임포트하지 않도록 격리한 구조입니다.

**실무 적용 해설**: 에이전트 파일시스템이나 검색 엔진이 Redis·Dragonfly 같은 특정 캐시 클라이언트에 직접 결합(AS-IS)되면 테스트 환경 전환이나 드라이버 교체 시 코어 로직까지 수정해야 합니다. `src/nexus/cache/domain.py`처럼 커널은 `CacheStoreABC`와 `NullCacheStore`만 인지하고 `CacheFactory`와 상위 인증·검색 서비스만 도메인 캐시를 소비하도록 역전(TO-BE)하면 인메모리·Null 드라이버 기반 단위 테스트가 단순해집니다. 다만 캐시 레이어와 메인 서버·배포 저장소가 이원화(`~/nexus` 등)되어 있어 PyPI 버전 릴리스와 배포 저장소 간 프로토콜 호환성을 함께 관리해야 합니다.

---

### 2.2 Hub-and-Spoke 오케스트레이션과 CLI 제어면 (`jeremyspofford/nova-ai-platform`)

- **출처**: [`jeremyspofford/nova-ai-platform`](https://github.com/jeremyspofford/nova-ai-platform) · **핵심 스택**: `Python`, `httpx`, `PostgreSQL`, `Redis`, `Alembic` · **적용 판단**: `Assess`
- **기술 개요**: 중앙 Hub가 전문 에이전트들을 조율하는 Hub-and-Spoke 구조로, GPU/CPU Docker 타깃과 Alembic 마이그레이션을 분리하고 `src/nova/cli/main.py`에서 Bearer 인증 기반 `httpx` 요청으로 태스크를 제출합니다.

**실무 적용 해설**: 자율 에이전트 작업을 로컬 스크립트에서 직접 실행(AS-IS)하면 태스크 상태 추적, DB 스키마 이력, 인증 경계가 파편화되기 쉽습니다. `nova-cli submit --project <uuid> --tier 2`처럼 CLI가 직접 엔진을 구동하지 않고 Hub HTTP API의 작업 큐와 PostgreSQL/Redis 상태 계층으로 요청을 위임(TO-BE)하면 다중 워커 환경에서도 실행 이력과 권한 감사를 일관되게 유지할 수 있습니다. 반면 로컬 검증 시에도 GPU/CPU 컨테이너 스택(`make up-cpu`)과 DB 마이그레이션 선행이 필요해 경량 CLI 도구 대비 초기 구동 비용이 높습니다.

---

### 2.3 테넌트별 워크스페이스 볼륨과 핫 리로드 API 격리 (`BulloRosso/etienne`)

- **출처**: [`BulloRosso/etienne`](https://github.com/BulloRosso/etienne) · **핵심 스택**: `NestJS`, `React/Vite`, `Flask`, `Docker` · **적용 판단**: `Assess`
- **기술 개요**: 중앙 마운트 볼륨(`/workspace/<project-name>`) 아래에 프로젝트별 `.claude/CLAUDE.md`, `settings.json`, `data/permissions.json`을 배치하고, `webserver/app.py`가 프로젝트별 정적 HTML과 동적 API 모듈을 핫 리로드로 서빙합니다.

**실무 적용 해설**: 단일 에이전트 컨테이너에서 여러 프로젝트의 프롬프트와 도구 권한을 공유(AS-IS)하면 테넌트 간 파일 오염이나 과도한 도구 허용 문제가 발생합니다. 프로젝트 디렉터리 단위로 `.claude/settings.json`과 `permissions.json`을 분리 마운트하고 `WORKSPACE_DIR` 환경 변수로 실행 경로를 고정(TO-BE)하면 프로젝트별 권한 정책과 입출력(`data/in`, `out`) 경계를 명확히 나눌 수 있습니다. 단, `webserver/app.py`처럼 `importlib.util` 기반 동적 파이썬 모듈 로딩을 허용할 경우 임의 코드 실행 위험이 따르므로 컨테이너 네트워크와 파일시스템 권한 격리가 전제되어야 합니다.

---

## 3. 모노레포 규칙, RAG 샌드박스 및 메타데이터 MCP 연동

### 3.1 패키지별 `CLAUDE.md` 범위 제한과 스킬 바인딩 (`mastra-ai/mastra`)

- **출처**: [`mastra-ai/mastra`](https://github.com/mastra-ai/mastra) · **핵심 스택**: `TypeScript`, `pnpm`, `Vite`, `Vitest`, `Storybook` · **적용 판단**: `Trial`
- **기술 개요**: 루트 `CLAUDE.md`에서 `examples/` 폴더 탐색 금지를 명시하고 `pnpm build:core`/`rag`/`evals` 등 패키지별 빌드 명령을 분리하며, `packages/playground-ui/CLAUDE.md`에 프론트엔드 전용 검증 스킬을 연결한 모노레포입니다.

**실무 적용 해설**: 대규모 TypeScript 모노레포에서 코딩 에이전트가 루트 전체와 예제 디렉터리까지 탐색(AS-IS)하면 컨텍스트 윈도우가 빠르게 소모되고 UI 수정 시 백엔드 테스트까지 불필요하게 실행됩니다. 루트 문서에서 비대상 경로(`examples/`)를 차단하고 `packages/playground-ui/CLAUDE.md`처럼 하위 패키지 수준에 `e2e-frontend-validation`과 Vitest·Storybook 명령을 지역화(TO-BE)하면 에이전트의 변경 반경과 검증 시간을 동시에 줄일 수 있습니다. 다만 패키지별 `CLAUDE.md`가 늘어날수록 루트 스크립트와 개별 패키지 명령 간 불일치가 생길 수 있어 CI 파이프라인 기준선과 주기적으로 대조해야 합니다.

---

### 3.2 블루프린트 기반 RAG API와 FastAPI 샌드박스 분리 (`felix-qiu/ragflow`)

- **출처**: [`felix-qiu/ragflow`](https://github.com/felix-qiu/ragflow) · **핵심 스택**: `Python`, `Flask`, `FastAPI`, `slowapi`, `UmiJS` · **적용 판단**: `Trial`
- **기술 개요**: 지식베이스·대화·문서·캔버스 기능을 Flask 블루프린트(`kb_app.py`, `canvas_app.py` 등)로 분할하고, 에이전트 코드 실행기(`agent/sandbox/executor_manager/main.py`)는 별도 FastAPI 앱과 `slowapi` 속도 제한으로 분리한 아키텍처입니다.

**실무 적용 해설**: 문서 파싱·검색 API 서버 내부에서 에이전트가 생성한 코드나 도구 호출을 동기 처리(AS-IS)하면 폭주 요청이나 무한 루프가 전체 RAG 서비스의 가용성을 떨어뜨립니다. `api/ragflow_server.py`의 비즈니스 라우팅과 `executor_manager` FastAPI 프로세스를 분리하고 `app.state.limiter` 및 `RateLimitExceeded` 핸들러로 실행기 앞단에 호출 제한을 거는 구조(TO-BE)를 택하면 장애 전파를 차단할 수 있습니다. 멀티 스토어(MySQL, Elasticsearch/Infinity, Redis, MinIO)와 두 가지 웹 프레임워크를 함께 운영하는 만큼 로컬 디버깅과 장애 추적 시 컨테이너 로그 집계가 필수입니다.

---

### 3.3 다국어 코딩 규율과 메타데이터 MCP 진입점 (`diqiu50/gravitino`)

- **출처**: [`diqiu50/gravitino`](https://github.com/diqiu50/gravitino) · **핵심 스택**: `Java`, `Gradle Spotless`, `Python`, `MCP` · **적용 판단**: `Assess`
- **기술 개요**: Java 코어에는 Google Java Style과 `./gradlew spotlessApply` 포맷팅을 강제하고, `mcp-server/mcp_server/main.py`에서는 CLI 인자 파싱과 `Setting` 객체를 통해 `GravitinoMCPServer`를 기동하도록 구성했습니다.

**실무 적용 해설**: 데이터 카탈로그처럼 Java/Gradle 기반 코어와 Python 기반 MCP 어댑터가 공존하는 저장소에서 에이전트가 언어별 규약 없이 코드를 수정(AS-IS)하면 포맷 불일치와 설정 누락으로 빌드가 깨지기 쉽습니다. `CLAUDE.md`에 영문 주석과 `spotlessApply` 실행 의무를 고정하고 `GravitinoMCPServer`의 설정 바인딩을 `DefaultSetting`/`Setting` 데이터 모델로 단일화(TO-BE)하면 코어와 MCP 서버 간 인터페이스 드리프트를 줄일 수 있습니다. 실제 운영 환경에서는 카탈로그 메타데이터 조회 권한이 MCP 클라이언트에 과도하게 위임되지 않도록 읽기/쓰기 스코프 설정을 검증해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - 모노레포 루트 `CLAUDE.md`에 `examples/`·빌드 산출물 제외 규칙을 추가하고, UI·에이전트 패키지별 하위 `CLAUDE.md`로 검증 명령 분리 검토.
  - Redis·Dragonfly 등 외부 스토어 의존 코어에서 `CacheStoreABC` / `NullCacheStore` 형태의 인터페이스를 추출해 단위 테스트의 외부 의존성 제거.
  - 에이전트 코드 실행 엔드포인트를 메인 API(Flask/Express)에서 별도 FastAPI 워커로 분리하고 `slowapi` 등 레이트 리미터 적용 확인.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-11 수집 시점의 공개 저장소 `CLAUDE.md` 및 주요 소스 파일 발췌본(최대 1,000자)에 근거하며, 전체 테스트 스위트 실행 결과나 프로덕션 트래픽 환경의 장기 안정성은 별도 검증이 필요합니다.
