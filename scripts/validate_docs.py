#!/usr/bin/env python3
"""Валидатор документации Vector Gene.

Каждая проверка появилась из реального дефекта, найденного при аудите 18.10.2026:

- в репозитории не было каталога data/patient/, хотя README, SKILL.md и .gitignore
  на него ссылались (шаблон пациента отсутствовал);
- NOTICE.md ссылался на upstream/, а файлы лежали в docs/upstream/ — шесть
  404-х ссылок;
- README утверждал, что у каждого навыка есть scripts/ и references/, хотя у четырёх
  навыков нет scripts/, а у четырёх — references/;
- числа «40 навыков / 66 скриптов / 8334 строки» были проставлены руками и не
  проверялись;
- в SKILL.md «шесть кейсов, три из них отрицательные», хотя отрицательных два.

Запуск:  python3 scripts/validate_docs.py [--repo-root DIR] [--json]
Выход:   0 — всё чисто; 1 — есть ошибки.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
BADGE_SKILLS_RE = re.compile(r"badge/Skills-(\d+)")
TABLE_ROW_RE = re.compile(r"^\|\s*[^|]+\|\s*(\d+)\s*\|")
PY_COUNT_RE = re.compile(r"(\d+)\s+Python-скрипт")
LINES_RE = re.compile(r"(\d+)\s+строк")
SKILLS_TEXT_RE = re.compile(r"\b(\d+)\s+(?:[а-яё]+\s+)?навыков")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def skill_dirs(root: Path) -> list[Path]:
    base = root / "skills" / "science"
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def py_scripts(root: Path) -> int:
    base = root / "skills" / "science"
    return sum(1 for _ in base.rglob("*.py")) if base.is_dir() else 0


def skill_line_count(root: Path) -> int:
    total = 0
    for d in skill_dirs(root):
        total += len(read(d / "SKILL.md").splitlines())
    return total


def check_counts(root: Path) -> list[str]:
    """Число навыков и производные счётчики должны совпадать с текстами."""
    errors: list[str] = []
    dirs = skill_dirs(root)
    actual = len(dirs)
    if actual == 0:
        return ["нет ни одного skills/science/*/SKILL.md"]

    readme = root / "README.md"
    if not readme.is_file():
        return ["нет README.md"]
    readme_text = read(readme)

    badge = BADGE_SKILLS_RE.search(readme_text)
    if not badge:
        errors.append("README: нет бейджа Skills-N")
    elif int(badge.group(1)) != actual:
        errors.append(f"README: бейдж Skills-{badge.group(1)}, а каталогов {actual}")

    for label, path, pattern in (
        ("README", readme, SKILLS_TEXT_RE),
        ("SKILL.md", root / "SKILL.md", SKILLS_TEXT_RE),
        ("agent-description.md", root / "agent-description.md", SKILLS_TEXT_RE),
    ):
        if not path.is_file():
            errors.append(f"{label}: файла нет")
            continue
        found = {int(m.group(1)) for m in pattern.finditer(read(path))}
        if not found:
            errors.append(f"{label}: не найдено упоминание числа навыков")
        elif found != {actual}:
            errors.append(f"{label}: числа {sorted(found)}, а каталогов {actual}")

    # 66 Python-скриптов
    m = PY_COUNT_RE.search(readme_text)
    if not m:
        errors.append("README: нет фразы «N Python-скриптов»")
    else:
        real = py_scripts(root)
        if int(m.group(1)) != real:
            errors.append(f"README: {m.group(1)} Python-скриптов, реально {real}")

    # 8334 строки инструкций
    m = LINES_RE.search(readme_text)
    if not m:
        errors.append("README: нет фразы «N строки инструкций»")
    else:
        real = skill_line_count(root)
        if int(m.group(1)) != real:
            errors.append(f"README: {m.group(1)} строк инструкций, реально {real}")

    return errors


def check_group_table(root: Path) -> list[str]:
    """Сумма столбца «Навыков» в таблице групп = общему числу навыков."""
    readme = root / "README.md"
    if not readme.is_file():
        return ["нет README.md"]
    text = read(readme)
    start = text.find("## Навыки")
    end = text.find("## Пайплайн")
    if start == -1 or end == -1 or end <= start:
        return ["README: не найден раздел «Навыки» до «Пайплайн»"]
    total = 0
    rows = 0
    for line in text[start:end].splitlines():
        m = TABLE_ROW_RE.match(line)
        if m:
            total += int(m.group(1))
            rows += 1
    actual = len(skill_dirs(root))
    if rows == 0:
        return ["README: в таблице групп нет строк с числом навыков"]
    if total != actual:
        return [f"README: сумма групп {total}, а каталогов {actual}"]
    return []


def check_links(root: Path) -> list[str]:
    """Все относительные ссылки в наших *.md должны вести на существующие файлы."""
    errors: list[str] = []
    targets = list(root.glob("*.md")) + list((root / "docs").glob("*.md"))
    data_dir = root / "data"
    if data_dir.is_dir():
        targets += list(data_dir.rglob("*.md"))
    # skills/science — вендор: его ссылки не наша ответственность.
    for path in sorted(set(targets)):
        base = path.parent
        for m in LINK_RE.finditer(read(path)):
            href = m.group(1).strip()
            if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            href = href.split("#", 1)[0].split("?", 1)[0]
            if not href:
                continue
            target = (base / unquote(href)).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: битая ссылка {href}")
    return errors


def check_gitkeep(root: Path) -> list[str]:
    """Файлы, обещанные .gitignore как !.../.gitkeep, должны существовать."""
    errors: list[str] = []
    gi = root / ".gitignore"
    if not gi.is_file():
        return ["нет .gitignore"]
    for line in read(gi).splitlines():
        line = line.strip()
        if not line.startswith("!") or not line[1:].endswith(".gitkeep"):
            continue
        rel = line[1:]
        if not (root / rel).exists():
            errors.append(f".gitignore обещает {rel}, файла нет")
    return errors


def check_duplicates(root: Path) -> list[str]:
    """Дубли строк в .gitignore (например, __pycache__/ дважды)."""
    entries = [ln.strip() for ln in read(root / ".gitignore").splitlines() if ln.strip()]
    seen: set[str] = set()
    dups: set[str] = set()
    for entry in entries:
        if entry in seen:
            dups.add(entry)
        seen.add(entry)
    return [f".gitignore: дубль {d}" for d in sorted(dups)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Валидатор документации Vector Gene")
    parser.add_argument("--repo-root", default=None, help="корень репозитория")
    parser.add_argument("--json", action="store_true", help="вывод в JSON")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    checks = {
        "counts": check_counts(root),
        "group_table": check_group_table(root),
        "links": check_links(root),
        "gitkeep": check_gitkeep(root),
        "gitignore_dups": check_duplicates(root),
    }
    errors = [f"[{name}] {msg}" for name, msgs in checks.items() for msg in msgs]

    if args.json:
        print(json.dumps({"root": str(root), "errors": errors, "ok": not errors},
                         ensure_ascii=False, indent=2))
    else:
        if errors:
            print(f"Ошибок: {len(errors)}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"OK: документация согласована ({len(skill_dirs(root))} навыков)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
