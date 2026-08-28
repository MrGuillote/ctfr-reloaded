from types import SimpleNamespace

from ctfr_reloaded import __version__
from ctfr_reloaded.constants import DEFAULT_API_PORT
from ctfr_reloaded.console import Console
from ctfr_reloaded.domains import clear_url, is_valid_domain
from ctfr_reloaded.output import build_json_payload
from ctfr_reloaded.reports import payload_to_results, render_html_report
from ctfr_reloaded.scanner import scan_domains
from ctfr_reloaded.sources import FREE_SOURCES
from ctfr_reloaded.web import render_dashboard


def build_scan_options(
    source="all",
    resolve=False,
    alive=False,
    takeover=False,
    tls=False,
    cdn=False,
    score=True,
):
    return SimpleNamespace(
        source=source,
        timeout=30,
        retries=3,
        threads=5,
        proxy=None,
        resolve=resolve,
        alive=alive,
        resolved_only=False,
        alive_only=False,
        takeover=takeover,
        takeover_only=False,
        tls=tls,
        cdn=cdn,
        score=score,
        no_wildcards=False,
        apex_only=False,
        subdomains_only=False,
        new_only=False,
        baseline_set=set(),
        cache=True,
        cache_dir=None,
        cache_ttl=3600,
        rate_limit=1.0,
        merge_subfinder=False,
        merge_amass=False,
        merge_assetfinder=False,
        show_progress=False,
        exclude_patterns=[],
        history_enabled=False,
        version=__version__,
    )


def run_scan(domain, options, console):
    clean = clear_url(domain)
    if not clean or not is_valid_domain(clean):
        raise ValueError("Dominio invalido")
    return scan_domains([clean], options, console)


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError('Instala dependencias API: pip install "ctfr-reloaded[api]"') from exc

    app = FastAPI(
        title="CTFR-Reloaded API",
        version=__version__,
        description="API gratuita de enumeracion de subdominios — MrGuillote",
    )
    console = Console(verbose=False, use_colors=False)

    @app.get("/", response_class=HTMLResponse)
    def dashboard():
        return HTMLResponse(render_dashboard(__version__, FREE_SOURCES))

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "version": __version__,
            "author": "MrGuillote",
            "sources": list(FREE_SOURCES),
        }

    @app.get("/scan")
    def scan(
        domain: str = Query(..., description="Dominio objetivo"),
        source: str = Query("all"),
        resolve: bool = False,
        alive: bool = False,
        takeover: bool = False,
        tls: bool = False,
        cdn: bool = False,
        score: bool = True,
    ):
        if source != "all" and source not in FREE_SOURCES:
            raise HTTPException(status_code=400, detail="Fuente no valida")

        options = build_scan_options(
            source=source,
            resolve=resolve,
            alive=alive,
            takeover=takeover,
            tls=tls,
            cdn=cdn,
            score=score,
        )
        try:
            results = run_scan(domain, options, console)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return build_json_payload(results)

    @app.post("/report", response_class=HTMLResponse)
    def report(payload: dict):
        try:
            results = payload_to_results(payload)
        except (KeyError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="Payload invalido") from exc
        if not results:
            raise HTTPException(status_code=400, detail="Sin resultados en el payload")
        domain = payload.get("domain") or next(iter(results))
        title = "CTFR-Reloaded — {domain}".format(domain=domain)
        return HTMLResponse(render_html_report(results, title=title))

    return app


def run_server(host="127.0.0.1", port=DEFAULT_API_PORT):
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError('Instala dependencias API: pip install "ctfr-reloaded[api]"') from exc

    uvicorn.run(create_app(), host=host, port=port)
