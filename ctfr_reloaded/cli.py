import argparse
import sys
from types import SimpleNamespace

from ctfr_reloaded import __version__
from ctfr_reloaded.config import (
    apply_config_defaults,
    get_exclude_patterns,
    load_config,
    save_default_config,
)
from ctfr_reloaded.console import Console
from ctfr_reloaded.domains import clear_url, is_valid_domain, load_domains_from_file
from ctfr_reloaded.history import ScanHistory
from ctfr_reloaded.integrations import run_integration
from ctfr_reloaded.output import emit_results, names_from_results
from ctfr_reloaded.scanner import load_baseline, scan_domains
from ctfr_reloaded.sources import FREE_SOURCES
from ctfr_reloaded.tui import run_tui
from ctfr_reloaded.watch import run_watch_loop
from ctfr_reloaded.constants import (
    DEFAULT_API_PORT,
    DEFAULT_CACHE_TTL,
    DEFAULT_MAX_DOMAINS,
    DEFAULT_RATE_LIMIT,
    DEFAULT_RETRIES,
    DEFAULT_THREADS,
    DEFAULT_TIMEOUT,
)


def build_parser():
    source_choices = list(FREE_SOURCES) + ["all"]
    parser = argparse.ArgumentParser(
        description="Enumeracion de subdominios 100%% gratuita (sin API keys).",
        epilog="Uso etico: solo escanea dominios que tengas autorizacion para probar.",
    )
    parser.add_argument(
        "-V", "--version", action="version", version="CTFR-Reloaded {v}".format(v=__version__)
    )
    parser.add_argument("-d", "--domain", type=str, help="Dominio objetivo.")
    parser.add_argument("-l", "--list", type=str, metavar="FILE", help="Archivo con dominios.")
    parser.add_argument("-o", "--output", type=str, help="Salida (.txt, .json, .csv, .html, .pdf).")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--no-wildcards", action="store_true")
    parser.add_argument("-j", "--json", action="store_true")
    parser.add_argument(
        "--format", choices=["plain", "json", "csv", "html", "pdf"], help="Formato de salida."
    )
    parser.add_argument("--source", choices=source_choices, default="all")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, metavar="SEC")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, metavar="N")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, metavar="N")
    parser.add_argument("--proxy", type=str)
    parser.add_argument("--resolve", action="store_true")
    parser.add_argument("--alive", action="store_true")
    parser.add_argument("--resolved-only", action="store_true")
    parser.add_argument("--alive-only", action="store_true")
    parser.add_argument("--takeover", action="store_true")
    parser.add_argument("--takeover-only", action="store_true")
    parser.add_argument("--tls", action="store_true")
    parser.add_argument("--cdn", action="store_true")
    parser.add_argument("--no-score", action="store_true")
    parser.add_argument("--new-only", metavar="FILE")
    parser.add_argument("--apex-only", action="store_true")
    parser.add_argument("--subdomains-only", action="store_true")
    parser.add_argument("--cache", action="store_true")
    parser.add_argument("--cache-dir", type=str)
    parser.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL, metavar="SEC")
    parser.add_argument("--rate-limit", type=float, default=DEFAULT_RATE_LIMIT, metavar="SEC")
    parser.add_argument("--max-domains", type=int, default=DEFAULT_MAX_DOMAINS, metavar="N")
    parser.add_argument("--pipe", action="store_true")
    parser.add_argument("--progress", action="store_true", help="Mostrar progreso.")
    parser.add_argument("--tqdm", action="store_true", help="Barra de progreso visual (tqdm).")
    parser.add_argument("--tui", action="store_true", help="Explorar resultados en TUI interactivo.")
    parser.add_argument("--merge-subfinder", action="store_true")
    parser.add_argument("--merge-amass", action="store_true")
    parser.add_argument("--merge-assetfinder", action="store_true")
    parser.add_argument(
        "--with", dest="with_tool",
        choices=["httpx", "nuclei", "subfinder", "amass", "assetfinder"],
    )
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--no-history", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=int, default=3600, metavar="SEC")
    parser.add_argument("--discord-webhook", type=str, help="Webhook Discord para alertas --watch.")
    parser.add_argument("--telegram-token", type=str, help="Bot token Telegram para --watch.")
    parser.add_argument("--telegram-chat-id", type=str, help="Chat ID Telegram para --watch.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--init-config", action="store_true")
    return parser


def resolve_domains(args):
    if args.list:
        return load_domains_from_file(args.list, args.max_domains)
    domain = clear_url(args.domain)
    if not domain or not is_valid_domain(domain):
        raise ValueError("Dominio invalido: {d}".format(d=args.domain))
    return [domain]


def build_options(args, config):
    exclude = get_exclude_patterns(config) + [p.lower() for p in args.exclude]
    history_enabled = config.get("history_enabled", True)
    if args.history:
        history_enabled = True
    if args.no_history:
        history_enabled = False

    return SimpleNamespace(
        source=args.source,
        timeout=args.timeout,
        retries=args.retries,
        threads=args.threads,
        proxy=args.proxy,
        resolve=args.resolve,
        alive=args.alive,
        resolved_only=args.resolved_only,
        alive_only=args.alive_only,
        takeover=args.takeover or args.takeover_only,
        takeover_only=args.takeover_only,
        tls=args.tls,
        cdn=args.cdn,
        score=not args.no_score,
        no_wildcards=args.no_wildcards,
        apex_only=args.apex_only,
        subdomains_only=args.subdomains_only,
        new_only=bool(args.new_only),
        baseline_set=set(),
        cache=args.cache,
        cache_dir=args.cache_dir,
        cache_ttl=args.cache_ttl,
        rate_limit=args.rate_limit,
        merge_subfinder=args.merge_subfinder,
        merge_amass=args.merge_amass,
        merge_assetfinder=args.merge_assetfinder,
        show_progress=args.progress or args.verbose or args.tqdm,
        use_tqdm=args.tqdm,
        exclude_patterns=exclude,
        history_enabled=history_enabled,
        version=__version__,
    )


def _explicit_cli_flags(parser, argv):
    """Marca argumentos pasados en CLI para no sobrescribirlos con config."""
    explicit = {}
    for action in parser._actions:
        dest = action.dest
        if dest in ("help", "version"):
            continue
        for opt in action.option_strings:
            if opt in argv:
                explicit[dest] = True
                break
            prefix = opt + "="
            if any(arg.startswith(prefix) for arg in argv):
                explicit[dest] = True
                break
    return explicit


def run_scan(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    cli_argv = argv if argv is not None else sys.argv[1:]

    if args.init_config:
        path = save_default_config()
        print("Config creado: {p}".format(p=path))
        return 0

    config = load_config(args.config)
    args_dict = vars(args)
    args_dict["_explicit"] = _explicit_cli_flags(parser, cli_argv)
    apply_config_defaults(args_dict, config)
    for key, value in args_dict.items():
        if key != "_explicit":
            setattr(args, key, value)

    if not args.domain and not args.list:
        parser.error("Se requiere -d/--domain o -l/--list.")
    if args.domain and args.list:
        parser.error("Usa solo -d/--domain o -l/--list.")
    if args.apex_only and args.subdomains_only:
        parser.error("Usa solo --apex-only o --subdomains-only.")
    if args.resolved_only and not args.resolve:
        parser.error("--resolved-only requiere --resolve.")
    if args.alive_only and not args.alive:
        parser.error("--alive-only requiere --alive.")
    if args.takeover_only and not args.takeover:
        args.takeover = True

    console = Console(verbose=args.verbose, use_colors=not args.no_color)

    try:
        domains = resolve_domains(args)
    except ValueError as exc:
        console.error(str(exc))
        return 1

    options = build_options(args, config)

    if args.new_only:
        try:
            options.baseline_set = load_baseline(args.new_only)
        except ValueError as exc:
            console.error(str(exc))
            return 1

    history = ScanHistory(config["history_db"], enabled=options.history_enabled)

    if not args.quiet and not args.json and not args.pipe and not args.watch:
        console.banner(__version__)

    if args.watch:
        return run_watch_loop(domains, options, args, console, history, scan_domains)

    try:
        results = scan_domains(domains, options, console, history)
    except (RuntimeError, ValueError) as exc:
        console.error(str(exc))
        return 1

    if args.format == "json":
        args.json = True

    emit_results(results, args, console)

    if args.tui:
        run_tui(results, console)

    if args.with_tool:
        names = names_from_results(results)
        if not names:
            console.warn("No hay subdominios para pasar a {t}.".format(t=args.with_tool))
        else:
            try:
                domain = domains[0] if len(domains) == 1 else None
                code = run_integration(args.with_tool, names, console, domain=domain)
                if code != 0:
                    return code
            except (RuntimeError, ValueError) as exc:
                console.error(str(exc))
                return 1

    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == "serve":
        from ctfr_reloaded.api import run_server

        serve_parser = argparse.ArgumentParser(description="API HTTP de CTFR-Reloaded")
        serve_parser.add_argument("command", choices=["serve"])
        serve_parser.add_argument("--host", default="127.0.0.1")
        serve_parser.add_argument("--port", type=int, default=DEFAULT_API_PORT)
        serve_args = serve_parser.parse_args(argv)
        run_server(host=serve_args.host, port=serve_args.port)
        return 0

    return run_scan(argv)


if __name__ == "__main__":
    sys.exit(main())
