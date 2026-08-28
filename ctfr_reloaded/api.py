import json
import queue
import threading
from types import SimpleNamespace

from ctfr_reloaded import __version__
from ctfr_reloaded.constants import DEFAULT_API_PORT
from ctfr_reloaded.console import Console
from ctfr_reloaded.domains import clear_url, is_valid_domain
from ctfr_reloaded.output import build_json_payload
from ctfr_reloaded.reports import payload_to_results, render_html_report
from ctfr_reloaded.scanner import scan_domains
from ctfr_reloaded.sources import FREE_SOURCES
from ctfr_reloaded.stream_console import StreamConsole
from ctfr_reloaded.web import render_dashboard


def build_scan_options(
    source="all",
    resolve=False,
    alive=False,
    takeover=False,
    tls=False,
    cdn=False,
    score=True,
    show_progress=False,
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
        show_progress=show_progress,
        exclude_patterns=[],
        history_enabled=False,
        version=__version__,
    )


def validate_scan_params(domain, source):
    if source != "all" and source not in FREE_SOURCES:
        raise ValueError("Fuente no valida")

    clean = clear_url(domain)
    if not clean or not is_valid_domain(clean):
        raise ValueError("Dominio invalido")
    return clean


def run_scan(domain, options, console):
    clean = validate_scan_params(domain, options.source)
    return scan_domains([clean], options, console)


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.responses import HTMLResponse, StreamingResponse
    except ImportError as exc:
        raise RuntimeError('Instala dependencias API: pip install "ctfr-reloaded[api]"') from exc

    app = FastAPI(
        title="CTFR-Reloaded API",
        version=__version__,
        description="API gratuita de enumeracion de subdominios — MrGuillote",
    )
    console = Console(verbose=False, use_colors=False)

    def parse_scan_params(
        domain,
        source="all",
        resolve=False,
        alive=False,
        takeover=False,
        tls=False,
        cdn=False,
        score=True,
    ):
        return {
            "domain": domain,
            "source": source,
            "resolve": resolve,
            "alive": alive,
            "takeover": takeover,
            "tls": tls,
            "cdn": cdn,
            "score": score,
        }

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
        params = parse_scan_params(domain, source, resolve, alive, takeover, tls, cdn, score)
        options = build_scan_options(**{k: v for k, v in params.items() if k != "domain"})
        try:
            results = run_scan(params["domain"], options, console)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return build_json_payload(results)

    @app.get("/scan/stream")
    def scan_stream(
        domain: str = Query(..., description="Dominio objetivo"),
        source: str = Query("all"),
        resolve: bool = False,
        alive: bool = False,
        takeover: bool = False,
        tls: bool = False,
        cdn: bool = False,
        score: bool = True,
    ):
        params = parse_scan_params(domain, source, resolve, alive, takeover, tls, cdn, score)
        try:
            validate_scan_params(params["domain"], params["source"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        options = build_scan_options(
            source=params["source"],
            resolve=params["resolve"],
            alive=params["alive"],
            takeover=params["takeover"],
            tls=params["tls"],
            cdn=params["cdn"],
            score=params["score"],
            show_progress=True,
        )

        def event_stream():
            event_queue = queue.Queue()
            result_holder = {}
            error_holder = {}

            def on_event(event):
                event_queue.put(("log", event))

            def worker():
                stream_console = StreamConsole(on_event=on_event)
                try:
                    stream_console.info(
                        "Iniciando scan de {d} (fuente: {s})".format(
                            d=params["domain"], s=params["source"]
                        )
                    )
                    results = run_scan(params["domain"], options, stream_console)
                    payload = build_json_payload(results)
                    count = payload.get("count") or payload.get("total", 0)
                    stream_console.success(
                        "Scan completado: {n} subdominios".format(n=count)
                    )
                    result_holder["payload"] = payload
                except Exception as exc:
                    error_holder["detail"] = str(exc)
                    stream_console.error(str(exc))
                finally:
                    event_queue.put(("done", None))

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()

            while True:
                try:
                    kind, payload = event_queue.get(timeout=1.0)
                except queue.Empty:
                    yield ": keepalive\n\n"
                    continue

                if kind == "done":
                    if error_holder:
                        yield "event: failed\ndata: {data}\n\n".format(
                            data=json.dumps(error_holder, ensure_ascii=False)
                        )
                    else:
                        yield "event: result\ndata: {data}\n\n".format(
                            data=json.dumps(result_holder["payload"], ensure_ascii=False)
                        )
                    break

                yield "event: log\ndata: {data}\n\n".format(
                    data=json.dumps(payload, ensure_ascii=False)
                )

            thread.join(timeout=30)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

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
