import ssl
import socket
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

CDN_PATTERNS = {
    "cloudflare": ["cloudflare", "cf-ray"],
    "aws": ["cloudfront", "x-amz-cf-id", "x-amz-request-id"],
    "fastly": ["fastly", "x-served-by"],
    "akamai": ["akamai", "x-akamai"],
    "azure": ["azure", "x-azure-ref"],
    "google": ["gws", "gse", "google"],
}


def get_tls_info(name, timeout=5, port=443):
    info = {"tls": False, "tls_issuer": None, "tls_expires": None, "tls_version": None}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((name, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=name) as ssock:
                cert = ssock.getpeercert()
                info["tls"] = True
                info["tls_version"] = ssock.version()
                if cert:
                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    info["tls_issuer"] = issuer.get("organizationName", issuer.get("commonName", ""))
                    not_after = cert.get("notAfter")
                    if not_after:
                        info["tls_expires"] = not_after
    except Exception:
        pass
    return info


def detect_cdn(name, headers=None):
    detected = []
    headers = headers or {}

    header_blob = " ".join(
        "{k}:{v}".format(k=k.lower(), v=str(v).lower()) for k, v in headers.items()
    )

    for cdn, patterns in CDN_PATTERNS.items():
        if any(p in header_blob for p in patterns):
            detected.append(cdn)

    cname_hints = []
    name_lower = name.lower()
    if "cloudflare" in name_lower:
        cname_hints.append("cloudflare")

    all_cdns = sorted(set(detected + cname_hints))
    return {"cdn": all_cdns[0] if all_cdns else None, "cdns": all_cdns}


def enrich_tls_cdn(items, session=None, threads=10, timeout=5):
    import requests

    session = session or requests.Session()
    results = {}

    def _enrich_one(item):
        name = item["name"]
        data = dict(item)
        data.update(get_tls_info(name, timeout=timeout))
        headers = {}
        try:
            response = session.head(
                "https://{n}".format(n=name), timeout=timeout, allow_redirects=True
            )
            headers = dict(response.headers)
        except requests.RequestException:
            pass
        data.update(detect_cdn(name, headers))
        return name, data

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(_enrich_one, item): item["name"] for item in items}
        for future in as_completed(futures):
            name, data = future.result()
            results[name] = data

    return [results[item["name"]] for item in items if item["name"] in results]
