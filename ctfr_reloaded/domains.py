import re

DOMAIN_PATTERN = re.compile(
    r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$"
)


def clear_url(target):
    target = target.strip()
    if not target or target.startswith("#"):
        return None
    target = re.sub(r"^https?://", "", target, flags=re.IGNORECASE)
    target = re.sub(r"^www\.", "", target, flags=re.IGNORECASE)
    return target.split("/")[0].split(":")[0].strip().lower()


def is_valid_domain(domain):
    if not domain or len(domain) > 253:
        return False
    if ".." in domain or domain.startswith(".") or domain.endswith("."):
        return False
    return bool(DOMAIN_PATTERN.match(domain))


def sanitize_domain_for_url(domain):
    return re.sub(r"[^a-z0-9.\-]", "", domain.lower())


def load_domains_from_file(path, max_domains):
    domains = []
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                domain = clear_url(line)
                if domain:
                    if not is_valid_domain(domain):
                        raise ValueError("Dominio invalido en archivo: {d}".format(d=domain))
                    domains.append(domain)
                    if len(domains) > max_domains:
                        raise ValueError(
                            "El archivo supera el limite de {n} dominios.".format(n=max_domains)
                        )
    except OSError as exc:
        raise ValueError("No se pudo leer el archivo: {e}".format(e=exc)) from exc

    domains = list(dict.fromkeys(domains))
    if not domains:
        raise ValueError("El archivo no contiene dominios validos.")
    return domains


def is_valid_subdomain(subdomain, target):
    if not subdomain or "*" in subdomain:
        return False
    return subdomain == target or subdomain.endswith("." + target)


def extract_names_from_entries(entries, target, exclude_wildcards=False, field="name_value"):
    subdomains = set()
    for entry in entries:
        name_value = entry.get(field, "")
        if isinstance(name_value, list):
            names = name_value
        else:
            names = str(name_value).split("\n")
        for name in names:
            name = str(name).strip().lower()
            if not name:
                continue
            if exclude_wildcards and name.startswith("*."):
                continue
            if is_valid_subdomain(name, target):
                subdomains.add(name)
    return sorted(subdomains)


def split_apex_subdomains(subdomains, target):
    apex = sorted(name for name in subdomains if name == target)
    subs = sorted(name for name in subdomains if name != target)
    return apex, subs
