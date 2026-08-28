# CTFR-Reloaded

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml/badge.svg)](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml)
[![100% Free](https://img.shields.io/badge/API%20keys-none-brightgreen.svg)]()
[![PyPI](https://img.shields.io/badge/PyPI-ctfr--reloaded-blue.svg)](https://pypi.org/project/ctfr-reloaded/)

Herramienta de enumeracion de subdominios **100% gratuita** — sin API keys, sin registro, sin costo.

Desarrollado por [MrGuillote](https://github.com/MrGuillote).

## Demo

<p align="center">
  <img src="docs/screenshot.svg" alt="CTFR-Reloaded terminal demo" width="720"/>
</p>

```
$ python ctfr.py -d ejemplo.com --source all --takeover --tqdm
[+] 42 subdominios encontrados. Listo!
```

Ver salida completa en [docs/demo-terminal.txt](docs/demo-terminal.txt).

## Instalacion

### pip (PyPI)

```bash
pip install ctfr-reloaded

# Con extras
pip install "ctfr-reloaded[api,pdf]"
```

### Desde GitHub

```bash
git clone https://github.com/MrGuillote/ctfr-reloaded.git
cd ctfr-reloaded
pip install -e ".[dev]"
```

### Docker (GHCR)

```bash
docker pull ghcr.io/mrguillote/ctfr-reloaded:latest
docker run --rm ghcr.io/mrguillote/ctfr-reloaded:latest -d ejemplo.com
```

## Fuentes gratuitas (7)

| Fuente | Flag |
|--------|------|
| crt.sh | `crtsh` |
| Certspotter | `certspotter` |
| HackerTarget | `hackertarget` |
| Wayback Machine | `wayback` |
| Anubis | `anubis` |
| Bufferover | `bufferover` |
| RapidDNS | `rapiddns` |
| **Todas** | `all` (default) |

## Uso rapido

```bash
# Scan completo
python ctfr.py -d ejemplo.com

# Recon pro con barra de progreso
python ctfr.py -d ejemplo.com --resolve --alive --takeover --tls --cdn --tqdm

# Reporte PDF
python ctfr.py -d ejemplo.com -o reporte.pdf --format pdf

# TUI interactivo
python ctfr.py -d ejemplo.com --tui

# Watch con alertas Discord
python ctfr.py -d ejemplo.com --watch --interval 1800 \
  --discord-webhook "https://discord.com/api/webhooks/..."

# Pipeline
python ctfr.py -d ejemplo.com --pipe | httpx -silent
```

## Features v4.1

| Feature | Flag |
|---------|------|
| Barra tqdm | `--tqdm` |
| TUI interactivo | `--tui` |
| Export PDF | `-o reporte.pdf` |
| Webhook Discord | `--discord-webhook URL` |
| Webhook Telegram | `--telegram-token` + `--telegram-chat-id` |
| Takeover detection | `--takeover` |
| Historial SQLite | `--history` |
| Monitoreo | `--watch --interval SEC` |

## API local

```bash
pip install "ctfr-reloaded[api]"
python -m ctfr_reloaded serve
curl "http://127.0.0.1:9473/scan?domain=ejemplo.com"
```

Puerto por defecto: **9473** (configurable con `--port`).

## Publicar en PyPI (mantenedores)

1. Crear release `v4.1.0` en GitHub
2. Configurar secret `PYPI_API_TOKEN` en el repo
3. El workflow `publish-pypi.yml` publica automaticamente

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

## Reportar bugs

Usa los [issue templates](.github/ISSUE_TEMPLATE/) del repo.

## Licencia

GPL v3 — [LICENSE](LICENSE)
