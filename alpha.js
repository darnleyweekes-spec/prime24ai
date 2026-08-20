(()=>{
  const q=s=>document.querySelector(s);
  const input=q('#missionInput');
  const industry=q('#industry');
  const state=q('#missionState');
  const empty=q('#empty');
  const result=q('#result');
  const acts=q('#resultActions');
  let brief='';

  const P={
    growth:{mode:'GROWTH / OUTREACH',agents:['ALPHA','ROSALIND','VISION','PAM','FRED','BILLY'],stack:'Vane/ROSALIND research · approved CRM/spreadsheet · Postiz/listmonk only after approval',flow:'Define buyer → research visible pain → score accounts → prepare personalized angle → human review → approved outreach → measure replies',plan:['Define ICP, offer, proof and conversion target','Research a small qualified account set with source provenance','Generate one workflow-specific observation per prospect','Human-review messaging and approve any external send','Track replies, objections, calls, Blueprint and implementation conversion'],gate:'Human approval before external outreach, posting, spend, CRM mutation, or commitment.'},
    research:{mode:'EVIDENCE-BACKED RESEARCH',agents:['ALPHA','ROSALIND','MR. HOLMES','SAM','VISION'],stack:'Vane/ROSALIND · permitted web extraction · document normalization · source log',flow:'Frame question → collect current sources → compare claims → separate fact from inference → synthesize decision brief',plan:['Clarify the decision the research must support','Collect current first-party and credible external evidence','Cross-check conflicting claims and capture uncertainty','Synthesize findings into options, risks, and indicators','Return a source-backed brief with next action'],gate:'Human approval before using private data, contacting subjects, or acting on research.'},
    build:{mode:'PRODUCT / BUILD',agents:['ALPHA','VISION','PAM','BIANCA','BOB','FRED','BENICIO'],stack:'GitHub · chosen app framework · Supabase where useful · workflow tools only when justified',flow:'Outcome → acceptance criteria → architecture → bounded implementation → tests → security review → deployment approval',plan:['Convert objective into measurable acceptance criteria','Inspect existing code, integrations, and constraints','Choose the smallest architecture that can prove value','Build and test the bounded workflow','Run security/quality review before production deployment'],gate:'Human approval before production deployment, destructive migrations, credential use, or paid infrastructure changes.'},
    automation:{mode:'WORKFLOW AUTOMATION',agents:['ALPHA','VISION','BIANCA','FRED','TED','BILLY'],stack:'n8n/compatible workflow layer · existing business systems · logs/audit trail · state store if required',flow:'Map current process → separate judgment from repetition → automate preparation/routing → add approval gates → instrument KPIs',plan:['Map steps, owners, inputs, and failure points','Identify repetitive steps with measurable cost','Design idempotent workflow and approval points','Implement one high-value automation first','Measure time saved, errors, throughput, and expansion value'],gate:'Human approval for consequential messages, financial changes, deletions, access changes, or exceptions.'},
    ai:{mode:'AI / ML SYSTEM',agents:['ALPHA','HAL','JAN','BOB','SARAH','TED','BILLY'],stack:'Strong foundation-model baseline · retrieval if needed · evaluation harness · provider routing if justified',flow:'Objective → data/eval set → baseline → model/RAG strategy → safety checks → deployment → monitoring',plan:['Define task, baseline, and success metrics','Inspect data quality, privacy, provenance, and evaluation coverage','Compare prompting/RAG/fine-tuning before custom training','Build representative tests including negative and edge cases','Deploy with monitoring, fallback, and versioned evaluation'],gate:'Human approval before sensitive-data training, production model changes, or high-impact automated decisions.'},
    security:{mode:'SECURITY / GOVERNANCE',agents:['ALPHA','BENICIO','BILLY','PAUL'],stack:'Defensive review tools · audit logs · permission-scoped test environment',flow:'Confirm authorization → define scope → threat model → defensive checks → findings → remediation → retest',plan:['Verify ownership/authorization and exact scope','Threat-model assets and data flows','Run non-destructive checks inside approved boundaries','Prioritize findings by likelihood and business impact','Remediate and validate without expanding scope'],gate:'Explicit authorization is mandatory before intrusive testing, scanning outside owned scope, credential use, exploitation, or destructive actions.'},
    operations:{mode:'BUSINESS OPERATIONS',agents:['ALPHA','VISION','PAM','BIANCA','FRED','MARK'],stack:'Existing business systems first · workflow automation only where ROI is clear · dashboard/logging layer',flow:'Find expensive repetition → quantify baseline → design supervised workflow → implement → measure → productize',plan:['Identify repetitive work and current labor/error cost','Select one workflow with urgent pain and measurable ROI','Define what AI prepares versus what humans decide','Implement the smallest useful operational system','Review KPI movement and expand only after proof'],gate:'Human approval remains on sensitive communications, exceptions, pricing, commitments, and irreversible actions.'}
  };

  function classify(t){
    t=t.toLowerCase();
    const h=a=>a.some(w=>t.includes(w));
    if(h(['security','pentest','penetration','vulnerability','threat']))return'security';
    if(h(['machine learning','llm','rag','model','fine-tun','embedding','generative']))return'ai';
    if(h(['build','website','app','software','product','develop','code','deploy']))return'build';
    if(h(['automate','automation','workflow','intake','routing','follow-up','follow up','reporting','document']))return'automation';
    if(h(['research','competitor','market','compare','investigate']))return'research';
    if(h(['lead','prospect','outreach','marketing','campaign','sales','linkedin','email','customer acquisition']))return'growth';
    return'operations';
  }

  function render(){
    if(!input||!industry||!state||!empty||!result||!acts)return;
    const obj=input.value.trim();
    if(obj.length<12){
      state.textContent='NEED MORE CONTEXT';
      empty.hidden=false;
      result.hidden=true;
      acts.hidden=true;
      empty.textContent='Add a little more detail: the outcome, who or what it affects, and any important constraint.';
      return;
    }
    const p=P[classify(obj)],ctx=industry.options[industry.selectedIndex].textContent;
    state.textContent='ROUTED / '+p.mode;
    empty.hidden=true;
    result.hidden=false;
    acts.hidden=false;
    const blocks=[
      ['Objective',obj],['Mission mode',p.mode],['Specialist team','<div class="chips">'+p.agents.map(a=>'<span class="chip">'+a+'</span>').join('')+'</div>'],['Recommended workflow',p.flow],['Candidate stack',p.stack],['5-step plan','<ol>'+p.plan.map(x=>'<li>'+x+'</li>').join('')+'</ol>'],['Human approval boundary',p.gate],['Business context',ctx]
    ];
    result.innerHTML=blocks.map(([l,v])=>'<div class="result"><small>'+l+'</small><div>'+v+'</div></div>').join('');
    brief=`PRIME24 AI — ALPHA MISSION BRIEF\n\nOBJECTIVE\n${obj}\n\nBUSINESS CONTEXT\n${ctx}\n\nMISSION MODE\n${p.mode}\n\nSPECIALIST TEAM\n${p.agents.join(', ')}\n\nWORKFLOW\n${p.flow}\n\nCANDIDATE STACK\n${p.stack}\n\nEXECUTION PLAN\n${p.plan.map((x,i)=>`${i+1}. ${x}`).join('\n')}\n\nHUMAN APPROVAL BOUNDARY\n${p.gate}\n\nGenerated by the browser-side Prime24 AI ALPHA Mission Lab. No external action was executed.`;
  }

  const runMission=q('#runMission');
  const exampleMission=q('#exampleMission');
  const copyMission=q('#copyMission');
  const downloadMission=q('#downloadMission');
  if(runMission)runMission.onclick=render;
  if(exampleMission)exampleMission.onclick=()=>{
    if(!input||!industry)return;
    input.value='Find qualified professional-services prospects, research a visible repetitive workflow at each company, prepare a personalized outreach angle, and keep final send approval human-owned.';
    industry.value='professional';
    render();
  };
  if(copyMission)copyMission.onclick=async()=>{
    if(!brief)return;
    try{
      await navigator.clipboard.writeText(brief);
      copyMission.textContent='Copied ✓';
      setTimeout(()=>copyMission.textContent='Copy Brief',1400);
    }catch{
      copyMission.textContent='Copy unavailable';
    }
  };
  if(downloadMission)downloadMission.onclick=()=>{
    if(!brief)return;
    const b=new Blob([brief],{type:'text/plain'}),u=URL.createObjectURL(b),a=document.createElement('a');
    a.href=u;
    a.download='prime24-alpha-mission-brief.txt';
    a.click();
    URL.revokeObjectURL(u);
  };
  if(input)input.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')render()});

  const email=['darnleyweekes','prime24ai.com'].join('@');
  const legacy={
    'Free Assessment':['Free Prime24 AI Workflow Assessment','Free Workflow Assessment'],
    'Get Free Assessment':['Free Prime24 AI Workflow Assessment','Free Workflow Assessment'],
    'Request Assessment':['Free Prime24 AI Workflow Assessment','Free Workflow Assessment'],
    'Have Prime24 Build This →':['Prime24 AI Mission Implementation','Mission Implementation'],
    'Start Blueprint':['Prime24 AI 48-Hour Blueprint','48-Hour Blueprint'],
    'Discuss a Build':['Prime24 AI Build Sprint','AI Build Sprint'],
    'Explore Managed Ops':['Prime24 AI Managed Ops','Managed AI Ops'],
    'Build My Chatbot →':['Prime24 AI Chatbot','Custom Chatbot']
  };

  let contact=q('#contact');
  if(!contact){
    contact=document.createElement('section');
    contact.id='contact';
    contact.innerHTML='<div class="wrap"><div class="panel contact-card"><div class="kicker">Contact Prime24 AI</div><h2 class="mid" id="contactService">Free Workflow Assessment</h2><p class="lead small" id="contactHelp">Your selected service is ready. Open Gmail with the correct recipient and subject, or copy the address and contact Prime24 AI directly.</p><p class="contact-line"><b>Email:</b><span id="contactEmail">Loading contact address…</span></p><div class="actions"><button class="btn primary" id="openEmail" type="button">Send via Gmail →</button><button class="btn" id="copyEmail" type="button">Copy Email</button></div><p class="note" id="contactStatus">No external action happens until you choose an option above.</p></div></div>';
    const final=q('.final');
    final?final.before(contact):document.querySelector('main')?.appendChild(contact);
  }

  const contactEmail=q('#contactEmail');
  const contactService=q('#contactService');
  const contactHelp=q('#contactHelp');
  const contactStatus=q('#contactStatus');
  const openEmail=q('#openEmail');
  const copyEmail=q('#copyEmail');
  let selectedSubject='Free Prime24 AI Workflow Assessment';

  if(contactEmail)contactEmail.textContent=email;
  if(contactHelp)contactHelp.textContent='Your selected service is ready. Open Gmail with the correct recipient and subject, or copy the address and contact Prime24 AI directly.';
  if(openEmail)openEmail.textContent='Send via Gmail →';

  document.querySelectorAll('a').forEach(a=>{
    const label=a.textContent.trim().replace(/\s+/g,' ');
    const fallback=legacy[label];
    const subject=a.dataset.contactSubject||(fallback&&fallback[0]);
    if(!subject)return;
    const display=a.dataset.contactLabel||(fallback&&fallback[1])||'Contact Prime24 AI';
    a.href='#contact';
    a.removeAttribute('data-cfemail');
    a.removeAttribute('target');
    a.addEventListener('click',()=>{
      selectedSubject=subject;
      if(contactService)contactService.textContent=display;
      if(contactStatus)contactStatus.textContent='Selected: '+subject+'. Choose Send via Gmail or Copy Email.';
    });
  });

  if(openEmail)openEmail.addEventListener('click',()=>{
    const gmailUrl='https://mail.google.com/mail/?view=cm&fs=1&to='+encodeURIComponent(email)+'&su='+encodeURIComponent(selectedSubject);
    if(contactStatus)contactStatus.textContent='Opening Gmail compose…';
    const popup=window.open(gmailUrl,'_blank','noopener,noreferrer');
    if(!popup)window.location.assign(gmailUrl);
    else if(contactStatus)contactStatus.textContent='Gmail compose opened in a new tab.';
  });

  if(copyEmail)copyEmail.addEventListener('click',async()=>{
    let ok=false;
    try{await navigator.clipboard.writeText(email);ok=true}catch{}
    if(!ok){
      const t=document.createElement('textarea');
      t.value=email;
      t.setAttribute('readonly','');
      t.style.position='fixed';
      t.style.opacity='0';
      document.body.appendChild(t);
      t.select();
      try{ok=document.execCommand('copy')}catch{}
      t.remove();
    }
    copyEmail.textContent=ok?'Email Copied ✓':'Copy Manually';
    if(contactStatus)contactStatus.textContent=ok?'Copied '+email+' to your clipboard.':'Email: '+email;
    setTimeout(()=>copyEmail.textContent='Copy Email',1800);
  });
})();