import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ctfr_reloaded.constants import USER_AGENT


def create_session(retries, proxy=None, version="3.0.0"):
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT.format(version=version)})
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})

    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
