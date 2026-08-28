import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ctfr_reloaded.cache import ResultCache
from ctfr_reloaded.dns import resolve_subdomains
from ctfr_reloaded.domains import split_apex_subdomains
from ctfr_reloaded.enrichment import enrich_tls_cdn
from ctfr_reloaded.filters import apply_result_filters
from ctfr_reloaded.history import ScanHistory
from ctfr_reloaded.http_check import check_alive_batch
from ctfr_reloaded.integrations import (
    run_amass_merge,
    run_assetfinder_merge,
    run_subfinder_merge,
)
from ctfr_reloaded.progress import ProgressTracker
from ctfr_reloaded.scoring import apply_exclude_patterns, enrich_scores
from ctfr_reloaded.session import create_session
from ctfr_reloaded.sources import get_sources
from ctfr_reloaded.takeover import enrich_takeover


def load_baseline(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return {line.strip().lower() for line in handle if line.strip()}
    except OSError as exc:
        raise ValueError("No se pudo leer baseline: {e}".format(e=exc)) from exc


def filter_new_only(subdomains, baseline):
    return sorted(name for name in subdomains if name.lower() not in baseline)


def apply_scope(subdomains, target, apex_only=False, subdomains_only=False):
    apex, subs = split_apex_subdomains(subdomains, target)
    if apex_only:
        return apex
    if subdomains_only:
        return subs
    return sorted(apex + subs)


def enrich_subdomains(names, resolve=False, alive=False, threads=10, timeout=5, session=None):
    enriched = [{"name": name} for name in names]
    if resolve:
        resolved = {
            item["name"]: item
            for item in resolve_subdomains(names, threads=threads, timeout=timeout)
        }
        for item in enriched:
            data = resolved.get(item["name"], {})
            item["resolved"] = data.get("resolved", False)
            item["addresses"] = data.get("addresses", [])
    if alive:
        alive_data = {
            item["name"]: item
            for item in check_alive_batch(names, threads=threads, timeout=timeout, session=session)
        }
        for item in enriched:
            data = alive_data.get(item["name"], {})
            item["alive"] = data.get("alive", False)
            item["url"] = data.get("url")
            item["status_code"] = data.get("status_code")
    return enriched


def _merge_external(domain, options, console, all_names):
    mergers = [
        (options.merge_subfinder, run_subfinder_merge, "subfinder"),
        (options.merge_amass, run_amass_merge, "amass"),
        (options.merge_assetfinder, run_assetfinder_merge, "assetfinder"),
    ]
    for enabled, func, label in mergers:
        if not enabled:
            continue
        try:
            names = func(domain, console)
            all_names.update(names)
            console.debug("{l}: {n} subdominios para {d}".format(l=label, n=len(names), d=domain))
        except RuntimeError as exc:
            console.warn(str(exc))


def scan_domain(domain, options, console, cache, session, history=None):
    all_names = set()

    for source_name, (source, extractor) in get_sources(options.source):
        cached = cache.get(domain, source_name)
        if cached is not None:
            console.debug("Cache hit para {d} ({s})".format(d=domain, s=source_name))
            names = cached
        else:
            try:
                entries = source.fetch(session, domain, options.timeout, options.retries, console)
                names = extractor(entries, domain, exclude_wildcards=options.no_wildcards)
                cache.set(domain, source_name, names)
            except RuntimeError as exc:
                if options.source == "all":
                    console.warn("{s}: {e}".format(s=source_name, e=exc))
                    continue
                raise
            if options.rate_limit > 0:
                time.sleep(options.rate_limit)
        all_names.update(names)
        console.debug(
            "{s}: {n} subdominios para {d}".format(s=source_name, n=len(names), d=domain)
        )

    _merge_external(domain, options, console, all_names)

    subdomains = apply_scope(
        sorted(all_names),
        domain,
        apex_only=options.apex_only,
        subdomains_only=options.subdomains_only,
    )

    if options.new_only:
        subdomains = filter_new_only(subdomains, options.baseline_set)

    if options.resolve or options.alive:
        enriched = enrich_subdomains(
            subdomains,
            resolve=options.resolve,
            alive=options.alive,
            threads=options.threads,
            timeout=options.timeout,
            session=session,
        )
    else:
        enriched = [{"name": name} for name in subdomains]

    if options.takeover:
        enriched = enrich_takeover(enriched, threads=options.threads, timeout=options.timeout)

    if options.tls or options.cdn:
        enriched = enrich_tls_cdn(
            enriched,
            session=session,
            threads=options.threads,
            timeout=options.timeout,
        )

    enriched = apply_exclude_patterns(enriched, options.exclude_patterns)

    if options.takeover_only:
        enriched = [item for item in enriched if item.get("vulnerable")]

    enriched = apply_result_filters(
        enriched,
        resolved_only=options.resolved_only,
        alive_only=options.alive_only,
    )

    if options.score:
        enriched = enrich_scores(enriched)

    if history and options.history_enabled:
        history.save_scan(domain, enriched)

    return enriched


def scan_domains(domains, options, console, history=None):
    cache = ResultCache(
        enabled=options.cache,
        cache_dir=options.cache_dir,
        ttl_seconds=options.cache_ttl,
    )
    session = create_session(
        retries=options.retries,
        proxy=options.proxy,
        version=options.version,
    )
    results = {}
    progress = ProgressTracker(
        len(domains),
        console,
        enabled=options.show_progress,
        use_tqdm=getattr(options, "use_tqdm", False),
        desc="Dominios",
    )
    progress.start("Escaneando dominios")

    try:
        if len(domains) == 1 or options.threads <= 1:
            for domain in domains:
                if not getattr(options, "use_tqdm", False):
                    console.info("Escaneando {d}...".format(d=domain))
                results[domain] = scan_domain(domain, options, console, cache, session, history)
                progress.step(domain)
        else:
            with ThreadPoolExecutor(max_workers=options.threads) as executor:
                futures = {
                    executor.submit(
                        scan_domain, domain, options, console, cache, session, history
                    ): domain
                    for domain in domains
                }
                for future in as_completed(futures):
                    domain = futures[future]
                    results[domain] = future.result()
                    progress.step(domain)
                    if not getattr(options, "use_tqdm", False):
                        console.success("Completado {d}".format(d=domain))
    finally:
        progress.close()

    return {domain: results[domain] for domain in domains}
