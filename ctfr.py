#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
	CTFR-Reloaded - Fork mejorado de CTFR por Sheila A. Berta (UnaPibaGeek)
------------------------------------------------------------------------------
"""

import argparse
import re
import sys

import requests

VERSION = "2.0.0"
CRTSH_URL = "https://crt.sh/?q=%.{domain}&output=json"
USER_AGENT = "ctfr-reloaded/{version}".format(version=VERSION)
REQUEST_TIMEOUT = 30


def parse_args():
    parser = argparse.ArgumentParser(
        description="Obtiene subdominios desde Certificate Transparency logs (crt.sh)."
    )
    parser.add_argument("-d", "--domain", type=str, required=True, help="Dominio objetivo.")
    parser.add_argument("-o", "--output", type=str, help="Archivo de salida.")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Solo muestra el conteo final."
    )
    parser.add_argument(
        "--no-wildcards",
        action="store_true",
        help="Excluir entradas con wildcard (*.dominio.com).",
    )
    return parser.parse_args()


def banner():
    print(
        """
          ____ _____ _____ ____  
         / ___|_   _|  ___|  _ \ 
        | |     | | | |_  | |_) |
        | |___  | | |  _| |  _ < 
         \____| |_| |_|   |_| \_\\

     CTFR-Reloaded v{v}
     Fork mejorado de CTFR (Sheila A. Berta / UnaPibaGeek)
    """.format(v=VERSION)
    )


def clear_url(target):
    target = target.strip()
    target = re.sub(r"^https?://", "", target, flags=re.IGNORECASE)
    target = re.sub(r"^www\.", "", target, flags=re.IGNORECASE)
    return target.split("/")[0].split(":")[0].strip()


def is_valid_subdomain(subdomain, target):
    if not subdomain or "*" in subdomain:
        return False
    return subdomain == target or subdomain.endswith("." + target)


def extract_subdomains(entries, target, exclude_wildcards=False):
    subdomains = set()
    for entry in entries:
        name_value = entry.get("name_value", "")
        for name in name_value.split("\n"):
            name = name.strip().lower()
            if not name:
                continue
            if exclude_wildcards and name.startswith("*."):
                continue
            if is_valid_subdomain(name, target):
                subdomains.add(name)
    return sorted(subdomains)


def fetch_certificates(target):
    url = CRTSH_URL.format(domain=target)
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        print("[X] Error de conexion: {e}".format(e=exc))
        sys.exit(1)

    if response.status_code != 200:
        print("[X] crt.sh respondio con codigo {c}".format(c=response.status_code))
        sys.exit(1)

    try:
        return response.json()
    except ValueError:
        print("[X] La respuesta de crt.sh no es JSON valido.")
        sys.exit(1)


def save_subdomains(subdomains, output_file):
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(subdomains) + "\n")


def main():
    args = parse_args()

    if not args.quiet:
        banner()

    target = clear_url(args.domain)
    entries = fetch_certificates(target)
    subdomains = extract_subdomains(entries, target, exclude_wildcards=args.no_wildcards)

    if not args.quiet:
        print("\n[!] ---- TARGET: {d} ---- [!]\n".format(d=target))

    for subdomain in subdomains:
        if not args.quiet:
            print("[-]  {s}".format(s=subdomain))

    if args.output:
        save_subdomains(subdomains, args.output)

    if args.quiet:
        print("{n}".format(n=len(subdomains)))
    else:
        print("\n\n[!]  {n} subdominios encontrados. Listo!".format(n=len(subdomains)))


if __name__ == "__main__":
    main()
