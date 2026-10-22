import {AppError,normalizeProduct,positiveId,quantity} from './model.js';
export function createApi(config,fetcher=globalThis.fetch){
 const base=String(config.API_BASE_URL||'').replace(/\/$/,'');
 if(!/^https?:\/\//.test(base)&&!base.startsWith('/'))throw new AppError('Configure a valid API base URL.','CONFIG');
 let token='',user=null,confirmed=[];
 const unsupported=message=>{throw new AppError(message,'NOT_SUPPORTED');};
 async function request(path,{method='GET',body,protectedRequest=false}={}){
  if(protectedRequest&&!token)throw new AppError('Please sign in to reserve food.','AUTH',401);
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),config.REQUEST_TIMEOUT_MS||12000);
  try{
   const headers={Accept:'application/json'};
   if(body!==undefined)headers['Content-Type']='application/json';
   if(protectedRequest)headers.Authorization='Bearer '+token;
   const response=await fetcher(base+path,{method,headers,credentials:'omit',signal:controller.signal,...(body!==undefined?{body:JSON.stringify(body)}:{})});
   let data;try{data=await response.json();}catch{throw new AppError(method==='GET'?'The service returned an unreadable response.':'The response is unreadable. The action may have completed; check with staff before retrying.','INVALID_JSON',response.status);}
   if(!response.ok){if(response.status===401&&protectedRequest){token='';user=null;confirmed=[];}
    const message=typeof data?.error==='string'?data.error:typeof data?.error?.message==='string'?data.error.message:typeof data?.message==='string'?data.message:({401:'Please sign in again.',409:'Availability has changed. Refresh the food selection.',503:'The database is unavailable. Please try again later.'}[response.status]||'The request failed.');
    throw new AppError(message,'HTTP_ERROR',response.status);
   }
   if(!data||typeof data!=='object')throw new AppError('Unexpected service response.','CONTRACT');
   return data;
  }catch(error){if(error instanceof AppError)throw error;throw new AppError(method==='GET'?'Cannot reach the service. Check your connection and try again.':'The connection was interrupted. The action may have completed; check with staff before retrying.',error.name==='AbortError'?'TIMEOUT':'NETWORK');}finally{clearTimeout(timer);}
 }
 async function products(){const data=await request('/products');if(!Array.isArray(data.products))throw new AppError('The service did not supply a product list.','CONTRACT');return data.products.map(raw=>normalizeProduct({...raw,can_reserve:raw.can_reserve===true&&data.fridge_status==='SAFE',reservation_message:raw.reservation_message||(data.fridge_status==='HOLD'?'Temporarily unavailable - temperature safety check':null)},'pence'));}
 return {
  mode:'api',sessionOnlyReservations:true,
  get user(){return user;},
  products,
  async product(id){positiveId(id);const p=(await products()).find(p=>p.batch_id===id);if(!p)throw new AppError('This product is no longer available. Refresh the food selection.','UNAVAILABLE',404);return p;},
  async login(email,password){const data=await request('/auth/login',{method:'POST',body:{email,password}});if(typeof data.access_token!=='string'||!data.user)throw new AppError('Sign-in was not confirmed.','CONTRACT');token=data.access_token;user=data.user;confirmed=[];return user;},
  async register(display_name,email,password){return request('/auth/register',{method:'POST',body:{display_name,email,password}});},
  async me(){const data=await request('/auth/me',{protectedRequest:true});user=data.user;return user;},
  logout(){token='';user=null;confirmed=[];},
  async reservations(){return confirmed.slice();},
  async reserve(batch_id,count){positiveId(batch_id);quantity(count);const data=await request('/reservations',{method:'POST',protectedRequest:true,body:{batch_id,quantity:count}});const value=data.reservation;if(!value||!Number.isSafeInteger(value.reservation_id)||value.status!=='PENDING')throw new AppError('The reservation response is incomplete. Check with staff before retrying.','CONTRACT');confirmed.push({...value,price_pence:value.unit_price_pence});return value;},
  async cancel(){unsupported('Cancellation is not available through the current API. Please contact collection staff.');},
  async collect(){unsupported('The current API does not provide a collection endpoint.');},
  async createProduct(){unsupported('The current API does not provide a staff stock-creation endpoint.');},
  async reports(){unsupported('Collection reports are not provided by the current API.');},
  async alerts(){const data=await request('/fridge/status');return data.status==='HOLD'?[{type:'Collection on hold',message:data.hold_reason||'Temperature safety check in progress.'}]:[];},
  async fridge(){const data=await request('/fridge/status');return {...data,connected:true,safety_state:data.status==='SAFE'?'OK':data.status};},
  async health(){return request('/health');}
 };
}
