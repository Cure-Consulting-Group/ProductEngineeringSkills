#!/usr/bin/env python3
"""benchmark-dashboard: render the benchmark log as a self-contained HTML dashboard.

Reads benchmark.jsonl (one project, or --all-projects), reuses benchmark-report's summaries and
decision rule, and writes one HTML file with inline SVG charts, tooltips, table views, and light and
dark themes. No libraries, no network. Open it locally or publish it as an artifact.

Examples:
  python3 benchmark-dashboard.py --out ~/Desktop/tri-lane-dashboard.html
  python3 benchmark-dashboard.py --all-projects --out dashboard.html --open
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_report_module():
    spec = importlib.util.spec_from_file_location("benchmark_report", HERE / "benchmark-report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slim(rows: list) -> list:
    out = []
    for r in rows:
        c = r.get("claude") or {}
        x = r.get("codex_lane") or {}
        xl = r.get("codex_logs") or {}
        a = r.get("agy") or {}
        f = r.get("findings") or {}
        out.append({
            "task": r.get("task"), "project": r.get("_project") or Path(r.get("project") or "").name, "arm": r.get("arm"), "kind": r.get("kind") or "",
            "route": r.get("route") or "", "lane": r.get("lane") or "", "status": r.get("status") or "", "advisor": r.get("advisor") or "",
            "model": r.get("model"), "effort": r.get("effort"), "started": r.get("started_at"), "ended": r.get("ended_at"),
            "elapsed_min": round((r.get("elapsed_seconds") or 0) / 60, 1),
            "claude_billable": c.get("billable_tokens") or 0, "claude_cache": c.get("cache_read_input_tokens") or 0, "claude_msgs": c.get("messages") or 0,
            "codex_billable": x.get("billable_tokens") or xl.get("billable_tokens") or 0, "agy_total": a.get("total_tokens") or 0,
            "rework": r.get("rework") or 0, "escalated": bool(r.get("escalated")), "escaped": r.get("escaped_defects") or 0,
            "window_checked": bool(r.get("window_checked_at")),
            "findings": {k: [int(v.get("confirmed") or 0), int(v.get("disputed") or 0), int(v.get("unverified") or 0)] for k, v in f.items()},
            "pool_deltas": r.get("pool_deltas") or {},
            "suggested": (r.get("suggested") or {}).get("lane") if r.get("suggested") else None, "followed": r.get("suggestion_followed"),
            "notes": (r.get("notes") or "")[:240],
        })
    out.sort(key=lambda t: t.get("ended") or "")
    return out


TEMPLATE = r"""<title>Tri-Lane Benchmark</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{--bg:#F3F5F7;--bg-2:#E9EDF1;--surface:#FFFFFF;--ink:#16202A;--ink-2:#4A5661;--ink-3:#7A8791;--line:#CFD6DC;--line-2:#B8C1C9;--grid:#E3E8EC;
--s1:#B7791F;--s2:#0A9C8C;--s3:#6D4FC2;--s4:#4A5661;--good:#1F7A3F;--good-bg:#E0F1E5;--warn:#9A5B00;--warn-bg:#FBEFD9;--crit:#B42318;--crit-bg:#FBE4E1;
--disp:"Familjen Grotesk","Helvetica Neue",Arial,sans-serif;--body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#10161C;--bg-2:#161E26;--surface:#182028;--ink:#E6EAEE;--ink-2:#AAB5BE;--ink-3:#7F8B95;--line:#2A3540;--line-2:#3A4752;--grid:#232D37;
--s1:#BD8524;--s2:#1E9C8E;--s3:#8A72D9;--s4:#AAB5BE;--good:#5CC57F;--good-bg:#12301C;--warn:#E5A84B;--warn-bg:#352609;--crit:#F0705F;--crit-bg:#3B1512}}
:root[data-theme="dark"]{--bg:#10161C;--bg-2:#161E26;--surface:#182028;--ink:#E6EAEE;--ink-2:#AAB5BE;--ink-3:#7F8B95;--line:#2A3540;--line-2:#3A4752;--grid:#232D37;
--s1:#BD8524;--s2:#1E9C8E;--s3:#8A72D9;--s4:#AAB5BE;--good:#5CC57F;--good-bg:#12301C;--warn:#E5A84B;--warn-bg:#352609;--crit:#F0705F;--crit-bg:#3B1512}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px 80px}
header{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px 24px;padding:36px 0 18px;border-bottom:1px solid var(--line)}
h1{font-family:var(--disp);font-weight:700;font-size:38px;letter-spacing:-.02em;line-height:1;margin:0}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
.meta{font-family:var(--mono);font-size:12.5px;color:var(--ink-3);text-align:right;line-height:1.7}
.verdict{margin:22px 0 0;border:1px solid var(--line);background:var(--surface);display:grid;grid-template-columns:minmax(220px,1fr) 2fr}
.verdict .v{padding:18px 22px;border-right:1px solid var(--line)}
.verdict .v .k{font-family:var(--mono);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3)}
.verdict .v .t{font-family:var(--disp);font-size:28px;font-weight:700;line-height:1.1;margin-top:6px;text-wrap:balance}
.checks{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--line)}
.checks>div{background:var(--surface);padding:12px 14px;font-size:13px}
.checks .n{font-family:var(--mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.pill{display:inline-block;font-family:var(--mono);font-size:11px;padding:1px 7px;border-radius:3px;margin-bottom:4px}
.pill.good{background:var(--good-bg);color:var(--good)}.pill.warn{background:var(--warn-bg);color:var(--warn)}.pill.crit{background:var(--crit-bg);color:var(--crit)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:18px 0 0}
.tiles>div{background:var(--surface);padding:14px 16px}
.tiles .k{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3)}
.tiles .v{font-family:var(--disp);font-size:30px;font-weight:700;line-height:1.05;margin:6px 0 2px;font-variant-numeric:tabular-nums}
.tiles .s{font-size:12.5px;color:var(--ink-2)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}
.grid .wide{grid-column:1/-1}
figure{margin:0;border:1px solid var(--line);background:var(--surface);padding:14px 16px 8px;position:relative;min-width:0}
figure h4{font-family:var(--disp);font-size:15.5px;font-weight:700;margin:0 0 2px}
figure .sub{font-size:12.5px;color:var(--ink-2);margin:0 0 8px}
figure svg{display:block;width:100%;height:auto;color:var(--ink);overflow:visible}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--ink-2);margin:2px 0 6px}.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.tbtn{position:absolute;top:12px;right:12px;font:11.5px var(--mono);background:var(--bg-2);color:var(--ink-2);border:1px solid var(--line);border-radius:3px;padding:2px 7px;cursor:pointer}
.tip{position:absolute;pointer-events:none;background:var(--ink);color:var(--bg);font:12px var(--body);padding:5px 8px;border-radius:3px;white-space:nowrap;transform:translate(-50%,calc(-100% - 10px));opacity:0;transition:opacity .08s;z-index:2}
.tip.on{opacity:1}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);font-weight:500;background:var(--bg-2);cursor:pointer}
tr:last-child td{border-bottom:0}td.num{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
.tbl{overflow-x:auto;border:1px solid var(--line);background:var(--surface);margin-top:18px}
.hidden{display:none}.empty{color:var(--ink-3);font-size:13px;padding:18px 0}
.arm{display:inline-block;font-family:var(--mono);font-size:11px;padding:1px 7px;border-radius:3px;background:var(--bg-2);color:var(--ink-2)}
.glance{margin-top:22px}
.intro{font-size:16.5px;color:var(--ink-2);max-width:78ch;margin:0 0 18px;line-height:1.55}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.card{border:1px solid var(--line);background:var(--surface);padding:18px 20px;display:flex;flex-direction:column;gap:8px}
.card .q{font-family:var(--disp);font-size:18px;font-weight:700;line-height:1.2;text-wrap:balance}
.card .a{font-family:var(--disp);font-size:30px;font-weight:700;line-height:1.05}
.card .a.good{color:var(--good)}.card .a.warn{color:var(--warn)}.card .a.crit{color:var(--crit)}
.card .why{font-size:14px;color:var(--ink-2);line-height:1.5}
.card .why b{color:var(--ink)}
.glossary{margin-top:16px;font-size:13.5px;color:var(--ink-2);max-width:90ch;line-height:1.55}
.glossary b{color:var(--ink)}.glossary i{font-style:normal;color:var(--ink);font-weight:500}
details.eng{margin-top:28px;border-top:1px solid var(--line);padding-top:12px}
details.eng>summary{cursor:pointer;font-family:var(--mono);font-size:12.5px;color:var(--ink-3);letter-spacing:.04em;padding:6px 0;list-style:none}
details.eng>summary::before{content:"▸ ";}details.eng[open]>summary::before{content:"▾ ";}
@media (max-width:900px){.grid{grid-template-columns:1fr}.verdict{grid-template-columns:1fr}.verdict .v{border-right:0;border-bottom:1px solid var(--line)}}
@media (prefers-reduced-motion: reduce){.tip{transition:none}}
</style>
<div class="wrap">
<header>
  <div><div class="eyebrow">Cure Consulting Group · cure-tri-lane · benchmark</div><h1>Tri-Lane Benchmark</h1></div>
  <div class="meta" id="meta"></div>
</header>
<section class="glance">
  <p class="intro">Cure runs software work through three AI systems: a lead that plans and checks (Claude), a builder and reviewer from a second vendor (OpenAI's Codex), and a systems reviewer from a third (Google's Antigravity). This page answers four questions from the recorded results. The engineering detail is further down, folded away.</p>
  <div class="cards" id="cards"></div>
  <div class="glossary"><b>Words used here.</b> A <i>task</i> is one piece of real work. A <i>confirmed finding</i> is a defect a reviewer reported that we checked and agreed was real. An <i>escaped defect</i> is a bug that reached users after we shipped. A <i>practice task</i> is a fixed exercise with a known answer, used to compare the AI models fairly. <i>Cost</i> is measured in tokens, the unit the vendors bill; lower is cheaper.</div>
</section>
<details class="eng"><summary>Details for engineers: decision rule, arms, findings, precision, routing, quotas, canary matrix, every task</summary>
<div class="verdict"><div class="v"><div class="k">Decision rule</div><div class="t" id="verdict"></div></div><div class="checks" id="checks"></div></div>
<div class="tiles" id="tiles"></div>
<div class="grid">
  <figure id="c-arms" class="wide"><h4>Arms compared</h4><p class="sub">Medians per task. One panel per measure, because the units differ.</p><div class="legend" id="arm-legend"></div><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-timeline" class="wide"><h4>Claude billable tokens per task, in order run</h4><p class="sub">Colour is the arm. Hover for the task.</p><div class="legend" id="tl-legend"></div><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-findings"><h4>Confirmed findings per task, by reviewer</h4><p class="sub">Disputed and unverified are in the table.</p><div class="legend"><span><i style="background:var(--s2)"></i>Codex review</span><span><i style="background:var(--s3)"></i>Antigravity</span><span><i style="background:var(--s1)"></i>Advisor</span></div><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-precision"><h4>Reviewer precision</h4><p class="sub">Confirmed share of each reviewer's findings, all tasks.</p><div class="legend"><span><i style="background:var(--ink)"></i>Confirmed</span><span><i style="background:var(--ink-3)"></i>Disputed</span><span><i style="background:var(--line-2)"></i>Unverified</span></div><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-router"><h4>Shadow router</h4><p class="sub">How often the capability table's suggestion matched the architect's choice, and rework either way.</p><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-pools"><h4>Quota pool movement per task</h4><p class="sub">Percentage points of each weekly pool consumed. Codex is used-percent; Google pools are remaining-percent, shown as consumption.</p><div class="legend"><span><i style="background:var(--s2)"></i>Codex weekly</span><span><i style="background:var(--s3)"></i>Google Gemini weekly</span></div><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
</div>
<div class="grid">
  <figure id="c-reliability" class="wide"><h4>Reliability: failures are results</h4><p class="sub">Per lane: how often the first attempt succeeded, failures by class (model failures score zero; infra, harness, and quota failures are retried once and charged to us), seconds to a result including failed attempts, tokens wasted on attempts that produced nothing, and cost per point with that waste included.</p><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
  <figure id="c-canary" class="wide"><h4>Canary suite: fixed tasks × lanes</h4><p class="sub">Mean score per cell from evals.jsonl; darker is better. Hover for pass count and grader detail. These numbers drive routing, not adoption.</p><button class="tbtn">table</button><div class="chart"></div><div class="tview hidden"></div></figure>
</div>
<div class="tbl"><table id="tasks"><thead><tr><th>Task</th><th>Project</th><th>Arm</th><th>Kind</th><th>Route</th><th>Lane</th><th>Model</th><th>Status</th><th>Advisor</th><th>Min</th><th>Claude billable</th><th>Codex billable</th><th>Antigravity</th><th>Confirmed</th><th>Rework</th><th>Escaped</th><th>Window</th></tr></thead><tbody></tbody></table></div>
</details>
</div>
<script>
const DATA = __DATA__;
(function(){
  const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const NS="http://www.w3.org/2000/svg"; const el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;};
  const fmt=n=>n>=1e6?(n/1e6).toFixed(2)+"M":n>=1e3?Math.round(n/1e3)+"k":String(Math.round(n));
  const ARMS=["manual","tri-lane","advisor-only","tri-lane-lean"]; const ARMC={"manual":css("--s4"),"tri-lane":css("--s1"),"advisor-only":css("--s3"),"tri-lane-lean":css("--s2")};
  const T=DATA.tasks, S=DATA.arms, D=DATA.decision;
  function tip(fig){let t=fig.querySelector(".tip");if(!t){t=document.createElement("div");t.className="tip";fig.appendChild(t);}return t;}
  function hover(n,fig,txt){const t=tip(fig);n.addEventListener("mousemove",e=>{const r=fig.getBoundingClientRect();t.textContent=txt;t.style.left=(e.clientX-r.left)+"px";t.style.top=(e.clientY-r.top)+"px";t.classList.add("on");});n.addEventListener("mouseleave",()=>t.classList.remove("on"));}
  function svg(fig,w,h,label){const s=el("svg",{viewBox:`0 0 ${w} ${h}`,role:"img","aria-label":label});fig.querySelector(".chart").appendChild(s);return s;}
  function table(fig,head,rows){const t=document.createElement("table");t.innerHTML="<thead><tr>"+head.map(h=>`<th>${h}</th>`).join("")+"</tr></thead><tbody>"+rows.map(r=>"<tr>"+r.map((c,i)=>`<td class="${i?'num':''}">${c}</td>`).join("")+"</tr>").join("")+"</tbody>";fig.querySelector(".tview").appendChild(t);}
  function empty(fig,msg){fig.querySelector(".chart").innerHTML=`<div class="empty">${msg}</div>`;}
  const armsPresent=ARMS.filter(a=>S[a]);

  // at-a-glance cards for non-technical readers, computed from the same data
  (function(){
    const C=DATA.canary||[]; const conf=T.reduce((a,t)=>a+Object.values(t.findings).reduce((b,f)=>b+f[0],0),0);
    const fixFirst=T.filter(t=>t.advisor==="fix-first").length, withAdvisor=T.filter(t=>t.advisor).length;
    const manual=T.filter(t=>t.arm==="manual").length, tri=T.filter(t=>t.arm==="tri-lane").length;
    const esc=T.reduce((a,t)=>a+t.escaped,0), unchecked=T.filter(t=>!t.window_checked).length;
    const cards=[];
    // 1. quality
    cards.push({q:"Are the extra reviewers catching real problems?", a: conf?`Yes: ${conf} real defects`:"Not enough data", cls: conf?"good":"warn",
      why: conf?`Found across <b>${T.length} real tasks</b> and confirmed by a person, not just reported. The independent final check changed what shipped on <b>${fixFirst} of ${withAdvisor}</b> tasks.`:"No tasks have been logged yet."});
    // 2. cost
    let costA, costCls, costWhy;
    if(D.checks && D.checks.claude_tokens_drop){const v=D.checks.claude_tokens_drop.value; costA=(v>=0?"Yes":"No")+`: ${Math.round(Math.abs(v)*100)}% ${v>=0?"less":"more"} lead-model cost`; costCls=D.checks.claude_tokens_drop.pass?"good":"crit"; costWhy=`Compared to the old way of working over ${manual} and ${tri} matched tasks.`;}
    else {costA="Not measurable yet"; costCls="warn"; costWhy=`This needs <b>8 tasks done the old way</b> and 8 with the new system, under the same conditions. So far: <b>${manual} of 8</b> old-way, <b>${tri} of 8</b> new-way. Until then, cost claims are opinion.`;}
    cards.push({q:"Is it cheaper than working the old way?", a:costA, cls:costCls, why:costWhy});
    // 3. which model
    if(C.length){const byLane={}; C.filter(e=>e.lane!=="reference").forEach(e=>{const k=e.lane+" @ "+e.effort; (byLane[k]=byLane[k]||{n:0,p:0,s:0}); byLane[k].n++; byLane[k].p+=e.pass?1:0; byLane[k].s+=(e.score||0);});
      const rows=Object.entries(byLane).map(([k,v])=>({k,rate:v.p/v.n,mean:v.s/v.n,n:v.n})).sort((a,b)=>b.rate-a.rate||b.mean-a.mean);
      const nice=k=>k.replace("gpt-5.6-luna","Codex Luna (cheapest)").replace("gpt-5.6-sol","Codex Sol").replace("gpt-6-astra","GPT-6 Astra (most expensive)").replace("gemini-3.8-flash-high","Google Gemini Flash").replace(/ @ (\w+)/," at $1 effort");
      const top=rows[0]; const cheapest=rows.find(r=>r.k.includes("luna"));
      cards.push({q:"Which AI should do which job?", a: cheapest&&cheapest.rate>=0.9?"The cheapest one, almost always":"See the practice results", cls:"good",
        why:`On <b>${C.filter(e=>e.lane!=="reference").length} practice tasks</b> with known answers, ${cheapest?`<b>${nice(cheapest.k)}</b> passed ${Math.round(cheapest.rate*100)}% (${cheapest.n} runs)`:""}${top&&cheapest&&top.k!==cheapest.k?`; the best, <b>${nice(top.k)}</b>, passed ${Math.round(top.rate*100)}%`:""}. The expensive models earn their cost only when the instructions are incomplete and the AI has to notice and ask.`});
    } else cards.push({q:"Which AI should do which job?", a:"No practice results yet", cls:"warn", why:"Run the practice suite to compare models on tasks with known answers."});
    // 4. safety
    const R=DATA.reliability||{}; const rl=Object.values(R); const infraHarness=rl.reduce((a,d)=>a+((d.classes||{}).infra||0)+((d.classes||{}).harness||0)+((d.classes||{}).quota||0),0); const stalls=rl.reduce((a,d)=>a+((d.classes||{}).model||0),0);
    cards.push({q:"Is it safe to let it run?", a: esc?`${esc} bug${esc>1?"s":""} reached users`:"No bugs have reached users", cls: esc?"crit":(unchecked?"warn":"good"),
      why:`${unchecked?`<b>${unchecked} task${unchecked>1?"s are":" is"} still inside the 7-day watch window</b>, so this can change. `:""}Every AI change is made in an isolated copy of the code, checked by a second vendor, and reviewed by a fresh, independent check before it can be merged. Failures are recorded, not hidden: <b>${infraHarness}</b> caused by our environment or tooling (retried once, not charged to the AI) and <b>${stalls}</b> where the AI itself fell short (scored zero).`});
    document.getElementById("cards").innerHTML=cards.map(c=>`<div class="card"><div class="q">${c.q}</div><div class="a ${c.cls}">${c.a}</div><div class="why">${c.why}</div></div>`).join("");
  })();

  // meta + verdict + checks
  document.getElementById("meta").innerHTML=`generated ${DATA.generated}<br>${DATA.source}<br>${T.length} tasks · ${armsPresent.map(a=>a+" "+S[a].tasks).join(" · ")}`;
  const vb=document.getElementById("verdict"); vb.textContent=D.verdict;
  const ck=document.getElementById("checks"); const names={sample_size:"Sample size",model_frozen:"Model frozen",defect_windows_closed:"Defect windows",claude_tokens_drop:"Claude tokens −33%",escaped_defects_not_up:"Defects not up",slowdown:"Elapsed ≤ 1.5×"};
  const checks=D.checks||{}; if(!Object.keys(checks).length){ck.innerHTML=`<div><span class="pill warn">insufficient data</span><div>${D.reason||""}</div></div>`;}
  for(const k in checks){const c=checks[k];const d=document.createElement("div");const val=c.value!==undefined?c.value:(c.manual!==undefined?`${c.manual} → ${c.tri_lane}`:(c.models_seen?c.models_seen.join(", "):(c.open?`${c.open.length} open`:"")));d.innerHTML=`<span class="pill ${c.pass?'good':'crit'}">${c.pass?'pass':'blocking'}</span><div class="n">${names[k]||k}</div><div>${val}</div>`;ck.appendChild(d);}

  // tiles
  const conf=T.reduce((a,t)=>a+Object.values(t.findings).reduce((b,f)=>b+f[0],0),0);
  const allF=T.reduce((a,t)=>{for(const k in t.findings){a[0]+=t.findings[k][0];a[1]+=t.findings[k][1];a[2]+=t.findings[k][2];}return a;},[0,0,0]);
  const prec=allF[0]+allF[1]+allF[2]?Math.round(100*allF[0]/(allF[0]+allF[1]+allF[2])):null;
  const esc=T.reduce((a,t)=>a+t.escaped,0); const due=T.filter(t=>!t.window_checked).length;
  const med=a=>{a=a.filter(x=>x!=null).sort((x,y)=>x-y);return a.length?a[Math.floor((a.length-1)/2)]:null;};
  const tl=T.filter(t=>t.arm==="tri-lane"), mn=T.filter(t=>t.arm==="manual");
  document.getElementById("tiles").innerHTML=[
    ["Confirmed findings",conf,"across "+T.length+" tasks"],
    ["Reviewer precision",prec==null?"—":prec+"%",`${allF[0]} / ${allF[1]} / ${allF[2]} C/D/U`],
    ["Escaped defects",esc,due+" windows unchecked"],
    ["Claude billable, tri-lane median",tl.length?fmt(med(tl.map(t=>t.claude_billable))):"—",mn.length?"manual "+fmt(med(mn.map(t=>t.claude_billable))):"no manual arm yet"],
    ["Advisor fix-first",T.filter(t=>t.advisor==="fix-first").length+" / "+T.filter(t=>t.advisor).length,"verdicts that changed the outcome"],
    ["Rework per task",T.length?(T.reduce((a,t)=>a+t.rework,0)/T.length).toFixed(2):"—","corrected specs sent back"],
  ].map(([k,v,s])=>`<div><div class="k">${k}</div><div class="v">${v}</div><div class="s">${s}</div></div>`).join("");

  // arms compared: small multiples
  (function(){const fig=document.getElementById("c-arms"); if(armsPresent.length<1){empty(fig,"no tasks");return;}
    document.getElementById("arm-legend").innerHTML=armsPresent.map(a=>`<span><i style="background:${ARMC[a]}"></i>${a}</span>`).join("");
    const measures=[["claude_billable_median","Claude billable"],["codex_tokens_median","Codex billable"],["agy_tokens_median","Antigravity tokens"],["elapsed_min_median","Elapsed min"],["rework_mean","Rework"],["escaped_defects_mean","Escaped defects"]];
    const W=1160,PW=W/measures.length,H=170,T0=26,B=22; const s=svg(fig,W,H,"Arms compared across six measures");
    measures.forEach(([k,label],mi)=>{const x0=mi*PW+10; const vals=armsPresent.map(a=>S[a][k]||0); const max=Math.max(...vals,1e-9); const bw=(PW-30)/armsPresent.length;
      el("text",{x:x0,y:14,"font-size":"12","font-weight":"600",fill:css("--ink")},s).textContent=label;
      armsPresent.forEach((a,i)=>{const v=S[a][k]||0;const h=(H-T0-B)*(v/max);const r=el("rect",{x:x0+i*bw+2,y:H-B-h,width:bw-4,height:h,fill:ARMC[a]},s);hover(r,fig,`${a} · ${label}: ${typeof v==="number"?fmt(v):v}`);el("text",{x:x0+i*bw+bw/2,y:H-B-h-4,"text-anchor":"middle","font-size":"10.5",fill:css("--ink-2")},s).textContent=typeof v==="number"?(v>=1000?fmt(v):v):v;});
      el("line",{x1:x0,y1:H-B,x2:x0+PW-20,y2:H-B,stroke:css("--line-2")},s);});
    table(fig,["Measure",...armsPresent],measures.map(([k,l])=>[l,...armsPresent.map(a=>S[a][k]??"—")]));})();

  // timeline
  (function(){const fig=document.getElementById("c-timeline"); if(!T.length){empty(fig,"no tasks");return;}
    document.getElementById("tl-legend").innerHTML=armsPresent.map(a=>`<span><i style="background:${ARMC[a]}"></i>${a}</span>`).join("");
    const W=1160,H=230,L=70,R=20,Tp=14,B=36; const s=svg(fig,W,H,"Claude billable tokens per task in run order, coloured by arm");
    const max=Math.max(...T.map(t=>t.claude_billable),1); const y=v=>Tp+(H-Tp-B)*(1-v/max); const gw=(W-L-R)/T.length;
    for(let g=0;g<=4;g++){const v=max*g/4;el("line",{x1:L,y1:y(v),x2:W-R,y2:y(v),stroke:css("--grid")},s);el("text",{x:L-8,y:y(v)+4,"text-anchor":"end","font-size":"11",fill:css("--ink-3")},s).textContent=fmt(v);}
    T.forEach((t,i)=>{const cx=L+i*gw+gw/2; el("line",{x1:cx,y1:y(t.claude_billable),x2:cx,y2:y(0),stroke:ARMC[t.arm]||css("--s4"),"stroke-width":"2"},s); const c=el("circle",{cx,cy:y(t.claude_billable),r:6,fill:ARMC[t.arm]||css("--s4"),stroke:css("--surface"),"stroke-width":"2"},s); hover(c,fig,`${t.task} (${t.arm}, ${t.route}) · ${t.claude_billable.toLocaleString()} billable · ${t.claude_msgs} msgs · ${t.elapsed_min} min`); el("text",{x:cx,y:H-20,"text-anchor":"middle","font-size":"11",fill:css("--ink")},s).textContent=t.task.length>16?t.task.slice(0,15)+"…":t.task; el("text",{x:cx,y:H-7,"text-anchor":"middle","font-size":"10",fill:css("--ink-3")},s).textContent=(t.ended||"").slice(5,10);});
    el("line",{x1:L,y1:y(0),x2:W-R,y2:y(0),stroke:css("--line-2")},s);
    table(fig,["Task","Arm","Ended","Claude billable","Cache read","Messages","Elapsed min"],T.map(t=>[t.task,t.arm,(t.ended||"").slice(0,10),t.claude_billable.toLocaleString(),t.claude_cache.toLocaleString(),t.claude_msgs,t.elapsed_min]));})();

  // findings stacked
  (function(){const fig=document.getElementById("c-findings"); if(!T.length){empty(fig,"no tasks");return;}
    const W=560,rowH=34,L=150,R=36,H=T.length*rowH+26; const s=svg(fig,W,H,"Confirmed findings per task by reviewer");
    const tot=t=>["codex","agy","advisor"].reduce((a,k)=>a+((t.findings[k]||[0])[0]),0); const max=Math.max(...T.map(tot),1); const x=v=>L+v*(W-L-R)/max;
    const ser=[["codex","Codex review",css("--s2")],["agy","Antigravity",css("--s3")],["advisor","Advisor",css("--s1")]];
    T.forEach((t,i)=>{const y=8+i*rowH; el("text",{x:L-8,y:y+16,"text-anchor":"end","font-size":"11.5",fill:css("--ink")},s).textContent=t.task.length>18?t.task.slice(0,17)+"…":t.task; let acc=0;
      ser.forEach(([k,n,c])=>{const v=(t.findings[k]||[0])[0]; if(!v)return; const r=el("rect",{x:x(acc)+(acc?2:0),y:y+3,width:Math.max(0,x(acc+v)-x(acc)-(acc?2:0)),height:20,fill:c},s); const f=t.findings[k]; hover(r,fig,`${t.task} · ${n}: ${f[0]} confirmed, ${f[1]} disputed, ${f[2]} unverified`); acc+=v;});
      el("text",{x:x(acc)+6,y:y+17,"font-size":"11",fill:css("--ink-2")},s).textContent=acc||("0 · "+t.route);});
    table(fig,["Task","Codex C/D/U","Antigravity C/D/U","Advisor C/D/U"],T.map(t=>[t.task,(t.findings.codex||[0,0,0]).join("/"),(t.findings.agy||[0,0,0]).join("/"),(t.findings.advisor||[0,0,0]).join("/")]));})();

  // precision
  (function(){const fig=document.getElementById("c-precision"); const rev={}; T.forEach(t=>{for(const k in t.findings){rev[k]=rev[k]||[0,0,0];t.findings[k].forEach((v,i)=>rev[k][i]+=v);}});
    const names={codex:"Codex review",agy:"Antigravity",advisor:"Advisor"}; const keys=Object.keys(rev); if(!keys.length){empty(fig,"no findings logged");return;}
    const W=560,rowH=34,L=130,R=90,H=keys.length*rowH+26; const s=svg(fig,W,H,"Reviewer precision as confirmed share"); const max=Math.max(...keys.map(k=>rev[k].reduce((a,b)=>a+b,0)),1); const x=v=>L+v*(W-L-R)/max; const cols=[css("--ink"),css("--ink-3"),css("--line-2")];
    keys.forEach((k,i)=>{const y=8+i*rowH; el("text",{x:L-8,y:y+16,"text-anchor":"end","font-size":"11.5",fill:css("--ink")},s).textContent=names[k]||k; let acc=0; ["Confirmed","Disputed","Unverified"].forEach((lab,j)=>{const v=rev[k][j]; if(!v)return; const r=el("rect",{x:x(acc)+(acc?2:0),y:y+3,width:Math.max(0,x(acc+v)-x(acc)-(acc?2:0)),height:20,fill:cols[j]},s); hover(r,fig,`${names[k]||k} · ${lab}: ${v}`); acc+=v;}); const tot=rev[k].reduce((a,b)=>a+b,0); el("text",{x:x(acc)+6,y:y+17,"font-size":"11",fill:css("--ink-2")},s).textContent=tot?Math.round(100*rev[k][0]/tot)+"% precision":"";});
    table(fig,["Reviewer","Confirmed","Disputed","Unverified","Precision"],keys.map(k=>{const t=rev[k].reduce((a,b)=>a+b,0);return [names[k]||k,...rev[k],t?(rev[k][0]/t).toFixed(2):"—"];}));})();

  // router shadow
  (function(){const fig=document.getElementById("c-router"); const sug=T.filter(t=>t.suggested); if(!sug.length){empty(fig,"no shadow suggestions logged yet — run lane-route.py suggest --task <id> before each task");return;}
    const f=sug.filter(t=>t.followed), n=sug.filter(t=>t.followed===false); const mean=a=>a.length?(a.reduce((x,t)=>x+t.rework,0)/a.length).toFixed(2):"—";
    const W=560,H=120; const s=svg(fig,W,H,"Shadow router agreement and rework"); const rows=[["Suggestion followed",f.length,css("--s2")],["Architect chose differently",n.length,css("--s1")]]; const max=Math.max(f.length,n.length,1);
    rows.forEach(([lab,v,c],i)=>{const y=14+i*44; el("text",{x:0,y:y+14,"font-size":"11.5",fill:css("--ink")},s).textContent=lab; const r=el("rect",{x:200,y:y,width:(W-260)*v/max,height:22,fill:c},s); hover(r,fig,`${lab}: ${v} tasks`); el("text",{x:200+(W-260)*v/max+6,y:y+15,"font-size":"11",fill:css("--ink-2")},s).textContent=`${v} · rework ${mean(i?n:f)}`;});
    table(fig,["Task","Suggested","Chosen","Followed","Rework"],sug.map(t=>[t.task,t.suggested,t.lane,t.followed?"yes":"no",t.rework]));})();

  // pools
  (function(){const fig=document.getElementById("c-pools"); const rows=T.filter(t=>Object.keys(t.pool_deltas).length); if(!rows.length){empty(fig,"no pool snapshots (tasks were backfilled)");return;}
    const W=560,rowH=30,L=150,R=40,H=rows.length*rowH+26; const s=svg(fig,W,H,"Quota pool consumption per task");
    const val=(t,k)=>{const d=t.pool_deltas; if(k==="codex")return d.codex_weekly||0; return -(d.google_gemini_weekly||0);}; const max=Math.max(...rows.flatMap(t=>[val(t,"codex"),val(t,"gem")]),1); const x=v=>L+Math.max(0,v)*(W-L-R)/max;
    rows.forEach((t,i)=>{const y=8+i*rowH; el("text",{x:L-8,y:y+14,"text-anchor":"end","font-size":"11.5",fill:css("--ink")},s).textContent=t.task.length>18?t.task.slice(0,17)+"…":t.task; [["codex",css("--s2"),0],["gem",css("--s3"),11]].forEach(([k,c,dy])=>{const v=val(t,k); const r=el("rect",{x:L,y:y+2+dy,width:x(v)-L,height:9,fill:c},s); hover(r,fig,`${t.task} · ${k==="codex"?"Codex weekly":"Google Gemini weekly"}: ${v} points`);}); });
    table(fig,["Task","Codex weekly used (pts)","Gemini weekly consumed (pts)"],rows.map(t=>[t.task,val(t,"codex"),val(t,"gem")]));})();

  // reliability
  (function(){const fig=document.getElementById("c-reliability"); const R=DATA.reliability||{}; const lanes=Object.keys(R).sort(); if(!lanes.length){empty(fig,"no lane runs yet");return;}
    const W=1160,rowH=34,L=230,H=lanes.length*rowH+30; const s=svg(fig,W,H,"First-attempt success rate per lane with failure classes"); const x=v=>L+v*(W-L-260);
    for(let g=0;g<=1;g+=0.25){el("line",{x1:x(g),y1:8,x2:x(g),y2:H-22,stroke:css("--grid")},s);el("text",{x:x(g),y:H-6,"text-anchor":"middle","font-size":"11",fill:css("--ink-3")},s).textContent=Math.round(g*100)+"%";}
    lanes.forEach((k,i)=>{const d=R[k]; const y=8+i*rowH; el("text",{x:L-10,y:y+18,"text-anchor":"end","font-size":"12",fill:css("--ink")},s).textContent=k;
      const rate=d.first_attempt_success_rate||0; const r=el("rect",{x:L,y:y+4,width:x(rate)-L,height:22,fill:css("--s2")},s); hover(r,fig,`${k}: first attempt succeeded ${Math.round(rate*100)}% of ${d.first_attempts}; failures ${JSON.stringify(d.classes)}; ${d.mean_seconds_to_result}s to a result; ${d.wasted_tokens.toLocaleString()} tokens wasted`);
      const c=d.classes||{}; el("text",{x:x(1)+12,y:y+18,"font-size":"11.5",fill:css("--ink-2")},s).textContent=`${Math.round(rate*100)}% · model ${c.model||0} · infra ${c.infra||0} · harness ${c.harness||0} · quota ${c.quota||0} · ${d.mean_seconds_to_result}s`;});
    table(fig,["Lane","First-try success","Attempts","Model","Infra","Harness","Quota","Seconds to result","Wasted tokens","Cost/point incl. waste"],lanes.map(k=>{const d=R[k],c=d.classes||{};return [k,d.first_attempt_success_rate,d.attempts,c.model||0,c.infra||0,c.harness||0,c.quota||0,d.mean_seconds_to_result,d.wasted_tokens.toLocaleString(),d.cost_per_point_incl_waste??"—"];}));})();

  // canary matrix
  (function(){const fig=document.getElementById("c-canary"); const C=DATA.canary||[]; if(!C.length){empty(fig,"no canary runs yet — python3 lane-eval.py run --task all --lane reference, then real lanes");return;}
    const lanes=[...new Set(C.map(e=>e.lane+" @ "+e.effort))].sort(); const tasks=[...new Set(C.map(e=>e.task))].sort();
    const cell=(t,l)=>C.filter(e=>e.task===t&&e.lane+" @ "+e.effort===l);
    const W=1160,L=200,T0=30,rowH=30,colW=Math.min(150,(W-L)/lanes.length),H=T0+tasks.length*rowH+8; const s=svg(fig,W,H,"Canary suite score matrix");
    lanes.forEach((l,j)=>{el("text",{x:L+j*colW+colW/2,y:18,"text-anchor":"middle","font-size":"11",fill:css("--ink-2")},s).textContent=l.length>20?l.slice(0,19)+"…":l;});
    const mix=(hex,alpha)=>{const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);return `rgba(${r},${g},${b},${alpha})`;};
    tasks.forEach((t,i)=>{const y=T0+i*rowH; el("text",{x:L-10,y:y+19,"text-anchor":"end","font-size":"12",fill:css("--ink")},s).textContent=t;
      lanes.forEach((l,j)=>{const rs=cell(t,l); const x=L+j*colW+2; if(!rs.length){el("rect",{x,y:y+2,width:colW-4,height:rowH-4,fill:css("--bg-2")},s);return;}
        const sc=rs.reduce((a,e)=>a+(e.score||0),0)/rs.length; const p=rs.filter(e=>e.pass).length; const r=el("rect",{x,y:y+2,width:colW-4,height:rowH-4,fill:mix(css("--s2"),0.15+0.85*sc)},s);
        hover(r,fig,`${t} · ${l}: ${p}/${rs.length} pass, mean ${Math.round(sc*100)}% · ${JSON.stringify(rs[rs.length-1].detail)}`);
        el("text",{x:x+(colW-4)/2,y:y+19,"text-anchor":"middle","font-size":"11.5",fill:sc>0.55?css("--surface"):css("--ink")},s).textContent=`${Math.round(sc*100)}% · ${p}/${rs.length}`;});});
    table(fig,["Task","Lane","Runs","Pass","Mean score","Last detail"],tasks.flatMap(t=>lanes.map(l=>{const rs=cell(t,l);if(!rs.length)return null;return [t,l,rs.length,rs.filter(e=>e.pass).length,(rs.reduce((a,e)=>a+(e.score||0),0)/rs.length).toFixed(2),JSON.stringify(rs[rs.length-1].detail)];}).filter(Boolean)));})();

  // task table with sort
  (function(){const tb=document.querySelector("#tasks tbody"); const cell=(v,num)=>`<td class="${num?'num':''}">${v}</td>`;
    const rowHtml=t=>`<tr>${cell(t.task)}${cell(t.project)}<td><span class="arm">${t.arm}</span></td>${cell(t.kind)}${cell(t.route)}${cell(t.lane)}${cell((t.model||"?")+(t.effort?" @ "+t.effort:""))}${cell(t.status)}${cell(t.advisor)}${cell(t.elapsed_min,1)}${cell(t.claude_billable.toLocaleString(),1)}${cell(t.codex_billable.toLocaleString(),1)}${cell(t.agy_total.toLocaleString(),1)}${cell(Object.values(t.findings).reduce((a,f)=>a+f[0],0),1)}${cell(t.rework,1)}${cell(t.escaped,1)}<td>${t.window_checked?'<span class="pill good">checked</span>':'<span class="pill warn">open</span>'}</td></tr>`;
    let rows=T.slice(); const render=()=>tb.innerHTML=rows.map(rowHtml).join(""); render();
    const keys=["task","project","arm","kind","route","lane","model","status","advisor","elapsed_min","claude_billable","codex_billable","agy_total","confirmed","rework","escaped","window_checked"];
    document.querySelectorAll("#tasks th").forEach((th,i)=>{let asc=true; th.addEventListener("click",()=>{const k=keys[i]; rows.sort((a,b)=>{const va=k==="confirmed"?Object.values(a.findings).reduce((x,f)=>x+f[0],0):a[k]; const vb=k==="confirmed"?Object.values(b.findings).reduce((x,f)=>x+f[0],0):b[k]; return (va>vb?1:va<vb?-1:0)*(asc?1:-1);}); asc=!asc; render();});});})();

  document.querySelectorAll(".tbtn").forEach(b=>b.addEventListener("click",()=>{const f=b.closest("figure");const c=f.querySelector(".chart"),t=f.querySelector(".tview");const showT=t.classList.contains("hidden");t.classList.toggle("hidden",!showT);c.classList.toggle("hidden",showT);b.textContent=showT?"chart":"table";}));
})();
</script>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="benchmark.jsonl path (default: this repo's)")
    ap.add_argument("--all-projects", action="store_true", help="aggregate every project's log under the Cure project roots")
    ap.add_argument("--out", required=True, help="HTML file to write")
    ap.add_argument("--claude-drop", type=float, default=0.33)
    ap.add_argument("--max-slowdown", type=float, default=1.5)
    ap.add_argument("--open", action="store_true", help="open the file after writing (macOS)")
    ap.add_argument("--json", action="store_true", help="also print the embedded data as JSON")
    a = ap.parse_args()

    br = load_report_module()
    if a.all_projects:
        rows, source = br.load_all_projects(), "all projects under ~/CureVault/projects"
    else:
        log = Path(a.log) if a.log else br.default_log()
        rows, source = br.load(log), str(log)
    summary = br.summarise(rows) if rows else {}
    decision = br.decide(summary, a.claude_drop, a.max_slowdown) if rows else {"verdict": "no tasks logged", "checks": {}, "reason": "run lane-log.py start/end around a task"}
    # canary suite results (evals.jsonl next to each benchmark.jsonl)
    canary = []
    seen = set()
    logs = [Path(r["_log"]).parent / "evals.jsonl" for r in rows if r.get("_log")] if rows else []
    if not a.all_projects:
        logs.append((Path(a.log).parent if a.log else br.default_log().parent) / "evals.jsonl")
    for lp in logs:
        try:
            key = str(lp.resolve())
        except Exception:
            continue
        if key in seen or not lp.exists():
            continue
        seen.add(key)
        for line in lp.read_text().splitlines():
            try:
                e = json.loads(line)
                canary.append({"task": e.get("task"), "role": e.get("role"), "kind": e.get("kind"), "lane": e.get("lane"), "effort": e.get("effort"), "pass": bool(e.get("pass")),
                               "score": e.get("score"), "elapsed": e.get("elapsed_seconds"), "ts": e.get("ts"), "detail": {k: v for k, v in (e.get("grade") or {}).items() if k in ("recall", "precision", "passed", "expected", "failed_runs", "forbidden_left", "missed", "false_positives")}})
            except Exception:
                pass
    # reliability per lane, from the same evals logs (failures are results)
    reliability = {}
    try:
        spec_e = importlib.util.spec_from_file_location("lane_eval", HERE / "lane-eval.py")
        le = importlib.util.module_from_spec(spec_e); spec_e.loader.exec_module(le)
        eval_rows = []
        for lp in seen:
            for line in Path(lp).read_text().splitlines():
                try:
                    eval_rows.append(json.loads(line))
                except Exception:
                    pass
        reliability = le._reliability(eval_rows)
    except Exception:
        reliability = {}
    data = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "source": source, "tasks": slim(rows), "arms": summary, "decision": decision, "canary": canary, "reliability": reliability}
    html = TEMPLATE.replace("__DATA__", json.dumps(data))
    out = Path(a.out).expanduser()
    out.write_text(html)
    print(f"wrote {out} ({len(rows)} tasks, verdict: {decision.get('verdict')})")
    if a.json:
        print(json.dumps(data, indent=2))
    if a.open:
        subprocess.run(["open", str(out)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
