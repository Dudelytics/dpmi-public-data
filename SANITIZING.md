# Pre-publication sanitizing rules

Reviewed against the Dudelytics secure source export policy (snapshot 2026-10-02, source-export.php 0.8d), plus the stricter public-data scope agreed for this archive.

The repository is built from new documentation, a public-only collector, a GitHub workflow and six projected JSON files. No source snapshot files are copied. Never upload private directories, backups, sessions, logs, caches/temp, .env files, provider configuration, credentials, key/certificate files, database dumps or archives. The source export's filename/directory exclusion rules remain a minimum requirement; source-export eligibility alone does not make a file public.

Only the six hard-coded HTTPS source endpoints are fetched, without authentication. Raw responses are used only in memory and never written or logged. The collector copies named fields individually and validates numbers, UTC timestamps and bounded version identifiers. It never recursively copies objects. Unknown source fields do not enter the archive.

Only the DPMI leg leaves the benchmark response. No provider prices, market caps, volumes, API keys, admin/candidate/shadow/review fields or configuration are allowed. Do not add historical change fields without separately verifying their provenance.

Before the first publication, check every staged path and JSON structure, compare values and timestamps against fetched public inputs, inject forbidden fields in a test to ensure they are excluded, and confirm that a failed source cannot publish a partial capture. Changes to the allowlist require review before publication.
