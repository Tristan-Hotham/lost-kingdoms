"""Reddit collage (r/dataisbeautiful style), light background, 2700 x 2160 px: the UK map of kingdom-named businesses over
approximate kingdom extents, headline numbers, and the share inside each kingdom vs the share of residents.
Run after code/04_site.py:  python3 reddit/collage.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
import pandas as pd, geopandas as gpd
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "IBMPlexMono-Regular.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name()
plt.rcParams.update({"font.family": "Source Serif 4", "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#6E604E", "xtick.color": "#6E604E", "ytick.color": "#6E604E"})
PAPER, INK, MUT, LAND = "#FAF6EC", "#2B2119", "#6E604E", "#ECE3CC"
HALO = [pe.withStroke(linewidth=4, foreground=PAPER)]
R = jload(f"{DATA}/results.json")
BNG = "EPSG:27700"
UK = gpd.read_file(f"{GEO}/lad23_bsc.geojson").to_crs(BNG).dissolve()
EX = gpd.read_file(f"{DATA}/extents.geojson").to_crs(BNG)
F = pd.read_csv(f"{DATA}/features_geo.csv")
P = gpd.GeoDataFrame(F, geometry=gpd.points_from_xy(F.lon, F.lat), crs="EPSG:4326").to_crs(BNG)
P = P[(P.cls == "PRIVATE") & P.kingdom.isin(NAMES) & (P.kingdom != "East Anglia")]
W, M, NO = (R["names"][k]["private"] for k in ("Wessex", "Mercia", "Northumbria"))

fig = plt.figure(figsize=(13.5, 10.8), dpi=200)
fig.patch.set_facecolor(PAPER)
fig.text(0.035, 0.965, "Lost kingdoms on the high street", family=DISP, fontsize=33, fontweight="bold", color=INK, va="top")
fig.text(0.035, 0.905, "UK businesses, clubs and societies named after early medieval kingdoms, over rough outlines of the kingdoms around\nAD 800. Kingdoms that vanished over a thousand years ago still keep their names at home.", fontsize=14, color=MUT, va="top")
ax = fig.add_axes([0.0, 0.07, 0.56, 0.77]); ax.set_facecolor(PAPER)
UK.plot(ax=ax, color=LAND, edgecolor="#B9AC8C", lw=0.4)
FILL = ["Wessex", "Mercia", "Lindsey", "Elmet", "Strathclyde", "Dalriada"]
for k in FILL:
    EX[(EX.kingdom == k) & (EX.version == "main")].plot(ax=ax, facecolor=COL[k], alpha=0.14, edgecolor=COL[k], lw=0.9)
for k in ("Northumbria", "Rheged"):
    EX[(EX.kingdom == k) & (EX.version == "main")].boundary.plot(ax=ax, color=COL[k], lw=1.5, linestyle="--")
for k in NAMES:
    s = P[P.kingdom == k]
    ax.scatter(s[s.in_main == 1].geometry.x, s[s.in_main == 1].geometry.y, s=30, color=COL[k], edgecolor="white", lw=0.7, zorder=5)
    ax.scatter(s[s.in_main == 0].geometry.x, s[s.in_main == 0].geometry.y, s=34, color="white", edgecolor=COL[k], lw=1.6, zorder=6)
ax.set_xlim(-60000, 690000); ax.set_ylim(0, 1000000); ax.set_aspect("equal"); ax.axis("off")
lab = {"Wessex": (50000, 90000, "right"), "Mercia": (130000, 290000, "right"), "Northumbria": (520000, 580000, "left"),
       "Elmet": (575000, 455000, "left"), "Lindsey": (595000, 390000, "left"), "Strathclyde": (110000, 690000, "right"),
       "Dalriada": (60000, 800000, "right"), "Rheged": (232000, 440000, "center")}
for k, (x, y, ha) in lab.items():
    p = R["names"][k]["private"]
    ax.text(x, y, f"{k}\n{p['n_in']} of {p['n']} inside", color=COL[k], fontsize=13, fontweight="bold", ha=ha, va="center", path_effects=HALO, linespacing=1.1, zorder=9)
ax.text(0.70, 0.99, "Filled: inside\nRing: outside\nShaded or dashed:\nrough outline c. 800", transform=ax.transAxes, va="top", fontsize=11.5, color=MUT, path_effects=HALO)
for i, k in enumerate(("Bernicia", "Dumnonia")):
    p = R["names"][k]["private"]
    ax.scatter([0.705], [0.80 - i * 0.035], transform=ax.transAxes, s=30, color=COL[k], edgecolor="white", lw=0.7)
    ax.text(0.725, 0.80 - i * 0.035, f"{k} ({p['n']} feature, no outline)", transform=ax.transAxes, va="center", fontsize=11, color=COL[k], path_effects=HALO)


def card(x0, y0, big, txt, col):
    fig.text(x0, y0, big, family=DISP, fontsize=40, fontweight="bold", color=col, va="top")
    fig.text(x0, y0 - 0.068, txt, fontsize=13, color=INK, va="top", linespacing=1.3)


card(0.58, 0.845, f"{W['n_in']} of {W['n']}", f"Wessex businesses are in Wessex,\nhome to {W['base_share']:.0f}% of UK residents", COL["Wessex"])
card(0.80, 0.845, f"{M['n_in']} of {M['n']}", "Mercia businesses\nare in Mercia", COL["Mercia"])
card(0.58, 0.685, f"{NO['n_in']} of {NO['n']}", "Northumbria businesses\nare in Northumbria", COL["Northumbria"])
card(0.80, 0.685, f"{R['H1']['pooled']['irr']:.0f}x", "as many per resident\ninside as outside", INK)
ax2 = fig.add_axes([0.66, 0.16, 0.29, 0.31]); ax2.set_facecolor(PAPER)
rows = ["Wessex", "Mercia", "Northumbria"]
kinds = [("private", "Businesses, clubs", INK), ("public", "Public bodies", "#8C7B5E"), ("street", "Streets", "#CBBE9F")]
for i, k in enumerate(rows):
    for j, (kd, lb, c) in enumerate(kinds):
        v = R["names"][k][kd]["share_in"]
        ax2.barh(i * 1.0 + (j - 1) * 0.26, v, height=0.24, color=c, label=lb if i == 0 else None)
        ax2.text(v + 1.5, i + (j - 1) * 0.26, f"{v:.0f}%", va="center", fontsize=10.5, color=INK, family="IBM Plex Mono")
    ax2.plot([R["names"][k]["private"]["base_share"]] * 2, [i - 0.45, i + 0.45], color=COL[k], lw=2.2, ls=(0, (3, 1.5)))
ax2.set_yticks(range(3)); ax2.set_yticklabels(rows, fontsize=13)
for t, k in zip(ax2.get_yticklabels(), rows): t.set_color(COL[k]); t.set_fontweight("bold")
ax2.invert_yaxis(); ax2.set_xlim(0, 112); ax2.set_xticks([0, 25, 50, 75, 100]); ax2.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=10.5)
ax2.legend(frameon=False, fontsize=11, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, handlelength=1.2, columnspacing=0.8)
fig.text(0.58, 0.525, "Share inside the kingdom, by kind of name", fontsize=14, fontweight="bold", color=INK)
fig.text(0.58, 0.115, "Dashes: share of UK residents inside each kingdom.\nStreets, named by developers, wander; shops stay home.", fontsize=11, color=MUT, va="top")
fig.text(0.035, 0.022, "Data: OpenStreetMap contributors (ODbL) via QLever; residents: ONS, NRS, NISRA censuses (OGL v3.0). Outlines after Hill (1981) and Yorke (1990).\n"
         "Every match read by hand; East Anglia not mapped; Deira has none. Dr Tristan Hotham · maps.tristanhotham.com/lost-kingdoms",
         fontsize=10, color=MUT, family="IBM Plex Mono", va="bottom")
out = os.path.join(HERE, "lost_kingdoms_collage.png")
fig.savefig(out, dpi=200, facecolor=PAPER)
print(out)
