export class AppError extends Error {
  constructor(message, code='CLIENT_ERROR', status=0) {super(message); this.name='AppError'; this.code=code; this.status=status;}
}
export const money = pence => Number.isInteger(pence) ? new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(pence/100) : 'Not supplied';
export function positiveId(value,label='ID') {if(!Number.isSafeInteger(value)||value<1)throw new AppError(`${label} must be a positive integer.`,'VALIDATION');return value;}
export function quantity(value) {if(!Number.isSafeInteger(value)||value<1)throw new AppError('Enter a whole-number quantity of at least one.','VALIDATION');return value;}
export function normalizeProduct(raw,profile='pence') {
  if(!raw||typeof raw!=='object')throw new AppError('The server returned an invalid product.','CONTRACT');
  positiveId(raw.batch_id,'Product ID');
  if(typeof raw.name!=='string'||!raw.name.trim())throw new AppError('A product name is missing.','CONTRACT');
  if(!Number.isSafeInteger(raw.quantity_available)||raw.quantity_available<0)throw new AppError('The server returned invalid stock.','CONTRACT');
  const fromGbp = n => typeof n==='number'&&Number.isFinite(n)&&n>=0&&Math.abs(n*100-Math.round(n*100))<0.00001?Math.round(n*100):null;
  const original=profile==='gbp'?fromGbp(raw.original_price):raw.original_price_pence;
  const current=profile==='gbp'?fromGbp(raw.current_price):raw.discounted_price_pence;
  if(!Number.isSafeInteger(original)||original<0||!Number.isSafeInteger(current)||current<0)throw new AppError('The server must supply original and current prices in the configured format.','CONTRACT');
  let allergens=raw.allergens??raw.allergens_json;
  if(typeof allergens==='string'){try{allergens=JSON.parse(allergens);}catch{allergens=null;}}
  const allergensSupplied=raw.allergens_supplied!==undefined?raw.allergens_supplied:Array.isArray(allergens);
  const status=String(raw.status??raw.availability_status??'unavailable').toLowerCase();
  return {...raw,original_price_pence:original,discounted_price_pence:current,category:typeof raw.category==='string'?raw.category:'Other',status,allergens:Array.isArray(allergens)?allergens.filter(a=>typeof a==='string'):[],allergens_supplied:allergensSupplied,sell_by_at:raw.sell_by_at??null};
}
export function canReserve(product){return product.status==='available'&&product.quantity_available>0;}
export function createProductPayload(form,profile='pence') {
  const name=String(form.name??'').trim();if(!name||name.length>150)throw new AppError('Enter a product name of up to 150 characters.','VALIDATION');
  positiveId(form.category_id,'Category');quantity(form.quantity_available);
  if(!Number.isSafeInteger(form.original_price_pence)||form.original_price_pence<0)throw new AppError('Enter a valid non-negative price with up to two decimal places.','VALIDATION');
  if(!form.sell_by_at||Number.isNaN(Date.parse(form.sell_by_at)))throw new AppError('Enter a valid sell-by date and time.','VALIDATION');
  const common={name,category_id:form.category_id,sell_by_at:new Date(form.sell_by_at).toISOString()};
  if(profile==='gbp')return {...common,original_price:form.original_price_pence/100,quantity:form.quantity_available,allergens:form.allergens};
  return {...common,original_price_pence:form.original_price_pence,quantity_available:form.quantity_available,allergens_json:form.allergens};
}
export function priceInputToPence(text){if(!/^\d+(\.\d{1,2})?$/.test(String(text)))throw new AppError('Enter a price such as 5.50.','VALIDATION');const result=Math.round(Number(text)*100);if(!Number.isSafeInteger(result))throw new AppError('Price is too large.','VALIDATION');return result;}
export function formatDate(value){if(!value)return 'Not supplied';const date=new Date(value);return Number.isNaN(date.getTime())?'Not supplied':new Intl.DateTimeFormat('en-GB',{dateStyle:'medium',timeStyle:'short',timeZone:'Europe/London'}).format(date)+' (UK)';}
