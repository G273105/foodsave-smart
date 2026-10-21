# FoodSave Smart — Florin Tompi's front-end handover

Prepared 18 October 2026 for CPU4106. HTML, CSS and vanilla JavaScript, with no build step or third-party runtime dependencies.

## What is ready

- Responsive food catalogue with local photographs, dynamic category filtering, search and sorting.
- Product details, source-provided prices, allergens, sell-by information and quantity selection.
- Student reservations, active/collected/cancelled filters and cancellation confirmation.
- Staff workspace: batch creation, collection by reservation reference, stock overview and collection-only reports.
- Fridge and alert panels with honest unavailable, empty, loading and error states.
- Separate API and independent-review data services. API failures never switch silently to sample data.
- Configurable pence and GBP API profiles to accommodate the conflicting supplied documents.
- Request timeouts, no automatic mutation retries, duplicate-submit guards and server-status validation.
- Keyboard-operable native controls and dialogs, visible focus, skip link, live messages and responsive styles.
- Automated service checks and application event/state flows, including the delivered browser bundle, in a lightweight DOM harness.

This is an implemented front-end, not a claim of completed team integration. The published review runs independently until a working backend is provided. Live authentication, shared persistence and fridge readings have not been verified.

## Run locally

1. Right-click the ZIP and choose **Extract All**. Keep all folders together.
2. Open the extracted folder and double-click **index.html** at the top level.
3. The food selection, local photos, filters, reservations and staff review tools work directly from your device. No terminal or installation is required for independent review.

The committed `bundle.js` includes the same application code and embedded review product data, so local file access does not need ES module imports or JSON fetches. Source modules remain separate for maintenance. After editing a source module or product JSON, run `npm run build` and include the rebuilt bundle.

For backend integration or HTTP testing, optionally run `python -m http.server 8080` and visit http://localhost:8080. Live backend access still requires the team's API and appropriate server permissions.

No npm install is needed. To run the independent tests, use Node.js 20+ (Node.js 24 was used here):

```sh
npm test
npm run check
```

## Project files

| File | Purpose |
|---|---|
| `index.html`, `style.css` | Page structure and shared visual system |
| `app.js` | Interface events, validation and rendering |
| `model.js` | Money representation, product normalization and input validation |
| `api.js` | Flask HTTP adapter; no business-rule price calculation |
| `mock.js` | Isolated local review service; never used in API mode |
| `config.js` | Explicit deployment configuration |
| `mocks/products.json` | Product-list reference values for independent review only |
| `assets/` | Local illustrative food photographs and placeholder |
| `tests/` | Service, contract and UI event/state checks |
| `docs/HANDOVER.md` | Exact connection steps and unresolved team decisions |
| `docs/TEST_RESULTS.md` | Confirmed checks and verification limits |
| `docs/MANUAL_REVIEW.md` | Browser, keyboard and live-integration checklist |
| `inventory.html` | Unchanged earlier inventory prototype, preserved for reference; not the final staff/API flow |

Copy the contents of this package into the team frontend folder. Include the tests and docs in the PR. Do not copy any Sites hosting identity into the team's repository.

## Review data and honesty

The top banner identifies independent-review mode. Reservations, staff actions and quantities in that mode are stored on the reviewer's device, not in the team's database. No payment is taken. Product photographs are illustrative.

All ten original/reduced prices come from `FoodSaveSmart_Product_List_LARGE_PRINT_2_PAGES.docx`. The first four names, original prices, stock quantities, batch IDs, dates and allergens also follow `updated.sql`. The other six are document demonstration additions; their IDs, categories, stock, portions and reductions are not verified production records. They are never sent as automatic database seed data.

The three historical sell-by dates stay unchanged and cannot be reserved in the local review. The mock service may block a product when its sample date passes; this is isolated test behaviour, not the live source of truth. The API profile renders server status and prices. Only the backend may authorize reservations and calculate discounts.

## Asset provenance

Illustrative photographs are local downloads from Unsplash. See `docs/ASSETS.md` for source URLs. They are not photographs of confirmed campus stock. Replace them with staff-provided photos of actual products when available.

## Upload to the team GitHub repository

Ask the repository owner for write access if GitHub disables uploads. Extract the ZIP first. Upload the extracted files, not just the ZIP. Agree on a `frontend/` folder with the team; preserve their backend and existing files. Include the root HTML, CSS, JavaScript and assets, `scripts/`, `package.json`, tests and documentation.

For an independent frontend-only repository, upload all contents of this package to its root. The optional `.github/workflows/pages.yml` deploys the staged root website through GitHub Pages only when manually run, after Pages is enabled with GitHub Actions as its source. For the shared team repository, have the maintainer adapt paths to the agreed frontend directory before adding the workflow. GitHub Pages serves only the frontend; it does not run Flask or the database.

## Direct root entry point

The root index.html contains the complete application page. No redirect or dist directory is required. Open index.html locally or serve this directory; the root URL opens the application directly. If placed under frontend/ in the shared repository, configure hosting to publish frontend/ as its document root. The Pages workflow stages website files only in .pages-site; tests and documentation are excluded.
