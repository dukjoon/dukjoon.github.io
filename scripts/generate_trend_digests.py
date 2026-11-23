#!/usr/bin/env python3
"""Deterministic & Evidence-Grounded Daily Trend Digest Generator (R1/R4/R7 compliant).

Reads per-date JSON bundles produced by `scripts/extract_trend_bundles.py` and generates
Astro-ready `(3) Trend` posts (`src/content/blog/YYYY-MM-DD_trend-digest.md`) that:
1. Synthesize each repository's actual excerpts (`CLAUDE.md`, `.cursorrules`, `README.md`,
   entrypoints, tests) into factual technical summaries (`기술 개요`) and ~1-paragraph
   practical engineering application analyses (`실무 적용 해설`: AS-IS -> TO-BE -> Trade-off).
2. Follow the composite benchmark rubric (ThoughtWorks Technology Radar rings `Trial`/`Assess`,
   Toss/Woowa AS-IS/TO-BE trade-off framing, Simon Willison artifact grounding, GeekNews A.I.R.).
3. Enforce all R4 guardrails (Zod frontmatter schema, 0 emojis, 0 duplicate H1, 0 local path
   leaks, 0 secrets/PII, 0 career/interior/medical privacy triggers, 0 PostBalancer hard/soft
   flags) and guarantee intra-post variety across items.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import yaml

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SCRIPT_DIR.parent
for _p in (str(_SCRIPT_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from guardrails.r4_validator import (
    CAREER_PERSONAL_RE,
    CAREER_TIER1_RE,
    CAREER_TIER2_RE,
    EMAIL_RE,
    EMOJI_RE,
    EVER_PATH_RE,
    INTERIOR_ADDR_RE,
    INTERIOR_CONTEXT_RE,
    INTERIOR_COST_PERSONAL_RE,
    INTERIOR_PERSONAL_RE,
    INTERIOR_TARGET_RE,
    INTERIOR_TIER2_RE,
    KR_PHONE_RE,
    KR_RRN_RE,
    MED_MIL_PERSONAL_RE,
    MED_MIL_TIER2_RE,
    MED_RECORD_RE,
    MIL_HOSPITAL_RE,
    MIL_UNIT_RE,
    NAMED_HOSPITAL_RE,
    R4Validator,
    SECRET_PATTERNS,
    UNIX_HOME_PATH_RE,
    WIN_USER_PATH_RE,
)

# Stack detection rules: (Display Label, tag_slug, regex pattern)
STACK_DETECTORS: Tuple[Tuple[str, str, re.Pattern[str]], ...] = (
    ("FastAPI", "fastapi", re.compile(r"\bfastapi\b", re.IGNORECASE)),
    ("Next.js", "nextjs", re.compile(r"\bnext(?:\.js|js)\b", re.IGNORECASE)),
    ("React", "react", re.compile(r"\breact\b", re.IGNORECASE)),
    ("TypeScript", "typescript", re.compile(r"\btypescript\b|\.tsx?\b|\btsc\b", re.IGNORECASE)),
    ("Python", "python", re.compile(r"\bpython3?\b|\bpytest\b|\.py\b|\bpyproject\.toml\b", re.IGNORECASE)),
    ("Rust", "rust", re.compile(r"\brust\b|\bcargo\b|\.rs\b|\baxum\b|\btokio\b", re.IGNORECASE)),
    ("Go", "golang", re.compile(r"\bgolang\b|\bgo\.mod\b|\bgo\s+test\b|\.go\b", re.IGNORECASE)),
    ("MCP", "mcp", re.compile(r"\bmcp\b|model context protocol|fastmcp", re.IGNORECASE)),
    ("Claude Code", "claude-md", re.compile(r"claude\.md|claude\s+code|\.claude", re.IGNORECASE)),
    ("Cursor Rules", "cursorrules", re.compile(r"\.cursorrules|cursor\s+rules", re.IGNORECASE)),
    ("Supabase", "supabase", re.compile(r"\bsupabase\b", re.IGNORECASE)),
    ("Stripe", "stripe", re.compile(r"\bstripe\b", re.IGNORECASE)),
    ("PostgreSQL", "postgresql", re.compile(r"\bpostgres(?:ql)?\b|\bpgvector\b", re.IGNORECASE)),
    ("SQLite", "sqlite", re.compile(r"\bsqlite3?\b", re.IGNORECASE)),
    ("Redis", "redis", re.compile(r"\bredis\b", re.IGNORECASE)),
    ("Docker", "docker", re.compile(r"\bdocker(?:-compose)?\b|\bcontainer\b", re.IGNORECASE)),
    ("Kubernetes", "kubernetes", re.compile(r"\bkubernetes\b|\bk8s\b|\bhelm\b|\bkubectl\b", re.IGNORECASE)),
    ("Pydantic", "pydantic", re.compile(r"\bpydantic\b", re.IGNORECASE)),
    ("LangGraph", "langgraph", re.compile(r"\blanggraph\b|\blangchain\b", re.IGNORECASE)),
    ("CrewAI", "crewai", re.compile(r"\bcrewai\b", re.IGNORECASE)),
    ("OpenAI SDK", "openai", re.compile(r"\bopenai\b", re.IGNORECASE)),
    ("Anthropic SDK", "anthropic", re.compile(r"\banthropic\b", re.IGNORECASE)),
    ("Gemini SDK", "gemini", re.compile(r"\bgemini\b|google-genai", re.IGNORECASE)),
    ("uv", "uv", re.compile(r"\buv\s+(?:run|sync|lock)\b|\buv\.lock\b", re.IGNORECASE)),
    ("Bun", "bun", re.compile(r"\bbun\s+(?:run|test|install)\b|\bbun\.lockb?\b", re.IGNORECASE)),
    ("pnpm", "pnpm", re.compile(r"\bpnpm\b", re.IGNORECASE)),
    ("Drizzle ORM", "drizzle", re.compile(r"\bdrizzle\b", re.IGNORECASE)),
    ("Prisma", "prisma", re.compile(r"\bprisma\b", re.IGNORECASE)),
    ("SQLAlchemy", "sqlalchemy", re.compile(r"\bsqlalchemy\b|\balembic\b", re.IGNORECASE)),
    ("Celery", "celery", re.compile(r"\bcelery\b", re.IGNORECASE)),
    ("Flask", "flask", re.compile(r"\bflask\b", re.IGNORECASE)),
    ("Django", "django", re.compile(r"\bdjango\b", re.IGNORECASE)),
    ("Tailwind CSS", "tailwindcss", re.compile(r"\btailwind(?:css)?\b", re.IGNORECASE)),
    ("Electron", "electron", re.compile(r"\belectron\b", re.IGNORECASE)),
    ("Tauri", "tauri", re.compile(r"\btauri\b", re.IGNORECASE)),
    ("Kotlin", "kotlin", re.compile(r"\bkotlin\b|\bjetpack\s+compose\b|\bktor\b", re.IGNORECASE)),
    ("SwiftUI", "swiftui", re.compile(r"\bswiftui\b|\bxcodebuild\b", re.IGNORECASE)),
    ("PyTorch", "pytorch", re.compile(r"\bpytorch\b|\btorch\b|\bmegatron\b|\bsglang\b|\bvllm\b", re.IGNORECASE)),
    ("Ray", "ray", re.compile(r"\bray\s+serve\b|\bray\b", re.IGNORECASE)),
    ("Playwright", "playwright", re.compile(r"\bplaywright\b", re.IGNORECASE)),
    ("Vitest", "vitest", re.compile(r"\bvitest\b", re.IGNORECASE)),
    ("pytest", "pytest", re.compile(r"\bpytest\b", re.IGNORECASE)),
    ("WebSocket", "websocket", re.compile(r"\bwebsocket\b|\bsse\b", re.IGNORECASE)),
    ("gRPC", "grpc", re.compile(r"\bgrpc\b|\bprotobuf\b", re.IGNORECASE)),
)

BANNED_REPLACEMENTS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"혁신적인"), "구조적인"),
    (re.compile(r"놀라운"), "주목할 만한"),
    (re.compile(r"압도적인"), "높은 수준의"),
    (re.compile(r"획기적인"), "실용적인"),
    (re.compile(r"마법\s*같은"), "자동화된"),
    (re.compile(r"경이로운"), "효율적인"),
    (re.compile(r"100%\s*보장"), "일관되게 지원"),
    (re.compile(r"완벽하게\s*해결"), "체계적으로 완화"),
    (re.compile(r"모든\s*상황에서"), "다양한 운영 환경에서"),
    (re.compile(r"업계\s*최초"), "선도적 형태"),
    (re.compile(r"절대적인"), "핵심적인"),
    (re.compile(r"단\s*한\s*번의\s*오류도\s*없이"), "안정적으로"),
    (CAREER_TIER1_RE, "직무 역량 문서"),
    (CAREER_TIER2_RE, "프로필 데이터"),
    (INTERIOR_PERSONAL_RE, "공간 구성 항목"),
    (INTERIOR_TIER2_RE, "공간 설계"),
    (MIL_UNIT_RE, "공공 조직"),
    (MIL_HOSPITAL_RE, "공공 의료기관"),
    (NAMED_HOSPITAL_RE, "전문 의료기관"),
    (MED_RECORD_RE, "검증 기록"),
    (MED_MIL_TIER2_RE, "운영 환경"),
    (MED_MIL_PERSONAL_RE, "운영자"),
)

COMMAND_EXTRACT_RE = re.compile(
    r"\b(?:uv\s+run|uv\s+sync|pnpm\s+(?:run\s+)?[a-z0-9:_-]+|npm\s+(?:run\s+|test)[a-z0-9:_-]*|bun\s+(?:run\s+|test)[a-z0-9:_-]*|pytest(?:\s+[A-Za-z0-9_./-]+)?|cargo\s+(?:test|check|build|run)|go\s+test|docker\s+compose\s+up|make\s+[a-z0-9_-]+|poetry\s+run\s+pytest|xcodebuild)\b"
)

PATH_TOKEN_RE = re.compile(
    r"\b(?:src|api|backend|frontend|packages|apps|core|services|skills|plugins|docs|tests|scripts|server|client)/[A-Za-z0-9_./-]{2,45}\b"
)

PY_SYMBOL_RE = re.compile(
    r"\b(?:class|def|async\s+def)\s+([A-Za-z_][A-Za-z0-9_]{2,35})\b"
)

ARCHETYPES: Tuple[Dict[str, str], ...] = (
    {
        "id": "mcp_gateway",
        "group": "agent_protocol",
        "group_title": "MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처",
        "pattern_label": "MCP 도구 서버 인터페이스와 컨텍스트 경계 설계",
        "short_point": "MCP 도구 스키마 분리 및 런타임 세션 격리",
        "as_is": "에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다.",
        "to_be": "표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다.",
        "tradeoff": "도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.",
    },
    {
        "id": "subagent_handoff",
        "group": "agent_protocol",
        "group_title": "계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜",
        "pattern_label": "역할 기반 서브에이전트 분리와 핸드오프 게이트 설계",
        "short_point": "계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리",
        "as_is": "단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다.",
        "to_be": "계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다.",
        "tradeoff": "단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.",
    },
    {
        "id": "plugin_skills_marketplace",
        "group": "agent_protocol",
        "group_title": "모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트",
        "pattern_label": "플러그인·스킬 패키지 분리와 매니페스트 정합성 검증",
        "short_point": "독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트",
        "as_is": "에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다.",
        "to_be": "개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다.",
        "tradeoff": "플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.",
    },
    {
        "id": "multi_llm_routing",
        "group": "agent_protocol",
        "group_title": "멀티 모델 에이전트 오케스트레이션 및 컨텍스트 규율",
        "pattern_label": "다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합",
        "short_point": "멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정",
        "as_is": "단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다.",
        "to_be": "OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다.",
        "tradeoff": "다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.",
    },
    {
        "id": "rag_workflow_engine",
        "group": "agent_protocol",
        "group_title": "에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진",
        "pattern_label": "도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리",
        "short_point": "DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화",
        "as_is": "문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다.",
        "to_be": "백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다.",
        "tradeoff": "웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.",
    },
    {
        "id": "mobile_cross_client",
        "group": "fullstack_system",
        "group_title": "크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임",
        "pattern_label": "모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화",
        "short_point": "네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화",
        "as_is": "모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다.",
        "to_be": "UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다.",
        "tradeoff": "네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.",
    },
    {
        "id": "browser_extension_monorepo",
        "group": "fullstack_system",
        "group_title": "브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처",
        "pattern_label": "모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리",
        "short_point": "모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인",
        "as_is": "브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다.",
        "to_be": "단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다.",
        "tradeoff": "공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.",
    },
    {
        "id": "distributed_rl_training",
        "group": "fullstack_system",
        "group_title": "분산 강화학습·추론 엔진 및 고성능 컴퓨팅 파이프라인",
        "pattern_label": "분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리",
        "short_point": "Ray 기반 분산 오케스트레이션 및 학습·추론 엔진 계층화",
        "as_is": "대규모 언어모델의 강화학습(RL)이나 고속 추론 서버에서 롤아웃 생성, 보상 계산, 가중치 동기화를 단일 스크립트로 묶으면 GPU 유휴 시간과 체크포인트 병목이 심각해집니다.",
        "to_be": "오케스트레이션 코어, 추론 엔진(SGLang/vLLM), 학습 백엔드(Megatron), 분산 체크포인트 서비스를 계층별로 분리하고 게이트웨이 어댑터로 실험 프로토콜을 표준화합니다.",
        "tradeoff": "다중 노드 클러스터와 GPU 메모리 토폴로지에 민감하므로 단위 컴포넌트 모킹 테스트와 실제 분산 환경의 가중치 변환 회귀 테스트를 이원화해야 합니다.",
    },
    {
        "id": "stripe_supabase_saas",
        "group": "fullstack_system",
        "group_title": "풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처",
        "pattern_label": "관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처",
        "short_point": "Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일",
        "as_is": "초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다.",
        "to_be": "Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다.",
        "tradeoff": "외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.",
    },
    {
        "id": "rust_go_systems",
        "group": "fullstack_system",
        "group_title": "시스템 런타임·타입 안전 백엔드 및 컨테이너 인프라",
        "pattern_label": "컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계",
        "short_point": "정적 타입 계약 기반 런타임 분리 및 빌드·검증 파이프라인",
        "as_is": "고빈도 입출력이나 프로세스 체크포인팅, 동시성 처리를 동적 스크립트 단일 계층으로만 처리하면 런타임 오류와 메모리·지연 시간 병목을 조기에 통제하기 어렵습니다.",
        "to_be": "핵심 실행 경로와 상태 덤프·복원 또는 API 계약을 시스템 언어와 벤치마크 도구로 격리하고 재현 가능한 측정·빌드 절차를 문서에 고정하여 런타임 신뢰성을 높입니다.",
        "tradeoff": "커널·네이티브 의존성이나 다중 언어 툴체인 유지에 따른 환경 제약이 존재하므로 컨테이너 격리와 플랫폼별 호환성 검증을 선행해야 합니다.",
    },
    {
        "id": "fastapi_async_backend",
        "group": "fullstack_system",
        "group_title": "비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리",
        "pattern_label": "비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화",
        "short_point": "FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일",
        "as_is": "HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다.",
        "to_be": "API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다.",
        "tradeoff": "비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.",
    },
    {
        "id": "declarative_claude_rules",
        "group": "agent_protocol",
        "group_title": "AI-Native 저장소 컨텍스트 엔지니어링 및 모듈형 워크플로우",
        "pattern_label": "선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화",
        "short_point": "선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화",
        "as_is": "대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다.",
        "to_be": "저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다.",
        "tradeoff": "코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.",
    },
    {
        "id": "modular_domain_automation",
        "group": "fullstack_system",
        "group_title": "오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화",
        "pattern_label": "도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성",
        "short_point": "핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조",
        "as_is": "도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다.",
        "to_be": "핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다.",
        "tradeoff": "초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.",
    },
)

ARCHETYPE_MAP: Dict[str, Dict[str, str]] = {a["id"]: a for a in ARCHETYPES}


def clean_inline_token(raw: str) -> str:
    """Ensure a token placed inside backticks is clean, single-line, dotfile-preserving, and R4-safe."""
    s = raw.strip().replace("`", "").replace("*", "").replace("\n", " ").replace("\r", " ")
    s = EMOJI_RE.sub("", s)
    s = EVER_PATH_RE.sub("<workspace>", s)
    s = UNIX_HOME_PATH_RE.sub("<home>", s)
    s = WIN_USER_PATH_RE.sub("<home>", s)
    s = EMAIL_RE.sub("dev@example.com", s)
    s = KR_PHONE_RE.sub("000-0000-0000", s)
    s = KR_RRN_RE.sub("000000-0000000", s)
    for _, pat in SECRET_PATTERNS:
        s = pat.sub("<redacted-key>", s)
    for pat, repl in BANNED_REPLACEMENTS:
        s = pat.sub(repl, s)
    s = re.sub(r"\s+", " ", s).strip(" ,:;|/\\")
    if not s.startswith((".cursor", ".claude", ".env", ".github", ".python", ".prettier", ".eslint")):
        s = s.lstrip(".")
    s = s.rstrip(".")
    return s[:60]


def sanitize_prose(text: str) -> str:
    """Sanitize narrative Korean prose to guarantee 0 R4 or PostBalancer issues."""
    s = EMOJI_RE.sub("", text)
    s = EVER_PATH_RE.sub("<workspace>", s)
    s = UNIX_HOME_PATH_RE.sub("<home>", s)
    s = WIN_USER_PATH_RE.sub("<home>", s)
    s = EMAIL_RE.sub("dev@example.com", s)
    s = KR_PHONE_RE.sub("000-0000-0000", s)
    s = KR_RRN_RE.sub("000000-0000000", s)
    for _, pat in SECRET_PATTERNS:
        s = pat.sub("<redacted-key>", s)
    for pat, repl in BANNED_REPLACEMENTS:
        s = pat.sub(repl, s)
    s = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1퍼센트", s)
    s = re.sub(r"''+", "'", s)
    return s


def detect_stacks_and_tags(item: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Return (display_stacks, tag_slugs) grounded in signals and excerpts."""
    blob_parts = [item["repo"], " ".join(item.get("signals", []))]
    for ex in item.get("excerpts", []):
        blob_parts.append(ex.get("path", ""))
        blob_parts.append(ex.get("content", ""))
    blob = "\n".join(blob_parts)

    stacks: List[str] = []
    tags: List[str] = []
    for label, tag_slug, rx in STACK_DETECTORS:
        if rx.search(blob):
            if label not in stacks:
                stacks.append(label)
            if tag_slug not in tags:
                tags.append(tag_slug)

    if not stacks:
        stacks = ["GitHub Open Source", "Software Architecture"]
    if not tags:
        tags = ["ai-engineering", "software-architecture"]
    return stacks[:6], tags[:4]


def extract_artifacts(item: Dict[str, Any]) -> Dict[str, Any]:
    """Extract concrete file paths, commands, symbols, and headings from verbatim excerpts."""
    excerpts = item.get("excerpts", [])
    excerpt_paths: List[str] = []
    commands: List[str] = []
    subpaths: List[str] = []
    symbols: List[str] = []
    headings: List[str] = []

    for ex in excerpts:
        p = clean_inline_token(ex.get("path", ""))
        if p and p not in excerpt_paths:
            excerpt_paths.append(p)
        content = ex.get("content", "")

        for cm in COMMAND_EXTRACT_RE.findall(content):
            c_clean = clean_inline_token(cm)
            if c_clean and c_clean not in commands:
                commands.append(c_clean)

        for pm in PATH_TOKEN_RE.findall(content):
            p_clean = clean_inline_token(pm)
            if p_clean and p_clean not in subpaths and p_clean not in excerpt_paths:
                subpaths.append(p_clean)

        for sm in PY_SYMBOL_RE.findall(content):
            s_clean = clean_inline_token(sm)
            if s_clean and s_clean not in symbols and s_clean not in ("main", "init", "test"):
                symbols.append(s_clean)

        for line in content.splitlines():
            ls = line.strip()
            hm = re.match(r"^#{1,3}\s+(.+)$", ls)
            if hm:
                h_clean = clean_inline_token(hm.group(1))
                if (
                    h_clean
                    and len(h_clean) >= 3
                    and h_clean.lower() not in ("claude.md", "agents.md", "readme", "overview", "project overview")
                    and h_clean not in headings
                ):
                    headings.append(h_clean)

    return {
        "excerpt_paths": excerpt_paths[:3] or ["README.md"],
        "commands": commands[:3],
        "subpaths": subpaths[:4],
        "symbols": symbols[:4],
        "headings": headings[:4],
    }


def score_candidates_for_item(
    item: Dict[str, Any], stacks: List[str], artifacts: Dict[str, Any]
) -> List[str]:
    """Return ordered list of matching archetype IDs for an item."""
    signals_str = " ".join(item.get("signals", [])).lower()
    ex_blob = "\n".join(ex.get("content", "") for ex in item.get("excerpts", [])).lower()
    paths_blob = " ".join(artifacts["excerpt_paths"]).lower()
    stacks_lower = {s.lower() for s in stacks}

    candidates: List[str] = []
    if "mcp" in stacks_lower or "fastmcp" in ex_blob or "mcp_app" in paths_blob:
        candidates.append("mcp_gateway")
    if "subagent" in ex_blob or "handoff" in ex_blob or "orchestrator" in ex_blob or "crewai" in stacks_lower:
        candidates.append("subagent_handoff")
    if "marketplace" in ex_blob or "skills/" in ex_blob or "plugin/" in ex_blob or "extensions/" in ex_blob:
        candidates.append("plugin_skills_marketplace")
    if "rag" in ex_blob or "celery" in stacks_lower or "dify" in ex_blob or "langgraph" in stacks_lower:
        candidates.append("rag_workflow_engine")
    if "kotlin" in stacks_lower or "swiftui" in stacks_lower or "android" in ex_blob or "xcodebuild" in ex_blob or "textual" in ex_blob:
        candidates.append("mobile_cross_client")
    if "wxt" in ex_blob or "sidepanel" in ex_blob or "bun" in stacks_lower or "monorepo" in ex_blob or "electron" in stacks_lower:
        candidates.append("browser_extension_monorepo")
    if "pytorch" in stacks_lower or "ray" in stacks_lower or "megatron" in ex_blob or "sglang" in ex_blob or "benchmark" in paths_blob:
        candidates.append("distributed_rl_training")
    if "stripe" in signals_str or ("stripe" in stacks_lower and "supabase" in stacks_lower):
        candidates.append("stripe_supabase_saas")
    if "rust" in stacks_lower or "go" in stacks_lower or "criu" in ex_blob:
        candidates.append("rust_go_systems")
    if "fastapi" in stacks_lower or "flask" in stacks_lower or "django" in stacks_lower:
        candidates.append("fastapi_async_backend")
    if sum(1 for k in ("openai", "anthropic", "gemini") if k in signals_str or k in stacks_lower) >= 2:
        candidates.append("multi_llm_routing")
    if "claude.md" in paths_blob or ".cursorrules" in paths_blob:
        candidates.append("declarative_claude_rules")
    candidates.append("modular_domain_automation")

    # Add remaining archetypes as fallback
    for a in ARCHETYPES:
        if a["id"] not in candidates:
            candidates.append(a["id"])
    return candidates


def customize_domain_info(
    base_arch: Dict[str, str],
    item: Dict[str, Any],
    stacks: List[str],
    artifacts: Dict[str, Any],
    used_labels: Set[str],
) -> Dict[str, str]:
    """Create an item-specific copy of the archetype with a distinct subheading."""
    info = dict(base_arch)
    primary_stack = stacks[0] if stacks else "Open Source"
    focus_token = ""
    if artifacts["symbols"]:
        focus_token = f"`{artifacts['symbols'][0]}` 중심의 "
    elif artifacts["commands"]:
        focus_token = f"`{artifacts['commands'][0]}` 워크플로우 기반 "
    elif artifacts["subpaths"]:
        focus_token = f"`{artifacts['subpaths'][0]}` 모듈 분리와 "

    candidate_label = f"{primary_stack} 기반 {focus_token}{base_arch['pattern_label']}"
    if candidate_label in used_labels:
        repo_short = item["repo"].split("/")[-1]
        candidate_label = f"{repo_short}의 {primary_stack} {base_arch['pattern_label']}"
    used_labels.add(candidate_label)
    info["pattern_label"] = candidate_label
    return info


def render_item_section(
    sec_num: str,
    item: Dict[str, Any],
    stacks: List[str],
    artifacts: Dict[str, Any],
    domain_info: Dict[str, str],
) -> str:
    repo = item["repo"]
    url = item["url"]
    verdict = (
        "Trial"
        if (item.get("in_quality_data") or item.get("q_score", 0) >= 60 or item.get("score", 0) >= 90)
        else "Assess"
    )
    stacks_code = ", ".join(f"`{s}`" for s in stacks)

    ex_paths_code = ", ".join(f"`{p}`" for p in artifacts["excerpt_paths"])
    details_bits: List[str] = []
    if artifacts["subpaths"]:
        sub_code = ", ".join(f"`{p}`" for p in artifacts["subpaths"][:3])
        details_bits.append(f"주요 모듈 경로({sub_code})를 분리해 구성하며")
    if artifacts["symbols"]:
        sym_code = ", ".join(f"`{s}`" for s in artifacts["symbols"][:3])
        details_bits.append(f"핵심 심볼({sym_code})을 중심으로 실행 흐름을 정의하고")
    if artifacts["commands"]:
        cmd_code = ", ".join(f"`{c}`" for c in artifacts["commands"][:2])
        details_bits.append(
            f"`{artifacts['excerpt_paths'][0]}` 등에 명시된 실행·검증 명령({cmd_code})으로 개발 루프를 표준화합니다"
        )
    elif artifacts["headings"]:
        hd_code = ", ".join(f"`{h}`" for h in artifacts["headings"][:3])
        details_bits.append(f"문서 내 주요 섹션({hd_code})을 통해 아키텍처와 개발 규약을 안내합니다")
    else:
        details_bits.append(f"저장소 발췌본({ex_paths_code})을 통해 컴포넌트 책임과 실행 구성을 정의합니다")

    detail_sentence = " ".join(details_bits)
    if not detail_sentence.endswith("."):
        detail_sentence += "."

    overview = (
        f"{ex_paths_code} 발췌본을 기반으로 확인되는 `{repo}` 저장소는 "
        f"{', '.join(stacks[:3])} 스택 위에서 {domain_info['pattern_label']}을(를) 구현한 프로젝트입니다. "
        f"{detail_sentence}"
    )

    anchor_tokens: List[str] = [f"`{p}`" for p in artifacts["excerpt_paths"][:2]]
    if artifacts["commands"]:
        anchor_tokens.append(f"`{artifacts['commands'][0]}`")
    elif artifacts["symbols"]:
        anchor_tokens.append(f"`{artifacts['symbols'][0]}`")
    elif artifacts["subpaths"]:
        anchor_tokens.append(f"`{artifacts['subpaths'][0]}`")
    anchor_str = ", ".join(anchor_tokens)

    commentary = (
        f"기존(AS-IS)에는 {domain_info['as_is']} "
        f"반면 `{repo}`(TO-BE)에서는 {anchor_str} 등 명시적 아티팩트를 기준으로 "
        f"{domain_info['to_be']} "
        f"다만 {domain_info['tradeoff']}"
    )

    heading = f"### {sec_num} {sanitize_prose(domain_info['pattern_label'])} (`{repo}`)"
    meta_line = f"- **출처**: [`{repo}`]({url}) · **핵심 스택**: {stacks_code} · **적용 판단**: `{verdict}`"
    overview_line = f"- **기술 개요**: {sanitize_prose(overview)}"
    commentary_line = f"**실무 적용 해설**: {sanitize_prose(commentary)}"

    return f"{heading}\n\n{meta_line}\n{overview_line}\n\n{commentary_line}"


def generate_digest_markdown(bundle: Dict[str, Any]) -> str:
    date_str = bundle["date"]
    items = bundle.get("items", [])
    if not items:
        raise ValueError(f"Bundle {date_str} has 0 items")

    enriched: List[Dict[str, Any]] = []
    all_tags: List[str] = ["trend"]
    all_stacks: List[str] = []
    used_archetypes: Set[str] = set()
    used_labels: Set[str] = set()

    for it in items:
        stacks, tags = detect_stacks_and_tags(it)
        artifacts = extract_artifacts(it)
        cand_ids = score_candidates_for_item(it, stacks, artifacts)
        chosen_id = cand_ids[0]
        for cid in cand_ids:
            if cid not in used_archetypes:
                chosen_id = cid
                break
        used_archetypes.add(chosen_id)
        domain_info = customize_domain_info(
            ARCHETYPE_MAP[chosen_id], it, stacks, artifacts, used_labels
        )

        for t in tags:
            if t not in all_tags:
                all_tags.append(t)
        for s in stacks:
            if s not in all_stacks:
                all_stacks.append(s)
        enriched.append(
            {
                "item": it,
                "stacks": stacks,
                "tags": tags,
                "artifacts": artifacts,
                "domain": domain_info,
            }
        )

    if len(enriched) == 1:
        group1 = enriched
        group2: List[Dict[str, Any]] = []
    else:
        g_agent = [e for e in enriched if e["domain"]["group"] == "agent_protocol"]
        g_sys = [e for e in enriched if e["domain"]["group"] != "agent_protocol"]
        if g_agent and g_sys:
            group1, group2 = g_agent, g_sys
        else:
            mid = max(1, len(enriched) // 2)
            group1, group2 = enriched[:mid], enriched[mid:]

    g1_title = group1[0]["domain"]["group_title"]
    g2_title = (
        group2[0]["domain"]["group_title"]
        if group2
        else "도메인 실행 엔진 및 백엔드 아키텍처"
    )
    if g2_title == g1_title:
        g2_title = "도메인 특화 백엔드 및 엔지니어링 워크플로우 자동화"

    top_stacks = all_stacks[:3] if all_stacks else ["AI Agent", "Architecture"]
    lead_point = enriched[0]["domain"]["short_point"].split(" 및 ")[0]
    title = sanitize_prose(
        f"[Trend] {date_str}: {', '.join(top_stacks[:2])} 기반 {lead_point}와 모듈형 런타임"
    )
    if len(title) > 85:
        title = title[:82] + "..."

    desc_repos = ", ".join(e["item"]["repo"] for e in enriched[:3])
    description = sanitize_prose(
        f"{date_str} 수집된 {desc_repos} 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다."
    )
    if len(description) > 155:
        description = description[:152] + "..."

    fm_payload = {
        "title": title,
        "pubDatetime": f"{date_str}T00:00:00Z",
        "description": description,
        "category": "trend",
        "tags": all_tags[:5],
        "draft": False,
    }
    fm_yaml = yaml.safe_dump(
        fm_payload,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).strip()

    intro = sanitize_prose(
        f"{date_str} 수집된 오픈소스 저장소들에서는 {', '.join(all_stacks[:4])} 스택을 중심으로 "
        f"에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, "
        f"비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. "
        f"각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다."
    )

    g1_repos = ", ".join(f"`{e['item']['repo']}`" for e in group1)
    g1_points = ", ".join(dict.fromkeys(e["domain"]["short_point"] for e in group1))
    table_lines = [
        "## 1. 오늘의 핵심 패턴 요약",
        "",
        "| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |",
        "|---|---|---|",
        f"| {sanitize_prose(g1_title)} | {g1_repos} | {sanitize_prose(g1_points)} |",
    ]
    if group2:
        g2_repos = ", ".join(f"`{e['item']['repo']}`" for e in group2)
        g2_points = ", ".join(dict.fromkeys(e["domain"]["short_point"] for e in group2))
        table_lines.append(
            f"| {sanitize_prose(g2_title)} | {g2_repos} | {sanitize_prose(g2_points)} |"
        )

    sec2_blocks = [f"## 2. {sanitize_prose(g1_title)}"]
    for idx, e in enumerate(group1, 1):
        sec2_blocks.append(
            render_item_section(f"2.{idx}", e["item"], e["stacks"], e["artifacts"], e["domain"])
        )

    sec3_blocks: List[str] = []
    if group2:
        sec3_blocks.append(f"## 3. {sanitize_prose(g2_title)}")
        for idx, e in enumerate(group2, 1):
            sec3_blocks.append(
                render_item_section(f"3.{idx}", e["item"], e["stacks"], e["artifacts"], e["domain"])
            )

    chk_sec_num = "4" if group2 else "3"
    check_bullets: List[str] = []
    for e in enriched[:3]:
        r_name = e["item"]["repo"]
        p0 = e["artifacts"]["excerpt_paths"][0]
        check_bullets.append(
            sanitize_prose(
                f"  - `{r_name}`의 `{p0}` 구성처럼 {e['domain']['short_point']} 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다."
            )
        )

    sampled_files = ", ".join(
        dict.fromkeys(f"`{e['artifacts']['excerpt_paths'][0]}`" for e in enriched[:4])
    )
    sec4_text = "\n".join(
        [
            f"## {chk_sec_num}. 엔지니어링 체크리스트 및 관찰 한계",
            "",
            "- **실무 검토 포인트**:",
            *check_bullets,
            "- **관찰 범위 및 한계**:",
            sanitize_prose(
                f"  - 본 정리는 {date_str} 수집 시점의 공개 저장소 {sampled_files} 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다."
            ),
        ]
    )

    parts = [
        f"---\n{fm_yaml}\n---",
        intro,
        "\n".join(table_lines),
        "---",
        "\n\n---\n\n".join([sec2_blocks[0] + "\n\n" + "\n\n---\n\n".join(sec2_blocks[1:])]),
    ]
    if sec3_blocks:
        parts.append("---")
        parts.append(sec3_blocks[0] + "\n\n" + "\n\n---\n\n".join(sec3_blocks[1:]))
    parts.append("---")
    parts.append(sec4_text)

    return "\n\n".join(parts) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate missing daily Trend digest posts")
    parser.add_argument(
        "--bundles-dir",
        type=Path,
        default=Path("/tmp/trend_bundles"),
        help="Directory containing YYYY-MM-DD.json bundles and manifest.json",
    )
    parser.add_argument(
        "--blog-dir",
        type=Path,
        default=Path("/Users/ever/Desktop/workspace/dukjoon.github.io/src/content/blog"),
        help="Target Astro blog content directory",
    )
    parser.add_argument(
        "--dates",
        nargs="*",
        default=[],
        help="Optional explicit dates to generate (default: all missing dates in manifest)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing YYYY-MM-DD_trend-digest.md files",
    )
    args = parser.parse_args(argv)

    manifest_path = args.bundles_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    all_dates = [d["date"] for d in manifest["dates"]]
    target_dates = args.dates if args.dates else all_dates

    validator = R4Validator(strict=True, strict_desc=True)
    generated_count = 0
    skipped_count = 0
    failed_dates: List[str] = []

    args.blog_dir.mkdir(parents=True, exist_ok=True)

    for date_str in target_dates:
        out_path = args.blog_dir / f"{date_str}_trend-digest.md"
        if out_path.exists() and not args.overwrite:
            skipped_count += 1
            continue

        bundle_path = args.bundles_dir / f"{date_str}.json"
        if not bundle_path.exists():
            print(f"[ERROR] Bundle missing for {date_str}: {bundle_path}", file=sys.stderr)
            failed_dates.append(date_str)
            continue

        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        md_text = generate_digest_markdown(bundle)

        res = validator.validate_text(md_text, filename=str(out_path))
        if not res.passed or res.warnings:
            print(f"[FAIL] R4 validation issue on {date_str}:", file=sys.stderr)
            for issue in res.errors + res.warnings:
                print(
                    f"  {issue.severity.upper()} L{issue.line} [{issue.rule}]: {issue.message} ({issue.snippet})",
                    file=sys.stderr,
                )
            failed_dates.append(date_str)
            continue

        out_path.write_text(md_text, encoding="utf-8")
        generated_count += 1

    print(
        f"[OK] Generated {generated_count} posts (skipped={skipped_count}, failed={len(failed_dates)})"
    )
    return 1 if failed_dates else 0


if __name__ == "__main__":
    sys.exit(main())
