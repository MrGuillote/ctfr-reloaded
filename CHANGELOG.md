# Changelog

## 3.0.0

- Refactor a paquete `ctfr_reloaded` instalable con pip
- Multi-fuente CT: `crtsh`, `certspotter`, `all`
- `--resolve` para verificacion DNS
- `--alive` para verificacion HTTP/HTTPS
- `--new-only` para comparar con scan anterior
- `--apex-only` y `--subdomains-only`
- Export CSV automatico (`.csv`) o `--format csv`
- Cache local (`--cache`)
- Rate limiting (`--rate-limit`)
- Paralelismo con `--threads`
- Modo verbose (`-v`) y colores en terminal
- Proxy (`--proxy`)
- Limite de dominios en listas (`--max-domains`)
- Modo pipe (`--pipe`) para httpx/nuclei
- API HTTP opcional (`python -m ctfr_reloaded serve`)
- Tests con pytest y CI en GitHub Actions
- CHANGELOG, CONTRIBUTING y ejemplos

## 2.1.0

- Reintentos automaticos y timeout configurable
- Salida JSON (`-j`)
- Lista de dominios (`-l`)
- Dockerfile

## 2.0.0

- Version inicial con fixes de parseo, filtros y modo quiet
