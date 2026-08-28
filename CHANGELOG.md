# Changelog

## 4.0.0 — 100% Free Edition

- **Filosofia 100% gratuita**: sin API keys, sin registro, sin Censys
- **5 fuentes pasivas gratuitas**: crt.sh, certspotter, HackerTarget, Wayback, Anubis
- **Subdomain takeover detection** (`--takeover`, `--takeover-only`)
- **Scoring automatico** de subdominios por interes
- **Historial SQLite** (`--history`) para comparar scans
- **Modo watch** (`--watch --interval`) para monitoreo continuo
- **TLS info** (`--tls`) y **deteccion CDN** (`--cdn`)
- **Config JSON** (`--init-config`, `~/.config/ctfr-reloaded/config.json`)
- Integraciones: `--merge-amass`, `--merge-assetfinder`
- Filtros `--exclude` para patrones
- Reportes HTML/CSV enriquecidos con score, takeover, CDN, TLS

## 3.1.0

- Export HTML, reintentos, JSON, lista de dominios, integraciones httpx/nuclei

## 3.0.0

- Paquete modular, multi-fuente, resolve, alive, cache, API, tests, CI

## 2.0.0

- Version inicial mejorada
