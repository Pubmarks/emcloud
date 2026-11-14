# EMCLOUD rankings

**A weekly-updated scoreboard that ranks about 64 public cloud software companies (Adobe, Palantir, Atlassian, Datadog and others) on growth, profitability, valuation and size.**

[Open the live table: pubmarks.github.io/emcloud](https://pubmarks.github.io/emcloud/)

The table refreshes itself every Saturday.

This is an unofficial, independent project. It isn't affiliated with Bessemer Venture Partners or Nasdaq, and nothing here is investment advice.

## How to use the live table

The [live table](https://pubmarks.github.io/emcloud/) has one row per company, best first.

**What the columns mean**

- **Score** is the weighted result that drives the rank. A higher score means a better rank. [How it's calculated](#ranking-logic).
- **Market cap** is in billions of US dollars.
- **EV / revenue** is how expensive the company is relative to its sales (annualized and forward). Lower means cheaper.
- **Revenue growth, margins, efficiency, Rule of X** are percentages.
- **Efficiency** is revenue growth plus FCF margin, and **FCF margin** is free cash flow as a share of revenue.

The ranking is one opinionated way to compare these companies. Use it as a starting point for your own research. Sort by the metrics you care about instead of trusting the overall rank blindly.

**Want to run it yourself or change the weights?** See [What this repo does](#what-this-repo-does) and [Ranking logic](#ranking-logic).

## What is EMCLOUD?

EMCLOUD is a stock index that tracks emerging public companies that sell cloud software and services, such as Atlassian, Datadog, Palantir and Adobe.

- **Origins.** Bessemer Venture Partners (BVP) launched the BVP Cloud Index in 2013 as a benchmark for public cloud companies. In 2018 BVP partnered with Nasdaq to create the next-generation index, the [BVP Nasdaq Emerging Cloud Index](https://cloudindex.bvp.com/), listed as `EMCLOUD`. It began on 2 October 2018 at a base value of 1,000.
- **Who is in it.** A company must be listed on a US exchange and earn most of its revenue from business software that is delivered through the cloud and sold on a cloud economic model (subscription-, volume- or transaction-based). It needs a market cap of at least $500M, a three-month average daily traded value of at least $5M, and at least three months of trading history.
- **Growth requirement.** At each reconstitution, existing members stay if revenue grew at least 7% in one of the last two fiscal years. New candidates need at least 15% growth in each of the last two years.
- **Weighting.** The index is equal-weighted. It is reconstituted and rebalanced twice a year, in February and August.
- **Size.** It currently has about 64 constituents.

For the authoritative details, see the [BVP Cloud Index site](https://cloudindex.bvp.com/), the [Nasdaq EMCLOUD overview](https://indexes.nasdaqomx.com/Index/Overview/EMCLOUD) and the [official methodology (PDF)](https://indexes.nasdaqomx.com/docs/methodology_EMCLOUD.pdf).

BVP publishes the index constituents together with their key financial metrics: valuation multiples, growth, margins and so on. It doesn't say which company is "best". This repo fills that gap with a transparent, weighted ranking.

## What this repo does

Every Saturday, GitHub Actions turns BVP's published spreadsheet into a ranked table.

1. **Download.** `download_rank.py` fetches the [BVP spreadsheet](https://bvp-cloud-index.s3.amazonaws.com/BVP-Nasdaq-Emerging-Cloud-Index.xlsx) and reads the `Index Constituents` sheet.
2. **Rank.** It scores every company and writes the result to [`emcloud.csv`](emcloud.csv). See [Ranking logic](#ranking-logic).
3. **Render.** `render_html.py` builds a static, sortable and filterable page at `html/index.html`.
4. **Publish.** The page is deployed to [GitHub Pages](https://pubmarks.github.io/emcloud/).

The automation lives in two workflows:

| Workflow | Trigger | Job |
| --- | --- | --- |
| [`update-rankings.yml`](.github/workflows/update-rankings.yml) | Saturdays at 02:00 UTC, or manually | Runs `download_rank.py` and commits `emcloud.csv` |
| [`publish-page.yml`](.github/workflows/publish-page.yml) | After a successful update, or manually | Runs `render_html.py`, commits `html/`, and deploys to Pages |

### Run it locally

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer.

```sh
uv sync
uv run python download_rank.py   # downloads data and writes emcloud.csv
uv run python render_html.py     # writes html/index.html
```

### Files

| Path | Purpose |
| --- | --- |
| `download_rank.py` | Downloads the BVP data and calculates the rankings |
| `render_html.py` | Renders `emcloud.csv` into the static page |
| `emcloud.csv` | The latest ranked output |
| `html/` | The generated site served by GitHub Pages |
| `.github/workflows/` | The weekly update and publish automation |

## Ranking logic

The ranking is a weighted sum of **percentile-style ranks**, not raw values. Ranking each metric first stops outliers from dominating. For example, Palantir's very high EV/revenue multiple counts as "most expensive", not as a number many times bigger than everyone else's.

### 1. Rank each metric

For each of the 10 metrics, companies are ranked from 1 (worst) to N (best), where N is the number of companies. Ties share an average rank. The direction depends on the metric:

| Metric | Better when | Why |
| --- | --- | --- |
| Market cap | Higher | Rewards scale |
| Revenue growth rate | Higher | Rewards momentum |
| LTM FCF margin | Higher | Rewards cash generation (free cash flow is cash from operations minus capex) |
| Efficiency | Higher | Revenue growth plus FCF margin (a "Rule of 40" style score) |
| Gross margin | Higher | Rewards pricing power and unit economics |
| EV / annualized revenue | **Lower** | Cheaper valuation scores better |
| EV / forward revenue | **Lower** | Cheaper valuation scores better |
| SG&A margin | **Lower** | Leaner overhead scores better |
| R&D (% of revenue) | Higher | Rewards reinvestment in product |
| Sales & marketing (% of revenue) | Higher | Rewards investment in go-to-market |

### 2. Apply the weights

| Metric | Weight |
| --- | ---: |
| Market cap | 20% |
| LTM FCF margin | 15% |
| Revenue growth rate | 15% |
| Efficiency | 10% |
| EV / annualized revenue | 10% |
| EV / forward revenue | 10% |
| Gross margin | 10% |
| Sales & marketing (% of revenue) | 5% |
| R&D (% of revenue) | 2.5% |
| SG&A margin | 2.5% |
| **Total** | **100%** |

Grouped by theme, that is roughly:

- **Scale: 20%.** Market cap.
- **Cash generation and growth: 40%.** FCF margin, revenue growth and efficiency.
- **Valuation: 20%.** The two EV/revenue multiples.
- **Margins and spending: 20%.** Gross margin, S&M, R&D and SG&A.

### 3. Score and rank

```
Score = Σ (rank of metric × weight of metric), rounded to 2 decimals
Rank  = position when companies are sorted by Score, highest first
```

A company that came first on every metric would score N, the number of companies. If two companies have exactly the same score, the tie is broken arbitrarily, so every company still gets a unique rank from 1 to N.

### Caveats

- The weights are a judgement call, not a derived or backtested model. To change the model, edit the `weights` dictionary and the `ascending` flags in `calculate_rankings()` in [`download_rank.py`](download_rank.py).
- Scores are relative. They compare companies within the current index and say nothing about absolute quality or price.
- The data comes from BVP's spreadsheet as published. Any gaps or errors in it carry through to the ranking.
- Market cap is in USD millions in the source data, and the page shows it in billions. Growth, margins and efficiency are stored as fractions, and the page shows them as percentages.
- The `Rule of X` column is shown for reference but isn't part of the score. In the source data it is 2 × revenue growth + FCF margin.
