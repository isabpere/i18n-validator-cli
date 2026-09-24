import json

from click.testing import CliRunner

from src.cli import main
from src.parser import flatten, load_and_flatten, load_file
from src.pseudoloc import pseudo_localize, pseudo_localize_text
from src.validators import (
	compare_keys,
	compare_placeholders,
	find_mojibake,
	find_mojibake_in_locale,
	validate_locale,
)


def test_flatten_and_load_json(tmp_path):
	path = tmp_path / "locale.json"
	path.write_text(json.dumps({"messages": {"welcome": "Hi {name}"}}), encoding="utf-8")

	assert load_file(path)["messages"]["welcome"] == "Hi {name}"
	assert load_and_flatten(path) == {"messages.welcome": "Hi {name}"}
	assert flatten({"a": {"b": 1}}) == {"a.b": 1}


def test_compare_keys_uses_base_and_target_sets():
	assert compare_keys({"same": 1, "missing": 2}, {"same": 3, "extra": 4}) == {
		"missing": {"missing"},
		"extra": {"extra"},
	}


def test_compare_placeholders_detects_translation_and_removal():
	result = compare_placeholders(
		{"translated": "Hi {user}", "removed": "Open {url}"},
		{"translated": "Hola {usuario}", "removed": "Abrir"},
	)

	assert result["translated"] == {"expected": {"{user}"}, "actual": {"{usuario}"}}
	assert result["removed"] == {"expected": {"{url}"}, "actual": set()}


def test_find_mojibake():
	assert find_mojibake("MÃ¼ller y cafÃ©") == ["Ã¼", "Ã©"]
	assert find_mojibake("Muller") == []
	assert find_mojibake_in_locale({"name": "MÃ¼ller", "ok": "Muller"}) == {"name": ["Ã¼"]}


def test_validate_locale_reports_all_controlled_failures():
	result = validate_locale(
		{"present": "Hi {user}", "removed": "Open {url}", "required": "Value"},
		{"present": "Hola {usuario}", "removed": "Abrir", "extra": "MÃ¼ller"},
	)

	assert result["missing"] == {"required"}
	assert result["extra"] == {"extra"}
	assert result["placeholder_mismatches"]["present"] == {
		"expected": {"{user}"},
		"actual": {"{usuario}"},
	}
	assert result["placeholder_mismatches"]["removed"]["actual"] == set()
	assert result["mojibake"] == {"extra": ["Ã¼"]}


def test_pseudo_localization_preserves_placeholders():
	localized = pseudo_localize_text("Welcome, {name}!")

	assert localized.startswith("[!!")
	assert localized.endswith("!!]")
	assert "{name}" in localized
	assert localized != "Welcome, {name}!"
	assert pseudo_localize({"message": "Save {path}"})["message"] == "[!!Šȧvḗ {path}!!]"


def test_cli_check_returns_one_and_reports_issues(tmp_path):
	base = tmp_path / "en.json"
	target = tmp_path / "es.json"
	base.write_text(json.dumps({"message": "Hi {user}"}), encoding="utf-8")
	target.write_text(json.dumps({"message": "Hola {usuario}"}), encoding="utf-8")

	result = CliRunner().invoke(main, ["check", str(base), str(target)])

	assert result.exit_code == 1
	assert "Placeholder mismatch message" in result.output


def test_cli_check_returns_zero_for_matching_locale(tmp_path):
	base = tmp_path / "en.json"
	target = tmp_path / "es.json"
	content = json.dumps({"message": "Hi {user}"})
	base.write_text(content, encoding="utf-8")
	target.write_text(content, encoding="utf-8")

	result = CliRunner().invoke(main, ["check", str(base), str(target)])

	assert result.exit_code == 0
	assert "OK: no localization issues found." in result.output


def test_cli_pseudoloc_outputs_transformed_json(tmp_path):
	input_path = tmp_path / "en.json"
	input_path.write_text(json.dumps({"message": "Save {path}"}), encoding="utf-8")

	result = CliRunner().invoke(main, ["pseudoloc", str(input_path)])

	assert result.exit_code == 0
	assert "[!!Šȧvḗ {path}!!]" in result.output
