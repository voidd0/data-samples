#!/usr/bin/env python3
"""Python job offers on justjoin.it, 2026-11-26: the CSV and every number of article.md.

  python3 analysis.py              read the CSV next to this file, print the tables, write numbers.json (stdlib only)
  python3 analysis.py build [--raw items.json]
                                   (re)make the CSV from the public run dataset; needs vøiddo's in-house cleaning
                                   tools (data_file_clean.py, data_sample.py) in the folder named by VOIDDO_SCRIPTS

Source: one run of vøiddo's justjoin.it scraper on 2026-11-26 (run ljZCyGCTezLnv2BgC, dataset 2aUBz9sEIVr3P0b8g),
input {"categories": ["python"], "salaryOnly": false, "maxItems": 2000}: the site's Python category, all locations,
offers with and without a salary. Public listing pages only, robots.txt obeyed.

Rules used for every number:
- one row per offer: duplicates by url are dropped (data_file_clean.clean, key url); a multi-city offer is one row,
  its main city is the `city` column;
- salaries are the employer's own figures in the employer's currency; only PLN figures are summarised (other
  currencies are counted, not converted);
- per-month figures: month as stated, hour x 168 (21 working days x 8 hours), day x 21, year / 12;
- an offer's figure is the midpoint of its range (from + to) / 2, per contract type (an offer with B2B and an
  employment contract counts in both groups);
- quartiles: statistics.quantiles(n=4, method="inclusive") (linear interpolation); median = statistics.median;
- a median or quartile is given only for a group with at least MIN_N offers; smaller groups show n only;
- a B2B "per month" range under 1,000 PLN is taken as a unit error (it reads like an hourly rate) and left out of
  the figures; it is counted in `unit_errors`.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE / "python-jobs-poland-justjoin-2026-11-26.csv"
NUMBERS = HERE / "numbers.json"
RUN_ID, DATASET_ID = "ljZCyGCTezLnv2BgC", "2aUBz9sEIVr3P0b8g"
SITE_COUNT = 1029            # the run log: "all-locations/python: 1029 offers on the site" (one per city of an offer)
DATASET_ITEMS = 528          # rows in the run dataset before the CSV was made
MIN_N = 20
PER_MONTH = {"month": 1.0, "hour": 168.0, "day": 21.0, "year": 1 / 12}
TOP_CITIES = 6
OUTSIDE_POLAND = {"London", "Lisbon", "Paris", "Dublin", "Pune", "Chester", "Malmö", "Stockholm City", "Porto",
                  "Chennai", "Nicosia"}

# CSV columns: facts about the offer only (no description, no recruiter, no street address or map point)
COLS = ["offerId", "url", "title", "companyName", "category", "seniority", "workMode", "workingTime", "city",
        "locations", "skills", "contractTypes", "salaryFrom", "salaryTo", "currency", "salaryInterval", "salaryType",
        "contractType", "salaries", "promoted", "remoteInterview", "openToUkrainians", "publishedAt", "expiresAt",
        "scrapedAt"]


# ------------------------------------------------------------------------------------------------ build the CSV

def build(argv: list[str]) -> int:
    import os
    tools = os.environ.get("VOIDDO_SCRIPTS")
    if not tools:
        print("build: set VOIDDO_SCRIPTS to the folder with data_file_clean.py and data_sample.py", file=sys.stderr)
        return 2
    sys.path.insert(0, tools)
    from data_file_clean import clean                 # dedupe by url, values trimmed, nothing filled in
    from data_sample import SKIP_CHECK, personal      # e-mail / messenger / phone-like numbers

    if "--raw" in argv:
        items = json.loads(Path(argv[argv.index("--raw") + 1]).read_text(encoding="utf-8"))
    else:
        import urllib.request
        url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?format=json&clean=1&limit=5000"
        req = urllib.request.Request(url, headers={"User-Agent": "voiddo-sample/1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            items = json.loads(r.read().decode("utf-8"))

    def cell(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if v is None:
            return ""
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            return "; ".join(v)
        if isinstance(v, (list, dict)):
            return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
        return str(v)

    rows = [{c: cell(it.get(c)) for c in COLS} for it in items]
    kept, info = clean(COLS, rows, key="url")
    check = [c for c in COLS if not any(c.lower().endswith(s) or c.lower() == s for s in SKIP_CHECK)]
    for i, r in enumerate(kept):
        for c in check:
            if personal(r[c]):
                print(f"row {i} column {c} looks like a contact: {r[c][:80]!r}; nothing written", file=sys.stderr)
                return 3
    with open(CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(kept)
    print(json.dumps({**{k: info[k] for k in ("rows_in", "rows_out", "duplicates", "key")}, "checked": check,
                      "csv": str(CSV)}, ensure_ascii=False))
    return 0


# ------------------------------------------------------------------------------------------------ the numbers

def fold(s: str) -> str:
    t = s.replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii").lower().strip()


CITY_NAMES = {"warszawa": "Warsaw", "warsaw": "Warsaw", "krakow": "Kraków", "wroclaw": "Wrocław",
              "gdansk": "Gdańsk", "lodz": "Łódź", "poznan": "Poznań", "katowice": "Katowice", "gdynia": "Gdynia"}


def city_of(r: dict) -> str:
    """One name per city: Warszawa / Warsaw, Krakow / Kraków ... are the same place written two ways."""
    c = r["city"].strip()
    return CITY_NAMES.get(fold(c), c) if c else "(none)"


def monthly(s: dict) -> float:
    return (s["from"] + s["to"]) / 2 * PER_MONTH[s["interval"]]


def r100(v: float) -> int:
    """To the nearest 100 PLN, halves up (22,050 -> 22,100)."""
    return int(math.floor(v / 100.0 + 0.5)) * 100


def stats(values: list[float]) -> dict:
    out = {"n": len(values)}
    if len(values) >= MIN_N:
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        out.update({"p25": round(q1), "median": round(statistics.median(values)), "p75": round(q3)})
        out.update({k + "_r100": r100(out[k]) for k in ("p25", "median", "p75")})
    return out


def pct(a: int, b: int) -> float:
    return round(100.0 * a / b, 1) if b else 0.0


def analyse() -> dict:
    with open(CSV, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    urls = [r["url"] for r in rows]
    assert len(urls) == len(set(urls)), "the CSV has duplicate urls"
    for r in rows:
        r["_pay"] = json.loads(r["salaries"]) if r["salaries"] else []
        r["_city"] = city_of(r)
    n = len(rows)
    paid = [r for r in rows if r["_pay"]]

    # every PLN figure per contract key, with the unit errors and the other currencies counted
    unit_errors, other_ccy, no_type = [], Counter(), Counter()
    fig: dict[tuple, list[tuple[dict, float, dict]]] = {}
    units = Counter()
    for r in paid:
        for s in r["_pay"]:
            if s["contractType"] is None:
                no_type[s["currency"]] += 1
                continue
            if s["currency"] != "PLN":
                other_ccy[s["currency"]] += 1
                continue
            if s["contractType"] == "B2B" and s["interval"] == "month" and s["to"] < 1000:
                unit_errors.append({"url": r["url"], "from": s["from"], "to": s["to"]})
                continue
            key = (s["contractType"], s["type"])
            units[(s["contractType"], s["interval"])] += 1
            fig.setdefault(key, []).append((r, monthly(s), s))

    b2b = fig.get(("B2B", "net"), [])
    uop = fig.get(("employment contract", "gross"), [])
    pln_offers = {r["url"] for lst in fig.values() for r, _m, _s in lst}

    def by(lst, keyf, keys):
        return {k: stats([m for r, m, _s in lst if keyf(r) == k]) for k in keys}

    contract_tbl = {}
    for key, lst in sorted(fig.items(), key=lambda kv: -len(kv[1])):
        st = stats([m for _r, m, _s in lst])
        if len(lst) >= MIN_N:
            st["median_from"] = round(statistics.median([s["from"] * PER_MONTH[s["interval"]] for _r, _m, s in lst]))
            st["median_to"] = round(statistics.median([s["to"] * PER_MONTH[s["interval"]] for _r, _m, s in lst]))
            st["median_from_r100"] = r100(st["median_from"])
            st["median_to_r100"] = r100(st["median_to"])
        contract_tbl[f"{key[0]} ({key[1]})"] = st

    # location: fully remote offers on their own; the rest by main city (top Polish cities, other Polish cities,
    # outside Poland)
    def loc(r):
        if r["workMode"] == "remote":
            return "remote"
        return "outside Poland" if r["city"] in OUTSIDE_POLAND else r["_city"]
    on_site = Counter(loc(r) for r in rows if loc(r) not in ("remote", "outside Poland"))
    top = [c for c, _ in on_site.most_common(TOP_CITIES)]
    group = {r["url"]: (loc(r) if loc(r) in top or loc(r) in ("remote", "outside Poland") else "other Polish cities")
             for r in rows}
    loc_tbl = {}
    for k in top + ["other Polish cities", "outside Poland", "remote"]:
        sel = [r for r in rows if group[r["url"]] == k]
        sp = [r for r in sel if r["_pay"]]
        bl = [(r, m) for r, m, _s in b2b if group[r["url"]] == k]
        loc_tbl[k] = {"offers": len(sel), "with_salary": len(sp), "with_salary_pct": pct(len(sp), len(sel)),
                      "b2b_net": stats([m for _r, m in bl]),
                      "b2b_net_senior_share_pct": pct(sum(1 for r, _m in bl if r["seniority"] == "senior"), len(bl)),
                      "b2b_net_senior_only": stats([m for r, m in bl if r["seniority"] == "senior"])}
    assert sum(v["offers"] for v in loc_tbl.values()) == n

    # how much the hourly conversion matters: the B2B figures again with 160 hours a month instead of 168
    b2b_160 = [m * (160 / 168) if s["interval"] == "hour" else m for _r, m, s in b2b]
    b2b_hourly_n = sum(1 for _r, _m, s in b2b if s["interval"] == "hour")

    companies = Counter(r["companyName"] for r in rows)
    top_co, top_co_n = companies.most_common(1)[0]
    levels = ["junior", "mid", "senior", "manager"]
    sen_tbl = {}
    for lv in levels:
        sel = [r for r in rows if r["seniority"] == lv]
        sel_rest = [r for r in sel if r["companyName"] != top_co]
        sen_tbl[lv] = {"offers": len(sel), "with_salary": sum(1 for r in sel if r["_pay"]),
                       "with_salary_pct": pct(sum(1 for r in sel if r["_pay"]), len(sel)),
                       "without_top_company": {"offers": len(sel_rest),
                                               "with_salary_pct": pct(sum(1 for r in sel_rest if r["_pay"]),
                                                                      len(sel_rest))},
                       "b2b_net": stats([m for r, m, _s in b2b if r["seniority"] == lv]),
                       "employment_gross": stats([m for r, m, _s in uop if r["seniority"] == lv])}

    mode_tbl = {}
    for md in ("remote", "hybrid", "office"):
        sel = [r for r in rows if r["workMode"] == md]
        bl = [r for r, _m, _s in b2b if r["workMode"] == md]
        mode_tbl[md] = {"offers": len(sel), "with_salary": sum(1 for r in sel if r["_pay"]),
                        "b2b_net": stats([m for r, m, _s in b2b if r["workMode"] == md]),
                        "b2b_net_senior_share_pct": pct(sum(1 for r in bl if r["seniority"] == "senior"), len(bl))}

    top_co_paid = sum(1 for r in paid if r["companyName"] == top_co)
    rest = [r for r in rows if r["companyName"] != top_co]
    rest_paid = [r for r in rest if r["_pay"]]

    ratios = sorted(s["to"] / s["from"] for _r, _m, s in b2b + uop if s["from"])
    multi = sum(1 for r in rows if len([x for x in r["locations"].split("; ") if x]) > 1)
    same = Counter((r["companyName"], r["title"], r["salaries"]) for r in rows)
    same_paid = Counter((r["companyName"], r["title"], r["salaries"]) for r in paid)
    both = sum(1 for r in paid if {s["contractType"] for s in r["_pay"]} >= {"B2B", "employment contract"})
    pub = Counter(r["publishedAt"][:10] for r in rows)
    b2b_offers = {r["url"] for r, _m, _s in b2b}
    senior_mid = None
    if "median" in sen_tbl["senior"]["b2b_net"] and "median" in sen_tbl["mid"]["b2b_net"]:
        senior_mid = round(sen_tbl["senior"]["b2b_net"]["median"] / sen_tbl["mid"]["b2b_net"]["median"], 2)

    return {
        "source": {"site": "justjoin.it", "category": "Python", "location": "all locations",
                   "collected_utc": rows[0]["scrapedAt"] if rows else None, "run_id": RUN_ID, "dataset_id": DATASET_ID,
                   "site_count_listing_entries": SITE_COUNT},
        "rules": {"min_n": MIN_N, "per_month": {"hour": 168, "day": 21, "year": "1/12"},
                  "figure": "midpoint of the range, PLN per month", "quartiles": "inclusive (linear interpolation)"},
        "offers": n,
        "with_salary": len(paid), "with_salary_pct": pct(len(paid), n),
        "without_salary": n - len(paid),
        "offers_with_pln_figure": len(pln_offers),
        "offers_with_b2b_net_pln": len(b2b_offers),
        "offers_with_both_b2b_and_employment_salary": both,
        "salary_entries_other_currency": dict(other_ccy),
        "salary_entries_other_currency_total": sum(other_ccy.values()),
        "salary_entries_without_contract_type": sum(no_type.values()),
        "salary_entries_without_contract_type_by_currency": dict(no_type),
        "unit_errors": unit_errors,
        "pln_entries_by_contract_and_unit": {f"{k[0]} / {k[1]}": v for k, v in units.most_common()},
        "contracts": contract_tbl,
        "locations": loc_tbl, "top_cities": top,
        "seniority_all": {lv: sum(1 for r in rows if r["seniority"] == lv) for lv in levels},
        "seniority": sen_tbl,
        "work_mode": mode_tbl,
        "senior_to_mid_b2b_median_ratio": senior_mid,
        "range_to_over_from_median": round(statistics.median(ratios), 3) if ratios else None,
        "range_to_over_from_n": len(ratios),
        "range_top_above_bottom_pct": round(100 * (statistics.median(ratios) - 1), 1) if ratios else None,
        "companies": len(companies), "companies_with_salary": len({r["companyName"] for r in paid}),
        "top_company": {"name": top_co, "offers": top_co_n, "offers_pct": pct(top_co_n, n), "with_salary": top_co_paid,
                        "seniority": dict(Counter(r["seniority"] for r in rows if r["companyName"] == top_co)),
                        "same_company_title_salary_extra_rows": sum(v - 1 for k, v in same.items()
                                                                    if v > 1 and k[0] == top_co)},
        "work_mode_pct": {md: pct(v["offers"], n) for md, v in mode_tbl.items()},
        "seniority_pct": {lv: pct(v["offers"], n) for lv, v in sen_tbl.items()},
        "b2b_entries_by_unit_pct": {u: pct(units[("B2B", u)], len(b2b)) for u in ("hour", "month", "day")},
        "without_top_company": {"offers": len(rest), "with_salary": len(rest_paid),
                                "with_salary_pct": pct(len(rest_paid), len(rest))},
        "multi_city_offers": multi,
        "city_list_entries_in_file": sum(len([x for x in r["locations"].split("; ") if x]) for r in rows),
        "dataset_items": DATASET_ITEMS, "duplicate_urls_dropped": DATASET_ITEMS - n,
        "outside_poland_main_city": sum(1 for r in rows if r["city"] in OUTSIDE_POLAND),
        "outside_poland_with_salary": sum(1 for r in paid if r["city"] in OUTSIDE_POLAND),
        "outside_poland_remote": sum(1 for r in rows if r["city"] in OUTSIDE_POLAND and r["workMode"] == "remote"),
        "same_company_title_salary_extra_rows": sum(v - 1 for v in same.values() if v > 1),
        "same_company_title_salary_extra_rows_with_salary": sum(v - 1 for v in same_paid.values() if v > 1),
        "same_company_title_salary_extra_rows_other_without_salary": sum(
            v - 1 for k, v in same.items() if v > 1 and k[0] != top_co and not k[2]),
        "b2b_to_employment_offers_ratio": round(len(b2b) / len(uop), 1) if uop else None,
        "published_on_or_after_2026_11_22": sum(v for d, v in pub.items() if d >= "2026-11-22"),
        "b2b_hourly_entries": b2b_hourly_n,
        "b2b_net_if_160_hours": stats(b2b_160),
    }


def fmt(st: dict, k: str = "median") -> str:
    return f"{st[k + '_r100']:,}" if k + "_r100" in st else "-"


def tables(nb: dict) -> str:
    out = ["| Where | Offers | With salary | B2B net offers | B2B median (PLN/month) |", "|---|---:|---:|---:|---:|"]
    for k, v in nb["locations"].items():
        name = {"remote": "Fully remote", "outside Poland": "Outside Poland (office or hybrid)",
                "other Polish cities": "Other Polish cities"}.get(k, k)
        out.append(f"| {name} | {v['offers']} | {v['with_salary']} ({v['with_salary_pct']:.0f} %) | "
                   f"{v['b2b_net']['n']} | {fmt(v['b2b_net'])} |")
    out += ["", "| Contract (as stated) | n | P25 | Median | P75 |", "|---|---:|---:|---:|---:|"]
    for k, v in nb["contracts"].items():
        out.append(f"| {k} | {v['n']} | {fmt(v, 'p25')} | {fmt(v)} | {fmt(v, 'p75')} |")
    out += ["", "| Seniority | Offers | With salary | B2B net n | B2B P25 | B2B median | B2B P75 |",
            "|---|---:|---:|---:|---:|---:|---:|"]
    for k, v in nb["seniority"].items():
        b = v["b2b_net"]
        out.append(f"| {k} | {v['offers']} | {v['with_salary']} | {b['n']} | {fmt(b, 'p25')} | {fmt(b)} | "
                   f"{fmt(b, 'p75')} |")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"]:
        return build(argv[1:])
    nb = analyse()
    NUMBERS.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(tables(nb))
    print(f"\nnumbers.json written ({NUMBERS})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
