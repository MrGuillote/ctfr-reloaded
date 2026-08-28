import html
import json

from ctfr_reloaded import __version__
from ctfr_reloaded.reports import SCORE_BUCKETS, _report_styles, _score_help_block
from ctfr_reloaded.scoring import HIGH_VALUE_KEYWORDS


def render_dashboard(version=None, sources=None):
    version = version or __version__
    sources = sources or []
    source_options = ['<option value="all">Todas las fuentes</option>']
    for source in sources:
        source_options.append(
            '<option value="{name}">{name}</option>'.format(name=html.escape(source))
        )

    extra_styles = """
    .topbar { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }
    .actions { display:flex; gap:10px; flex-wrap:wrap; }
    .btn {
      appearance:none; border:none; border-radius:10px; padding:10px 14px;
      font: inherit; cursor:pointer; transition: transform .12s ease, opacity .12s ease;
    }
    .btn:hover { transform: translateY(-1px); }
    .btn-primary {
      color:white; background: linear-gradient(135deg, #4da3ff, #7c5cff);
      box-shadow: 0 10px 24px rgba(77, 163, 255, 0.25);
    }
    .btn-secondary {
      color: var(--text); background: rgba(255,255,255,0.06); border: 1px solid var(--border);
    }
    .form-grid {
      display:grid; grid-template-columns: 1.4fr 0.8fr; gap:14px;
    }
    @media (max-width: 900px) { .form-grid { grid-template-columns: 1fr; } }
    label { display:block; color: var(--muted); font-size:0.82rem; margin-bottom:6px; }
    input[type=text], select {
      width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--border);
      background: rgba(8, 12, 22, 0.65); color: var(--text); font: inherit;
    }
    .checks { display:flex; flex-wrap:wrap; gap:12px 18px; margin-top:14px; }
    .checks label { display:flex; align-items:center; gap:8px; margin:0; color:var(--text); }
    .toolbar { display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom:14px; }
    .toolbar input { max-width: 320px; }
    .hidden { display:none !important; }
    .loading {
      display:flex; align-items:center; gap:10px; color: var(--muted); padding: 8px 0 0;
    }
    .spinner {
      width: 16px; height: 16px; border-radius:50%;
      border: 2px solid rgba(255,255,255,0.15); border-top-color: var(--accent);
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .error {
      margin-top: 12px; padding: 12px 14px; border-radius: 10px;
      background: rgba(255, 107, 122, 0.12); border: 1px solid rgba(255, 107, 122, 0.35);
      color: #ffc1c8;
    }
    th.sortable { cursor:pointer; user-select:none; }
    th.sortable:hover { color: var(--text); }
    .empty {
      text-align:center; color: var(--muted); padding: 42px 20px;
    }
    .activity-backdrop {
      position: fixed; inset: 0; background: rgba(4, 8, 16, 0.55);
      backdrop-filter: blur(2px); z-index: 90; opacity: 0; pointer-events: none;
      transition: opacity 0.2s ease;
    }
    .activity-backdrop.open { opacity: 1; pointer-events: auto; }
    .activity-panel {
      position: fixed; top: 0; right: 0; width: min(440px, 94vw); height: 100vh;
      background: rgba(10, 16, 28, 0.98); border-left: 1px solid var(--border);
      box-shadow: -20px 0 60px rgba(0,0,0,0.45); z-index: 100;
      display: flex; flex-direction: column; transform: translateX(100%);
      transition: transform 0.24s ease;
    }
    .activity-panel.open { transform: translateX(0); }
    .activity-header {
      display:flex; justify-content:space-between; align-items:flex-start; gap:12px;
      padding: 16px 18px; border-bottom: 1px solid var(--border);
    }
    .activity-header strong { display:block; margin-bottom:4px; }
    .activity-status { color: var(--muted); font-size: 0.82rem; }
    .activity-body {
      flex: 1; overflow-y: auto; padding: 12px 14px;
      font-family: Consolas, "Cascadia Mono", "Segoe UI Mono", monospace;
      font-size: 0.8rem; line-height: 1.45; background: rgba(4, 8, 16, 0.92);
    }
    .log-line { padding: 3px 0; white-space: pre-wrap; word-break: break-word; }
    .log-line .ts { color: #64748b; margin-right: 8px; }
    .log-line.info { color: #7dd3fc; }
    .log-line.debug { color: #93c5fd; }
    .log-line.success { color: #6ee7b7; }
    .log-line.warn { color: #fcd34d; }
    .log-line.error { color: #fca5a5; }
    .activity-footer {
      padding: 10px 14px; border-top: 1px solid var(--border); color: var(--muted);
      font-size: 0.78rem;
    }
    .activity-fab {
      position: fixed; right: 0; top: 50%; transform: translateY(-50%);
      z-index: 85; border: 1px solid var(--border); border-right: none;
      border-radius: 12px 0 0 12px; padding: 14px 10px;
      background: linear-gradient(135deg, rgba(77, 163, 255, 0.22), rgba(124, 92, 255, 0.18));
      color: var(--text); font: inherit; font-size: 0.82rem; font-weight: 600;
      cursor: pointer; box-shadow: -8px 0 24px rgba(0,0,0,0.25);
      writing-mode: vertical-rl; text-orientation: mixed; letter-spacing: 0.04em;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }
    .activity-fab:hover { transform: translateY(-50%) translateX(-2px); }
    .activity-fab.hidden { display: none; }
  """

    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CTFR-Reloaded Dashboard</title>
  <style>{base_styles}{extra_styles}</style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div>
        <h1>CTFR-Reloaded</h1>
        <p>Dashboard web para enumeracion de subdominios. 100% gratuito, sin API keys.</p>
        <div class="badge-row">
          <span class="badge">v{version}</span>
          <span class="badge">by MrGuillote</span>
          <span class="badge">{source_count} fuentes</span>
        </div>
      </div>
      <div class="actions">
        <button type="button" class="btn btn-secondary hidden" id="activity-open-inline">Ver log</button>
        <a class="btn btn-secondary" href="/docs">API Docs</a>
        <a class="btn btn-secondary" href="/health" target="_blank">Health</a>
      </div>
    </div>

    <div class="content-stack">
    <div class="panel">
      <div class="panel-header"><h2>Nuevo scan</h2></div>
      <div class="panel-body">
        <form id="scan-form">
          <div class="form-grid">
            <div>
              <label for="domain">Dominio</label>
              <input id="domain" name="domain" type="text" placeholder="ejemplo.com" required>
            </div>
            <div>
              <label for="source">Fuente</label>
              <select id="source" name="source">{source_options}</select>
            </div>
          </div>
          <div class="checks">
            <label><input type="checkbox" name="resolve"> Resolver DNS</label>
            <label><input type="checkbox" name="alive"> Comprobar HTTP</label>
            <label><input type="checkbox" name="takeover"> Detectar takeover</label>
            <label><input type="checkbox" name="tls"> Info TLS</label>
            <label><input type="checkbox" name="cdn"> Detectar CDN</label>
            <label><input type="checkbox" name="score" checked> Calcular score</label>
          </div>
          <div style="margin-top:16px; display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-primary" type="submit">Escanear</button>
            <button class="btn btn-secondary" type="button" id="export-json" disabled>Exportar JSON</button>
            <button class="btn btn-secondary" type="button" id="export-html" disabled>Exportar HTML</button>
          </div>
          <div id="loading" class="loading hidden"><span class="spinner"></span><span>Escaneando...</span></div>
          <div id="error" class="error hidden"></div>
        </form>
      </div>
    </div>

    <div id="results" class="stack hidden">
      <div class="panel"><div class="panel-body" id="stats"></div></div>
      <div class="grid-2">
        <div class="panel">
          <div class="panel-header">
            <h2>Distribucion de scores</h2>
            <span class="meta">rangos 0-100</span>
          </div>
          <div class="panel-body" id="distribution"></div>
        </div>
        <div class="panel">
          <div class="panel-header"><h2>Keywords detectadas</h2></div>
          <div class="panel-body" id="keywords"></div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h2>Subdominios</h2>
          <span class="meta" id="result-meta"></span>
        </div>
        <div class="panel-body" style="padding-top:0">
          <div class="toolbar">
            <input id="filter" type="text" placeholder="Filtrar por nombre...">
            <span class="meta" id="filter-meta"></span>
          </div>
          <table>
            <thead>
              <tr>
                <th class="sortable" data-key="domain">Dominio</th>
                <th class="sortable" data-key="name">Subdominio</th>
                <th class="sortable" data-key="score">Score</th>
                <th class="sortable" data-key="resolved">DNS</th>
                <th class="sortable" data-key="alive">HTTP</th>
                <th>Takeover</th>
                <th>CDN</th>
                <th>TLS</th>
              </tr>
            </thead>
            <tbody id="table-body"></tbody>
          </table>
        </div>
      </div>
      <div class="panel"><div class="panel-body">{score_help}</div></div>
    </div>

    <div id="empty" class="panel">
      <div class="panel-body empty">
        <h2 style="margin-top:0">Listo para escanear</h2>
        <p>Ingresa un dominio y presiona <strong>Escanear</strong> para ver estadisticas y resultados.</p>
      </div>
    </div>
    </div>
  </div>

  <div id="activity-backdrop" class="activity-backdrop"></div>
  <button type="button" id="activity-open" class="activity-fab hidden" title="Abrir consola de actividad">LOG</button>
  <aside id="activity-panel" class="activity-panel" aria-live="polite">
    <div class="activity-header">
      <div>
        <strong>Consola de actividad</strong>
        <div class="activity-status" id="activity-status">En espera</div>
      </div>
      <button type="button" class="btn btn-secondary" id="activity-close">Cerrar</button>
    </div>
    <div class="activity-body" id="activity-log"></div>
    <div class="activity-footer">Logs en tiempo real del scan (fuentes, DNS, HTTP, scoring...)</div>
  </aside>

  <script>
    const state = {{
      payload: null,
      rows: [],
      sortKey: "score",
      sortDir: "desc",
      activityLogs: [],
    }};

    const STORAGE_KEY = "ctfr-reloaded-dashboard-v1";
    const scoreBuckets = {score_buckets_json};

    const form = document.getElementById("scan-form");
    const loading = document.getElementById("loading");
    const errorBox = document.getElementById("error");
    const results = document.getElementById("results");
    const empty = document.getElementById("empty");
    const exportJsonBtn = document.getElementById("export-json");
    const exportHtmlBtn = document.getElementById("export-html");
    const activityPanel = document.getElementById("activity-panel");
    const activityBackdrop = document.getElementById("activity-backdrop");
    const activityLog = document.getElementById("activity-log");
    const activityStatus = document.getElementById("activity-status");
    const activityClose = document.getElementById("activity-close");
    const activityOpen = document.getElementById("activity-open");
    const activityOpenInline = document.getElementById("activity-open-inline");
    let activeEventSource = null;

    const logPrefix = {{
      info: "[*]",
      debug: "[~]",
      success: "[+]",
      warn: "[!]",
      error: "[X]",
    }};

    function updateActivityControls() {{
      const hasLogs = state.activityLogs.length > 0;
      const isOpen = activityPanel.classList.contains("open");
      const show = hasLogs && !isOpen;
      activityOpen.classList.toggle("hidden", !show);
      activityOpenInline.classList.toggle("hidden", !hasLogs);
    }}

    function openActivityPanel(statusText, resetLogs) {{
      if (resetLogs !== false) {{
        state.activityLogs = [];
        activityLog.innerHTML = "";
      }}
      activityPanel.classList.add("open");
      activityBackdrop.classList.add("open");
      activityStatus.textContent = statusText || "Escaneando...";
      updateActivityControls();
    }}

    function reopenActivityPanel() {{
      if (!state.activityLogs.length) return;
      openActivityPanel(activityStatus.textContent || "Ultimo scan", false);
    }}

    function closeActivityPanel() {{
      activityPanel.classList.remove("open");
      activityBackdrop.classList.remove("open");
      updateActivityControls();
    }}

    function appendActivityLog(event) {{
      state.activityLogs.push(event);
      const line = document.createElement("div");
      line.className = "log-line " + (event.level || "info");
      const prefix = logPrefix[event.level] || "[?]";
      const time = event.time ? `<span class="ts">${{event.time}}</span>` : "";
      line.innerHTML = `${{time}}${{prefix}} ${{escapeHtml(event.message || "")}}`;
      activityLog.appendChild(line);
      activityLog.scrollTop = activityLog.scrollHeight;
      updateActivityControls();
    }}

    function collectFormState() {{
      const formData = new FormData(form);
      return {{
        domain: formData.get("domain") || "",
        source: formData.get("source") || "all",
        resolve: Boolean(formData.get("resolve")),
        alive: Boolean(formData.get("alive")),
        takeover: Boolean(formData.get("takeover")),
        tls: Boolean(formData.get("tls")),
        cdn: Boolean(formData.get("cdn")),
        score: formData.get("score") !== null,
      }};
    }}

    function applyFormState(formState) {{
      if (!formState) return;
      document.getElementById("domain").value = formState.domain || "";
      document.getElementById("source").value = formState.source || "all";
      for (const flag of ["resolve", "alive", "takeover", "tls", "cdn", "score"]) {{
        const input = form.querySelector(`[name="${{flag}}"]`);
        if (input) input.checked = Boolean(formState[flag]);
      }}
    }}

    function readSession() {{
      try {{
        const raw = sessionStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
      }} catch (error) {{
        return null;
      }}
    }}

    function persistSession() {{
      try {{
        const snapshot = {{
          payload: state.payload,
          form: collectFormState(),
          filter: document.getElementById("filter").value || "",
          sortKey: state.sortKey,
          sortDir: state.sortDir,
          activityLogs: state.activityLogs,
          activityStatus: activityStatus.textContent,
          savedAt: new Date().toISOString(),
        }};
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
      }} catch (error) {{
        // Ignorar errores de cuota o modo privado restrictivo.
      }}
    }}

    function restoreActivityLogs(logs, statusText) {{
      activityLog.innerHTML = "";
      state.activityLogs = Array.isArray(logs) ? [...logs] : [];
      for (const event of state.activityLogs) {{
        const line = document.createElement("div");
        line.className = "log-line " + (event.level || "info");
        const prefix = logPrefix[event.level] || "[?]";
        const time = event.time ? `<span class="ts">${{event.time}}</span>` : "";
        line.innerHTML = `${{time}}${{prefix}} ${{escapeHtml(event.message || "")}}`;
        activityLog.appendChild(line);
      }}
      activityStatus.textContent = statusText || "Ultimo scan (restaurado)";
      updateActivityControls();
    }}

    function restoreSession() {{
      const saved = readSession();
      if (!saved) return false;

      if (saved.form) applyFormState(saved.form);

      if (!saved.payload) return Boolean(saved.form);

      state.sortKey = saved.sortKey || "score";
      state.sortDir = saved.sortDir || "desc";
      applyScanResult(saved.payload);

      const filterInput = document.getElementById("filter");
      if (saved.filter) {{
        filterInput.value = saved.filter;
      }}
      renderTable();

      if (saved.activityLogs && saved.activityLogs.length) {{
        restoreActivityLogs(saved.activityLogs, saved.activityStatus);
      }}

      const meta = document.getElementById("result-meta");
      if (meta && saved.savedAt) {{
        const when = new Date(saved.savedAt);
        const label = Number.isNaN(when.getTime())
          ? "restaurado de esta pestana"
          : "restaurado " + when.toLocaleTimeString();
        meta.textContent = `${{state.rows.length}} resultados (${{label}})`;
      }}

      setError("");
      return true;
    }}

    function applyScanResult(payload) {{
      state.payload = payload;
      state.rows = payloadToRows(payload);
      const stats = computeStats(state.rows);
      renderStats(stats);
      renderTable();
      results.classList.remove("hidden");
      empty.classList.add("hidden");
      exportJsonBtn.disabled = false;
      exportHtmlBtn.disabled = false;
      persistSession();
    }}

    function stopActiveStream() {{
      if (activeEventSource) {{
        activeEventSource.close();
        activeEventSource = null;
      }}
    }}

    function escapeHtml(value) {{
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function boolLabel(item, key) {{
      if (!(key in item)) return "-";
      return item[key] ? "yes" : "no";
    }}

    function scoreClass(score) {{
      if (score >= 50) return "critical";
      if (score >= 25) return "high";
      return "";
    }}

    function payloadToRows(payload) {{
      if (payload.subdomains) {{
        return payload.subdomains.map((item) => ({{
          domain: payload.domain,
          ...item,
        }}));
      }}
      const rows = [];
      for (const [domain, block] of Object.entries(payload.results || {{}})) {{
        for (const item of block.subdomains || []) {{
          rows.push({{ domain, ...item }});
        }}
      }}
      return rows;
    }}

    function computeStats(rows) {{
      const scores = rows.map((row) => Number(row.score || 0));
      const keywords = {{}};
      const keywordList = {keywords_json};
      for (const row of rows) {{
        const name = (row.name || "").toLowerCase();
        for (const keyword of keywordList) {{
          if (name.includes(keyword)) {{
            keywords[keyword] = (keywords[keyword] || 0) + 1;
          }}
        }}
      }}
      const distribution = Object.fromEntries(scoreBuckets.map((bucket) => [bucket.label, 0]));
      for (const score of scores) {{
        for (const bucket of scoreBuckets) {{
          if (score >= bucket.min && score <= bucket.max) {{
            distribution[bucket.label] += 1;
            break;
          }}
        }}
      }}
      const domains = new Set(rows.map((row) => row.domain));
      return {{
        total: rows.length,
        domains: domains.size,
        high_score: scores.filter((score) => score >= 25).length,
        resolved: rows.filter((row) => row.resolved).length,
        alive: rows.filter((row) => row.alive).length,
        takeover: rows.filter((row) => row.vulnerable || row.takeover).length,
        avg_score: scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 0,
        max_score: scores.length ? Math.max(...scores) : 0,
        distribution,
        keywords: Object.fromEntries(
          Object.entries(keywords).sort((a, b) => b[1] - a[1]).slice(0, 8)
        ),
      }};
    }}

    function renderStats(stats) {{
      document.getElementById("stats").innerHTML = `
        <div class="stats">
          <div class="stat accent"><div class="label">Subdominios</div><div class="value">${{stats.total}}</div><div class="hint">${{stats.domains}} dominio(s)</div></div>
          <div class="stat warning"><div class="label">Score alto</div><div class="value">${{stats.high_score}}</div><div class="hint">score >= 25</div></div>
          <div class="stat success"><div class="label">Resueltos</div><div class="value">${{stats.resolved}}</div><div class="hint">DNS</div></div>
          <div class="stat success"><div class="label">Vivos</div><div class="value">${{stats.alive}}</div><div class="hint">HTTP</div></div>
          <div class="stat danger"><div class="label">Takeover</div><div class="value">${{stats.takeover}}</div><div class="hint">candidatos</div></div>
          <div class="stat"><div class="label">Score medio</div><div class="value">${{stats.avg_score}}</div><div class="hint">max ${{stats.max_score}}</div></div>
        </div>`;
      const total = stats.total || 1;
      document.getElementById("distribution").innerHTML = Object.entries(stats.distribution).map(([label, count]) => {{
        const width = Math.max(4, Math.round((count / total) * 100));
        return `<div class="bar-row"><div>${{label}}</div><div class="bar-track"><div class="bar-fill" style="width:${{width}}%"></div></div><div>${{count}}</div></div>`;
      }}).join("");
      const keywordEntries = Object.entries(stats.keywords);
      document.getElementById("keywords").innerHTML = keywordEntries.length
        ? `<div class="keywords">${{keywordEntries.map(([keyword, count]) => `<span class="chip">${{escapeHtml(keyword)}} <strong>${{count}}</strong></span>`).join("")}}</div>`
        : `<p class="meta">Sin keywords destacadas en este scan.</p>`;
      document.getElementById("result-meta").textContent = `${{stats.total}} resultados`;
    }}

    function sortRows(rows) {{
      const key = state.sortKey;
      const dir = state.sortDir === "asc" ? 1 : -1;
      return [...rows].sort((a, b) => {{
        const av = a[key];
        const bv = b[key];
        if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
        return String(av || "").localeCompare(String(bv || "")) * dir;
      }});
    }}

    function renderTable() {{
      const filter = document.getElementById("filter").value.trim().toLowerCase();
      let rows = sortRows(state.rows);
      if (filter) {{
        rows = rows.filter((row) => row.name.toLowerCase().includes(filter) || row.domain.toLowerCase().includes(filter));
      }}
      document.getElementById("filter-meta").textContent = filter ? `${{rows.length}} visibles` : "";
      const body = document.getElementById("table-body");
      if (!rows.length) {{
        body.innerHTML = `<tr><td colspan="8">Sin resultados</td></tr>`;
        return;
      }}
      body.innerHTML = rows.map((row) => {{
        const score = Number(row.score || 0);
        const takeover = row.vulnerable ? (row.service || "yes") : "-";
        return `<tr>
          <td>${{escapeHtml(row.domain)}}</td>
          <td><strong>${{escapeHtml(row.name)}}</strong></td>
          <td><span class="score-pill ${{scoreClass(score)}}">${{score}}</span></td>
          <td class="${{row.resolved ? "yes" : "no"}}">${{boolLabel(row, "resolved")}}</td>
          <td class="${{row.alive ? "yes" : "no"}}">${{boolLabel(row, "alive")}}</td>
          <td class="${{row.vulnerable ? "vuln" : ""}}">${{escapeHtml(takeover)}}</td>
          <td>${{escapeHtml(row.cdn || "-")}}</td>
          <td>${{escapeHtml(row.tls_issuer || "-")}}</td>
        </tr>`;
      }}).join("");
    }}

    function setError(message) {{
      errorBox.textContent = message;
      errorBox.classList.toggle("hidden", !message);
    }}

    async function runScan(event) {{
      event.preventDefault();
      setError("");
      stopActiveStream();
      loading.classList.remove("hidden");
      exportJsonBtn.disabled = true;
      exportHtmlBtn.disabled = true;

      const formData = new FormData(form);
      const domain = formData.get("domain");
      const params = new URLSearchParams();
      params.set("domain", domain);
      params.set("source", formData.get("source") || "all");
      for (const flag of ["resolve", "alive", "takeover", "tls", "cdn", "score"]) {{
        if (formData.get(flag)) params.set(flag, "true");
      }}

      openActivityPanel("Escaneando " + domain + "...");

      await new Promise((resolve, reject) => {{
        let finished = false;
        const finish = (fn, value) => {{
          if (finished) return;
          finished = true;
          stopActiveStream();
          fn(value);
        }};

        activeEventSource = new EventSource("/scan/stream?" + params.toString());

        activeEventSource.addEventListener("log", (message) => {{
          try {{
            appendActivityLog(JSON.parse(message.data));
          }} catch (error) {{
            appendActivityLog({{ level: "debug", message: message.data }});
          }}
        }});

        activeEventSource.addEventListener("result", (message) => {{
          try {{
            const payload = JSON.parse(message.data);
            activityStatus.textContent = "Completado";
            appendActivityLog({{ level: "success", message: "Resultados listos en el dashboard" }});
            applyScanResult(payload);
            persistSession();
            finish(resolve);
          }} catch (error) {{
            finish(reject, error);
          }}
        }});

        activeEventSource.addEventListener("failed", (message) => {{
          let detail = "Error al escanear";
          try {{
            detail = JSON.parse(message.data).detail || detail;
          }} catch (error) {{}}
          appendActivityLog({{ level: "error", message: detail }});
          activityStatus.textContent = "Error";
          setError(detail);
          finish(reject, new Error(detail));
        }});

        activeEventSource.onerror = () => {{
          if (finished) return;
          const detail = "Conexion con el servidor interrumpida";
          appendActivityLog({{ level: "error", message: detail }});
          activityStatus.textContent = "Desconectado";
          setError(detail);
          finish(reject, new Error(detail));
        }};
      }}).catch((error) => {{
        if (!errorBox.textContent) {{
          setError(error.message || "No se pudo completar el scan");
        }}
      }}).finally(() => {{
        loading.classList.add("hidden");
      }});
    }}

    function downloadFile(filename, content, type) {{
      const blob = new Blob([content], {{ type }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }}

    async function exportHtml() {{
      if (!state.payload) return;
      const domain = state.payload.domain || "scan";
      const response = await fetch("/report", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(state.payload),
      }});
      const html = await response.text();
      downloadFile(`${{domain}}-ctfr-report.html`, html, "text/html");
    }}

    form.addEventListener("submit", runScan);
    form.addEventListener("change", persistSession);
    activityClose.addEventListener("click", closeActivityPanel);
    activityBackdrop.addEventListener("click", closeActivityPanel);
    activityOpen.addEventListener("click", reopenActivityPanel);
    activityOpenInline.addEventListener("click", reopenActivityPanel);
    document.getElementById("filter").addEventListener("input", () => {{
      renderTable();
      persistSession();
    }});
    exportJsonBtn.addEventListener("click", () => {{
      if (!state.payload) return;
      const domain = state.payload.domain || "scan";
      downloadFile(`${{domain}}-ctfr.json`, JSON.stringify(state.payload, null, 2), "application/json");
    }});
    exportHtmlBtn.addEventListener("click", exportHtml);

    document.querySelectorAll("th.sortable").forEach((header) => {{
      header.addEventListener("click", () => {{
        const key = header.dataset.key;
        if (state.sortKey === key) {{
          state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
        }} else {{
          state.sortKey = key;
          state.sortDir = key === "score" ? "desc" : "asc";
        }}
        renderTable();
        persistSession();
      }});
    }});

    if (!restoreSession()) {{
      const params = new URLSearchParams(window.location.search);
      const initialDomain = params.get("domain");
      if (initialDomain) {{
        document.getElementById("domain").value = initialDomain;
      }}
    }}
  </script>
</body>
</html>""".format(
        version=html.escape(version),
        source_count=len(sources),
        source_options="".join(source_options),
        base_styles=_report_styles(),
        extra_styles=extra_styles,
        score_help=_score_help_block(),
        keywords_json=json.dumps(list(HIGH_VALUE_KEYWORDS)),
        score_buckets_json=json.dumps(
            [{"label": label, "min": low, "max": high} for label, low, high in SCORE_BUCKETS]
        ),
    )
