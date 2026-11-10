"""Step 9: README.md, LICENSE, reddit/post.md and release/paper/cover_note.md from data/results.json.
10.5281/zenodo.24104340, https://doi.org/10.5281/zenodo.24104340 and https://blog.tristanhotham.com/2026/10/31/lost-kingdoms/ are left for the publisher to fill."""
from common import *

R = jload(f"{DATA}/results.json")
N, H1, F = R["names"], R["H1"], R["flow"]
W, M, NO = N["Wessex"]["private"], N["Mercia"]["private"], N["Northumbria"]["private"]
rr = lambda p: f"{p['rr']:.1f} (95% CI {p['rr_lo']:.1f} to {p['rr_hi']:.1f})"
readme = f"""# Lost kingdoms on the high street

Wessex, Mercia, Elmet and Rheged in business names: where are the names of early medieval kingdoms used today? Every UK feature in OpenStreetMap named after one of twelve kingdoms (Wessex, Mercia, Northumbria, Elmet, Rheged, Deira, Bernicia, Lindsey, Strathclyde, Dalriada, Dumnonia, East Anglia), read and classified, compared with approximate extents of the kingdoms around AD 800 against a baseline of census residents. The analysis plan was written in NOTES.md before any feature was located against any extent. A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: https://maps.tristanhotham.com/{SLUG}/
Paper: {{https://doi.org/10.5281/zenodo.24104340}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/lost-kingdoms/}}
Code and data: {REPO}

## Headline results

- {F['features']:,} named features from {F['raw_rows']:,} raw OpenStreetMap rows: {F['private']} businesses and voluntary bodies, {F['public']} public bodies, {F['street']} streets, {F['site']} named buildings and sites, {F['other']} other (stops, routes, infrastructure, not the kingdom).
- Wessex: {W['n_in']} of {W['n']} businesses and voluntary bodies inside the main extent ({W['share_in']:.0f}%), where {W['base_share']:.1f}% of UK residents live; rate ratio per resident {rr(W)}, brand bootstrap.
- Mercia: {M['n_in']} of {M['n']} inside ({M['base_share']:.1f}% of residents); rate ratio {rr(M)}.
- Northumbria: all {NO['n']} inside (rate ratio at least {NO['rr_lo']:.0f}), all in the North East region.
- Pooled (Wessex, Mercia, Northumbria; Poisson, name fixed effects, errors clustered by local authority): {H1['pooled']['irr']:.1f} (95% CI {H1['pooled']['lo']:.1f} to {H1['pooled']['hi']:.1f}). All eleven kingdom names: {H1['pooled_all']['irr']:.1f} ({H1['pooled_all']['lo']:.1f} to {H1['pooled_all']['hi']:.1f}). Above 1 in all {R['robust_range']['n_checks']} planned checks (range {R['robust_range']['pt_min']:.1f} to {R['robust_range']['pt_max']:.1f}).
- Placebo (wrong kingdoms' extents): {R['P1']['irr']:.2f} ({R['P1']['lo']:.2f} to {R['P1']['hi']:.2f}).
- Public bodies vs businesses: {R['H3']['share_public']:.0f}% vs {R['H3']['share_private']:.0f}% inside; odds ratio {R['H3']['or']:.2f} ({R['H3']['or_lo']:.2f} to {R['H3']['or_hi']:.2f}), no detectable difference. Streets: only {R['streets']['share_in']:.0f}% inside.
- Small kingdoms (described, not tested): Elmet {N['Elmet']['private']['n_in']} of {N['Elmet']['private']['n']} inside ({R['place_derived_by_name']['Elmet']} from Sherburn in Elmet, Barwick in Elmet or Elmete), Lindsey {N['Lindsey']['private']['n_in']} of {N['Lindsey']['private']['n']}, Strathclyde {N['Strathclyde']['private']['n_in']} of {N['Strathclyde']['private']['n']}, Rheged {N['Rheged']['private']['n_in']} of {N['Rheged']['private']['n']}, Dalriada {N['Dalriada']['private']['n_in']} of {N['Dalriada']['private']['n']}. East Anglia (also a modern region): {N['East Anglia']['private']['n_in']} of {N['East Anglia']['private']['n']} in Norfolk and Suffolk.

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

Hotham, T. (2026) Lost kingdoms on the high street: early medieval kingdom names in modern British business names. Zenodo. {{https://doi.org/10.5281/zenodo.24104340}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
mit = open("/home/claude/studies/byelection-attention/LICENSE", encoding="utf-8").read().split("Text, figures and the paper")[0]
lic = mit + ("Text, figures and the paper: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/\n"
             "Derived data (data/): the feature files (osm_matches.csv, features.csv, features_geo.csv, site.json) are derived from OpenStreetMap "
             "and shared under the Open Database Licence 1.0, https://opendatacommons.org/licenses/odbl/1-0/ (OpenStreetMap contributors). "
             "Unit populations and boundaries: Open Government Licence v3.0 (ONS, NRS, NISRA). Other derived data CC BY 4.0.\n")
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Names of kingdoms that vanished 1,000+ years ago still stay at home: {W['n_in']} of {W['n']} "Wessex" businesses are in Wessex, and all {NO['n']} "Northumbria" businesses are in Northumbria

**Body:**

I read every business, club, public body and street in OpenStreetMap named after an early medieval British kingdom and checked it against a rough outline of the kingdom around AD 800.

- Wessex: {W['n_in']} of {W['n']} inside, in an area with {W['base_share']:.0f}% of UK residents. Most of the rest are just over the Avon in Bristol or over the Severn in Cardiff and Newport.
- Mercia: {M['n_in']} of {M['n']} inside. Northumbria: {NO['n_in']} of {NO['n']}, all in the North East.
- Per resident, {H1['pooled']['irr']:.0f}x as many kingdom-named businesses inside the kingdom as outside.
- Streets are the exception: only {R['streets']['share_in']:.0f}% of kingdom-named streets (the Wessex Closes and Mercia Drives) are inside their kingdom.
- Measured against the wrong kingdoms, the names show no preference at all.

Interactive map: https://maps.tristanhotham.com/{SLUG}/

**Source comment:**

Data: OpenStreetMap contributors (ODbL) via QLever; census residents from ONS, NRS and NISRA (OGL v3.0). Kingdom outlines are approximate, after Hill's Atlas of Anglo-Saxon England and Yorke's Kings and Kingdoms. Method: every match read by eye, rate ratio per resident inside vs outside with brand bootstrap intervals, plan written before the analysis. Tools: Python (pandas, geopandas, statsmodels, matplotlib), MapLibre. Paper and code: {REPO}
"""
os.makedirs(os.path.join(ROOT, "reddit"), exist_ok=True)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
cover = f"""# Cover note: Lost kingdoms on the high street

## Suitable journals (no article processing charge for the author)

Checked online in 2026 during review. Only venues where the author pays nothing on the standard route are listed. Word counts: the paper is about {{WORDS}} words before the references, counting tables and captions, and the abstract is {{ABWORDS}} words.

1. **Political Geography** (Elsevier). Subscription route free to authors; open access optional at the author's cost (listed at US$3,010), so choose the subscription route. Full-length papers up to 11,000 words (Cirad "Ou publier" journal record, which reproduces the Elsevier guide): the paper fits. Fit: good if framed around regional identity and the institutionalisation of regions (Paasi), less good for the onomastic angle.
2. **Journal of Cultural Analytics** (diamond open access: the DOAJ record states no publication fees of any kind; CC BY). Fit: good for the map-wide, open-data measurement of naming. Word limit: not stated on any page I could reach; confirm with the editors.
3. **Journal of Historical Geography** (Elsevier; hybrid, per the Max Planck Digital Library open access record, so the subscription route is free to authors). Fit: very good for the historical framing; it has published work on toponymy (Light 2004). Word limit: the Elsevier guide for authors could not be opened from the workspace; check it before submitting.
4. **Area** (RGS-IBG, Wiley; hybrid, per the same record, so the subscription route is free to authors). Suits a shortened version. Word limit: the Wiley author guidelines could not be opened from the workspace; Area papers are short, so expect to cut the paper substantially.

Not listed: **Names: A Journal of Onomastics** (its guidelines page sets a 200-word abstract limit and mentions possible fees for colour graphics, but states neither a word limit nor whether there is an article charge) and **Nomina** (not checked). Confirm fees before considering either.

## Summary of the contribution (for a cover letter)

The kingdoms of early medieval Britain have been gone for more than a thousand years, yet their names are used by police forces, utilities, regiments and some {F['private']} businesses and voluntary bodies in OpenStreetMap. This paper measures, across the whole UK, where those names are used. Reading every OpenStreetMap feature named after twelve kingdoms and comparing their locations with approximate kingdom extents fixed in an analysis plan beforehand, it finds that businesses and voluntary bodies named after Wessex, Mercia and Northumbria are concentrated inside their kingdoms at {H1['pooled']['irr']:.0f} times the per-resident rate outside, a result that survives every planned check and is absent in a placebo with the wrong kingdoms. Names that leave mostly stop just over the boundary. Public bodies are no more local than businesses, but street names, chosen by developers and councils, travel much further. The study connects regional identity, commercial naming and historical geography, with open data and code.
"""
import subprocess as _sp, re as _re
_txt = _sp.run(["pdftotext", os.path.join(REL, "paper", "Hotham_Lost_Kingdoms.pdf"), "-"], capture_output=True, text=True).stdout
_words = len(_txt.split("\nReferences\n")[0].split()); _ab = len(_txt.split("Abstract")[1].split("Keywords")[0].split())
cover = cover.replace("{WORDS}", f"{round(_words, -2):,}").replace("{ABWORDS}", str(_ab))
open(os.path.join(REL, "paper", "cover_note.md"), "w", encoding="utf-8").write(cover)
for t in (readme, post, cover, lic):
    for bad in ("—", "–", "DSIT", "DCMS", "civil serv", "pre-registered"):
        assert bad not in t, bad
print("readme", len(readme.split()), "words; cover", len(cover.split()))
