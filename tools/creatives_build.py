#!/usr/bin/env python3
"""Aggregate ad-level rows into creatives and inject them into a client report's data JSON.
usage: creatives_build.py <report_data.json> <ads_full.json> <ads_7d.json> <out_data.json>
ads files: {"meta":[rows],"snap":[rows],"tt":[rows]} as returned by Windsor (ad level, no date field).
Only ads whose (platform, account, trimmed campaign) exist in the report's campaigns are kept, so each
report's own inclusion rules apply automatically. A creative = same image/video (Snap media_id, TikTok
video_id/image, Meta thumbnail file), merged across ads and campaigns."""
import json, sys, re
n = lambda x: float(x or 0)
def key(p, r):
    if p == "tt": return "v:" + str(r.get("video_id") or r.get("image_url") or r.get("ad_name"))
    u = str(r.get("thumbnail_url") or "")
    m = re.search(r"media_id=([\w-]+)", u)
    if m: return "m:" + m.group(1)
    b = u.split("?")[0].rsplit("/", 1)[-1]
    return ("t:" + b) if b else ("n:" + str(r.get("ad_name")))
def leads(p, r):
    if p == "meta": return max(n(r.get("actions_lead")), n(r.get("actions_onsite_conversion_messaging_conversation_started_7d")))
    if p == "snap": return n(r.get("native_leads")) + n(r.get("conversion_sign_ups"))
    return n(r.get("onsite_form")) + n(r.get("form"))
rep = json.load(open(sys.argv[1], encoding="utf8"))
fx = rep.get("fx", {"SAR":1,"USD":3.75,"AED":1.021})
camps = {(c["p"], c["name"].strip()) for c in rep["campaigns"]}
def agg(path):
    d = json.load(open(path, encoding="utf8")); out = {}
    for p in ("meta","snap","tt"):
        for r in d.get(p, []) or []:
            if n(r.get("spend")) <= 0 or (p, (r.get("campaign") or "").strip()) not in camps: continue
            cur = r.get("account_currency") or r.get("currency") or "SAR"
            k = p + "|" + key(p, r)
            g = out.setdefault(k, {"p":p,"s":0,"l":0,"i":0,"c":0,"ads":0,"camps":set(),"names":{},"thumb":None})
            s = n(r.get("spend")) * fx.get(cur, 1)
            g["s"] += s; g["l"] += leads(p, r); g["i"] += n(r.get("impressions"))
            g["c"] += n(r.get("swipes")) if p == "snap" else n(r.get("clicks")); g["ads"] += 1
            g["camps"].add((r.get("campaign") or "").strip())
            nm = str(r.get("ad_name") or "—"); g["names"][nm] = g["names"].get(nm, 0) + s
            th = r.get("thumbnail_url") or r.get("image_url")
            if th and not g["thumb"]: g["thumb"] = th
    return out
full, last = agg(sys.argv[2]), agg(sys.argv[3])
res = []
for k, g in full.items():
    r7 = last.get(k, {})
    res.append({"p":g["p"],"name":max(g["names"].items(), key=lambda kv:kv[1])[0],"thumb":g["thumb"],
        "s":round(g["s"],2),"l":int(g["l"]),"i":int(g["i"]),"c":int(g["c"]),"ads":g["ads"],"camps":len(g["camps"]),
        "s7":round(r7.get("s",0),2),"l7":int(r7.get("l",0)),"i7":int(r7.get("i",0)),"c7":int(r7.get("c",0))})
res.sort(key=lambda x:(-x["l"], x["s"]))
rep["creatives"] = res
json.dump(rep, open(sys.argv[4], "w", encoding="utf8"), ensure_ascii=False, separators=(",",":"))
print(len(res), "creatives;", sum(x["l"] for x in res), "leads;", round(sum(x["s"] for x in res)), "SAR")
