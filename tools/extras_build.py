#!/usr/bin/env python3
"""Add the optional "aud" (Meta audience) key to a client report's data JSON and carry the "manual" key over
from the page that is already published, so targets / lead quality / notes survive every data refresh.
usage: extras_build.py <data.json> <aud.json|-> <current index.html|-> <out.json> <sum|max>
aud.json: {"age_gender":[rows with age, gender], "placement":[rows with publisher_platform, platform_position]},
rows as returned by Windsor (facebook connector, no "date" field, the report's own Meta accounts and date range),
each with account_currency, campaign, spend, impressions, clicks, actions_lead and
actions_onsite_conversion_messaging_conversation_started_7d. Rows whose campaign is not in the report are dropped.
Last argument: how Meta leads are counted in this report: "sum" = leads + messages (report A), "max" = Meta dedup.
"manual" (edited by hand, never by the refresh): {"target": CPL in SAR, "budget": monthly budget in SAR,
"q": {"YYYY-MM": {"q": qualified, "v": visits, "b": bookings}}, "notes": [{"d": "YYYY-MM-DD", "t": "text"}]}"""
import json, re, sys
n = lambda x: float(x or 0)
rep = json.load(open(sys.argv[1], encoding="utf8"))
mode = sys.argv[5] if len(sys.argv) > 5 else "max"
fx = rep.get("fx", {"SAR": 1, "USD": 3.75, "AED": 1.021})
camps = {c["name"].strip() for c in rep["campaigns"] if c["p"] == "meta"}
def leads(r):
    a, m = n(r.get("actions_lead")), n(r.get("actions_onsite_conversion_messaging_conversation_started_7d"))
    return a + m if mode == "sum" else max(a, m)
def keep(r):
    return n(r.get("spend")) > 0 and ("campaign" not in r or (r.get("campaign") or "").strip() in camps)
def group(rows, keyf):
    out = {}
    for r in rows or []:
        if not keep(r): continue
        g = out.setdefault(keyf(r), {"s": 0, "i": 0, "c": 0, "l": 0})
        g["s"] += n(r.get("spend")) * fx.get(r.get("account_currency") or "SAR", 1)
        g["i"] += n(r.get("impressions")); g["c"] += n(r.get("clicks")); g["l"] += leads(r)
    return [{"k": k, "s": round(v["s"], 2), "i": int(v["i"]), "c": int(v["c"]), "l": int(v["l"])} for k, v in out.items()]
if sys.argv[2] != "-":
    try:
        a = json.load(open(sys.argv[2], encoding="utf8"))
        ag, pl = a.get("age_gender") or [], a.get("placement") or []
        age = sorted(group(ag, lambda r: str(r.get("age") or "Unknown")), key=lambda x: x["k"])
        gen = sorted(group(ag, lambda r: str(r.get("gender") or "unknown").lower()), key=lambda x: -x["l"])
        place = sorted(group(pl, lambda r: str(r.get("publisher_platform") or "") + "|" + str(r.get("platform_position") or "")), key=lambda x: -x["l"])
        cross = [x for x in group(ag, lambda r: str(r.get("age") or "Unknown") + "|" + str(r.get("gender") or "unknown").lower()) if x["l"] > 0 and re.search(r"\d", x["k"]) and x["k"].split("|")[1] in ("male", "female")]
        tot = sum(x["l"] for x in age)
        if tot > 0:
            days = sorted(d for c in rep["campaigns"] if c["p"] == "meta" for d in c["days"])
            aud = {"from": days[0] if days else None, "to": rep.get("end"), "age": age, "gender": gen, "place": place}
            if cross:
                t = max(cross, key=lambda x: x["l"]); ka, kg = t["k"].split("|")
                aud["top"] = {"age": ka, "gender": kg, "l": t["l"], "share": round(t["l"] / tot * 100), "cpl": round(t["s"] / t["l"], 2)}
            rep["aud"] = aud
            print("aud:", tot, "leads;", round(sum(x["s"] for x in age)), "SAR;", len(place), "placements")
    except Exception as e:
        print("aud skipped:", e)
if sys.argv[3] != "-":
    try:
        m = re.search(r'<script type="application/json" id="data">(.*?)</script>', open(sys.argv[3], encoding="utf8").read(), re.S)
        old = json.loads(m.group(1))
        if isinstance(old.get("manual"), dict) and "manual" not in rep:
            rep["manual"] = old["manual"]; print("manual kept:", ",".join(old["manual"].keys()))
    except Exception as e:
        print("manual not carried:", e)
json.dump(rep, open(sys.argv[4], "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
