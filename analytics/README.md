# Me-LON usage analytics

Firebase project: `statoberrydrona` (existing Blaze plan). Firestore: default database in `asia-south1`.
Endpoint: `https://asia-south1-statoberrydrona.cloudfunctions.net/melonMetrics`.
Dashboard: `https://www.agrinoteskau.com/usage.html`.

## Public summary

The homepage, library book cards and usage page display 30-day aggregate totals. GET with ?summary=public returns only fixed-period totals for the allowlisted resources, with a one-minute server cache. It excludes daily records, page breakdowns, visitor records and identifiers.

## Access

Only verified Firebase accounts for `pratheesh.pg@kau.in` and `statoberry@gmail.com` may request reports. Use the dashboard to sign in, create the Pratheesh account if needed, verify the email, or request a password reset. Passwords go directly to Firebase Authentication; they are not stored by the website. The function checks the verified email on every report request. Existing Firestore rules deny all direct client access and are unchanged.

## What the numbers mean

- Opens: one session per browser tab, book and IST calendar day. Reloads in the same session do not add opens.
- Daily readers: unique random browser identifiers per resource and day. Summing daily readers is not period-unique students.
- Engaged sessions: at least 30 estimated active seconds.
- Active time: visible, focused and recently active browser time, paused after 90 idle seconds, capped at six hours per session/day.
- Page views: page/chapter transitions, deduplicated on reload. Direct book visits also report usage; browsers blocking collection are absent.
- A book reader passes its anonymous Me-LON context to an allowlisted embedded book using `postMessage`. This supports third-party storage blocking and keeps the parent iframe from guessing reading activity.

The system does not backfill past use, identify students, prove attendance or completion, or promise tamper-proof counts. CORS, validation, bot filtering, per-network daily caps and maximum function instances reduce accidental/automated abuse but do not authenticate anonymous readers.

## Data and cost controls

All documents use `melonMetrics*` namespaces. Raw IP, name and email are not included in these records. Rate-limit keys use a one-way digest scoped to an IST day. Google infrastructure logs may contain request metadata. Daily aggregates remain for reports. Session, visitor and rate-limit records have 45-day Firestore TTL. One heartbeat per active minute plus navigation events, maximum two function instances and zero minimum instances. These reduce cost; they are not a hard billing cap. Deployment image cleanup is enabled.

## Updates

1. Edit source assets and run `scripts/render.ps1` to render the site with content-versioned CSS.
2. Run `node --test analytics/functions/*.test.js analytics/tracker.test.cjs`.
3. From `analytics/`, deploy only `functions:melon-metrics` to `statoberrydrona`. Do not deploy replacement Firestore rules or other DRONA resources.
4. Book trackers live inside the published statistics and R books, as well as the Me-LON wrapper. Their source configurations include the scripts for future renders. `integrate-books.cjs` stages tracker updates in the isolated clones in `analytics/integrations`; inspect before pushing.
5. Push rendered Me-LON `docs/` and the book tracker changes, then check each Pages deployment.

No audit inventories, service-account keys, credentials, or cloned book repositories are part of the published Me-LON website.

