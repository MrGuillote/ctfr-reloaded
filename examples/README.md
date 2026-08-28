# Ejemplos de uso

## Basico

```bash
python ctfr.py -d ejemplo.com
```

## Multi-fuente + verbose

```bash
python ctfr.py -d ejemplo.com --source all -v
```

## Solo subdominios nuevos

```bash
python ctfr.py -d ejemplo.com -o scan1.txt
python ctfr.py -d ejemplo.com --new-only scan1.txt
```

## DNS + HTTP

```bash
python ctfr.py -d ejemplo.com --resolve --alive -j
```

## Pipeline con httpx

```bash
python ctfr.py -d ejemplo.com --pipe | httpx -silent
```

## Lista de dominios en paralelo

```bash
python ctfr.py -l examples/domains.txt --threads 5 -o salida.csv
```

## API local (opcional)

```bash
pip install ".[api]"
python -m ctfr_reloaded serve --port 8000
curl "http://127.0.0.1:8000/scan?domain=ejemplo.com"
```
