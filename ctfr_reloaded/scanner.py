import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ctfr_reloaded.cache import ResultCache
from ctfr_reloaded.dns import resolve_subdomains
from ctfr_reloaded.domains import split_apex_subdomains
from ctfr_reloaded.http_check import check_alive_batch
from ctfr_reloaded.session import create_session
from ctfr_reloaded.sources import get_sources


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
        resolved = {item["name"]: item for item in resolve_subdomains(names, threads=threads, timeout=timeout)}
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


def scan_domain(domain, options, console, cache, session):
    all_names = set()
    source_names = {}

    for source_name, (source, extractor) in get_sources(options.source):
        cached = cache.get(domain, source_name)
        if cached is not None:
            console.debug("Cache hit para {d} ({s})".format(d=domain, s=source_name))
            names = cached
        else:
            entries = source.fetch(session, domain, options.timeout, options.retries, console)
            names = extractor(entries, domain, exclude_wildcards=options.no_wildcards)
            cache.set(domain, source_name, names)
            if options.rate_limit > 0:
                time.sleep(options.rate_limit)
        source_names[source_name] = names
        all_names.update(names)
        console.debug(
            "{s}: {n} subdominios para {d}".format(s=source_name, n=len(names), d=domain)
        )

    subdomains = apply_scope(
        sorted(all_names),
        domain,
        apex_only=options.apex_only,
        subdomains_only=options.subdomains_only,
    )

    if options.new_only:
        subdomains = filter_new_only(subdomains, options.baseline_set)

    if options.resolve or options.alive:
        return enrich_subdomains(
            subdomains,
            resolve=options.resolve,
            alive=options.alive,
            threads=options.threads,
            timeout=options.timeout,
            session=session,
        )

    return [{"name": name} for name in subdomains]


def scan_domains(domains, options, console):
    cache = ResultCache(enabled=options.cache, cache_dir=options.cache_dir)
    session = create_session(
        retries=options.retries,
        proxy=options.proxy,
        version=options.version,
    )
    results = {}

    if len(domains) == 1 or options.threads <= 1:
        for domain in domains:
            console.info("Escaneando {d}...".format(d=domain))
            results[domain] = scan_domain(domain, options, console, cache, session)
        return results

    with ThreadPoolExecutor(max_workers=options.threads) as executor:
        futures = {
            executor.submit(scan_domain, domain, options, console, cache, session): domain
            for domain in domains
        }
        for future in as_completed(futures):
            domain = futures[future]
            results[domain] = future.result()
            console.success("Completado {d}".format(d=domain))

    return {domain: results[domain] for domain in domains}
