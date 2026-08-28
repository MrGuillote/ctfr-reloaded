import pytest

from ctfr_reloaded.config import load_config, save_default_config, get_exclude_patterns
from ctfr_reloaded.domains import (
    clear_url,
    extract_names_from_entries,
    is_valid_domain,
    is_valid_subdomain,
    split_apex_subdomains,
)
from ctfr_reloaded.filters import apply_result_filters
from ctfr_reloaded.output import build_json_payload, detect_output_format
from ctfr_reloaded.scoring import score_subdomain, apply_exclude_patterns, enrich_scores
from ctfr_reloaded.scanner import filter_new_only
from ctfr_reloaded.sources import (
    extract_from_anubis,
    extract_from_certspotter,
    extract_from_crtsh,
    extract_from_hackertarget,
    extract_from_wayback,
    get_sources,
    FREE_SOURCES,
)
from ctfr_reloaded.enrichment import detect_cdn
from ctfr_reloaded.takeover_fingerprints import TAKEOVER_FINGERPRINTS


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


def test_extract_from_crtsh():
    entries = [{"name_value": "api.ejemplo.com\nwww.ejemplo.com"}]
    assert extract_from_crtsh(entries, "ejemplo.com") == ["api.ejemplo.com", "www.ejemplo.com"]


def test_extract_from_certspotter():
    entries = [{"dns_names": ["api.ejemplo.com", "*.ejemplo.com"]}]
    assert extract_from_certspotter(entries, "ejemplo.com", exclude_wildcards=True) == ["api.ejemplo.com"]


def test_extract_from_hackertarget():
    text = "api.ejemplo.com,1.2.3.4\nwww.ejemplo.com,1.2.3.5"
    result = extract_from_hackertarget(text, "ejemplo.com")
    assert "api.ejemplo.com" in result


def test_extract_from_anubis():
    text = "api.ejemplo.com\nwww.ejemplo.com"
    result = extract_from_anubis(text, "ejemplo.com")
    assert len(result) == 2


def test_extract_from_wayback():
    entries = [
        ["urlkey", "original"],
        ["key", "http://api.ejemplo.com/path"],
    ]
    result = extract_from_wayback(entries, "ejemplo.com")
    assert "api.ejemplo.com" in result


def test_free_sources_registry():
    sources = get_sources("all")
    names = [s[0] for s in sources]
    assert len(names) == 7
    assert "bufferover" in names
    assert "rapiddns" in names


def test_filter_new_only():
    baseline = {"www.ejemplo.com"}
    assert filter_new_only(["api.ejemplo.com", "www.ejemplo.com"], baseline) == ["api.ejemplo.com"]


def test_scoring():
    item = {"name": "admin.api.ejemplo.com", "resolved": True, "alive": True}
    assert score_subdomain(item) > 30


def test_exclude_patterns():
    items = [{"name": "staging.ejemplo.com"}, {"name": "api.ejemplo.com"}]
    result = apply_exclude_patterns(items, ["staging"])
    assert len(result) == 1


def test_detect_cdn_cloudflare():
    result = detect_cdn("test.com", {"server": "cloudflare", "cf-ray": "abc"})
    assert result["cdn"] == "cloudflare"


def test_detect_output_format_html():
    assert detect_output_format("out.html", False) == "html"


def test_build_json_payload():
    payload = build_json_payload({"ejemplo.com": [{"name": "www.ejemplo.com"}]})
    assert payload["count"] == 1


def test_takeover_fingerprints_not_empty():
    assert "github.io" in TAKEOVER_FINGERPRINTS


def test_config_defaults():
    config = load_config("/nonexistent/path/config.json")
    assert config["defaults"]["source"] == "all"
