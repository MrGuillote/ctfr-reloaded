import re

import pytest
import responses

from ctfr_reloaded.scanner import scan_domains
from ctfr_reloaded.console import Console
from types import SimpleNamespace


@pytest.fixture
def scan_options():
    return SimpleNamespace(
        source="crtsh",
        timeout=10,
        retries=1,
        threads=1,
        proxy=None,
        resolve=False,
        alive=False,
        resolved_only=False,
        alive_only=False,
        takeover=False,
        takeover_only=False,
        tls=False,
        cdn=False,
        score=False,
        no_wildcards=False,
        apex_only=False,
        subdomains_only=False,
        new_only=False,
        baseline_set=set(),
        cache=False,
        cache_dir=None,
        cache_ttl=3600,
        rate_limit=0,
        merge_subfinder=False,
        merge_amass=False,
        merge_assetfinder=False,
        show_progress=False,
        use_tqdm=False,
        exclude_patterns=[],
        history_enabled=False,
        version="4.1.0",
    )


@responses.activate
def test_integration_crtsh_scan(scan_options):
    responses.add(
        responses.GET,
        re.compile(r"https://crt\.sh/.*"),
        json=[{"name_value": "api.ejemplo.com\nwww.ejemplo.com"}],
        status=200,
    )

    console = Console(verbose=False, use_colors=False)
    results = scan_domains(["ejemplo.com"], scan_options, console)
    names = [item["name"] for item in results["ejemplo.com"]]
    assert "api.ejemplo.com" in names
    assert "www.ejemplo.com" in names


@responses.activate
def test_integration_anubis_source(scan_options):
    scan_options.source = "anubis"
    responses.add(
        responses.GET,
        "https://jldc.me/anubis/subdomains/ejemplo.com.txt",
        body="dev.ejemplo.com\napi.ejemplo.com",
        status=200,
    )

    console = Console(verbose=False, use_colors=False)
    results = scan_domains(["ejemplo.com"], scan_options, console)
    names = [item["name"] for item in results["ejemplo.com"]]
    assert "api.ejemplo.com" in names


@responses.activate
def test_integration_hackertarget_source(scan_options):
    scan_options.source = "hackertarget"
    responses.add(
        responses.GET,
        re.compile(r"https://api\.hackertarget\.com/.*"),
        body="mail.ejemplo.com,1.2.3.4",
        status=200,
    )

    console = Console(verbose=False, use_colors=False)
    results = scan_domains(["ejemplo.com"], scan_options, console)
    names = [item["name"] for item in results["ejemplo.com"]]
    assert "mail.ejemplo.com" in names


@responses.activate
def test_integration_crtname_source(scan_options):
    scan_options.source = "crtname"
    responses.add(
        responses.GET,
        "https://crt.name/v1/search?apex=ejemplo.com",
        body="api.ejemplo.com\nwww.ejemplo.com",
        status=200,
    )

    console = Console(verbose=False, use_colors=False)
    results = scan_domains(["ejemplo.com"], scan_options, console)
    names = [item["name"] for item in results["ejemplo.com"]]
    assert "api.ejemplo.com" in names


@responses.activate
def test_integration_bufferover_source(scan_options):
    scan_options.source = "bufferover"
    responses.add(
        responses.GET,
        re.compile(r"https://tls\.bufferover\.run/.*"),
        json={"FDNS_A": ["1.2.3.4,api.ejemplo.com"], "RDNS": []},
        status=200,
    )

    console = Console(verbose=False, use_colors=False)
    results = scan_domains(["ejemplo.com"], scan_options, console)
    names = [item["name"] for item in results["ejemplo.com"]]
    assert "api.ejemplo.com" in names
