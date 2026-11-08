#!/usr/bin/env python3
"""Build the hourly agency snapshot.
usage: agency_build.py <today_rows.json> <yday_rows.json> <prev_data.json|-> <now ISO+03:00> <out_data.json> <out_telegram.txt> <page_url>
rows file: {"meta":[...windsor rows...],"snap":[...],"tt":[...]}
"""
import json, sys
FX = {"SAR":1,"USD":3.75,"AED":1.021,"QAR":1.03,"EGP":0.0667,"GBP":5.0}
CLIENTS = {
 "meta:1620638329403862":"مساب العقارية","snap:35861d53-7066-4688-bd31-dce0cebb2d5b":"مساب العقارية","tt:7682750301601824788":"مساب العقارية",
 "meta:852323024077178":"النموذجية الأولى","snap:2a051572-c841-4f03-b473-56ad204c79a8":"النموذجية الأولى","tt:7389264380287991824":"النموذجية الأولى","tt:7696162242630467636":"النموذجية الأولى",
 "meta:943643444739467":"مكيون","meta:1597810178042256":"مكيون","tt:7703457655599300609":"مكيون","meta:1143955064371755":"مكيون","meta:1452337152504913":"مكيون",
 "meta:2897945980567876":"هدف","snap:a497c584-0f95-4b36-9dcd-7a8529f1f95b":"هدف",
 "snap:416d4e33-c33f-4da3-9bbb-262ba4103752":"زاوية المفتاح",
 "meta:2270492903138751":"OIA Properties","meta:1036295864285013":"OIA Properties",
 "meta:1251868995537337":"Invest in Dubai","meta:1220323656571523":"Invest in Dubai",
 "meta:521180493985738":"كاستوريا","meta:196249910250210":"كاستوريا",
 "meta:3430468447102635":"إيوان","meta:1473327353143492":"Apoelezz","meta:630552978916290":"The Global","meta:1706006544185118":"نيو إيفنت",
 "meta:1321648629567685":"101 Agency","meta:1666919771668464":"101 Agency","snap:1b737305-aa69-43cf-8e4b-c398070f694f":"101 Agency","snap:5b1252eb-459b-4877-a3f3-00be42c603ed":"101 Agency","snap:96b3cb6c-a885-4cdd-8571-cd96ed4217ea":"101 Agency","tt:7568644170794680337":"101 Agency"}
PL = {"meta":"Meta","snap":"Snapchat","tt":"TikTok"}
n = lambda x: float(x or 0)

def norm(p, r):
    cur = r.get("account_currency") or r.get("currency") or "SAR"
    if p == "meta":
        L, M = n(r.get("actions_lead")), n(r.get("actions_onsite_conversion_messaging_conversation_started_7d"))
        leads, clicks = max(L, M), n(r.get("clicks"))
    elif p == "snap":
        leads, clicks = n(r.get("native_leads")) + n(r.get("conversion_sign_ups")), n(r.get("swipes"))
    else:
        leads, clicks = n(r.get("onsite_form")) + n(r.get("form")), n(r.get("clicks"))
    acc = str(r.get("account_id", ""))
    camp = (r.get("campaign") or "—").strip()
    client = "مكيون" if "mayan" in camp.lower() else CLIENTS.get(p + ":" + acc, r.get("account_name") or acc)
    return {"p":p,"acc":acc,"accName":(r.get("account_name") or acc).strip(),"client":client,"cur":cur,"camp":camp,
            "status":r.get("campaign_status") or "","s":round(n(r.get("spend"))*FX.get(cur,1),2),
            "i":int(n(r.get("impressions"))),"c":int(clicks),"l":int(leads)}

def load(path):
    d = json.load(open(path, encoding="utf8"))
    return [norm(p, r) for p in ("meta","snap","tt") for r in d.get(p, []) if n(r.get("spend")) > 0]

today, yday = load(sys.argv[1]), load(sys.argv[2])
prev = {} if sys.argv[3] == "-" else json.load(open(sys.argv[3], encoding="utf8"))
now, out_data, out_tg, url = sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]
date, hhmm = now[:10], now[11:16]

def agg(rows, key):
    o = {}
    for r in rows:
        a = o.setdefault(key(r), {"s":0,"l":0,"i":0,"c":0,"n":0})
        a["s"] += r["s"]; a["l"] += r["l"]; a["i"] += r["i"]; a["c"] += r["c"]; a["n"] += 1
    return o
T = {"s":sum(r["s"] for r in today),"l":sum(r["l"] for r in today)}
Y = {"s":sum(r["s"] for r in yday),"l":sum(r["l"] for r in yday)}
byC, byCy, byP = agg(today, lambda r:r["client"]), agg(yday, lambda r:r["client"]), agg(today, lambda r:r["p"])

hist = [h for h in prev.get("hist", []) if prev.get("date") == date]
hist = [h for h in hist if h[0] != hhmm] + [[hhmm, round(T["s"],2), T["l"]]]
last = hist[-2] if len(hist) >= 2 else None
dh = {"s": round(T["s"]-last[1],2), "l": T["l"]-last[2], "since": last[0]} if last else None

alerts = []
for r in sorted(today, key=lambda r:-r["s"]):
    if r["s"] >= 150 and r["l"] == 0:
        alerts.append(f"حملة «{r['camp']}» ({r['client']} · {PL[r['p']]}) صرفت {r['s']:,.0f} ر.س بدون عملاء")
for c, a in byC.items():
    y = byCy.get(c)
    if y and y["l"] >= 3 and a["l"] >= 3:
        cy, ct = y["s"]/y["l"], a["s"]/a["l"]
        if ct > cy*1.5: alerts.append(f"{c}: تكلفة العميل اليوم {ct:,.0f} ر.س مقابل {cy:,.0f} أمس (+{(ct/cy-1)*100:.0f}%)")
if int(hhmm[:2]) >= 10:
    for c, y in byCy.items():
        if y["s"] >= 200 and c not in byC:
            alerts.append(f"{c}: صرف أمس {y['s']:,.0f} ر.س ومفيش صرف النهارده لحد دلوقتي (حملات متوقفة أو مشكلة دفع؟)")

data = {"updated":now,"date":date,"rows":today,"yday":{"tot":Y,"byClient":{k:{"s":round(v["s"],2),"l":v["l"]} for k,v in byCy.items()}},
        "hist":hist,"lastHour":dh,"alerts":alerts}
json.dump(data, open(out_data,"w",encoding="utf8"), ensure_ascii=False, separators=(",",":"))

f = lambda v: f"{v:,.0f}"
cpl = lambda s,l: f"{s/l:,.0f} ر.س" if l else "—"
L = [f"📊 تقرير الوكالة — {hhmm} (اليوم حتى الآن)", "",
     f"💰 الصرف: {f(T['s'])} ر.س" + (f"  (أمس كامل: {f(Y['s'])})" if Y['s'] else ""),
     f"👥 العملاء المحتملون: {T['l']}" + (f"  (أمس: {Y['l']})" if Y['s'] else ""),
     f"🎯 تكلفة العميل: {cpl(T['s'],T['l'])}"]
if dh: L.append(f"⏱ منذ {dh['since']}: +{f(dh['s'])} ر.س · +{dh['l']} عميل")
L += ["", "🏢 حسب العميل:"]
for c, a in sorted(byC.items(), key=lambda kv:-kv[1]["s"]):
    L.append(f"• {c}: {f(a['s'])} ر.س · {a['l']} عميل · {cpl(a['s'],a['l'])}")
L += ["", "📱 حسب المنصة:"]
for p in ("meta","snap","tt"):
    if p in byP: a = byP[p]; L.append(f"• {PL[p]}: {f(a['s'])} ر.س · {a['l']} عميل")
L += ["", "🔝 أعلى الحملات صرفًا:"]
for i, r in enumerate(sorted(today, key=lambda r:-r["s"])[:5], 1):
    L.append(f"{i}. {r['camp']} ({r['client']} · {PL[r['p']]}): {f(r['s'])} ر.س · {r['l']} عميل")
if alerts: L += ["", "⚠️ تنبيهات:"] + [f"• {a}" for a in alerts[:6]]
L += ["", f"التفاصيل الكاملة: {url}"]
txt = "\n".join(L)
open(out_tg,"w",encoding="utf8").write(txt[:4000])
print(txt)
