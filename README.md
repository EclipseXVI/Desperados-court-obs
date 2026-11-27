# European Court Performance Observatory

**Course:** Data Science for Business (MSc in Data Science)  
**Team:** Desperados (Thomas Konstantinou, Areti Vika, Christos Rountaris, Maria Kuriaki Diafonidou, Lampros Kouremenos, Athanasios Mponos)  
**Track:** Option B — Working Prototype  

---

## 1. Overview & Policy Question
This interactive observatory enables a **European Semester policy analyst** to evaluate judicial budget effectiveness across four EU Member States with contrasting funding and operational profiles: **Greece (`EL`)**, **Sweden (`SE`)**, **Italy (`IT`)**, and **Romania (`RO`)**.

**Core Research Question:**  
> *Across four EU judicial systems with contrasting funding profiles (Sweden, Italy, Romania, and Greece), how do incoming caseloads, clearance rates, and disposition times evolve over time—and do higher-funded systems consistently convert resources into faster case resolution without backlog accumulation?*

---

## 2. Analytical Scope (v1)
* **Geographies:** Greece (`EL` — focus country), Sweden (`SE` — efficiency benchmark), Italy (`IT` — civil-law peer), Romania (`RO` — high-growth peer).
* **Core Metrics (`2014–2024` observation years):**
  * **Incoming & Resolved Caseloads:** Cases per 100 inhabitants (1st instance).
  * **Clearance Rate ($CR$):** $\frac{\text{Resolved}}{\text{Incoming}} \times 100$ (benchmark $\ge 100\%$ indicates backlog reduction).
  * **Disposition Time ($DT$):** $\frac{\text{Pending}}{\text{Resolved}} \times 365$ (estimated calendar days to resolve pending stock).
  * **Budget Context:** General government expenditure on law courts (€ per inhabitant and % of GDP).
* **Case Categories (Non-Criminal):**
  1. Litigious civil and commercial cases
  2. Administrative cases
  3. All civil, commercial, administrative, and other cases combined

---

## 3. Repository Structure
```text
european-court-observatory/
├── data/
│   ├── raw/2026_EUJS_quantitative.xlsx   # Preserved raw source (CEPEJ / 2026 EUJS)
│   └── processed/eujs_clean.json         # Cleaned, standardized JSON dataset
├── scripts/
│   └── prepare_data.py                   # Reproducible ETL & audit script
├── docs/
│   └── data_dictionary.md                # Variable definitions, denominators & footnotes
├── index.html                            # Interactive web observatory (GitHub Pages entry)
├── app.js                                # Charting, filters & client-side Excel uploader
└── README.md                             # Project documentation & setup guide
```

---

## 4. Data Sources & Evaluation Guardrails
* **Primary Data:** 2026 EU Justice Scoreboard Quantitative Data (`CEPEJ-STAT` & `Eurostat`).
* **Data Hygiene & Caveats Tracked in UI:**
  * **Publication vs. Observation Lag:** Published in 2026; latest judicial observation year is **2024**.
  * **Methodology Breaks & Missing Values:** Flags country-specific breaks (e.g., methodology changes and missing historical entries in `EL`) and distinguishes `NA` vs. `NAP`.
  * **Category Matching:** Separates contested litigious disputes from non-litigious registry workloads and excludes criminal cases.

---

## 5. Running & Hosting
* **https://eclipsexvi.github.io/Desperados-court-obs/)**
