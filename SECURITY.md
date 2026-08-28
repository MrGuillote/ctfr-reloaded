# Security Policy

## Uso autorizado

CTFR-Reloaded es una herramienta de reconocimiento pasivo. Solo debe usarse sobre dominios y sistemas para los que tengas **autorizacion explicita**.

El autor ([MrGuillote](https://github.com/MrGuillote)) no se hace responsable del uso indebido de esta herramienta.

## Reportar vulnerabilidades

Si encuentras una vulnerabilidad en CTFR-Reloaded:

1. **No** abras un issue publico con detalles sensibles
2. Contacta al mantenedor via GitHub Issues con el titulo `Security: ...`
3. Incluye pasos para reproducir y el impacto estimado

## Buenas practicas

- Respeta rate limits de crt.sh, certspotter, hackertarget y demas fuentes gratuitas
- No compartas API keys en repositorios publicos
- Usa `--cache` con moderacion en entornos compartidos
- Revisa los resultados antes de ejecutar herramientas agresivas (`nuclei`, etc.)
