import {formatReadingTime} from './reading-time.js?v=20261021-1';
(() => {
 'use strict';
 const blocks=[...document.querySelectorAll('[data-public-usage]')],bookPanels=[...document.querySelectorAll('[data-book-usage]')];
 if(!blocks.length&&!bookPanels.length)return;
 const number=n=>new Intl.NumberFormat('en-IN',{maximumFractionDigits:0}).format(n);
 async function load(){
  const response=await fetch('https://asia-south1-statoberrydrona.cloudfunctions.net/melonMetrics?summary=public',{credentials:'omit',signal:AbortSignal.timeout(12000)});
  if(!response.ok)throw Error('Usage unavailable');const data=await response.json();
  for(const id of ['platform','agricultural-statistics','r-agricultural-data'])if(!data.books?.[id]||!['opens','engagedReads','activeSeconds'].every(k=>Number.isFinite(data.books[id][k])&&data.books[id][k]>=0))throw Error('Invalid usage');
  const books=Object.entries(data.books).filter(([id])=>id!=='platform').map(([,book])=>book),totals={visits:data.books.platform.opens,opens:books.reduce((n,b)=>n+b.opens,0),engaged:books.reduce((n,b)=>n+b.engagedReads,0),minutes:books.reduce((n,b)=>n+b.activeSeconds,0)};
  for(const block of blocks){for(const key of Object.keys(totals)){const el=block.querySelector(`[data-usage="${key}"]`);if(el)el.textContent=key==='minutes'?formatReadingTime(totals[key]):number(totals[key]);}const status=block.querySelector('[data-usage-status]');if(status)status.textContent=`Last 30 days · ${data.from} to ${data.through} (IST). Updated ${new Date(data.updatedAt).toLocaleTimeString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit'})} IST.`;}
  for(const panel of bookPanels){const b=data.books[panel.dataset.bookUsage];if(!b){panel.textContent="Tracking starting soon";continue;}panel.textContent=`${number(b.opens)} opens · ${number(b.engagedReads)} reads · ${formatReadingTime(b.activeSeconds)}`;panel.title='Last 30 days. An engaged read is a session with at least 30 estimated active seconds. Reloads in the same tab are deduplicated.';}
 }
 load().catch(()=>{for(const block of blocks){const status=block.querySelector('[data-usage-status]');if(status)status.textContent='Usage totals are temporarily unavailable. Please try again later.';}for(const panel of bookPanels)panel.textContent='Usage temporarily unavailable';});
})();
