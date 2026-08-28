from ctfr_reloaded import __version__
from ctfr_reloaded.cli import main
from ctfr_reloaded.domains import clear_url, is_valid_domain
from ctfr_reloaded.console import Console
from ctfr_reloaded.output import build_json_payload
from ctfr_reloaded.scanner import scan_domains
from types import SimpleNamespace


def run_server(host="127.0.0.1", port=8000):
    try:
        from fastapi import FastAPI, HTTPException, Query
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "Instala dependencias API: pip install ctfr-reloaded[api]"
        ) from exc

    app = FastAPI(title="CTFR-Reloaded API", version=__version__)
    console = Console(verbose=False, use_colors=False)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": __version__}

    @app.get("/scan")
    def scan(
        domain: str = Query(..., description="Dominio objetivo"),
        source: str = Query("crtsh", pattern="^(crtsh|certspotter|all)$"),
        resolve: bool = False,
        alive: bool = False,
    ):
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
            no_wildcards=False,
            apex_only=False,
            subdomains_only=False,
            new_only=False,
            baseline_set=set(),
            cache=True,
            cache_dir=None,
            rate_limit=1.0,
            version=__version__,
        )
        try:
            results = scan_domains([clean], options, console)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return build_json_payload(results)

    uvicorn.run(app, host=host, port=port)
