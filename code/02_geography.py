"""Step 2: areal units, populations and kingdom extents; every feature located in a unit and measured against every extent.
Areal units: MSOA 2021 (England and Wales, 7,264), council areas (Scotland, 32) and districts (Northern Ireland, 11), with
usual residents (Census 2021; Scotland 2022). Each unit gets its ceremonial county, its 2021 district, its local authority
(for clustering) and its English region or nation. Extents (core, main, wide) are unions of units per the token lists in
common.EXT, fixed in NOTES.md before any feature was located. Distances in metres on the British National Grid
(EPSG:27700); 0 inside. Outputs: data/units.csv, data/extents.geojson (simplified, for the page), data/features_geo.csv."""
import warnings
import numpy as np, pandas as pd, geopandas as gpd
from shapely.ops import unary_union
from common import *

warnings.filterwarnings("ignore")
BNG = "EPSG:27700"
ms = gpd.read_file(f"{GEO}/msoa21_bsc.geojson").to_crs(BNG)
ms["district"] = ms.MSOA21NM.str.replace(r" \d{3}$", "", regex=True)
pe = pd.read_csv(f"{POP}/ew_msoa_2021.csv", usecols=["msoa21cd", "la_code", "all_residents"])
ms = ms.merge(pe, left_on="MSOA21CD", right_on="msoa21cd", how="left")
assert ms.all_residents.notna().all()
ms = ms.rename(columns={"MSOA21CD": "code", "MSOA21NM": "uname", "all_residents": "pop", "la_code": "lad"})[["code", "uname", "district", "lad", "pop", "geometry"]]
lad = gpd.read_file(f"{GEO}/lad23_bsc.geojson").to_crs(BNG)
pl = pd.read_csv(f"{POP}/uk_local_authorities.csv", usecols=["code", "name", "all_residents"])
sn = lad[lad.LAD23CD.str[0].isin(["S", "N"])].merge(pl, left_on="LAD23CD", right_on="code", how="left")
assert sn.all_residents.notna().all(), sn[sn.all_residents.isna()].LAD23NM.tolist()
sn = sn.assign(uname=sn.LAD23NM, district=sn.LAD23NM, lad=sn.LAD23CD, pop=sn.all_residents)[["code", "uname", "district", "lad", "pop", "geometry"]]
U = gpd.GeoDataFrame(pd.concat([ms, sn], ignore_index=True), crs=BNG)
U["nation"] = U.code.str[0].map({"E": "England", "W": "Wales", "S": "Scotland", "N": "Northern Ireland"})
rp = U.representative_point()
cty = gpd.read_file(f"{GEO}/counties_uk.geojson").to_crs(BNG)
j = gpd.sjoin(gpd.GeoDataFrame(geometry=rp, crs=BNG), cty[["county", "geometry"]], how="left", predicate="within")
j = j[~j.index.duplicated()]
U["county"] = j["county"].values
miss = U.county.isna()
if miss.any():   # representative point just outside a generalised county edge: nearest county
    jn = gpd.sjoin_nearest(gpd.GeoDataFrame(geometry=rp[miss], crs=BNG), cty[["county", "geometry"]], how="left")
    U.loc[miss, "county"] = jn[~jn.index.duplicated()]["county"].values
U.loc[U.code.str[0] == "S", "county"] = U.loc[U.code.str[0] == "S", "uname"]
rg = gpd.read_file(f"{GEO}/uk_topo.json", layer="rgn").set_crs("EPSG:4326").to_crs(BNG)
j = gpd.sjoin_nearest(gpd.GeoDataFrame(geometry=rp, crs=BNG), rg[["areanm", "geometry"]], how="left")
j = j[~j.index.duplicated()]
U["region"] = np.where(U.nation == "England", j["areanm"].values, U.nation)
U["area_km2"] = U.area / 1e6
U["x"], U["y"] = rp.x.values, rp.y.values

# ---- extents ----
def members(k, v):
    toks = EXT[k][v]
    if toks and toks[0] == "+main":
        toks = EXT[k]["main"] + toks[1:]
    m = np.zeros(len(U), bool)
    for t in toks:
        kind, nm = t.split(":", 1)
        if kind == "C":
            hit = (U.county == nm).values
        elif kind == "D":
            hit = (U.district == nm).values
        else:
            hit = (U.uname == nm).values
        assert hit.any(), (k, v, t)
        m |= hit
    return m


EX = {}
for k in NAMES:
    for v in ("core", "main", "wide"):
        m = members(k, v)
        U[f"in_{k}_{v}"] = m.astype(int)
        EX[(k, v)] = unary_union(U.geometry[m].buffer(30).values).buffer(-30)
# distance from each unit's representative point to each main extent (km)
for k in NAMES:
    g = EX[(k, "main")]
    U[f"d_{k}"] = [0.0 if U.at[i, f"in_{k}_main"] else g.distance(rp.iloc[i]) / 1000 for i in range(len(U))]
U.drop(columns="geometry").to_csv(f"{DATA}/units.csv", index=False)

# simplified extents for the page and figures (WGS84)
recs = []
for (k, v), g in EX.items():
    gs = gpd.GeoSeries([g.simplify(600 if v != "core" else 400)], crs=BNG).to_crs("EPSG:4326").iloc[0]
    recs.append({"kingdom": k, "version": v, "geometry": gs})
E = gpd.GeoDataFrame(recs, crs="EPSG:4326")
E["geometry"] = E.geometry.apply(lambda g: g.buffer(0))
if os.path.exists(f"{DATA}/extents.geojson"):
    os.remove(f"{DATA}/extents.geojson")
E.to_file(f"{DATA}/extents.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)

# ---- features located ----
F = pd.read_csv(f"{DATA}/features.csv")
P = gpd.GeoDataFrame(F, geometry=gpd.points_from_xy(F.lon, F.lat), crs="EPSG:4326").to_crs(BNG)
j = gpd.sjoin(P[["fid", "geometry"]], U[["code", "geometry"]], how="left", predicate="within")
j = j[~j.index.duplicated()]
F["unit"] = j["code"].values
miss = F.unit.isna()
jn = gpd.sjoin_nearest(P.loc[miss, ["fid", "geometry"]], U[["code", "geometry"]], how="left", distance_col="dist")
jn = jn[~jn.index.duplicated()]
F.loc[miss, "unit"] = np.where(jn.dist <= 3000, jn.code, None)
F["offshore_m"] = 0.0
F.loc[miss, "offshore_m"] = jn.dist.round(0).values
print("features not in any unit within 3 km (dropped):", int(F.unit.isna().sum()), F[F.unit.isna()][["kingdom", "name", "lat", "lon"]].to_string())
F["x"], F["y"] = P.geometry.x.round(0), P.geometry.y.round(0)
uu = U.set_index("code")
for col in ("county", "district", "lad", "region", "nation"):
    F[col] = F.unit.map(uu[col])
for k in NAMES:
    pass
own = []
for i, r in F.iterrows():
    k = r.kingdom if r.kingdom in NAMES else "East Anglia"
    pt = P.geometry.iloc[i]
    o = {}
    for v in ("core", "main", "wide"):
        o[f"in_{v}"] = int(r.unit is not None and r.unit == r.unit and bool(uu.at[r.unit, f"in_{k}_{v}"]))
    o["d_main_km"] = 0.0 if o["in_main"] else round(EX[(k, "main")].distance(pt) / 1000, 2)
    nm, la, lo = CORE_PT[k]
    o["d_core_km"] = round(km(r.lat, r.lon, la, lo), 1)
    own.append(o)
F = pd.concat([F, pd.DataFrame(own)], axis=1)
# membership of every other kingdom's main extent (placebo P1)
for k in NAMES:
    F[f"in_{k}"] = [int(u == u and u is not None and bool(uu.at[u, f"in_{k}_main"])) for u in F.unit]
F.to_csv(f"{DATA}/features_geo.csv", index=False)
print(U.groupby("nation")["pop"].sum(), "units", len(U))
for k in NAMES:
    print(k, "main pop share %.3f" % (U.loc[U[f"in_{k}_main"] == 1, "pop"].sum() / U["pop"].sum()))
