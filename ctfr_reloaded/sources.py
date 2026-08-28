import re
import time

from ctfr_reloaded.domains import (
    extract_names_from_entries,
    is_valid_subdomain,
    sanitize_domain_for_url,
)

# Fuentes 100% gratuitas, sin API key ni registro.
FREE_SOURCES = (
    "crtsh",
    "crtname",
    "certspotter",
    "hackertarget",
    "wayback",
    "anubis",
    "bufferover",
    "rapiddns",
)


class CertificateSource:
    name = "base"

    def fetch(self, session, domain, timeout, retries, console):
        raise NotImplementedError


class CrtShSource(CertificateSource):
    name = "crtsh"
    url_template = "https://crt.sh/?q=%.{domain}&output=json"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        # crt.sh suele ser lento; dar mas margen de lectura
        effective_timeout = max(timeout, 60)
        return _fetch_json(
            session, url, domain, effective_timeout, retries, console, self.name
        )


class CrtNameSource(CertificateSource):
    name = "crtname"
    url_template = "https://crt.name/v1/search?apex={domain}"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_text(session, url, domain, timeout, retries, console, self.name)


class CertspotterSource(CertificateSource):
    name = "certspotter"
    url_template = (
        "https://api.certspotter.com/v1/issuances"
        "?domain={domain}&include_subdomains=true&expand=dns_names"
    )

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_json(session, url, domain, timeout, retries, console, self.name)


class HackerTargetSource(CertificateSource):
    name = "hackertarget"
    url_template = "https://api.hackertarget.com/hostsearch/?q={domain}"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_text(session, url, domain, timeout, retries, console, self.name)


class WaybackSource(CertificateSource):
    name = "wayback"
    url_template = (
        "https://web.archive.org/cdx/search/cdx"
        "?url=*.{domain}/*&output=json&fl=original&collapse=urlkey&limit=5000"
    )

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_json(session, url, domain, timeout, retries, console, self.name)


class AnubisSource(CertificateSource):
    name = "anubis"
    url_template = "https://jldc.me/anubis/subdomains/{domain}.txt"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_text(session, url, domain, timeout, retries, console, self.name)


class BufferoverSource(CertificateSource):
    name = "bufferover"
    url_template = "https://tls.bufferover.run/dns?q=.{domain}"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_json(session, url, domain, timeout, retries, console, self.name)


class RapidDnsSource(CertificateSource):
    name = "rapiddns"
    url_template = "https://rapiddns.io/subdomain/{domain}?full=1"

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        return _fetch_text(session, url, domain, timeout, retries, console, self.name)


def _fetch_json(session, url, domain, timeout, retries, console, source_name):
    response = _request(session, url, domain, timeout, retries, console, source_name)
    if response.status_code == 404:
        return []
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            "JSON invalido de {s} para {d}".format(s=source_name, d=domain)
        ) from exc


def _fetch_text(session, url, domain, timeout, retries, console, source_name):
    response = _request(session, url, domain, timeout, retries, console, source_name)
    if response.status_code == 404:
        return ""
    return response.text


def _request(session, url, domain, timeout, retries, console, source_name):
    last_error = None
    for attempt in range(1, retries + 1):
        console.debug(
            "Consultando {s} ({a}/{r}) para {d}".format(
                s=source_name, a=attempt, r=retries, d=domain
            )
        )
        try:
            response = session.get(url, timeout=timeout)
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(attempt)
                continue
            raise RuntimeError(
                "Error de conexion {s} para {d}: {e}".format(s=source_name, d=domain, e=exc)
            )

        if response.status_code == 200:
            return response

        if response.status_code == 404:
            return response

        if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(attempt * 2)
            continue

        raise RuntimeError(
            "{s} respondio {c} para {d}".format(s=source_name, c=response.status_code, d=domain)
        )

    raise RuntimeError(
        "Error de conexion {s} para {d}: {e}".format(s=source_name, d=domain, e=last_error)
    )


def extract_from_crtsh(entries, target, exclude_wildcards=False):
    return extract_names_from_entries(entries, target, exclude_wildcards, field="name_value")


def extract_from_certspotter(entries, target, exclude_wildcards=False):
    subdomains = set()
    for entry in entries:
        for name in entry.get("dns_names", []):
            name = name.strip().lower()
            if not name:
                continue
            if exclude_wildcards and name.startswith("*."):
                continue
            if is_valid_subdomain(name, target):
                subdomains.add(name)
    return sorted(subdomains)


def extract_from_hackertarget(text, target, exclude_wildcards=False):
    subdomains = set()
    for line in str(text).splitlines():
        host = line.split(",")[0].strip().lower()
        if not host:
            continue
        if exclude_wildcards and host.startswith("*."):
            continue
        if is_valid_subdomain(host, target):
            subdomains.add(host)
    return sorted(subdomains)


def extract_from_wayback(entries, target, exclude_wildcards=False):
    subdomains = set()
    if not entries:
        return []
    for row in entries[1:]:
        if not row:
            continue
        url = None
        for cell in row:
            if "://" in str(cell):
                url = cell
                break
        if not url:
            continue
        match = re.search(r"https?://([^/]+)", url, re.IGNORECASE)
        if not match:
            continue
        host = match.group(1).split(":")[0].strip().lower()
        if exclude_wildcards and host.startswith("*."):
            continue
        if is_valid_subdomain(host, target):
            subdomains.add(host)
    return sorted(subdomains)


def extract_from_anubis(text, target, exclude_wildcards=False):
    return _extract_lines(text, target, exclude_wildcards)


def extract_from_crtname(text, target, exclude_wildcards=False):
    return _extract_lines(text, target, exclude_wildcards)


def _extract_lines(text, target, exclude_wildcards=False):
    subdomains = set()
    for line in str(text).splitlines():
        host = line.strip().lower()
        if not host:
            continue
        if exclude_wildcards and host.startswith("*."):
            continue
        if is_valid_subdomain(host, target):
            subdomains.add(host)
    return sorted(subdomains)


def extract_from_bufferover(entries, target, exclude_wildcards=False):
    subdomains = set()
    if not isinstance(entries, dict):
        return []
    for key in ("FDNS_A", "RDNS"):
        for item in entries.get(key, []):
            if "," in str(item):
                host = str(item).split(",")[1].strip().lower()
            else:
                host = str(item).strip().lower()
            if not host:
                continue
            if exclude_wildcards and host.startswith("*."):
                continue
            if is_valid_subdomain(host, target):
                subdomains.add(host)
    return sorted(subdomains)


def extract_from_rapiddns(html, target, exclude_wildcards=False):
    subdomains = set()
    for match in re.finditer(
        r'<td>([a-z0-9][a-z0-9.\-]*\.{domain})</td>'.format(domain=re.escape(target)),
        str(html),
        re.IGNORECASE,
    ):
        host = match.group(1).strip().lower()
        if exclude_wildcards and host.startswith("*."):
            continue
        if is_valid_subdomain(host, target):
            subdomains.add(host)
    if subdomains:
        return sorted(subdomains)
    for match in re.finditer(
        r"([a-z0-9][a-z0-9\-]*\." + re.escape(target) + r")",
        str(html),
        re.IGNORECASE,
    ):
        host = match.group(1).strip().lower()
        if exclude_wildcards and host.startswith("*."):
            continue
        if is_valid_subdomain(host, target):
            subdomains.add(host)
    return sorted(subdomains)


SOURCE_REGISTRY = {
    "crtsh": (CrtShSource(), extract_from_crtsh),
    "crtname": (CrtNameSource(), extract_from_crtname),
    "certspotter": (CertspotterSource(), extract_from_certspotter),
    "hackertarget": (HackerTargetSource(), extract_from_hackertarget),
    "wayback": (WaybackSource(), extract_from_wayback),
    "anubis": (AnubisSource(), extract_from_anubis),
    "bufferover": (BufferoverSource(), extract_from_bufferover),
    "rapiddns": (RapidDnsSource(), extract_from_rapiddns),
}


def get_sources(selected):
    if selected == "all":
        return list(SOURCE_REGISTRY.items())

    if selected not in SOURCE_REGISTRY:
        raise ValueError("Fuente desconocida: {s}".format(s=selected))

    return [(selected, SOURCE_REGISTRY[selected])]
