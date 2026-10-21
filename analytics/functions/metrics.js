const {createHash}=require('node:crypto');
const ORIGINS=new Set(['https://www.agrinoteskau.com','https://agrinoteskau.com','https://kaumelon.github.io','https://statoberrypapaya.github.io']);
const ADMINS=new Set(['pratheesh.pg@kau.in']);
const BOOKS=new Set(['platform','agricultural-statistics','r-agricultural-data','professional-personal-skills','pgdaem-decision-making']);
const UUID=/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const digest=s=>createHash('sha256').update(s).digest('hex');
const dayAt=t=>new Date(t+19800000).toISOString().slice(0,10);
function validate(body){return body&&BOOKS.has(body.book)&&UUID.test(body.visitor||'')&&UUID.test(body.session||'')&&Number.isInteger(body.seconds)&&body.seconds>=0&&body.seconds<=21600&&Number.isInteger(body.seq)&&body.seq>=0&&body.seq<=10000&&typeof body.page==='string'&&/^\/[a-zA-Z0-9/_\-.]{0,180}$/.test(body.page)&&['mobile','tablet','desktop'].includes(body.device)&&['book','site'].includes(body.source);}
function increment(old={},delta={}){const next={...old};for(const [key,val]of Object.entries(delta))next[key]=(old[key]||0)+val;return next;}
function advance(previous,body,now){if(previous&&body.seq<=previous.seq)return null;const elapsed=previous?Math.max(0,(now-previous.updatedAt)/1000):0;const seconds=previous?Math.min(Math.max(0,body.seconds-previous.reportedSeconds),Math.floor(elapsed+3),90,Math.max(0,21600-(previous.activeSeconds||0))):0;const total=(previous?.activeSeconds||0)+seconds;return{seconds,total,newSession:!previous,newEngaged:total>=30&&!previous?.engaged,newPage:!previous||body.page!==previous.page,state:{seq:body.seq,reportedSeconds:body.seconds,activeSeconds:total,engaged:total>=30,page:body.page,createdAt:previous?.createdAt||now,updatedAt:now}};}
function createHandler(db,auth,Timestamp,clock=Date.now){let summaryCache=null,summaryPending=null;return async(req,res)=>{
 const origin=req.get('origin');res.set('Vary','Origin');res.set('Cache-Control','no-store');
 if(origin&&ORIGINS.has(origin))res.set('Access-Control-Allow-Origin',origin);
 res.set('Access-Control-Allow-Methods','GET, POST, OPTIONS');res.set('Access-Control-Allow-Headers','Content-Type, Authorization');
 if(req.method==='OPTIONS')return res.status(origin&&ORIGINS.has(origin)?204:403).send('');
 try{
 if(req.method==='GET'){
  if(req.query.summary==='public'){
   const now=clock();
   if(!summaryCache||now-summaryCache.at>=60000){
    if(!summaryPending)summaryPending=(async()=>{
     const refs=[];for(let i=29;i>=0;i--)refs.push(db.collection('melonMetricsDays').doc(dayAt(now-i*86400000)));
     const snapshots=await db.getAll(...refs),books={};
     for(const id of BOOKS)books[id]={opens:0,readers:0,engagedReads:0,activeSeconds:0,pageViews:0};
     for(const snap of snapshots)for(const [id,data]of Object.entries(snap.data()?.books||{}))if(BOOKS.has(id))for(const key of Object.keys(books[id]))books[id][key]+=Number.isSafeInteger(data[key])&&data[key]>=0?data[key]:0;
     summaryCache={at:now,data:{days:30,from:dayAt(now-29*86400000),through:dayAt(now),timezone:'Asia/Kolkata',updatedAt:new Date(now).toISOString(),books}};
    })().finally(()=>{summaryPending=null;});
    await summaryPending;
   }
   res.set('Cache-Control','public, max-age=60');return res.json(summaryCache.data);
  }
  const bearer=req.get('authorization')||'';if(!bearer.startsWith('Bearer '))return res.status(401).json({error:'Sign in to view metrics.'});
  let user;try{user=await auth.verifyIdToken(bearer.slice(7),true);}catch{return res.status(401).json({error:'Sign in again.'});}
  if(!(user.email_verified||user.melonMetricsAdmin===true)||!ADMINS.has((user.email||'').toLowerCase()))return res.status(403).json({error:'Administrator access is required.'});
  const days=Number(req.query.days||30);if(![7,30,90].includes(days))return res.status(400).json({error:'Choose 7, 30 or 90 days.'});
  const end=clock(),records=[];for(let i=days-1;i>=0;i--){const day=dayAt(end-i*86400000);records.push({day,ref:db.collection('melonMetricsDays').doc(day)});}
  const snapshots=await db.getAll(...records.map(x=>x.ref));
  return res.json({timezone:'Asia/Kolkata',days,generatedAt:new Date(end).toISOString(),daily:snapshots.map((s,i)=>({day:records[i].day,...(s.data()||{})})),definitions:{opens:'One book session per browser tab and book per IST day. Reloads in the same tab are deduplicated.',readers:'Estimated daily unique browsers, not verified students. Summing days counts returning browsers again.',engagedReads:'Book sessions with at least 30 estimated active seconds.',activeSeconds:'Visible, focused, recently active time. Idle after 90 seconds. Capped at 6 hours per session per day.',pageViews:'Chapter/page changes reported by the book; reloads in the same tab are deduplicated.'}});
 }
 if(req.method!=='POST')return res.status(405).json({error:'Method not allowed'});
 if(!origin||!ORIGINS.has(origin)||/bot|crawler|spider|headless|preview/i.test(req.get('user-agent')||''))return res.status(403).json({error:'Event not accepted'});
 if(Number(req.get('content-length')||0)>2048)return res.status(413).json({error:'Event too large'});
 let body=req.body;if(typeof body==='string'){try{body=JSON.parse(body);}catch{return res.status(400).json({error:'Invalid event'});}}
 if(!validate(body))return res.status(400).json({error:'Invalid event'});
 if(body.source==='site'&&body.book!=='platform')return res.status(400).json({error:'Book metrics must come from the book.'});
 const now=clock(),day=dayAt(now),expiry=Timestamp.fromMillis(now+45*86400000);
 const daily=db.collection('melonMetricsDays').doc(day),session=db.collection('melonMetricsSessions').doc(digest(day+'|'+body.book+'|'+body.visitor+'|'+body.session));
 const visitor=db.collection('melonMetricsVisitors').doc(digest(day+'|'+body.book+'|'+body.visitor));
 // Daily network cap limits accidental storms. Raw IP and browser identifiers are never stored in Firestore.
 const limit=db.collection('melonMetricsLimits').doc(digest(day+'|'+(req.ip||'unknown')+'|'+(req.get('user-agent')||'')));
 const result=await db.runTransaction(async tx=>{
  const [d,s,v,l]=await Promise.all([tx.get(daily),tx.get(session),tx.get(visitor),tx.get(limit)]);const previous=s.data(),a=advance(previous,body,now);
  if(!a)return{recorded:true,duplicate:true};
  if((l.data()?.count||0)>=3000)return{recorded:false,limited:true};
  if(previous&&body.page===previous.page&&now-previous.updatedAt<10000)return{recorded:false,retry:true};
  const data=d.data()||{},books=data.books||{},old=books[body.book]||{};
  const counts=increment(old,{opens:a.newSession?1:0,readers:v.exists?0:1,engagedReads:a.newEngaged?1:0,activeSeconds:a.seconds,pageViews:a.newPage?1:0});
  const devices={...(old.devices||{})};if(a.newSession)devices[body.device]=(devices[body.device]||0)+1;
  const pages={...(old.pages||{})};if(a.newPage&&Object.keys(pages).length<250)pages[body.page]=(pages[body.page]||0)+1;
  // A book may report time only after a first server timestamp exists; client totals alone cannot invent hours.
  tx.set(daily,{day,books:{...books,[body.book]:{...counts,devices,pages}},updatedAt:new Date(now).toISOString()});
  tx.set(session,{...a.state,expireAt:expiry});if(!v.exists)tx.set(visitor,{expireAt:expiry});
  tx.set(limit,{count:(l.data()?.count||0)+1,expireAt:expiry});return{recorded:true};
 });return res.status(result.limited?429:200).json(result);
 }catch(e){console.error('Me-LON metrics request failed',e.code||'request');return res.status(503).json({error:'Metrics temporarily unavailable.'});}
};}
module.exports={createHandler,validate,advance,dayAt,increment};



