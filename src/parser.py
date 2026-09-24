"""Load and flatten JSON or YAML locale files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
	"""Flatten nested mappings into ``section.key`` entries."""
	flattened: dict[str, Any] = {}
	for key, value in data.items():
		dotted_key = f"{prefix}.{key}" if prefix else key
		if isinstance(value, dict):
			flattened.update(flatten(value, dotted_key))
		else:
			flattened[dotted_key] = value
	return flattened


def load_file(path: str | Path) -> dict[str, Any]:
	"""Load a JSON or YAML file and return its top-level mapping."""
	file_path = Path(path)
	suffix = file_path.suffix.lower()
	text = file_path.read_text(encoding="utf-8")

	if suffix == ".json":
		data = json.loads(text)
	elif suffix in {".yaml", ".yml"}:
		try:
			import yaml
		except ImportError as error:
			raise RuntimeError("YAML support requires the PyYAML package") from error
		data = yaml.safe_load(text)
	else:
		raise ValueError(f"Unsupported locale format: {suffix or '<none>'}")

	if not isinstance(data, dict):
		raise ValueError(f"Locale file must contain a mapping: {file_path}")
	return data


def load_and_flatten(path: str | Path) -> dict[str, Any]:
	"""Load a locale file and return its values in dot notation."""
	return flatten(load_file(path))
