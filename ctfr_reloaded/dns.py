import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


def resolve_subdomain(name, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        records = socket.getaddrinfo(name, None)
        addresses = sorted({item[4][0] for item in records})
        return {"name": name, "resolved": True, "addresses": addresses}
    except socket.gaierror:
        return {"name": name, "resolved": False, "addresses": []}


def resolve_subdomains(names, threads=10, timeout=3):
    results = {}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(resolve_subdomain, name, timeout): name for name in names}
        for future in as_completed(futures):
            item = future.result()
            results[item["name"]] = item
    return [results[name] for name in names if name in results]
