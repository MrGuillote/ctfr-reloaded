# CTFR-Reloaded

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml/badge.svg)](https://github.com/MrGuillote/ctfr-reloaded/actions/workflows/ci.yml)
[![100% Free](https://img.shields.io/badge/API%20keys-none-brightgreen.svg)]()
[![PyPI](https://img.shields.io/badge/PyPI-ctfr--reloaded-blue.svg)](https://pypi.org/project/ctfr-reloaded/)

Herramienta de enumeracion de subdominios **100% gratuita** — sin API keys, sin registro, sin costo.

Desarrollado por **[MrGuillote](https://github.com/MrGuillote)**.

| CLI + TUI | Dashboard web | Consola en vivo |
|-----------|---------------|-----------------|
| 8 fuentes CT gratuitas | Stats, scores y export | Logs SSE durante el scan |
| DNS, HTTP, takeover, TLS, CDN | Tabla filtrable y ordenable | Mismo motor que la terminal |

> **Uso etico:** escanea solo dominios sobre los que tengas autorizacion.

---

## Inicio rapido

```bash
pip install ctfr-reloaded
```

| Que queres hacer | Comando |
|------------------|---------|
| Scan en terminal | `ctfr-reloaded -d ejemplo.com` |
| Scan completo | `ctfr-reloaded -d ejemplo.com --resolve --alive --takeover --tls --cdn --tqdm` |
| Dashboard web | `python -m ctfr_reloaded serve` → http://127.0.0.1:9473/ |
| Reporte HTML / PDF | `ctfr-reloaded -d ejemplo.com -o reporte.html` |
| Burp Suite | `ctfr-reloaded -d ejemplo.com --burp` |

> Si clonaste el repo, tambien podes usar `python ctfr.py` en lugar de `ctfr-reloaded`.

---

## Demo

Capturas reales con **`osint.com.ar`**: todas las fuentes, resolucion DNS, comprobacion HTTP, takeover, TLS, CDN y scoring.

### Terminal

<p align="center">
  <img src="https://raw.githubusercontent.com/MrGuillote/ctfr-reloaded/main/docs/terminal-demo.png" alt="CTFR-Reloaded — scan en terminal" width="860"/>
</p>

<p align="center"><sub>CLI con colores, logs por fuente y barras de progreso</sub></p>

```bash
ctfr-reloaded -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -v
```

Salida completa de ejemplo: [docs/demo-terminal.txt](docs/demo-terminal.txt).

### Dashboard web

<p align="center">
  <img src="https://raw.githubusercontent.com/MrGuillote/ctfr-reloaded/main/docs/dashboard-scan.png" alt="Dashboard — resultados del scan" width="920"/>
</p>

<p align="center"><sub>Tarjetas de resumen, distribucion de scores, keywords y tabla interactiva</sub></p>

```bash
python -m ctfr_reloaded serve
# → http://127.0.0.1:9473/
```

### Consola de actividad

<p align="center">
  <img src="https://raw.githubusercontent.com/MrGuillote/ctfr-reloaded/main/docs/dashboard-log.png" alt="Dashboard — consola de actividad en vivo" width="920"/>
</p>

<p align="center"><sub>Panel lateral <strong>LOG</strong> con streaming en tiempo real (fuentes, DNS, HTTP, scoring…)</sub></p>

---

## Instalacion

### pip (PyPI)

```bash
pip install ctfr-reloaded
```

Un solo paquete con todo incluido: terminal, dashboard web, export HTML/PDF/JSON/CSV y modo Burp. No hace falta instalar extras.

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

---

## Fuentes gratuitas (8)

| Fuente | Flag | Notas |
|--------|------|-------|
| crt.sh | `crtsh` | Lento, a veces 404/timeout |
| **crt.name** | `crtname` | Rapido, recomendado |
| Certspotter | `certspotter` | |
| HackerTarget | `hackertarget` | |
| Wayback Machine | `wayback` | |
| Anubis | `anubis` | |
| Bufferover | `bufferover` | |
| RapidDNS | `rapiddns` | |
| **Todas** | `all` (default) | |

---

## Uso

### Scan basico

```bash
ctfr-reloaded -d ejemplo.com
```

### Scan FULL

Todas las fuentes + DNS + HTTP + takeover + TLS + CDN + score + reporte HTML:

```bash
ctfr-reloaded -d ejemplo.com \
  --source all \
  --resolve --alive --takeover --tls --cdn \
  --tqdm -v \
  --history \
  -o reporte.html --format html
```

Equivalente en una linea:

```bash
ctfr-reloaded -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -v --history -o reporte.html --format html
```

Salida JSON:

```bash
ctfr-reloaded -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -j -o resultados.json
```

### Mas ejemplos

```bash
# Recon con barra de progreso
ctfr-reloaded -d ejemplo.com --resolve --alive --takeover --tls --cdn --tqdm

# TUI interactivo
ctfr-reloaded -d ejemplo.com --tui

# Watch con alertas Discord
ctfr-reloaded -d ejemplo.com --watch --interval 1800 \
  --discord-webhook "https://discord.com/api/webhooks/..."

# Pipeline
ctfr-reloaded -d ejemplo.com --pipe | httpx -silent
```

---

## Burp Suite

```bash
# 1. Abrir Burp (proxy en 127.0.0.1:8080)
# 2. Ejecutar
ctfr-reloaded -d ejemplo.com --burp
```

`--burp` configura el proxy, activa `--resolve` + `--alive` y exporta `ejemplo.com-burp.txt` con URLs listas para importar.

**En Burp:** Target → Scope → Add → Paste URL(s).

```bash
# Solo URLs por consola
ctfr-reloaded -d ejemplo.com --burp --pipe

# Poblar site map con httpx via Burp
ctfr-reloaded -d ejemplo.com --burp --with httpx
```

---

## Features

| Feature | Flag |
|---------|------|
| Burp Suite | `--burp` |
| Barra tqdm | `--tqdm` |
| TUI interactivo | `--tui` |
| Export PDF | `-o reporte.pdf` |
| Webhook Discord | `--discord-webhook URL` |
| Webhook Telegram | `--telegram-token` + `--telegram-chat-id` |
| Takeover detection | `--takeover` |
| Historial SQLite | `--history` |
| Monitoreo | `--watch --interval SEC` |
| Desactivar score | `--no-score` |

---

## Score (priorizacion)

Cada subdominio recibe un **score de 0 a 100** para ordenar resultados. **No es un nivel de riesgo real** — es una heuristica de prioridad para pentest u OSINT.

| Factor | Puntos |
|--------|--------|
| Base | +10 |
| Keyword interesante (`api`, `dev`, `mail`, `admin`, `git`, etc.) | +15 por match |
| Resuelve DNS (`--resolve`) | +10 |
| Responde HTTP (`--alive`) | +20 |
| Posible subdomain takeover (`--takeover`) | +50 |
| Deteccion CDN (`--cdn`) | +5 |
| Info TLS (`--tls`) | +5 |
| Nombre corto (apex) | +5 |

Ejemplo sin flags extra:

```
api.ejemplo.com     → 25  (10 + keyword "api")
dev.ejemplo.com     → 25  (10 + keyword "dev")
ejemplo.com         → 15  (10 + nombre corto)
www.ejemplo.com     → 10  (solo base)
```

Para desactivar el calculo: `--no-score`.

---

## Dashboard web y API local

```bash
python -m ctfr_reloaded serve
# → http://127.0.0.1:9473/
```

Servidor **local** en tu PC — no requiere API keys ni servicios externos.

| URL | Descripcion |
|-----|-------------|
| http://127.0.0.1:9473/ | Dashboard — formulario, stats, tabla interactiva |
| http://127.0.0.1:9473/docs | Swagger (endpoints REST) |
| http://127.0.0.1:9473/scan?domain=ejemplo.com | Scan JSON basico |
| http://127.0.0.1:9473/health | Estado del servidor |

Puerto configurable: `python -m ctfr_reloaded serve --port 8080`

El reporte `-o reporte.html` usa el mismo diseno visual. Ver capturas en [Demo](#demo).

---

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para setup, tests y pull requests.

Encontraste un bug? Abri un [issue](https://github.com/MrGuillote/ctfr-reloaded/issues).

---

## Licencia

GPL v3 — [LICENSE](LICENSE)
