
# # Corruption and Economic Development Analysis
# 
# ## Dataset Choice and Analytical Motivation
# 
# The Corruption Perceptions Index (CPI), published annually by Transparency International, is one of the most widely used governance indicators in comparative political economy research. It aggregates expert assessments and surveys from multiple independent sources into a single country-level score (0 = highly corrupt, 100 = very clean), enabling consistent cross-country and over-time comparisons.
# 
# This dataset is analytically rich for several reasons:
# 
# - The CPI covers over 180 countries and spans more than two decades, providing both geographic breadth and temporal depth for trend analysis.
# - The relationship between corruption and GDP per capita is well-documented in the literature but non-linear: wealthier countries tend to score higher, yet there are notable outliers on both ends — resource-rich economies that remain highly corrupt despite high incomes (e.g. Russia, Equatorial Guinea) and lower-income countries that have achieved comparatively strong governance (e.g. Rwanda, Botswana). These exceptions are analytically interesting precisely because they do not fit the expected pattern and invite deeper investigation.
# - Pairing the CPI with the World Bank's Government Effectiveness Index and GDP per capita allows the analysis to disentangle two related but distinct phenomena: whether corruption is primarily a governance failure or an income-level effect.
# 
# ## Analytical Questions
# 
# 1. **Structural Relationship** — How does corruption correlate with GDP per capita and human development, and does the relationship differ across world regions?
# 2. **Temporal Evolution** — How have CPI scores and economic indicators changed between 2000 and 2022, and which countries broke the expected pattern by improving or deteriorating significantly?
# 3. **Geographic Patterns** — Which regions concentrate persistent corruption hotspots, and how have these spatial patterns shifted over the study period?
# 
# ## Objectives
# 
# - Load and explore the Corruption Perceptions Index (CPI) and World Bank development indicators
# - Harmonise country names across datasets and merge into a unified country-year panel
# - Create derived variables and hierarchies for Tableau
# - Export a curated dataset ready for dashboard development
# 


# Imports and display settings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

print("Libraries imported successfully.")



# ## 0. Data Preparation — Reshape Raw Files
# 
# This section converts the raw downloaded files into the long-format CSVs used throughout the notebook. **Run these cells once before anything else.** The files produced are saved to `data/` and are not pushed to GitHub.
# 
# File naming — place your downloads in the `data/` folder with these exact names:
# - `data/cpi_wide.csv` — CPI Timeseries sheet, saved as CSV (semicolon-separated)
# - `data/gdp_per_capita_raw.csv` — World Bank GDP per capita CSV
# - `data/gov_effectiveness_raw.csv` — WGICSV.csv renamed
# - `data/hdi_raw.csv` — UNDP HDI composite time series CSV
# 


import os
os.makedirs('data', exist_ok=True)

# ── CPI ───────────────────────────────────────────────────────────────────────
# The CPI timeseries CSV is semicolon-separated and has 2 header rows to skip
# Download: https://images.transparencycdn.org/images/CPI2025_Results.zip
# Open the Excel, go to sheet "CPI Timeseries 2012 - 2025", Save As CSV (semicolon)
cpi_raw = pd.read_csv('data/cpi_wide.csv', sep=';', skiprows=2)
# Row 0 of this read is the actual column header
cpi_raw.columns = cpi_raw.iloc[0]
cpi_raw = cpi_raw.drop(index=0).reset_index(drop=True)

# Keep CPI score columns (note: 2013/2012 use 'CPI Score', rest use 'CPI score')
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
cpi_long = cpi_long.sort_values(['country', 'year']).reset_index(drop=True)
cpi_long.to_csv('data/cpi_2000_2023.csv', index=False)
print(f"CPI: {cpi_long.shape[0]:,} rows | years {cpi_long['year'].min()}-{cpi_long['year'].max()} | countries {cpi_long['country'].nunique()}")

# ── GDP per capita ────────────────────────────────────────────────────────────
# Download: https://api.worldbank.org/v2/en/indicator/NY.GDP.PCAP.PP.KD?downloadformat=csv
# Use the API_NY.GDP.PCAP.PP.KD_...csv file from the zip (skiprows=4 skips WB metadata)
gdp_wide = pd.read_csv('data/gdp_per_capita_raw.csv', skiprows=4)
year_cols = [c for c in gdp_wide.columns if str(c).isdigit()]
gdp_long = gdp_wide.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols,
    var_name='year',
    value_name='gdp_per_capita_ppp'
)
gdp_long['year'] = gdp_long['year'].astype(int)
gdp_long = gdp_long.rename(columns={'Country Name': 'country', 'Country Code': 'iso3'})
gdp_long = gdp_long[gdp_long['year'].between(2000, 2025)].dropna(subset=['gdp_per_capita_ppp'])
print(f"GDP: {gdp_long.shape[0]:,} rows | years {gdp_long['year'].min()}-{gdp_long['year'].max()}")

# ── Government Effectiveness (WGI) ───────────────────────────────────────────
# Download: https://databank.worldbank.org/data/download/WGI_CSV.zip → use WGICSV.csv
# Indicator code is GOV_WGI_GE.EST
wgi = pd.read_csv('data/gov_effectiveness_raw.csv')
gov = wgi[wgi['Indicator Code'] == 'GOV_WGI_GE.EST'].copy()
year_cols = [c for c in gov.columns if str(c).isdigit()]
gov_long = gov.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols,
    var_name='year',
    value_name='gov_effectiveness'
)
gov_long['year'] = gov_long['year'].astype(int)
gov_long = gov_long.rename(columns={'Country Name': 'country', 'Country Code': 'iso3'})
gov_long = gov_long[gov_long['year'].between(2000, 2025)].dropna(subset=['gov_effectiveness'])
print(f"Gov Effectiveness: {gov_long.shape[0]:,} rows | years {gov_long['year'].min()}-{gov_long['year'].max()}")

# ── Merge GDP + Gov Effectiveness → single World Bank file ───────────────────
wb_prep = gdp_long.merge(
    gov_long[['iso3', 'year', 'gov_effectiveness']],
    on=['iso3', 'year'], how='left'
)
wb_prep.to_csv('data/worldbank_indicators_2000_2023.csv', index=False)
print(f"World Bank merged: {wb_prep.shape[0]:,} rows → data/worldbank_indicators_2000_2023.csv")

# ── HDI ───────────────────────────────────────────────────────────────────────
# Download: https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv
# Columns: iso3, country, region, hdi_1990, hdi_1991, ..., hdi_2022
hdi_raw = pd.read_csv('data/hdi_raw.csv', encoding='latin-1')
hdi_cols = [c for c in hdi_raw.columns if c.startswith('hdi_') and c[4:].isdigit()]
id_cols  = [c for c in ['iso3', 'country', 'region'] if c in hdi_raw.columns]
hdi_long = hdi_raw[id_cols + hdi_cols].melt(
    id_vars=id_cols,
    value_vars=hdi_cols,
    var_name='year_label',
    value_name='hdi'
)
hdi_long['year'] = hdi_long['year_label'].str.extract(r'(\d{4})').astype(int)
hdi_long = hdi_long.drop(columns='year_label')
hdi_long = hdi_long[hdi_long['year'].between(2000, 2025)].dropna(subset=['hdi'])
hdi_long.to_csv('data/hdi_2000_2023.csv', index=False)
print(f"HDI: {hdi_long.shape[0]:,} rows | years {hdi_long['year'].min()}-{hdi_long['year'].max()}")

print("\nAll files ready. Continue with the rest of the notebook.")



# ## 1. Load and Explore the CPI Dataset


# Load the CPI dataset
# Source: Transparency International — https://www.transparency.org/en/cpi
# Download: CPI full data series (Excel or CSV), reshape to long format before loading
# Expected columns: country, iso3, region, year, cpi_score, cpi_rank, cpi_sources
print("Loading CPI dataset...")
cpi = pd.read_csv('data/cpi_2000_2023.csv')
print(f"CPI dataset loaded: {cpi.shape[0]:,} rows, {cpi.shape[1]} columns")
print(f"\nFirst rows:")
print(cpi.head(10))



# Dataset overview
print("=" * 70)
print("CPI DATASET OVERVIEW")
print("=" * 70)
print(f"\nShape: {cpi.shape[0]:,} rows x {cpi.shape[1]} columns")
print(f"Year range: {cpi['year'].min()} - {cpi['year'].max()}")
print(f"Unique countries: {cpi['country'].nunique()}")
print(f"Unique regions: {cpi['region'].nunique()}")
print(f"\nColumn names:")
for col in cpi.columns:
    print(f"  - {col}")



# Missing values and data types
print("=" * 70)
print("DATA QUALITY CHECK — CPI")
print("=" * 70)
missing = pd.DataFrame({
    'Column': cpi.columns,
    'Data_Type': cpi.dtypes,
    'Null_Count': cpi.isnull().sum(),
    'Null_Pct': (cpi.isnull().sum() / len(cpi) * 100).round(2)
}).sort_values('Null_Pct', ascending=False)
print(missing.to_string(index=False))



# CPI score distribution
# Score: 0 = highly corrupt, 100 = very clean
print("=" * 70)
print("CPI SCORE STATISTICS")
print("=" * 70)
print(f"\nGlobal CPI score (all years):")
print(cpi['cpi_score'].describe().round(2))

print(f"\nAverage CPI score by region:")
regional = cpi.groupby('region')['cpi_score'].agg(['mean', 'min', 'max', 'std']).round(2)
regional = regional.sort_values('mean', ascending=False)
print(regional)

print(f"\nTop 10 cleanest countries (average CPI score):")
top_clean = cpi.groupby('country')['cpi_score'].mean().sort_values(ascending=False).head(10)
print(top_clean.round(2))

print(f"\nTop 10 most corrupt countries (average CPI score):")
top_corrupt = cpi.groupby('country')['cpi_score'].mean().sort_values(ascending=True).head(10)
print(top_corrupt.round(2))



# Temporal coverage check
print("=" * 70)
print("TEMPORAL COVERAGE — CPI")
print("=" * 70)
yearly_obs = cpi.groupby('year')['country'].count()
print(f"\nCountries per year:")
print(yearly_obs.to_string())
# Note: CPI only covered ~90 countries in early 2000s; expanded to ~180 by 2012



# ## 2. Load and Explore the World Bank Development Indicators


# Load World Bank indicators — GDP per capita and Government Effectiveness
# Source: World Bank World Development Indicators (GDP) and Worldwide Governance Indicators (WGI)
# Both files were downloaded and reshaped to long format via SETUP.md before loading here
# Expected columns: country, iso3, year, gdp_per_capita_ppp, gov_effectiveness
print("Loading World Bank dataset...")
wb = pd.read_csv('data/worldbank_indicators_2000_2023.csv')
print(f"World Bank dataset loaded: {wb.shape[0]:,} rows, {wb.shape[1]} columns")
print(f"\nFirst rows:")
print(wb.head(10))



# World Bank dataset overview
print("=" * 70)
print("WORLD BANK DATASET OVERVIEW")
print("=" * 70)
print(f"Year range: {wb['year'].min()} - {wb['year'].max()}")
print(f"Unique countries: {wb['country'].nunique()}")
print(f"\nKey indicators — statistics:")
# Note: HDI is loaded separately from UNDP and merged in Section 4
key_indicators = ['gdp_per_capita_ppp', 'gov_effectiveness']
for col in key_indicators:
    if col in wb.columns:
        print(f"\n{col}:")
        print(wb[col].describe().round(2))



# Missing values
print("=" * 70)
print("DATA QUALITY CHECK — WORLD BANK")
print("=" * 70)
missing_wb = pd.DataFrame({
    'Column': wb.columns,
    'Null_Count': wb.isnull().sum(),
    'Null_Pct': (wb.isnull().sum() / len(wb) * 100).round(2)
}).sort_values('Null_Pct', ascending=False)
print(missing_wb.to_string(index=False))



# ## 3. Country Name Harmonisation


# Compare country names across both datasets to identify mismatches
cpi_countries = set(cpi['country'].dropna().unique())
wb_countries  = set(wb['country'].dropna().unique())

print(f"CPI unique countries: {len(cpi_countries)}")
print(f"World Bank unique countries: {len(wb_countries)}")
print(f"Direct matches: {len(cpi_countries & wb_countries)}")

in_cpi_not_wb = sorted(cpi_countries - wb_countries)
in_wb_not_cpi = sorted(wb_countries - cpi_countries)

print(f"\nIn CPI but not World Bank ({len(in_cpi_not_wb)}):")
print(in_cpi_not_wb)
print(f"\nIn World Bank but not CPI ({len(in_wb_not_cpi)}):")
print(in_wb_not_cpi)



# Manual mapping dictionary — adjust based on the actual mismatches printed above
# Keys = CPI names, Values = World Bank names
country_mapping = {
    'Bosnia and Herzegovina':               'Bosnia & Herzegovina',
    'Congo':                                'Congo, Rep.',
    'Democratic Republic of the Congo':     'Congo, Dem. Rep.',
    'Czechia':                              'Czech Republic',
    'Egypt':                                'Egypt, Arab Rep.',
    'Gambia':                               'Gambia, The',
    'Iran':                                 'Iran, Islamic Rep.',
    'Ivory Coast':                          "Cote d'Ivoire",
    'Kyrgyzstan':                           'Kyrgyz Republic',
    'Laos':                                 'Lao PDR',
    'North Macedonia':                      'Macedonia, FYR',
    'Palestine':                            'West Bank and Gaza',
    'Russia':                               'Russian Federation',
    'Saint Kitts and Nevis':               'St. Kitts and Nevis',
    'Saint Lucia':                          'St. Lucia',
    'Saint Vincent and the Grenadines':    'St. Vincent and the Grenadines',
    'Slovakia':                             'Slovak Republic',
    'South Korea':                          'Korea, Rep.',
    'Syria':                                'Syrian Arab Republic',
    'Tanzania':                             'Tanzania',
    'Trinidad and Tobago':                  'Trinidad & Tobago',
    'United States':                        'United States',
    'Venezuela':                            'Venezuela, RB',
    'Vietnam':                              'Viet Nam',
    'Yemen':                                'Yemen, Rep.',
}

# Apply mapping to CPI
cpi['country_harmonised'] = cpi['country'].replace(country_mapping)
wb['country_harmonised']  = wb['country'].copy()  # WB names are the reference

# Verify coverage after mapping
cpi_h = set(cpi['country_harmonised'].unique())
wb_h  = set(wb['country_harmonised'].unique())
print(f"Coverage after mapping:")
print(f"  Direct matches: {len(cpi_h & wb_h)}")
print(f"  Remaining unmatched in CPI: {len(cpi_h - wb_h)}")
print(f"  Unmatched countries: {sorted(cpi_h - wb_h)}")



# ## 4. Merge Datasets


# Load HDI dataset (produced by SETUP.md reshape step)
# Source: UNDP Human Development Reports
# Expected columns: iso3, country, year, hdi
print("Loading HDI dataset...")
hdi = pd.read_csv('data/hdi_2000_2023.csv')
print(f"HDI dataset loaded: {hdi.shape[0]:,} rows")
print(f"Year range: {hdi['year'].min()} - {hdi['year'].max()}")
print(f"Unique countries: {hdi['country'].nunique()}")
print(f"\nHDI score statistics:")
print(hdi['hdi'].describe().round(3))



# Merge CPI + World Bank + HDI into a single country-year panel
# Step 1: filter to study period
cpi_filtered = cpi[cpi['year'].between(2000, 2022)].copy()
wb_filtered  = wb[wb['year'].between(2000, 2022)].copy()
hdi_filtered = hdi[hdi['year'].between(2000, 2022)].copy()

# Step 2: merge CPI with World Bank (GDP + Gov Effectiveness)
merged = cpi_filtered.merge(
    wb_filtered[['country_harmonised', 'year', 'gdp_per_capita_ppp', 'gov_effectiveness']],
    on=['country_harmonised', 'year'],
    how='left',
    indicator=True
)
wb_match = (merged['_merge'] == 'both').sum()
merged = merged.drop(columns=['_merge'])

# Step 3: merge in HDI via ISO3 code (more reliable than country name)
# HDI file uses iso3 + year as key
if 'iso3' in merged.columns and 'iso3' in hdi_filtered.columns:
    merged = merged.merge(
        hdi_filtered[['iso3', 'year', 'hdi']],
        on=['iso3', 'year'],
        how='left'
    )
else:
    # Fallback: merge on harmonised country name
    merged = merged.merge(
        hdi_filtered[['country', 'year', 'hdi']].rename(columns={'country': 'country_harmonised'}),
        on=['country_harmonised', 'year'],
        how='left'
    )

print("Merge results:")
print(f"  Total records: {len(merged):,}")
print(f"  Matched with World Bank: {wb_match:,} ({wb_match/len(merged)*100:.1f}%)")
print(f"  Records with HDI: {merged['hdi'].notna().sum():,} ({merged['hdi'].notna().sum()/len(merged)*100:.1f}%)")
print(f"\nFinal merged shape: {merged.shape}")
print(f"\nSample:")
print(merged[['country_harmonised', 'year', 'cpi_score', 'gdp_per_capita_ppp', 'gov_effectiveness', 'hdi']].head(10))



# ## 5. Derived Variables and Hierarchies


# Log GDP per capita — GDP is heavily right-skewed; log scale linearises the relationship
merged['log_gdp_per_capita'] = np.log10(merged['gdp_per_capita_ppp'].replace(0, np.nan)).round(4)

# CPI change year-on-year within each country
merged = merged.sort_values(['country_harmonised', 'year'])
merged['cpi_change_yoy'] = merged.groupby('country_harmonised')['cpi_score'].diff().round(2)

# Cumulative CPI change from first available year per country
merged['cpi_change_cumulative'] = merged.groupby('country_harmonised')['cpi_score'].transform(
    lambda x: x - x.iloc[0]
).round(2)

# CPI category (quintile-based across all country-years)
merged['cpi_category'] = pd.cut(
    merged['cpi_score'],
    bins=[0, 29, 44, 59, 74, 100],
    labels=['Highly Corrupt (0-29)', 'Corrupt (30-44)',
            'Moderate (45-59)', 'Fairly Clean (60-74)', 'Very Clean (75-100)'],
    include_lowest=True
)

# Flag: broad-coverage years (CPI covered >150 countries from 2012 onwards)
merged['broad_coverage'] = merged['year'] >= 2012

print("Derived variables added:")
print(merged[['country_harmonised', 'year', 'cpi_score', 'log_gdp_per_capita',
              'cpi_change_yoy', 'cpi_change_cumulative', 'cpi_category']].head(12))



# Geographic hierarchy for Tableau drill-down: Region > Country
merged['geo_level1'] = merged['region']
merged['geo_level2'] = merged['country_harmonised']

# ISO3 code for map joins in Tableau (requires iso3 column from CPI source)
if 'iso3' in merged.columns:
    merged['geo_code'] = merged['iso3']

# Temporal hierarchy: Decade > Year
merged['decade'] = (merged['year'] // 10 * 10).astype(str) + 's'
merged['temporal_level1'] = merged['decade']
merged['temporal_level2'] = merged['year'].astype(str)

# HDI category
if 'hdi' in merged.columns:
    merged['hdi_category'] = pd.cut(
        merged['hdi'],
        bins=[0, 0.549, 0.699, 0.799, 1.0],
        labels=['Low', 'Medium', 'High', 'Very High'],
        include_lowest=True
    )

print("Hierarchies created.")
print(merged[['geo_level1', 'geo_level2',
              'temporal_level1', 'temporal_level2',
              'cpi_category']].head(10))



# ## 6. Data Quality Checks


# Missing values in key columns
print("=" * 70)
print("MISSING VALUES IN MERGED DATASET")
print("=" * 70)
key_cols = ['cpi_score', 'gdp_per_capita_ppp', 'log_gdp_per_capita',
            'gov_effectiveness', 'hdi', 'cpi_change_yoy']
for col in key_cols:
    if col in merged.columns:
        n = merged[col].isnull().sum()
        pct = n / len(merged) * 100
        print(f"  {col:<35} {n:>5} missing ({pct:.1f}%)")



# Duplicate country-year check
dupes = merged.duplicated(subset=['country_harmonised', 'year'], keep=False)
print(f"Duplicate country-year pairs: {dupes.sum()}")
if dupes.sum() > 0:
    print(merged[dupes][['country_harmonised', 'year', 'cpi_score']].head(10))

# Value range checks
print(f"\nCPI range: {merged['cpi_score'].min():.1f} - {merged['cpi_score'].max():.1f}  (expected 0-100)")
if 'hdi' in merged.columns:
    print(f"HDI range: {merged['hdi'].min():.3f} - {merged['hdi'].max():.3f}  (expected 0-1)")
print(f"GDP per capita range: ${merged['gdp_per_capita_ppp'].min():,.0f} - ${merged['gdp_per_capita_ppp'].max():,.0f}")



# ## 7. Exploratory Data Analysis


# ### 7.1 Tabular EDA


# Regional summary
print("=" * 70)
print("REGIONAL SUMMARY (averaged across all years)")
print("=" * 70)
regional = merged.groupby('region').agg(
    avg_cpi=('cpi_score', 'mean'),
    avg_gdp=('gdp_per_capita_ppp', 'mean'),
    avg_hdi=('hdi', 'mean'),
    n_countries=('country_harmonised', 'nunique'),
    n_obs=('cpi_score', 'count')
).round(2).sort_values('avg_cpi', ascending=False)
print(regional.to_string())

print("\n" + "=" * 70)
print("TOP 10 LEAST CORRUPT (highest average CPI)")
print("=" * 70)
country_avg = merged.groupby(['country_harmonised', 'region']).agg(
    avg_cpi=('cpi_score', 'mean'),
    avg_gdp=('gdp_per_capita_ppp', 'mean')
).round(2).sort_values('avg_cpi', ascending=False)
print(country_avg.head(10).to_string())

print("\n" + "=" * 70)
print("TOP 10 MOST CORRUPT (lowest average CPI)")
print("=" * 70)
print(country_avg.tail(10).to_string())



# Global yearly averages
print("=" * 70)
print("GLOBAL YEARLY TRENDS")
print("=" * 70)
yearly = merged.groupby('year').agg(
    avg_cpi=('cpi_score', 'mean'),
    avg_gdp=('gdp_per_capita_ppp', 'mean'),
    n_countries=('country_harmonised', 'nunique')
).round(2)
print(yearly.to_string())

if 2000 in yearly.index and 2022 in yearly.index:
    cpi_delta = yearly.loc[2022, 'avg_cpi'] - yearly.loc[2000, 'avg_cpi']
    gdp_delta = yearly.loc[2022, 'avg_gdp'] - yearly.loc[2000, 'avg_gdp']
    print(f"\nChange 2000 to 2022:")
    print(f"  CPI: {yearly.loc[2000,'avg_cpi']:.1f} -> {yearly.loc[2022,'avg_cpi']:.1f}  ({cpi_delta:+.1f} points)")
    print(f"  GDP/capita: ${yearly.loc[2000,'avg_gdp']:,.0f} -> ${yearly.loc[2022,'avg_gdp']:,.0f}  ({gdp_delta:+,.0f} USD)")



# Correlations between CPI and development indicators
print("=" * 70)
print("CORRELATIONS WITH CPI SCORE")
print("=" * 70)
corr_cols = ['gdp_per_capita_ppp', 'log_gdp_per_capita', 'gov_effectiveness', 'hdi']
corr_cols = [c for c in corr_cols if c in merged.columns]
corr = merged[corr_cols + ['cpi_score']].corr()['cpi_score'].drop('cpi_score').sort_values(ascending=False)
print(corr.round(3))

print("\nCorrelation matrix — all key variables:")
print(merged[corr_cols + ['cpi_score']].corr().round(3).to_string())



# Countries with biggest CPI improvement and deterioration
cpi_2000 = merged[merged['year'] == 2000][['country_harmonised', 'region', 'cpi_score']].rename(
    columns={'cpi_score': 'cpi_2000'})
cpi_2022 = merged[merged['year'] == 2022][['country_harmonised', 'cpi_score']].rename(
    columns={'cpi_score': 'cpi_2022'})
cpi_change = cpi_2000.merge(cpi_2022, on='country_harmonised', how='inner')
cpi_change['change'] = (cpi_change['cpi_2022'] - cpi_change['cpi_2000']).round(1)

print("Top 10 biggest CPI improvements (2000-2022):")
print(cpi_change.sort_values('change', ascending=False).head(10).to_string(index=False))

print("\nTop 10 biggest CPI deteriorations (2000-2022):")
print(cpi_change.sort_values('change', ascending=True).head(10).to_string(index=False))



# ### 7.2 Visual EDA


# Visual settings
sns.set_theme(style="whitegrid", rc={"figure.figsize": (11, 6)})



# #### AQ1 — Corruption vs Development Structure


# Scatter: CPI vs log GDP per capita coloured by region (country averages)
country_avg = merged.groupby(['country_harmonised', 'region']).agg(
    avg_cpi=('cpi_score', 'mean'),
    avg_log_gdp=('log_gdp_per_capita', 'mean'),
    avg_gdp=('gdp_per_capita_ppp', 'mean')
).reset_index()

plt.figure(figsize=(12, 7))
sns.scatterplot(data=country_avg, x='avg_log_gdp', y='avg_cpi',
                hue='region', alpha=0.8, s=60)
sns.regplot(data=country_avg, x='avg_log_gdp', y='avg_cpi',
            scatter=False, color='black', line_kws={'linewidth': 1.5, 'linestyle': '--'})

# Label notable outliers
outliers = country_avg[
    (country_avg['avg_cpi'] > 80) |
    (country_avg['avg_cpi'] < 15) |
    ((country_avg['avg_log_gdp'] > 4.2) & (country_avg['avg_cpi'] < 40))
]
for _, row in outliers.iterrows():
    plt.annotate(row['country_harmonised'],
                 (row['avg_log_gdp'], row['avg_cpi']),
                 fontsize=7, alpha=0.8,
                 xytext=(4, 0), textcoords='offset points')

plt.title("CPI Score vs GDP per Capita (log scale) — Country Averages 2000-2022")
plt.xlabel("Log10 GDP per Capita (PPP, constant 2017 USD)")
plt.ylabel("Corruption Perceptions Index (higher = less corrupt)")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()



# Bar chart: average CPI by region with GDP overlay
regional_avg = merged.groupby('region').agg(
    avg_cpi=('cpi_score', 'mean'),
    avg_gdp=('gdp_per_capita_ppp', 'mean')
).sort_values('avg_cpi', ascending=False).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 6))
bars = ax1.bar(regional_avg['region'], regional_avg['avg_cpi'],
               color='steelblue', alpha=0.8, label='Avg CPI Score')
ax1.set_ylabel("Average CPI Score", color='steelblue')
ax1.set_ylim(0, 100)
ax1.tick_params(axis='x', rotation=35)

ax2 = ax1.twinx()
ax2.plot(regional_avg['region'], regional_avg['avg_gdp'],
         color='crimson', marker='o', linewidth=2, label='Avg GDP/capita')
ax2.set_ylabel("Average GDP per Capita (PPP USD)", color='crimson')

plt.title("Average CPI Score and GDP per Capita by Region (2000-2022)")
fig.tight_layout()
plt.show()



# CPI vs Government Effectiveness Index
if 'gov_effectiveness' in merged.columns:
    gov_avg = merged.dropna(subset=['gov_effectiveness']).groupby(
        ['country_harmonised', 'region']).agg(
        avg_cpi=('cpi_score', 'mean'),
        avg_gov=('gov_effectiveness', 'mean')
    ).reset_index()

    plt.figure(figsize=(11, 6))
    sns.scatterplot(data=gov_avg, x='avg_gov', y='avg_cpi', hue='region', alpha=0.75)
    sns.regplot(data=gov_avg, x='avg_gov', y='avg_cpi',
                scatter=False, color='black', line_kws={'linewidth': 1.2})
    plt.title("CPI Score vs Government Effectiveness Index")
    plt.xlabel("Government Effectiveness (World Bank, higher = more effective)")
    plt.ylabel("CPI Score (higher = less corrupt)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
    plt.tight_layout()
    plt.show()



# #### AQ2 — Temporal Evolution


# Global average CPI over time with 3-year moving average
yearly_cpi = merged.groupby('year')['cpi_score'].mean()

plt.figure(figsize=(12, 5))
plt.plot(yearly_cpi.index, yearly_cpi.values,
         linewidth=1.5, label='Annual average CPI', color='steelblue')
plt.plot(yearly_cpi.index, yearly_cpi.rolling(3).mean().values,
         linewidth=2.2, linestyle='--', label='3-year moving average', color='navy')
plt.axvspan(2020, 2021, alpha=0.1, color='red', label='COVID-19 period')
plt.title("Global Average CPI Score Over Time (2000-2022)")
plt.xlabel("Year")
plt.ylabel("CPI Score (higher = less corrupt)")
plt.legend()
plt.tight_layout()
plt.show()



# CPI evolution by region
region_year = merged.groupby(['region', 'year'])['cpi_score'].mean().reset_index()

plt.figure(figsize=(13, 6))
for region in sorted(region_year['region'].unique()):
    subset = region_year[region_year['region'] == region]
    plt.plot(subset['year'], subset['cpi_score'], label=region, linewidth=1.8)

plt.title("CPI Score Evolution by Region (2000-2022)")
plt.xlabel("Year")
plt.ylabel("Average CPI Score")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()



# Dual-axis: global average CPI (left) and global average GDP per capita (right)
yearly_gdp = merged.groupby('year')['gdp_per_capita_ppp'].mean()

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(yearly_cpi.index, yearly_cpi.values,
         color='steelblue', linewidth=2, label='CPI Score')
ax1.set_ylabel("CPI Score (higher = less corrupt)", color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

ax2 = ax1.twinx()
ax2.plot(yearly_gdp.index, yearly_gdp.values,
         color='darkorange', linewidth=2, linestyle='--', label='GDP per capita')
ax2.set_ylabel("Average GDP per Capita (PPP USD)", color='darkorange')
ax2.tick_params(axis='y', labelcolor='darkorange')

plt.title("Global CPI and GDP per Capita Over Time (2000-2022)")
fig.tight_layout()
plt.show()



# CPI trajectory for notable individual countries
highlight_countries = [
    'Denmark', 'Finland',         # Consistently clean
    'Somalia', 'Syria',           # Consistently corrupt
    'Georgia', 'Estonia',         # Strong improvers
    'Hungary', 'Turkey',          # Notable decliners
    'Rwanda',                     # Regional outlier — Africa
]
highlight_countries = [c for c in highlight_countries if c in merged['country_harmonised'].values]

country_year = merged[merged['country_harmonised'].isin(highlight_countries)]

plt.figure(figsize=(13, 6))
for country in highlight_countries:
    subset = country_year[country_year['country_harmonised'] == country]
    plt.plot(subset['year'], subset['cpi_score'], label=country, linewidth=1.8, marker='o', markersize=3)

plt.title("CPI Trajectories — Selected Countries (2000-2022)")
plt.xlabel("Year")
plt.ylabel("CPI Score")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
plt.tight_layout()
plt.show()



# #### AQ3 — Geographic Patterns


# Heatmap: average CPI by region and year
pivot = merged.groupby(['region', 'year'])['cpi_score'].mean().reset_index()
pivot_table = pivot.pivot(index='region', columns='year', values='cpi_score').round(1)

plt.figure(figsize=(17, 6))
sns.heatmap(pivot_table, cmap='RdYlGn', annot=False,
            linewidths=0.3, vmin=20, vmax=80)
plt.title("Average CPI Score by Region and Year (green = less corrupt, red = more corrupt)")
plt.xlabel("Year")
plt.ylabel("Region")
plt.tight_layout()
plt.show()



# CPI category distribution over time — stacked area chart
cat_year = merged.groupby(['year', 'cpi_category'])['country_harmonised'].count().unstack(fill_value=0)

cat_year.plot(kind='area', stacked=True, figsize=(13, 6),
              colormap='RdYlGn', alpha=0.8)
plt.title("Distribution of Countries by CPI Category Over Time")
plt.xlabel("Year")
plt.ylabel("Number of Countries")
plt.legend(title="CPI Category", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()



# ## 8. Export Curated Dataset for Tableau


# Select final columns for Tableau
final_cols = [
    # Identifiers
    'country_harmonised', 'country', 'year',
    # Geography
    'region', 'geo_level1', 'geo_level2',
    # ISO code for map joins
    'iso3',
    # Temporal hierarchy
    'temporal_level1', 'temporal_level2', 'decade',
    # Core indicators
    'cpi_score', 'cpi_rank', 'cpi_category',
    'cpi_change_yoy', 'cpi_change_cumulative',
    # Development indicators
    'gdp_per_capita_ppp', 'log_gdp_per_capita',
    'gov_effectiveness', 'hdi', 'hdi_category',
    # Coverage flag
    'broad_coverage',
]

final_cols = [c for c in final_cols if c in merged.columns]
export_df = merged[final_cols].copy()

print(f"Export dataset: {export_df.shape[0]:,} rows, {export_df.shape[1]} columns")
print(f"Year range: {export_df['year'].min()} - {export_df['year'].max()}")
print(f"Countries: {export_df['country_harmonised'].nunique()}")
print(f"\nColumn list:")
for col in export_df.columns:
    print(f"  - {col}")

export_df.to_csv('data/cpi_development_panel.csv', index=False, encoding='utf-8')
print("\nExported to: data/cpi_development_panel.csv")



# Final dataset summary
print("=" * 70)
print("FINAL DATASET SUMMARY")
print("=" * 70)
print(f"\nRecords: {len(export_df):,}")
print(f"Countries: {export_df['country_harmonised'].nunique()}")
print(f"Regions: {export_df['region'].nunique()}")
print(f"Years covered: {export_df['year'].min()} - {export_df['year'].max()}")
print(f"\nCPI Score:")
print(export_df['cpi_score'].describe().round(2))
print(f"\nGDP per Capita (PPP):")
print(export_df['gdp_per_capita_ppp'].describe().round(0))
print(f"\nCPI Category distribution:")
print(export_df['cpi_category'].value_counts().sort_index())
print("\nExport complete. Ready for Tableau.")



# ## 9. Summary and Next Steps
# 
# ### Dataset Produced
# 
# - **cpi_development_panel.csv** — Country-year panel (2000-2022) combining CPI scores with GDP per capita, government effectiveness and HDI, plus derived variables and hierarchies. Ready for Tableau.
# 
# ### Key Variables for Each Dashboard
# 
# - **Dashboard 1 (AQ1):** `cpi_score` vs `log_gdp_per_capita` scatter, `cpi_score` vs `gov_effectiveness` scatter, bar chart by `region`, heatmap of indicators by `cpi_category`.
# - **Dashboard 2 (AQ2):** Line charts of `cpi_score` over `year` by `region` and for individual countries. Dual-axis with `gdp_per_capita_ppp`. `cpi_change_cumulative` for identifying the biggest movers.
# - **Dashboard 3 (AQ3):** Choropleth map coloured by `cpi_score` using `iso3` for joins. Scatter `cpi_score` vs `log_gdp_per_capita` with `year` page slider. Stacked area of `cpi_category` distribution.
# 
# ### Suggested Next Steps
# 
# - Incorporate press freedom index (RSF) as an additional predictor — journalist safety and corruption tend to co-vary strongly.
# - Test whether improvements in `gov_effectiveness` Granger-cause CPI improvements with a 3-5 year lag.
# - Separate analysis for resource-rich countries (oil exporters) where the GDP-corruption correlation often breaks down.
# 
