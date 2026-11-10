"""Shared paths, constants and helpers for the lost-kingdoms study ("Lost kingdoms on the high street").

Inputs (read in place, never modified):
  RAW/osm_names_rose_kingdom.tsv  OpenStreetMap features in the UK whose name contains one of a list of historic county,
                                  rose and early medieval kingdom names, queried through QLever (osm-planet), retrieved
                                  2026 (ODbL, OpenStreetMap contributors). Columns ?x (OSM URI), ?name, ?shop, ?amenity,
                                  ?office, ?craft, ?leisure, ?highway, ?wkt. Shared with another study: read only.
  GEO/msoa21_bsc.geojson          ONS MSOA 2021 boundaries (England and Wales), Open Government Licence v3.0.
  GEO/lad23_bsc.geojson           ONS local authority districts December 2023 (UK; Scottish council areas, NI districts).
  GEO/counties_uk.geojson         England ceremonial counties, Welsh preserved counties, Scottish council areas, NI.
  POP/ew_msoa_2021.csv            Census 2021 usual residents by MSOA (ONS via Nomis, OGL v3.0), as compiled in Faith on the
                                  map (Hotham 2026, doi:10.5281/zenodo.23842991).
  POP/uk_local_authorities.csv    Usual residents by council: Scotland's Census 2022 (NRS), NI Census 2021 (NISRA), OGL.
"""
import json, gzip, os, re, math, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("LK_RAW", "/home/claude/newdata/raw_new13")
GEO = os.environ.get("LK_GEO", "/home/claude/newdata/raw/geo")
POP = os.environ.get("LK_POP", "/home/claude/studies/religion-map/data")
FONTS = os.environ.get("LK_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("LK_SCRATCH", "/home/claude/scratch/lost-kingdoms")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
REL = os.path.join(ROOT, "release")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "lost-kingdoms"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
TITLE = "Lost kingdoms on the high street"
SUBTITLE = "Wessex, Mercia, Elmet and Rheged in business names"

# kingdom names: whole-word regex (case-insensitive) on the feature name
NAMES = ["Wessex", "Mercia", "Northumbria", "Elmet", "Rheged", "Deira", "Bernicia", "Lindsey", "Strathclyde",
         "Dalriada", "Dumnonia", "East Anglia"]
PAT = {"Wessex": r"wessex", "Mercia": r"mercian?", "Northumbria": r"northumbrian?", "Elmet": r"elmete?",
       "Rheged": r"rheged", "Deira": r"deiran?", "Bernicia": r"bernician?", "Lindsey": r"lindsey",
       "Strathclyde": r"strathclyde", "Dalriada": r"dal ?riad(?:a|an)|d[aá]l riata", "Dumnonia": r"dumnonian?",
       "East Anglia": r"east anglian?"}
ANGLIA_VAR = r"(?<!east )anglian?"     # Anglia / Anglian without "East": robustness R9 only
COL = {"Wessex": "#B3202A", "Mercia": "#2F7FB8", "Northumbria": "#D08A1E", "Elmet": "#3B8B5A", "Rheged": "#7A4FA0",
       "Deira": "#C2577F", "Bernicia": "#8A6A3B", "Lindsey": "#2E9C9C", "Strathclyde": "#55606B", "Dalriada": "#6B8E23",
       "Dumnonia": "#A0522D", "East Anglia": "#9C9384"}
MIN_TEST = 20                          # names with fewer private features are described, not tested

# ---- kingdom extents: unions of areal units (pre-specified in NOTES.md before any feature was located) ----
# tokens: "C:<ceremonial county>" (counties_uk.geojson name), "D:<2021 district>" (MSOA name prefix), "S:<council>" / "N:<district>"
EXT = {
 "Wessex": {"core": ["C:Hampshire", "C:Wiltshire", "C:Dorset", "C:Somerset"],
            "main": ["C:Hampshire", "C:Isle of Wight", "C:Wiltshire", "C:Dorset", "C:Somerset", "C:Berkshire", "C:Devon"],
            "wide": ["+main", "C:Cornwall", "C:Surrey", "C:East Sussex", "C:West Sussex", "C:Kent", "C:Bristol"]},
 "Mercia": {"core": ["C:Staffordshire", "C:West Midlands", "C:Warwickshire", "C:Leicestershire", "C:Derbyshire", "C:Nottinghamshire"],
            "main": ["C:Staffordshire", "C:West Midlands", "C:Warwickshire", "C:Worcestershire", "C:Herefordshire", "C:Shropshire",
                     "C:Gloucestershire", "C:Bristol", "C:Cheshire", "C:Derbyshire", "C:Nottinghamshire", "C:Leicestershire",
                     "C:Rutland", "C:Northamptonshire", "C:Lincolnshire", "C:Oxfordshire", "C:Buckinghamshire",
                     "C:Bedfordshire", "C:Hertfordshire"],
            "wide": ["+main", "C:Cambridgeshire", "C:Greater London", "C:Essex"]},
 "Northumbria": {"core": ["C:Northumberland", "C:Tyne and Wear", "C:Durham", "C:North Yorkshire", "C:East Riding of Yorkshire"],
                 "main": ["C:Northumberland", "C:Tyne and Wear", "C:Durham", "C:North Yorkshire", "C:East Riding of Yorkshire",
                          "C:West Yorkshire", "C:South Yorkshire", "C:Cumbria", "C:Lancashire"],
                 "wide": ["+main", "C:Scottish Borders", "C:East Lothian", "C:Midlothian", "C:City of Edinburgh", "C:West Lothian",
                          "C:Dumfries and Galloway", "C:Greater Manchester", "C:Merseyside"]},
 "Deira": {"core": ["C:East Riding of Yorkshire", "D:York"],
           "main": ["C:East Riding of Yorkshire", "C:North Yorkshire"],
           "wide": ["+main", "C:West Yorkshire", "C:South Yorkshire"]},
 "Bernicia": {"core": ["C:Northumberland"],
              "main": ["C:Northumberland", "C:Tyne and Wear", "C:Durham", "C:Scottish Borders", "C:East Lothian", "C:Midlothian",
                       "C:City of Edinburgh", "C:West Lothian"],
              "wide": ["+main", "C:Falkirk", "C:Cumbria"]},
 "Elmet": {"core": ["D:Leeds", "D:Selby"],
           "main": ["D:Leeds", "D:Bradford", "D:Calderdale", "D:Kirklees", "D:Wakefield", "D:Selby"],
           "wide": ["+main", "D:Harrogate", "D:Barnsley", "D:Doncaster", "D:Rotherham", "D:Sheffield"]},
 "Rheged": {"core": ["D:Carlisle"],
            "main": ["C:Cumbria", "C:Dumfries and Galloway"],
            "wide": ["+main", "C:Lancashire", "C:South Ayrshire"]},
 "Lindsey": {"core": ["D:West Lindsey", "D:Lincoln"],
             "main": ["D:West Lindsey", "D:East Lindsey", "D:Lincoln", "D:North Lincolnshire", "D:North East Lincolnshire"],
             "wide": ["+main", "C:Lincolnshire"]},
 "Strathclyde": {"core": ["C:West Dunbartonshire"],
                 "main": ["C:West Dunbartonshire", "C:East Dunbartonshire", "C:Glasgow City", "C:Renfrewshire", "C:East Renfrewshire",
                          "C:Inverclyde", "C:North Lanarkshire", "C:South Lanarkshire"],
                 "wide": ["+main", "C:North Ayrshire", "C:South Ayrshire", "C:East Ayrshire", "C:Stirling", "C:Dumfries and Galloway",
                          "C:Cumbria"]},
 "Dalriada": {"core": ["C:Argyll and Bute"],
              "main": ["C:Argyll and Bute", "N:Causeway Coast and Glens", "N:Mid and East Antrim"],
              "wide": ["+main", "C:Highland", "N:Antrim and Newtownabbey"]},
 "Dumnonia": {"core": ["C:Cornwall", "C:Devon"],
              "main": ["C:Cornwall", "C:Devon", "D:Somerset West and Taunton"],
              "wide": ["+main", "C:Somerset", "C:Dorset"]},
 "East Anglia": {"core": ["C:Norfolk", "C:Suffolk"],
                 "main": ["C:Norfolk", "C:Suffolk"],
                 "wide": ["+main", "C:Cambridgeshire", "C:Essex"]},
}
CORE_PT = {"Wessex": ("Winchester", 51.0632, -1.3080), "Mercia": ("Tamworth", 52.6339, -1.6950),
           "Northumbria": ("Bamburgh", 55.6090, -1.7099), "Bernicia": ("Bamburgh", 55.6090, -1.7099),
           "Deira": ("York", 53.9590, -1.0815), "Elmet": ("Leeds", 53.7997, -1.5492), "Rheged": ("Carlisle", 54.8925, -2.9329),
           "Lindsey": ("Lincoln", 53.2307, -0.5406), "Strathclyde": ("Dumbarton", 55.9364, -4.5627),
           "Dalriada": ("Dunadd", 56.0889, -5.4782), "Dumnonia": ("Exeter", 50.7184, -3.5339), "East Anglia": ("Norwich", 52.6309, 1.2974)}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", "and")
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "x1": return f"{float(v):.1f} times"
    raise ValueError(f)
