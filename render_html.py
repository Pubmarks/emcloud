import csv
import json
from datetime import datetime, timezone
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


def json_for_script(value):
    return json.dumps(value).replace("<", "\\u003c")


def json_rows(rows):
    payload = []
    for row in rows:
        item = {}
        for column in COLUMNS:
            raw = row[column["key"]]
            if column["kind"] in {"company", "text"}:
                item[column["key"]] = raw
            elif column["kind"] == "rank":
                item[column["key"]] = int(float(raw))
            else:
                item[column["key"]] = float(raw)
        payload.append(item)
    return json_for_script(payload)


def render_page(rows):
    now = datetime.now(timezone.utc)
    stamp = f"{now.day} {now.strftime('%b %Y')} · {now.strftime('%H:%M')} UTC"
    return (
        PAGE.replace("{{STAMP}}", stamp)
        .replace("{{COUNT}}", str(len(rows)))
        .replace("{{DATA}}", json_rows(rows))
        .replace("{{COLUMNS}}", json_for_script(COLUMNS))
    )


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
  <link href="https://cdn.jsdelivr.net/npm/tabulator-tables@6.7.1/dist/css/tabulator.min.css" rel="stylesheet">
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
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      display: flex;
      flex-direction: column;
      height: 100dvh;
      overflow: hidden;
      background: var(--paper);
      color: var(--ink);
      font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      font-size: 15px;
      line-height: 1.4;
    }
    .scroller {
      flex: 1;
      min-height: 0;
      overflow-x: hidden;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
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
    .tabulator {
      margin: 0 1rem 1rem;
      overflow: visible !important;
      background: var(--sheet);
      border: 1px solid #d5cec2;
      border-radius: 12px;
      font-family: inherit;
      font-size: 15px;
      color: var(--ink);
    }
    .tabulator .tabulator-header {
      position: sticky !important;
      top: 0;
      z-index: 30;
      background: var(--ink);
      color: #f3eadc;
      border-bottom: none;
      font-weight: 600;
    }
    .tabulator .tabulator-header .tabulator-col {
      background: var(--ink);
      border-right: none;
    }
    .tabulator .tabulator-header .tabulator-col:hover {
      background: #2a251f;
    }
    .tabulator .tabulator-header .tabulator-col .tabulator-col-content {
      padding: 0.7rem 0.8rem;
    }
    .tabulator .tabulator-col-title { padding-right: 0.4rem; }
    .th-label span, .th-label small { display: block; }
    .th-label small {
      margin-top: 0.15rem;
      color: #b7aa9a;
      font-size: 0.68rem;
      font-weight: 400;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .tabulator .tabulator-header .tabulator-col .tabulator-col-sorter .tabulator-arrow {
      border-bottom-color: #8d8274;
    }
    .tabulator .tabulator-header .tabulator-col[aria-sort="ascending"] .tabulator-arrow {
      border-bottom-color: #d7b48a;
    }
    .tabulator .tabulator-header .tabulator-col[aria-sort="descending"] .tabulator-arrow {
      border-bottom-color: transparent;
      border-top-color: #d7b48a;
    }
    .tabulator .tabulator-tableholder {
      height: auto !important;
      max-height: none !important;
      overflow-x: auto !important;
      overflow-y: hidden !important;
      -webkit-overflow-scrolling: touch;
      background: var(--sheet);
    }
    .tabulator .tabulator-table { background: var(--sheet); }
    .tabulator-row {
      background: var(--sheet);
      border-bottom: 1px solid var(--line);
    }
    .tabulator-row.tabulator-row-even { background: var(--sheet); }
    .tabulator-row:hover,
    .tabulator-row:hover .tabulator-cell.tabulator-frozen { background: var(--hover); }
    .tabulator .tabulator-cell {
      border-right: none;
      padding: 0.62rem 0.8rem;
    }
    .tabulator .tabulator-cell.num,
    .tabulator .tabulator-cell.score {
      font-variant-numeric: tabular-nums;
    }
    .tabulator .tabulator-cell.score { font-weight: 600; }
    .tabulator .tabulator-cell[tabulator-field="Company"] { font-weight: 500; }
    .tabulator .tabulator-cell.top { color: var(--brass); font-weight: 600; }
    .tabulator .neg { color: var(--neg); }
    .tabulator .tabulator-cell.tabulator-frozen,
    .tabulator .tabulator-header .tabulator-col.tabulator-frozen {
      background: var(--sheet);
    }
    .tabulator .tabulator-header .tabulator-col.tabulator-frozen { background: var(--ink); }
    .tabulator .tabulator-header .tabulator-col.tabulator-frozen:hover { background: #2a251f; }
    .tabulator .tabulator-frozen[tabulator-field="Company"] {
      box-shadow: 1px 0 0 var(--line), 12px 0 16px -14px rgba(27, 23, 20, 0.85);
    }
    .tabulator .tabulator-header .tabulator-frozen[tabulator-field="Company"] {
      box-shadow: 1px 0 0 #3a342e;
    }
    .tabulator .tabulator-placeholder { color: var(--muted); }
    .tabulator .tabulator-footer { display: none; }
    .note {
      position: sticky;
      bottom: 0;
      z-index: 40;
      flex: none;
      margin: 0;
      padding: 0.75rem 1.25rem;
      background: #efe8dc;
      border-top: 1px solid #d5cec2;
      color: var(--muted);
      font-size: 0.82rem;
    }
    @media (max-width: 720px) {
      .mast { flex-direction: column; align-items: stretch; gap: 0.7rem; padding: 0.8rem 0.85rem 0.7rem; }
      .mast-side { align-items: stretch; gap: 0.35rem; }
      h1 { font-size: 1.65rem; }
      .deck { font-size: 0.92rem; }
      .updated, .count { margin: 0; }
      .filter input { width: 100%; }
      .hint { padding-left: 0.75rem; padding-right: 0.75rem; }
      .tabulator { margin-left: 0.5rem; margin-right: 0.5rem; }
      .tabulator .tabulator-header .tabulator-col .tabulator-col-content,
      .tabulator .tabulator-cell { padding: 0.55rem 0.7rem; }
      .tabulator .tabulator-cell[tabulator-field="Company"],
      .tabulator .tabulator-col[tabulator-field="Company"] .tabulator-col-title {
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .note { padding-left: 0.75rem; padding-right: 0.75rem; }
    }
  </style>
</head>
<body>
  <div class="scroller" id="scroller">
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
    <p class="hint">Tap a column heading to sort. Scroll sideways for every metric. Rank and company stay fixed.</p>
    <div id="sheet"></div>
  </div>
  <footer class="note">Market cap is shown in billions of US dollars. Growth, margins, efficiency, and Rule of X are percentages. Score is the weighted ranking.</footer>
  <script id="rankings-columns" type="application/json">{{COLUMNS}}</script>
  <script id="rankings-data" type="application/json">{{DATA}}</script>
  <script src="https://cdn.jsdelivr.net/npm/tabulator-tables@6.7.1/dist/js/tabulator.min.js"></script>
  <script>
    const columns = JSON.parse(document.getElementById("rankings-columns").textContent);
    const data = JSON.parse(document.getElementById("rankings-data").textContent);
    const oneDecimal = new Intl.NumberFormat("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const priceFormat = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
    const scoreFormat = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    function label(value, className) {
      const span = document.createElement("span");
      if (className) span.className = className;
      span.textContent = String(value);
      return span;
    }

    function formatNumber(kind, value) {
      if (kind === "price") return priceFormat.format(value);
      if (kind === "cap") return "$" + oneDecimal.format(value / 1000) + "B";
      if (kind === "multiple") return oneDecimal.format(value) + "\\u00d7";
      if (kind === "pct") return oneDecimal.format(value * 100) + "%";
      if (kind === "score") return scoreFormat.format(value);
      return String(value);
    }

    function headerTitle(name, unit) {
      return function () {
        const wrap = document.createElement("span");
        wrap.className = "th-label";
        const title = document.createElement("span");
        title.textContent = name;
        const small = document.createElement("small");
        small.textContent = unit || "\\u00a0";
        wrap.append(title, small);
        return wrap;
      };
    }

    function widths() {
      const narrow = window.matchMedia("(max-width: 720px)").matches;
      return { rank: narrow ? 58 : 78, company: narrow ? 148 : 220 };
    }

    function buildColumns() {
      const size = widths();
      return columns.map((column) => {
        const numeric = column.kind !== "rank" && column.kind !== "company" && column.kind !== "text";
        const definition = {
          title: column.label,
          field: column.key,
          titleFormatter: headerTitle(column.label, column.unit),
          headerSort: true,
          sorter: numeric || column.kind === "rank" ? "number" : "string",
          hozAlign: numeric ? "right" : "left",
          resizable: false,
        };
        if (column.kind === "rank") {
          definition.frozen = true;
          definition.width = size.rank;
          definition.minWidth = size.rank;
          definition.formatter = (cell) => {
            const value = cell.getValue();
            cell.getElement().classList.toggle("top", value <= 3);
            return label(value);
          };
        } else if (column.kind === "company") {
          definition.frozen = true;
          definition.width = size.company;
          definition.minWidth = size.company;
          definition.formatter = (cell) => {
            const value = cell.getValue();
            cell.getElement().title = value;
            return label(value);
          };
        } else if (numeric) {
          definition.minWidth = 112;
          definition.cssClass = column.kind === "score" ? "num score" : "num";
          definition.formatter = (cell) => {
            const value = cell.getValue();
            return label(formatNumber(column.kind, value), value < 0 ? "neg" : "");
          };
        }
        return definition;
      });
    }

    const count = document.getElementById("count");
    const table = new Tabulator("#sheet", {
      data,
      index: "Symbol",
      columns: buildColumns(),
      layout: "fitData",
      renderVertical: "basic",
      renderHorizontal: "basic",
      headerSortTristate: false,
      selectableRows: false,
      placeholder: "No matching companies.",
      initialSort: [{ column: "Rank", dir: "asc" }],
    });

    function showCount(rows) {
      count.textContent = String(rows.length);
    }
    table.on("dataLoaded", showCount);
    table.on("dataFiltered", (_filters, rows) => showCount(rows));

    document.getElementById("q").addEventListener("input", (event) => {
      const query = event.target.value.trim().toLowerCase();
      if (!query) {
        table.clearFilter();
        return;
      }
      table.setFilter((row) => (row.Company + " " + row.Symbol).toLowerCase().includes(query));
    });

    window.matchMedia("(max-width: 720px)").addEventListener("change", () => {
      const size = widths();
      table.getColumn("Rank").updateDefinition({ width: size.rank, minWidth: size.rank });
      table.getColumn("Company").updateDefinition({ width: size.company, minWidth: size.company });
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
