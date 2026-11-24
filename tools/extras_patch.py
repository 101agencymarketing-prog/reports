#!/usr/bin/env python3
"""Add the "extras" to a client report page (page shell only, the data block is never touched). Idempotent.
usage: extras_patch.py <report.html> [<out.html>]
Adds: custom period + last month, PDF / Excel download of the selected period, audience panel (data key "aud"),
goal + budget panel, lead-quality funnel and team notes (data key "manual"), frequency / video views on creatives.
Every panel stays hidden until its data key exists, so the same shell is safe for every report."""
import sys
p = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else p
t = open(p, encoding="utf8").read()
if 'id="xsecs"' in t:
    print("already patched"); open(out, "w", encoding="utf8").write(t); sys.exit()

CSS = """<style>
/* extras */
.xdl button{color:var(--gold-hi)}
.xrange{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:-4px 0 14px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--surface);font-size:13.5px}
.xrange label{display:inline-flex;align-items:center;gap:6px;color:var(--muted)}
.xrange input{background:var(--sunk);color:var(--ink);border:1px solid var(--line);border-radius:7px;padding:6px 8px;font:inherit;color-scheme:dark}
.xrange button{border:0;border-radius:7px;padding:7px 16px;font:inherit;font-weight:600;background:var(--gold);color:#06201f;cursor:pointer}
.xrange .msg{color:var(--warn)}
.xgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}
.xgrid h3{margin:0 0 10px;font-size:13.5px;font-weight:600;color:var(--muted)}
.xrow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 10px;margin-bottom:10px;font-size:13px}
.xrow .k{font-weight:600;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.xrow .v{color:var(--muted);white-space:nowrap}
.xrow .xb{grid-column:1/-1;height:6px;border-radius:3px;background:var(--sunk);overflow:hidden}
.xrow .xb span{display:block;height:100%;border-radius:3px;background:linear-gradient(90deg,var(--gold),var(--gold-hi))}
.xlede{margin:0 0 14px;padding:10px 12px;border-radius:10px;background:rgba(44,194,187,.05);border:1px solid var(--line);font-size:13.5px;line-height:1.75}
.xlede b{color:var(--gold-hi);font-weight:600}
.xtile{border:1px solid var(--line);border-radius:12px;padding:14px;background:var(--surface)}
.xtile .lbl{font-size:12.5px;color:var(--muted)}.xtile .val{font-family:var(--f-display);font-size:24px;margin:2px 0 8px}
.xtile .val small{font-family:var(--f-body);font-size:12.5px;color:var(--muted);font-weight:400}
.xprog{position:relative;height:9px;border-radius:5px;background:var(--sunk);margin:8px 0 6px}
.xprog span{position:absolute;inset-block:0;inset-inline-start:0;border-radius:5px;background:linear-gradient(90deg,var(--gold),var(--gold-hi))}
.xprog i{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--ink);border-radius:1px}
.xtile .sub{font-size:12.5px;color:var(--muted);line-height:1.6}
.xpill{display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:600}
.xpill.good{background:var(--good-bg);color:var(--good)}.xpill.warn{background:var(--warn-bg);color:var(--warn)}.xpill.bad{background:var(--bad-bg);color:var(--bad)}
.xsteps{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.xstep{border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--surface)}
.xstep .n{font-family:var(--f-display);font-size:24px;color:var(--gold-hi)}.xstep .l{font-size:13px;font-weight:600}.xstep .s{font-size:12px;color:var(--muted);line-height:1.6}
.xnotes{list-style:none;margin:10px 0 0;padding:0;font-size:12.5px;display:flex;flex-direction:column;gap:5px}
.xnotes li{display:flex;gap:8px;align-items:baseline}.xnotes time{color:var(--gold-hi);font-weight:600;white-space:nowrap}
.xtoast{position:fixed;inset-inline:16px;bottom:18px;margin:auto;max-width:440px;padding:11px 14px;border-radius:10px;background:var(--sunk);border:1px solid var(--line);color:var(--ink);font-size:13.5px;z-index:50;box-shadow:0 8px 24px rgba(0,0,0,.4)}
#xprint{display:none}
@media print{
 @page{size:A4;margin:8mm}
 html,body{background:var(--bg)!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .toolbar,.xrange,.xtoast{display:none!important}
 #xprint{display:block;margin:0 0 12px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font-size:13.5px}
 #xprint b{color:var(--gold-hi)}
 .panel,.kpi,.cre,.itile,.pcard,.xtile,.xstep,tr{break-inside:avoid}
 details>*{display:block!important}
 *{animation:none!important;transition:none!important}
}
</style>
"""

TOOLBAR_OLD = 'id="plats"></div></div>'
TOOLBAR_NEW = ('id="plats"></div><div class="chips xdl" id="xdl" role="group" aria-label="تحميل التقرير">'
               '<button type="button" data-x="pdf">تحميل PDF</button><button type="button" data-x="csv">تحميل Excel</button></div></div>'
               '<div class="xrange" id="xrange" hidden><label>من <input type="date" id="xfrom"></label><label>إلى <input type="date" id="xto"></label>'
               '<button type="button" data-x="apply">عرض الفترة</button><span class="msg" id="xmsg"></span></div>'
               '<div id="xprint"></div>')

SECS = ('  <div id="xsecs">'
        '<section class="panel" id="xgoal" hidden><div class="panel-h"><h2>المستهدف والميزانية</h2><span class="stamp" id="xgoalLbl"></span></div><div class="xgrid" id="xgoalB"></div></section>'
        '<section class="panel" id="xqual" hidden><div class="panel-h"><h2>جودة العملاء المحتملين</h2><span class="stamp" id="xqualLbl"></span></div><div class="xsteps" id="xqualB"></div>'
        '<p class="note" style="margin:10px 0 0">أرقام المؤهلين والزيارات والحجوزات من متابعة فريق المبيعات للعملاء المحتملين القادمين من الإعلانات.</p></section>'
        '<section class="panel" id="xaud" hidden><div class="panel-h"><h2>من يتفاعل مع إعلاناتك</h2><span class="stamp" id="xaudLbl"></span></div><p class="xlede" id="xaudL" hidden></p><div class="xgrid" id="xaudB"></div></section>'
        '</div>\n')
SECS_ANCHOR = '  <section class="panel" id="creSec"'

HOOK_OLD = ' drawTrend(a,b);\n if(anim)play();'
HOOK_NEW = (' drawTrend(a,b);\n if(window.__xr)window.__xr({a:a,b:b,len:len,all:all,by:by,camps:camps,cs:cs,p:p,plat:plat,period:period,'
            'PL:PL,PK:PK,sum:sum,within:within,daySum:daySum,rangeDays:rangeDays,DAYS:DAYS});\n if(anim)play();')
INIT_OLD = 'if(!RM)document.documentElement.classList.add("anim");\nrender(true);'
INIT_NEW = ('if(!RM)document.documentElement.classList.add("anim");\n'
            'if(window.__xi)window.__xi({P:P,go:function(k){period=k;render(true)}});\nrender(true);')
CRE_OLD = """%</span></dd></div></dl><div class="rec'"""
CRE_NEW = """%</span></dd></div>'+(window.__xc?window.__xc(g):"")+'</dl><div class="rec'"""

JS = r"""<script>
(function(){
var D;try{D=JSON.parse(document.getElementById("data").textContent)}catch(e){return}
var M=D.manual||{},A=D.aud,R=null,S=null;
var $=function(s){return document.querySelector(s)};
var esc=function(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})};
var nf0=new Intl.NumberFormat("en-US",{maximumFractionDigits:0}),nf1=new Intl.NumberFormat("en-US",{maximumFractionDigits:1}),nf2=new Intl.NumberFormat("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
var money=function(v){return isFinite(v)?'<span class="num">'+(v>=1000?nf0.format(v):nf2.format(v))+"</span> ر.س":"—"};
var num=function(v){return'<span class="num">'+nf0.format(v)+"</span>"};
function sh(ymd,n){var d=new Date(ymd+"T12:00:00Z");d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)}
var all=[];(D.campaigns||[]).forEach(function(c){for(var d in c.days)all.push(d)});all.sort();
var END=D.end,MIN=all[0]||END;
var dlong=function(d){return new Date(d+"T12:00:00Z").toLocaleDateString("ar-SA-u-nu-latn",{day:"numeric",month:"long",year:"numeric",timeZone:"UTC"})};
var dshort=function(d){return new Date(d+"T12:00:00Z").toLocaleDateString("ar-SA-u-nu-latn",{day:"numeric",month:"short",timeZone:"UTC"})};
var mname=function(k){return new Date(k+"-15T12:00:00Z").toLocaleDateString("ar-SA-u-nu-latn",{month:"long",year:"numeric",timeZone:"UTC"})};
function tot(a,b){return S.sum((D.campaigns||[]).reduce(function(o,c){return o.concat(S.within(c,a,b))},[]))}

window.__xi=function(rep){R=rep;
 var f=END.slice(0,8)+"01",pl=sh(f,-1),pf=pl.slice(0,8)+"01";
 if(MIN<=pf)rep.P.push(["lastm","الشهر الماضي",pf,pl]);
 var a=sh(END,-13);rep.P.push(["custom","فترة مخصصة",a<MIN?MIN:a,END])};
window.__xr=function(s){S=s;try{range()}catch(e){}try{goal()}catch(e){}try{quality()}catch(e){}try{audience()}catch(e){}try{notes()}catch(e){}try{head()}catch(e){}};
window.__xc=function(g){var h="";
 if(g.fq>0)h+='<div><dt>تكرار الظهور</dt><dd><span class="num">'+nf1.format(g.fq)+"</span> مرة</dd></div>";
 if(g.vv>0&&g.i>0&&g.vv/g.i>=.05){h+='<div><dt>مشاهدات الفيديو</dt><dd><span class="num">'+nf0.format(g.vv)+"</span></dd></div>";
  if(g.vc>0)h+='<div><dt>مشاهدة كاملة</dt><dd><span class="num">'+nf0.format(g.vc/g.vv*100)+"%</span></dd></div>"}
 return h};

function range(){var box=$("#xrange");if(!box)return;var on=S.period==="custom";box.hidden=!on;if(!on)return;
 var f=$("#xfrom"),t=$("#xto");f.min=t.min=MIN;f.max=t.max=END;f.value=S.a;t.value=S.b;
 $("#xmsg").textContent="البيانات المتاحة من "+dshort(MIN)+" إلى "+dshort(END)}
function apply(){var a=$("#xfrom").value,b=$("#xto").value,m=$("#xmsg");
 if(!a||!b){m.textContent="اختر تاريخ البداية والنهاية.";return}
 if(a>b){var x=a;a=b;b=x}if(a<MIN)a=MIN;if(b>END)b=END;if(a>b){m.textContent="لا توجد بيانات في هذه الفترة.";return}
 var e=R.P.filter(function(x){return x[0]==="custom"})[0];e[2]=a;e[3]=b;R.go("custom")}

function head(){var el=$("#xprint");if(!el)return;
 el.innerHTML="تقرير أداء الحملات الإعلانية · <b>"+esc(D.client||"")+"</b> · الفترة: <b>"+(S.a===S.b?dlong(S.a):dlong(S.a)+" – "+dlong(S.b))+"</b>"+(S.plat==="all"?"":" · "+S.PL[S.plat].l)+" · إعداد 101 Agency"}

function goal(){var sec=$("#xgoal");if(!sec)return;var T=+M.target||0,B=+M.budget||0;if(!(T>0||B>0)){sec.hidden=true;return}
 var a=END.slice(0,8)+"01",t=tot(a,END),y=+END.slice(0,4),m=+END.slice(5,7),dim=new Date(Date.UTC(y,m,0)).getUTCDate(),day=+END.slice(8),h="";
 $("#xgoalLbl").textContent=mname(END.slice(0,7))+" · حتى "+dshort(END);
 if(B>0){var exp=B*day/dim,pc=Math.min(100,t.s/B*100),df=exp?(t.s/exp-1)*100:0,st=t.s>B?["bad","تجاوز الميزانية"]:Math.abs(df)<=10?["good","على المسار"]:df>10?["warn","أسرع من الخطة"]:["warn","أبطأ من الخطة"];
  h+='<div class="xtile"><div class="lbl">ميزانية الشهر</div><div class="val">'+money(t.s)+" <small>من "+money(B)+'</small></div><div class="xprog"><span style="width:'+pc.toFixed(1)+'%"></span><i style="inset-inline-start:'+Math.min(100,day/dim*100).toFixed(1)+'%" title="المتوقع حتى اليوم"></i></div><div class="sub"><span class="xpill '+st[0]+'">'+st[1]+"</span> تم صرف "+nf0.format(t.s/B*100)+"% من الميزانية بعد مرور "+nf0.format(day/dim*100)+"% من الشهر. المتبقي "+money(Math.max(0,B-t.s))+".</div></div>"}
 if(T>0){var ok=isFinite(t.cpl),d2=ok?(t.cpl/T-1)*100:0,s2=!ok?["warn","لا توجد نتائج بعد"]:d2<=0?["good","ضمن المستهدف"]:d2<=15?["warn","قريب من المستهدف"]:["bad","أعلى من المستهدف"];
  h+='<div class="xtile"><div class="lbl">تكلفة العميل المحتمل</div><div class="val">'+money(t.cpl)+" <small>المستهدف "+money(T)+'</small></div><div class="sub"><span class="xpill '+s2[0]+'">'+s2[1]+"</span> "+(ok?(d2<=0?"أقل من المستهدف بنسبة "+nf0.format(-d2)+"%":"أعلى من المستهدف بنسبة "+nf0.format(d2)+"%")+" · "+nf0.format(t.res)+" عميلًا محتملًا هذا الشهر.":"")+"</div></div>"}
 $("#xgoalB").innerHTML=h;sec.hidden=false}

function quality(){var sec=$("#xqual");if(!sec)return;var Q=M.q||{},ks=Object.keys(Q).filter(function(k){return/^\d{4}-\d\d$/.test(k)&&k<=END.slice(0,7)&&Q[k]&&(+Q[k].q>0||+Q[k].v>0||+Q[k].b>0)}).sort();
 if(!ks.length){sec.hidden=true;return}var k=ks[ks.length-1],q=Q[k],a=k+"-01",y=+k.slice(0,4),m=+k.slice(5,7),b=k+"-"+String(new Date(Date.UTC(y,m,0)).getUTCDate()).padStart(2,"0");if(b>END)b=END;
 var t=tot(a,b),st=[["العملاء المحتملون",t.res,"من الإعلانات"],["عملاء مؤهلون",+q.q||0],["زيارات للمشروع",+q.v||0],["حجوزات",+q.b||0]],h="";
 $("#xqualLbl").textContent=mname(k);
 st.forEach(function(s,i){if(i&&!s[1])return;var pv=i?st[i-1][1]:0,x=i?(pv?nf0.format(s[1]/pv*100)+"% من المرحلة السابقة":""):s[2];
  h+='<div class="xstep"><div class="n">'+num(s[1])+'</div><div class="l">'+s[0]+'</div><div class="s">'+x+(s[1]&&t.s?"<br>التكلفة لكل واحد "+money(t.s/s[1]):"")+"</div></div>"});
 $("#xqualB").innerHTML=h;sec.hidden=false}

var PLACE={"facebook|feed":"فيسبوك · الصفحة الرئيسية","facebook|facebook_reels":"فيسبوك · ريلز","facebook|facebook_stories":"فيسبوك · ستوري","facebook|instream_video":"فيسبوك · داخل الفيديو","facebook|marketplace":"فيسبوك · ماركت بليس","facebook|facebook_reels_overlay":"فيسبوك · إعلانات على الريلز","facebook|video_feeds":"فيسبوك · الفيديوهات","facebook|search":"فيسبوك · البحث","facebook|facebook_profile_feed":"فيسبوك · صفحات الحسابات","instagram|feed":"إنستجرام · الصفحة الرئيسية","instagram|instagram_reels":"إنستجرام · ريلز","instagram|instagram_stories":"إنستجرام · ستوري","instagram|instagram_explore":"إنستجرام · استكشاف","instagram|instagram_explore_grid_home":"إنستجرام · استكشاف","instagram|instagram_profile_feed":"إنستجرام · صفحات الحسابات","threads|threads_feed":"ثريدز"};
var PUB={facebook:"فيسبوك",instagram:"إنستجرام",audience_network:"شبكة الشركاء",messenger:"ماسنجر",threads:"ثريدز"};
var GEN={male:"رجال",female:"نساء"};
function bars(title,rows,L){return"<div><h3>"+title+"</h3>"+rows.map(function(r){var sh=L?r.l/L*100:0;return'<div class="xrow"><span class="k">'+esc(r.n)+'</span><span class="v">'+nf0.format(sh)+"% من العملاء · "+(r.l?money(r.s/r.l):"—")+'</span><span class="xb"><span style="width:'+sh.toFixed(1)+'%"></span></span></div>'}).join("")+"</div>"}
var audDone=false;
function audience(){var sec=$("#xaud");if(!sec||audDone)return;if(!A||!(A.age||A.gender||A.place)){sec.hidden=true;return}audDone=true;
 var L=function(x){return(x||[]).reduce(function(s,r){return s+r.l},0)},h="";
 $("#xaudLbl").textContent="Meta"+(A.from&&A.to?" · "+dshort(A.from)+" – "+dshort(A.to):"");
 var age=(A.age||[]).filter(function(r){return/\d/.test(r.k)}).map(function(r){return{n:r.k.replace("-","–")+" سنة",s:r.s,l:r.l}});
 if(age.length)h+=bars("الفئة العمرية",age,L(A.age));
 var gen=(A.gender||[]).filter(function(r){return GEN[r.k]}).map(function(r){return{n:GEN[r.k],s:r.s,l:r.l}});
 if(gen.length)h+=bars("الجنس",gen,L(A.gender));
 var pl=(A.place||[]).slice().sort(function(x,y){return y.l-x.l||y.s-x.s}).slice(0,5).map(function(r){var p=r.k.split("|");return{n:PLACE[r.k]||(PUB[p[0]]||p[0])+(p[0]==="audience_network"?"":" · "+String(p[1]||"").replace(/_/g," ")),s:r.s,l:r.l}});
 if(pl.length)h+=bars("أماكن ظهور الإعلان",pl,L(A.place));
 $("#xaudB").innerHTML=h;
 var T=A.top,le=$("#xaudL");if(T&&T.l>0&&GEN[T.gender]){le.innerHTML="أكثر شريحة تسجيلًا: <b>"+GEN[T.gender]+" "+esc(String(T.age).replace("-","–"))+" سنة</b>، بعدد <b>"+nf0.format(T.l)+" عميلًا محتملًا</b> ("+nf0.format(T.share)+"% من عملاء Meta) وتكلفة "+money(T.cpl)+" للعميل.";le.hidden=false}
 sec.hidden=!h}

function notes(){var N=(M.notes||[]).filter(function(n){return n&&n.d&&n.t&&S.DAYS.indexOf(n.d)>=0}).sort(function(x,y){return x.d<y.d?-1:1});
 var el=$("#trend"),old=$("#xnotes");if(old)old.remove();if(!el||!N.length)return;
 var svg=el.querySelector("svg");if(svg){var W=Math.max(300,el.clientWidth||600),pl=44,bw=(W-78)/S.DAYS.length,NS="http://www.w3.org/2000/svg";
  N.forEach(function(n){var x=pl+S.DAYS.indexOf(n.d)*bw+bw/2,g=document.createElementNS(NS,"path");g.setAttribute("d","M"+(x-5).toFixed(1)+" 1h10l-5 8z");g.setAttribute("fill","var(--brand-orange)");
   var ti=document.createElementNS(NS,"title");ti.textContent=n.d+" · "+n.t;g.appendChild(ti);svg.appendChild(g);
   var ln=document.createElementNS(NS,"line");ln.setAttribute("x1",x.toFixed(1));ln.setAttribute("x2",x.toFixed(1));ln.setAttribute("y1",9);ln.setAttribute("y2",194);ln.setAttribute("stroke","var(--brand-orange)");ln.setAttribute("stroke-dasharray","2 4");ln.setAttribute("opacity",".55");svg.appendChild(ln)})}
 var ul=document.createElement("ul");ul.className="xnotes";ul.id="xnotes";ul.setAttribute("dir","rtl");
 ul.innerHTML=N.slice(-6).map(function(n){return"<li><time>▼ "+dshort(n.d)+"</time><span>"+esc(n.t)+"</span></li>"}).join("");el.parentNode.appendChild(ul)}

function toast(t){var o=document.querySelector(".xtoast");if(o)o.remove();var d=document.createElement("div");d.className="xtoast";d.setAttribute("role","status");d.textContent=t;document.body.appendChild(d);setTimeout(function(){d.remove()},6000)}
function csv(){var s=S,L=[],q=function(v){return'"'+String(v==null?"":v).replace(/"/g,'""')+'"'},n=function(v){return isFinite(v)?Math.round(v*100)/100:""};
 var row=function(a){L.push(a.map(q).join(","))},act=function(x){return/ACTIVE|ENABLE/.test(x)&&!/DISABLE/.test(x)?"نشطة":"متوقفة"};
 row(["تقرير أداء الحملات الإعلانية",D.client||""]);row(["الفترة",s.a,s.b]);row(["المنصة",s.plat==="all"?"كل المنصات":s.PL[s.plat].l]);row(["إعداد","101 Agency"]);row([]);
 row(["الملخص"]);row(["الصرف (ر.س)","العملاء المحتملون","نماذج التسجيل","المحادثات","تكلفة العميل (ر.س)","مرات الظهور","النقرات","نسبة النقر %"]);
 row([n(s.all.s),s.all.res,s.all.f,s.all.m,n(s.all.cpl),s.all.i,s.all.c,n(s.all.ctr)]);row([]);
 row(["المنصات"]);row(["المنصة","الصرف (ر.س)","العملاء المحتملون","تكلفة العميل (ر.س)","مرات الظهور","النقرات"]);
 s.PK.filter(function(k){return s.plat==="all"||s.plat===k}).forEach(function(k){var x=s.by[k];if(x.s)row([s.PL[k].l,n(x.s),x.res,n(x.cpl),x.i,x.c])});row([]);
 row(["الحملات"]);row(["الحملة","المنصة","الحالة","الصرف (ر.س)","نماذج التسجيل","المحادثات","العملاء المحتملون","تكلفة العميل (ر.س)","مرات الظهور","النقرات","نسبة النقر %"]);
 s.camps.forEach(function(c){row([c.name,s.PL[c.p].l,act(c.status),n(c.s),c.f,c.m,c.res,n(c.cpl),c.i,c.c,n(c.ctr)])});row([]);
 row(["السجل اليومي"]);row(["اليوم","الصرف (ر.س)","العملاء المحتملون","تكلفة العميل (ر.س)","مرات الظهور","النقرات"]);
 s.rangeDays(s.a,s.b).forEach(function(d){var t=s.daySum(s.cs,d);row([d,n(t.s),t.res,n(t.cpl),t.i,t.c])});
 var nm="تقرير-"+String(D.client||"الحملات").replace(/[\\/:*?"<>|]/g,"").replace(/\s+/g,"-")+"-"+s.a+"_"+s.b+".csv",tx="﻿"+L.join("\r\n");
 try{if(window.claude&&window.claude.downloads&&window.claude.downloads.save){window.claude.downloads.save({filename:nm,data:tx});return}}catch(e){}
 try{var b=new Blob([tx],{type:"text/csv;charset=utf-8"}),u=URL.createObjectURL(b),a=document.createElement("a");
  a.href=u;a.download=nm;document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},5000);
  toast("جارٍ تحميل ملف Excel للفترة المختارة. إذا لم يبدأ التحميل، افتح التقرير في المتصفح مباشرة.")}catch(e){toast("تعذّر التحميل من هذه النافذة. افتح التقرير في المتصفح مباشرة ثم أعد المحاولة.")}}
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-x]");if(!b||!S)return;var k=b.getAttribute("data-x");
 if(k==="apply")apply();else if(k==="csv")csv();else if(k==="pdf")pdf()});

/* real PDF file: every section is captured as an image and laid out on pages (no print dialog needed) */
var busy=false;
function load(u){return new Promise(function(ok,no){var s=document.createElement("script");s.src=u;s.onload=ok;s.onerror=no;document.head.appendChild(s)})}
function lib(test,local,cdn){return test()?Promise.resolve():load(local).catch(function(){return load(cdn)})}
function printPdf(){toast("اختر «حفظ بصيغة PDF» من نافذة الطباعة لتحميل تقرير الفترة المختارة.");setTimeout(function(){try{window.print()}catch(x){}},350)}
function cuts(el){var t0=el.getBoundingClientRect().top,o=[];[].forEach.call(el.querySelectorAll(".cre,.panel,tr,li,.pcard,.xtile,.xstep,.cmp,.kpi,.itile,.hl-card,.xrow"),function(c){var r=c.getBoundingClientRect();if(r.height>0)o.push(r.bottom-t0+6)});return o.sort(function(a,b){return a-b})}
function pdf(){if(busy)return;
 if(/claudeusercontent\.com$/.test(location.hostname)){toast("تحميل PDF يعمل من رابط التقرير المباشر في المتصفح، وليس من داخل هذه النافذة.");return}
 busy=true;var test=location.hash==="#xpdftest",xp=$("#xprint"),stick=function(m){toast(m);var d=document.querySelector(".xtoast");return d};
 toast("جارٍ تجهيز ملف PDF للفترة المختارة… قد يستغرق بضع ثوانٍ.");
 lib(function(){return window.modernScreenshot},"../assets/modern-screenshot.js","https://cdn.jsdelivr.net/npm/modern-screenshot@4.7.0/dist/index.js")
 .then(function(){return lib(function(){return window.jspdf},"../assets/jspdf.umd.min.js","https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js")})
 .then(function(){
  var wrap=document.querySelector("main .wrap");if(xp)xp.style.display="block";
  var db=$("#dailyBox"),wasOpen=db&&db.open;if(db)db.open=true;
  var blocks=[].filter.call(wrap.children,function(el){return!el.hidden&&!el.classList.contains("toolbar")&&el.id!=="xrange"&&el.offsetHeight>0});
  var W=Math.round(wrap.clientWidth),sc=W>900?1.5:2,bg=getComputedStyle(document.body).backgroundColor,mg=16,gap=12,PW=W+mg*2,PH=Math.round(PW*1.414),av=PH-mg*2;
  var rgb=(bg.match(/\d+/g)||[13,14,17]).map(Number);
  var doc=new window.jspdf.jsPDF({unit:"px",format:[PW,PH],hotfixes:["px_scaling"],compress:true}),y=mg,pages=1,shots=[];
  var paint=function(){doc.setFillColor(rgb[0],rgb[1],rgb[2]);doc.rect(0,0,PW,PH,"F")},page=function(){doc.addPage([PW,PH]);pages++;paint();y=mg};paint();
  var put=function(c,from,h){var k=document.createElement("canvas");k.width=c.width;k.height=Math.round(h*sc);var x=k.getContext("2d");x.fillStyle=bg;x.fillRect(0,0,k.width,k.height);x.drawImage(c,0,Math.round(from*sc),c.width,k.height,0,0,c.width,k.height);
   doc.addImage(k.toDataURL("image/jpeg",.86),"JPEG",mg,y,c.width/sc,h,undefined,"FAST");y+=h+gap};
  var i=0,next=function(){if(i>=blocks.length)return Promise.resolve();var el=blocks[i++];
   return window.modernScreenshot.domToCanvas(el,{scale:sc,backgroundColor:bg,timeout:8000,fetch:{placeholderImage:"data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}}).then(function(c){
    if(test)shots.push(c);var h=c.height/sc;
    if(h<=av){if(y+h>PH-mg)page();put(c,0,h)}
    else{var cs=cuts(el),off=0;if(y>mg+av*.35)page();
     while(off<h-1){var room=PH-mg-y,lim=off+room,cut=h<=lim?h:0;if(!cut){for(var j=0;j<cs.length;j++)if(cs[j]<=lim&&cs[j]>off+room*.35)cut=cs[j];if(!cut)cut=lim}
      put(c,off,cut-off);off=cut;if(off<h-1)page()}}
    return next()})};
  return next().then(function(){if(xp)xp.style.display="";if(db)db.open=wasOpen;
   var nm="تقرير-"+String(D.client||"الحملات").replace(/[\\/:*?"<>|]/g,"").replace(/\s+/g,"-")+"-"+S.a+"_"+S.b+".pdf",blob=doc.output("blob");
   if(test){var o=document.createElement("div");o.style.cssText="position:fixed;inset:0;z-index:99;background:#333;overflow:auto;padding:10px;direction:ltr";o.innerHTML="<p style='color:#fff'>PDF test: "+pages+" pages, "+Math.round(blob.size/1024)+" KB, "+shots.length+" blocks</p>";shots.forEach(function(c){c.style.cssText="width:48%;margin:1%;vertical-align:top";o.appendChild(c)});document.body.appendChild(o);return}
   var u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download=nm;document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},8000);
   toast("تم تجهيز ملف PDF ("+pages+" صفحة) وبدأ التحميل.")})})
 .catch(function(e){if(xp)xp.style.display="";printPdf()}).then(function(){busy=false})}

})();
</script>
"""

def sub(old, new, label):
    global t
    if t.count(old) != 1:
        sys.exit("anchor not unique or missing: " + label + " (" + str(t.count(old)) + ")")
    t = t.replace(old, new)

sub(TOOLBAR_OLD, TOOLBAR_NEW, "toolbar")
sub(SECS_ANCHOR, SECS + SECS_ANCHOR, "sections")
sub(HOOK_OLD, HOOK_NEW, "render hook")
sub(INIT_OLD, INIT_NEW, "init hook")
sub(CRE_OLD, CRE_NEW, "creative card")
sub("<!--DATA-END-->", "<!--DATA-END-->\n" + CSS + JS, "data end")
open(out, "w", encoding="utf8").write(t)
print("patched", out)
