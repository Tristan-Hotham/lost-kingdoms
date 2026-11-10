"""Step 4: page data. data/site.json = every curated feature that is a business, public body, street or named site (not
transport stops, routes or infrastructure), with its kingdom name, class, point, district and whether it is inside the
name's approximate extent; data/extents_web.geojson = the core, main and wide extents (WGS84, simplified)."""
import pandas as pd, geopandas as gpd
from common import *

F = pd.read_csv(f"{DATA}/features_geo.csv")
F = F[F.cls.isin(["PRIVATE", "PUBLIC", "STREET", "SITE"]) & F.kingdom.isin(NAMES)].copy()
CL = {"PRIVATE": "b", "PUBLIC": "p", "STREET": "s", "SITE": "x"}
feats = []
for r in F.itertuples():
    osm = r.osm.replace("https://www.openstreetmap.org/", "")
    feats.append([r.name, NAMES.index(r.kingdom), CL[r.cls], round(r.lat, 5), round(r.lon, 5), int(r.in_main), round(r.d_main_km),
                  r.district if isinstance(r.district, str) else "", osm, int(r.place_derived), int(r.ambiguous)])
S = {"names": NAMES, "col": [COL[k] for k in NAMES], "core": [CORE_PT[k][0] for k in NAMES],
     "f": feats, "cols": ["name", "k", "cls", "lat", "lon", "in", "dkm", "district", "osm", "pd", "amb"]}
jsave(S, f"{DATA}/site.json")
E = gpd.read_file(f"{DATA}/extents.geojson")
E["geometry"] = E.geometry.simplify(0.004)
E.to_file(f"{DATA}/extents_web.geojson", driver="GeoJSON", COORDINATE_PRECISION=3)
print(len(feats), "features;", os.path.getsize(f"{DATA}/site.json") // 1024, "KB;", os.path.getsize(f"{DATA}/extents_web.geojson") // 1024, "KB extents")

# extra descriptive numbers used in the text (added to results.json)
R = jload(f"{DATA}/results.json")
P = pd.read_csv(f"{DATA}/features_geo.csv")
P = P[(P.cls == "PRIVATE") & P.kingdom.isin(NAMES)]
wo = P[(P.kingdom == "Wessex") & (P.in_main == 0)]
R["wessex_out"] = {"n": int(len(wo)), "by_district": {k: int(v) for k, v in wo.district.value_counts().items()},
                   "within25": int((wo.d_main_km <= 25).sum()), "bristol": int((wo.district == "Bristol").sum()),
                   "wales": int(wo.district.isin(["Cardiff", "Newport"]).sum()), "garages_brand_wales": int((wo.district.isin(["Cardiff", "Newport"]) & wo.name.str.contains("Kia|Hyundai|Nissan|Garages")).sum()),
                   "in_wide": int(wo.in_wide.sum())}
R["place_derived_by_name"] = {k: int(((P.kingdom == k) & (P.place_derived == 1)).sum()) for k in NAMES}
R["ambiguous_by_name"] = {k: int(((P.kingdom == k) & (P.ambiguous == 1)).sum()) for k in NAMES}
R["site"] = {"features": len(feats)}
R["northumbria_ne"] = int(((P.kingdom == "Northumbria") & (pd.read_csv(f"{DATA}/features_geo.csv").loc[P.index, "region"] == "North East")).sum())
wi = P[(P.kingdom == "Wessex") & (P.in_main == 1)]
R["wessex_in_by_county"] = {k: int(v) for k, v in wi.county.value_counts().items()}

# completeness check (review, 2026): the main raw file has exactly 7,500 rows, so a second, unlimited export with exact
# keywords (osm_names_full_v2.tsv) was compared by OSM id. That export itself stopped on a time-out (no nodes), so it can
# only show whether it holds kingdom-name objects that the main file lacks.
def _ids(fn):
    out = {}
    with open(f"{RAW}/{fn}", encoding="utf-8") as f:
        f.readline()
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) == 9:
                out[r[0].strip().strip('"')] = r[1].strip().strip('"')
    return out
_hit = lambda n: any(re.search(r"\b(?:" + PAT[k] + r")\b", n, re.I) for k in NAMES) or bool(re.search(r"\b" + ANGLIA_VAR + r"\b", n, re.I))
if os.path.exists(f"{RAW}/osm_names_full_v2.tsv"):
    v1, v2 = _ids("osm_names_rose_kingdom.tsv"), _ids("osm_names_full_v2.tsv")
    k1 = {i for i, n in v1.items() if _hit(n)}; k2 = {i for i, n in v2.items() if _hit(n)}
    R["completeness"] = {"v1_rows": len(v1), "v2_rows": len(v2), "v1_kingdom_objects": len(k1), "v2_kingdom_objects": len(k2),
                         "v2_missing_from_v1": len(k2 - k1), "merged_in": 0}
jsave(R, f"{DATA}/results.json", indent=1)
print(R["wessex_out"])
