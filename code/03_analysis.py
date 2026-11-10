"""Step 3: the pre-specified analysis (NOTES.md). H1 tracking (rate ratio inside vs outside each name's main extent, per
resident; brand-cluster bootstrap CIs; pooled Poisson with name fixed effects, SEs clustered by local authority), H2
distance decay outside the extent, H3 public vs private, H4 which names travelled furthest, placebo P1 (wrong extents)
and robustness checks R1 to R10. Output: data/results.json (every number quoted anywhere), data/name_table.csv,
data/robustness.csv."""
import warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from common import *

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20261110)
B = 2000
U = pd.read_csv(f"{DATA}/units.csv")
F = pd.read_csv(f"{DATA}/features_geo.csv")
F = F[F.unit.notna()].copy()
POPT = U["pop"].sum()
KING = [k for k in NAMES if k != "East Anglia"]


def wilson(x, n, z=1.96):
    if n == 0: return (None, None)
    p = x / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def rr_counts(n_in, n_out, p_in, p_out):
    if n_out == 0 or n_in == 0:
        return (n_in + 0.5) / p_in / ((n_out + 0.5) / p_out)
    return (n_in / p_in) / (n_out / p_out)


def per_name(G, k, ver="main", base="pop", boot=True):
    """rate ratio inside vs outside the extent of name k for the features in G (one name)."""
    inside = U[f"in_{k}_{ver}"] == 1
    w = U["pop"] if base == "pop" else U["area_km2"]
    p_in, p_out = w[inside].sum(), w[~inside].sum()
    col = f"in_{ver}"
    n = len(G); n_in = int(G[col].sum()); n_out = n - n_in
    o = {"n": n, "n_in": n_in, "n_out": n_out, "brands": int(G.brand.nunique()), "share_in": 100 * n_in / n if n else None,
         "base_share": 100 * p_in / (p_in + p_out), "rr": rr_counts(n_in, n_out, p_in, p_out) if n else None}
    lo, hi = wilson(n_in, n)
    o["share_lo"], o["share_hi"] = (100 * lo, 100 * hi) if n else (None, None)
    if n:   # the rate ratio is the odds of being inside over the odds of a resident being inside: Wilson bounds carry over
        b_ = p_in / (p_in + p_out); odds = lambda s: s / (1 - s) if s < 1 else float("inf")
        o["rr_w_lo"] = odds(lo) / odds(b_); o["rr_w_hi"] = odds(hi) / odds(b_)
        if n_in and n_out:
            o["rr"] = odds(n_in / n) / odds(b_)
    if boot and n:
        br = G.groupby("brand")[col].agg(["sum", "size"])
        s, z = br["sum"].values, br["size"].values
        draws = []
        for _ in range(B):
            ix = rng.integers(0, len(br), len(br))
            a, t = s[ix].sum(), z[ix].sum()
            draws.append(math.log(rr_counts(a, t - a, p_in, p_out)))
        o["rr_lo"], o["rr_hi"] = float(np.exp(np.percentile(draws, 2.5))), float(np.exp(np.percentile(draws, 97.5)))
        o["zero_cell"] = int(n_in == 0 or n_out == 0)
        if o["zero_cell"]:   # bootstrap is degenerate when every feature is on one side: report the Wilson bound only
            o["rr"], o["rr_lo"], o["rr_hi"] = None, o["rr_w_lo"], o["rr_w_hi"]
    return o


def panel(G, names, ver="main", drop_units=None):
    """(name, unit) counts with inside indicator and distance to the main extent."""
    rows = []
    Uk = U if drop_units is None else U[~drop_units]
    cnt = G.groupby(["kingdom", "unit"]).size()
    for k in names:
        d = pd.DataFrame({"unit": Uk.code.values, "lad": Uk.lad.values, "pop": Uk["pop"].values, "area": Uk.area_km2.values,
                          "inside": Uk[f"in_{k}_{ver}"].values, "dist": Uk[f"d_{k}"].values / 100.0, "name": k})
        c = cnt.get(k)
        d["y"] = d.unit.map(c).fillna(0).values if c is not None else 0
        rows.append(d)
    return pd.concat(rows, ignore_index=True)


def pois(df, formula, offset="pop", key="inside"):
    m = smf.glm(formula, df, family=sm.families.Poisson(), offset=np.log(df[offset])).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df.lad)[0]})
    b, se = m.params[key], m.bse[key]
    return {"irr": float(np.exp(b)), "lo": float(np.exp(b - 1.96 * se)), "hi": float(np.exp(b + 1.96 * se)), "coef": float(b), "se": float(se),
            "p": float(m.pvalues[key]), "n_rows": int(len(df)), "n_features": int(df.y.sum()), "clusters": int(df.lad.nunique())}


R = {"meta": {"title": TITLE, "subtitle": SUBTITLE, "B": B, "min_test": MIN_TEST}}
# ---- data flow ----
RAW_N = sum(1 for _ in open(f"{RAW}/osm_names_rose_kingdom.tsv", encoding="utf-8")) - 1
OM = pd.read_csv(f"{DATA}/osm_matches.csv")
FA = pd.read_csv(f"{DATA}/features.csv")
fl = {"raw_rows": RAW_N, "matched_objects": int(OM.osm.nunique()), "matched_pairs": int(len(OM)),
      "features": int(len(FA[FA.kingdom != "Anglia (no East)"])), "hand_rows": int(OM.hand.sum()),
      "hand_pc": 100 * OM.hand.mean()}
for c in ("PRIVATE", "PUBLIC", "STREET", "SITE", "OTHER"):
    fl[c.lower()] = int(((FA.cls == c) & (FA.kingdom != "Anglia (no East)")).sum())
fl["private_kingdoms"] = int(((FA.cls == "PRIVATE") & FA.kingdom.isin(KING)).sum())
fl["private_brands"] = int(FA[(FA.cls == "PRIVATE") & FA.kingdom.isin(KING)].brand.nunique())
fl["not_kingdom"] = int(FA["sub"].str.contains("not the kingdom", na=False).sum())
fl["place_derived_private"] = int(((FA.cls == "PRIVATE") & (FA.place_derived == 1) & FA.kingdom.isin(KING)).sum())
fl["ambiguous_private"] = int(((FA.cls == "PRIVATE") & (FA.ambiguous == 1)).sum())
R["flow"] = fl
R["population"] = {"total": int(POPT), "units": int(len(U))}

PRIV = F[(F.cls == "PRIVATE") & F.kingdom.isin(NAMES)]
PUB = F[(F.cls == "PUBLIC") & F.kingdom.isin(NAMES)]
STR = F[(F.cls == "STREET") & F.kingdom.isin(NAMES)]
TESTED = [k for k in KING if (PRIV.kingdom == k).sum() >= MIN_TEST]
R["tested"] = TESTED
R["n_tested"] = len(TESTED)

# ---- H1 per name ----
names = {}
tab = []
for k in NAMES:
    o = {"private": per_name(PRIV[PRIV.kingdom == k], k), "public": per_name(PUB[PUB.kingdom == k], k),
         "street": per_name(STR[STR.kingdom == k], k, boot=False)}
    G = PRIV[PRIV.kingdom == k]
    o["private"]["tested"] = int(k in TESTED)
    if len(G):
        out = G[G.in_main == 0]
        o["private"]["med_out_km"] = float(out.d_main_km.median()) if len(out) else 0.0
        o["private"]["max_out_km"] = float(out.d_main_km.max()) if len(out) else 0.0
        o["private"]["within50_pc"] = 100 * float((G.d_main_km <= 50).mean())
        o["private"]["med_core_km"] = float(G.d_core_km.median())
        o["private"]["far_name"] = out.sort_values("d_main_km").iloc[-1]["name"] if len(out) else ""
        o["private"]["far_place"] = (out.sort_values("d_main_km").iloc[-1]["district"] if len(out) else "")
    o["core_point"] = CORE_PT[k][0]
    o["n_all"] = int((F.kingdom == k).sum())
    names[k] = o
    p = o["private"]
    tab.append({"kingdom": k, "private": p["n"], "brands": p["brands"], "in": p["n_in"], "share_in": p["share_in"],
                "share_lo": p["share_lo"], "share_hi": p["share_hi"], "pop_share": p["base_share"], "rr": p["rr"],
                "rr_lo": p.get("rr_lo"), "rr_hi": p.get("rr_hi"), "public": o["public"]["n"], "public_share_in": o["public"]["share_in"],
                "streets": o["street"]["n"], "street_share_in": o["street"]["share_in"], "street_rr": o["street"]["rr"], "tested": int(k in TESTED)})
R["names"] = names
pd.DataFrame(tab).to_csv(f"{DATA}/name_table.csv", index=False, float_format="%.4g")
Ptab = pd.DataFrame(tab)
R["kingdom_private_n"] = int(Ptab[Ptab.kingdom != "East Anglia"].private.sum())
R["kingdom_private_in"] = int(Ptab[Ptab.kingdom != "East Anglia"]["in"].sum())
R["kingdom_private_share_in"] = 100 * R["kingdom_private_in"] / R["kingdom_private_n"]

# pooled Poisson (main): tested names; secondary: every kingdom name
pan = panel(PRIV, TESTED)
R["H1"] = {"pooled": pois(pan, "y ~ C(name) + inside"), "pooled_all": pois(panel(PRIV, [k for k in KING if (PRIV.kingdom == k).any()]), "y ~ C(name) + inside")}
# exploratory: streets, which councils and developers name
R["streets"] = {"pooled": pois(panel(STR, TESTED), "y ~ C(name) + inside"), "n": int(STR.kingdom.isin(KING).sum()),
                "share_in": 100 * float(STR[STR.kingdom.isin(KING)].in_main.mean())}
spo = panel(STR, TESTED); spo = spo[spo.inside == 0]
R["streets"]["decay"] = pois(spo, "y ~ C(name) + dist", key="dist")
# per name from the same Poisson (analytic, clustered by local authority) as a cross-check of the bootstrap
R["H1"]["per_name_poisson"] = {k: pois(panel(PRIV, [k]), "y ~ inside") for k in TESTED}

# ---- H2 distance decay outside the extent ----
po = pan[pan.inside == 0].copy()
nout = po.groupby("name").y.sum()
H2N = [k for k in TESTED if nout.get(k, 0) >= 5]
po = po[po.name.isin(H2N)]
R["H2"] = {"pooled": pois(po, "y ~ C(name) + dist" if len(H2N) > 1 else "y ~ dist", key="dist"), "names": H2N,
           "excluded": [k for k in TESTED if k not in H2N]}
R["H2"]["per_name"] = {k: pois(po[po.name == k], "y ~ dist", key="dist") for k in H2N}
allp = PRIV[PRIV.kingdom.isin(KING)]
R["H2"]["within50_pc"] = 100 * float((allp.d_main_km <= 50).mean())
R["H2"]["med_out_km"] = float(allp[allp.in_main == 0].d_main_km.median())
R["H2"]["n_out"] = int((allp.in_main == 0).sum())
# distance bands for the figure: features per million residents by band of distance from the extent (tested names pooled)
bands = [(-1, 0), (0, 25), (25, 50), (50, 100), (100, 200), (200, 400), (400, 2000)]
bt = []
for a, b_ in bands:
    sel = (pan.dist * 100 > a) & (pan.dist * 100 <= b_) if a >= 0 else (pan.inside == 1)
    bt.append({"band": "inside" if a < 0 else f"{a} to {b_} km", "features": int(pan.y[sel].sum()), "pop_m": float(pan["pop"][sel].sum() / 1e6),
               "rate": float(pan.y[sel].sum() / (pan["pop"][sel].sum() / 1e6))})
R["H2"]["bands"] = bt

# ---- H3 public vs private ----
PP = pd.concat([PRIV.assign(public=0), PUB.assign(public=1)])
PP = PP[PP.kingdom.isin(KING)]
t3 = PP[PP.kingdom.isin(TESTED)]
lg = smf.logit("in_main ~ public + C(kingdom)", t3).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(t3.brand)[0]})
lpm = smf.ols("in_main ~ public + C(kingdom)", PP).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(PP.brand)[0]})
b, se = lg.params["public"], lg.bse["public"]
R["H3"] = {"or": float(np.exp(b)), "or_lo": float(np.exp(b - 1.96 * se)), "or_hi": float(np.exp(b + 1.96 * se)), "p": float(lg.pvalues["public"]),
           "n": int(len(t3)), "n_public": int(t3.public.sum()), "brands": int(t3.brand.nunique()),
           "lpm_pp": 100 * float(lpm.params["public"]), "lpm_lo": 100 * float(lpm.conf_int().loc["public", 0]), "lpm_hi": 100 * float(lpm.conf_int().loc["public", 1]),
           "lpm_p": float(lpm.pvalues["public"]), "lpm_n": int(len(PP)),
           "share_private": 100 * float(t3[t3.public == 0].in_main.mean()), "share_public": 100 * float(t3[t3.public == 1].in_main.mean()),
           "share_private_all": 100 * float(PP[PP.public == 0].in_main.mean()), "share_public_all": 100 * float(PP[PP.public == 1].in_main.mean())}

# ---- H4 which names travelled furthest (exploratory) ----
R["H4"] = {"rank_share_out": sorted([k for k in TESTED], key=lambda k: names[k]["private"]["share_in"]),
           "rank_med_core": sorted([k for k in TESTED], key=lambda k: -names[k]["private"]["med_core_km"])}

# ---- P1 wrong extents ----
ov = {}
for k in NAMES:
    for j_ in NAMES:
        ov[(k, j_)] = bool(((U[f"in_{k}_main"] == 1) & (U[f"in_{j_}_main"] == 1)).any())
rows = []; plist = []
cnt = PRIV.groupby(["kingdom", "unit"]).size()
for k in TESTED:
    for j_ in NAMES:
        if j_ == k or ov[(k, j_)]:
            continue
        d = pd.DataFrame({"unit": U.code, "lad": U.lad, "pop": U["pop"], "inside": U[f"in_{j_}_main"], "name": k, "pl": j_})
        d["y"] = d.unit.map(cnt.get(k)).fillna(0)
        d = d[U[f"in_{k}_main"].values == 0]          # outside the name's own extent: is a wrong extent favoured?
        rows.append(d)
        G = PRIV[PRIV.kingdom == k]
        n_in = int(G[f"in_{j_}"].sum()); pin = U.loc[U[f"in_{j_}_main"] == 1, "pop"].sum()
        plist.append({"name": k, "wrong": j_, "n_in": n_in, "pop_share": 100 * pin / POPT})
PD = pd.concat(rows, ignore_index=True)
PD["np"] = PD.name + "|" + PD.pl
R["P1"] = pois(PD, "y ~ C(np) + inside")
R["P1"]["pairs"] = len(plist)
R["P1"]["n_in_total"] = int(sum(p["n_in"] for p in plist))
R["P1"]["list"] = plist

# ---- robustness (pooled tested names; Wessex alone alongside) ----
rob = []
ALLN = [k for k in KING if (PRIV.kingdom == k).any()]
def add(group, label, G, ver="main", base="pop", drop_units=None):
    o = {"group": group, "label": label}
    for tag, nm in (("pt", TESTED), ("pa", ALLN), ("wx", ["Wessex"])):
        df = panel(G, nm, ver=ver, drop_units=drop_units)
        if df.y.sum() == 0:
            continue
        r_ = pois(df, "y ~ C(name) + inside" if len(nm) > 1 else "y ~ inside", offset="pop" if base == "pop" else "area")
        o.update({f"{tag}_{a}": r_[a] for a in ("irr", "lo", "hi", "p", "n_features")})
    rob.append(o)
add("Main", "Main specification", PRIV)
add("Extent", "R1 wide extents", PRIV, ver="wide")
add("Extent", "R2 core extents", PRIV, ver="core")
Gb = PRIV.sort_values("fid").drop_duplicates(["kingdom", "brand"])
add("Counting", "R3 each brand once", Gb)
for rg in sorted(U.region.unique()):
    add("Leave one region out", f"R4 without {rg}", PRIV[PRIV.region != rg], drop_units=(U.region == rg).values)
add("Names", "R5 without place-derived and ambiguous names", PRIV[(PRIV.place_derived == 0) & (PRIV.ambiguous == 0)])
add("Baseline", "R6 per square kilometre, not per resident", PRIV, base="area")
bc = PRIV.groupby(["kingdom", "brand"]).fid.transform("size")
add("Counting", "R7 without chains (brands with more than 3 features)", PRIV[bc <= 3])
add("Classes", "R8 private names plus streets", pd.concat([PRIV, STR]))
SITE = F[(F.cls == "SITE") & F.kingdom.isin(NAMES)]
add("Classes", "R10 private names plus named buildings and sites (exploratory)", pd.concat([PRIV, SITE]))
add("Classes", "Public bodies only (H3 comparison)", PUB)
RB = pd.DataFrame(rob)
RB.to_csv(f"{DATA}/robustness.csv", index=False, float_format="%.4g")
R["robust"] = rob
chk = RB[RB.group != "Main"]
chk = chk[~chk.label.str.startswith("Public") & ~chk.label.str.contains("exploratory")]
R["robust_range"] = {"n_checks": int(len(chk)), "pt_sig": int((chk.pt_lo > 1).sum()), "pt_min": float(chk.pt_irr.min()), "pt_max": float(chk.pt_irr.max()),
                     "pa_sig": int((chk.pa_lo > 1).sum()), "pa_min": float(chk.pa_irr.min()), "pa_max": float(chk.pa_irr.max()),
                     "wx_sig": int((chk.wx_lo > 1).sum()), "wx_min": float(chk.wx_irr.min()), "wx_max": float(chk.wx_irr.max())}
# R9: East Anglia with Anglia / Anglian without East
AV = F[(F.cls == "PRIVATE") & (F.kingdom.isin(["East Anglia", "Anglia (no East)"]))].copy()
AV["in_main"] = AV.unit.map(U.set_index("code")["in_East Anglia_main"]).astype(int)
AV["kingdom"] = "East Anglia"
R["R9_east_anglia_plus_anglia"] = per_name(AV, "East Anglia")
AW = AV.copy(); AW["in_main"] = AW.unit.map(U.set_index("code")["in_East Anglia_wide"]).astype(int)
R["R9_wide"] = per_name(AW, "East Anglia")
R["EA_wide"] = per_name(PRIV[PRIV.kingdom == "East Anglia"].assign(in_main=lambda d: d.in_wide), "East Anglia")

# ---- headline helpers ----
W = names["Wessex"]["private"]
R["x"] = {"wessex_rr": W["rr"], "wessex_share": W["share_in"], "wessex_pop": W["base_share"]}
for k in TESTED:
    R["x"][f"{k.lower()}_rr"] = names[k]["private"]["rr"]
jsave(R, f"{DATA}/results.json", indent=1)
print(pd.DataFrame(tab)[["kingdom", "private", "brands", "in", "share_in", "pop_share", "rr", "rr_lo", "rr_hi", "public", "public_share_in", "streets", "street_share_in"]].round(2).to_string())
print("H1", {k: round(v, 3) if isinstance(v, float) else v for k, v in R["H1"]["pooled"].items()})
print("H1 all", {k: round(v, 3) if isinstance(v, float) else v for k, v in R["H1"]["pooled_all"].items()})
print("H2", {k: round(v, 3) if isinstance(v, float) else v for k, v in R["H2"]["pooled"].items()}, R["H2"]["within50_pc"], R["H2"]["med_out_km"])
print({k: round(v["irr"], 3) for k, v in R["H2"]["per_name"].items()})
print(pd.DataFrame(bt))
print("H3", {k: round(v, 3) if isinstance(v, float) else v for k, v in R["H3"].items()})
print("P1", {k: round(v, 3) if isinstance(v, float) else v for k, v in R["P1"].items() if k != "list"})
print(RB[["label", "pt_irr", "pt_lo", "pt_hi", "pt_n_features", "pa_irr", "pa_lo", "pa_hi", "wx_irr", "wx_lo", "wx_hi"]].round(2).to_string())
print("R9", {k: round(v, 2) if isinstance(v, float) else v for k, v in R["R9_east_anglia_plus_anglia"].items()})
