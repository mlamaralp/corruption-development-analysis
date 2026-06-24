# Setup Instructions

Follow these steps before running `analysis.ipynb`.

---

## 1. Download the Data Files

You need four files. All are free — no account or registration required.

---

### File 1: Corruption Perceptions Index (CPI) — Transparency International

The CPI is the most widely used measure of perceived public sector corruption. It aggregates expert and business surveys from over a dozen independent sources, making it more robust than any single survey. It covers 180+ countries annually since 1995, which gives enough temporal depth for trend analysis.

- Paste this URL directly into your browser to download the ZIP:
  `https://images.transparencycdn.org/images/CPI2025_Results.zip`
- Extract the ZIP and open the Excel file
- At the bottom of the Excel, click the sheet **"CPI Timeseries 2012 - 2025"**
- File → Save As → CSV (semicolon-delimited) → name it `cpi_wide.csv`
- Place it in the `data/` folder

Expected format: semicolon-separated CSV with 2 header rows to skip. Real column names on row 3: `Country / Territory`, `ISO3`, `Region`, `CPI score 2025`, `CPI score 2024`, ..., `CPI Score 2012`

---

### File 2: GDP per Capita, PPP — World Bank

GDP per capita in purchasing power parity (constant 2017 USD) is the standard measure for comparing living standards across countries while removing price level differences. It is the most appropriate income variable to pair with the CPI because it allows direct comparison between, say, Qatar and Norway without being distorted by cost-of-living differences.

- Paste this URL directly into your browser to download the ZIP:
  `https://api.worldbank.org/v2/en/indicator/NY.GDP.PCAP.PP.KD?downloadformat=csv`
- Extract the ZIP — you will get three files. Use only the one named `API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_XXXXXXX.csv` (ignore the two metadata files)
- Rename it to `gdp_per_capita_raw.csv`
- Place it in the `data/` folder

Expected format: wide CSV — countries as rows, years as column headers (`1960`, `1961`, ..., `2023`), plus columns `Country Name`, `Country Code`, `Indicator Name`, `Indicator Code`

---

### File 3: Government Effectiveness Index — World Bank (WGI)

The World Bank's Worldwide Governance Indicators (WGI) include a Government Effectiveness score that captures perceptions of the quality of public services, civil service, and policy implementation. It is a natural complement to the CPI because it separates the question of institutional capacity from corruption perception, which lets us test whether a country is corrupt because its government is weak, or despite having capable institutions.

- Paste this URL directly into your browser to download the ZIP:
  `https://databank.worldbank.org/data/download/WGI_CSV.zip`
- Extract the ZIP — you will get three files: `WGICountry.csv`, `WGICSV.csv`, `WGISeries.csv`
- Use only **`WGICSV.csv`** — this is the one with all country data
- Rename it to `gov_effectiveness_raw.csv`
- Place it in the `data/` folder

Expected format: wide CSV with columns `Country Name`, `Country Code`, `Indicator Name`, `Indicator Code`, and year columns (`1996`, `1998`, `2000`, ..., `2024`). This file contains 36 WGI indicator variants — the reshape code below filters to `GOV_WGI_GE.EST` (Government Effectiveness, governance estimate).

---

### File 4: Human Development Index (HDI) — UNDP

The HDI combines life expectancy, education and income into a single composite score (0–1). Including it allows the analysis to go beyond pure economic output (GDP) and ask whether corruption affects broader human welfare — health, education access, and standard of living together. It is one of the most cited development indicators in academic and policy research.

- Paste this URL directly into your browser to download the CSV:
  `https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv`
- Rename it to `hdi_raw.csv`
- Place it in the `data/` folder

Expected format: long-format CSV with columns `country`, `iso3`, and one column per indicator per year (e.g. `hdi_2022`, `hdi_2021`, ...). The reshape code below extracts only the HDI columns.

---

## 2. Reshape the Files to Long Format

All four files are in wide format (one column per year) or need filtering. Run this code once — either in a separate script or as the first cell of `analysis.ipynb` — to produce the cleaned CSVs the notebook expects.

```python
import pandas as pd

# ── CPI ───────────────────────────────────────────────────────────────────────
# The CPI CSV is semicolon-separated with 2 header rows
cpi_raw = pd.read_csv('data/cpi_wide.csv', sep=';', skiprows=2)
cpi_raw.columns = cpi_raw.iloc[0]
cpi_raw = cpi_raw.drop(index=0).reset_index(drop=True)
score_cols = [c for c in cpi_raw.columns if str(c).lower().startswith('cpi score')]
cpi_long = cpi_raw.melt(
    id_vars=['Country / Territory', 'ISO3', 'Region'],
    value_vars=score_cols,
    var_name='year_label',
    value_name='cpi_score'
)
cpi_long['year'] = cpi_long['year_label'].str.extract(r'(\d{4})').astype(int)
cpi_long = cpi_long.rename(columns={'Country / Territory': 'country', 'ISO3': 'iso3', 'Region': 'region'})
cpi_long['cpi_score'] = pd.to_numeric(cpi_long['cpi_score'], errors='coerce')
cpi_long = cpi_long[['country', 'iso3', 'region', 'year', 'cpi_score']].dropna(subset=['cpi_score'])
cpi_long.to_csv('data/cpi_2000_2023.csv', index=False)
print(f"CPI: {cpi_long.shape[0]:,} rows | years {cpi_long['year'].min()}-{cpi_long['year'].max()}")

# ── GDP per capita ────────────────────────────────────────────────────────────
# skiprows=4 skips the World Bank header lines before the actual data starts
gdp_wide = pd.read_csv('data/gdp_per_capita_raw.csv', skiprows=4)
year_cols = [c for c in gdp_wide.columns if c.isdigit()]
gdp_long = gdp_wide.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols,
    var_name='year',
    value_name='gdp_per_capita_ppp'
)
gdp_long['year'] = gdp_long['year'].astype(int)
gdp_long = gdp_long.rename(columns={'Country Name': 'country', 'Country Code': 'iso3'})
gdp_long = gdp_long[gdp_long['year'].between(2000, 2023)].dropna(subset=['gdp_per_capita_ppp'])
print(f"GDP: {gdp_long.shape}")

# ── Government Effectiveness (WGI) ───────────────────────────────────────────
# WGICSV.csv contains all 6 WGI indicators — filter to GE.EST only
wgi = pd.read_csv('data/gov_effectiveness_raw.csv')
gov = wgi[wgi['Indicator Code'] == 'GOV_WGI_GE.EST'].copy()
year_cols = [c for c in gov.columns if c.isdigit()]
gov_long = gov.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols,
    var_name='year',
    value_name='gov_effectiveness'
)
gov_long['year'] = gov_long['year'].astype(int)
gov_long = gov_long.rename(columns={'Country Name': 'country', 'Country Code': 'iso3'})
gov_long = gov_long[gov_long['year'].between(2000, 2023)].dropna(subset=['gov_effectiveness'])
print(f"Gov Effectiveness: {gov_long.shape}")

# ── Merge World Bank indicators ───────────────────────────────────────────────
wb = gdp_long.merge(
    gov_long[['iso3', 'year', 'gov_effectiveness']],
    on=['iso3', 'year'], how='left'
)
wb.to_csv('data/worldbank_indicators_2000_2023.csv', index=False)
print(f"World Bank merged: {wb.shape}")

# ── HDI ───────────────────────────────────────────────────────────────────────
# The UNDP file has one column per indicator per year (e.g. hdi_2022, hdi_2021, ...)
hdi_raw = pd.read_csv('data/hdi_raw.csv')
hdi_cols = [c for c in hdi_raw.columns if c.startswith('hdi_') and c[4:].isdigit()]
id_cols  = [c for c in ['country', 'iso3', 'region'] if c in hdi_raw.columns]
hdi_long = hdi_raw[id_cols + hdi_cols].melt(
    id_vars=id_cols,
    value_vars=hdi_cols,
    var_name='year_label',
    value_name='hdi'
)
hdi_long['year'] = hdi_long['year_label'].str.extract(r'(\d{4})').astype(int)
hdi_long = hdi_long[hdi_long['year'].between(2000, 2023)].dropna(subset=['hdi'])
hdi_long = hdi_long.drop(columns='year_label')
hdi_long.to_csv('data/hdi_2000_2023.csv', index=False)
print(f"HDI: {hdi_long.shape} | years {hdi_long['year'].min()}-{hdi_long['year'].max()}")
```

---

## 3. Folder Structure Before Running the Notebook

After the reshape step, your `data/` folder should look like this:

```
data/
├── cpi_2000_2023.csv                   ← produced by reshape (used by notebook)
├── worldbank_indicators_2000_2023.csv  ← produced by reshape (used by notebook)
├── hdi_2000_2023.csv                   ← produced by reshape (used by notebook)
│
├── cpi_wide.csv                        ← original download (keep as backup)
├── gdp_per_capita_raw.csv              ← original download (keep as backup)
├── gov_effectiveness_raw.csv           ← original download (keep as backup)
└── hdi_raw.csv                         ← original download (keep as backup)
```

The `data/` folder is in `.gitignore` — none of these files are pushed to GitHub.

---

## 4. Update the Notebook Loading Cells

The notebook loads `data/hdi_data_2000_2022.csv` by default. After the reshape above you have `data/hdi_2000_2023.csv` instead. Open `analysis.ipynb` and in the HDI loading cell change:

```python
# from:
hdi = pd.read_csv('data/hdi_data_2000_2022.csv')
# to:
hdi = pd.read_csv('data/hdi_2000_2023.csv')
```

---

## 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Run the Notebook

- Open `analysis.ipynb` in VS Code or Jupyter
- Run all cells top to bottom
- The final export cell writes `data/cpi_development_panel.csv` — this is the file you connect to in Tableau

---

## 7. Build the Dashboards in Tableau

- Open Tableau Desktop or Tableau Public
- Connect to `data/cpi_development_panel.csv`
- Follow the step-by-step instructions in `dashboards/TABLEAU_GUIDE.md`
