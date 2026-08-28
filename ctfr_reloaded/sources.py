import time

from ctfr_reloaded.domains import (
    extract_names_from_entries,
    is_valid_subdomain,
    sanitize_domain_for_url,
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
        last_error = None

        for attempt in range(1, retries + 1):
            console.debug(
                "Consultando crt.sh ({a}/{r}) para {d}".format(a=attempt, r=retries, d=domain)
            )
            try:
                response = session.get(url, timeout=timeout)
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(attempt)
                    continue
                raise RuntimeError("Error de conexion crt.sh para {d}: {e}".format(d=domain, e=exc))

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as exc:
                    last_error = exc
                    if attempt < retries:
                        time.sleep(attempt)
                        continue
                    raise RuntimeError("JSON invalido de crt.sh para {d}".format(d=domain))

            if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(attempt * 2)
                continue

            raise RuntimeError(
                "crt.sh respondio {c} para {d}".format(c=response.status_code, d=domain)
            )

        raise RuntimeError("Error de conexion crt.sh para {d}: {e}".format(d=domain, e=last_error))


class CertspotterSource(CertificateSource):
    name = "certspotter"
    url_template = (
        "https://api.certspotter.com/v1/issuances"
        "?domain={domain}&include_subdomains=true&expand=dns_names"
    )

    def fetch(self, session, domain, timeout, retries, console):
        safe_domain = sanitize_domain_for_url(domain)
        url = self.url_template.format(domain=safe_domain)
        last_error = None

        for attempt in range(1, retries + 1):
            console.debug(
                "Consultando certspotter ({a}/{r}) para {d}".format(
                    a=attempt, r=retries, d=domain
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
                    "Error de conexion certspotter para {d}: {e}".format(d=domain, e=exc)
                )

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as exc:
                    last_error = exc
                    if attempt < retries:
                        time.sleep(attempt)
                        continue
                    raise RuntimeError("JSON invalido de certspotter para {d}".format(d=domain))

            if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(attempt * 3)
                continue

            raise RuntimeError(
                "certspotter respondio {c} para {d}".format(c=response.status_code, d=domain)
            )

        raise RuntimeError(
            "Error de conexion certspotter para {d}: {e}".format(d=domain, e=last_error)
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


SOURCE_REGISTRY = {
    "crtsh": (CrtShSource(), extract_from_crtsh),
    "certspotter": (CertspotterSource(), extract_from_certspotter),
}


def get_sources(selected):
    if selected == "all":
        return list(SOURCE_REGISTRY.items())
    if selected not in SOURCE_REGISTRY:
        raise ValueError("Fuente desconocida: {s}".format(s=selected))
    return [(selected, SOURCE_REGISTRY[selected])]
