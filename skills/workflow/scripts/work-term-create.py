#!/usr/bin/env python3
"""
work-term-create — scaffold a new term file in ~/engineering/terms/<domain>/

Allocates the next TERM-NNN ID from .counters/terms, creates the file with
front-matter pre-filled, and prints the path. Fill the body manually after.

Usage:
    work-term-create --term "Ciclo de faturamento" --domain financeiro
    work-term-create --term "..." --domain financeiro --aliases "billing cycle,faturamento"
"""

import argparse
import json
import re
from datetime import date
from pathlib import Path

ENG_DIR = Path.home() / "engineering"
TERMS_DIR = ENG_DIR / "terms"
COUNTERS_DIR = ENG_DIR / ".counters"


def next_term_id() -> str:
    COUNTERS_DIR.mkdir(parents=True, exist_ok=True)
    counter_path = COUNTERS_DIR / "terms"
    current = int(counter_path.read_text().strip()) if counter_path.exists() else 0
    next_val = current + 1
    counter_path.write_text(str(next_val))
    return f"{next_val:03d}"


def slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    parts = slug.split("-")
    return "-".join(parts[:5])


def parse_aliases(aliases_str: str) -> list[str]:
    if not aliases_str:
        return []
    return [a.strip() for a in aliases_str.split(",") if a.strip()]


def build_term_content(term_id: str, term: str, domain: str, aliases: list[str]) -> str:
    aliases_yaml = f"[{', '.join(repr(a) for a in aliases)}]" if aliases else "[]"

    return f"""---
id: TERM-{term_id}
term: "{term}"
domain: {domain}
aliases: {aliases_yaml}
---

## Definição

<!-- O que esse conceito significa no domínio de negócio.
     Normativo: define o que é, não como está implementado. -->

## No código

<!-- Só preencher se o nome no código divergir do nome de negócio.
     Omitir a seção caso contrário. -->

## Não é

<!-- Distinções importantes: o que este conceito NÃO abrange,
     e com quais outros conceitos ele costuma ser confundido. -->

---

## Referências

<!-- - [[FACT-NNN-slug]] -->
<!-- - [[TERM-NNN-slug]] -->
"""


def create_term(term: str, domain: str, aliases: list[str]) -> dict:
    domain_dir = TERMS_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    term_id = next_term_id()
    slug = slugify(term)
    filename = f"TERM-{term_id}-{slug}.md"
    term_path = domain_dir / filename

    content = build_term_content(term_id, term, domain, aliases)
    term_path.write_text(content)

    return {
        "id": f"TERM-{term_id}",
        "term": term,
        "domain": domain,
        "aliases": aliases,
        "path": str(term_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new term file")
    parser.add_argument("--term", required=True, help="Term name (business concept label)")
    parser.add_argument("--domain", required=True, help="Business domain (e.g. financeiro, fretboard)")
    parser.add_argument(
        "--aliases",
        default="",
        help="Comma-separated aliases (e.g. 'billing cycle,faturamento')",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    aliases = parse_aliases(args.aliases)
    term = create_term(args.term, args.domain, aliases)

    if args.fmt == "json":
        print(json.dumps(term, indent=2))
    else:
        print(f"{term['id']}  [{term['domain']}]  {term['term']}")
        if term["aliases"]:
            print(f"aliases: {', '.join(term['aliases'])}")
        print(f"path: {term['path']}")
        print("Fill ## Definição and ## Não é, then run: qmd update && qmd embed")


if __name__ == "__main__":
    main()
