from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}")


def extract_variables(*templates: str | None) -> List[str]:
    found: list[str] = []
    seen: set[str] = set()
    for template in templates:
        if not template:
            continue
        for match in VARIABLE_PATTERN.findall(template):
            if match not in seen:
                found.append(match)
                seen.add(match)
    return found


def _lookup_value(values: Dict[str, Any], dotted_key: str) -> Any:
    current: Any = values
    for part in dotted_key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(dotted_key)
    return current


def render_template(template: str | None, values: Dict[str, Any]) -> str | None:
    if template is None:
        return None

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = _lookup_value(values, key)
        return str(value)

    return VARIABLE_PATTERN.sub(replace, template)


def ensure_variables_present(required: Iterable[str], values: Dict[str, Any]) -> None:
    missing = []
    for key in required:
        try:
            _lookup_value(values, key)
        except KeyError:
            missing.append(key)
    if missing:
        raise ValueError(f"Missing template inputs: {', '.join(missing)}")

