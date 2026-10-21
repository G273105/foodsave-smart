/* Minimal DOM harness for event/state integration. This is NOT browser or visual QA. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{
 constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.attrs={};this.dataset={};this.value='';this.textContent='';this.listeners={};this.className='';this.disabled=false;this.hidden=false;this.open=false;this.classList={toggle:(s,on)=>{const names=new Set(this.className.split(' ').filter(Boolean));if(on)names.add(s);else names.delete(s);this.className=[...names].join(' ');}};}
 append(...nodes){this.children.push(...nodes);if(this.tagName==='SELECT'&&!this.value&&this.children[0])this.value=this.children[0].value;}
 prepend(...nodes){this.children.unshift(...nodes);}
 replaceChildren(...nodes){this.children=nodes;}
 setAttribute(k,v){this.attrs[k]=v;}
 removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 showModal(){this.open=true;}
 close(){this.open=false;this.listeners.close?.();}
 focus(){}
 querySelector(selector){return walk(this).find(e=>e.tagName===selector.toUpperCase())||null;}
 reset(){walk(this).forEach(e=>{if(e.tagName==='INPUT')e.value='';});}
}
function walk(el){return el.children.flatMap(child=>typeof child==='object'?[child,...walk(child)]:[]);}
function byText(root,text){return walk(root).find(el=>el.textContent===text);}
function documentHarness(){const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8'),ids={};for(const match of html.matchAll(/<([a-z0-9]+)\b[^>]*\bid="([^"]+)"[^>]*>/g)){const e=new Element(match[1]);e.id=match[2];ids[e.id]=e;}
const nav=[...html.matchAll(/<button class="nav[^"]*" data-view="([^"]+)"[^>]*>/g)].map(m=>{const e=m[1]==='staff'?ids['staff-nav']:new Element('button');e.dataset.view=m[1];return e;});const brands=[new Element('a'),new Element('a')];const views=['browse','reservations','status','staff'].map(id=>{ids[id].append(new Element('h1'));return ids[id];});const close=new Element('button');ids.sort.value='featured';ids['reservation-filter'].value='all';return {ids,views,nav,getElementById:id=>ids[id],createElement:tag=>new Element(tag),querySelector:()=>close,querySelectorAll:s=>s==='.nav'?nav:s==='.brand'?brands:s==='.view'?views:[]};}
const seed=JSON.parse(fs.readFileSync(new URL('../mocks/products.json',import.meta.url),'utf8'));
const flush=()=>new Promise(resolve=>setTimeout(resolve,15));
for (const delivery of ['source modules','downloaded browser bundle']) test('student and staff flow: '+delivery,async()=>{
 const doc=documentHarness(),storageData={};globalThis.document=doc;globalThis.window={FOODSAVE_CONFIG:{MODE:'mock',CATEGORIES:[{category_id:1,name:'Ready meal'},{category_id:2,name:'Bakery'}]},localStorage:{getItem:k=>storageData[k]??null,setItem:(k,v)=>{storageData[k]=v;}},scrollTo(){}};globalThis.history={replaceState(){}};globalThis.location={hash:''};globalThis.fetch=async()=>({ok:true,json:async()=>structuredClone(seed)});
 if(delivery==='downloaded browser bundle'){
  globalThis.fetch=async()=>{throw new Error('Local file review must not fetch JSON or API data');};
  vm.runInThisContext(fs.readFileSync(new URL('../config.js',import.meta.url),'utf8'));
  vm.runInThisContext(fs.readFileSync(new URL('../bundle.js',import.meta.url),'utf8'));
  await window.FOODSAVE_READY;
 }else{const {ready}=await import('../app.js?interface');await ready;}
 assert.equal(doc.nav.every(n=>typeof n.onclick==='function'),true);
 assert.equal(doc.ids['mode-banner'].textContent.startsWith('Independent review'),true);
 assert.equal(doc.ids.products.children.length,10);
 assert.equal(walk(doc.ids.products).filter(e=>e.tagName==='IMG').length,10);
 for(const image of walk(doc.ids.products).filter(e=>e.tagName==='IMG'))assert(fs.existsSync(new URL('../'+image.src,import.meta.url)));
 await doc.nav.find(n=>n.dataset.view==='staff').onclick();
 assert.equal(doc.ids.staff.hidden,false);
 await doc.nav.find(n=>n.dataset.view==='browse').onclick();
 assert.equal(doc.ids.browse.hidden,false);
 doc.ids.search.value='apples';doc.ids.search.oninput();assert.equal(doc.ids.products.children.length,1);
 doc.ids.search.value='nonexistent';doc.ids.search.oninput();assert.equal(doc.ids.products.children[0].textContent,'No matching food. Try a different search or category.');
 doc.ids.search.value='apples';doc.ids.search.oninput();await byText(doc.ids.products,'Reserve ↗').onclick();
 const details=doc.ids['detail-content'];assert.equal(doc.ids.details.open,true);const form=walk(details).find(x=>x.tagName==='FORM'),qty=walk(form).find(x=>x.tagName==='INPUT');qty.value='2';await form.onsubmit({preventDefault(){}});assert.equal(doc.ids.details.open,false);assert.equal(doc.ids['reservation-count'].textContent,1);
 const reservations=doc.ids['reservation-list'];byText(reservations,'Cancel reservation').onclick();await doc.ids['confirm-yes'].onclick();assert.equal(doc.ids['reservation-count'].textContent,0);
 // Reserve once more and confirm collection through the staff UI.
 await byText(doc.ids.products,'Reserve ↗').onclick();const form2=walk(doc.ids['detail-content']).find(x=>x.tagName==='FORM');await form2.onsubmit({preventDefault(){}});doc.ids['collection-id'].value='502';doc.ids['collect-form'].onsubmit({preventDefault(){}});await doc.ids['confirm-yes'].onclick();assert(walk(doc.ids['collection-feedback']).some(n=>String(n.textContent).includes('confirmed')));
 for(const [id,value] of Object.entries({'batch-name':'Staff lunch','batch-category':'1','batch-price':'5.50','batch-quantity':'3','batch-date':'2026-12-01T12:00','batch-allergens':'milk'}))doc.ids[id].value=value;
 await doc.ids['add-batch'].onsubmit({preventDefault(){}});assert(walk(doc.ids['batch-feedback']).some(n=>String(n.textContent).includes('saved')));doc.ids.search.value='Staff lunch';doc.ids.search.oninput();assert.equal(doc.ids.products.children.length,1);
 // Alerts and unavailable fridge status render independently.
 await doc.nav.find(x=>x.dataset.view==='status').onclick();assert(walk(doc.ids['fridge-content']).some(x=>x.textContent==='Status unavailable'));assert(doc.ids['alerts-content'].children.length>0);
 await flush();
});
