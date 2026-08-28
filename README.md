# CTFR-Reloaded

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml/badge.svg)](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml)

Herramienta de enumeracion de subdominios via Certificate Transparency logs, sin diccionarios ni brute-force.

Desarrollado por [MrGuillote](https://github.com/MrGuillote).

> **Uso etico:** solo escanea dominios sobre los que tengas autorizacion.

## Features

| Version | Mejoras |
|---------|---------|
| **3.0** | Multi-fuente CT, DNS resolve, HTTP alive, CSV, cache, threads, API, tests, CI |
| **2.1** | Reintentos, JSON, lista de dominios, Docker |
| **2.0** | Fix parseo, filtros, quiet mode |

## Instalacion

```bash
git clone https://github.com/MrGuillote/ctfr-reloaded.git
cd ctfr-reloaded
pip install -r requirements.txt

# o como paquete
pip install -e .
```

## Uso rapido

```bash
python ctfr.py -d ejemplo.com
python ctfr.py -d ejemplo.com -j
python ctfr.py -d ejemplo.com --source all --resolve --alive
python ctfr.py -l examples/domains.txt --threads 5 -o salida.csv
python ctfr.py -d ejemplo.com --new-only scan_anterior.txt
python ctfr.py -d ejemplo.com --pipe | httpx -silent
```

## Parametros principales

| Parametro | Descripcion |
|-----------|-------------|
| `-d`, `--domain` | Dominio objetivo |
| `-l`, `--list` | Archivo con dominios (uno por linea) |
| `-o`, `--output` | Salida `.txt`, `.json` o `.csv` |
| `-j`, `--json` | Salida JSON |
| `--format` | `plain`, `json` o `csv` |
| `--source` | `crtsh`, `certspotter` o `all` |
| `--resolve` | Verificar DNS |
| `--alive` | Verificar HTTP/HTTPS |
| `--new-only FILE` | Solo subdominios nuevos vs scan anterior |
| `--threads N` | Paralelismo (default: 5) |
| `--cache` | Cache local en `~/.cache/ctfr-reloaded` |
| `--proxy URL` | Proxy HTTP/HTTPS |
| `-v`, `--verbose` | Modo debug |
| `--pipe` | Solo nombres (para pipelines) |

Ver todos: `python ctfr.py --help`

## API HTTP (opcional)

```bash
pip install ".[api]"
python -m ctfr_reloaded serve --port 8000
curl "http://127.0.0.1:8000/scan?domain=ejemplo.com&resolve=true"
```

## Docker

```bash
docker build -t ctfr-reloaded .
docker run --rm ctfr-reloaded -d ejemplo.com -j
```

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md) y [CHANGELOG.md](CHANGELOG.md).

## Licencia

GPL v3 — ver [LICENSE](LICENSE).
