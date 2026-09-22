const PRODUCTS = {
  prime: {
    name: "Prime24AI",
    short: "Workflow pilot",
    url: "https://prime24ai.com/",
    headline: "Turn one expensive workflow into a supervised system.",
    subhead: "Start with the repeated work, its baseline, and the approval point—not a broad AI transformation project.",
    fit: "Best when a small team can name a repeated workflow that affects response time, capacity, customer experience, or revenue, but cannot justify an open-ended implementation.",
    signal: ["Repeated handoffs", "A measured, supervised workflow", "Work moves across inboxes and tools.", "Automation prepares; a named owner approves."],
    evidence: [["01","Narrow boundary","One workflow, one owner, one baseline KPI."],["02","Human control","Important messages, decisions, and actions remain approval-gated."],["03","Visible result","Track time, completed work, exceptions, and the outcome after launch."]],
    competitors: ["Prime24AI","Studio24","AIGist24","M24"],
    rows: [["Best first step","$299 48-hour blueprint","Workshop or scoped pilot","Discovery + proof of concept","Free discovery call"],["Core distinction","Fixed, low-cost decision artifact before build","Build-and-handover studio","Custom implementation","Custom workflow service"],["Human approval","Explicit action gates","Depends on scope","Human-in-loop positioning","Depends on scope"],["Outcome proof","Baseline + stop/scale rule","Testing and handover","Baseline and tracked metrics","Measured custom result"]],
    sources: [["Prime24AI","https://prime24ai.com/"],["Studio24","http://www.studio24.ai/"],["AIGist24","https://aigist24.com/services/custom-implementation"],["M24","https://messaging24.com/"]],
    offer: ["48-Hour Blueprint","$299","Delivered within 48 hours"],
    scopes: [
      ["Blueprint","Lowest-risk paid start",["Current-state workflow map","Recommended stack and control points","Failure cases and fallback","Implementation sequence and decision rule"],"Proceed only if the expected annual capacity or revenue impact clearly exceeds implementation and operating cost."],
      ["Build sprint","One approved production workflow",["Implementation of the approved scope","System integration and acceptance tests","Human approval gate","Handoff and operating notes"],"Scale only after the pilot hits the agreed KPI without unacceptable exceptions."],
      ["Managed ops","Monitor after launch",["Exception review","Cost and reliability tracking","Monthly outcome report","Controlled change backlog"],"Continue only while monitored value exceeds ongoing cost and review burden."]
    ]
  },
  agents: {
    name: "Agents by Prime24AI", short: "Supervised agent", url: "https://agents.prime24ai.com/",
    headline: "Put one agent role on trial before buying an agent platform.",
    subhead: "Define the role, evidence, permissions, and approval boundary first. Then test it against real work.",
    fit: "Best for teams that want an agent outcome but do not want to choose a platform, buy seats, or expose production systems before the job and acceptance test are clear.",
    signal: ["Platform-first setup", "Role-first controlled pilot", "Tools and credits arrive before proof.", "The job, evidence, and approval test come first."],
    evidence: [["01","Role contract","Inputs, tools, permissions, output, and escalation are explicit."],["02","Evidence trail","Claims and actions point back to sources and logged decisions."],["03","Acceptance test","Positive, negative, edge, and failure cases determine release readiness."]],
    competitors: ["Prime24AI Agents","Lindy","Relevance AI","Zapier Agents"],
    rows: [["Buying motion","Scoped role pilot","Self-serve platform plans","Platform + usage credits","Part of automation platform"],["Setup owner","Prime24AI + customer owner","Customer/team","Customer/team","Customer/team"],["Approval design","Included in role contract","Configurable","Configurable","Configurable"],["Best fit","One accountable role with proof","Broad no-code agent building","Multi-agent tool building","Existing Zapier users"]],
    sources: [["Agents","https://agents.prime24ai.com/"],["Lindy pricing","https://www.lindy.ai/pricing"],["Relevance AI pricing","https://relevanceai.com/pricing"],["Zapier Agents","https://zapier.com/agents"]],
    offer: ["Workflow Agent Pilot","$1,500","Fixed scope; one role"],
    scopes: [["Agent role pilot","One role, one workflow",["Role contract and permission map","Working agent path","Evidence and event log","Acceptance and failure tests"],"Release only when the agent passes the agreed tests and a human owner accepts the residual risk."],["Agent role library","Design before implementation",["Prioritized role inventory","Tool and data boundaries","Approval map","Pilot recommendation"],"Build only the top role when it has a measurable baseline and a safe fallback."],["Verification sprint","Test an existing agent",["Critical-path test plan","Edge and adversarial cases","Cost and latency evidence","Release recommendation"],"Keep the current system unchanged unless test evidence justifies a controlled revision."]]
  },
  learn: {
    name: "Learn by Prime24AI", short: "Workflow learning", url: "https://learn.prime24ai.com/",
    headline: "Teach the actual workflow—not another generic AI course.",
    subhead: "Short, role-specific practice for accounting, insurance, credentialing, HR, mortgage, and real-estate teams.",
    fit: "Best when employees need to use AI inside a real job process with approved examples, review rules, and a manager-visible completion result.",
    signal: ["Course completion", "Workflow competence", "Learners watch general material.", "Learners practice the job task and review standard."],
    evidence: [["01","Role-specific","Exercises match the documents, decisions, and checks in the job."],["02","Practice output","The learner produces a reviewable work artifact, not just a quiz score."],["03","Manager handoff","The team gets a repeatable lesson and an adoption checkpoint."]],
    competitors: ["Prime24AI Learn","Coursera Business","DataCamp Business","Generic LMS"],
    rows: [["Primary unit","One real workflow lesson","Course or certificate","Data/AI skill track","Hosted course content"],["Customization","Role and workflow specific","Catalog + enterprise programs","Catalog + custom tracks","Depends on authoring"],["Proof","Practice artifact + review","Completion and assessment","Skill assessment","Completion data"],["Best fit","Small team adopting one workflow","Broad enterprise learning","Technical data upskilling","Existing internal training"]],
    sources: [["Learn","https://learn.prime24ai.com/"],["Coursera Business","https://www.coursera.org/business/compare-plans"],["DataCamp Business","https://www.datacamp.com/business/compare-plans"]],
    offer: ["Workflow Lesson Pilot","Custom","One role; one lesson"],
    scopes: [["Single lesson pilot","One repeated job task",["Workflow-specific interactive lesson","Approved and unsafe examples","Practice artifact","Manager review guide"],"Expand only if learners complete the task more accurately or quickly against the starting baseline."],["Team lesson pack","Three connected tasks",["Three role-specific lessons","Shared review rubric","Completion view","30-day adoption check"],"Keep only lessons that change verified on-the-job behavior."],["Existing-content conversion","Turn SOPs into practice",["Source-content review","Interactive scenarios","Knowledge checks","Owner sign-off"],"Publish only after the process owner verifies every critical step."]]
  },
  pitchme: {
    name: "PitchMe", short: "Candidate-first recruiting", url: "https://pitchme.prime24ai.com/",
    headline: "Make employers pitch the opportunity before candidates spend the time.",
    subhead: "A candidate-controlled marketplace where compensation, process, timeline, and selection reason arrive first.",
    fit: "Best for recruiting partners, communities, and employers who want a small, transparent talent campaign rather than another high-volume application funnel.",
    signal: ["More applications", "Better-qualified interest", "Candidates repeat the same work.", "Employers provide the decision context first."],
    evidence: [["01","Candidate control","Profiles stay private until the person opts into visibility."],["02","Structured opportunity","Compensation, work style, process, timing, and reason are required."],["03","Clear response","Interested, Maybe, or Pass produces a cleaner signal than application volume."]],
    competitors: ["PitchMe","LinkedIn","Wellfound","Teal / Huntr"],
    rows: [["Who pitches first","Employer","Usually candidate or recruiter","Candidate or recruiter","Candidate manages applications"],["Compensation context","Required in pitch","Varies by listing/message","Common in startup roles","Pulled from job listing"],["Candidate visibility","Private by default; opt in","Profile settings","Candidate profile","Private tool account"],["Best fit","Small transparent talent campaign","Large professional network","Startup hiring","Individual job search"]],
    sources: [["PitchMe","https://pitchme.prime24ai.com/"],["LinkedIn Talent","https://business.linkedin.com/talent-solutions"],["Wellfound","https://wellfound.com/recruit/overview"],["Huntr pricing","https://tryhuntr.com/pricing"]],
    offer: ["Structured Talent Pilot","Custom","One role; small cohort"],
    scopes: [["Single-role campaign","One role, one opted-in cohort",["Structured opportunity template","Candidate visibility controls","Employer pitch workflow","Interest and pass summary"],"Continue only if qualified interest improves without increasing candidate time or ambiguity."],["Community pilot","For a member network",["Private onboarding","Employer pitch standard","Cohort dashboard","Feedback review"],"Scale only with explicit candidate consent and a verified employer-response standard."],["Hiring-process audit","Fix the pitch before launch",["Current funnel map","Candidate-effort audit","Transparency gaps","Rewritten structured opportunity"],"Launch only when compensation, process, timeline, and decision criteria are clear."]]
  },
  paws: {
    name: "Paws & Power", short: "Dog-mom fitness", url: "https://pawsandpowerfit.prime24ai.com/",
    headline: "Build one routine that includes the dog and the human.",
    subhead: "Personalized human workouts, realistic meal planning, and dog-inclusive activity prompts in one membership.",
    fit: "Best for dog-mom communities, trainers, pet businesses, and wellness partners that want a joint consistency challenge instead of separate human-fitness and pet-tracking products.",
    signal: ["Two separate routines", "One shared consistency loop", "Human fitness and dog care compete for time.", "The dog becomes part of the prompt and accountability."],
    evidence: [["01","Human plan","Workouts and practical meals are designed for the member."],["02","Dog-inclusive cue","Walks, play, mobility, and enrichment prompts fit the shared routine."],["03","Partner-ready pilot","A small challenge can test completion and retention before a larger partnership."]],
    competitors: ["Paws & Power","Woofz","FitBark","FitFido"],
    rows: [["Primary focus","Human + dog routine","Dog training and wellness","Dog activity tracking","Dog nutrition and health"],["Human workouts","Core","No","No; human tracker linking","No"],["Human meal plans","Core","No","No","No"],["Best fit","Dog moms building consistency","Dog behavior/training","Device-based activity data","Dog weight and meal tracking"]],
    sources: [["Paws & Power","https://pawsandpowerfit.prime24ai.com/"],["Woofz","https://www.woofz.com/"],["FitBark","https://www.fitbark.com/store/fitbark2/"],["FitFido","https://apps.apple.com/us/app/fitfido-dog-nutrition-tracker/id6760243353"]],
    offer: ["Partner Challenge Pilot","$29/member","Small cohort; 30 days"],
    scopes: [["30-day partner challenge","Small, invited cohort",["Partner-specific invite page","Human workout and meal rhythm","Dog-inclusive prompts","Completion and feedback summary"],"Expand only if the cohort uses both sides of the routine and reports a credible consistency benefit."],["Community bundle","For an existing audience",["Cohort onboarding","Weekly challenge rhythm","Partner check-ins","End-of-cycle results"],"Renew only when participation and week-four retention clear the agreed threshold."],["Member test","Individual starting point",["Personalized plan","Human meal prompts","Dog-inclusive activity cues","Progress check"],"Continue only if the routine is sustainable for both member and dog."]]
  }
};

const params = new URLSearchParams(location.search);
const safe = (value, fallback, limit = 120) => (value || fallback).replace(/[<>]/g, "").trim().slice(0, limit);
const state = {
  product: PRODUCTS[params.get("product")] ? params.get("product") : "prime",
  company: safe(params.get("company"), "your team"),
  workflow: safe(params.get("workflow"), "the repeated workflow", 180),
  scope: 0
};

const el = id => document.getElementById(id);
const money = value => new Intl.NumberFormat("en-US", {style:"currency",currency:"USD",maximumFractionDigits:0}).format(value);

function renderTabs(){
  el("productTabs").innerHTML = Object.entries(PRODUCTS).map(([key,p]) => `<button class="product-tab" role="tab" aria-selected="${key===state.product}" data-product="${key}"><b>${p.name}</b><span>${p.short}</span></button>`).join("");
  document.querySelectorAll("[data-product]").forEach(button => button.addEventListener("click",()=>{state.product=button.dataset.product;state.scope=0;const next=new URL(location.href);next.searchParams.set("product",state.product);history.replaceState(null,"",next);render();}));
}

function renderComparison(p){
  el("comparisonHead").innerHTML = `<tr><th>Decision factor</th>${p.competitors.map((name,i)=>`<th class="${i===0?"highlight":""}">${name}</th>`).join("")}</tr>`;
  el("comparisonBody").innerHTML = p.rows.map(row=>`<tr>${row.map((cell,i)=>`<td class="${i===1?"highlight":""}">${cell}</td>`).join("")}</tr>`).join("");
  el("sourceList").innerHTML = `<span>Public sources checked:</span>${p.sources.map(([name,url])=>`<a href="${url}" target="_blank" rel="noreferrer">${name} ↗</a>`).join("")}`;
}

function renderScopes(p){
  el("scopeOptions").innerHTML=p.scopes.map((s,i)=>`<button class="scope-option" aria-pressed="${i===state.scope}" data-scope="${i}"><b>${s[0]}</b><span>${s[1]}</span></button>`).join("");
  document.querySelectorAll("[data-scope]").forEach(button=>button.addEventListener("click",()=>{state.scope=Number(button.dataset.scope);renderScopes(p);}));
  const s=p.scopes[state.scope];
  el("scopeTitle").textContent=s[0];
  el("scopeDeliverables").innerHTML=s[2].map(item=>`<li>${item}</li>`).join("");
  el("decisionRule").textContent=s[3];
  updateEmailLinks(p,s[0]);
}

function updateEmailLinks(p,scope){
  const subject=encodeURIComponent(`${p.name} proposal for ${state.company}`);
  const body=encodeURIComponent(`Darnley,\n\nI reviewed the ${p.name} proposal room. I want to discuss the ${scope} for ${state.workflow}.\n\nCompany: ${state.company}\nCurrent tool(s): \nWeekly volume: \nApproval owner: \n\nBest next step:`);
  const href=`mailto:darnleyweekes@prime24ai.com?subject=${subject}&body=${body}`;
  el("emailLink").href=href;el("finalEmailLink").href=href;
}

function calculate(){
  const people=Math.max(1,Number(el("peopleInput").value)||1);
  const hours=Math.max(0,Number(el("hoursInput").value)||0);
  const rate=Math.max(1,Number(el("rateInput").value)||1);
  const reduction=Number(el("reductionInput").value);
  const saved=people*hours*52*reduction;
  const annual=saved*rate;
  el("annualValue").textContent=money(annual);
  el("hoursSaved").textContent=Math.round(saved).toLocaleString();
  el("monthlyValue").textContent=money(annual/12);
  el("roiSentence").textContent=`If ${state.company} verifies these inputs, a ${Math.round(reduction*100)}% reduction represents ${Math.round(saved).toLocaleString()} hours of annual capacity.`;
}

function render(){
  const p=PRODUCTS[state.product];
  document.title=`${p.name} proposal for ${state.company}`;
  el("preparedFor").textContent=`Prepared for ${state.company}`;
  el("headline").textContent=p.headline;
  el("subhead").textContent=`${p.subhead} This proposal focuses on ${state.workflow}.`;
  el("productLink").href=p.url;el("productLink").textContent=`Open ${p.name}`;
  el("signalTitle").textContent=`${p.name} · ${state.workflow}`;
  ["beforeLabel","afterLabel","beforeDetail","afterDetail"].forEach((id,i)=>el(id).textContent=p.signal[i]);
  el("fitCopy").textContent=p.fit;
  el("evidenceStack").innerHTML=p.evidence.map(([n,title,copy])=>`<article class="evidence"><span>${n}</span><div><b>${title}</b><p>${copy}</p></div></article>`).join("");
  el("offerLabel").textContent=p.offer[0];el("offerPrice").textContent=p.offer[1];el("offerTiming").textContent=p.offer[2];
  renderTabs();renderComparison(p);renderScopes(p);calculate();
}

["peopleInput","hoursInput","rateInput","reductionInput"].forEach(id=>el(id).addEventListener("input",calculate));
el("printButton").addEventListener("click",()=>window.print());
render();
