import argparse
import sys
from types import SimpleNamespace

from ctfr_reloaded import __version__
from ctfr_reloaded.console import Console
from ctfr_reloaded.domains import clear_url, is_valid_domain, load_domains_from_file
from ctfr_reloaded.output import emit_results
from ctfr_reloaded.scanner import load_baseline, scan_domains
from ctfr_reloaded.constants import (
    DEFAULT_MAX_DOMAINS,
    DEFAULT_RATE_LIMIT,
    DEFAULT_RETRIES,
    DEFAULT_THREADS,
    DEFAULT_TIMEOUT,
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Enumeracion de subdominios via Certificate Transparency.",
        epilog="Uso etico: solo escanea dominios que tengas autorizacion para probar.",
    )
    parser.add_argument("-d", "--domain", type=str, help="Dominio objetivo.")
    parser.add_argument(
        "-l", "--list", type=str, metavar="FILE", help="Archivo con lista de dominios."
    )
    parser.add_argument("-o", "--output", type=str, help="Archivo de salida (.txt, .json, .csv).")
    parser.add_argument("-q", "--quiet", action="store_true", help="Solo muestra el conteo final.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verbose.")
    parser.add_argument("--no-color", action="store_true", help="Desactivar colores.")
    parser.add_argument(
        "--no-wildcards",
        action="store_true",
        help="Excluir entradas con wildcard (*.dominio.com).",
    )
    parser.add_argument("-j", "--json", action="store_true", help="Salida en formato JSON.")
    parser.add_argument(
        "--format",
        choices=["plain", "json", "csv"],
        help="Formato de salida para -o (auto-detecta por extension).",
    )
    parser.add_argument(
        "--source",
        choices=["crtsh", "certspotter", "all"],
        default="crtsh",
        help="Fuente CT (default: crtsh).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        metavar="SEC",
        help="Timeout en segundos (default: {d}).".format(d=DEFAULT_TIMEOUT),
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        metavar="N",
        help="Reintentos ante error (default: {d}).".format(d=DEFAULT_RETRIES),
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        metavar="N",
        help="Hilos para multiples dominios/checks (default: {d}).".format(d=DEFAULT_THREADS),
    )
    parser.add_argument("--proxy", type=str, help="Proxy HTTP/HTTPS (ej: http://127.0.0.1:8080).")
    parser.add_argument("--resolve", action="store_true", help="Verificar resolucion DNS.")
    parser.add_argument("--alive", action="store_true", help="Verificar respuesta HTTP/HTTPS.")
    parser.add_argument(
        "--new-only",
        metavar="FILE",
        help="Mostrar solo subdominios no presentes en un scan anterior.",
    )
    parser.add_argument("--apex-only", action="store_true", help="Solo dominio apex.")
    parser.add_argument(
        "--subdomains-only", action="store_true", help="Excluir dominio apex."
    )
    parser.add_argument("--cache", action="store_true", help="Usar cache local.")
    parser.add_argument("--cache-dir", type=str, help="Directorio de cache personalizado.")
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=DEFAULT_RATE_LIMIT,
        metavar="SEC",
        help="Pausa entre consultas CT (default: {d}).".format(d=DEFAULT_RATE_LIMIT),
    )
    parser.add_argument(
        "--max-domains",
        type=int,
        default=DEFAULT_MAX_DOMAINS,
        metavar="N",
        help="Limite de dominios en -l (default: {d}).".format(d=DEFAULT_MAX_DOMAINS),
    )
    parser.add_argument(
        "--pipe",
        action="store_true",
        help="Imprimir solo nombres (util para httpx/nuclei).",
    )
    return parser


def resolve_domains(args):
    if args.list:
        return load_domains_from_file(args.list, args.max_domains)

    domain = clear_url(args.domain)
    if not domain or not is_valid_domain(domain):
        raise ValueError("Dominio invalido: {d}".format(d=args.domain))
    return [domain]


def run_scan(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.domain and not args.list:
        parser.error("Se requiere -d/--domain o -l/--list.")
    if args.domain and args.list:
        parser.error("Usa solo -d/--domain o -l/--list, no ambos.")
    if args.apex_only and args.subdomains_only:
        parser.error("Usa solo --apex-only o --subdomains-only.")

    console = Console(verbose=args.verbose, use_colors=not args.no_color)

    try:
        domains = resolve_domains(args)
    except ValueError as exc:
        console.error(str(exc))
        return 1

    baseline_set = set()
    if args.new_only:
        try:
            baseline_set = load_baseline(args.new_only)
        except ValueError as exc:
            console.error(str(exc))
            return 1

    options = SimpleNamespace(
        source=args.source,
        timeout=args.timeout,
        retries=args.retries,
        threads=args.threads,
        proxy=args.proxy,
        resolve=args.resolve,
        alive=args.alive,
        no_wildcards=args.no_wildcards,
        apex_only=args.apex_only,
        subdomains_only=args.subdomains_only,
        new_only=bool(args.new_only),
        baseline_set=baseline_set,
        cache=args.cache,
        cache_dir=args.cache_dir,
        rate_limit=args.rate_limit,
        version=__version__,
    )

    if not args.quiet and not args.json and not args.pipe:
        console.banner(__version__)

    try:
        results = scan_domains(domains, options, console)
    except (RuntimeError, ValueError) as exc:
        console.error(str(exc))
        return 1

    if args.format == "json":
        args.json = True

    emit_results(results, args, console)
    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == "serve":
        from ctfr_reloaded.api import run_server

        serve_parser = argparse.ArgumentParser(description="API HTTP de CTFR-Reloaded")
        serve_parser.add_argument("command", choices=["serve"])
        serve_parser.add_argument("--host", default="127.0.0.1")
        serve_parser.add_argument("--port", type=int, default=8000)
        args = serve_parser.parse_args(argv)
        run_server(host=args.host, port=args.port)
        return 0

    return run_scan(argv)


if __name__ == "__main__":
    sys.exit(main())
