---
title: "[Trend] 2026-05-10: 클린 아키텍처, 토큰 명명 규약과 다중 권한 평면 분리"
pubDatetime: 2026-05-10T00:00:00Z
description: "OpenAI Agents SDK 4계층 클린 아키텍처, Airflow Dag/DAG 토큰 규약, Krab-openclaw 3계층 권한 평면, ProxyFix IP 보정 및 안전 실행 모드를 분석합니다."
category: trend
tags:
  - trend
  - ai-agent
  - claude-md
  - fastapi
  - devops
draft: false
---

2026년 5월 10일 수집 데이터에서는 에이전트 예제가 단일 스크립트를 벗어나 4계층 클린 아키텍처와 의존성 주입(DI)으로 구조화되는 흐름과 함께, 자연어 문서와 코드 식별자 간 대소문자 표기까지 제어하는 정밀한 `CLAUDE.md` 규칙이 확인되었습니다. 운영 백엔드 영역에서는 3단계 권한 평면 분리, PaaS 역프록시 뒤의 클라이언트 IP 복원, 그리고 인프라 명령 실행 전 의도 설명을 강제하는 안전 실행 모드가 핵심으로 나타났습니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 클린 아키텍처·토큰 명명 규약과 업스트림·다운스트림 경계 | `jsh0116/agent-class`, `jscheffl/airflow`, `nguyencmc/openclaw` | 4계층 DI + `AI_BASE_URL` 프로바이더 추상화, 산문 `Dag` vs 코드 `DAG` 토큰 보존 규약, 업스트림 계약 검증을 적용함 |
| 다중 권한 평면·역프록시 IP 보정과 안전 실행 가드레일 | `Pavua/Krab-openclaw`, `dprodger/ApproachNote`, `therealruthvik/devops-ai-playbook` | 텔레그램·관리 패널·게이트웨이 3평면 격리, `ProxyFix` + 풀링 선행 설정, AWS 명령 전 사전 의도 설명을 강제함 |

---

## 2. 클린 아키텍처·토큰 명명 규약과 업스트림·다운스트림 경계

### 2.1 OpenAI Agents SDK 4계층 클린 아키텍처와 `uv` 서브격리 (`jsh0116/agent-class`)

- **출처**: [`jsh0116/agent-class`](https://github.com/jsh0116/agent-class) · **핵심 스택**: `Python`, `uv`, `OpenAI Agents SDK`, `Streamlit`, `Jupyter` · **적용 판단**: `Trial`
- **기술 개요**: 각 서브프로젝트가 독립된 `pyproject.toml`, `.python-version`, `uv.lock`, 개별 `CLAUDE.md`를 가지는 에이전트 예제 모음입니다. 특히 `life-coach-agent`는 `domain/`(dataclass 엔티티) → `application/`(`CoachChatUseCase`, `AppContext` DI 컨테이너) → `infrastructure/`(`load_run_config()`) → `presentation/`(`WebSearchTool`, `get_coaching_tip`, `Agent`) 4계층으로 분리하고 `main.py`를 조립 루트(Composition Root)로 삼아 `AI_BASE_URL` 환경 변수 유무에 따라 `OpenAIProvider` 엔드포인트를 전환합니다.

**실무 적용 해설**: LLM 에이전트 프로토타입은 대개 UI 코드(`Streamlit`) 안에 프롬프트, 도메인 모델, API 클라이언트 초기화가 뒤섞여 모델 프로바이더 교체나 단위 테스트가 어렵습니다. 기존(AS-IS)의 단일 파일 스크립트를 4계층 클린 아키텍처 + `AppContext` DI + `AI_BASE_URL` 기반 `OpenAIProvider` 추상화(TO-BE)로 분리하면 도메인 유스케이스를 에이전트 SDK나 특정 클라우드 엔드포인트로부터 독립적으로 검증할 수 있습니다. 물론 간단한 단일 목적 봇에서는 파일과 계층 수가 늘어나는 보일러플레이트 비용을 감안해 적용 수위를 조절해야 합니다.

---

### 2.2 산문(`Dag`)과 코드 토큰(`DAG`)을 분리하는 정밀 명명 규약 (`jscheffl/airflow`)

- **출처**: [`jscheffl/airflow`](https://github.com/jscheffl/airflow) · **핵심 스택**: `Python`, `Apache Airflow`, `FastAPI`, `prek`, `Breeze` · **적용 판단**: `Assess`
- **기술 개요**: 전날 살펴본 Airflow 포크(`diogosilva30/airflow`)의 `breeze` 워크트리 격리 환경에 더해, 본 저장소의 `CLAUDE.md`는 에이전트의 전역 치환 실수를 막는 정밀한 토큰 수준 명명 규약을 담고 있습니다. 산문(Prose)에서는 `Dag`(Title Case)로 쓰고 "Directed Acyclic Graph" 풀네임 풀기를 금지하되, Python SDK(`from airflow.sdk import DAG`, `dag_id`), CLI(`airflow dags list`), 경로(`dag_processing/`)의 리터럴 코드 토큰은 코드 블록 안에서도 절대 대소문자를 고치지 못하게 명시합니다.

**실무 적용 해설**: AI 코딩 에이전트에게 "문서에서 용어 표기를 통일하라"고 지시하면 정규식 치환처럼 Python 클래스명(`DAG`)이나 CLI 플래그(`dags`), 디렉터리 경로까지 일괄 변경해 코드가 깨지는 사고가 자주 발생합니다. 기존(AS-IS)의 모호한 스타일 가이드 대신 산문 표기(`Dag`)와 절대 변경 금지 코드 토큰(`DAG`, `dag_id`, `dag_processing/`)을 구체적 반례와 함께 `CLAUDE.md`에 열거(TO-BE)하면 문서 품질과 코드 무결성을 동시에 지킬 수 있습니다. 다만 예외 목록이 길어질수록 초기 프롬프트 토큰을 점유하므로 핵심 토큰 패턴 위주로 간결히 유지하는 것이 중요합니다.

---

### 2.3 업스트림 계약 규율과 다운스트림 런타임 배포의 대비 (`nguyencmc/openclaw`)

- **출처**: [`nguyencmc/openclaw`](https://github.com/nguyencmc/openclaw) · **핵심 스택**: `TypeScript`, `pnpm`, `Mintlify`, `CLAUDE.md` · **적용 판단**: `Assess`
- **기술 개요**: `openclaw/openclaw` 업스트림 코어 규칙을 담은 본 저장소는 아래에서 다룰 다운스트림 배포 사례(`Pavua/Krab-openclaw`)와 흥미로운 대조를 이룹니다. 업스트림 코어는 `CLAUDE.md`와 `docs/CLAUDE.md`를 통해 의존성 계약 선행 확인, 저장소 루트 상대 경로 인용, Mintlify 링크 규격 같은 플랫폼 자체의 일관성 규율에 집중하는 반면, 다운스트림 운영 저장소는 이를 감싸는 다중 프로세스 경계와 운영 런처 규율을 덧입힙니다.

**실무 적용 해설**: 오픈소스 에이전트 플랫폼을 직접 포크해 개인·사내 운영 환경에 배포할 때 업스트림의 코딩·문서 규약과 다운스트림의 운영·권한 규약이 한 파일에 뒤섞이면 업스트림 동기화 시 충돌이 잦아집니다. 코어 플랫폼 계층(`nguyencmc/openclaw`)과 운영 어댑터 계층(`Krab-openclaw`)의 관심사를 구분해 파악하면(TO-BE), 향후 업스트림 패치를 반영하면서도 로컬 런타임 정책을 안정적으로 유지할 수 있습니다.

---

## 3. 다중 권한 평면·역프록시 IP 보정과 안전 실행 가드레일

### 3.1 3계층 권한 평면 분리와 런타임 우선 원칙 (`Pavua/Krab-openclaw`)

- **출처**: [`Pavua/Krab-openclaw`](https://github.com/Pavua/Krab-openclaw) · **핵심 스택**: `Python`, `Pyrofork (MTProto)`, `OpenClaw Gateway`, `Tkinter`, `pytest` · **적용 판단**: `Assess`
- **기술 개요**: Telegram MTProto 유저봇(`pyrofork`)과 OpenClaw 게이트웨이를 연동한 개인 비서 런타임으로, 권한 평면을 (1) Telegram 유저봇(메시지 전달·ACL), (2) 소유자 웹 패널(`127.0.0.1:8080`, 헬스·라우팅·운영), (3) OpenClaw 게이트웨이(`127.0.0.1:18789`, 네이티브 챗·도구·에이전트) 세 개로 분리합니다. `CLAUDE.md`는 게이트웨이에 `SIGHUP` 시그널을 보내지 말고 전용 런처 스크립트를 쓰도록 지시하며, 문서와 실제 런타임 동작이 어긋날 때는 "런타임을 신뢰하라"는 원칙을 명시합니다.

**실무 적용 해설**: 채팅 메신저 봇에 에이전트 툴 실행 권한과 운영 제어 기능을 한 프로세스로 몰아넣으면 ACL 누락 시 메신저 채널을 통해 호스트 제어 권한이 통째로 노출될 위험이 큽니다. 외부 전달 채널(Telegram + ACL), 로컬 운영 패널(`:8080`), 에이전트 실행 게이트웨이(`:18789`)를 포트와 역할 평면으로 분리하고 시그널·재기동 절차를 고정(TO-BE)하면 피해 반경을 크게 좁힐 수 있습니다. 다만 다중 프로세스로 나뉘는 만큼 기동 순서와 상태 동기화를 관리하는 전용 런처 스크립트의 안정성이 뒷받침되어야 합니다.

---

### 3.2 `ProxyFix` 클라이언트 IP 복원과 커넥션 풀 임포트 순서 (`dprodger/ApproachNote`)

- **출처**: [`dprodger/ApproachNote`](https://github.com/dprodger/ApproachNote) · **핵심 스택**: `Python 3.13`, `Flask`, `Gunicorn`, `PostgreSQL`, `Werkzeug ProxyFix`, `SwiftUI` · **적용 판단**: `Trial`
- **기술 개요**: 재즈 스탠다드 레퍼런스 API(`backend/app.py`)와 SwiftUI iOS/macOS 앱으로 구성된 프로젝트로, PaaS(Render) 배포 환경에서 흔히 겪는 두 가지 Flask 프로덕션 함정을 명시적으로 방어합니다. 첫째는 `db_utils` 임포트 *이전에* `os.environ['DB_USE_POOLING'] = 'true'`를 선행 설정해 모듈 임포트 시점 풀링 분기를 보장하는 것이고, 둘째는 `ProxyFix` 미들웨어를 장착해 `Flask-Limiter`가 리버스 프록시 IP가 아닌 실제 클라이언트 IP 기준으로 요청 제한을 적용하도록 교정한 점입니다.

**실무 적용 해설**: Render, Cloud Run, ALB 같은 리버스 프록시 뒤에서 `Flask-Limiter`를 운영할 때 `ProxyFix`를 빠뜨리면 모든 사용자 요청이 프록시 단일 IP로 집계되어 정상 사용자까지 한꺼번에 `429 Too Many Requests` 차단에 걸리는 장애가 발생합니다. 기존(AS-IS)의 기본 Flask 앱 구성에 `ProxyFix`와 모듈 임포트 전 환경 변수 설정(TO-BE)을 적용하면 실제 클라이언트 IP 기반 속도 제한과 DB 커넥션 풀링을 안정적으로 동작시킬 수 있습니다. 단, `ProxyFix`의 `x_for` 홉 수는 실제 인프라 앞단의 신뢰 가능한 프록시 개수와 정확히 일치시켜야 `X-Forwarded-For` 스푸핑을 막을 수 있습니다.

---

### 3.3 인프라 명령 전 사전 의도 설명을 강제하는 안전 실행 모드 (`therealruthvik/devops-ai-playbook`)

- **출처**: [`therealruthvik/devops-ai-playbook`](https://github.com/therealruthvik/devops-ai-playbook) · **핵심 스택**: `Docker Compose`, `Node.js 18+`, `AWS EKS`, `Python`, `Streamlit`, `AWS Bedrock` · **적용 판단**: `Assess`
- **기술 개요**: 10개 마이크로서비스(`boutique-microservices`)의 로컬 개발부터 EKS 배포, AWS Bedrock 에이전트 기반 AIOps 원인 분석(`projects/aiops-assistant/app.py`)까지 다루는 DevOps 플레이북 저장소입니다. `CLAUDE.md`는 **Safe Execution Mode** 규칙을 두어 라이브 AWS 인프라에 영향을 주는 작업을 수행하기 전 "무엇을 왜 실행하려는지" 1~2문장의 평이한 설명을 먼저 출력한 뒤 진행하도록 의무화합니다.

**실무 적용 해설**: 클라우드 CLI(`aws`, `kubectl`, `terraform`) 접근 권한을 가진 코딩 에이전트가 사용자 확인이나 맥락 설명 없이 파괴적인 변경 명령을 즉시 실행하면 복구가 어려운 인프라 장애로 이어집니다. 실행 직전 1~2문장의 사전 의도 설명을 강제하는 Safe Execution Mode 규율(TO-BE)은 사람이 명령의 목적과 영향 범위를 한 번 더 검증할 수 있는 최소한의 감사 게이트 역할을 합니다. 물론 상호작용 턴마다 약간의 출력 지연과 확인 비용이 추가되지만 프로덕션 AWS 계정과 맞닿은 작업에서는 충분히 감수할 만한 안전장치입니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - PaaS나 로드밸런서 뒤에서 IP 기반 Rate Limiting(`Flask-Limiter`, `SlowAPI`)을 사용할 때 `ProxyFix` 등 프록시 헤더 신뢰 설정과 홉 수가 인프라 구성과 일치하는지 점검합니다.
  - 용어 통일 규칙 작성 시 산문 표기(`Dag`)와 변경 금지 코드 식별자(`DAG`, `dag_id`)를 명확히 분리해 에이전트의 과잉 치환을 예방합니다.
  - 라이브 클라우드·DB·프로덕션 권한이 연결된 세션에서는 파괴적 CLI 실행 전 1~2문장 의도 설명 또는 승인 게이트를 `CLAUDE.md` 필수 규칙으로 둡니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-05-10 수집 시점의 공개 저장소 `CLAUDE.md`, 백엔드 엔트리포인트, 서브프로젝트 구조 발췌본에 근거하며, 각 런타임의 실운영 보안성 및 지연 시간은 별도 검증이 필요합니다.
