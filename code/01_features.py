"""Step 1: curate kingdom-name features from the shared OpenStreetMap names file.
Whole-word matching of each kingdom name (and its adjective) in the feature name; a representative point for every
geometry; classification into PRIVATE / PUBLIC / STREET / SITE / OTHER from OSM tags, then name keywords, then the
hand decisions in code/overrides.csv (every untagged and every ambiguous case read by eye); duplicates merged (same
normalised name within 250 m; streets within 1 km). Output: data/features.csv (one row per merged feature and name),
data/osm_matches.csv (every matched raw OSM object with its class, before merging)."""
import csv, sys
import numpy as np, pandas as pd
from shapely import wkt as swkt
from common import *

csv.field_size_limit(sys.maxsize)
st = lambda s: s.strip().strip('"')
rows = []
with open(f"{RAW}/osm_names_rose_kingdom.tsv", encoding="utf-8") as f:
    head = f.readline().rstrip("\n").split("\t")
    for line in f:
        r = line.rstrip("\n").split("\t")
        if len(r) != 9:
            continue
        rows.append(r)
n_raw = len(rows)

# ---- tags and classes ----
PUB_AMEN = {"police", "fire_station", "ambulance_station", "school", "college", "university", "hospital", "clinic", "doctors",
            "library", "townhall", "courthouse", "prison", "dentist_nhs"}
OTHER_AMEN = {"parking", "parking_entrance", "parking_space", "bench", "waste_basket", "post_box", "telephone", "bicycle_parking",
              "toilets", "shelter", "recycling", "fountain", "grit_bin", "vending_machine", "charging_station", "bus_station",
              "taxi", "loading_dock", "waste_disposal", "drinking_water", "letter_box", "motorcycle_parking", "clock",
              "bicycle_rental", "compressed_air", "atm", "dog_toilet", "post_depot", "ferry_terminal", "car_wash_self"}
OPEN_LEIS = {"park", "playground", "garden", "nature_reserve", "common", "recreation_ground", "picnic_table", "dog_park",
             "slipway", "outdoor_seating", "firepit", "bandstand"}
ROAD = {"residential", "service", "tertiary", "secondary", "primary", "trunk", "unclassified", "living_street", "pedestrian",
        "motorway", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "motorway_link", "road", "busway"}
PATHS = {"footway", "cycleway", "path", "track", "steps", "bridleway", "corridor", "construction", "proposed"}
STOP = {"bus_stop", "platform", "stop", "street_lamp", "crossing", "traffic_signals", "milestone", "give_way", "turning_circle",
        "elevator", "emergency_access_point", "speed_camera", "stop_position"}
SUFFIX = r"(?:road|rd|street|st|way|close|drive|avenue|ave|lane|gardens|crescent|place|grove|walk|court|mews|rise|terrace)"
K_OTHER = [r"\bbus\b", r"=>", r"<->", r"greater anglia:", r"\b(?:s|n|e|w|se|sw|ne|nw)-bound\b", r"\badj\b", r"\bopp\b",
           r"\bmain line\b", r"\bline\b", r"substation", r"transformer", r"pumping station", r"pump station", r"sewage",
           r"\bstw\b", r"telephone exchange", r"grid connection", r"gride connection", r"converter station", r"\bshaft\b",
           r"signalling", r"milepost", r"village sign", r"westland wessex", r"ford anglia", r"battle of", r"\bboundary\b",
           r"\bsolar\b", r"\bbooster\b", r"treatment (?:plant|works|compound)", r"\bwind farm\b", r"\bone\b.*connection",
           r"\bthree\b", r"\btwo\b.*(?:substation|connection)", r"\bcable\b", r"\btrail\b", r"ridge ?way", r"greenway",
           r"\bpole\b", r"capital of east anglia", r"\bstatue\b", r"memorial", r"\bsign\b", r"refinery", r"\bmasterplan\b",
           r"\bphase \d", r"demolition", r"\bformer\b", r"^parts of lindsey$", r"\bregion$", r"\bloch\b", r"information$",
           r"\bwood\b$", r"\bfarm\b$", r"\bfields?\b$", r"\bmount\b$", r"\bfold\b$", r"allotments", r"play area", r"\bheliport|helipad"]
K_PUBLIC = [r"\bpolice\b", r"constabulary", r"probation", r"\bnhs\b", r"\bhospital\b", r"ambulance", r"\bfire\b", r"\bcouncil\b",
            r"\bschool\b", r"\bacademy\b", r"\bcollege\b", r"universit", r"\bcadets?\b", r"regiment", r"\barmy\b", r"\breserve\b",
            r"yeomanry", r"battalion", r"officers", r"air squadron", r"(?:wessex|northumbrian?|anglian?) water", r"national landscape", r"\bdowns\b", r"\blibrary\b",
            r"health and social care", r"blood centre", r"urgent care", r"^hms\b", r"\bnursery school\b", r"probation trust", r"\bbattery\b",
            r"field hospital", r"\bmuseum of the\b.*regiment", r"regiment museum", r"\bhq\b", r"\bvolunteers\b", r"immunis",
            r"community eye service", r"training camp", r"\bdistrict\b", r"forces"]
K_PRIVATE = [r"\bltd\b", r"limited", r"\bplc\b", r"hotel", r"\binn\b", r"guest ?house", r"\bb ?& ?b\b", r"\bclub\b", r"\bfc\b",
             r"\brfc\b", r"society", r"scouts?\b", r"museum", r"archaeology", r"motors", r"\bgarage\b", r"\bhomes\b", r"marina",
             r"\bmc\b", r"cuisine", r"tandoori", r"\bclinic\b", r"osteopath", r"chiropract", r"\bdental\b", r"\bbank\b", r"auction",
             r"\bcleaners\b", r"\blifts\b", r"packaging", r"envelopes", r"\btimber\b", r"\bprint", r"\bevents\b", r"labels",
             r"\bsecurities\b", r"\bretail\b$", r"gaming", r"radio", r"karting", r"snooker", r"camping", r"caravan", r"\bmotel\b",
             r"roofing", r"forklift", r"haulage", r"decorators", r"chemicals", r"\bsalt\b", r"\bproduce\b", r"\bsalads\b",
             r"\beggs\b", r"\boptics\b", r"radiators", r"recovery", r"\blead\b", r"\bpress\b", r"components", r"landscapes",
             r"wood burner", r"airflow", r"handling", r"forwarding", r"cargo", r"camper", r"energy", r"sportswear|schoolwear",
             r"sporting", r"flight cent", r"home improvements", r"wealth management", r"fine foods", r"helicopters",
             r"computer repairs", r"car hire", r"blow mouldings", r"nursury", r"gliding", r"amateur radio", r"\bsuite\b",
             r"heartbeat", r"science centre", r"bike hub", r"animal health", r"test equipment", r"foot clinic", r"therapy centre",
             r"associated industries", r"\bgas\b", r"trucks", r"real estate", r"\bblind society\b", r"community action",
             r"library of things", r"\bdriveability\b", r"installation systems", r"archives", r"apareline", r"pumping services",
             r"garden products", r"radiotelephones", r"image print", r"volvo trucks", r"railway museum", r"transport museum",
             r"\bguesthouse\b", r"\bsquash\b", r"cave club", r"light haulage", r"sweet & drink|sweet and drink", r"security services",
             r"\bsports\b", r"\bfarm$"]
K_SITE = [r"\bhouse\b", r"\bcourt\b", r"\blodge\b", r"\bbuildings?\b", r"\bcentre\b", r"\bcenter\b", r"business park", r"\bpark\b",
          r"industrial", r"trade centre", r"\bchambers\b", r"\bhall\b", r"\bhalls\b", r"apartments", r"\bunits\b", r"\btower\b",
          r"\bplace\b", r"\bgate\b", r"\bquay\b", r"\bsquare\b", r"\bcomplex\b", r"\boval\b", r"\bestate\b", r"\bcastle\b",
          r"\bwharf\b", r"\bmill\b", r"retail park", r"\bshops\b", r"\bground\b"]


def tags(r):
    return {k: st(v) for k, v in zip(["shop", "amenity", "office", "craft", "leisure", "highway"], r[2:8]) if st(v)}


def classify(name, t, gtype):
    n = name.lower()
    hw = t.get("highway")
    if hw:
        if hw in STOP: return "OTHER", "transport stop"
        if hw in ROAD: return "STREET", "street"
        if hw in PATHS: return "OTHER", "path or track"
        return "OTHER", f"highway={hw}"
    am, of, le = t.get("amenity"), t.get("office"), t.get("leisure")
    if am in OTHER_AMEN: return "OTHER", f"amenity={am}"
    if le in OPEN_LEIS: return "OTHER", "open space"
    if any(re.search(p, n) for p in K_OTHER):
        return "OTHER", "infrastructure, route or sign"
    KW = r"\b(?:" + "|".join(PAT.values()) + r"|anglian?)\b\s+" + SUFFIX + r"\b"
    if re.search(KW + r"\s*\S", n) and not re.search(r"\bcourt (?:school|hotel)", n):
        return "OTHER", "named after a street"
    if re.fullmatch(r"(?:the )?" + KW, n) and not (t.get("shop") or am or of or t.get("craft") or le):
        return "SITE", "named building, estate or site"
    sc = t.get("shop") or t.get("craft")
    if sc and not re.search(r"universit|(?:wessex|northumbrian?|anglian?) water|police|council", n):
        return "PRIVATE", "tagged business or venue"
    if am in PUB_AMEN or of in ("government", "educational_institution", "police", "nhs") or any(re.search(p, n) for p in K_PUBLIC):
        if re.search(r"nuffield|spire|\bbmi\b|ramsay|\bltd\b|limited|private|aviation medical", n):
            return "PRIVATE", "private health"
        return "PUBLIC", "public body"
    if t.get("shop") or am or of or t.get("craft") or le:
        return "PRIVATE", "tagged business or venue"
    if any(re.search(p, n) for p in K_PRIVATE):
        return "PRIVATE", "named business or society"
    if any(re.search(p, n) for p in K_SITE):
        return "SITE", "named building, estate or site"
    if gtype in ("POLYGON", "MULTIPOLYGON"):
        return "SITE", "named building or area"
    return "REVIEW", "unclassified"


recs = []
for r in rows:
    name = st(r[1])
    hits = [k for k in NAMES if re.search(r"\b(?:" + PAT[k] + r")\b", name, re.I)]
    anglia = bool(re.search(r"\b" + ANGLIA_VAR + r"\b", name, re.I)) and "East Anglia" not in hits
    if not hits and not anglia:
        continue
    w = r[8].strip().strip('"')
    w = re.sub(r"\^\^.*$", "", w).strip('"')
    try:
        g = swkt.loads(w)
        p = g.representative_point() if g.geom_type != "Point" else g
        if g.geom_type == "GeometryCollection":
            p = g.centroid
        lon, lat = p.x, p.y
    except Exception as e:
        print("bad wkt", r[0], str(e)[:80]); continue
    gt = w.split("(")[0].strip().upper()
    t = tags(r)
    for k in hits + (["Anglia (no East)"] if anglia else []):
        cls, sub = classify(name, t, gt)
        recs.append(dict(osm=st(r[0]).strip("<>"), name=name, kingdom=k, lat=round(lat, 6), lon=round(lon, 6), gtype=gt,
                         tags=";".join(f"{a}={b}" for a, b in t.items()), cls=cls, sub=sub))
D = pd.DataFrame(recs)
print("raw rows", n_raw, "matched objects x names", len(D))

# ---- hand decisions (regex on the lower-case name) and rule-based flags ----
OV = pd.read_csv(os.path.join(ROOT, "code", "overrides.csv"), comment="#", dtype=str).fillna("")
D["place_derived"] = 0; D["ambiguous"] = 0; D["note"] = ""; D["hand"] = 0
PLACE = {"Elmet": r"sherburn.{0,4}in.{0,4}elmet|barwick.{0,4}in.{0,4}elmet|scholes \(elmet\)|elmete",
         "Lindsey": r"kirton.{0,4}(?:in.)?lindsey|(?:east|west|north|north east) lindsey|lindsey marsh|lincoln (?:&|and) lindsey",
         "Strathclyde": r"strathclyde (?:country )?park|strathclyde business (?:park|cent)|glasgow strathclyde"}
NOTK = {"Lindsey": [(52.060, 0.868), (52.262, -1.667)]}       # Lindsey (Suffolk) and Norton Lindsey (Warwickshire): 3 km
for i, r in D.iterrows():
    n = r["name"].lower()
    if r.kingdom in PLACE and re.search(PLACE[r.kingdom], n):
        D.at[i, "place_derived"] = 1
    if r.kingdom in NOTK and any(km(r.lat, r.lon, a, b) <= 3 for a, b in NOTK[r.kingdom]):
        D.at[i, "cls"] = "OTHER"; D.at[i, "sub"] = "not the kingdom (Suffolk or Warwickshire Lindsey)"; D.at[i, "hand"] = 1
    for o in OV.itertuples():
        if (o.kingdom in ("*", r.kingdom)) and re.fullmatch(o.pattern, n):
            D.at[i, "hand"] = 1
            if o.cls: D.at[i, "cls"] = o.cls; D.at[i, "sub"] = o.sub
            if o.flag == "P": D.at[i, "place_derived"] = 1
            if o.flag == "A": D.at[i, "ambiguous"] = 1
            if o.flag == "N": D.at[i, "cls"] = "OTHER"; D.at[i, "sub"] = "not the kingdom name"
            D.at[i, "note"] = o.note
            break
left = D[D.cls == "REVIEW"]
if len(left):
    print("STILL TO REVIEW:", len(left)); print(left[["kingdom", "name", "gtype", "tags"]].drop_duplicates("name").to_string())
D.to_csv(f"{DATA}/osm_matches.csv", index=False)

# ---- merge duplicates: same normalised name and kingdom within 250 m (streets 1 km) ----
D["nn"] = D["name"].map(norm)
out = []
for (k, nn), g in D.groupby(["kingdom", "nn"], sort=False):
    idx = list(g.index); par = {i: i for i in idx}
    def fnd(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    la, lo = g.lat.values, g.lon.values
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            lim = 1.0 if "STREET" in (g.cls.iloc[a], g.cls.iloc[b]) else 0.25
            if km(la[a], lo[a], la[b], lo[b]) <= lim:
                par[fnd(idx[a])] = fnd(idx[b])
    grp = {}
    for i in idx:
        grp.setdefault(fnd(i), []).append(i)
    for members in grp.values():
        m = D.loc[members]
        # class priority: a tagged business beats an untagged outline of the same thing
        pri = {"PRIVATE": 0, "PUBLIC": 1, "STREET": 2, "SITE": 3, "OTHER": 4, "REVIEW": 5}
        best = m.iloc[np.argsort([pri[c] for c in m.cls], kind="stable")[0]]
        out.append(dict(fid=None, kingdom=k, name=best["name"], brand=nn, cls=best.cls, sub=best["sub"], lat=m.lat.mean().round(6),
                        lon=m.lon.mean().round(6), n_osm=len(m), osm=best.osm, tags=best.tags, place_derived=int(m.place_derived.max()),
                        ambiguous=int(m.ambiguous.max()), hand=int(m.hand.max()),
                        note=best.note))
BRANDS = [(r"children.?s hospice|\beach\b", "east anglias childrens hospices"), (r"(wessex|northumbrian?|anglian?) water", None),
          (r"anglia ruskin", "anglia ruskin university"), (r"strathclyde universit|university of strathclyde", "university of strathclyde"),
          (r"northumbria universit", "northumbria university"), (r"university of east anglia", "university of east anglia"),
          (r"west mercia (police|constabulary)", "west mercia police"), (r"northumbria police", "northumbria police"),
          (r"strathclyde police", "strathclyde police"), (r"mercian regiment", "mercian regiment"), (r"royal anglian regiment", "royal anglian regiment"),
          (r"college of west anglia", "college of west anglia"), (r"wessex pharmac", "wessex pharmacy"), (r"wessex photo", "wessex photo"),
          (r"wessex kia|kia motors wessex", "wessex kia"), (r"wessex garages", "wessex garages"), (r"wessex archaeology", "wessex archaeology"),
          (r"wessex lifts", "wessex lifts"), (r"wessex cancer trust", "wessex cancer trust"), (r"king of wessex", "king of wessex"),
          (r"anglian home improvements", "anglian home improvements"), (r"lindsey age uk", "lindsey age uk"),
          (r"north lindsey college", "north lindsey college"), (r"west lindsey district council", "west lindsey district council"),
          (r"lindsey marsh drainage", "lindsey marsh drainage board"), (r"lincoln (&|and) lindsey blind", "lincoln and lindsey blind society"),
          (r"northumbria army cadet", "northumbria army cadet force"), (r"strathclyde business (park|cent)", "strathclyde business park"),
          (r"strathclyde park", "strathclyde park"), (r"lindsey lodge", "lindsey lodge hospice"), (r"west mercia fork", "west mercia fork trucks"),
          (r"wessex auction", "wessex auction rooms"), (r"northumbria gliding", "northumbria gliding club"), (r"taste of northumbria", "taste of northumbria"),
          (r"mercia marina", "mercia marina"), (r"earl of mercia", "earl of mercia"), (r"wessex pictures", "wessex pictures"),
          (r"east anglian? (railway|transport) museum", None), (r"west mercia probation", "west mercia probation")]


def brand(name):
    n = norm(re.sub(r"\(.*?\)", " ", name))
    for p_, b_ in BRANDS:
        m_ = re.search(p_, n)
        if m_:
            return b_ or m_.group(0)
    n = re.sub(r"^the ", "", n)
    return n


F = pd.DataFrame(out)
F["brand"] = F["name"].map(brand)
F = F.sort_values(["kingdom", "cls", "name"]).reset_index(drop=True)
F["fid"] = np.arange(1, len(F) + 1)
F.to_csv(f"{DATA}/features.csv", index=False)
print(pd.crosstab(F.kingdom, F.cls, margins=True).to_string())
