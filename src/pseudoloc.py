"""Pseudo-localization utilities."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")
ACCENT_MAP = str.maketrans({
	"a": "ȧ", "A": "Ȧ", "e": "ḗ", "E": "Ḗ", "i": "ī", "I": "Ī",
	"o": "ō", "O": "Ō", "u": "ū", "U": "Ū", "c": "ƈ", "C": "Ƈ",
	"n": "ɲ", "N": "Ɲ", "s": "š", "S": "Š",
})


def pseudo_localize_text(value: str, left: str = "[!!", right: str = "!!]") -> str:
	"""Add accented characters and delimiters while preserving placeholders."""
	parts: list[str] = []
	position = 0
	for match in PLACEHOLDER_PATTERN.finditer(value):
		parts.append(value[position : match.start()].translate(ACCENT_MAP))
		parts.append(match.group(0))
		position = match.end()
	parts.append(value[position:].translate(ACCENT_MAP))
	return f"{left}{''.join(parts)}{right}"


def pseudo_localize(value: Any) -> Any:
	"""Recursively pseudo-localize strings in nested locale data."""
	if isinstance(value, str):
		return pseudo_localize_text(value)
	if isinstance(value, Mapping):
		return {key: pseudo_localize(item) for key, item in value.items()}
	if isinstance(value, list):
		return [pseudo_localize(item) for item in value]
	return value


pseudolocalize = pseudo_localize
