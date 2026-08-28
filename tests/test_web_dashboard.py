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
    assert stats["distribution"]["25-39"] == 1
    assert stats["distribution"]["0-14"] == 1
    assert stats["distribution"]["15-24"] == 1
    assert "api" in stats["keywords"]


def test_score_distribution_high_scores():
    stats = compute_report_stats(
        {
            "ejemplo.com": [
                {"name": "api.ejemplo.com", "score": 65},
                {"name": "www.ejemplo.com", "score": 50},
                {"name": "dev.ejemplo.com", "score": 25},
            ]
        }
    )
    assert stats["distribution"]["60-100"] == 1
    assert stats["distribution"]["40-59"] == 1
    assert stats["distribution"]["25-39"] == 1


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
    assert "Consola de actividad" in html
    assert "/scan/stream" in html
    assert "ctfr-reloaded-dashboard-v1" in html
    assert 'id="activity-open"' in html


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


def test_stream_console_emits_events():
    from ctfr_reloaded.stream_console import StreamConsole

    events = []
    console = StreamConsole(on_event=events.append)
    console.info("inicio")
    console.debug("consultando fuente")
    console.warn("fuente fallo")
    assert len(events) == 3
    assert events[0]["level"] == "info"
    assert events[1]["level"] == "debug"
    assert "time" in events[0]


def test_scan_stream_route(api_client, mocker):
    mocker.patch(
        "ctfr_reloaded.api.run_scan",
        return_value={"ejemplo.com": [{"name": "api.ejemplo.com", "score": 25}]},
    )
    with api_client.stream("GET", "/scan/stream", params={"domain": "ejemplo.com"}) as response:
        assert response.status_code == 200
        body = response.read().decode("utf-8")
    assert "event: log" in body
    assert "event: result" in body
    assert "api.ejemplo.com" in body
