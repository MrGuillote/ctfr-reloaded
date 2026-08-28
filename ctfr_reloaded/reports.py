import html
from datetime import datetime, timezone

from ctfr_reloaded import __version__


def save_html_output(results, output_file):
    total = sum(len(items) for items in results.values())
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    for domain, items in results.items():
        for item in items:
            rows.append(
                "<tr>"
                "<td>{domain}</td>"
                "<td>{name}</td>"
                "<td>{score}</td>"
                "<td>{resolved}</td>"
                "<td>{alive}</td>"
                "<td>{takeover}</td>"
                "<td>{cdn}</td>"
                "<td>{tls}</td>"
                "</tr>".format(
                    domain=html.escape(domain),
                    name=html.escape(item["name"]),
                    score=html.escape(str(item.get("score", "-"))),
                    resolved="yes" if item.get("resolved") else ("no" if "resolved" in item else "-"),
                    alive="yes" if item.get("alive") else ("no" if "alive" in item else "-"),
                    takeover=html.escape(
                        item.get("service", "") if item.get("vulnerable") else "-"
                    ),
                    cdn=html.escape(item.get("cdn") or "-"),
                    tls=html.escape(item.get("tls_issuer") or "-"),
                )
            )

    document = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>CTFR-Reloaded Report</title>
  <style>
    body {{ font-family: Segoe UI, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
    h1 {{ color: #38bdf8; }}
    .meta {{ color: #94a3b8; margin-bottom: 1.5rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #334155; padding: 0.6rem; text-align: left; font-size: 0.9rem; }}
    th {{ background: #1e293b; }}
    tr:nth-child(even) {{ background: #111827; }}
    .vuln {{ color: #f87171; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>CTFR-Reloaded Report</h1>
  <p class="meta">v{version} | {generated} | Total: {total} | 100% Free - MrGuillote</p>
  <table>
    <thead>
      <tr>
        <th>Domain</th><th>Subdomain</th><th>Score</th><th>DNS</th>
        <th>HTTP</th><th>Takeover</th><th>CDN</th><th>TLS</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>""".format(
        version=html.escape(__version__),
        generated=generated,
        total=total,
        rows="\n".join(rows) if rows else "<tr><td colspan='8'>No results</td></tr>",
    )

    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(document)
