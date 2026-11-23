#!/usr/bin/env python3
"""Deterministic R4 Validator for Astro Blog Posts (schema, formatting, secrets, PII, R4 privacy).

Validates markdown posts against:
1. dukjoon.github.io Astro Zod Content Collection schema + R2 empty `(5) Study` guard
2. Guardrail hard/soft tags ([검수필요], [문체점검], [추정])
3. Markdown formatting defects (duplicate H1, emojis outside code, unbalanced ** bolding, '' auto-trim remnants)
4. Local machine path leaks (/Users/..., /home/..., C:\\Users\\...)
5. Secrets / API keys / private keys (length-bounded to avoid false positives like risk-fingerprinting)
6. PII (emails, Korean phone numbers, Korean RRNs)
7. Context-aware R4 domain privacy heuristics (career/resume, interior/remodeling, medical/military)
8. Optional PostBalancer(channel="git") integration
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date, datetime
import glob
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
import yaml

_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from guardrails.post_balancer import PostBalancer

CANONICAL_CATEGORIES: Tuple[str, ...] = (
    "ai-engineering",
    "system",
    "trend",
    "law",
    "study",
)

DEFAULT_ALLOWED_EMAIL_DOMAINS: Set[str] = {
    "example.com",
    "example.org",
    "test.com",
    "localhost",
    "users.noreply.github.com",
}

DEFAULT_ALLOWED_PATH_USERS: Set[str] = {
    "user",
    "username",
    "ubuntu",
    "runner",
    "app",
    "developer",
    "your-name",
    "<user>",
}

EMOJI_RE = re.compile(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]", flags=re.UNICODE)
ISO_DATE_STR_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$"
)
ALLOWLIST_COMMENT_RE = re.compile(r"<!--\s*r4-allow:\s*([A-Za-z0-9_,-]+)\s*-->")

SECRET_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("OpenAI/Anthropic/Stripe key", re.compile(r"\bsk-(?:proj-|ant-|live-|test-)?[A-Za-z0-9_\-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b")),
    ("Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}=*")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    (
        "Hardcoded credential assignment",
        re.compile(
            r"(?i)(?:api_key|secret_key|access_token|auth_token|password)\s*[:=]\s*['\"][A-Za-z0-9\-._~+/]{16,}['\"]"
        ),
    ),
)

SECRET_PLACEHOLDER_MARKERS = (
    "your_token",
    "your_api_key",
    "your-",
    "placeholder",
    "dummy",
    "fake_",
    "xxxx",
    "1234567890abcd",
    "ghp_test",
    "sk_test_",
    "example_token",
    "example_key",
)

SECRET_PLACEHOLDER_EXACT_CASE_MARKERS = (
    "YOUR_",
    "DUMMY_",
    "EXAMPLE_",
)

EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
KR_PHONE_RE = re.compile(
    r"(?<![\d.])(?:01[016789]-\d{3,4}-\d{4}|01[016789]\d{8}|(?:02|0[3-6][1-5]|070)-\d{3,4}-\d{4})(?![\d.])"
)
KR_RRN_RE = re.compile(r"(?<!\d)\d{6}-[1-4]\d{6}(?!\d)")

EVER_PATH_RE = re.compile(r"/Users/ever(?:/[^\s`'\"\)\]>]*)?")
UNIX_HOME_PATH_RE = re.compile(r"(?<!://)(?:/Users/|/home/)([A-Za-z0-9._-]+)(?:/[^\s`'\"\)\]>]*)?")
WIN_USER_PATH_RE = re.compile(r"[A-Za-z]:\\Users\\([A-Za-z0-9._-]+)(?:\\[^\s`'\"\)\]>]*)?")

CAREER_TIER1_RE = re.compile(
    r"자소서|자기소개서|지원동기|이직\s*사유|희망\s*연봉|직전\s*연봉|현재\s*연봉|연봉\s*협상|경력기술서|서류\s*합격|서류\s*탈락|최종\s*합격|면접\s*후기"
)
CAREER_TIER2_RE = re.compile(r"이력서|지원서|연봉")
CAREER_SW_RE = re.compile(r"파싱|계산기|추정|공공데이터|SaaS|API|매칭|오픈소스|저장소")
CAREER_PERSONAL_RE = re.compile(
    r"제가|저는|나의"
    r"|(?:^|(?<=\s))내\s+(?:이력|자소서|지원|연봉|경력|포트폴리오|소개|경험|생각|개인|집|계좌|주소|이메일|전화|비밀번호|토큰)"
    r"|입사\s*지원|회사에?\s*지원|서류\s*지원|직접\s*지원한"
    r"|합격|불합격|본인"
)

INTERIOR_ADDR_RE = re.compile(
    r"[가-힣]+(?:구|시|동)\s+[가-힣0-9]+(?:아파트|빌라|오피스텔|단지|\d+동\s*\d+호)"
)
INTERIOR_CONTEXT_RE = re.compile(r"인테리어|리모델링|시공|견적")
INTERIOR_PERSONAL_RE = re.compile(r"우리\s*집|내\s*집|시공\s*중|계약금|중도금|잔금|실장님|도배|샷시|목공")
INTERIOR_TARGET_RE = re.compile(r"인테리어|리모델링|견적서|시공사")
INTERIOR_TIER2_RE = re.compile(r"인테리어|리모델링|시공업체|실측|공사\s*일정")
INTERIOR_SW_RE = re.compile(
    r"포트폴리오|웹앱|SaaS|분석|시스템|컴포넌트|매칭|오픈소스|저장소"
    r"|아키텍처|도구|라이브러리|프로젝트|앱|API|플랫폼|자동화|파이프라인|모델|설계|구현|서비스|클라이언트|서버"
)
INTERIOR_COST_PERSONAL_RE = re.compile(r"우리\s*집|내\s*집|제가|저는|견적서|계약금|중도금|잔금|실장님")

MIL_UNIT_RE = re.compile(
    r"(?<!\d)\d{1,3}(?:사단|여단|연대|대대|중대|소대|분대|비행단|전대|전단|함대|군단|훈련소)"
)
MIL_HOSPITAL_RE = re.compile(r"국군[가-힣]+병원|군번|병적증명서|현역복무부적합")
NAMED_HOSPITAL_RE = re.compile(
    r"(?:서울대|연세세브란스|세브란스|삼성서울|서울아산|아산|가톨릭성모|성모|고려대|경희대|한양대|중앙대|분당서울대|보라매|국립중앙의료원)[가-힣]*병원"
)
MED_RECORD_RE = re.compile(
    r"진단서|소견서|의무기록|수술\s*기록|입원\s*기간|퇴원일|상병코드|장해등급|상이등급"
)
MED_MIL_TIER2_RE = re.compile(r"환자|병원|입원|수술|응급실|군복무|국가배상|보훈")
MED_MIL_PERSONAL_RE = re.compile(r"본인|제가|저는|입원했|수술했|사고\s*당시|진료받|다쳐서|군\s*병원")

GITHUB_URL_RE = re.compile(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


@dataclass
class ValidationIssue:
    rule: str
    severity: str  # "error" or "warning"
    line: int
    message: str
    snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "line": self.line,
            "message": self.message,
            "snippet": self.snippet,
        }


@dataclass
class FileValidationResult:
    path: str
    passed: bool
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    category: Optional[str] = None
    allowlisted: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "path": self.path,
            "passed": self.passed,
            "category": self.category,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }
        if self.allowlisted:
            payload["info"] = self.allowlisted
        return payload


def _mask_inline_code_in_line(line: str) -> str:
    """Replace inline code spans (`...` or ``...``) with spaces, preserving line length."""
    result: List[str] = []
    i = 0
    n = len(line)
    while i < n:
        if line[i] == "`":
            tick_end = i
            while tick_end < n and line[tick_end] == "`":
                tick_end += 1
            tick_len = tick_end - i
            close_marker = "`" * tick_len
            close_idx = line.find(close_marker, tick_end)
            while close_idx != -1:
                after = close_idx + tick_len
                if after < n and line[after] == "`":
                    # longer run, advance past it
                    while after < n and line[after] == "`":
                        after += 1
                    close_idx = line.find(close_marker, after)
                    continue
                break
            if close_idx != -1:
                span_len = (close_idx + tick_len) - i
                result.append(" " * span_len)
                i = close_idx + tick_len
                continue
        result.append(line[i])
        i += 1
    return "".join(result)


def mask_code_preserving_lines(text: str) -> str:
    """Mask fenced code blocks and inline code while preserving exact 1-based line numbers."""
    lines = text.splitlines()
    masked_lines: List[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for raw_line in lines:
        stripped = raw_line.lstrip()
        if not in_fence:
            m = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
            if m:
                marker = m.group(1)
                rest = m.group(2)
                # Single-line backtick fence edge case? CommonMark: backtick info string cannot contain backticks
                if marker[0] == "`" and "`" in rest:
                    masked_lines.append(_mask_inline_code_in_line(raw_line))
                else:
                    in_fence = True
                    fence_char = marker[0]
                    fence_len = len(marker)
                    masked_lines.append("")
                continue
            masked_lines.append(_mask_inline_code_in_line(raw_line))
        else:
            close_m = re.match(rf"^({re.escape(fence_char)}{{{fence_len},}})\s*$", stripped)
            if close_m:
                in_fence = False
                fence_char = ""
                fence_len = 0
            masked_lines.append("")

    if text.endswith("\n"):
        return "\n".join(masked_lines) + "\n"
    return "\n".join(masked_lines)


def split_frontmatter(text: str) -> Tuple[Optional[str], str, int]:
    """Return (yaml_text_or_None, body_text, body_start_line_1_based)."""
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n([\s\S]*))?$", text)
    if m:
        yaml_text = m.group(1)
        body = m.group(2) if m.group(2) is not None else ""
        # Count newlines before group(2) start (or before end of match if group(2) is None)
        prefix = text[: m.start(2)] if m.group(2) is not None else text[: m.end()]
        body_start_line = prefix.count("\n") + 1
        return yaml_text, body, body_start_line

    empty_m = re.match(r"^---\r?\n---(?:\r?\n([\s\S]*))?$", text)
    if empty_m:
        body = empty_m.group(1) if empty_m.group(1) is not None else ""
        prefix = text[: empty_m.start(1)] if empty_m.group(1) is not None else text[: empty_m.end()]
        return "", body, prefix.count("\n") + 1

    return None, text, 1


class R4Validator:
    def __init__(
        self,
        policy_path: Optional[Path] = None,
        allow_study: bool = False,
        strict: bool = False,
        strict_desc: bool = False,
        use_balancer: bool = True,
        check_schema: bool = True,
    ):
        if policy_path is None:
            policy_path = Path(__file__).resolve().parent / "policy.yaml"
        self.policy_path = Path(policy_path)
        self.allow_study = allow_study
        self.strict = strict
        self.strict_desc = strict_desc
        self.use_balancer = use_balancer
        self.check_schema = check_schema

        self.policy = self._load_policy()
        r4_cfg = self.policy.get("r4_privacy", {}) if isinstance(self.policy, dict) else {}
        self.allowed_email_domains: Set[str] = DEFAULT_ALLOWED_EMAIL_DOMAINS | {
            str(d).strip().lower() for d in r4_cfg.get("allowed_email_domains", []) if str(d).strip()
        }
        self.allowed_path_users: Set[str] = DEFAULT_ALLOWED_PATH_USERS | {
            str(u).strip() for u in r4_cfg.get("allowed_path_users", []) if str(u).strip()
        }
        self.allowed_path_users.discard("ever")
        self.extra_blocked_terms: List[str] = [
            str(t).strip() for t in r4_cfg.get("extra_blocked_terms", []) if str(t).strip()
        ]

        self.balancer: Optional[PostBalancer] = None
        if self.use_balancer:
            self.balancer = PostBalancer(policy_path=self.policy_path)

    def _load_policy(self) -> Dict[str, Any]:
        if not self.policy_path.exists():
            return {}
        try:
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    @staticmethod
    def _parse_allowlists(lines: List[str]) -> Dict[int, Set[str]]:
        """Map 1-based line number -> set of allowlisted rule IDs from same or previous line."""
        allow_map: Dict[int, Set[str]] = {}
        for idx, line in enumerate(lines, 1):
            for m in ALLOWLIST_COMMENT_RE.finditer(line):
                rules = {r.strip() for r in m.group(1).split(",") if r.strip()}
                allow_map.setdefault(idx, set()).update(rules)
                allow_map.setdefault(idx + 1, set()).update(rules)
        return allow_map

    @staticmethod
    def _coerce_pub_datetime_date(val: Any) -> Optional[str]:
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d")
        if isinstance(val, date):
            return val.strftime("%Y-%m-%d")
        if isinstance(val, str):
            s = val.strip()
            if not ISO_DATE_STR_RE.match(s):
                return None
            try:
                if "T" in s:
                    datetime.fromisoformat(s.replace("Z", "+00:00"))
                else:
                    date.fromisoformat(s)
                return s[:10]
            except ValueError:
                return None
        return None

    @staticmethod
    def _split_sections(lines: List[str], start_line: int) -> List[Tuple[int, List[Tuple[int, str]]]]:
        """Split body lines into heading-bounded sections (## or ###) preserving 1-based line numbers."""
        sections: List[Tuple[int, List[Tuple[int, str]]]] = []
        current: List[Tuple[int, str]] = []
        section_start = start_line

        for offset, line in enumerate(lines):
            lineno = start_line + offset
            if re.match(r"^#{2,3}\s+", line):
                if current:
                    sections.append((section_start, current))
                section_start = lineno
                current = [(lineno, line)]
            else:
                current.append((lineno, line))
        if current:
            sections.append((section_start, current))
        return sections

    def _add_issue(
        self,
        errors: List[ValidationIssue],
        warnings: List[ValidationIssue],
        allowlisted: List[Dict[str, Any]],
        allow_map: Dict[int, Set[str]],
        rule: str,
        severity: str,
        line: int,
        message: str,
        snippet: str = "",
    ) -> None:
        if rule in allow_map.get(line, set()):
            allowlisted.append({"rule": rule, "line": line, "message": message})
            return
        eff_sev = "error" if (severity == "warning" and self.strict and rule in ("schema_filename_date_mismatch", "guardrail_uncleaned_soft_tag")) else severity
        issue = ValidationIssue(
            rule=rule,
            severity=eff_sev,
            line=line,
            message=message,
            snippet=snippet[:120],
        )
        if eff_sev == "error":
            errors.append(issue)
        else:
            warnings.append(issue)

    def validate_file(self, path: Path, source_text: str = "") -> FileValidationResult:
        text = Path(path).read_text(encoding="utf-8")
        return self.validate_text(text, filename=str(path), source_text=source_text)

    def validate_text(
        self,
        text: str,
        filename: str = "<memory>",
        source_text: str = "",
    ) -> FileValidationResult:
        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []
        allowlisted: List[Dict[str, Any]] = []

        all_lines = text.splitlines()
        allow_map = self._parse_allowlists(all_lines)

        fm_yaml, body, body_start_line = split_frontmatter(text)
        fm_dict: Dict[str, Any] = {}
        category_val: Optional[str] = None

        # 1. Frontmatter & Astro Zod Schema checks
        if self.check_schema:
            if fm_yaml is None:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "fm_missing", "error", 1,
                    "Missing YAML frontmatter block delimited by '---'.",
                )
            else:
                try:
                    loaded = yaml.safe_load(fm_yaml)
                except Exception as exc:
                    loaded = None
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "fm_invalid_yaml", "error", 1,
                        f"Invalid YAML frontmatter: {exc}",
                    )
                if loaded is None and not any(e.rule == "fm_invalid_yaml" for e in errors):
                    loaded = {}
                if loaded is not None and not isinstance(loaded, dict):
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "fm_invalid_yaml", "error", 1,
                        "Frontmatter must be a YAML mapping.",
                    )
                elif isinstance(loaded, dict):
                    fm_dict = loaded
                    # title
                    title_v = fm_dict.get("title")
                    if not isinstance(title_v, str) or not title_v.strip():
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_title", "error", 2,
                            "Frontmatter 'title' must be a non-empty string.",
                        )
                    # pubDatetime
                    pub_date_prefix = self._coerce_pub_datetime_date(fm_dict.get("pubDatetime"))
                    if pub_date_prefix is None:
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_pub_datetime", "error", 2,
                            "Frontmatter 'pubDatetime' must be a valid ISO date or datetime.",
                        )
                    else:
                        fname_m = re.match(r"^(\d{4}-\d{2}-\d{2})", Path(filename).name)
                        if fname_m and fname_m.group(1) != pub_date_prefix:
                            self._add_issue(
                                errors, warnings, allowlisted, allow_map,
                                "schema_filename_date_mismatch", "warning", 2,
                                f"Filename date '{fname_m.group(1)}' does not match pubDatetime '{pub_date_prefix}'.",
                            )
                    # description
                    desc_v = fm_dict.get("description")
                    if not isinstance(desc_v, str) or not desc_v.strip():
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_description", "error", 2,
                            "Frontmatter 'description' must be a non-empty string.",
                        )
                    elif len(desc_v.strip()) > 160:
                        sev = "error" if self.strict_desc else "warning"
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_description", sev, 2,
                            f"Frontmatter 'description' exceeds 160 chars ({len(desc_v.strip())}).",
                        )
                    # category
                    cat_v = fm_dict.get("category")
                    if not isinstance(cat_v, str) or cat_v not in CANONICAL_CATEGORIES:
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_category", "error", 2,
                            f"Frontmatter 'category' must be one of {list(CANONICAL_CATEGORIES)}, got {cat_v!r}.",
                        )
                    else:
                        category_val = cat_v
                        if cat_v == "study" and not self.allow_study:
                            self._add_issue(
                                errors, warnings, allowlisted, allow_map,
                                "r2_reserved_study_category", "error", 2,
                                "Category 'study' is reserved empty under R2 (0 posts allowed without --allow-study).",
                            )
                    # tags
                    tags_v = fm_dict.get("tags")
                    if (
                        not isinstance(tags_v, list)
                        or len(tags_v) < 1
                        or not all(isinstance(t, str) and t.strip() for t in tags_v)
                    ):
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_tags", "error", 2,
                            "Frontmatter 'tags' must be a non-empty list of non-empty strings.",
                        )
                    # draft
                    draft_v = fm_dict.get("draft")
                    if not isinstance(draft_v, bool):
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "schema_draft", "error", 2,
                            "Frontmatter 'draft' must be a boolean.",
                        )

                    # Emoji in FM title/description
                    for fm_key in ("title", "description"):
                        val = fm_dict.get(fm_key)
                        if isinstance(val, str):
                            em = EMOJI_RE.findall(val)
                            if em:
                                self._add_issue(
                                    errors, warnings, allowlisted, allow_map,
                                    "emoji_outside_code", "error", 2,
                                    f"Emoji found in frontmatter '{fm_key}': {''.join(em)}",
                                    snippet=val,
                                )

        # 2. Full-file line checks (including code blocks): guardrail tags, local paths, secrets, PII
        for idx, line in enumerate(all_lines, 1):
            # [검수필요]
            hb = re.search(r"\[검수필요(?::[^\]]*)?\]?", line)
            if hb:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "guardrail_hard_tag", "error", idx,
                    f"Unresolved hard-gate tag found: {hb.group(0)}",
                    snippet=line.strip(),
                )
            # [문체점검:...] or [추정]
            sw = re.search(r"\[문체점검:[^\]]+\]|\[추정\]", line)
            if sw:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "guardrail_uncleaned_soft_tag", "warning", idx,
                    f"Uncleaned soft-warning tag found: {sw.group(0)}",
                    snippet=line.strip(),
                )
            # Local path leaks
            if EVER_PATH_RE.search(line):
                m_ever = EVER_PATH_RE.search(line)
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "local_path_leak", "error", idx,
                    f"Local user path leak detected: {m_ever.group(0) if m_ever else '/Users/ever'}",
                    snippet=line.strip(),
                )
            else:
                for m_unix in UNIX_HOME_PATH_RE.finditer(line):
                    full_p = m_unix.group(0)
                    username = m_unix.group(1)
                    if "<" in full_p or username in self.allowed_path_users:
                        continue
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "local_path_leak", "error", idx,
                        f"Local home path leak detected: {full_p}",
                        snippet=line.strip(),
                    )
                    break
                for m_win in WIN_USER_PATH_RE.finditer(line):
                    full_p = m_win.group(0)
                    username = m_win.group(1)
                    if "<" in full_p or username in self.allowed_path_users:
                        continue
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "local_path_leak", "error", idx,
                        f"Local Windows user path leak detected: {full_p}",
                        snippet=line.strip(),
                    )
                    break

            # Secret / token leaks
            for label, pat in SECRET_PATTERNS:
                for sm in pat.finditer(line):
                    matched = sm.group(0)
                    low = matched.lower()
                    if any(marker in low for marker in SECRET_PLACEHOLDER_MARKERS) or any(
                        marker in matched for marker in SECRET_PLACEHOLDER_EXACT_CASE_MARKERS
                    ):
                        continue
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "secret_token_leak", "error", idx,
                        f"Potential {label} detected.",
                        snippet=matched[:40],
                    )

            # PII: Email, KR phone, KR RRN
            for em_m in EMAIL_RE.finditer(line):
                local_part = em_m.group(1).lower()
                domain = em_m.group(2).lower()
                if domain in self.allowed_email_domains or local_part.startswith("noreply"):
                    continue
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "pii_email_phone_rrn", "error", idx,
                    f"Email address detected: {em_m.group(0)}",
                    snippet=line.strip(),
                )
            ph_m = KR_PHONE_RE.search(line)
            if ph_m:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "pii_email_phone_rrn", "error", idx,
                    f"Korean phone number detected: {ph_m.group(0)}",
                    snippet=line.strip(),
                )
            rrn_m = KR_RRN_RE.search(line)
            if rrn_m:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "pii_email_phone_rrn", "error", idx,
                    "Korean resident registration number pattern detected.",
                    snippet=line.strip(),
                )

            # Extra blocked terms from policy.yaml
            for term in self.extra_blocked_terms:
                if term in line:
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "r4_custom_blocked_term", "error", idx,
                        f"Blocked privacy term detected: {term}",
                        snippet=line.strip(),
                    )

        # 3. Masked body checks (code blocks & inline code excluded, preserving line numbers)
        masked_body = mask_code_preserving_lines(body)
        masked_body_lines = masked_body.splitlines()

        for offset, mline in enumerate(masked_body_lines):
            lineno = body_start_line + offset

            # Emojis outside code
            emojis = EMOJI_RE.findall(mline)
            if emojis:
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "emoji_outside_code", "error", lineno,
                    f"Emoji outside code block: {''.join(emojis)}",
                    snippet=mline.strip(),
                )

            # Duplicate H1 (# Title)
            if re.match(r"^#\s+.+$", mline):
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "duplicate_h1", "error", lineno,
                    "Body contains H1 ('# ...') which duplicates post title H1.",
                    snippet=mline.strip(),
                )

            # Broken markdown bolding
            if not re.match(r"^\s*\*{3,}\s*$", mline):
                bold_tokens = re.findall(r"(?<!\*)\*\*(?!\*)", mline)
                if len(bold_tokens) % 2 != 0 or re.search(r":\*\*\s+[^*\n]+\*\*:", mline):
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "broken_markdown_bold", "error", lineno,
                        "Unbalanced or malformed '**' markdown bolding detected.",
                        snippet=mline.strip(),
                    )

            # Auto-trim remnant ('')
            if re.search(r"(?<!['\w])''(?!['\w])", mline):
                self._add_issue(
                    errors, warnings, allowlisted, allow_map,
                    "auto_trim_remnant", "error", lineno,
                    "Empty quote remnant '' (likely from auto-trim) detected.",
                    snippet=mline.strip(),
                )

        # 4. Context-aware R4 domain privacy checks (body sections + frontmatter text)
        sections = self._split_sections(masked_body_lines, body_start_line)
        fm_text_lines: List[Tuple[int, str]] = []
        for k in ("title", "description"):
            v = fm_dict.get(k)
            if isinstance(v, str) and v.strip():
                fm_text_lines.append((2, v))
        if fm_text_lines:
            sections = [(2, fm_text_lines)] + sections

        for _, sec_lines in sections:
            sec_text = "\n".join(line for _, line in sec_lines)
            has_github_url = bool(GITHUB_URL_RE.search(sec_text))

            # Career / resume privacy
            for lineno, line in sec_lines:
                t1 = CAREER_TIER1_RE.search(line)
                if t1:
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "r4_career_leak", "error", lineno,
                        f"Career/application leak marker detected: '{t1.group(0)}'",
                        snippet=line.strip(),
                    )
                    continue
                t2 = CAREER_TIER2_RE.search(line)
                if t2:
                    is_public_sw = (
                        has_github_url
                        and bool(CAREER_SW_RE.search(sec_text))
                        and not bool(CAREER_PERSONAL_RE.search(sec_text))
                    )
                    if not is_public_sw:
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "r4_career_leak", "error", lineno,
                            f"Uncontextualized career/salary term detected: '{t2.group(0)}'",
                            snippet=line.strip(),
                        )

            # Interior / remodeling privacy
            sec_has_addr = bool(INTERIOR_ADDR_RE.search(sec_text))
            sec_has_interior_ctx = bool(INTERIOR_CONTEXT_RE.search(sec_text))
            sec_has_interior_personal = bool(INTERIOR_PERSONAL_RE.search(sec_text))
            sec_has_interior_target = bool(INTERIOR_TARGET_RE.search(sec_text))

            for lineno, line in sec_lines:
                if (INTERIOR_ADDR_RE.search(line) and sec_has_interior_ctx) or (
                    sec_has_addr and INTERIOR_CONTEXT_RE.search(line)
                ):
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "r4_interior_leak", "error", lineno,
                        "Address combined with interior/remodeling context detected.",
                        snippet=line.strip(),
                    )
                    continue
                if (INTERIOR_PERSONAL_RE.search(line) and sec_has_interior_target) or (
                    sec_has_interior_personal and INTERIOR_TARGET_RE.search(line)
                ):
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "r4_interior_leak", "error", lineno,
                        "Personal/ongoing interior project term detected.",
                        snippet=line.strip(),
                    )
                    continue
                it2 = INTERIOR_TIER2_RE.search(line)
                if it2:
                    is_public_sw = (
                        has_github_url
                        and bool(INTERIOR_SW_RE.search(sec_text))
                        and not bool(INTERIOR_COST_PERSONAL_RE.search(sec_text))
                        and not sec_has_addr
                    )
                    if not is_public_sw:
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "r4_interior_leak", "error", lineno,
                            f"Uncontextualized interior/remodeling term detected: '{it2.group(0)}'",
                            snippet=line.strip(),
                        )

            # Medical / military privacy
            sec_has_med_personal = bool(MED_MIL_PERSONAL_RE.search(sec_text))
            for lineno, line in sec_lines:
                for pat in (MIL_UNIT_RE, MIL_HOSPITAL_RE, NAMED_HOSPITAL_RE, MED_RECORD_RE):
                    mm = pat.search(line)
                    if mm:
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "r4_medical_military_leak", "error", lineno,
                            f"Medical/military identifier detected: '{mm.group(0)}'",
                            snippet=line.strip(),
                        )
                        break
                else:
                    mt2 = MED_MIL_TIER2_RE.search(line)
                    if mt2 and (MED_MIL_PERSONAL_RE.search(line) or sec_has_med_personal):
                        self._add_issue(
                            errors, warnings, allowlisted, allow_map,
                            "r4_medical_military_leak", "error", lineno,
                            f"Personal medical/military incident context detected near '{mt2.group(0)}'",
                            snippet=line.strip(),
                        )

        # 5. PostBalancer integration (use masked_body to preserve 1-based line alignment and 4-backtick/tilde fences)
        if self.balancer is not None:
            bal_res = self.balancer.analyze(masked_body, channel="git", source_text=source_text)
            for v in bal_res.violations:
                # Skip duplicate emoji violation since emoji_outside_code is already enforced
                if v.rule_type == "excessive_emojis":
                    continue
                file_line = body_start_line + v.line_number - 1
                if v.is_blocking:
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "post_balancer_hard_block", "error", file_line,
                        f"PostBalancer ({v.rule_type}): {v.suggestion}",
                        snippet=v.matched_text,
                    )
                else:
                    self._add_issue(
                        errors, warnings, allowlisted, allow_map,
                        "post_balancer_soft_warn", "warning", file_line,
                        f"PostBalancer ({v.rule_type}): {v.suggestion}",
                        snippet=v.matched_text,
                    )

        passed = len(errors) == 0 and (not self.strict or len(warnings) == 0)
        return FileValidationResult(
            path=filename,
            passed=passed,
            errors=errors,
            warnings=warnings,
            category=category_val,
            allowlisted=allowlisted,
        )


def resolve_targets(
    paths_or_globs: Sequence[str],
    batch_dir: Optional[Path] = None,
    excludes: Sequence[str] = (),
) -> List[Path]:
    resolved: List[Path] = []
    seen: Set[Path] = set()
    exclude_set = set(excludes)

    def _add(p: Path) -> None:
        rp = p.resolve()
        if rp.name in exclude_set:
            return
        if rp.is_file() and rp not in seen:
            seen.add(rp)
            resolved.append(rp)

    if batch_dir is not None:
        bdir = Path(batch_dir)
        if bdir.is_dir():
            for p in sorted(bdir.glob("*.md")):
                _add(p)

    for raw in paths_or_globs:
        p = Path(raw)
        if p.is_dir():
            for child in sorted(p.rglob("*.md")):
                _add(child)
        elif p.is_file():
            _add(p)
        else:
            matches = sorted(glob.glob(raw, recursive=True))
            for m in matches:
                mp = Path(m)
                if mp.is_dir():
                    for child in sorted(mp.rglob("*.md")):
                        _add(child)
                elif mp.is_file():
                    _add(mp)

    return resolved


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="R4 Validator for dukjoon.github.io Astro blog posts"
    )
    parser.add_argument("targets", nargs="*", help="Markdown file paths, directories, or globs")
    parser.add_argument("--batch-dir", type=Path, default=None, help="Directory of *.md posts to validate")
    parser.add_argument("--exclude", action="append", default=[], help="Basenames to exclude (repeatable)")
    parser.add_argument("--source-dir", type=Path, default=None, help="Optional source directory matching post stem")
    parser.add_argument("--policy", type=Path, default=None, help="Path to policy.yaml")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--strict-desc", action="store_true", help="Treat description >160 chars as error")
    parser.add_argument("--allow-study", action="store_true", help="Allow category: study (disabled by R2)")
    parser.add_argument("--no-balancer", action="store_true", help="Skip PostBalancer integration")
    parser.add_argument("--no-schema", action="store_true", help="Skip Astro frontmatter Zod schema checks")

    args = parser.parse_args(argv)
    targets = resolve_targets(args.targets, batch_dir=args.batch_dir, excludes=args.exclude)
    if not targets:
        print("[ERROR] No markdown target files resolved.", file=sys.stderr)
        return 2

    validator = R4Validator(
        policy_path=args.policy,
        allow_study=args.allow_study,
        strict=args.strict,
        strict_desc=args.strict_desc,
        use_balancer=not args.no_balancer,
        check_schema=not args.no_schema,
    )

    results: List[FileValidationResult] = []
    for t in targets:
        source_text = ""
        if args.source_dir is not None and args.source_dir.is_dir():
            stem_date = re.match(r"^(\d{4}-\d{2}-\d{2})", t.name)
            candidates = [args.source_dir / f"{t.stem}.md", args.source_dir / f"{t.stem}.json"]
            if stem_date:
                d = stem_date.group(1)
                candidates.extend([
                    args.source_dir / f"{d}.md",
                    args.source_dir / f"{d}_deep.md",
                    args.source_dir / f"{d}.json",
                ])
            for c in candidates:
                if c.is_file():
                    source_text += c.read_text(encoding="utf-8", errors="replace") + "\n"
        results.append(validator.validate_file(t, source_text=source_text))

    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    if args.as_json:
        payload = {
            "summary": {
                "files_checked": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
            },
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"[{status}] {r.path} (category={r.category}, errors={len(r.errors)}, warnings={len(r.warnings)})")
            for err in r.errors:
                print(f"  ERROR L{err.line} [{err.rule}]: {err.message}")
            for warn in r.warnings:
                print(f"  WARN  L{warn.line} [{warn.rule}]: {warn.message}")
        print(
            f"\nSummary: checked={len(results)} passed={passed_count} failed={failed_count} "
            f"errors={total_errors} warnings={total_warnings}"
        )

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
