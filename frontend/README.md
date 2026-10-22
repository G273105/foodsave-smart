# FoodSave Smart — Florin frontend API update

Updated 21 October 2026 against the supplied backend/API_CONTRACT.md.
The existing design, photos and offline sample inventory are retained.

## Open the website

For API integration, serve this folder at http://127.0.0.1:3000 and open
http://127.0.0.1:3000/index.html.

Windows with Python installed: double-click START_LOCAL.bat, keep its window open,
and open the address it prints. Alternatively run:

```
python -m http.server 3000 --bind 127.0.0.1
```

The default API URL is https://foodsave-smart.onrender.com/api in config.js.
Change it to http://127.0.0.1:5000/api to work with a local Flask backend.
A service outage displays an error; it never silently substitutes sample stock.

To inspect the existing offline experience without a server, double-click
OFFLINE_REVIEW.html. It is explicitly labelled sample data and makes no real bookings.
The root index.html opens API mode; double-clicking it cannot bypass browser CORS.

## Implemented for Florin

- GET /api/products and details from that same documented catalogue route.
- Original price, reduced price and discount percentage supplied by Flask.
- Integer pence converted only for GBP display; no frontend discount calculation.
- can_reserve and reservation_message used for disabled buttons and messages.
- Stock/expired/blocked display if supplied; HOLD prevents reservations.
- Registration, login, in-memory JWT and Bearer-authenticated reservation POST.
- Reservation body contains batch_id and quantity; no user ID chosen by frontend.
- PENDING confirmation, stock refresh, loading/empty/error states and conflict handling.
- Fridge SAFE/HOLD and alerts derived from fridge status.
- Only this signed-in session's successful reservation responses are shown.
- Logout clears token/account/session reservation list; refresh also clears them.
- No automatic retry of a failed write. Uncertain outcomes tell users to check with staff.

## Outstanding integration dependencies

1. Backend CORS: allow the agreed website origin on authentication AND reservation
   endpoints, including OPTIONS, Content-Type and Authorization. Current source
   allows auth only on localhost ports 3000/5173 and has no reservation CORS rule.
2. Expiry timezone: current sell_by_at omits an offset. The UI shows the supplied
   timestamp with a timezone notice. Countdown updates every 30 seconds when API
   timestamps include Z or an explicit offset. No timezone is guessed.
3. The catalogue excludes expired/out-of-stock batches. The UI can show their states
   when returned, but cannot invent missing products. Agree endpoint coverage.
4. Reservation history, cancellation, staff stock creation, collection and reports
   have no documented endpoints. API mode does not call invented routes. The staff
   workspace is available in offline review only. The alert panel uses fridge HOLD;
   it is not a full independent alerts feed.
5. Backend database compatibility and end-to-end reservation testing remain unverified.

No shared database accounts or bookings were created during this update.
Coordinate with the team before testing real registration/reservation writes.

## GitHub handover

Upload these files to your existing frontend folder on feature/frontend, preserving
its structure. Do not replace backend files or commit private .env credentials.
Source files live in dist; bundle.js is generated. After editing run:

```
npm run build
npm run check
npm test
```

No npm install is required for the included Node tests/build.
See docs/TEST_RESULTS.md and docs/HANDOVER.md for evidence and remaining checks.
