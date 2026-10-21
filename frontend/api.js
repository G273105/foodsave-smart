import {AppError,normalizeProduct,positiveId,quantity,createProductPayload} from './model.js';
export function createApi(config,fetcher=globalThis.fetch){
  const base=String(config.API_BASE_URL||'').replace(/\/$/,'');
  if(!/^https?:\/\//.test(base)&&!base.startsWith('/'))throw new AppError('Configure a valid API base URL.','CONFIG');
  const profile=config.CONTRACT_PROFILE;if(!['gbp','pence'].includes(profile))throw new AppError('Select the pence or gbp API contract profile.','CONFIG');
  async function request(path,{method='GET',body}={}){
    const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),config.REQUEST_TIMEOUT_MS||12000);
    try{
      const headers={Accept:'application/json'};if(body!==undefined)headers['Content-Type']='application/json';if(config.CSRF_TOKEN)headers['X-CSRF-Token']=config.CSRF_TOKEN;
      const response=await fetcher(base+path,{method,headers,credentials:config.CREDENTIALS||'same-origin',signal:controller.signal,...(body!==undefined?{body:JSON.stringify(body)}:{})});
      let data;try{data=await response.json();}catch{throw new AppError(method==='GET'?'The server returned an unreadable response.':'The server response is unreadable. The action may have completed; refresh before retrying.','INVALID_JSON',response.status);}
      if(!response.ok){const messages={401:'Sign in through the team application to continue.',403:'You do not have permission for this action.',404:'That record could not be found.',409:'Availability or reservation status has changed. Refresh and try again.',500:'The server could not complete the request.'};throw new AppError(typeof data?.error?.message==='string'?data.error.message:messages[response.status]||'The request failed.',data?.error?.code||'HTTP_ERROR',response.status);}
      if(data?.error)throw new AppError(data.error.message||'The server returned an error.',data.error.code||'API_ERROR',response.status);
      if(!data||typeof data!=='object')throw new AppError('The server returned an unexpected response.','CONTRACT');
      return data;
    }catch(error){if(error instanceof AppError)throw error;throw new AppError(method==='GET'?'Could not reach the team service. Check the connection and try again.':'The connection was interrupted. The action may have completed; refresh before retrying.',error.name==='AbortError'?'TIMEOUT':'NETWORK');}finally{clearTimeout(timer);}
  }
  const list=(data,key)=>{if(!Array.isArray(data[key]))throw new AppError(`The server did not return the expected ${key} list.`,'CONTRACT');return data[key];};
  const checkStatus=(r,status)=>{if(!status.includes(r.status.toLowerCase()))throw new AppError('The action was not confirmed. Refresh before retrying.','CONTRACT');return r;};
  const reservationResult=data=>{positiveId(data.reservation_id,'Reservation ID');if(typeof data.status!=='string')throw new AppError('Reservation status is missing.','CONTRACT');return data;};
  return {
    mode:'api',
    async products(){return list(await request('/products'),'products').map(p=>normalizeProduct(p,profile));},
    async product(id){positiveId(id);return normalizeProduct((await request('/products/'+id)).product,profile);},
    async reservations(){return list(await request('/reservations?user_id='+positiveId(config.USER_ID,'User ID')),'reservations').map(reservationResult);},
    async reserve(batch_id,count){positiveId(batch_id);quantity(count);return checkStatus(reservationResult(await request('/reservations',{method:'POST',body:{batch_id,user_id:positiveId(config.USER_ID),quantity:count}})),['reserved','pending']);},
    async cancel(id){positiveId(id);return checkStatus(reservationResult(await request('/reservations/'+id+'/cancel',{method:'POST',body:{user_id:positiveId(config.USER_ID)}})),['cancelled']);},
    async collect(id){positiveId(id);return checkStatus(reservationResult(await request('/reservations/'+id+'/collect',{method:'POST',body:{staff_user_id:positiveId(config.STAFF_USER_ID)}})),['collected']);},
    async createProduct(form){const result=await request('/products',{method:'POST',body:createProductPayload(form,profile)});positiveId(result.batch_id,'Created product ID');if(result.status!=='created')throw new AppError('Batch creation was not confirmed. Refresh before retrying.','CONTRACT');return result;},
    async alerts(){return list(await request('/alerts'),'alerts');},
    async reports(){return request('/reports');},
    async fridge(){if(!config.FRIDGE_STATUS_PATH)return {connected:false,safety_state:null,hold_reason:'Live fridge status is awaiting an agreed backend route.'};const data=await request(config.FRIDGE_STATUS_PATH);return {connected:true,...data};},
    async health(){return request('/health');}
  };
}
