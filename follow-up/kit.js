"use strict";
(function(){
 const $=id=>document.getElementById(id),kit=globalThis.FollowUpKit;
 let items=[];
 function announce(s){$("notice").textContent=s;}
 function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function render(){
  const old=$("client").value,clients=[...new Set(items.map(x=>x.client))];
  $("client").replaceChildren(...clients.map(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;return o;}));
  if(clients.includes(old))$("client").value=old;
  $("rows").replaceChildren();
  items.forEach((x,i)=>{
   const tr=document.createElement("tr");
   [x.client,x.item,x.due||"Not set"].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.append(td);});
   const td=document.createElement("td"),sel=document.createElement("select");sel.setAttribute("aria-label","Status for "+x.item+" for "+x.client);
   kit.statuses.forEach(s=>{const o=document.createElement("option");o.value=s;o.textContent=s;sel.append(o);});sel.value=x.status;sel.onchange=()=>{items[i].status=sel.value;render();};td.append(sel);tr.append(td);
   const action=document.createElement("td"),b=document.createElement("button");b.type="button";b.textContent="Remove";b.className="quiet";b.setAttribute("aria-label","Remove "+x.item+" for "+x.client);b.onclick=()=>{items.splice(i,1);render();announce("Item removed. Download a backup to keep changes.");};action.append(b);tr.append(action);$("rows").append(tr);
  });
  $("empty").hidden=items.length>0;
  $("count").textContent=items.filter(x=>x.status!=="Received").length+" open / "+items.length+" total";
  $("draft").value="";$("copy").disabled=true;$("save-draft").disabled=true;
  $("generate").disabled=!items.length;
 }
 $("add").onsubmit=e=>{
  e.preventDefault();try{
   const row={client:$("alias").value,item:$("item").value,due:$("due").value,status:"Missing"};
   items=kit.normalize({items:[...items,row]}).items;
   $("item").value="";render();announce("Request added. Data stays in this tab until you download it.");
  }catch(err){announce(err.message);}
 };
 $("sample").onclick=()=>{
  if(items.length&&!confirm("Replace the current list with fictional sample requests? Download a backup first if needed."))return;
  items=[{client:"Sample client A",item:"August bank statement",due:"",status:"Received"},{client:"Sample client A",item:"August card statement",due:"",status:"Missing"},{client:"Sample client A",item:"Receipt for the equipment purchase",due:"",status:"Needs correction"}];render();announce("Fictional sample loaded. Mark the card statement received to see the next draft change.");
 };
 $("generate").onclick=()=>{try{$("draft").value=kit.draft(items,$("client").value,$("tone").value,$("portal").value);$("copy").disabled=false;$("save-draft").disabled=false;announce("Draft ready. Check item names, dates and portal address before sending.");}catch(err){announce(err.message);}};
 ["client","tone","portal"].forEach(id=>$(id).addEventListener("input",()=>{$("draft").value="";$("copy").disabled=true;$("save-draft").disabled=true;}));
 $("copy").onclick=async()=>{try{await navigator.clipboard.writeText($("draft").value);announce("Draft copied. Nothing has been sent.");}catch{$("draft").focus();$("draft").select();announce("Select and copy the draft, or download it.");}};
 $("save-draft").onclick=()=>download("follow-up-draft.txt",$("draft").value,"text/plain");
 $("csv").onclick=()=>download("document-tracker.csv",kit.csv(items),"text/csv;charset=utf-8");
 $("backup").onclick=()=>{download("follow-up-backup.json",JSON.stringify({version:1,items},null,2),"application/json");announce("Backup downloaded. Keep it in a folder approved by your firm.");};
 $("restore").onchange=async e=>{
  const f=e.target.files[0];if(!f)return;
  try{if(f.size>200000)throw Error("Backup is too large. Maximum 200 KB.");
   const parsed=kit.normalize(JSON.parse(await f.text()));
   if(items.length&&!confirm("Replace your current list with this backup?"))return;
   items=parsed.items;render();announce("Backup restored in this tab.");
  }catch(err){announce("Could not restore: "+err.message);}finally{e.target.value="";}
 };
 $("clear").onclick=()=>{if(items.length&&!confirm("Clear this tab's list? Download a backup first if needed."))return;items=[];render();announce("List cleared.");};
 $("intake").onsubmit=e=>{
  e.preventDefault();
  const body="Client Follow-Up Kit setup\n\nFirm: "+$("firm").value+"\nWork email: "+$("email").value+"\nExisting portal: "+$("intake-portal").value+"\nWorkflow: "+$("workflow").value+"\n\nI understand this is a $149 manual setup service for one monthly workflow. Please confirm availability before I order.";
  $("intake-text").value=body;$("intake-result").hidden=false;
  $("email-draft").href="mailto:darnleyweekes@prime24ai.com?subject="+encodeURIComponent("Client Follow-Up Kit setup request")+"&body="+encodeURIComponent(body);
  $("gmail-draft").href="https://mail.google.com/mail/?view=cm&fs=1&to=darnleyweekes%40prime24ai.com&su="+encodeURIComponent("Client Follow-Up Kit setup request")+"&body="+encodeURIComponent(body);
  $("intake-status").textContent="Your request is prepared below. Open it in email and send it to submit. This page has not sent anything.";
 };
 render();
})();