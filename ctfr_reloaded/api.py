from types import SimpleNamespace

from ctfr_reloaded import __version__
from ctfr_reloaded.console import Console
from ctfr_reloaded.domains import clear_url, is_valid_domain
from ctfr_reloaded.output import build_json_payload
from ctfr_reloaded.scanner import scan_domains
from ctfr_reloaded.sources import FREE_SOURCES


def run_server(host="127.0.0.1", port=8000):
    try:
        from fastapi import FastAPI, HTTPException, Query
        import uvicorn
    except ImportError as exc:
        raise RuntimeError('Instala dependencias API: pip install "ctfr-reloaded[api]"') from exc

    app = FastAPI(
        title="CTFR-Reloaded API",
        version=__version__,
        description="API gratuita de enumeracion de subdominios — MrGuillote",
    )
    console = Console(verbose=False, use_colors=False)

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

        clean = clear_url(domain)
        if not clean or not is_valid_domain(clean):
            raise HTTPException(status_code=400, detail="Dominio invalido")

        options = SimpleNamespace(
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
        try:
            results = scan_domains([clean], options, console)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return build_json_payload(results)

    uvicorn.run(app, host=host, port=port)
