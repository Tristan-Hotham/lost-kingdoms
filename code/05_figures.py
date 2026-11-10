"""Step 5: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px), the paper (release/paper/f_*.pdf)
and header.png (1200 x 630). Light paper background; each kingdom name has its own colour (common.COL)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"; DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name(); MONO = "IBM Plex Mono"
PAPER, INK, MUT, RULE, SEA, LAND = "#F6EED8", "#2B2119", "#6E604E", "#D9C9A3", "#F6EED8", "#ECE3CC"
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": MUT, "axes.labelcolor": INK, "xtick.color": MUT,
                     "ytick.color": MUT, "axes.facecolor": PAPER, "figure.facecolor": PAPER, "axes.unicode_minus": False,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
HALO = [pe.withStroke(linewidth=3.2, foreground=PAPER)]
R = jload(f"{DATA}/results.json")
F = pd.read_csv(f"{DATA}/features_geo.csv")
T = pd.read_csv(f"{DATA}/name_table.csv")
RB = pd.read_csv(f"{DATA}/robustness.csv")
BLOG, PAPD = f"{REL}/blog", f"{REL}/paper"
for d_ in (BLOG, PAPD):
    os.makedirs(d_, exist_ok=True)
SRC = "Data: OpenStreetMap contributors (ODbL); ONS, NRS and NISRA census populations (OGL v3.0)\nmaps.tristanhotham.com/lost-kingdoms"
BNG = "EPSG:27700"
UK = gpd.read_file(f"{GEO}/lad23_bsc.geojson").to_crs(BNG)
UKD = UK.dissolve()
EX = gpd.read_file(f"{DATA}/extents.geojson").to_crs(BNG)
P = gpd.GeoDataFrame(F, geometry=gpd.points_from_xy(F.lon, F.lat), crs="EPSG:4326").to_crs(BNG)
PRIV = P[(P.cls == "PRIVATE") & P.kingdom.isin(NAMES)]
ORDER = ["Wessex", "Mercia", "Northumbria", "East Anglia", "Elmet", "Lindsey", "Strathclyde", "Dalriada", "Rheged", "Bernicia", "Dumnonia", "Deira"]


def out(fig, name, page=True, blog=True, paper=True):
    if paper:
        fig.savefig(f"{PAPD}/f_{name}.pdf", facecolor=fig.get_facecolor())
    fig.savefig(f"{SCR}/{name}.png", dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{SCR}/{name}.png").convert("RGB")
    if page:
        w = min(1500, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=85, optimize=True)
    if blog:
        im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    os.remove(f"{SCR}/{name}.png")


def title(fig, t, sub, y=0.97):
    fig.text(0.04, y, t, family=DISP, fontsize=20, fontweight="bold", color=INK, va="top")
    fig.text(0.04, y - 0.055, sub, fontsize=11.5, color=MUT, va="top")


def foot(fig, y=0.012):
    fig.text(0.04, y, SRC, fontsize=8.5, color=MUT, family=MONO, va="bottom")


def base(ax, xlim=(-80000, 670000), ylim=(-10000, 1000000)):
    ax.set_facecolor(SEA)
    UKD.plot(ax=ax, color=LAND, edgecolor="#B9AC8C", lw=0.4)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")


# ---------- 1. the main map: every private name over its kingdom's approximate extent
fig = plt.figure(figsize=(10, 12.2))
title(fig, "Lost kingdoms on the high street", "Businesses, clubs and societies named after early medieval kingdoms, over the kingdoms'\napproximate extents around AD 800 (shaded). Each dot is one named place in OpenStreetMap.")
ax = fig.add_axes([0.02, 0.05, 0.96, 0.83]); base(ax, xlim=(-60000, 680000), ylim=(0, 1010000))
FILL = ["Wessex", "Mercia", "Lindsey", "Elmet", "Strathclyde", "Dalriada"]
LINE = ["Northumbria", "Rheged", "East Anglia"]
for k in FILL:
    EX[(EX.kingdom == k) & (EX.version == "main")].plot(ax=ax, facecolor=COL[k], alpha=0.13, edgecolor="none", zorder=2)
for k in FILL:
    EX[(EX.kingdom == k) & (EX.version == "main")].boundary.plot(ax=ax, color=COL[k], lw=0.9, zorder=3)
for k in LINE:
    EX[(EX.kingdom == k) & (EX.version == "main")].boundary.plot(ax=ax, color=COL[k], lw=1.4, linestyle="--", zorder=3)
for k in ORDER:
    s = PRIV[PRIV.kingdom == k]
    ax.scatter(s.geometry.x, s.geometry.y, s=26, color=COL[k], edgecolor="white", lw=0.7, zorder=5)
lab = {"Wessex": (60000, 95000, "right"), "Mercia": (135000, 300000, "right"), "Northumbria": (520000, 560000, "left"),
       "Elmet": (585000, 455000, "left"), "Lindsey": (600000, 400000, "left"), "East Anglia": (655000, 230000, "left"),
       "Strathclyde": (110000, 700000, "right"), "Dalriada": (60000, 810000, "right"), "Rheged": (200000, 520000, "right"),
       "Bernicia": (478000, 650000, "left")}
for k, (x, y, ha) in lab.items():
    p = R["names"][k]["private"]
    t = f"{k}\n{p['n_in']} of {p['n']} inside" if p["n"] else k
    ax.text(x, y, t, color=COL[k], fontsize=11, fontweight="bold", ha=ha, va="center", path_effects=HALO, zorder=8, linespacing=1.1)
ax.text(0.99, 0.99, "Shaded or outlined: approximate extents c. 800 (unions of modern\nareas, after Hill 1981 and Yorke 1990); boundaries uncertain.\nDashed: Northumbria, Rheged and East Anglia (also a modern\nregion). Deira, Bernicia and Dumnonia not drawn (0 to 1 places).",
        transform=ax.transAxes, ha="right", va="top", fontsize=9.5, color=MUT, path_effects=HALO)
foot(fig)
out(fig, "map")

# ---------- 2. share inside vs population share, per name
fig = plt.figure(figsize=(10, 7.2))
title(fig, "Most kingdom names stay inside the kingdom", "Share of each name's businesses, clubs and societies inside its kingdom's approximate extent (dot, with 95% interval),\nagainst the share of the UK's residents who live there (grey bar). Only names with 20 or more such places are tested.")
ax = fig.add_axes([0.18, 0.17, 0.66, 0.62])
rows = [k for k in ORDER if R["names"][k]["private"]["n"] > 0]
for i, k in enumerate(rows):
    p = R["names"][k]["private"]; y = len(rows) - 1 - i
    ax.barh(y, p["base_share"], color="#D8CDB3", height=0.55, zorder=1)
    ax.plot([p["share_lo"], p["share_hi"]], [y, y], color=COL[k], lw=2.2, zorder=3)
    ax.scatter([p["share_in"]], [y], s=70 if p["n"] >= MIN_TEST else 40, color=COL[k], edgecolor="white", lw=1, zorder=4,
               marker="o" if p["n"] >= MIN_TEST else "D")
    ax.text(101.5, y, f"{p['n_in']} of {p['n']}", va="center", fontsize=10, color=INK, family=MONO)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows[::-1], fontsize=11.5)
for t_, k in zip(ax.get_yticklabels(), rows[::-1]):
    t_.set_color(COL[k]); t_.set_fontweight("bold" if R["names"][k]["private"]["n"] >= MIN_TEST else "normal")
ax.set_xlim(0, 100); ax.set_xlabel("% inside the kingdom's approximate extent", fontsize=11)
ax.text(101.5, len(rows) - 0.3, "inside", fontsize=9, color=MUT, family=MONO)
fig.text(0.96, 0.075, "Diamonds: fewer than 20 places, described only. East Anglia is also a modern region.", ha="right", fontsize=9.5, color=MUT)
foot(fig)
out(fig, "share")

# ---------- 3. Wessex close-up: where it leaks
fig = plt.figure(figsize=(10, 8.4))
w = R["names"]["Wessex"]["private"]
title(fig, "Where Wessex leaks", f"{w['n_in']} of {w['n']} Wessex businesses, clubs and societies are inside the kingdom's approximate extent. Most of the\nrest are a few kilometres away, across the Avon in Bristol and over the Severn in Cardiff and Newport.")
ax = fig.add_axes([0.02, 0.05, 0.96, 0.80]); base(ax, xlim=(240000, 520000), ylim=(55000, 240000))
EX[(EX.kingdom == "Wessex") & (EX.version == "main")].plot(ax=ax, facecolor=COL["Wessex"], alpha=0.13, edgecolor=COL["Wessex"], lw=1.2, zorder=2)
EX[(EX.kingdom == "Wessex") & (EX.version == "wide")].boundary.plot(ax=ax, color=COL["Wessex"], lw=0.8, linestyle="--", zorder=2)
UK.plot(ax=ax, facecolor="none", edgecolor="#CDBF9F", lw=0.25, zorder=1)
s = PRIV[PRIV.kingdom == "Wessex"]
ax.scatter(s[s.in_main == 1].geometry.x, s[s.in_main == 1].geometry.y, s=34, color=COL["Wessex"], edgecolor="white", lw=0.8, zorder=5)
ax.scatter(s[s.in_main == 0].geometry.x, s[s.in_main == 0].geometry.y, s=46, color="white", edgecolor=COL["Wessex"], lw=1.6, zorder=6)
for nm, x, y, ha in (("Bristol", 352000, 186000, "right"), ("Cardiff", 312000, 166000, "right"), ("Bath", 380000, 158000, "left"),
                     ("Winchester", 448000, 140000, "left"), ("Dorchester", 369000, 80000, "right"), ("Salisbury", 414000, 136000, "left")):
    ax.text(x, y, nm, fontsize=10, color=INK, ha=ha, path_effects=HALO, zorder=9, style="italic")
ax.text(0.02, 0.97, "Filled: inside the extent\nOpen rings: outside\nDashed: wider extent (adds Cornwall,\nthe south east and Bristol)", transform=ax.transAxes, va="top", fontsize=10, color=MUT, path_effects=HALO)
foot(fig)
out(fig, "wessex")

# ---------- 4. private, public and streets
fig = plt.figure(figsize=(10, 6.2))
title(fig, "Businesses, public bodies and streets", "Share inside the kingdom's approximate extent, by kind of name, for the three names with enough places to test.\nStreets, named by councils and developers, travel further than shops and public bodies.")
ax = fig.add_axes([0.08, 0.18, 0.88, 0.58])
kinds = [("private", "Businesses, clubs, societies", "#2B2119"), ("public", "Public bodies", "#8C7B5E"), ("street", "Streets", "#CBBE9F")]
TE = R["tested"]
for j, (kd, lb, c) in enumerate(kinds):
    xs = np.arange(len(TE)) + (j - 1) * 0.26
    v = [R["names"][k][kd]["share_in"] or 0 for k in TE]
    ax.bar(xs, v, width=0.24, color=c, label=lb)
    for x_, v_, k in zip(xs, v, TE):
        n_ = R["names"][k][kd]["n"]
        ax.text(x_, v_ + 1.5, f"{v_:.0f}%\n(n={n_})", ha="center", fontsize=8.6, color=INK, family=MONO)
for i, k in enumerate(TE):
    ax.plot([i - 0.45, i + 0.45], [R["names"][k]["private"]["base_share"]] * 2, color=COL[k], lw=2, ls=(0, (3, 1.5)))
ax.set_xticks(range(len(TE))); ax.set_xticklabels(TE, fontsize=12.5)
for t_, k in zip(ax.get_xticklabels(), TE): t_.set_color(COL[k]); t_.set_fontweight("bold")
ax.set_ylim(0, 118); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_ylabel("% inside the extent")
ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 1.13), fontsize=10.5)
fig.text(0.96, 0.085, "Coloured dashes: share of UK residents living inside each extent.", ha="right", fontsize=9.5, color=MUT)
foot(fig)
out(fig, "types")

# ---------- 5. distance bands
fig = plt.figure(figsize=(10, 5.8))
title(fig, "A cliff at the border", "Kingdom-named businesses, clubs and societies per million residents, by distance from the kingdom's approximate\nextent (Wessex, Mercia and Northumbria pooled). Most of the drop happens at the edge.")
ax = fig.add_axes([0.1, 0.16, 0.86, 0.6])
bt = pd.DataFrame(R["H2"]["bands"])
cols = ["#2B2119"] + ["#9C8656"] * (len(bt) - 1)
ax.bar(range(len(bt)), bt.rate, color=cols, width=0.7)
for i, r in bt.iterrows():
    ax.text(i, r.rate + 0.08, f"{r.rate:.2f}\n({int(r.features)})", ha="center", fontsize=9.5, family=MONO, color=INK)
ax.set_xticks(range(len(bt))); ax.set_xticklabels(bt.band.str.replace(" to ", "-").str.replace("400-2000 km", "over 400 km"), fontsize=10.5)
ax.set_ylabel("per million residents"); ax.set_ylim(0, bt.rate.max() * 1.3)
ax.text(0.99, 0.9, "number of places in brackets", transform=ax.transAxes, ha="right", fontsize=9.5, color=MUT)
foot(fig)
out(fig, "bands")

# ---------- 6. robustness
fig = plt.figure(figsize=(10, 9.4))
title(fig, "Every check", "Rate ratio inside vs outside the extent, per resident (Poisson, name fixed effects, 95% intervals clustered by local\nauthority). Black: the three tested names pooled. Red: Wessex alone. Log scale; 1 = no tracking at all.")
ax = fig.add_axes([0.42, 0.1, 0.55, 0.75])
rb = RB.copy()
ys = np.arange(len(rb))[::-1]
for y, (_, r) in zip(ys, rb.iterrows()):
    ax.plot([r.pt_lo, r.pt_hi], [y + 0.15] * 2, color=INK, lw=1.6); ax.scatter([r.pt_irr], [y + 0.15], color=INK, s=22, zorder=3)
    if r.wx_irr == r.wx_irr:
        ax.plot([r.wx_lo, r.wx_hi], [y - 0.15] * 2, color=COL["Wessex"], lw=1.6); ax.scatter([r.wx_irr], [y - 0.15], color=COL["Wessex"], s=22, zorder=3)
ax.axvline(1, color=MUT, lw=1, ls=(0, (3, 2)))
ax.set_xscale("log"); ax.set_xticks([1, 3, 10, 30, 100, 300, 1000]); ax.set_xticklabels(["1", "3", "10", "30", "100", "300", "1000"])
ax.set_yticks(ys); ax.set_yticklabels([l.replace(" (exploratory)", "*").replace(" (H3 comparison)", "") for l in rb.label], fontsize=9.6)
ax.set_xlim(0.7, 1500); ax.minorticks_off()
fig.text(0.96, 0.02, "* exploratory, not in the plan", fontsize=9, color=MUT, ha="right")
foot(fig, y=0.008)
out(fig, "robust", blog=True)

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100)
fig.patch.set_facecolor(PAPER)
fig.text(0.05, 0.86, "Lost kingdoms", family=DISP, fontsize=50, fontweight="bold", color=INK, va="top")
fig.text(0.05, 0.71, "on the high street", family=DISP, fontsize=36, fontweight="bold", color=COL["Wessex"], va="top")
fig.text(0.05, 0.55, f"Wessex, Mercia and Northumbria businesses\nstay inside the old kingdoms:\n{w['n_in']} of {w['n']} Wessex names are in Wessex,\nwhere {w['base_share']:.0f}% of the UK lives.",
         fontsize=17, color=INK, va="top", linespacing=1.35)
fig.text(0.05, 0.08, "Dr Tristan Hotham · maps.tristanhotham.com/lost-kingdoms", fontsize=12, color=MUT, family=MONO)
ax = fig.add_axes([0.55, 0.02, 0.43, 0.96]); base(ax, xlim=(40000, 660000), ylim=(0, 1000000))
for k in FILL:
    EX[(EX.kingdom == k) & (EX.version == "main")].plot(ax=ax, facecolor=COL[k], alpha=0.15, edgecolor=COL[k], lw=0.7)
for k in ["Northumbria", "Rheged"]:
    EX[(EX.kingdom == k) & (EX.version == "main")].boundary.plot(ax=ax, color=COL[k], lw=1.0, linestyle="--")
for k in ORDER:
    if k == "East Anglia": continue
    s_ = PRIV[PRIV.kingdom == k]
    ax.scatter(s_.geometry.x, s_.geometry.y, s=16, color=COL[k], edgecolor="white", lw=0.5, zorder=5)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER)
plt.close(fig)
assert Image.open(f"{ROOT}/header.png").size == (1200, 630)
print("figures done", sorted(os.listdir(IMG)), sorted(f for f in os.listdir(BLOG) if f.startswith("b_")))
