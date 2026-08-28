import csv
import json
import sys

from ctfr_reloaded import __version__
from ctfr_reloaded.reports import save_html_output, save_pdf_output


def names_from_results(results):
    names = []
    for items in results.values():
        for item in items:
            names.append(item["name"])
    return names


def build_json_payload(results, version=None):
    version = version or __version__
    total = sum(len(items) for items in results.values())

    if len(results) == 1:
        domain = next(iter(results))
        items = results[domain]
        return {
            "tool": "ctfr-reloaded",
            "version": version,
            "domain": domain,
            "count": len(items),
            "subdomains": items,
        }

    return {
        "tool": "ctfr-reloaded",
        "version": version,
        "total": total,
        "results": {
            domain: {"count": len(items), "subdomains": items}
            for domain, items in results.items()
        },
    }


def urls_from_results(results, alive_only=False):
    urls = []
    seen = set()
    for items in results.values():
        for item in items:
            if alive_only and not item.get("alive"):
                continue
            url = item.get("url") or "https://{name}".format(name=item["name"])
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def save_burp_output(results, output_file, alive_only=False):
    urls = urls_from_results(results, alive_only=alive_only)
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(urls) + ("\n" if urls else ""))
    return len(urls)


def save_plain_output(results, output_file):
    lines = names_from_results(results)
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + ("\n" if lines else ""))


def save_json_output(results, output_file):
    payload = build_json_payload(results)
    with open(output_file, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def save_csv_output(results, output_file):
    fieldnames = [
        "domain", "subdomain", "score", "resolved", "addresses",
        "alive", "url", "status_code", "cname", "service", "vulnerable",
        "cdn", "tls_issuer", "tls_expires",
    ]
    with open(output_file, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for domain, items in results.items():
            for item in items:
                writer.writerow(
                    {
                        "domain": domain,
                        "subdomain": item["name"],
                        "score": item.get("score", ""),
                        "resolved": item.get("resolved", ""),
                        "addresses": ",".join(item.get("addresses", []) or []),
                        "alive": item.get("alive", ""),
                        "url": item.get("url", "") or "",
                        "status_code": item.get("status_code", "") or "",
                        "cname": item.get("cname", "") or "",
                        "service": item.get("service", "") or "",
                        "vulnerable": item.get("vulnerable", ""),
                        "cdn": item.get("cdn", "") or "",
                        "tls_issuer": item.get("tls_issuer", "") or "",
                        "tls_expires": item.get("tls_expires", "") or "",
                    }
                )


def detect_output_format(output_path, json_flag, explicit_format=None):
    if explicit_format:
        return explicit_format
    if json_flag:
        return "json"
    if output_path:
        lower = output_path.lower()
        if lower.endswith(".csv"):
            return "csv"
        if lower.endswith(".html"):
            return "html"
        if lower.endswith(".pdf"):
            return "pdf"
        if lower.endswith(".json"):
            return "json"
        if lower.endswith("-burp.txt") or lower.endswith(".burp.txt"):
            return "burp"
    return "plain"


def save_output(results, output_path, output_format, alive_only=False):
    if output_format == "json":
        save_json_output(results, output_path)
    elif output_format == "csv":
        save_csv_output(results, output_path)
    elif output_format == "html":
        save_html_output(results, output_path)
    elif output_format == "pdf":
        save_pdf_output(results, output_path)
    elif output_format == "burp":
        return save_burp_output(results, output_path, alive_only=alive_only)
    else:
        save_plain_output(results, output_path)
    return None


def format_subdomain_extra(item):
    parts = []
    if item.get("score") is not None:
        parts.append("score:{s}".format(s=item["score"]))
    if "resolved" in item:
        parts.append("DNS" if item["resolved"] else "NO-DNS")
    if "alive" in item:
        parts.append("HTTP" if item["alive"] else "NO-HTTP")
    if item.get("vulnerable"):
        parts.append("TAKEOVER:{s}".format(s=item.get("service", "?")))
    if item.get("cdn"):
        parts.append("CDN:{c}".format(c=item["cdn"]))
    if item.get("status_code"):
        parts.append(str(item["status_code"]))
    return "({p})".format(p=", ".join(parts)) if parts else ""


def print_text_results(results, console, quiet):
    total = 0
    for domain, items in results.items():
        if not quiet:
            console.warn("---- TARGET: {d} ----".format(d=domain))
        for item in items:
            if not quiet:
                console.subdomain(item["name"], format_subdomain_extra(item))
        total += len(items)

    if quiet:
        print(total)
    else:
        console.success("{n} subdominios encontrados. Listo!".format(n=total))


def print_json_results(results):
    print(json.dumps(build_json_payload(results), indent=2, ensure_ascii=False))


def emit_results(results, args, console):
    output_format = detect_output_format(args.output, args.json, getattr(args, "format", None))
    if getattr(args, "burp", False) and not getattr(args, "format", None):
        output_format = "burp"
    alive_only = getattr(args, "alive_only", False)
    burp_urls = urls_from_results(results, alive_only=alive_only) if output_format == "burp" else None

    if args.pipe:
        if burp_urls is not None:
            for url in burp_urls:
                print(url)
        else:
            for name in names_from_results(results):
                print(name)
        if args.output:
            save_output(results, args.output, output_format, alive_only=alive_only)
        return

    if args.json:
        print_json_results(results)
    else:
        print_text_results(results, console, args.quiet)

    if args.output:
        count = save_output(results, args.output, output_format, alive_only=alive_only)
        if getattr(args, "burp", False) and not args.quiet:
            if output_format == "burp" and count is not None:
                console.info("{n} URLs exportadas para Burp Suite.".format(n=count))
            console.info("Burp -> Target -> Scope -> Add -> Paste URL(s)")
            console.info("Archivo: {p}".format(p=args.output))
