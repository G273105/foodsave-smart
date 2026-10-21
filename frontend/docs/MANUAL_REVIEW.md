# Browser and integration checks still required

Use an agreed isolated test environment for database-changing actions.

1. Open API mode through localhost:3000 and check desktop/tablet/mobile widths
   1440, 768 and 390. Check keyboard focus, dialogs, labels and image layout.
2. Verify real original/reduced price/percentage against API response fields.
3. Confirm HOLD disables cards/details; check empty catalogue and service outage.
4. Once CORS is fixed, test sign-in, sign-out, token expiry and one approved test
   reservation. Verify backend stock decreases once and the PENDING reference appears.
5. Check conflict after stock changes. Do not blindly retry uncertain writes.
6. Confirm offset-aware expiry timestamps before accepting the countdown.
7. Verify unsupported history/cancel/staff features are clearly described.
8. Open OFFLINE_REVIEW.html separately; confirm it is labelled sample data.
9. Record actual browser/version/date, screenshots and Git commit evidence.
