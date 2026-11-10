# Lost kingdoms on the high street

Wessex, Mercia, Elmet and Rheged in business names: where are the names of early medieval kingdoms used today? Every UK feature in OpenStreetMap named after one of twelve kingdoms (Wessex, Mercia, Northumbria, Elmet, Rheged, Deira, Bernicia, Lindsey, Strathclyde, Dalriada, Dumnonia, East Anglia), read and classified, compared with approximate extents of the kingdoms around AD 800 against a baseline of census residents. The analysis plan was written in NOTES.md before any feature was located against any extent. A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: https://maps.tristanhotham.com/lost-kingdoms/
Paper: https://doi.org/10.5281/zenodo.24104340
Blog post: https://blog.tristanhotham.com/2026/10/31/lost-kingdoms/
Code and data: https://github.com/Tristan-Hotham/lost-kingdoms

## Headline results

- 1,087 named features from 7,500 raw OpenStreetMap rows: 254 businesses and voluntary bodies, 93 public bodies, 336 streets, 62 named buildings and sites, 342 other (stops, routes, infrastructure, not the kingdom).
- Wessex: 75 of 95 businesses and voluntary bodies inside the main extent (79%), where 10.0% of UK residents live; rate ratio per resident 33.9 (95% CI 19.5 to 70.7), brand bootstrap.
- Mercia: 30 of 32 inside (25.6% of residents); rate ratio 43.6 (95% CI 15.1 to 200.6).
- Northumbria: all 33 inside (rate ratio at least 50), all in the North East region.
- Pooled (Wessex, Mercia, Northumbria; Poisson, name fixed effects, errors clustered by local authority): 44.0 (95% CI 19.5 to 99.7). All eleven kingdom names: 83.5 (34.1 to 204.6). Above 1 in all 19 planned checks (range 14.5 to 66.2).
- Placebo (wrong kingdoms' extents): 0.97 (0.51 to 1.83).
- Public bodies vs businesses: 89% vs 86% inside; odds ratio 0.87 (0.29 to 2.60), no detectable difference. Streets: only 52% inside.
- Small kingdoms (described, not tested): Elmet 10 of 10 inside (6 from Sherburn in Elmet, Barwick in Elmet or Elmete), Lindsey 9 of 10, Strathclyde 8 of 9, Rheged 2 of 2, Dalriada 2 of 5. East Anglia (also a modern region): 43 of 56 in Norfolk and Suffolk.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; every named feature coloured by kingdom (filled inside, ring outside), extents (heartland, around 800, widest) as toggles, filters by name and kind, search, full screen, popups with OpenStreetMap links. |
| `header.png` | Social card, 1200 x 630. |
| `data/osm_matches.csv` | Every matched OpenStreetMap object with its class, flags and whether it was decided by hand. |
| `data/features.csv`, `data/features_geo.csv` | Merged features with brand key, class, flags, areal unit, district, region, inside flags (core, main, wide) and distances. |
| `data/units.csv` | 7,307 areal units (MSOA, Scottish councils, NI districts) with residents, county, district, region and extent membership. |
| `data/extents.geojson`, `data/extents_web.geojson` | Approximate extents, three versions per kingdom. |
| `data/name_table.csv`, `data/robustness.csv` | Per-name results and every robustness check. |
| `data/results.json`, `data/site.json` | Every number quoted anywhere; page data. |
| `code/` | Scripts in order, templates, `overrides.csv` (hand decisions), `qa.js`. |
| `release/` | Paper (PDF, LaTeX, figures, `cover_note.md`), blog post and figures, Zenodo files. |
| `reddit/` | Collage, its script, the looping GIF and the post text. |
| `NOTES.md` | Working notes and the analysis plan, written before any location test. |

## Method in brief

- Names: whole-word matches of each kingdom (and adjective) in the OpenStreetMap name; every non-street match read by eye; duplicates within 250 m merged (streets 1 km); chains given a brand key.
- Classes: businesses and voluntary bodies (main sample), public bodies, streets, named buildings and sites, other. Names built on a street ("Wessex Road Surgery") excluded; Lindsey personal names and the Suffolk and Warwickshire Lindseys excluded; place-derived names (Sherburn in Elmet, Kirton in Lindsey, Strathclyde Park) flagged.
- Extents: unions of MSOAs (by county or 2021 district), Scottish council areas and NI districts, after Hill (1981) and Yorke (1990), in core, main and wide versions (paper, Table 4).
- Tests: rate ratio inside vs outside per resident, brand bootstrap CIs; pooled Poisson with name fixed effects and log-population offset, clustered by local authority; distance decay outside; logit of inside on public; placebo with other kingdoms' extents; the planned robustness checks (R1 to R10, with leave-one-region-out).

## How to rerun

Needs Python 3 with pandas, numpy, geopandas, shapely, statsmodels, matplotlib, Pillow; xelatex; node with Playwright for QA. Raw inputs are listed in `code/common.py`.

```
python3 code/01_features.py   # match, classify, merge
python3 code/02_geography.py  # areal units, populations, extents, locate features
python3 code/03_analysis.py   # all tests (results.json)
python3 code/04_site.py       # page data and descriptive extras
python3 code/05_figures.py    # figures and header
python3 code/06_build_site.py # index.html
python3 code/07_paper.py      # paper (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py
python3 code/09_readme.py     # README, LICENSE, Reddit post, cover note
python3 code/08_release.py    # blog post, Zenodo files
```

## Sources and licences

- OpenStreetMap contributors, via the QLever SPARQL engine (osm-planet), retrieved 2026. Open Database Licence 1.0; the derived feature files in `data/` are shared under ODbL 1.0.
- Census 2021 usual residents (ONS via Nomis; NISRA) and Scotland's Census 2022 (NRS), as compiled in Hotham (2026) *Faith on the map*, doi:10.5281/zenodo.23842991. ONS boundaries (MSOA 2021, LAD 2023, counties). Open Government Licence v3.0; contains OS data Crown copyright and database right.
- Kingdom extents: my approximations after D. Hill (1981) *An Atlas of Anglo-Saxon England* and B. Yorke (1990) *Kings and Kingdoms of Early Anglo-Saxon England*.
- Base map: OpenFreeMap Positron (OpenStreetMap contributors, ODbL). MapLibre GL JS (BSD 3-Clause).
- Text and figures CC BY 4.0; code MIT; data derived from OpenStreetMap ODbL 1.0.

## Citation

Hotham, T. (2026) Lost kingdoms on the high street: early medieval kingdom names in modern British business names. Zenodo. https://doi.org/10.5281/zenodo.24104340

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
