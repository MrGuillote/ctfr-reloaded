# Changelog

## 4.2.3

- **`--burp`**: modo Burp Suite — proxy automatico (`127.0.0.1:8080`), resolve+alive y export de URLs listas para importar en Target Scope
- README simplificado para usuarios; instrucciones de PyPI movidas a CONTRIBUTING.md

## 4.2.2

- **Instalacion todo-en-uno**: `pip install ctfr-reloaded` incluye CLI, dashboard web (FastAPI/uvicorn) y export PDF
- Extras `[api]` y `[pdf]` quedan vacios por compatibilidad; solo `[dev]` es opcional (tests)
- README simplificado para una experiencia de usuario directa

## 4.2.1

- Capturas reales en README (terminal, dashboard y consola de actividad)
- URLs absolutas de GitHub para que las imagenes se vean tambien en PyPI

## 4.2.0

- **Dashboard web** en `http://127.0.0.1:9473/` con stats, filtros, tabla ordenable y export JSON/HTML
- **Consola lateral en vivo** durante el scan (SSE `/scan/stream`) con logs de fuentes, DNS, HTTP y scoring
- **Persistencia en pestana** via `sessionStorage` (resultados, filtros y formulario sobreviven al F5)
- Distribucion de scores por rangos reales (0-14 ... 60-100)
- Reporte HTML (`-o reporte.html`) rediseñado con el mismo estilo visual
- Endpoint `POST /report` para generar HTML desde resultados JSON
- `/docs` se mantiene para la API

## 4.1.1

- Nueva fuente **crt.name** (`--source crtname`) — API rapida alternativa a crt.sh
- crt.sh: timeout minimo 60s (suele ser lento/inestable)
- Mejor tolerancia a 404 y fallos parciales en `--source all`

## 4.1.0

- **7 fuentes 100% free**: +Bufferover, +RapidDNS
- **tqdm**: barra de progreso visual (`--tqdm`)
- **Webhooks**: Discord y Telegram en `--watch`
- **TUI interactivo**: `--tui` para explorar resultados
- **Export PDF**: `--format pdf` o `.pdf` (requiere `[pdf]`)
- **PyPI**: publicacion automatica en release
- **Docker GHCR**: `ghcr.io/mrguillote/ctfr-reloaded`
- **Issue templates**: bug, feature, question
- **Tests de integracion** con mocks de red (`responses`)
- Puerto API por defecto: **9473**
- Demo visual en `docs/screenshot.svg`

## 4.0.0 — 100% Free Edition

- 5 fuentes pasivas sin API key
- Subdomain takeover, scoring, historial SQLite, watch
- TLS, CDN, config JSON, integraciones externas

## 3.0.0

- Paquete modular, multi-fuente, API, tests, CI

## 2.0.0

- Version inicial mejorada
