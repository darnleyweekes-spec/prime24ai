"use strict";
(function(root){
 const statuses=["Missing","Needs correction","Received"];
 function clean(s,max=300){return String(s??"").replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,"").trim().slice(0,max);}
 function normalize(data){
  if(!data||!Array.isArray(data.items)||data.items.length>200)throw Error("Use a kit backup with at most 200 items.");
  const items=data.items.map(x=>{
   if(!x||!statuses.includes(x.status)||!clean(x.item)||!clean(x.client))throw Error("Each item needs a client, item name and valid status.");
   if(x.due && !/^\d{4}-\d{2}-\d{2}$/.test(x.due))throw Error("Dates must use YYYY-MM-DD.");
   return {client:clean(x.client,80),item:clean(x.item,160),due:clean(x.due,10),status:x.status};
  });
  return {version:1,items};
 }
 function draft(items,client,kind,portal){
  const rows=items.filter(x=>x.client===client),pending=rows.filter(x=>x.status!=="Received");
  if(!rows.length)throw Error("Add a request first.");
  const url=clean(portal,500);
  if(url){let u;try{u=new URL(url);}catch{throw Error("Enter a valid HTTPS portal address, or leave it blank.");}if(u.protocol!=="https:"||u.username||u.password)throw Error("Use an HTTPS portal address without embedded credentials.");}
  const received=rows.length-pending.length;
  if(!pending.length)return "Subject: Document checklist complete\n\nHi "+client+",\n\nThanks — all "+rows.length+" items on this checklist are marked received. We will review them and let you know if anything else is needed. This confirms receipt, not completion of the bookkeeping.\n\nThank you.";
  const intro={request:"Here is the document checklist for this period.",reminder:"These items are still open on our checklist.",overdue:"We are still waiting on the items below. Please let us know when you can provide them.",correction:"Please review the open items below, including anything marked for correction."}[kind]||"These items are still open on our checklist.";
  return "Subject: Open document requests\n\nHi "+client+",\n\n"+intro+"\n\n"+pending.map(x=>"- "+x.item+(x.status==="Needs correction"?" (correction requested)":"")+(x.due?" — requested by "+x.due:"")).join("\n")+"\n\n"+(url?"Please use your existing upload portal: "+url:"Please use our usual secure upload channel.")+"\n\nIf something is unavailable or does not apply, reply with the item name so we can agree on the next step."+ (received?"\n\nWe have marked "+received+" other item"+(received===1?"":"s")+" received; no need to resend those.":"")+"\n\nThank you.";
 }
 function csv(items){
  const cell=x=>{let v=String(x??"");if(/^[\s]*[=+@-]/.test(v))v="'"+v;return '"'+v.replace(/"/g,'""')+'"';};
  return [["Client alias","Item","Due date","Status"],...items.map(x=>[x.client,x.item,x.due,x.status])].map(row=>row.map(cell).join(",")).join("\r\n");
 }
 root.FollowUpKit={normalize,draft,csv,statuses};
})(typeof globalThis!=="undefined"?globalThis:this);