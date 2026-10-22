/* Public settings only. JWTs are kept in memory after sign-in. */
window.FOODSAVE_CONFIG = Object.freeze({
 MODE: 'api', // Use 'mock' only for an explicitly labelled offline review.
 API_BASE_URL: 'https://foodsave-smart.onrender.com/api',
 CONTRACT_PROFILE: 'pence',
 CATEGORIES: [{category_id:1,name:'Ready meal'},{category_id:2,name:'Bakery'}],
 REQUEST_TIMEOUT_MS: 20000
});
