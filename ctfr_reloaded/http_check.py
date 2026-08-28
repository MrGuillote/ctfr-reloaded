from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def check_alive(name, timeout=5, session=None):
    session = session or requests.Session()
    for scheme in ("https", "http"):
        url = "{scheme}://{name}".format(scheme=scheme, name=name)
        try:
            response = session.head(url, timeout=timeout, allow_redirects=True)
            return {
                "name": name,
                "alive": True,
                "url": response.url,
                "status_code": response.status_code,
            }
        except requests.RequestException:
            continue
    return {"name": name, "alive": False, "url": None, "status_code": None}


def check_alive_batch(names, threads=10, timeout=5, session=None):
    session = session or requests.Session()
    results = {}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_alive, name, timeout, session): name for name in names
        }
        for future in as_completed(futures):
            item = future.result()
            results[item["name"]] = item
    return [results[name] for name in names if name in results]
