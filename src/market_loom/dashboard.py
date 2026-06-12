from __future__ import annotations

from html import escape
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .db_summary import summarize_duckdb


def build_dashboard_html(summary: dict[str, Any]) -> str:
    rows = "\n".join(_table_row(table) for table in summary["tables"])
    if not rows:
        rows = '<tr><td colspan="5" class="empty">No local DuckDB tables found.</td></tr>'

    db_path = escape(str(summary["database_path"]))
    table_count = int(summary["table_count"])
    total_rows = int(summary["total_rows"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Loom</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17211c;
      --muted: #5f6c66;
      --paper: #f7f3ea;
      --panel: #fffdf8;
      --line: #d8d0c1;
      --green: #17624a;
      --blue: #235a7a;
      --amber: #a96f14;
      --red: #9c3535;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Times New Roman", serif;
      background:
        linear-gradient(90deg, rgba(23,98,74,.08) 1px, transparent 1px),
        linear-gradient(rgba(35,90,122,.07) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
      color: var(--ink);
    }}
    main {{
      width: min(1180px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}
    header {{
      border-bottom: 2px solid var(--ink);
      padding-bottom: 18px;
      margin-bottom: 20px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 5vw, 4.5rem);
      line-height: .95;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .path {{
      color: var(--muted);
      font-size: .96rem;
      overflow-wrap: anywhere;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 22px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      background: rgba(255,253,248,.82);
      padding: 14px 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: .78rem;
      text-transform: uppercase;
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 2rem;
      line-height: 1;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
    }}
    th, td {{
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      font-size: .76rem;
      letter-spacing: .04em;
      text-transform: uppercase;
      color: var(--muted);
      background: #ebe3d3;
    }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .badge {{
      display: inline-block;
      min-width: 68px;
      padding: 3px 7px;
      border: 1px solid currentColor;
      font-size: .76rem;
      text-transform: uppercase;
    }}
    .raw {{ color: var(--blue); }}
    .research {{ color: var(--green); }}
    .meta {{ color: var(--amber); }}
    .audit {{ color: var(--red); }}
    .other {{ color: var(--muted); }}
    .columns {{
      color: var(--muted);
      font-size: .88rem;
      max-width: 460px;
      overflow-wrap: anywhere;
    }}
    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 30px;
    }}
    @media (max-width: 760px) {{
      main {{ width: min(100vw - 24px, 1180px); padding-top: 22px; }}
      .metrics {{ grid-template-columns: 1fr; }}
      table, thead, tbody, tr, th, td {{ display: block; }}
      thead {{ display: none; }}
      tr {{ border-bottom: 1px solid var(--line); }}
      td {{ border-bottom: 0; padding: 8px 12px; }}
      .num {{ text-align: left; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Market Loom</h1>
      <div class="path">{db_path}</div>
    </header>
    <section class="metrics" aria-label="Database summary">
      <div class="metric"><span>Database</span><strong>{"online" if summary["exists"] else "missing"}</strong></div>
      <div class="metric"><span>Tables</span><strong>{table_count:,}</strong></div>
      <div class="metric"><span>Rows</span><strong>{total_rows:,}</strong></div>
    </section>
    <table>
      <thead>
        <tr>
          <th>Layer</th>
          <th>Table</th>
          <th class="num">Rows</th>
          <th class="num">Columns</th>
          <th>Column Preview</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </main>
</body>
</html>
"""


def write_dashboard(summary: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_dashboard_html(summary), encoding="utf-8")
    return path


def serve_dashboard(db_path: str | Path, *, host: str, port: int) -> None:
    db = Path(db_path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            summary = summarize_duckdb(db)
            if parsed.path == "/api/summary":
                self._send_json(summary)
                return
            if parsed.path in {"", "/"}:
                self._send_html(build_dashboard_html(summary))
                return
            self.send_error(404)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_html(self, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    ThreadingHTTPServer((host, port), Handler).serve_forever()


def _table_row(table: dict[str, Any]) -> str:
    layer = escape(str(table["layer"]))
    name = escape(str(table["name"]))
    row_count = int(table["row_count"])
    column_count = int(table["column_count"])
    preview = ", ".join(
        f"{column['name']}:{column['type']}" for column in table["columns"][:8]
    )
    return f"""<tr>
  <td><span class="badge {layer}">{layer}</span></td>
  <td>{name}</td>
  <td class="num">{row_count:,}</td>
  <td class="num">{column_count:,}</td>
  <td class="columns">{escape(preview)}</td>
</tr>"""
