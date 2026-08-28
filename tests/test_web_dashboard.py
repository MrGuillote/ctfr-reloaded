import json

import pytest

from ctfr_reloaded.reports import compute_report_stats, render_html_report, save_html_output
from ctfr_reloaded.web import render_dashboard


@pytest.fixture
def sample_results():
    return {
        "ejemplo.com": [
            {"name": "api.ejemplo.com", "score": 25, "resolved": True, "alive": True},
            {"name": "www.ejemplo.com", "score": 10},
            {"name": "ejemplo.com", "score": 15},
        ]
    }


def test_compute_report_stats(sample_results):
    stats = compute_report_stats(sample_results)
    assert stats["total"] == 3
    assert stats["high_score"] == 1
    assert stats["resolved"] == 1
    assert stats["alive"] == 1
    assert stats["avg_score"] == 16.7
    assert stats["distribution"]["25+"] == 1
    assert "api" in stats["keywords"]


def test_render_html_report_contains_stats(sample_results):
    document = render_html_report(sample_results)
    assert "api.ejemplo.com" in document
    assert "Distribucion de scores" in document
    assert "Score alto" in document


def test_save_html_output(tmp_path, sample_results):
    output = tmp_path / "report.html"
    save_html_output(sample_results, output)
    content = output.read_text(encoding="utf-8")
    assert "CTFR-Reloaded Report" in content
    assert "api.ejemplo.com" in content


def test_render_dashboard_contains_form():
    html = render_dashboard("4.2.0", ["crtname", "crtsh"])
    assert "CTFR-Reloaded" in html
    assert 'id="scan-form"' in html
    assert "crtname" in html
    assert "/docs" in html


@pytest.fixture
def api_client():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from ctfr_reloaded.api import create_app

    return TestClient(create_app())


def test_dashboard_route(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert "CTFR-Reloaded" in response.text
    assert "Nuevo scan" in response.text


def test_report_route(api_client):
    payload = {
        "tool": "ctfr-reloaded",
        "version": "4.2.0",
        "domain": "ejemplo.com",
        "count": 1,
        "subdomains": [{"name": "api.ejemplo.com", "score": 25}],
    }
    response = api_client.post("/report", json=payload)
    assert response.status_code == 200
    assert "api.ejemplo.com" in response.text
    assert "Subdominios" in response.text


def test_scan_route_mocked(api_client, mocker):
    mocked = mocker.patch(
        "ctfr_reloaded.api.run_scan",
        return_value={"ejemplo.com": [{"name": "api.ejemplo.com", "score": 25}]},
    )
    response = api_client.get("/scan", params={"domain": "ejemplo.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "ejemplo.com"
    assert data["subdomains"][0]["name"] == "api.ejemplo.com"
    mocked.assert_called_once()
