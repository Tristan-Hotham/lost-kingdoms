# lost-kingdoms: working notes

Brief: /home/claude/work/new13/BRIEFS.md section D ("Lost kingdoms on the high street: Wessex, Mercia, Elmet and Rheged in
business names"), plus the shared rules it points to (new12, new11, new10, new9, new8 tops; house brief
/home/claude/newdata/BRIEF.md; GIF brief /home/claude/gifs/BRIEF.md). Format refs: fame-half-life, byelection-attention.
Scratch: /home/claude/scratch/lost-kingdoms (delete by exact path at the end).
Raw names file /home/claude/newdata/raw_new13/osm_names_rose_kingdom.tsv is SHARED with the rose-border builder: read only.

## Analysis plan (written 2026-11-10 08:35 UTC, before any feature was located against any kingdom extent)

What I had seen when writing this: the brief; the file's columns; raw regex hit counts per term over the whole name
string (which showed that "Mercia" also matches "Commercial", "Deira" matches "Madeira" and "Lindsey" is also a personal
name, so curation needs whole-word matching and reading by eye). No coordinates had been compared with any extent.

### Question
How closely do modern uses of early medieval kingdom names (Wessex, Mercia, Northumbria, Elmet, Rheged, Deira, Bernicia,
Lindsey, Strathclyde, Dalriada, Dumnonia; East Anglia separately because it is also a modern region) track the kingdoms'
approximate extents c. 600 to 900, and which names travelled furthest? Do private names (shops, pubs, clubs, firms) differ
from public bodies (police, NHS, councils, schools, regiments, utilities)?

### Unit, outcome, exposure
- Unit: a curated named feature in OpenStreetMap (UK) whose name contains a kingdom name as a whole word (variants:
  Mercian, Northumbrian, Elmete, Deiran, Bernician, Dalriadan/Dal Riata, Dumnonian, East Anglian). Duplicates merged:
  same normalised name within 250 m is one feature (node + building outline of one pub); street segments with the same
  name within 1 km are one street.
- Types (from OSM tags, then name keywords, every untagged case read by eye): PRIVATE (shops, pubs, cafes, restaurants,
  hotels, firms and offices, crafts, clubs and societies, leisure and sports venues, places of worship, charities);
  PUBLIC (police, fire, ambulance, NHS and health, councils and government, schools, colleges and universities, military,
  utilities named for statutory regions, protected landscapes); STREET (named highways: analysed separately, since
  streets are named by councils and developers); OTHER (transport stops, rail lines and routes, bare housing estates,
  natural features: excluded and counted). Main analysis = PRIVATE; PUBLIC compared with it (H3).
- Place-derived names: names that contain the kingdom word only as part of a modern place name (Sherburn in Elmet,
  Barwick in Elmet, Lindsey in Suffolk, West/East Lindsey district) are flagged; kept in the main analysis when the place
  name itself descends from the kingdom (Elmet, Lindsey districts), with a robustness check dropping them.
- Extents: approximate areas c. 800 (the kingdom at its main early medieval extent), drawn as unions of modern areal
  units (England and Wales: MSOA 2021 assigned by ceremonial county or 2021 district; Scotland: council areas; Northern
  Ireland: 2023 council districts). Three versions per kingdom: CORE (heartland), MAIN (c. 800), WIDE (greatest
  plausible extent before c. 900). Sources: Hill (1981) Atlas of Anglo-Saxon England; Yorke (1990); and the specialist
  works cited per kingdom in the paper. Boundaries are uncertain; the analysis is about broad tracking, not lines.
  MAIN definitions (written now, before looking):
  - Wessex: Hampshire, Isle of Wight, Wiltshire, Dorset, Somerset (incl. N Somerset, Bath and NE Somerset), Berkshire,
    Devon. CORE: Hampshire, Wiltshire, Dorset, Somerset. WIDE: + Cornwall, Surrey, Sussex (East, West), Kent, Bristol.
  - Mercia: Staffordshire, West Midlands, Warwickshire, Worcestershire, Herefordshire, Shropshire, Gloucestershire
    (incl. South Glos) and Bristol, Cheshire, Derbyshire, Nottinghamshire, Leicestershire, Rutland, Northamptonshire,
    Lincolnshire, Oxfordshire, Buckinghamshire, Bedfordshire, Hertfordshire. CORE: Staffordshire, West Midlands,
    Warwickshire, Leicestershire, Derbyshire, Nottinghamshire. WIDE: + Cambridgeshire, Greater London, Essex.
  - Northumbria: Northumberland, Tyne and Wear, Durham, North Yorkshire, East Riding of Yorkshire, West Yorkshire, South
    Yorkshire, Cumbria, Lancashire. CORE: Northumberland, Tyne and Wear, Durham, North Yorkshire, East Riding. WIDE: +
    Scottish Borders, East Lothian, Midlothian, City of Edinburgh, West Lothian, Dumfries and Galloway, Greater
    Manchester, Merseyside.
  - Deira: East Riding of Yorkshire, North Yorkshire. CORE: East Riding (incl. Hull) + York. WIDE: + West Yorkshire,
    South Yorkshire.
  - Bernicia: Northumberland, Tyne and Wear, Durham, Scottish Borders, East Lothian, Midlothian, City of Edinburgh, West
    Lothian. CORE: Northumberland. WIDE: + Falkirk, Cumbria.
  - Elmet: districts Leeds, Bradford, Calderdale, Kirklees, Wakefield, Selby. CORE: Leeds, Selby. WIDE: + Harrogate,
    Barnsley, Doncaster, Rotherham, Sheffield.
  - Rheged: Cumbria, Dumfries and Galloway. CORE: Carlisle district. WIDE: + Lancashire, South Ayrshire.
  - Lindsey: districts West Lindsey, East Lindsey, Lincoln, North Lincolnshire, North East Lincolnshire. CORE: West
    Lindsey, Lincoln. WIDE: all Lincolnshire (ceremonial).
  - Strathclyde: West Dunbartonshire, East Dunbartonshire, Glasgow City, Renfrewshire, East Renfrewshire, Inverclyde,
    North Lanarkshire, South Lanarkshire. CORE: West Dunbartonshire. WIDE: + North, South and East Ayrshire, Stirling,
    Dumfries and Galloway, Cumbria (the later southward expansion).
  - Dalriada: Argyll and Bute, Causeway Coast and Glens, Mid and East Antrim. CORE: Argyll and Bute. WIDE: + Highland,
    Antrim and Newtownabbey.
  - Dumnonia: Devon, Cornwall (incl. Isles of Scilly), Somerset West and Taunton district. CORE: Cornwall, Devon. WIDE: +
    all Somerset, Dorset.
  - East Anglia: Norfolk, Suffolk. CORE: same. WIDE: + Cambridgeshire, Essex (the modern sense).
  Core points for distance from the centre: Winchester (Wessex), Tamworth (Mercia), Bamburgh (Northumbria, Bernicia),
  York (Deira), Leeds (Elmet), Carlisle (Rheged), Lincoln (Lindsey), Dumbarton (Strathclyde), Dunadd (Dalriada),
  Exeter (Dumnonia), Norwich (East Anglia).
- Baseline: usual residents (Census 2021 England, Wales, Northern Ireland; Scotland 2022) of the areal units.

### Hypotheses and tests (main specification)
- H1 (tracking): for each name, private features are more common per resident inside its MAIN extent than outside.
  Estimand: rate ratio RR_k = (n_in / pop_in) / (n_out / pop_out); 95% CI by cluster bootstrap over brands (distinct
  normalised names; 2,000 draws), so chains do not count as independent; also share inside with Wilson interval and the
  extent's population share. Pooled: Poisson regression of feature counts by (name, areal unit) with name fixed effects,
  log population offset and an inside indicator; SEs clustered by local authority. Against H1: RR CI including 1.
- H2 (distance decay): outside the extent, density per resident falls with distance from the extent edge. Poisson over
  areal units outside each extent, name fixed effects, log population offset, distance to the MAIN extent in 100 km;
  SEs clustered by local authority. Report exp(gamma) per 100 km. Against H2: CI including 1. Descriptive: median
  distance outside; share within 50 km of the edge.
- H3 (private vs public): public bodies' names sit inside the extent more often than private names (public bodies serve
  defined modern territories chosen to fit the name). Logit (linear probability as a check) of inside on public, name
  fixed effects, SEs clustered by brand. Two-sided; expectation public > private.
- H4 (which travelled furthest): names ranked by share outside and by RR; no directional hypothesis beyond the brief's
  candidates (Wessex: Hardy's revival; Mercia: modern institutional use; Elmet: local). Exploratory, labelled as such,
  bootstrap CIs. Names with fewer than 20 private features are described but not tested.
- East Anglia: reported separately as a modern-region comparison, not pooled with the kingdoms.

### Pre-specified checks
- Placebo P1 (wrong extents): the RR of each name for every other kingdom's MAIN extent that does not overlap its own;
  expected at or below 1.
- R1 WIDE extents; R2 CORE extents; R3 brand level (each distinct normalised name once, at its first-listed location);
  R4 leave one nation or English region out (pooled RR); R5 drop place-derived names; R6 area baseline (per km2) instead
  of residents; R7 drop chains (brands with more than 3 features); R8 add streets to private; R9 include ambiguous
  variants (Anglia/Anglian without East).
- A result is called robust only if its CI excludes 1 in the main specification and in every check above except where a
  check removes most of the data (stated).

### Honesty
OpenStreetMap coverage is uneven; names are a sample of what is mapped, not of all businesses (Companies House not
reachable from the workspace). Some names predate any revival; I cannot date features. Extents are approximate.
Correlational throughout.

## Log
- 08:40 to 09:10 UTC. Curation (01_features.py, code/overrides.csv), before any location test. Whole-word matching found
  2,547 object-name pairs in 7,500 raw rows (most raw hits were "Commercial", "Madeira", Lancashire/Yorkshire names).
  Every non-street object read by eye. Rules: highways split into streets, stops and paths; infrastructure, routes,
  signs, rail lines (425 segments of "Wessex Main Line"), substations, refinery: OTHER; names built on a street
  ("Wessex Road Surgery", "Northumbria Way Pharmacy"): OTHER; tagged shops, amenities, offices, crafts and leisure
  venues: PRIVATE unless a public body (police, councils, schools, universities, NHS, regiments, statutory water
  companies, drainage boards). Untagged building names, estates and business parks: a SITE class (not in the plan;
  added because they are neither businesses nor public bodies; used only in the exploratory check R10).
  Not the kingdom: Deira in "The New Dhanak Deira" (a district of Dubai); Lindsey as a personal name (Cunningham
  Lindsey, Flowers by Lindsey, Taylor Lindsey...), and anything within 3 km of Lindsey (Suffolk) or Norton Lindsey
  (Warwickshire), a rule fixed before looking at extents. Place-derived (kept, dropped in R5): Sherburn in Elmet,
  Barwick in Elmet, Elmete (Leeds), Kirton in Lindsey, East/West/North Lindsey, Lindsey Marsh, Strathclyde Park and
  Business Park. Ambiguous (could be a first name; dropped in R5): ten Lindsey names. Brands: chains canonicalised
  (East Anglia's Children's Hospices, Anglian Home Improvements, Wessex Garages, Wessex Photo...).
- Data caveat: the raw file has exactly 7,500 rows, sorted by OSM IRI and ending in the last way IDs; it looks complete,
  but a round number could mean a query limit. Worth checking with the lead (if truncated, ways with high IDs and all
  relations after them would be missing, which is not what the sort order shows: relations sort before ways and are present).
- 09:15 UTC. Geography (02): MSOA 2021 + Scottish councils + NI districts, 7,307 units, 67.0 million residents.
- 09:25 UTC. Analysis (03) run once as planned. Then two fixes that do not change any estimate: (1) H2 cannot be
  estimated for names with no or almost no features outside (Northumbria 0, Mercia 2): H2 is reported for Wessex only,
  as the brief's pooled model would be identified by Wessex alone; (2) when every feature of a name is inside (or
  outside) the bootstrap is degenerate, so for those names the CI is the Wilson bound carried to the rate ratio scale.
  R5 does not touch the three tested names (their names have no place-derived or ambiguous cases): it matters only for the
  all-names pooled model, which is reported beside it.
- 09:30 to 10:00 UTC. Figures, page (QA desktop 1280 and phone 390: 0 console errors, no horizontal scroll, full-screen
  button present), paper (21 pages, about 7,600 words before references, 36 references), blog, collage, GIF, release.
  References: verified by web search in this session (Yorke, Hill, Bassett, Rollason, Brown and Farr, Clarkson,
  Campbell, McCarthy, Vince, Pearce x2, Hughes and Godwin, Hardy preface, Gatrell, Paasi x2, Light and Young 2015,
  Rose-Redwood et al., Haklay 2010) or taken from reviewed, published sibling papers (Alderman, Azaryahu, Light,
  Light and Young 2014, Oto-Peralias, Bancilhon, Gutierrez-Mora, Collignon and Sajuria, Haklay and Weber, Bast x2,
  Cameron x2, Efron and Tibshirani, Santos Silva and Tenreyro). The shared web search allowance ran out before I could
  check the Names / Nomina / Area author pages: cover note says so.

## Independent review (2026)
- Data completeness. Main raw file: 7,500 rows (exactly), 2,547 kingdom-name objects (incl. "Anglia" variants), sorted by OSM IRI.
  Re-run without a limit, exact keywords, UK only (raw_new13/osm_names_full_v2.tsv): 5,835 data rows, 1,775 kingdom-name
  objects. That export itself ended with "Operation timed out" and holds no nodes (214 relations, 5,621 ways), so it is
  partial too. Compared by OSM id: 0 kingdom-name objects in v2 are missing from the main file, and no v2 object sorts
  after the main file's last row (way/99954334). Counts before and after the merge: 2,547 objects / 1,087 features /
  254 private, unchanged (nothing to merge). Recorded in results.json "completeness" (code/04_site.py) and in the paper's
  limitations. Residual risk: kingdom-name ways sorting after way/99954334 (a tiny id range) could be absent from both.
- Re-ran 01 to 04: features.csv identical, results.json identical to the stored file.
- Fixes: street share was described as "of the tested names" (it is all eleven kingdom names: 335 streets); robustness
  table now uses unrounded values (19.5 not 19.4); "at least 15" -> 14.5; Wessex "commonest in Dorset and Wiltshire"
  corrected to Dorset 22, Hampshire 21 (results.json wessex_in_by_county); unchecked superlatives and a Paasi phrase
  presented as a quotation removed; tab:out now referenced; blog/page/post claims softened; cover note journals re-checked
  online (Political Geography 11,000 words; JCA no fees; JHG and Area hybrid, limits not reachable); collage Rheged label
  moved off Northern Ireland, Bernicia and Dumnonia added to the legend; GIF subtitle overflow fixed, source credit added.
