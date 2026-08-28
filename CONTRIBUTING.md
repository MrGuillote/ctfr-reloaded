# Contributing to CTFR-Reloaded

Gracias por contribuir.

## Setup local

```bash
git clone https://github.com/MrGuillote/ctfr-reloaded.git
cd ctfr-reloaded
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"
```

## Tests

```bash
pytest
```

## Estilo

- Mantener cambios enfocados y pequenos
- Seguir convenciones existentes del paquete `ctfr_reloaded`
- No romper compatibilidad de `python ctfr.py -d dominio.com`

## Uso etico

Solo prueba dominios sobre los que tengas autorizacion explicita.

## Pull requests

1. Crea un branch descriptivo
2. Agrega tests si aplica
3. Actualiza `CHANGELOG.md`
4. Describe el cambio y como probarlo
