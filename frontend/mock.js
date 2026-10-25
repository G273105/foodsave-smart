/* Independent fixture service. It never runs in API mode and does not define backend business rules. */
import {AppError,normalizeProduct,quantity,positiveId,createProductPayload} from './model.js';
export function createMockService(seed,{storage=null,now=()=>new Date()}={}){
  const KEY='foodsave-independent-review-v4';let persistent=!!storage;
  let state={products:structuredClone(seed),reservations:[],nextReservation:501};
  try{const saved=JSON.parse(storage?.getItem(KEY)||'null');if(saved&&Array.isArray(saved.products)&&Array.isArray(saved.reservations)&&Number.isSafeInteger(saved.nextReservation)&&saved.nextReservation>=501){saved.products.forEach(p=>normalizeProduct(p));state=saved;}}catch{persistent=false;}
  function save(){try{if(!storage)throw Error();storage.setItem(KEY,JSON.stringify(state));}catch{persistent=false;}}
  const effective=p=>({...p,status:p.sell_by_at&&new Date(p.sell_by_at)<=now()?'past_sell_by':p.status});
  function findProduct(id){const p=state.products.find(p=>p.batch_id===id);if(!p)throw new AppError('Product not found.','NOT_FOUND',404);return p;}
  function findReservation(id){const r=state.reservations.find(r=>r.reservation_id===id);if(!r)throw new AppError('Reservation not found.','NOT_FOUND',404);return r;}
  return {
    mode:'mock',get persistent(){return persistent;},
    async products(){return structuredClone(state.products.map(p=>normalizeProduct(effective(p))));},
    async product(id){return normalizeProduct(structuredClone(effective(findProduct(id))));},
    async reservations(){return structuredClone(state.reservations);},
    async reserve(id,count){positiveId(id);quantity(count);const p=findProduct(id);if(effective(p).status!=='available'||p.quantity_available<count)throw new AppError('This quantity is no longer available.','CONFLICT',409);p.quantity_available-=count;const reservation={reservation_id:state.nextReservation++,batch_id:id,name:p.name,quantity:count,status:'reserved',price_pence:p.discounted_price_pence,original_price_pence:p.original_price_pence,created_at:now().toISOString()};state.reservations.push(reservation);save();return structuredClone(reservation);},
    async cancel(id){const r=findReservation(id);if(r.status==='cancelled')return structuredClone(r);if(r.status!=='reserved')throw new AppError('Only an active reservation can be cancelled.','CONFLICT',409);findProduct(r.batch_id).quantity_available+=r.quantity;r.status='cancelled';save();return structuredClone(r);},
    async collect(id){const r=findReservation(id);if(r.status==='collected')return structuredClone(r);if(r.status!=='reserved')throw new AppError('Only an active reservation can be collected.','CONFLICT',409);r.status='collected';save();return structuredClone(r);},
    async createProduct(form){createProductPayload(form,'pence');const batch_id=Math.max(...state.products.map(p=>p.batch_id),0)+1;const p={...structuredClone(form),batch_id,category:form.category_name||'Other',discounted_price_pence:form.original_price_pence,status:'available',availability_status:'AVAILABLE',allergens_supplied:true,source:'staff review entry'};state.products.push(p);save();return {batch_id,status:'created'};},
    async alerts(){return [{alert_id:1,type:'integration',message:'Independent review mode: stock, reservations and staff actions are local examples.'},...state.products.filter(p=>effective(p).status==='past_sell_by').map(p=>({alert_id:100+p.batch_id,batch_id:p.batch_id,type:'past_sell_by',message:p.name+' has passed its recorded sample sell-by date.'}))];},
    async reports(){const collected=state.reservations.filter(r=>r.status==='collected');return {collected_units:collected.reduce((s,r)=>s+r.quantity,0),estimated_original_value_gbp:collected.reduce((s,r)=>s+r.original_price_pence*r.quantity,0)/100,estimated_sales_value_gbp:collected.reduce((s,r)=>s+r.price_pence*r.quantity,0)/100};},
    async fridge(){return {connected:false,safety_state:null,hold_reason:'The review site has no live fridge connection.'};},
    async health(){return {status:'ok',source:'local review fixtures'};}
  };
}
