"""Step 7: the paper. Fills code/paper_template.tex from data/results.json, data/name_table.csv, data/robustness.csv and
data/features_geo.csv, adds the tables and compiles with xelatex. Output: release/paper/Hotham_Lost_Kingdoms.pdf and .tex
beside the f_*.pdf figures. The DOI stays a https://doi.org/10.5281/zenodo.24104340 placeholder unless DOI is set: DOI=10.5281/zenodo.N python3 code/07_paper.py"""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(REL, "paper"); NAME = "Hotham_Lost_Kingdoms"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    for k in ("f0", "f1", "f2", "f3"):
        if f == k: return f"{float(v):.{k[1]}f}".replace("-", "$-$")
    return tex(str(v))


def ci(x, lo, hi, d=1):
    f = lambda v: "n/a" if v is None or v != v else ("$\\infty$" if v == float("inf") else f"{v:.{d}f}")
    return f"{f(x)} [{f(lo)}, {f(hi)}]"


F = R["flow"]
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{From raw rows to the analysis sample.}\\label{tab:flow}\\begin{tabular}{lr}\\toprule Step & Number\\\\\\midrule\n"
      f"OpenStreetMap rows with a county, rose or kingdom word in the name & {F['raw_rows']:,}\\\\\n"
      f"Objects matching a kingdom name as a whole word & {F['matched_pairs']:,}\\\\\n"
      f"Named features after merging duplicates (twelve names) & {F['features']:,}\\\\\n"
      f"\\quad businesses and voluntary bodies (private) & {F['private']:,}\\\\\n"
      f"\\quad public bodies & {F['public']:,}\\\\\n"
      f"\\quad streets & {F['street']:,}\\\\\n"
      f"\\quad named buildings and sites & {F['site']:,}\\\\\n"
      f"\\quad other (stops, routes, infrastructure, signs; not the kingdom) & {F['other']:,}\\\\\\midrule\n"
      f"Private features, eleven kingdom names (East Anglia apart) & {F['private_kingdoms']:,}\\\\\n"
      f"\\quad distinct brands & {F['private_brands']:,}\\\\\n"
      f"\\quad place-derived (kept; dropped in R5) & {F['place_derived_private']:,}\\\\\n"
      f"Objects changed or flagged by hand & {F['hand_rows']:,} ({F['hand_pc']:.1f}\\%)\\\\\n"
      f"Areal units (MSOA, Scottish councils, NI districts) & {R['population']['units']:,}\\\\\\bottomrule\\end{{tabular}}\\end{{table}}")
rows = ""
for k in ["Wessex", "Mercia", "Northumbria", "Elmet", "Lindsey", "Strathclyde", "Dalriada", "Rheged", "Bernicia", "Dumnonia", "Deira", "East Anglia"]:
    o = R["names"][k]; p = o["private"]
    if k == "East Anglia": rows += "\\midrule\n"
    sh = ci(p["share_in"], p["share_lo"], p["share_hi"], 0) if p["n"] else "n/a"
    rr = (ci(p["rr"], p["rr_lo"], p["rr_hi"], 1) if not p.get("zero_cell") else f"$\\geq${p['rr_lo']:.0f}" if p["n_in"] else "n/a") if p["n"] and k in R["tested"] else ""
    pub = f"{o['public']['n']} ({o['public']['share_in']:.0f}\\%)" if o["public"]["n"] else "0"
    stt = f"{o['street']['n']} ({o['street']['share_in']:.0f}\\%)" if o["street"]["n"] else "0"
    rows += f"{'\\textbf{' + k + '}' if k in R['tested'] else k} & {p['n']} & {p['brands']} & {p['n_in']} & {sh} & {p['base_share']:.1f} & {rr} & {pub} & {stt}\\\\\n"
TN = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Kingdom names: businesses and voluntary bodies (private) inside the main extent, the share of UK residents there, and the rate ratio per resident inside vs outside (brand bootstrap 95\\% CI; for names with every feature inside, the Wilson lower bound). Public bodies and streets: number and \\% inside. Tested names in bold.}\\label{tab:names}"
      "\\setlength{\\tabcolsep}{3.5pt}\\begin{tabular}{lrrrlrlll}\\toprule Name & Private & Brands & Inside & \\% inside [CI] & \\% residents & Rate ratio [CI] & Public & Streets\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
RB = pd.DataFrame(R["robust"])  # unrounded values (the CSV is rounded to 4 significant figures)
rows = ""; grp = None
for _, x in RB.iterrows():
    if x.group != grp:
        rows += f"\\multicolumn{{4}}{{l}}{{\\textit{{{tex(x.group)}}}}}\\\\\n"; grp = x.group
    wx = ci(x.wx_irr, x.wx_lo, x.wx_hi) if x.wx_irr == x.wx_irr else ""
    rows += f"\\quad {tex(x.label)} & {int(x.pt_n_features)} & {ci(x.pt_irr, x.pt_lo, x.pt_hi)} & {ci(x.pa_irr, x.pa_lo, x.pa_hi)} & {wx}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{Robustness: rate ratio inside vs outside per resident (Poisson with name fixed effects and a log-population offset, R6 log-area; 95\\% CI clustered by local authority) for the three tested names pooled, all eleven kingdom names pooled, and Wessex alone. N = features in the tested-names model.}\\label{tab:robust}"
      "\\setlength{\\tabcolsep}{3pt}\\begin{tabular}{p{6.2cm}rlll}\\toprule Check & N & Tested names & All names & Wessex\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for k in NAMES:
    e = EXT[k]
    f = lambda toks: ", ".join(t.split(":", 1)[1] for t in toks if not t.startswith("+"))
    rows += f"{k} & {tex(f(e['core']))} & {tex(f(e['main']))} & {tex('main + ' + f(e['wide']))}\\\\\n"
TE = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{Approximate kingdom extents as unions of modern areas (ceremonial counties, 2021 districts, Scottish council areas, NI districts), fixed in the analysis plan. Main extents follow \\citet{hill1981} and \\citet{yorke1990}.}\\label{tab:ext}"
      "\\begin{tabular}{p{1.7cm}p{3.4cm}p{6.2cm}p{3.6cm}}\\toprule Name & Core & Main (around 800) & Wide\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
G = pd.read_csv(f"{DATA}/features_geo.csv")
o = G[G.cls.isin(["PRIVATE", "PUBLIC"]) & G.kingdom.isin(NAMES) & (G.in_main == 0)].sort_values(["kingdom", "cls", "d_main_km"])
rows = "".join(f"{tex(r.kingdom)} & {tex(r['name'])} & {'public' if r.cls == 'PUBLIC' else 'private'} & {tex(r.district)} & {r.d_main_km:.0f}\\\\\n" for _, r in o.iterrows())
TO = ("\\begin{longtable}{p{2cm}p{6.6cm}lp{3.2cm}r}\\caption{Every business, voluntary body and public body outside its kingdom's main extent, with distance from the extent (km).}\\label{tab:out}\\\\\\toprule Name & Feature & Kind & District & km\\\\\\midrule\\endhead\n"
      + rows + "\\bottomrule\\end{longtable}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO).replace("{{TESTED}}", ", ".join(R["tested"][:-1]) + " and " + R["tested"][-1])
for k, v in (("TABLE_FLOW", TF), ("TABLE_NAMES", TN), ("TABLE_ROBUST", TR), ("TABLE_EXT", TE), ("TABLE_OUT", TO)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24104340", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:5]
for bad in ("DSIT", "DCMS", "pre-registered", "preregistered"):
    assert bad not in t, bad
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or l.startswith("!")][:15])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = txt.split("\nReferences\n")[0]
ab = txt.split("Abstract")[1].split("Keywords")[0]
cites = set(re.findall(r"\\cite[pt]?\{([^}]+)\}", open(os.path.join(OUT, NAME + ".tex")).read()))
keys = {c.strip() for s in cites for c in s.split(",")}
bib = set(re.findall(r"\\bibitem\[[^\]]*\]\{([^}]+)\}", t))
print("uncited:", bib - keys, "missing:", keys - bib, "refs:", len(bib))
print("paper", r.returncode, len(txt.split()), "words total;", len(body.split()), "before references; abstract", len(ab.split()), "words;",
      [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–"))
