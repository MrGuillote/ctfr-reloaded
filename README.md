# CTFR-Reloaded

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml/badge.svg)](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml)
[![100% Free](https://img.shields.io/badge/API%20keys-none-brightgreen.svg)]()

Herramienta de enumeracion de subdominios **100% gratuita** — sin API keys, sin registro, sin costo.

Desarrollado por [MrGuillote](https://github.com/MrGuillote).

> **Uso etico:** solo escanea dominios autorizados. Ver [SECURITY.md](SECURITY.md).

## Fuentes gratuitas incluidas

| Fuente | Tipo |
|--------|------|
| **crt.sh** | Certificate Transparency |
| **certspotter** | Certificate Transparency |
| **HackerTarget** | Passive DNS |
| **Wayback Machine** | URLs archivadas |
| **Anubis** | Base de datos pasiva |

Mas integraciones opcionales (tambien gratis): **subfinder**, **amass**, **assetfinder**, **httpx**, **nuclei**.

## Instalacion

```bash
git clone https://github.com/MrGuillote/ctfr-reloaded.git
cd ctfr-reloaded
pip install -r requirements.txt
pip install -e .
```

## Uso rapido

```bash
# Todas las fuentes gratuitas
python ctfr.py -d ejemplo.com

# Recon completo
python ctfr.py -d ejemplo.com --resolve --alive --takeover --tls --cdn -o reporte.html

# Solo vulnerables a takeover
python ctfr.py -d ejemplo.com --takeover --takeover-only

# Monitoreo continuo
python ctfr.py -d ejemplo.com --watch --interval 3600 --history

# Pipeline
python ctfr.py -d ejemplo.com --pipe | httpx -silent
```

## Features v4.0

- 5 fuentes pasivas **sin API key**
- **Subdomain takeover** detection (CNAME dangling)
- **Scoring** automatico de subdominios
- **Historial SQLite** (`--history`)
- **Modo watch** (`--watch`)
- **TLS info** y **deteccion CDN**
- **Config JSON** (`--init-config`)
- Filtros `--exclude`, `--resolved-only`, `--alive-only`
- Integraciones: subfinder, amass, assetfinder, httpx, nuclei

## Configuracion

```bash
python ctfr.py --init-config
# Crea ~/.config/ctfr-reloaded/config.json
```

Ver [examples/config.json](examples/config.json).

## Parametros principales

| Parametro | Descripcion |
|-----------|-------------|
| `--source all` | Todas las fuentes gratuitas (default) |
| `--takeover` | Detectar subdomain takeover |
| `--tls` / `--cdn` | Info TLS y CDN |
| `--watch` | Monitoreo periodico |
| `--history` | Guardar en SQLite |
| `--merge-amass` | Combinar con amass |
| `--exclude` | Excluir patrones |
| `-o reporte.html` | Export HTML |

Ver todos: `python ctfr.py --help`

## API (opcional)

```bash
pip install ".[api]"
python -m ctfr_reloaded serve --port 8000
```

## Docker

```bash
docker build -t ctfr-reloaded .
docker run --rm ctfr-reloaded -d ejemplo.com
```

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

## Licencia

GPL v3 — [LICENSE](LICENSE)
