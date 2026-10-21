/* Deployment configuration, not a sign-in mechanism. No credentials belong here. */
window.FOODSAVE_CONFIG = Object.freeze({
  MODE: 'mock', // 'mock' for independent review; 'api' to use the team's Flask service.
  API_BASE_URL: 'http://127.0.0.1:5000/api',
  CONTRACT_PROFILE: 'pence', // 'pence' preserves database fields; 'gbp' implements api-contract.docx.
  USER_ID: 1, // updated.sql seeds student 1; the older API draft uses student 12. Confirm at integration.
  STAFF_USER_ID: 2,
  ROLE: 'student', // API mode reads this trusted deployment setting; backend MUST enforce permissions.
  CREDENTIALS: 'same-origin', // change to 'include' only with backend session/CORS/CSRF agreement.
  CSRF_TOKEN: '', // session token may be injected at runtime by Flask, never committed.
  FRIDGE_STATUS_PATH: null, // No agreed route exists. Configure a relative /api-base route after agreement.
  CATEGORIES: [{category_id: 1, name: 'Ready meal'}, {category_id: 2, name: 'Bakery'}],
  REQUEST_TIMEOUT_MS: 12000
});
