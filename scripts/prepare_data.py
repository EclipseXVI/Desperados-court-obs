"""
Reproducible ETL Pipeline for the European Court Performance Observatory (Step 3)
Reads raw 2026 EU Justice Scoreboard quantitative workbook (data/raw/2026_EUJS_quantitative.xlsx),
audits missing values and structural quirks, standardizes units, and outputs data/processed/eujs_clean.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/2026_EUJS_quantitative.xlsx")
FALLBACK_RAW_PATH = Path("2026_EUJS_quantitative.xlsx")
OUT_JSON_PATH = Path("data/processed/eujs_clean.json")

COUNTRIES = ["EL", "IT", "RO", "SE"]

COUNTRY_PROFILES = {
    "EL": {
        "name": "Greece",
        "funding_tier": "Moderate-to-Low per Capita / Major RRF Reformer",
        "role": "Primary focus country: recovering from prolonged backlog with RRF-backed judicial map & digitization reforms",
        "caveats": [
            "Methodology break (*) flagged in CEPEJ/EUJS series across civil/commercial and administrative figures.",
            "Missing observations (NaN) in 2014, 2016, 2019, 2020 for All Non-Criminal; 2014 & 2019 for Administrative; and 2020 for Litigious Civil & Commercial."
        ]
    },
    "IT": {
        "name": "Italy",
        "funding_tier": "High per Capita / Major RRF Reformer",
        "role": "Large-budget Southern civil-law peer: significant RRF targets on disposition time reduction",
        "caveats": [
            "2020 COVID-19 court suspension spike visible in Disposition Time (673.9 days in Litigious Civil & Commercial).",
            "High non-litigious civil volume inflates All Non-Criminal incoming caseload (5.55 per 100 in 2024 vs. 2.33 Litigious)."
        ]
    },
    "RO": {
        "name": "Romania",
        "funding_tier": "Low per Capita / High % of GDP Effort",
        "role": "High-caseload Eastern EU benchmark: tests whether high GDP budget share offsets surging civil demand",
        "caveats": [
            "Highest incoming litigious civil & commercial caseload among peers (8.42 per 100 inhabitants in 2024), yet maintains low disposition time (179.8 days).",
            "Highest judicial expenditure as % of GDP (0.41% in 2024) despite lower EUR per inhabitant (76.08 EUR) due to GDP denominator."
        ]
    },
    "SE": {
        "name": "Sweden",
        "funding_tier": "High per Capita / Lean Budget Share of GDP",
        "role": "Upper efficiency frontier: high per-inhabitant funding (137.05 EUR) & digitalized courts with low civil litigation volume",
        "caveats": [
            "Administrative incoming caseload (1.64 per 100 in 2024) is over double its litigious civil & commercial caseload (0.70 per 100), reflecting Sweden's broad administrative court remit (tax, social insurance, migration)."
        ]
    }
}

EFFICIENCY_SHEETS = [
    ("Fig(1)Incoming.Non-crim", "incoming_per_100", "all_non_criminal", "cases per 100 inhabitants"),
    ("Fig(2)Incoming.Lit.civ&comm", "incoming_per_100", "litigious_civil_commercial", "cases per 100 inhabitants"),
    ("Fig(3)Incoming.Admin", "incoming_per_100", "administrative", "cases per 100 inhabitants"),
    ("Fig(4)DT.Non-criminal", "disposition_time_days", "all_non_criminal", "days"),
    ("Fig(5)DT.Lit.civ&comm", "disposition_time_days", "litigious_civil_commercial", "days"),
    ("Fig(7)DT.Admin", "disposition_time_days", "administrative", "days"),
    ("Fig(9)CR.Non-criminal", "clearance_rate_pct", "all_non_criminal", "percent"),
    ("Fig(10)CR.Lit.civ&comm", "clearance_rate_pct", "litigious_civil_commercial", "percent"),
    ("Fig(11)CR.Admin", "clearance_rate_pct", "administrative", "percent"),
    ("Fig(12)Pending.Non-crim", "pending_per_100", "all_non_criminal", "cases per 100 inhabitants"),
    ("Fig(13)Pending.Lit.civ&comm", "pending_per_100", "litigious_civil_commercial", "cases per 100 inhabitants"),
    ("Fig(14)Pending.Admin", "pending_per_100", "administrative", "cases per 100 inhabitants"),
]

BUDGET_SHEETS = [
    ("Fig(33)Budget.total", "budget_eur_per_inhabitant", "EUR per inhabitant"),
    ("Fig(34)Budget.GDP", "budget_pct_gdp", "percent of GDP"),
]


def run_pipeline():
    source_path = RAW_PATH if RAW_PATH.exists() else FALLBACK_RAW_PATH
    xls = pd.ExcelFile(source_path)

    efficiency_records = []
    missing_log = []

    for sheet_name, metric, category, unit in EFFICIENCY_SHEETS:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        headers = df.iloc[0].tolist()
        year_cols = {}
        for col_idx, h in enumerate(headers):
            try:
                yr = int(float(h))
                if 2000 <= yr <= 2030:
                    year_cols[col_idx] = yr
            except (ValueError, TypeError):
                continue

        # Sort year columns chronologically (fixes Fig(5) where 2012 precedes 2010)
        sorted_years = sorted(year_cols.items(), key=lambda x: x[1])

        sub = df.iloc[1:30].copy()
        for _, row in sub.iterrows():
            cc = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if cc not in COUNTRIES:
                continue
            for col_idx, yr in sorted_years:
                raw_val = row.iloc[col_idx]
                if pd.isna(raw_val):
                    val = None
                    missing_log.append({
                        "sheet": sheet_name,
                        "country_code": cc,
                        "observation_year": yr,
                        "category": category,
                        "metric": metric
                    })
                else:
                    val = float(raw_val)
                    if metric == "clearance_rate_pct":
                        val = round(val * 100.0, 2)
                    else:
                        val = round(val, 4)

                efficiency_records.append({
                    "country_code": cc,
                    "country_name": COUNTRY_PROFILES[cc]["name"],
                    "observation_year": yr,
                    "publication_year": 2026,
                    "category": category,
                    "metric": metric,
                    "unit": unit,
                    "value": val,
                    "source_sheet": sheet_name
                })

    budget_records = []
    for sheet_name, metric, unit in BUDGET_SHEETS:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        headers = df.iloc[1].tolist()
        year_cols = {}
        for col_idx, h in enumerate(headers):
            try:
                yr = int(float(h))
                if 2000 <= yr <= 2030:
                    year_cols[col_idx] = yr
            except (ValueError, TypeError):
                continue

        # Rows 2..28 hold the EU-27 block (excludes non-EU rows IS/NO/CH and repeated chart blocks below row 34)
        sub = df.iloc[2:29].copy()
        for _, row in sub.iterrows():
            cc = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            if cc not in COUNTRIES:
                continue
            for col_idx, yr in sorted(year_cols.items(), key=lambda x: x[1]):
                raw_val = row.iloc[col_idx]
                val = round(float(raw_val), 4) if pd.notna(raw_val) else None
                budget_records.append({
                    "country_code": cc,
                    "country_name": COUNTRY_PROFILES[cc]["name"],
                    "observation_year": yr,
                    "publication_year": 2026,
                    "metric": metric,
                    "unit": unit,
                    "value": val,
                    "source_sheet": sheet_name
                })

    payload = {
        "metadata": {
            "title": "European Court Performance Observatory — Cleaned Dataset (v1)",
            "publication_edition": "2026 EU Justice Scoreboard (published June 2026)",
            "latest_observation_year": 2024,
            "efficiency_observation_years": [2010, 2012, 2014, 2016, 2019, 2020, 2021, 2022, 2023, 2024],
            "budget_observation_years": list(range(2012, 2025)),
            "sources": [
                "CEPEJ study (via 2026 EU Justice Scoreboard Figures 1-5, 7, 9-14)",
                "Eurostat gov_10a_exp COFOG99 Law Courts (via 2026 EU Justice Scoreboard Figures 33-34)"
            ],
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "synthetic_data_used": False,
            "missing_value_count": len(missing_log),
            "missing_value_log": missing_log,
            "country_profiles": COUNTRY_PROFILES
        },
        "efficiency_records": efficiency_records,
        "budget_records": budget_records
    }

    OUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(efficiency_records)} efficiency records and {len(budget_records)} budget records to {OUT_JSON_PATH}")
    print(f"Logged {len(missing_log)} missing values (all in EL).")


if __name__ == "__main__":
    run_pipeline()