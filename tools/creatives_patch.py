#!/usr/bin/env python3
"""Insert the creatives section (CSS + HTML + JS) into a client report page. Idempotent.
usage: creatives_patch.py <report.html> [<out.html>]"""
import sys
p = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else p
t = open(p, encoding="utf8").read()
if "id=\"creSec\"" in t:
    print("already patched"); open(out, "w", encoding="utf8").write(t); sys.exit()
CSS = """<style>
/* creatives section */
.cre-sum{list-style:none;margin:0 0 14px;padding:0;display:flex;flex-direction:column;gap:8px}
.cre-sum li{padding:10px 12px;border-radius:10px;background:rgba(44,194,187,.05);border:1px solid var(--line);font-size:13.5px;line-height:1.75}
.cre-sum li b{color:var(--gold-hi);font-weight:600}
.cre-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.cre{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#121419;display:flex;flex-direction:column;min-width:0}
.cre .th{aspect-ratio:4/5;background:var(--sunk);display:grid;place-items:center;overflow:hidden;position:relative}
.cre .th img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cre .th .ph{font-family:var(--f-display);font-size:26px;color:var(--muted)}
.cre .rk{position:absolute;top:8px;inset-inline-start:8px;background:rgba(13,14,17,.85);border:1px solid var(--line);border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600;z-index:1}
.cre .st{position:absolute;top:8px;inset-inline-end:8px;border-radius:999px;padding:2px 9px;font-size:11.5px;font-weight:600;z-index:1}
.st.win{background:var(--good-bg);color:var(--good)}.st.prom{background:rgba(44,194,187,.18);color:var(--gold-hi)}.st.test{background:var(--sunk);color:var(--muted)}.st.weak{background:var(--bad-bg);color:var(--bad)}
.cre .bd{padding:10px 12px;display:flex;flex-direction:column;gap:6px;flex:1}
.cre .nm{font-weight:600;font-size:13.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cre .mt{font-size:11.5px;color:var(--muted)}
.cre .big{display:flex;justify-content:space-between;align-items:baseline;gap:6px}
.cre .big b{font-family:var(--f-display);font-size:22px;color:var(--gold-hi)}
.cre .bar{height:5px;border-radius:3px;background:var(--sunk);overflow:hidden}.cre .bar span{display:block;height:100%;background:linear-gradient(90deg,var(--gold),var(--gold-hi))}
.cre dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px 8px;margin:0;font-size:12px}
.cre dt{color:var(--muted);font-size:11px}.cre dd{margin:0;font-weight:600}
.cre .rec{margin-top:auto;font-size:12.5px;line-height:1.6;padding:8px 10px;border-radius:8px;background:var(--sunk)}
.cre .rec.fat{border-inline-start:3px solid var(--warn)}
</style>
"""
HTML = """  <section class="panel" id="creSec" hidden><div class="panel-h"><h2>أداء التصاميم الإعلانية</h2><div class="chips" id="creWin" role="group" aria-label="فترة التصاميم"></div></div>
    <p class="note" style="margin:0 0 10px">كل تصميم محسوب مرة واحدة حتى لو استُخدم في أكثر من إعلان أو حملة. «فعّال» = حقق 5 تسجيلات أو أكثر بتكلفة أقل من متوسط الحملة.</p>
    <ul class="cre-sum" id="creSum"></ul><div class="chips" id="creFilter" role="group" aria-label="تصنيف التصاميم" style="margin-bottom:12px;width:fit-content"></div><div class="cre-grid" id="creGrid"></div>
  </section>
"""
JS = r"""<script>
(function(){
const D=JSON.parse(document.getElementById("data").textContent),C=D.creatives||[];if(!C.length)return;
const sec=document.getElementById("creSec");sec.hidden=false;
const PLN={meta:["Meta","var(--meta)"],snap:["Snapchat","var(--snap)"],tt:["TikTok","var(--tt)"]};
const f0=new Intl.NumberFormat("en-US",{maximumFractionDigits:0}),f2=new Intl.NumberFormat("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
const M=v=>isFinite(v)?'<span class="num">'+(v>=1000?f0.format(v):f2.format(v))+"</span> ر.س":"—";
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const ST={win:"فعّال",prom:"واعد",test:"قيد الاختبار",weak:"أداء أضعف"};
let win="all",flt="all";
function rows(){return C.map(g=>{const o=win==="7"?{s:g.s7,l:g.l7,i:g.i7,c:g.c7}:{s:g.s,l:g.l,i:g.i,c:g.c};return Object.assign({},g,o,{cpl:o.l?o.s/o.l:NaN,cpl7:g.l7?g.s7/g.l7:NaN})}).filter(g=>g.s>0)}
function draw(){
 const R=rows(),S=R.reduce((a,g)=>a+g.s,0),L=R.reduce((a,g)=>a+g.l,0),avg=L?S/L:NaN;
 document.getElementById("creWin").innerHTML=[["all","كل فترة التقرير"],["7","آخر 7 أيام"]].map(([k,l])=>'<button type="button" data-cw="'+k+'" aria-pressed="'+(k===win)+'">'+l+"</button>").join("");
 R.forEach(g=>{g.st=g.l>=5&&g.cpl<=avg?"win":g.l>=1&&g.cpl<=avg*1.25?"prom":((g.l===0&&g.s>=avg*2)||(g.l>=1&&g.cpl>avg*1.5&&g.s>=avg*2))?"weak":"test";
  g.fat=win==="all"&&g.st==="win"&&g.s7>=avg&&(g.l7===0||g.cpl7>g.cpl*1.4)});
 const wins=R.filter(g=>g.st==="win").sort((a,b)=>b.l-a.l||a.cpl-b.cpl),best=wins[0]||R.filter(g=>g.l>0).sort((a,b)=>a.cpl-b.cpl)[0];
 R.forEach(g=>{g.rec=g.st==="win"?(g.fat?"حقق نتائج قوية لكن أداءه تراجع في الأيام الأخيرة؛ نوصي بتجهيز نسخة متجددة منه مع الحفاظ على ميزانيته.":"نوصي بزيادة الميزانية المخصصة لهذا التصميم تدريجيًا."):
  g.st==="prom"?"نتائجه مبشّرة؛ نوصي بمنحه ميزانية إضافية لتأكيد أدائه.":g.st==="weak"?"نوصي بإيقافه وتحويل ميزانيته"+(best&&best!==g?" إلى «"+esc(best.name)+"» على "+PLN[best.p][0]:" إلى التصاميم الفعّالة")+".":"يحتاج إلى مزيد من البيانات قبل الحكم على أدائه."});
 const sum=[],byL=R.slice().sort((a,b)=>b.l-a.l);
 if(best)sum.push("أفضل تصميم أداءً: <b>«"+esc(best.name)+"»</b> على "+PLN[best.p][0]+"، حقق <b>"+f0.format(best.l)+" تسجيلًا</b> ("+f0.format(L?best.l/L*100:0)+"% من الإجمالي) بتكلفة <b>"+M(best.cpl)+"</b> للتسجيل مقابل متوسط "+M(avg)+".");
 if(R.length>=4&&L){const t3=byL.slice(0,3).reduce((a,g)=>a+g.l,0);sum.push("أعلى 3 تصاميم حققت <b>"+f0.format(t3/L*100)+"%</b> من التسجيلات، و<b>"+wins.length+"</b> تصاميم فعّالة من أصل "+R.length+" تصميمًا.")}
 const weak=R.filter(g=>g.st==="weak"),ws=weak.reduce((a,g)=>a+g.s,0);
 if(weak.length&&S)sum.push("صُرف <b>"+M(ws)+"</b> ("+f0.format(ws/S*100)+"% من الميزانية) على "+weak.length+" تصاميم أداؤها أضعف؛ نوصي بإعادة توزيع هذا المبلغ على التصاميم الفعّالة.");
 const fat=R.filter(g=>g.fat);if(fat.length)sum.push("رُصد تراجع حديث في أداء "+fat.length+" من التصاميم الفعّالة ("+fat.slice(0,3).map(g=>"«"+esc(g.name)+"»").join("، ")+")؛ نوصي بتجهيز نسخ متجددة منها.");
 const plats=[...new Set(R.map(g=>g.p))];if(best&&plats.length>1){const oth=plats.filter(p=>p!==best.p).filter(p=>{const x=R.filter(g=>g.p===p),s=x.reduce((a,g)=>a+g.s,0),l=x.reduce((a,g)=>a+g.l,0);return s>0&&(!l||s/l>avg)});
  if(oth.length)sum.push("نقترح تطبيق أسلوب التصميم الأنجح على "+PLN[best.p][0]+" في حملات "+oth.map(p=>PLN[p][0]).join(" و")+" لرفع كفاءتها.")}
 document.getElementById("creSum").innerHTML=sum.map(s=>"<li>"+s+"</li>").join("");
 const cnt=k=>R.filter(g=>k==="all"||g.st===k).length;
 document.getElementById("creFilter").innerHTML=[["all","الكل"],["win",ST.win],["prom",ST.prom],["test",ST.test],["weak",ST.weak]].filter(([k])=>k==="all"||cnt(k)).map(([k,l])=>'<button type="button" data-cf="'+k+'" aria-pressed="'+(k===flt)+'">'+l+" ("+cnt(k)+")</button>").join("");
 const list=byL.filter(g=>flt==="all"||g.st===flt).slice(0,24),rank=new Map(byL.map((g,i)=>[g,i+1]));
 document.getElementById("creGrid").innerHTML=list.map(g=>'<article class="cre"><div class="th"><span class="ph">'+PLN[g.p][0]+"</span>"+(g.thumb?'<img loading="lazy" referrerpolicy="no-referrer" alt="" src="'+esc(g.thumb)+'" onerror="this.remove()">':"")+'<span class="rk">#'+rank.get(g)+'</span><span class="st '+g.st+'">'+ST[g.st]+'</span></div><div class="bd"><div class="nm" title="'+esc(g.name)+'">'+esc(g.name)+'</div><div class="mt"><span class="dot" style="background:'+PLN[g.p][1]+'"></span> '+PLN[g.p][0]+" · "+g.camps+" حملة · "+g.ads+' إعلان</div><div class="big"><span><b>'+f0.format(g.l)+'</b> تسجيل</span><span class="mt">'+(L?f0.format(g.l/L*100):0)+'% من التسجيلات</span></div><div class="bar"><span style="width:'+(L?(g.l/L*100).toFixed(1):0)+'%"></span></div><dl><div><dt>تكلفة التسجيل</dt><dd>'+M(g.cpl)+"</dd></div><div><dt>الصرف</dt><dd>"+M(g.s)+'</dd></div><div><dt>نسبة النقر</dt><dd><span class="num">'+(g.i?f2.format(g.c/g.i*100):"0")+'%</span></dd></div></dl><div class="rec'+(g.fat?" fat":"")+'">'+g.rec+"</div></div></article>").join("")||'<p class="note">لا توجد تصاميم في هذا التصنيف.</p>'}
document.addEventListener("click",e=>{const w=e.target.closest("[data-cw]");if(w){win=w.dataset.cw;flt="all";draw();return}const f=e.target.closest("[data-cf]");if(f){flt=f.dataset.cf;draw()}});
draw()})();
</script>
"""
anchor = '  <section class="panel"><div class="panel-h"><h2>تفاصيل الحملات</h2>'
assert t.count(anchor) == 1, "anchor"
t = t.replace(anchor, HTML + anchor)
i = t.index("<!--DATA-START-->")
t = t[:i] + CSS + t[i:]
j = t.rindex("</script>") + len("</script>")
t = t[:j] + "\n" + JS + t[j:]
open(out, "w", encoding="utf8").write(t)
print("patched")
