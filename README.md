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

---

## Inicio rapido

**Un solo comando.** Terminal, dashboard web y export PDF vienen incluidos — no hace falta instalar extras.

```bash
pip install ctfr-reloaded
```

| Que queres hacer | Comando |
|------------------|---------|
| Scan en terminal | `ctfr-reloaded -d ejemplo.com` |
| Dashboard web | `python -m ctfr_reloaded serve` → http://127.0.0.1:9473/ |
| Reporte HTML | `ctfr-reloaded -d ejemplo.com -o reporte.html` |
| Reporte PDF | `ctfr-reloaded -d ejemplo.com -o reporte.pdf` |

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

### pip (PyPI) — recomendado

```bash
pip install ctfr-reloaded
```

Incluye todo lo necesario para usar la herramienta:

| Componente | Dependencias | Incluido |
|------------|--------------|----------|
| Terminal + TUI | requests, colorama, dnspython, tqdm | Si |
| Dashboard web | FastAPI, uvicorn, httpx | Si |
| Export PDF | fpdf2 | Si |
| Tests (`pytest`) | pytest, pytest-mock, responses | No — solo con `[dev]` |

Los extras `[api]` y `[pdf]` de versiones anteriores **ya no hacen falta** (se mantienen vacios por compatibilidad).

Para contribuir al proyecto:

```bash
pip install "ctfr-reloaded[dev]"
```

### Desde GitHub

```bash
git clone https://github.com/MrGuillote/ctfr-reloaded.git
cd ctfr-reloaded
pip install -e ".[dev]"

# Scan full de ejemplo
python ctfr.py -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -v -o reporte.html --format html
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

## Uso rapido

```bash
# Scan basico (todas las fuentes por defecto)
ctfr-reloaded -d ejemplo.com
```

### Scan FULL (traer todo)

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

Salida JSON en lugar de HTML:

```bash
ctfr-reloaded -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -j -o resultados.json
```

Docker (mismo scan full):

```bash
docker run --rm ghcr.io/mrguillote/ctfr-reloaded:latest \
  -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn --tqdm -v -j
```

### Mas ejemplos

```bash
# Recon pro con barra de progreso
ctfr-reloaded -d ejemplo.com --resolve --alive --takeover --tls --cdn --tqdm

# Reporte PDF
ctfr-reloaded -d ejemplo.com -o reporte.pdf --format pdf

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

Modo mas sencillo: un solo flag prepara todo para Burp.

```bash
# 1. Abrir Burp y dejar el proxy en 127.0.0.1:8080 (default)
# 2. Ejecutar CTFR en modo Burp
ctfr-reloaded -d ejemplo.com --burp
```

`--burp` hace automaticamente:

| Accion | Detalle |
|--------|---------|
| Proxy | Envia checks HTTP via `127.0.0.1:8080` (trafico visible en Burp) |
| DNS + HTTP | Activa `--resolve` y `--alive` |
| Export | Genera `ejemplo.com-burp.txt` con URLs (`https://...`) |

**Importar en Burp:** Target → Scope → Add → Paste URL(s) → pegar el contenido del archivo.

Solo URLs por consola (sin archivo):

```bash
ctfr-reloaded -d ejemplo.com --burp --pipe
```

Pasando httpx por Burp para poblar el site map:

```bash
ctfr-reloaded -d ejemplo.com --burp --with httpx
```

Proxy manual (sin `--burp`):

```bash
ctfr-reloaded -d ejemplo.com --alive --proxy http://127.0.0.1:8080 -o urls.txt --format burp
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

Cada subdominio recibe un **score de 0 a 100** para ordenar resultados: arriba van los que conviene revisar primero en un pentest u OSINT.

**No es un nivel de riesgo real** ni confirma vulnerabilidades; es una heuristica de prioridad.

| Factor | Puntos |
|--------|--------|
| Base | +10 |
| Palabra clave interesante en el nombre (`api`, `dev`, `mail`, `admin`, `test`, `git`, etc.) | +15 por match |
| Resuelve DNS (`--resolve`) | +10 |
| Responde HTTP (`--alive`) | +20 |
| Posible subdomain takeover (`--takeover`) | +50 |
| Deteccion CDN (`--cdn`) | +5 |
| Info TLS (`--tls`) | +5 |
| Nombre corto (apex o pocas partes, ej. `ejemplo.com`) | +5 |

Ejemplo sin flags extra:

```
api.ejemplo.com     → 25  (10 + keyword "api")
dev.ejemplo.com     → 25  (10 + keyword "dev")
ejemplo.com         → 15  (10 + nombre corto)
www.ejemplo.com     → 10  (solo base)
```

Con `--resolve --alive --takeover` los scores suben segun lo que se detecte en cada host. Para desactivar el calculo: `--no-score`.

---

## Servidor web local (dashboard)

El **modo web** levanta un servidor HTTP en tu maquina (por defecto `127.0.0.1:9473`). Incluye el dashboard visual y endpoints REST para integrar scans desde otros scripts.

**No usa servicios externos ni pide API keys** — todo corre localmente en tu PC.

```bash
python -m ctfr_reloaded serve
# Abrir en el navegador: http://127.0.0.1:9473/
```

Puerto configurable: `python -m ctfr_reloaded serve --port 8080`

| URL | Descripcion |
|-----|-------------|
| http://127.0.0.1:9473/ | **Dashboard web** — formulario, estadisticas, tabla interactiva |
| http://127.0.0.1:9473/docs | Documentacion interactiva (Swagger) de los endpoints REST |
| http://127.0.0.1:9473/scan?domain=ejemplo.com | Scan JSON basico |
| http://127.0.0.1:9473/scan?domain=ejemplo.com&source=all&resolve=true&alive=true&takeover=true&tls=true&cdn=true&score=true | Scan completo (JSON) |
| http://127.0.0.1:9473/health | Estado del servidor |

El dashboard incluye tarjetas de estadisticas, distribucion de scores, keywords detectadas, filtro y orden por columnas, export a JSON/HTML, y una **consola lateral en vivo** durante el scan. Ver capturas en la seccion [Demo](#demo). El reporte `-o reporte.html` usa el mismo diseno.

---

## Publicar en PyPI (mantenedores)

1. Crear tag `vX.Y.Z` y pushearlo a GitHub
2. Configurar secret `PYPI_API_TOKEN` en el repo
3. Ejecutar workflow `publish-pypi.yml` (manual o tras release publicado)

---

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

---

## Reportar bugs

Usa los [issue templates](.github/ISSUE_TEMPLATE/) del repo.

---

## Licencia

GPL v3 — [LICENSE](LICENSE)
