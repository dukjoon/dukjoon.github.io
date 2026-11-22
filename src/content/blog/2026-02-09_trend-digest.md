---
title: "[Trend] 2026-02-09: YAML-PDF 파싱 백엔드와 DXF 마이크로서비스 경계"
pubDatetime: 2026-02-09T00:00:00Z
description: "YAML 템플릿 파싱·Jinja2 PDF 생성 Flask API, ezdxf FastAPI 마이크로서비스, 확장 런타임 격리 및 다중 프레임워크 규칙 충돌 사례를 분석합니다."
category: trend
tags:
  - trend
  - fastapi
  - flask
  - pdfkit
  - architecture
draft: false
---

프론트엔드와 백엔드를 결합한 풀스택 애플리케이션에서 YAML 템플릿 파싱·PDF 렌더링이나 CAD 도면(`DXF`) 변환처럼 무거운 외부 바이너리 작업을 전용 API 서비스로 격리하는 아키텍처가 뚜렷해지고 있습니다. 이번 일자에서는 파일 변환 백엔드 설계와 확장 모듈·규칙 파일 경계 사례를 살펴봅니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 파일 변환 백엔드 및 마이크로서비스 격리 | `aafre/resume-builder`, `YorgosPag/NestorApp` | YAML-Jinja2-`pdfkit` 비동기 API 분리, `ezdxf` FastAPI 서비스 및 ADR·시맨틱 HTML 규약 |
| 플러그인 격리 및 규칙 파일 드리프트 | `FullStackKevinVanDriel/openclaw` (`johnakelly-yahoo-com/openclaw`, `jualiandominguez73-cell/molbook-openclaw`), `gamingopgamingop/sarthak-skill-forge` | `npm install --omit=dev` 기준 확장 패키지 경계, `.claude/CLAUDE.md`와 `.cursorrules` 스택 불일치 점검 |

---

## 2. 파일 변환 백엔드 및 마이크로서비스 격리

### 2.1 YAML 템플릿 파싱과 Jinja2·`pdfkit` PDF 렌더링 API (`aafre/resume-builder`)

- **출처**: [`aafre/resume-builder`](https://github.com/aafre/resume-builder) · **핵심 스택**: `React + Vite (TypeScript)`, `Flask`, `Jinja2`, `pdfkit`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: React/TypeScript 프론트엔드(`resume-builder-ui/`)와 Flask 백엔드(`app.py`)를 결합해 YAML 템플릿을 파싱하고 Jinja2 HTML/CSS 템플릿과 `pdfkit` 파이프라인(`resume_generator.py`)으로 구조화된 문서 PDF를 생성하는 오픈소스 저장소입니다. `ProxyFix`, `secure_filename`, `ThreadPoolExecutor`, `Flask-Compress`, `DEBUG_LOGGING` 환경변수 분기가 백엔드 API에 포함되어 있습니다.

**실무 적용 해설**: 브라우저 클라이언트 측 인쇄 API로 문서 PDF를 직접 렌더링하면(AS-IS) OS별 폰트·페이지 나누기 불일치와 CSS 깨짐이 반복됩니다. 이 오픈소스 저장소처럼 프론트엔드(`resume-builder-ui/`)는 입력 상태와 프리뷰를 담당하고, Flask API 서버가 YAML 데이터 파싱과 Jinja2·`pdfkit` 변환을 전담하며 `ThreadPoolExecutor`와 `secure_filename`으로 동시 변환 및 파일명 보안 경계를 처리(TO-BE)하면 일관된 PDF 출력 품질을 유지할 수 있습니다. 다만 `pdfkit`(wkhtmltopdf 래퍼)은 외부 바이너리 프로세스를 호출하므로 요청량이 높은 운영 환경에서는 워커 스레드 풀 상한과 임시 파일(`tempfile`) 정리 주기를 별도 제어해야 합니다.

### 2.2 `ezdxf` 변환 마이크로서비스와 중앙 ADR 규약 (`YorgosPag/NestorApp`)

- **출처**: [`YorgosPag/NestorApp`](https://github.com/YorgosPag/NestorApp) · **핵심 스택**: `FastAPI`, `ezdxf`, `Docker`, `ADR Architecture` · **적용 판단**: `Trial`
- **기술 개요**: `services/dxf-export/src/main.py`에 `ezdxf` 기반 CAD 도면 내보내기 전용 FastAPI 마이크로서비스(`asynccontextmanager` 수명주기, `/export`·`/health` 라우터, 단일 워커 컨테이너 실행)를 분리하고, `CLAUDE.md`에서 중앙 ADR 인덱스(`adr-index.md`), `any` 및 인라인 스타일 금지, 시맨틱 HTML(`section`, `nav`, `main`) 강제, npm 패키지 라이선스 사전 검사를 규정한 사례입니다.

**실무 적용 해설**: CAD 파일 생성(`ezdxf`)이나 무거운 바이너리 포맷 변환 로직을 메인 웹 백엔드에 직접 포함하면(AS-IS) CPU 점유와 의존성 충돌로 핵심 API 응답성이 저하됩니다. `NestorApp`처럼 도면 변환을 독립 FastAPI 마이크로서비스(`ADR-052`)로 떼어내 컨테이너로 배포하고, 에이전트가 시맨틱 태그 대신 무분별한 중첩 `<div>`나 미검증 오픈소스 라이선스 패키지를 끌어오지 못하도록 `CLAUDE.md`에 하드 가드레일을 명시(TO-BE)하면 아키텍처 일관성과 법적 컴플라이언스를 함께 지킬 수 있습니다. 다만 `CLAUDE.md`에 로컬 Windows 절대 경로가 참조되어 있으므로, 협업·CI 환경에서는 저장소 상대 경로로 ADR 문서를 연결하는 보완이 필요합니다.

---

## 3. 플러그인 격리 및 규칙 파일 드리프트

### 3.1 `extensions/*` 운영 설치 격리와 스킬 스키마 계약 (`FullStackKevinVanDriel/openclaw`, `johnakelly-yahoo-com/openclaw`, `jualiandominguez73-cell/molbook-openclaw`)

- **출처**: [`FullStackKevinVanDriel/openclaw`](https://github.com/FullStackKevinVanDriel/openclaw) · [`johnakelly-yahoo-com/openclaw`](https://github.com/johnakelly-yahoo-com/openclaw) · [`jualiandominguez73-cell/molbook-openclaw`](https://github.com/jualiandominguez73-cell/molbook-openclaw) · **핵심 스택**: `TypeScript`, `Node.js (npm)`, `FastAPI`, `Pydantic Schemas` · **적용 판단**: `Assess`
- **기술 개요**: 동일 업스트림 기반의 파생 저장소 3건이 공통으로 보여주는 구조로, 루트 `package.json` 비대화를 막기 위해 `extensions/*` 플러그인 설치 시 해당 디렉터리 내부에서 `npm install --omit=dev`만 실행하도록 경계를 두고 `docs/`에 큐·Pi 설정 문서를 두며, Python 스킬(`local_places/main.py`)에서는 `/ping` 헬스 엔드포인트와 `LocationResolveRequest`·`PlaceDetails`·`SearchRequest` 스키마 계약을 분리했습니다.

**실무 적용 해설**: 확장 플러그인 수가 늘어날수록 모든 플러그인 패키지를 루트 `package.json`에 합치면(AS-IS) 불필요한 의존성 트리가 코어 런타임까지 전파되고 취약점 패치 범위가 커집니다. 플러그인 디렉터리 단위의 `npm install --omit=dev` 독립 설치 모델과 스킬별 Pydantic 입출력 스키마 분리(TO-BE)를 유지하면 코어 빌드와 개별 스킬 서비스의 배포 수명주기를 깔끔하게 끊어낼 수 있습니다. 또한 동일 업스트림 규약이 여러 포크에 그대로 복제되어 유통되는 경향이 있으므로, 파생 저장소 도입 시에는 업스트림 대비 실제 커밋 차이를 먼저 대조해야 합니다.

### 3.2 `.claude/CLAUDE.md`와 `.cursorrules` 간 스택 드리프트 (`gamingopgamingop/sarthak-skill-forge`)

- **출처**: [`gamingopgamingop/sarthak-skill-forge`](https://github.com/gamingopgamingop/sarthak-skill-forge) · **핵심 스택**: `Remix / React / UnoCSS (bolt.diy)`, `Angular / Signals`, `Cloudflare Pages` · **적용 판단**: `Assess`
- **기술 개요**: `.cursorrules`에는 Remix + React + UnoCSS + Cloudflare Pages 기반 `bolt.diy` 풀스택 빌더 스택과 `.env.local` 시크릿 격리가 기술된 반면, `.claude/CLAUDE.md`에는 Angular Standalone 컴포넌트(시그널, `input()`/`output()`, `@HostBinding` 금지, `NgOptimizedImage`) 지침이 담긴 이중 구성 사례입니다.

**실무 적용 해설**: 템플릿 포크나 스킬 모음 저장소에서 과거 프로젝트의 `.claude/CLAUDE.md`와 현재 작업 중인 `.cursorrules`를 정리하지 않고 공존시키면(AS-IS) 사용하는 AI 도구에 따라 전혀 다른 프레임워크 문법(Angular vs React/Remix)으로 코드를 생성하는 혼선이 발생합니다. 실무 저장소에서는 `.cursorrules`의 `.env.local` 비밀키 격리 원칙과 엄격한 `unknown` 타입 강제 규칙은 유지하되(TO-BE), 실제 `package.json` 의존성과 어긋나는 프레임워크 지침 파일을 CI에서 검증해 단일 스택 기준으로 동기화해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `pdfkit`이나 `ezdxf` 등 외부 바이너리·도면 변환 작업은 메인 API에서 분리된 스레드 풀 또는 독립 마이크로서비스로 격리하고 임시 파일 정리를 검증합니다.
  - 여러 에이전트 규약 파일(`.claude/CLAUDE.md`, `.cursorrules`)을 함께 둘 때는 실제 `package.json` 스택과 모순되는 잔여 지침이 없는지 정기 점검합니다.
  - `CLAUDE.md`에 하드코딩된 개인 로컬 경로 대신 저장소 상대 경로를 사용해 팀원과 CI 환경 모두에서 ADR 문서를 참조할 수 있게 합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-09 수집 시점의 `CLAUDE.md`, `.cursorrules`, `app.py`, `main.py` 최대 1,000자 발췌본에 근거합니다. 당일 동일 발췌가 수집된 `openclaw` 파생 3건(`FullStackKevinVanDriel`, `johnakelly-yahoo-com`, `jualiandominguez73-cell/molbook-openclaw`)은 단일 아키텍처 항목으로 통합해 다뤘습니다.
