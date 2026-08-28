import pytest

from ctfr_reloaded.domains import (
    clear_url,
    extract_names_from_entries,
    is_valid_domain,
    is_valid_subdomain,
    split_apex_subdomains,
)
from ctfr_reloaded.output import build_json_payload, detect_output_format
from ctfr_reloaded.scanner import filter_new_only
from ctfr_reloaded.sources import extract_from_certspotter, extract_from_crtsh


def test_clear_url():
    assert clear_url("https://www.Ejemplo.com/path") == "ejemplo.com"
    assert clear_url("# comment") is None


def test_is_valid_domain():
    assert is_valid_domain("ejemplo.com")
    assert not is_valid_domain("..com")
    assert not is_valid_domain("invalid")


def test_is_valid_subdomain():
    assert is_valid_subdomain("api.ejemplo.com", "ejemplo.com")
    assert not is_valid_subdomain("api.otro.com", "ejemplo.com")
    assert not is_valid_subdomain("*.ejemplo.com", "ejemplo.com")


def test_extract_from_crtsh():
    entries = [{"name_value": "api.ejemplo.com\nwww.ejemplo.com"}]
    result = extract_from_crtsh(entries, "ejemplo.com")
    assert result == ["api.ejemplo.com", "www.ejemplo.com"]


def test_extract_from_certspotter():
    entries = [{"dns_names": ["api.ejemplo.com", "*.ejemplo.com"]}]
    result = extract_from_certspotter(entries, "ejemplo.com", exclude_wildcards=True)
    assert result == ["api.ejemplo.com"]


def test_split_apex_subdomains():
    apex, subs = split_apex_subdomains(
        ["ejemplo.com", "api.ejemplo.com", "www.ejemplo.com"], "ejemplo.com"
    )
    assert apex == ["ejemplo.com"]
    assert subs == ["api.ejemplo.com", "www.ejemplo.com"]


def test_filter_new_only():
    baseline = {"www.ejemplo.com"}
    result = filter_new_only(["api.ejemplo.com", "www.ejemplo.com"], baseline)
    assert result == ["api.ejemplo.com"]


def test_build_json_payload_single():
    payload = build_json_payload(
        {"ejemplo.com": [{"name": "www.ejemplo.com"}]}, version="3.0.0"
    )
    assert payload["count"] == 1
    assert payload["domain"] == "ejemplo.com"


def test_detect_output_format():
    assert detect_output_format("out.csv", False) == "csv"
    assert detect_output_format("out.txt", True) == "json"


def test_extract_names_multiline():
    entries = [{"name_value": "a.ejemplo.com\nb.ejemplo.com"}]
    names = extract_names_from_entries(entries, "ejemplo.com")
    assert len(names) == 2
