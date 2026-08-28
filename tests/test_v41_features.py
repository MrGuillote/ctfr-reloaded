import tempfile
from pathlib import Path

import pytest

from ctfr_reloaded.notifications import notify_watch, send_discord
from ctfr_reloaded.reports import save_pdf_output
from ctfr_reloaded.sources import extract_from_bufferover, extract_from_rapiddns
from ctfr_reloaded.tui import _filter_items


def test_extract_from_bufferover():
    data = {"FDNS_A": ["1.2.3.4,api.ejemplo.com"], "RDNS": []}
    result = extract_from_bufferover(data, "ejemplo.com")
    assert "api.ejemplo.com" in result


def test_extract_from_rapiddns():
    html = "<td>api.ejemplo.com</td><td>1.2.3.4</td>"
    result = extract_from_rapiddns(html, "ejemplo.com")
    assert "api.ejemplo.com" in result


def test_tui_filter():
    items = [
        ("ejemplo.com", {"name": "api.ejemplo.com"}),
        ("ejemplo.com", {"name": "staging.ejemplo.com"}),
    ]
    filtered = _filter_items(items, "api")
    assert len(filtered) == 1


def test_save_pdf_output():
    results = {"ejemplo.com": [{"name": "www.ejemplo.com", "score": 50}]}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "report.pdf"
        save_pdf_output(results, str(path))
        assert path.exists()
        assert path.stat().st_size > 100


@pytest.mark.parametrize("url", ["https://discord.com/api/webhooks/test"])
def test_notify_watch_no_crash(url):
    notify_watch("ejemplo.com", ["new.ejemplo.com"], discord_webhook=None)
