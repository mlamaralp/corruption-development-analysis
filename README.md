# Corruption and Economic Development Analysis

## Overview

This project investigates the relationship between corruption and economic development across countries from 2012 to 2022. Using the Corruption Perceptions Index (CPI) from Transparency International and development indicators from the World Bank — GDP per capita, government effectiveness and HDI — it explores how corruption shapes a country's economic trajectory and whether development reduces corruption over time.

This project was independently designed and developed by me, drawing inspiration from a group data visualisation project completed during my degree. The analytical structure follows the same methodology — two complementary datasets merged into a country-year panel, three analytical questions, and interactive Tableau dashboards — but the topic, datasets, research questions, code and conclusions are entirely my own original work.

Developed for the **Data Visualization** course at Nova School of Business and Economics.

## Research Questions

1. **Structural relationship** — How does corruption correlate with GDP per capita and human development, and which world regions show the strongest association between the two?
2. **Temporal evolution** — How have CPI scores and economic indicators changed between 2012 and 2022, and are there countries that broke the pattern by improving or deteriorating rapidly?
3. **Geographic patterns** — Which regions concentrate persistent corruption, and how have global hotspots shifted over time?

## Key Findings

- The relationship between corruption and GDP per capita is strong and non-linear: above roughly $20,000 GDP per capita (PPP), nearly all countries score above 50 on the CPI (less corrupt). Below that threshold, scores are widely dispersed, suggesting that economic development is necessary but not sufficient to reduce corruption.
- Sub-Saharan Africa and parts of South Asia show the weakest improvement over the study period despite economic growth, pointing to institutional inertia rather than a purely economic mechanism.
- Eastern Europe and Central Asia show the most variance: countries like Estonia and Georgia improved dramatically after 2004, while others stagnated suggesting that political will and EU accession pressure are stronger predictors of anti-corruption progress than income alone.
- The COVID-19 period (2020–2021) coincides with a measurable CPI decline in several middle-income countries, consistent with emergency procurement opacity and reduced institutional oversight during crises.
- Nordic countries (Denmark, Finland, Norway) have held the top CPI positions throughout the entire period with minimal variance, forming a stable benchmark. At the bottom, Somalia, South Sudan and Syria have shown no meaningful improvement despite international pressure.

## Datasets

| Dataset | Source | Coverage |
|---------|--------|----------|
| Corruption Perceptions Index (CPI) | Transparency International | 2012–2025, annual, country-level |
| GDP per capita (PPP, constant 2017 USD) | World Bank — World Development Indicators | 2000–2023, annual, country-level |
| Human Development Index (HDI) | UNDP Human Development Reports | 2012–2022, annual, country-level |
| Government Effectiveness Index | World Bank — Worldwide Governance Indicators | 2000–2023, annual, country-level |

All datasets are free to download:
- CPI: [transparency.org/en/cpi](https://www.transparency.org/en/cpi)
- World Bank GDP: [data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD)
- World Bank Gov. Effectiveness: [data.worldbank.org/indicator/GE.EST](https://data.worldbank.org/indicator/GE.EST)
- UNDP HDI: [hdr.undp.org/data-center/documentation-and-downloads](https://hdr.undp.org/data-center/documentation-and-downloads)

The analysis uses the overlap period: **2012–2022**.

## Repository Structure

```
corruption-development-analysis/
├── analysis.ipynb              # Main notebook: cleaning, merging, EDA, Tableau prep
├── requirements.txt            # Python dependencies
├── .gitignore
└── dashboards/
    └── TABLEAU_GUIDE.md        # Step-by-step instructions to build the 3 dashboards
```

> Data files go in a `data/` folder (excluded from Git — see `.gitignore`).

## Tableau Dashboards

| Dashboard | Research Question | Link |
|-----------|-------------------|------|
| Dashboard 1 — Structural Relationship | How does corruption correlate with development? | [View on Tableau Public](https://public.tableau.com/app/profile/margarida.amaral/viz/corruption-development-analysisbook1/Howdoescorruptionshapeeconomicdevelopment) |
| Dashboard 2 — Temporal Evolution | How has corruption evolved over time? | [View on Tableau Public](https://public.tableau.com/app/profile/margarida.amaral/viz/corruption-development-analysisbook2/Howhascorruptionevolvedovertime) |
| Dashboard 3 — Geographic Patterns | Where are the corruption hotspots? | [View on Tableau Public](https://public.tableau.com/app/profile/margarida.amaral/viz/corruption-development-analysisbook3/Wherearethecorruptionhotspotsandhowhavetheyshifted) |

## Tools Used

- **Python** (Pandas, NumPy, Matplotlib, Seaborn) for data cleaning, merging and EDA
- **Tableau** for interactive dashboards

## Visualisation Design Notes

These notes document deliberate design choices and known limitations in the dashboards.

**Dashboard 1 — Indicators Heatmap (Sheet 1D)**

The heatmap compares three development indicators (GDP per capita, Government Effectiveness, HDI) across CPI corruption categories. A known limitation of this view is that the three indicators operate on very different scales: GDP per capita ranges from roughly $1,000 to $70,000, Government Effectiveness from -2.5 to +2.5, and HDI from 0 to 1. A single shared colour scale would be dominated entirely by GDP and make the other two indicators invisible.

To address this, a per-row colour encoding is used, where the darkest colour within each row represents the highest value for that indicator. This allows meaningful within-indicator comparison across corruption categories while acknowledging that cross-indicator colour comparisons are not valid. The pattern that emerges — Very Clean countries consistently showing darker colours across all three rows, is robust regardless of this limitation.

**Scatter plots — Log GDP per capita**

GDP per capita is displayed on a log scale rather than a linear scale throughout the dashboards. This is a deliberate choice: the raw distribution of GDP is heavily right-skewed, with a small number of very high-income countries compressing all other variation into a narrow band. The log transformation linearises the relationship with CPI and makes the scatter plots far more readable without distorting the underlying pattern.

**Dashboard 2 — Country Trajectories (Sheet 2D)**

Nine countries were selected for the trajectory analysis, each representing a distinct analytical pattern:

- **Denmark and Finland** — consistently at the top of the CPI throughout the entire period, serving as a benchmark for what sustained clean governance looks like over time.
- **Somalia and Syria** — persistently at the bottom, cases of fragile states where corruption has not improved despite international pressure, illustrating that external intervention alone is insufficient.
- **Georgia and Estonia** — the two most striking anti-corruption reform success stories in the dataset. Estonia improved dramatically after EU accession in 2004; Georgia reformed rapidly after the 2003 Rose Revolution. Both show that fast, large-scale improvement is possible under the right political conditions.
- **Hungary and Turkey** — notable cases of deterioration in countries that were previously improving, demonstrating that anti-corruption progress is neither linear nor irreversible.
- **Rwanda** — a low-income country that scores significantly above its regional peers in Sub-Saharan Africa, breaking the expected income-corruption pattern and showing that institutional choices matter independently of GDP level.

Together these nine countries tell a complete analytical story: stability at the top, collapse at the bottom, reform as possibility, backsliding as risk, and geographic exceptions to the income-corruption rule.
