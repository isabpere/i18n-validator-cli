# Loc Validator CLI

CLI en Python para revisar archivos de traducción JSON y YAML antes de desplegar código. Compara un idioma base con un idioma destino y detecta errores habituales de i18n que pueden romper la interfaz o dejar textos corruptos en producción.

## Problema que resuelve

Las traducciones suelen evolucionar separadas del código. Una clave puede desaparecer, una variable puede traducirse o eliminarse, y un archivo puede contener texto afectado por una decodificación UTF-8 incorrecta. Esta herramienta convierte esos problemas en errores visibles durante el desarrollo o en CI.

Detecta:

- Claves ausentes en el idioma destino.
- Claves huérfanas o extra.
- Placeholders modificados, traducidos o eliminados, como `{user}` -> `{usuario}`.
- Patrones frecuentes de mojibake, como `MÃ¼ller`.

## Instalación

Se requiere Python 3.10 o superior.

```bash
git clone <repository-url>
cd CLI_l18n
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test,lint]"
```

## Uso

### Validar traducciones

El primer archivo es la referencia y el segundo es el idioma que se valida:

```bash
loc-validator check locales/en.json locales/es.json
```

El comando imprime los problemas encontrados y devuelve:

- `0` si no hay diferencias problemáticas.
- `1` si encuentra claves, placeholders o mojibake inválidos.

También puede ejecutarse sin instalar el entry point:

```bash
python -m src.cli check locales/en.json locales/de.json
```

### Generar pseudo-localización

La pseudo-localización añade diacríticos y delimitadores para revelar problemas de espacio o truncamiento, preservando los placeholders:

```bash
loc-validator pseudoloc locales/en.json --output /tmp/en-pseudo.json
```

Si no se indica `--output`, el resultado se imprime en la terminal. Se admiten archivos `.json`, `.yaml` y `.yml`.

## Desarrollo y testing

```bash
python -m pytest -q
ruff check src tests
python -m compileall -q src tests
```

La suite incluye pruebas del parser, comparación de claves, placeholders, mojibake, pseudo-localización y códigos de salida del CLI.

## Integración continua

GitHub Actions ejecuta el linter y la suite de tests en cada `push` y Pull Request mediante [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Estructura

```text
locales/       Archivos JSON de ejemplo
src/parser.py  Carga y aplanado JSON/YAML
src/validators.py
			   Validación de claves, placeholders y codificación
src/pseudoloc.py
			   Generación de pseudo-localización
src/cli.py     Comandos de terminal
tests/         Pruebas automatizadas
```

## Tecnologías

- Python 3.10+
- Click para la interfaz de línea de comandos
- PyYAML para archivos YAML
- pytest para testing
- Ruff para linting
- GitHub Actions para integración continua
