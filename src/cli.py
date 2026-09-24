"""Command-line interface for localization validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from .parser import load_and_flatten, load_file
from .pseudoloc import pseudo_localize
from .validators import validate_locale


def _format_values(values: set[str]) -> str:
	return ", ".join(sorted(values)) or "none"


def _write_pseudoloc(data: Any, path: Path) -> None:
	if path.suffix.lower() == ".json":
		path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
	elif path.suffix.lower() in {".yaml", ".yml"}:
		try:
			import yaml
		except ImportError as error:
			raise click.ClickException("YAML output requires the PyYAML package") from error
		path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
	else:
		raise click.ClickException("Output must use a .json, .yaml, or .yml extension")


@click.group()
def main() -> None:
	"""Validate localization files before deployment."""


@main.command()
@click.argument("base", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("target", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def check(base: Path, target: Path) -> None:
	"""Compare TARGET against the BASE locale."""
	try:
		result = validate_locale(load_and_flatten(base), load_and_flatten(target))
	except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
		raise click.ClickException(str(error)) from error

	issues = bool(
		result["missing"]
		or result["extra"]
		or result["placeholder_mismatches"]
		or result["mojibake"]
	)
	if not issues:
		click.secho("OK: no localization issues found.", fg="green")
		return

	click.secho(f"Issues found in {target}:", fg="red", bold=True)
	if result["missing"]:
		click.echo(f"  Missing keys: {_format_values(result['missing'])}")
	if result["extra"]:
		click.echo(f"  Extra keys: {_format_values(result['extra'])}")
	for key, mismatch in sorted(result["placeholder_mismatches"].items()):
		click.echo(
			f"  Placeholder mismatch {key}: expected {_format_values(mismatch['expected'])}; "
			f"found {_format_values(mismatch['actual'])}"
		)
	for key, matches in sorted(result["mojibake"].items()):
		click.echo(f"  Mojibake {key}: {_format_values(set(matches))}")
	ctx = click.get_current_context()
	ctx.exit(1)


@main.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path))
def pseudoloc(input_path: Path, output_path: Path | None) -> None:
	"""Generate a pseudo-localized copy of INPUT_PATH."""
	try:
		localized = pseudo_localize(load_file(input_path))
		if output_path:
			_write_pseudoloc(localized, output_path)
		else:
			if input_path.suffix.lower() == ".json":
				click.echo(json.dumps(localized, ensure_ascii=False, indent=2))
			else:
				import yaml
				click.echo(yaml.safe_dump(localized, allow_unicode=True, sort_keys=False), nl=False)
	except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
		raise click.ClickException(str(error)) from error


if __name__ == "__main__":
	main()
