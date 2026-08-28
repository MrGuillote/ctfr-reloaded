import socket

from ctfr_reloaded.takeover_fingerprints import TAKEOVER_FINGERPRINTS


def get_cname_chain(name, timeout=3):
    try:
        import dns.resolver
    except ImportError:
        return []

    chain = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout
        answers = resolver.resolve(name, "CNAME")
        for rdata in answers:
            chain.append(str(rdata.target).rstrip(".").lower())
    except Exception:
        pass
    return chain


def detect_takeover(name, timeout=3):
    chain = get_cname_chain(name, timeout=timeout)
    if not chain:
        return {"takeover": False, "cname": None, "service": None, "vulnerable": False}

    cname = chain[-1]
    for suffix, service in TAKEOVER_FINGERPRINTS.items():
        if cname == suffix or cname.endswith("." + suffix):
            vulnerable = _check_dangling(name, timeout)
            return {
                "takeover": vulnerable,
                "cname": cname,
                "service": service,
                "vulnerable": vulnerable,
            }

    return {"takeover": False, "cname": cname, "service": None, "vulnerable": False}


def _check_dangling(name, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(name, None)
        return False
    except socket.gaierror:
        return True


def enrich_takeover(items, threads=10, timeout=3):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = {}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(detect_takeover, item["name"], timeout): item["name"] for item in items
        }
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()

    for item in items:
        item.update(results.get(item["name"], {}))
    return items
