import html
import json
from datetime import datetime, timezone

from ctfr_reloaded import __version__
from ctfr_reloaded.scoring import HIGH_VALUE_KEYWORDS

# Rangos reales de score (0-100), no valores discretos sueltos.
SCORE_BUCKETS = (
    ("0-14", 0, 14),
    ("15-24", 15, 24),
    ("25-39", 25, 39),
    ("40-59", 40, 59),
    ("60-100", 60, 100),
)


def compute_score_distribution(scores):
    distribution = {label: 0 for label, _, _ in SCORE_BUCKETS}
    for raw_score in scores:
        score = int(raw_score or 0)
        for label, low, high in SCORE_BUCKETS:
            if low <= score <= high:
                distribution[label] += 1
                break
    return distribution


def flatten_results(results):
    rows = []
    for domain, items in results.items():
        for item in items:
            rows.append({"domain": domain, **item})
    return rows


def compute_report_stats(results):
    rows = flatten_results(results)
    scores = [int(item.get("score") or 0) for item in rows]
    keywords = {}
    for item in rows:
        name = item.get("name", "").lower()
        for keyword in HIGH_VALUE_KEYWORDS:
            if keyword in name:
                keywords[keyword] = keywords.get(keyword, 0) + 1

    distribution = compute_score_distribution(scores)

    return {
        "total": len(rows),
        "domains": len(results),
        "high_score": sum(1 for score in scores if score >= 25),
        "resolved": sum(1 for item in rows if item.get("resolved")),
        "alive": sum(1 for item in rows if item.get("alive")),
        "takeover": sum(1 for item in rows if item.get("vulnerable") or item.get("takeover")),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "distribution": distribution,
        "keywords": dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True)[:8]),
    }


def _format_bool_cell(item, key):
    if key not in item:
        return "-"
    return "yes" if item.get(key) else "no"


def report_styles():
    return """
    :root {
      --bg: #0b1220;
      --surface: rgba(22, 32, 54, 0.82);
      --surface-2: rgba(30, 42, 68, 0.92);
      --border: rgba(120, 145, 190, 0.22);
      --text: #f3f6fc;
      --muted: #9db0d1;
      --accent: #4da3ff;
      --accent-2: #7c5cff;
      --success: #3dd68c;
      --warning: #ffb357;
      --danger: #ff6b7a;
      --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
      --radius: 14px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "Segoe UI Variable", system-ui, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(77, 163, 255, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(124, 92, 255, 0.16), transparent 24%),
        linear-gradient(180deg, #0b1220 0%, #10182a 100%);
      min-height: 100vh;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .shell { max-width: 1280px; margin: 0 auto; padding: 28px 20px 48px; }
    .content-stack { display: flex; flex-direction: column; gap: 18px; }
    .stack { display: flex; flex-direction: column; gap: 18px; }
    .stack .panel + .panel { margin-top: 0; }
    .hero {
      display: flex; justify-content: space-between; gap: 16px; align-items: flex-start;
      margin-bottom: 24px; flex-wrap: wrap;
    }
    .hero h1 { margin: 0 0 8px; font-size: 2rem; letter-spacing: -0.03em; }
    .hero p { margin: 0; color: var(--muted); max-width: 720px; line-height: 1.5; }
    .badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 10px; border-radius: 999px;
      background: rgba(77, 163, 255, 0.12); border: 1px solid var(--border);
      color: var(--muted); font-size: 0.82rem;
    }
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }
    .panel + .panel { margin-top: 0; }
    .panel-header {
      padding: 16px 18px; border-bottom: 1px solid var(--border);
      display: flex; justify-content: space-between; align-items: center; gap: 12px;
    }
    .panel-header h2 { margin: 0; font-size: 1rem; }
    .panel-body { padding: 18px; }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 14px;
    }
    .stat {
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }
    .stat .label { color: var(--muted); font-size: 0.82rem; margin-bottom: 8px; }
    .stat .value { font-size: 1.8rem; font-weight: 700; line-height: 1; }
    .stat .hint { color: var(--muted); font-size: 0.78rem; margin-top: 8px; }
    .stat.accent .value { color: var(--accent); }
    .stat.success .value { color: var(--success); }
    .stat.warning .value { color: var(--warning); }
    .stat.danger .value { color: var(--danger); }
    .bars { display: grid; gap: 10px; }
    .bar-row { display: grid; grid-template-columns: 72px 1fr 42px; gap: 10px; align-items: center; }
    .bar-track {
      height: 10px; border-radius: 999px; background: rgba(255,255,255,0.06); overflow: hidden;
    }
    .bar-fill {
      height: 100%; border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }
    .keywords { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip {
      padding: 6px 10px; border-radius: 999px;
      background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      color: var(--muted); font-size: 0.82rem;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td {
      padding: 11px 12px; border-bottom: 1px solid var(--border);
      text-align: left; font-size: 0.9rem;
    }
    th { color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }
    tr:hover td { background: rgba(255,255,255,0.03); }
    .score-pill {
      display: inline-flex; min-width: 42px; justify-content: center;
      padding: 4px 8px; border-radius: 999px; font-weight: 700; font-size: 0.82rem;
      background: rgba(77, 163, 255, 0.14); color: var(--accent);
    }
    .score-pill.high { background: rgba(255, 179, 87, 0.16); color: var(--warning); }
    .score-pill.critical { background: rgba(255, 107, 122, 0.16); color: var(--danger); }
    .yes { color: var(--success); }
    .no { color: var(--muted); }
    .vuln { color: var(--danger); font-weight: 600; }
    .meta { color: var(--muted); font-size: 0.88rem; }
    .grid-2 { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; align-items: stretch; }
    .grid-2 .panel { height: 100%; margin: 0; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
    details summary { cursor: pointer; color: var(--muted); }
    details p, details ul { color: var(--muted); line-height: 1.55; }
    """


def _render_stats_cards(stats):
  return """
  <div class="stats">
    <div class="stat accent"><div class="label">Subdominios</div><div class="value">{total}</div><div class="hint">{domains} dominio(s)</div></div>
    <div class="stat warning"><div class="label">Score alto</div><div class="value">{high_score}</div><div class="hint">score &ge; 25</div></div>
    <div class="stat success"><div class="label">Resueltos</div><div class="value">{resolved}</div><div class="hint">DNS</div></div>
    <div class="stat success"><div class="label">Vivos</div><div class="value">{alive}</div><div class="hint">HTTP</div></div>
    <div class="stat danger"><div class="label">Takeover</div><div class="value">{takeover}</div><div class="hint">candidatos</div></div>
    <div class="stat"><div class="label">Score medio</div><div class="value">{avg_score}</div><div class="hint">max {max_score}</div></div>
  </div>
  """.format(**stats)


def _render_distribution(stats):
    total = stats["total"] or 1
    rows = []
    for label, count in stats["distribution"].items():
        width = max(4, int((count / total) * 100))
        rows.append(
            '<div class="bar-row"><div>{label}</div><div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div><div>{count}</div></div>'.format(
                label=html.escape(label),
                width=width,
                count=count,
            )
        )
    return '<div class="bars">{rows}</div>'.format(rows="".join(rows))


def _render_keywords(stats):
    if not stats["keywords"]:
        return '<p class="meta">Sin keywords destacadas en este scan.</p>'
    chips = []
    for keyword, count in stats["keywords"].items():
        chips.append(
            '<span class="chip">{keyword} <strong>{count}</strong></span>'.format(
                keyword=html.escape(keyword),
                count=count,
            )
        )
    return '<div class="keywords">{chips}</div>'.format(chips="".join(chips))


def _score_class(score):
    if score >= 50:
        return "critical"
    if score >= 25:
        return "high"
    return ""


def _render_table_rows(results):
    rows = []
    for domain, items in results.items():
        for item in items:
            score = int(item.get("score") or 0)
            takeover = item.get("service", "") if item.get("vulnerable") else "-"
            rows.append(
                "<tr>"
                "<td>{domain}</td>"
                "<td><strong>{name}</strong></td>"
                "<td><span class=\"score-pill {score_class}\">{score}</span></td>"
                "<td class=\"{resolved_class}\">{resolved}</td>"
                "<td class=\"{alive_class}\">{alive}</td>"
                "<td class=\"{takeover_class}\">{takeover}</td>"
                "<td>{cdn}</td>"
                "<td>{tls}</td>"
                "</tr>".format(
                    domain=html.escape(domain),
                    name=html.escape(item["name"]),
                    score=score,
                    score_class=_score_class(score),
                    resolved=_format_bool_cell(item, "resolved"),
                    resolved_class="yes" if item.get("resolved") else "no",
                    alive=_format_bool_cell(item, "alive"),
                    alive_class="yes" if item.get("alive") else "no",
                    takeover=html.escape(str(takeover)),
                    takeover_class="vuln" if item.get("vulnerable") else "",
                    cdn=html.escape(item.get("cdn") or "-"),
                    tls=html.escape(item.get("tls_issuer") or "-"),
                )
            )
    if not rows:
        return "<tr><td colspan='8'>Sin resultados</td></tr>"
    return "".join(rows)


def score_help_block():
    return """
    <details>
      <summary>Como funciona el score</summary>
      <p>El score (0-100) prioriza subdominios interesantes. No confirma vulnerabilidades.</p>
      <ul>
        <li>+10 base</li>
        <li>+15 por keyword (api, dev, mail, admin, git, etc.)</li>
        <li>+10 DNS resuelto, +20 HTTP vivo, +50 takeover, +5 CDN/TLS, +5 nombre corto</li>
      </ul>
    </details>
    """


def render_html_report(results, title="CTFR-Reloaded Report"):
    stats = compute_report_stats(results)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{styles}</style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div>
        <h1>{title}</h1>
        <p class="meta">v{version} | {generated} | 100% Free - MrGuillote</p>
      </div>
    </div>
    <div class="panel"><div class="panel-body">{stats_cards}</div></div>
    <div class="grid-2">
      <div class="panel">
        <div class="panel-header">
        <h2>Distribucion de scores</h2>
        <span class="meta">rangos 0-100</span>
      </div>
        <div class="panel-body">{distribution}</div>
      </div>
      <div class="panel">
        <div class="panel-header"><h2>Keywords detectadas</h2></div>
        <div class="panel-body">{keywords}</div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-header"><h2>Subdominios</h2><span class="meta">{total} resultados</span></div>
      <div class="panel-body" style="padding-top:0">
        <table>
          <thead>
            <tr>
              <th>Dominio</th><th>Subdominio</th><th>Score</th><th>DNS</th>
              <th>HTTP</th><th>Takeover</th><th>CDN</th><th>TLS</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>
    <div class="panel"><div class="panel-body">{score_help}</div></div>
  </div>
</body>
</html>""".format(
        title=html.escape(title),
        styles=report_styles(),
        version=html.escape(__version__),
        generated=generated,
        stats_cards=_render_stats_cards(stats),
        distribution=_render_distribution(stats),
        keywords=_render_keywords(stats),
        total=stats["total"],
        rows=_render_table_rows(results),
        score_help=score_help_block(),
    )


def save_html_output(results, output_file):
    document = render_html_report(results)
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(document)


def save_pdf_output(results, output_file):
    """Genera PDF simple. Requiere fpdf2 (pip install ctfr-reloaded[pdf])."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError('Instala soporte PDF: pip install "ctfr-reloaded[pdf]"') from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CTFR-Reloaded Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    total = sum(len(items) for items in results.values())
    pdf.cell(0, 8, "Version {v} | Total: {t}".format(v=__version__, t=total), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 9)
    headers = ["Domain", "Subdomain", "Score", "DNS", "HTTP", "Takeover"]
    col_widths = [35, 55, 15, 12, 12, 35]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 7, header, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", size=8)
    for domain, items in results.items():
        for item in items:
            row = [
                domain[:30],
                item["name"][:40],
                str(item.get("score", "-")),
                "Y" if item.get("resolved") else "-",
                "Y" if item.get("alive") else "-",
                (item.get("service") or "-")[:25] if item.get("vulnerable") else "-",
            ]
            for i, value in enumerate(row):
                pdf.cell(col_widths[i], 6, value, border=1)
            pdf.ln()

    pdf.output(output_file)


def payload_to_results(payload):
    if "subdomains" in payload:
        return {payload["domain"]: payload["subdomains"]}
    return {
        domain: block["subdomains"]
        for domain, block in payload.get("results", {}).items()
    }
