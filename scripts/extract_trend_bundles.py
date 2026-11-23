#!/usr/bin/env python3
"""Deterministic Per-Date Trend Bundle Extractor for idea-capture/collected_data.

STRICT NO-PROSE CONTRACT:
This script ONLY parses, filters, deduplicates, ranks, and emits deterministic JSON
bundles containing verbatim repository names, canonical GitHub URLs, raw signals,
and sanitized verbatim source excerpts. It NEVER calls an LLM and NEVER generates
blog post titles, summaries, descriptions, tags, or commentary.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

LEGACY_HEADING_RE = re.compile(r"^### 📦 ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\s*$", re.MULTILINE)
LEGACY_URL_RE = re.compile(r"- \*\*URL\*\*:\s*\[[^\]]*\]\((https?://[^)\s]+)\)")
LEGACY_README_HEADER_RE = re.compile(r"^#### 📝 README 요약\s*$", re.MULTILINE)

DEEP_HEADING_RE = re.compile(
    r"^## 💎 ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) \[SCORE: (\d+)\]\s*$",
    re.MULTILINE,
)
DEEP_SIGNALS_RE = re.compile(r"^- Signals:\s*(.+)$", re.MULTILINE)
DEEP_EXCERPT_RE = re.compile(r"^### 📄 (.+)$", re.MULTILINE)

COLLECTED_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:_deep)?\.md$")

REGISTRY_PATTERNS: Tuple[str, ...] = (
    r"^rust-lang/crates\.io-index$",
    r"^NixOS/nixpkgs$",
    r"^Homebrew/",
    r"^conda-forge/",
    r"^regro/cf-graph",
    r"^JuliaRegistries/",
    r"^opentofu/registry$",
    r"^aquaproj/aqua-registry$",
    r"^hyperlane-xyz/hyperlane-registry$",
    r"^gripped/archpkgbuilds$",
    r"^calungaproject/index$",
    r"(^|/)homebrew-tap$",
)

NOISE_PATTERNS: Tuple[str, ...] = REGISTRY_PATTERNS + (
    # Automated plugin/skill/nix mirrors & aggregators
    r"^tomevault-io/",
    r"^sudosubin/agents\.nix$",
    r"^openclaw/skills$",
    r"^jentic/jentic-public-apis$",
    r"^tom-doerr/repo_posts$",
    # Automated mirrors, bots, personal Obsidian syncs, news feeds, docs-only
    r"MSDyn365BC\.Sandbox\.Code\.History$",
    r"^aws-mwaa/upstream-to-airflow$",
    r"(^|[-_.])mirror([-_.]|$)",
    r"^[^/]+-bot/",
    r"/(.*-)?bot$",
    r"^kriscendobot/",
    r"^admin-baked/bakedbot-for-brands$",
    r"(ObsidianVault|obsidian-github-publisher-sync)$",
    r"^(Demoaccount010/smilenews-data|JTFNews/jtfnews|chesmangatelli-spec/viral-news-artes)$",
    r"^pilgrimdelamare/lentemattutinacontent$",
    r"^eltonaguiar/findtorontoevents_antigravity\.ca$",
    r"/awesome(-|$)",
    r"^(MicrosoftDocs|DataDog/documentation|odoo/documentation)/",
)

COMPILED_REGISTRY_RES = tuple(re.compile(p, re.IGNORECASE) for p in REGISTRY_PATTERNS)
COMPILED_NOISE_RES = tuple(re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS)

AI_CONFIG_NAMES = ("claude.md", ".cursorrules", ".claudecode.json", "instruction.md", "rules.md")
CODE_EXTENSIONS = (".py", ".ts", ".js", ".go", ".rs")


def assign_batch(date_str: str) -> str:
    month = date_str[:7]
    if month in ("2026-02", "2026-03"):
        return "2026-02..03"
    if month in ("2026-04", "2026-05"):
        return "2026-04..05"
    if month in ("2026-06", "2026-07", "2026-08"):
        return "2026-06..08"
    return "2026-09..11+"


def is_registry_repo(repo: str) -> bool:
    return any(rx.search(repo) for rx in COMPILED_REGISTRY_RES)


def is_noise_repo(repo: str) -> bool:
    return any(rx.search(repo) for rx in COMPILED_NOISE_RES)


def is_binary_or_corrupted_excerpt(raw_excerpt: str) -> bool:
    if not raw_excerpt:
        return False
    if raw_excerpt.count("\x00") > 5:
        return True
    sample = raw_excerpt[:1000]
    if not sample:
        return False
    printable = sum(1 for ch in sample if ch.isprintable() or ch in "\n\r\t")
    return (printable / len(sample)) < 0.85


def sanitize_excerpt_text(raw_excerpt: str) -> str:
    cleaned = raw_excerpt.replace("\x00", "").replace("\ufffd", "")
    return "".join(ch for ch in cleaned if ch.isprintable() or ch in "\n\r\t")


def strip_code_wrapper(raw_block: str) -> str:
    """Strip trailing entry separator '---' and outer ```text / ``` wrapper."""
    text = raw_block.strip("\r\n")
    text = re.sub(r"(?:\r?\n)+---\s*$", "", text).rstrip("\r\n")
    text = re.sub(r"^```[^\n]*\r?\n", "", text, count=1)
    text = re.sub(r"\r?\n```\s*$", "", text)
    return text.strip("\r\n")


def split_top_level_signals(signals_line: str) -> List[str]:
    """Split comma-separated signals without breaking commas inside [...] or (...)."""
    signals: List[str] = []
    buf: List[str] = []
    paren_depth = 0
    bracket_depth = 0
    for ch in signals_line:
        if ch == "(":
            paren_depth += 1
        elif ch == ")" and paren_depth > 0:
            paren_depth -= 1
        elif ch == "[":
            bracket_depth += 1
        elif ch == "]" and bracket_depth > 0:
            bracket_depth -= 1
        elif ch == "," and paren_depth == 0 and bracket_depth == 0:
            token = "".join(buf).strip()
            if token:
                signals.append(token)
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        signals.append(tail)
    return signals


def evaluate_quality(project_content: str) -> int:
    """Replicates idea-capture/qualifier.py:evaluate_quality."""
    score = 0
    if any(x in project_content for x in (".cursorrules", "CLAUDE.md", "agent.json")):
        score += 40
    if any(x in project_content for x in ("requirements.txt", "package.json", "pyproject.toml")):
        score += 20
    if ".env.example" in project_content or "config.py" in project_content:
        score += 20
    if len(project_content) > 1500:
        score += 20
    return score


def compute_excerpt_richness(excerpts: Sequence[Dict[str, Any]]) -> int:
    if not excerpts:
        return 0
    substantive = [
        ex
        for ex in excerpts
        if ex["content"].strip() not in ("", "@AGENTS.md", "@AGENTS.md.")
        and len(ex["content"].strip()) >= 40
    ]
    if not substantive:
        return 5

    total_chars = sum(len(ex["content"].strip()) for ex in substantive)
    pts = min(40, total_chars // 40)

    paths_lower = [ex["path"].lower() for ex in substantive]
    if any(any(name in p for name in AI_CONFIG_NAMES) for p in paths_lower):
        pts += 15
    if any(p.endswith(CODE_EXTENSIONS) for p in paths_lower):
        pts += 15
    if any("readme" in p for p in paths_lower):
        pts += 15
    if len(substantive) >= 2:
        pts += 10
    return pts


@dataclass
class RepoEntry:
    repo: str
    url: str
    raw_score: int
    signals: List[str] = field(default_factory=list)
    source_formats: List[str] = field(default_factory=list)
    excerpts: List[Dict[str, Any]] = field(default_factory=list)
    q_score: int = 0
    in_quality_data: bool = False
    excerpt_richness: int = 0
    rank_score: float = 0.0


def parse_legacy_file(path: Path) -> Tuple[int, List[RepoEntry]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(LEGACY_HEADING_RE.finditer(text))
    entries: List[RepoEntry] = []

    for idx, m in enumerate(matches):
        repo = m.group(1).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]

        url_m = LEGACY_URL_RE.search(block)
        url = url_m.group(1).strip() if url_m else f"https://github.com/{repo}"

        excerpts: List[Dict[str, Any]] = []
        readme_m = LEGACY_README_HEADER_RE.search(block)
        if readme_m:
            raw_readme = strip_code_wrapper(block[readme_m.end():])
            if raw_readme and not is_binary_or_corrupted_excerpt(raw_readme):
                clean_readme = sanitize_excerpt_text(raw_readme)
                if clean_readme.strip():
                    excerpts.append(
                        {
                            "path": "README.md",
                            "content": clean_readme,
                            "char_count": len(clean_readme),
                            "truncated_at_source": len(clean_readme) >= 490 or clean_readme.rstrip().endswith("..."),
                        }
                    )

        if block.count("\x00") > 5 and not excerpts:
            continue

        entries.append(
            RepoEntry(
                repo=repo,
                url=url,
                raw_score=50,
                signals=[],
                source_formats=["legacy"],
                excerpts=excerpts,
            )
        )

    return len(matches), entries


def parse_deep_file(path: Path) -> Tuple[int, List[RepoEntry]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(DEEP_HEADING_RE.finditer(text))
    entries: List[RepoEntry] = []

    for idx, m in enumerate(matches):
        repo = m.group(1).strip()
        raw_score = int(m.group(2))
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]

        sig_m = DEEP_SIGNALS_RE.search(block)
        signals = split_top_level_signals(sig_m.group(1).strip()) if sig_m else []

        ex_matches = list(DEEP_EXCERPT_RE.finditer(block))
        excerpts: List[Dict[str, Any]] = []
        for ex_idx, ex_m in enumerate(ex_matches):
            ex_path = ex_m.group(1).strip()
            if Path(ex_path).name.startswith("._"):
                continue
            ex_start = ex_m.end()
            ex_end = ex_matches[ex_idx + 1].start() if ex_idx + 1 < len(ex_matches) else len(block)
            raw_content = strip_code_wrapper(block[ex_start:ex_end])
            if is_binary_or_corrupted_excerpt(raw_content):
                continue
            clean_content = sanitize_excerpt_text(raw_content)
            if not clean_content.strip():
                continue
            excerpts.append(
                {
                    "path": ex_path,
                    "content": clean_content,
                    "char_count": len(clean_content),
                    "truncated_at_source": len(clean_content) >= 990,
                }
            )

        if block.count("\x00") > 5 and not excerpts:
            continue

        entries.append(
            RepoEntry(
                repo=repo,
                url=f"https://github.com/{repo}",
                raw_score=raw_score,
                signals=signals,
                source_formats=["deep"],
                excerpts=excerpts,
            )
        )

    return len(matches), entries


def parse_quality_file(path: Path) -> Dict[str, int]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(DEEP_HEADING_RE.finditer(text))
    scores: Dict[str, int] = {}
    for idx, m in enumerate(matches):
        repo = m.group(1).strip()
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        raw_entry = re.sub(r"(?:\r?\n)+---\s*$", "", text[start:end].strip())
        q_score = evaluate_quality(raw_entry)
        if repo not in scores or q_score > scores[repo]:
            scores[repo] = q_score
    return scores


def merge_day_entries(parsed_entries: Sequence[RepoEntry]) -> List[RepoEntry]:
    """Deduplicate intra-day entries by repo name, merging signals, formats, and excerpts."""
    merged: Dict[str, RepoEntry] = {}
    seen_excerpts: Dict[str, set] = {}

    for entry in parsed_entries:
        if entry.repo not in merged:
            merged[entry.repo] = RepoEntry(
                repo=entry.repo,
                url=f"https://github.com/{entry.repo}",
                raw_score=entry.raw_score,
                signals=list(dict.fromkeys(entry.signals)),
                source_formats=list(dict.fromkeys(entry.source_formats)),
                excerpts=[],
            )
            seen_excerpts[entry.repo] = set()
        else:
            cur = merged[entry.repo]
            if entry.raw_score > cur.raw_score:
                cur.raw_score = entry.raw_score
            for s in entry.signals:
                if s not in cur.signals:
                    cur.signals.append(s)
            for fmt in entry.source_formats:
                if fmt not in cur.source_formats:
                    cur.source_formats.append(fmt)

        cur = merged[entry.repo]
        for ex in entry.excerpts:
            key = (ex["path"], ex["content"])
            if key not in seen_excerpts[entry.repo]:
                seen_excerpts[entry.repo].add(key)
                cur.excerpts.append(ex)

    return list(merged.values())


def score_entry(entry: RepoEntry, q_scores: Dict[str, int]) -> RepoEntry:
    entry.in_quality_data = entry.repo in q_scores
    entry.q_score = q_scores.get(entry.repo, 0)
    entry.excerpt_richness = compute_excerpt_richness(entry.excerpts)
    has_substantive = 1 if entry.excerpt_richness >= 20 else 0
    entry.rank_score = (
        (has_substantive * 100.0)
        + (40.0 if entry.in_quality_data else 0.0)
        + (entry.q_score * 0.5)
        + float(entry.excerpt_richness)
        + (min(entry.raw_score, 140) * 0.5)
    )
    return entry


def sync_idea_capture(idea_capture_dir: Path) -> Dict[str, Any]:
    proc = subprocess.run(
        ["git", "-C", str(idea_capture_dir), "pull", "--ff-only"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return {
        "attempted": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def get_git_head(repo_dir: Path) -> Optional[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode == 0:
        return proc.stdout.strip()
    return None


def extract_bundles(
    idea_capture_dir: Path,
    out_dir: Path,
    target_min: int = 4,
    target_default: int = 5,
    target_max: int = 6,
    cooldown_days: int = 21,
    sync_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    collected_dir = idea_capture_dir / "collected_data"
    quality_dir = idea_capture_dir / "quality_data"
    if not collected_dir.is_dir():
        raise FileNotFoundError(f"collected_data directory not found: {collected_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Group collected_data/*.md by date
    files_by_date: Dict[str, Dict[str, Path]] = {}
    for p in sorted(collected_dir.iterdir()):
        if not p.is_file():
            continue
        m = COLLECTED_FILE_RE.match(p.name)
        if not m:
            continue
        date_str = m.group(1)
        kind = "deep" if p.name.endswith("_deep.md") else "legacy"
        files_by_date.setdefault(date_str, {})[kind] = p

    sorted_dates = sorted(files_by_date.keys())
    last_selected: Dict[str, date] = {}
    batches_map: Dict[str, List[str]] = {
        "2026-02..03": [],
        "2026-04..05": [],
        "2026-06..08": [],
        "2026-09..11+": [],
    }
    manifest_dates: List[Dict[str, Any]] = []
    total_selected_items = 0

    for date_str in sorted_dates:
        date_obj = date.fromisoformat(date_str)
        day_files = files_by_date[date_str]

        raw_entries_count = 0
        parsed_entries: List[RepoEntry] = []
        source_files: List[str] = []

        # Process deep file first so deep excerpts lead
        if "deep" in day_files:
            dp = day_files["deep"]
            source_files.append(f"collected_data/{dp.name}")
            rc, entries = parse_deep_file(dp)
            raw_entries_count += rc
            parsed_entries.extend(entries)

        if "legacy" in day_files:
            lp = day_files["legacy"]
            source_files.append(f"collected_data/{lp.name}")
            rc, entries = parse_legacy_file(lp)
            raw_entries_count += rc
            parsed_entries.extend(entries)

        merged_entries = merge_day_entries(parsed_entries)

        q_path = quality_dir / f"{date_str}_quality.md"
        q_scores = parse_quality_file(q_path)
        quality_rel = f"quality_data/{q_path.name}" if q_path.is_file() else None

        non_noise: List[RepoEntry] = []
        noise_non_registry: List[RepoEntry] = []
        for entry in merged_entries:
            score_entry(entry, q_scores)
            if is_noise_repo(entry.repo):
                if not is_registry_repo(entry.repo):
                    noise_non_registry.append(entry)
            else:
                non_noise.append(entry)

        non_noise.sort(key=lambda e: (-e.rank_score, -e.raw_score, e.repo.lower()))
        noise_non_registry.sort(key=lambda e: (-e.rank_score, -e.raw_score, e.repo.lower()))

        eligible: List[RepoEntry] = []
        cooldown_skipped: List[RepoEntry] = []
        for entry in non_noise:
            prev = last_selected.get(entry.repo)
            if prev is None or (date_obj - prev).days >= cooldown_days:
                eligible.append(entry)
            else:
                cooldown_skipped.append(entry)

        selected: List[RepoEntry] = list(eligible[:target_default])
        if (
            len(eligible) >= target_max
            and target_default < target_max
            and eligible[target_default].rank_score >= 200.0
        ):
            selected.append(eligible[target_default])

        fallback_tier = "none"
        if len(selected) < 3 and cooldown_skipped:
            cooldown_skipped_sorted = sorted(
                cooldown_skipped,
                key=lambda e: (-(date_obj - last_selected[e.repo]).days, -e.rank_score, e.repo.lower()),
            )
            desired = min(target_min, len(eligible) + len(cooldown_skipped_sorted))
            for cand in cooldown_skipped_sorted:
                if len(selected) >= desired:
                    break
                selected.append(cand)
            fallback_tier = "cooldown_relaxed"

        if len(non_noise) < target_min:
            if len(selected) < 3 and noise_non_registry:
                for cand in noise_non_registry:
                    if len(selected) >= target_min:
                        break
                    selected.append(cand)
                fallback_tier = "noise_relaxed"
            elif fallback_tier == "none":
                fallback_tier = "low_volume_all_valid"

        for item in selected:
            last_selected[item.repo] = date_obj

        batch_name = assign_batch(date_str)
        batches_map.setdefault(batch_name, []).append(date_str)
        total_selected_items += len(selected)

        bundle_payload = {
            "date": date_str,
            "batch": batch_name,
            "source_files": source_files,
            "quality_file": quality_rel,
            "stats": {
                "raw_entries": raw_entries_count,
                "unique_repos": len(merged_entries),
                "after_noise_filter": len(non_noise),
                "after_cooldown": len(eligible),
                "selected_count": len(selected),
                "fallback_tier": fallback_tier,
            },
            "items": [
                {
                    "rank": rank_idx,
                    "repo": item.repo,
                    "url": item.url,
                    "score": item.raw_score,
                    "q_score": item.q_score,
                    "in_quality_data": item.in_quality_data,
                    "excerpt_richness": item.excerpt_richness,
                    "rank_score": item.rank_score,
                    "signals": item.signals,
                    "source_formats": item.source_formats,
                    "excerpts": item.excerpts,
                }
                for rank_idx, item in enumerate(selected, 1)
            ],
        }

        bundle_path = out_dir / f"{date_str}.json"
        bundle_path.write_text(
            json.dumps(bundle_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest_dates.append(
            {
                "date": date_str,
                "batch": batch_name,
                "bundle_path": str(bundle_path),
                "selected_count": len(selected),
                "fallback_tier": fallback_tier,
            }
        )

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "idea_capture_head": get_git_head(idea_capture_dir),
        "sync_status": sync_status or {"attempted": False},
        "total_dates": len(sorted_dates),
        "total_selected_items": total_selected_items,
        "batch_counts": {k: len(v) for k, v in batches_map.items()},
        "batches": batches_map,
        "dates": manifest_dates,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic per-date trend bundle extractor (no prose generation)"
    )
    parser.add_argument(
        "--idea-capture-dir",
        type=Path,
        default=Path("/Users/ever/Desktop/workspace/idea-capture"),
        help="Path to idea-capture repository",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("/tmp/trend_bundles"),
        help="Output directory for YYYY-MM-DD.json and manifest.json",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Attempt git pull --ff-only in idea-capture before extracting",
    )
    parser.add_argument("--target-min", type=int, default=4)
    parser.add_argument("--target-default", type=int, default=5)
    parser.add_argument("--target-max", type=int, default=6)
    parser.add_argument("--cooldown-days", type=int, default=21)

    args = parser.parse_args(argv)
    sync_status: Optional[Dict[str, Any]] = None
    if args.sync:
        sync_status = sync_idea_capture(args.idea_capture_dir)
        if sync_status["returncode"] != 0:
            print(
                f"[WARN] idea-capture git pull failed (exit={sync_status['returncode']}): "
                f"{sync_status['stderr'] or sync_status['stdout']}",
                file=sys.stderr,
            )

    manifest = extract_bundles(
        idea_capture_dir=args.idea_capture_dir,
        out_dir=args.out_dir,
        target_min=args.target_min,
        target_default=args.target_default,
        target_max=args.target_max,
        cooldown_days=args.cooldown_days,
        sync_status=sync_status,
    )
    print(
        f"[OK] Extracted {manifest['total_dates']} dates ({manifest['total_selected_items']} items) -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
