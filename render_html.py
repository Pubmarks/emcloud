import csv
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "emcloud.csv"
OUT_DIR = ROOT / "html"
OUT_FILE = OUT_DIR / "index.html"

COLUMNS = [
    {"key": "Rank", "label": "Rank", "unit": "", "kind": "rank"},
    {"key": "Company", "label": "Company", "unit": "", "kind": "company"},
    {"key": "Symbol", "label": "Ticker", "unit": "", "kind": "text"},
    {"key": "Price", "label": "Price", "unit": "USD", "kind": "price"},
    {"key": "Market Cap", "label": "Market cap", "unit": "USD bn", "kind": "cap"},
    {"key": "EV / Annualized Revenue", "label": "EV / revenue", "unit": "Annualized", "kind": "multiple"},
    {"key": "EV / Forward Revenue", "label": "EV / revenue", "unit": "Forward", "kind": "multiple"},
    {"key": "Efficiency", "label": "Efficiency", "unit": "", "kind": "pct"},
    {"key": "Revenue Growth Rate", "label": "Revenue growth", "unit": "", "kind": "pct"},
    {"key": "Gross Margin", "label": "Gross margin", "unit": "", "kind": "pct"},
    {"key": "LTM FCF Margin", "label": "FCF margin", "unit": "LTM", "kind": "pct"},
    {"key": "SGA Margin", "label": "SG&A margin", "unit": "", "kind": "pct"},
    {"key": "R&D Revenue", "label": "R&D", "unit": "of revenue", "kind": "pct"},
    {"key": "Sales Marketing Revenue", "label": "Sales & marketing", "unit": "of revenue", "kind": "pct"},
    {"key": "Rule of X", "label": "Rule of X", "unit": "", "kind": "pct"},
    {"key": "Score", "label": "Score", "unit": "Weighted", "kind": "score"},
]


def load_rows(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"No rows in {path}")
    return rows


def format_value(kind, raw):
    if kind in {"rank", "company", "text"}:
        return escape(raw), ""
    value = float(raw)
    negative = " neg" if value < 0 else ""
    if kind == "price":
        return f"${value:,.2f}", negative
    if kind == "cap":
        return f"${value / 1000:,.1f}B", negative
    if kind == "multiple":
        return f"{value:,.1f}×", negative
    if kind == "pct":
        return f"{value * 100:,.1f}%", negative
    if kind == "score":
        return f"{value:,.2f}", negative
    raise ValueError(f"Unknown column kind: {kind}")


def header_cells():
    cells = []
    for column in COLUMNS:
        unit = escape(column["unit"]) if column["unit"] else "&nbsp;"
        classes = []
        if column["kind"] == "rank":
            classes.append("col-rank")
        elif column["kind"] == "company":
            classes.append("col-company")
        elif column["kind"] != "text":
            classes.append("num")
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        cells.append(
            f"<th{class_attr} scope=\"col\">"
            f"<span>{escape(column['label'])}</span><small>{unit}</small></th>"
        )
    return "".join(cells)


def render_row(row):
    company = row["Company"]
    symbol = row["Symbol"]
    search = escape(f"{company} {symbol}".lower())
    rank = int(float(row["Rank"]))
    cells = []
    for column in COLUMNS:
        text, negative = format_value(column["kind"], row[column["key"]])
        if column["kind"] == "rank":
            top = " top" if rank <= 3 else ""
            cells.append(f'<th class="col-rank{top}" scope="row">{text}</th>')
        elif column["kind"] == "company":
            cells.append(
                f'<th class="col-company" scope="row" title="{escape(company)}">{text}</th>'
            )
        elif column["kind"] == "text":
            cells.append(f"<td>{text}</td>")
        else:
            score = " score" if column["kind"] == "score" else ""
            cells.append(f'<td class="num{negative}{score}">{text}</td>')
    return f'<tr data-search="{search}">{"".join(cells)}</tr>'


def render_page(rows):
    now = datetime.now(timezone.utc)
    stamp = f"{now.day} {now.strftime('%b %Y')} · {now.strftime('%H:%M')} UTC"
    count = len(rows)
    return PAGE.replace("{{STAMP}}", stamp).replace("{{COUNT}}", str(count)).replace(
        "{{HEADER}}", header_cells()
    ).replace("{{ROWS}}", "\n".join(render_row(row) for row in rows))


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EMCLOUD rankings</title>
  <meta name="description" content="Weekly rankings of the BVP Nasdaq Emerging Cloud Index.">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%231b1714'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='Georgia' font-size='16' fill='%23f3eadc'%3EE%3C/text%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,550;1,6..72,550&display=swap" rel="stylesheet">
  <style>
    :root {
      --ink: #1b1714;
      --muted: #6d655c;
      --paper: #e5ded2;
      --sheet: #f7f4ee;
      --line: #e3dace;
      --brass: #8d5a2b;
      --neg: #8f3a32;
      --hover: #e5f1e4;
      --rank-w: 4.5rem;
      --company-w: 13.75rem;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      display: flex;
      flex-direction: column;
      min-height: 100dvh;
      background: var(--paper);
      color: var(--ink);
      font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      font-size: 15px;
      line-height: 1.4;
    }
    .mast {
      display: flex;
      justify-content: space-between;
      gap: 1.5rem;
      align-items: end;
      padding: 1.25rem 1.5rem 1rem;
      background: var(--ink);
      color: #f3eadc;
    }
    .kicker {
      margin: 0 0 0.2rem;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.16em;
    }
    h1 {
      margin: 0;
      font-family: Newsreader, Georgia, serif;
      font-size: clamp(1.8rem, 3vw, 2.6rem);
      font-weight: 550;
      letter-spacing: -0.03em;
      line-height: 1;
    }
    .deck, .updated, .count { margin: 0.35rem 0 0; color: #cbbfae; }
    .deck { max-width: 38rem; }
    .mast-side { display: flex; flex-direction: column; align-items: flex-end; gap: 0.65rem; }
    .count { font-variant-numeric: tabular-nums; }
    .filter input {
      width: min(18rem, 70vw);
      padding: 0.6rem 0.9rem;
      border: 1px solid #4a433c;
      border-radius: 999px;
      background: transparent;
      color: #f3eadc;
      font: 1rem/1.2 "IBM Plex Sans", sans-serif;
    }
    .filter input::placeholder { color: #a89886; }
    .filter input:focus { outline: 2px solid #d7b48a; outline-offset: 2px; }
    .hint {
      margin: 0;
      padding: 0.45rem 1.5rem;
      color: var(--muted);
      font-size: 0.82rem;
    }
    .sheet {
      flex: 1;
      min-height: 0;
      margin: 0 1rem 1rem;
      overflow: auto;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: contain;
      background: var(--sheet);
      border: 1px solid #d5cec2;
      border-radius: 12px;
    }
    table {
      width: max-content;
      min-width: 100%;
      border-collapse: separate;
      border-spacing: 0;
    }
    caption {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
    th, td {
      padding: 0.62rem 0.8rem;
      text-align: left;
      white-space: nowrap;
      background: var(--sheet);
      vertical-align: bottom;
    }
    thead th {
      position: sticky;
      top: 0;
      z-index: 2;
      padding-top: 0.75rem;
      padding-bottom: 0.7rem;
      background: var(--ink);
      color: #f3eadc;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.01em;
    }
    thead th span, thead th small { display: block; }
    thead th small {
      margin-top: 0.15rem;
      color: #b7aa9a;
      font-size: 0.68rem;
      font-weight: 400;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    tbody th, tbody td { border-bottom: 1px solid var(--line); font-weight: 400; }
    tbody tr:hover th, tbody tr:hover td { background: var(--hover); }
    .col-rank, .col-company { position: sticky; z-index: 1; }
    .col-rank { left: 0; width: var(--rank-w); min-width: var(--rank-w); max-width: var(--rank-w); }
    .col-company { left: var(--rank-w); width: var(--company-w); min-width: var(--company-w); max-width: var(--company-w); }
    thead .col-rank, thead .col-company { z-index: 3; }
    tbody .col-company {
      font-weight: 500;
      box-shadow: 1px 0 0 var(--line), 12px 0 16px -14px rgba(27, 23, 20, 0.85);
    }
    thead .col-company { box-shadow: 1px 0 0 #3a342e; }
    .num { text-align: right; font-variant-numeric: tabular-nums; min-width: 7.5rem; }
    .top { color: var(--brass); font-weight: 600; }
    .score { font-weight: 600; }
    .neg { color: var(--neg); }
    .empty {
      margin: 0 1rem 0.35rem;
      color: var(--muted);
    }
    .note {
      margin: 0 1rem 0.85rem;
      color: var(--muted);
      font-size: 0.82rem;
    }
    @media (max-width: 720px) {
      :root { --rank-w: 3.25rem; --company-w: 9.25rem; }
      .mast { flex-direction: column; align-items: stretch; gap: 0.7rem; padding: 0.8rem 0.85rem 0.7rem; }
      .mast-side { align-items: stretch; gap: 0.35rem; }
      h1 { font-size: 1.65rem; }
      .deck { font-size: 0.92rem; }
      .updated, .count { margin: 0; }
      .filter input { width: 100%; }
      .hint, .sheet, .empty, .note { margin-left: 0.5rem; margin-right: 0.5rem; }
      .hint { padding-left: 0.25rem; padding-right: 0.25rem; }
      th, td { padding: 0.55rem 0.7rem; }
      .col-company { overflow: hidden; text-overflow: ellipsis; }
    }
  </style>
</head>
<body>
  <header class="mast">
    <div>
      <p class="kicker">EMCLOUD</p>
      <h1>Emerging cloud rankings</h1>
      <p class="deck">BVP Nasdaq Emerging Cloud Index, weighted across efficiency, valuation, growth, margins, and scale.</p>
    </div>
    <div class="mast-side">
      <p class="updated">Updated {{STAMP}}</p>
      <p class="count"><span id="count">{{COUNT}}</span> companies</p>
      <label class="filter">
        <span class="sr" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">Filter by company or ticker</span>
        <input id="q" type="search" placeholder="Filter company or ticker" autocomplete="off" enterkeyhint="search">
      </label>
    </div>
  </header>
  <p class="hint">Scroll sideways for every metric. Rank and company stay fixed.</p>
  <div class="sheet" id="sheet">
    <table>
      <caption>Emerging cloud company rankings</caption>
      <thead><tr>{{HEADER}}</tr></thead>
      <tbody id="rows">
{{ROWS}}
      </tbody>
    </table>
  </div>
  <p id="empty" class="empty" hidden>No matching companies.</p>
  <p class="note">Market cap is shown in billions of US dollars. Growth, margins, efficiency, and Rule of X are percentages. Score is the weighted ranking.</p>
  <script>
    const input = document.getElementById("q");
    const rows = Array.from(document.querySelectorAll("#rows tr"));
    const empty = document.getElementById("empty");
    const count = document.getElementById("count");
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      let shown = 0;
      for (const row of rows) {
        const match = query.length === 0 || row.dataset.search.includes(query);
        row.hidden = !match;
        if (match) shown += 1;
      }
      empty.hidden = shown !== 0;
      count.textContent = String(shown);
    });
  </script>
</body>
</html>
"""


def main():
    rows = load_rows(CSV_PATH)
    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text(render_page(rows), encoding="utf-8")
    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Wrote {OUT_FILE} ({len(rows)} companies)")


if __name__ == "__main__":
    main()
