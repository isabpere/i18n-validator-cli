# i18n-validator-cli
A Python command-line interface to validate and check JSON and YAML localization files before deployment. It compares a base language file against a target language file to detect common internationalization (i18n) issues that could break user interfaces or cause corrupt text in production.

## Problem It Solves

Translation files often evolve independently from application code. Keys can go missing, placeholders can be incorrectly translated or deleted, and encoding issues can corrupt characters (mojibake). This tool identifies these issues early in the local development or CI pipelines.

It detects:
- **Missing Keys:** Keys defined in the base language file but absent in the target language file.
- **Extra / Orphan Keys:** Keys present in the target language file but missing in the base language file.
- **Placeholder Mismatches:** Translation placeholders that were modified, translated, or removed (e.g., `{user}` changed to `{usuario}`).
- **Mojibake:** Common broken characters caused by incorrect UTF-8 decoding (e.g., `MÃ¼ller`).

Additionally, it provides a pseudo-localization tool to help identify UI layout and truncation issues beforehand.

## Installation

Python 3.10 or higher is required.

Clone the repository and install the dependencies:

```bash
git clone <repository-url>
cd CLI_l18n
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test,lint]"
```

## Usage

When installed, the package provides two CLI commands: `loc-validator` and `loc-check`. They are identical aliases.

### Validating Translations

To validate translations, pass the reference (base) language file first, and the target language file second:

```bash
loc-validator check locales/en.json locales/es.json
```
*(Or use `loc-check check locales/en.json locales/es.json`)*

The command prints details of any identified issues and exits with:
- `0` if no localization issues are found.
- `1` if any missing keys, extra keys, placeholder mismatches, or mojibake patterns are detected.

You can also run the tool directly as a module without installing the package entry points:

```bash
python -m src.cli check locales/en.json locales/de.json
```

### Generating Pseudo-localization

Pseudo-localization automatically adds diacritics/accents to text and wraps it in delimiters to help test UI spacing, truncation, or layout issues, while preserving formatting placeholders:

```bash
loc-validator pseudoloc locales/en.json --output /tmp/en-pseudo.json
```

If the `--output` option is omitted, the pseudo-localized content is printed directly to stdout:

```bash
loc-validator pseudoloc locales/en.json
```

The command supports nested structures and handles `.json`, `.yaml`, and `.yml` formats automatically.

## Project Structure

- `locales/`: Directory containing sample translation files.
- `src/parser.py`: Functions to load JSON/YAML files and flatten nested dictionary structures using dot notation (e.g., `section.key`).
- `src/validators.py`: Logic for validation checks (missing keys, placeholder extraction, and Mojibake detection).
- `src/pseudoloc.py`: Recursive helper function to pseudo-localize text structures.
- `src/cli.py`: Click command-line interface definition and CLI output formatting.
- `tests/`: Automated unit and integration tests.

## Development and Testing

Install development dependencies:

```bash
python -m pip install -e ".[test,lint]"
```

Run tests and linter:

```bash
# Run tests with pytest
python -m pytest -q

# Run code style and linting checks with Ruff
ruff check src tests

# Verify compilation
python -m compileall -q src tests
```

The test suite covers nested structure flattening, key/placeholder comparisons, mojibake detection, pseudo-localization transformations, and CLI exit codes.

## Continuous Integration

GitHub Actions automatically runs the linter and test suite on every `push` and Pull Request using [`.github/workflows/ci.yml`](.github/workflows/ci.yml). It automatically checks for broken .json files inside the `locales/` directory.

## Technologies Used

- **Python 3.10+**
- **Click**: For a clean command-line user interface.
- **PyYAML**: For robust YAML/YML parsing and writing.
- **pytest**: For unit testing and CLI test runners.
- **Ruff**: For modern, fast Python linting and formatting.


