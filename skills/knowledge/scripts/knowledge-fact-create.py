#!/usr/bin/env python3
"""
knowledge-fact-create — scaffold a new fact file in ~/engineering/facts/

Allocates the next FACT-NNN ID from .counters/facts, creates the file with
front-matter pre-filled, and prints the path. Fill the body manually after.

Usage:
    knowledge-fact-create --title "Auth token refresh happens before expiry check"
    knowledge-fact-create --title "..." --tags auth,clojure --confidence validated
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ENG_DIR = Path.home() / "engineering"
FACTS_DIR = ENG_DIR / "facts"
COUNTERS_DIR = ENG_DIR / ".counters"


def next_fact_id() -> str:
    COUNTERS_DIR.mkdir(parents=True, exist_ok=True)
    counter_path = COUNTERS_DIR / "facts"
    current = int(counter_path.read_text().strip()) if counter_path.exists() else 0
    next_val = current + 1
    counter_path.write_text(str(next_val))
    return f"{next_val:03d}"


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    # Truncate to 5 meaningful words
    parts = slug.split("-")
    return "-".join(parts[:5])


def parse_tags(tags_str: str) -> list[str]:
    if not tags_str:
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


def build_fact_content(fact_id: str, title: str, tags: list[str], confidence: str) -> str:
    today = date.today().isoformat()
    tags_yaml = f"[{', '.join(tags)}]" if tags else "[]"
    confirmed_line = f"confirmed: {today}" if confidence == "validated" else "confirmed:"

    return f"""---
id: FACT-{fact_id}
title: "{title}"
confidence: {confidence}
created: {today}
{confirmed_line}
tags: {tags_yaml}
refs:
  - spike:
  - issue:
  - commit:
---

## Statement

<!-- One paragraph. Plain language. Behavioral claim, not code description.
     What is true, not how it is implemented. -->

## Evidence

<!-- What anchors this fact. File and line, commit hash, or test name.
     Prefer commit hash over file:line — a changed hash signals staleness. -->

## Depends on

<!-- - [[FACT-NNN-slug]] -->

## Notes

<!-- Optional. Caveats, edge cases, conditions under which this might not hold. -->
"""


def create_fact(title: str, tags: list[str], confidence: str) -> dict:
    FACTS_DIR.mkdir(parents=True, exist_ok=True)

    fact_id = next_fact_id()
    slug = slugify(title)
    filename = f"FACT-{fact_id}-{slug}.md"
    fact_path = FACTS_DIR / filename

    content = build_fact_content(fact_id, title, tags, confidence)
    fact_path.write_text(content)

    return {
        "id": f"FACT-{fact_id}",
        "title": title,
        "confidence": confidence,
        "tags": tags,
        "path": str(fact_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new fact file")
    parser.add_argument("--title", required=True, help="Fact title / short label")
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags (e.g. auth,clojure,seubarriga)",
    )
    parser.add_argument(
        "--confidence",
        default="asserted",
        choices=["asserted", "validated"],
        help="Confidence level (default: asserted)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    tags = parse_tags(args.tags)
    fact = create_fact(args.title, tags, args.confidence)

    if args.fmt == "json":
        print(json.dumps(fact, indent=2))
    else:
        print(f"{fact['id']}  {fact['confidence']}  {fact['title']}")
        print(f"path: {fact['path']}")
        print("Fill ## Statement, ## Evidence, and refs, then run: qmd update && qmd embed")


if __name__ == "__main__":
    main()
