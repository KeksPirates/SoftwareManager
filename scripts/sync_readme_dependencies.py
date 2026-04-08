from __future__ import annotations

from pathlib import Path
import re


ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"

START_MARKER = "<!-- python-dependencies:start -->"
END_MARKER = "<!-- python-dependencies:end -->"
REQUIREMENT_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z0-9_.\-\[\]]+)\s*(?P<specifier>(==|~=|>=|<=|!=|>|<).+)?$"
)


def iter_requirements(requirements_text: str) -> list[str]:
    formatted_lines: list[str] = []

    for raw_line in requirements_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        match = REQUIREMENT_PATTERN.match(line)
        if not match:
            formatted_lines.append(f"   {line}")
            continue

        name = match.group("name")
        specifier = (match.group("specifier") or "").strip()

        if specifier.startswith("=="):
            formatted_lines.append(f"   {name} ({specifier[2:]})")
        elif specifier:
            formatted_lines.append(f"   {name} {specifier}")
        else:
            formatted_lines.append(f"   {name}")

    return formatted_lines


def render_dependency_block(requirements_text: str) -> str:
    dependency_lines = iter_requirements(requirements_text)
    return "\n".join(
        [
            START_MARKER,
            "   ```text",
            *dependency_lines,
            "   ```",
            END_MARKER,
        ]
    )


def replace_managed_block(readme_text: str, rendered_block: str) -> str:
    start_index = readme_text.find(START_MARKER)
    end_index = readme_text.find(END_MARKER)

    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise RuntimeError("README dependency markers are missing or invalid.")

    end_index += len(END_MARKER)
    return readme_text[:start_index] + rendered_block + readme_text[end_index:]


def main() -> None:
    requirements_text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    rendered_block = render_dependency_block(requirements_text)
    updated_readme = replace_managed_block(readme_text, rendered_block)

    if updated_readme != readme_text:
        README_PATH.write_text(updated_readme, encoding="utf-8")


if __name__ == "__main__":
    main()