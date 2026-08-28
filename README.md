# CTFR-Reloaded

Fork mejorado de [CTFR](https://github.com/UnaPibaGeek/ctfr) por Sheila A. Berta (UnaPibaGeek).

Obtiene subdominios desde Certificate Transparency logs ([crt.sh](https://crt.sh/)) sin diccionarios ni brute-force.

## Mejoras respecto al original

- Fix: separa correctamente `name_value` (varios dominios por `\n`)
- Timeout en peticiones a crt.sh (30s)
- User-Agent identificable
- Filtra solo subdominios del dominio objetivo
- Opción `--no-wildcards` para excluir `*.dominio.com`
- Opción `-q` / `--quiet` para pipelines
- Escritura eficiente del archivo de salida (una sola operación)
- Manejo de errores de red y JSON
- Estructura `if __name__ == "__main__"`

## Requisitos

- Python 3.6+
- pip3

## Instalación

```bash
git clone https://github.com/TU_USUARIO/ctfr-reloaded.git
cd ctfr-reloaded
pip3 install -r requirements.txt
```

## Uso

```bash
python3 ctfr.py -d ejemplo.com
python3 ctfr.py -d ejemplo.com -o subdominios.txt
python3 ctfr.py -d ejemplo.com --no-wildcards
python3 ctfr.py -d ejemplo.com -q
```

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `-d`, `--domain` | Dominio objetivo (requerido) |
| `-o`, `--output` | Archivo de salida (opcional) |
| `-q`, `--quiet` | Solo muestra el conteo final |
| `--no-wildcards` | Excluye entradas `*.dominio.com` |

## Licencia

GPL v3 — ver [LICENSE](LICENSE).

Basado en CTFR original por Sheila A. Berta (UnaPibaGeek).
