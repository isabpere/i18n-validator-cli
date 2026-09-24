"""Validation helpers for translation mappings."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")
MOJIBAKE_PATTERN = re.compile(r"(?:Ã.|Â.|â.|ð.|�)")


def compare_keys(base: Mapping[str, Any], target: Mapping[str, Any]) -> dict[str, set[str]]:
	"""Return keys missing from, and extra in, the target locale."""
	base_keys = set(base)
	target_keys = set(target)
	return {"missing": base_keys - target_keys, "extra": target_keys - base_keys}


def extract_placeholders(value: Any) -> set[str]:
	"""Extract placeholders such as ``{user}`` from a translation value."""
	return set(PLACEHOLDER_PATTERN.findall(str(value)))


def compare_placeholders(
	base: Mapping[str, Any], target: Mapping[str, Any]
) -> dict[str, dict[str, set[str]]]:
	"""Return target entries whose placeholders differ from the base."""
	mismatches: dict[str, dict[str, set[str]]] = {}
	for key in set(base) & set(target):
		expected = extract_placeholders(base[key])
		actual = extract_placeholders(target[key])
		if expected != actual:
			mismatches[key] = {"expected": expected, "actual": actual}
	return mismatches


def find_mojibake(value: Any) -> list[str]:
	"""Return suspicious sequences commonly caused by broken UTF-8 decoding."""
	return MOJIBAKE_PATTERN.findall(str(value))


def find_mojibake_in_locale(locale: Mapping[str, Any]) -> dict[str, list[str]]:
	"""Find mojibake sequences in each affected locale entry."""
	return {
		key: matches
		for key, value in locale.items()
		if (matches := find_mojibake(value))
	}


def validate_locale(base: Mapping[str, Any], target: Mapping[str, Any]) -> dict[str, Any]:
	"""Run key, placeholder, and mojibake checks for one target locale."""
	key_results = compare_keys(base, target)
	return {
		**key_results,
		"placeholder_mismatches": compare_placeholders(base, target),
		"mojibake": find_mojibake_in_locale(target),
	}
