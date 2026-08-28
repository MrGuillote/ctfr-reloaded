# Ejemplos CTFR-Reloaded

## Scan completo gratuito

```bash
python ctfr.py -d ejemplo.com --source all --resolve --alive --takeover --tls --cdn
```

## Reporte HTML para pentest

```bash
python ctfr.py -d ejemplo.com --source all --takeover --tls --cdn -o reporte.html
```

## Solo takeover vulnerables

```bash
python ctfr.py -d ejemplo.com --takeover --takeover-only -j
```

## Monitoreo continuo

```bash
python ctfr.py -d ejemplo.com --watch --interval 1800 --history
```

## Excluir entornos de desarrollo

```bash
python ctfr.py -d ejemplo.com --exclude staging --exclude dev --exclude test
```

## Combinar con herramientas gratuitas

```bash
python ctfr.py -d ejemplo.com --merge-subfinder --merge-amass --with httpx
```

## Config inicial

```bash
python ctfr.py --init-config
```

## Pipeline bug bounty

```bash
python ctfr.py -d ejemplo.com --source all --pipe | httpx -silent -status-code | tee alive.txt
```
