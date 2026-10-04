# Public derived archive schema v1

This is a minimal projection of existing public JSON endpoints, not an exact copy of those endpoint schemas. Index formulas and values are unchanged.

| Field | Type | Meaning |
|---|---|---|
| `archive_schema` | string | `dudelytics.public-derived.v1` |
| `capture_date_utc` | string | UTC calendar date, `YYYY-MM-DD`; also the directory name |
| `captured_at_utc` | string | Actual archive retrieval time in UTC; differs from source observation time |
| `source_url` | string | Fixed public Dudelytics JSON endpoint used for the projection |
| `data` | object | Dataset-specific allowlisted values below |

## DPMI and DPMI-HQ

`index_id` (string), `value` (finite number, index level), `source_timestamp` (UTC timestamp from the public source), `methodology_version` (string), `live_history_start` (UTC timestamp). `live_history_start` is the source's live-series start, not this GitHub archive's start. Percentage changes, reconstructed history and compositions are not included.

## Sector indices

`methodology_version` (string) and `sectors` (object). The fixed keys are `defi`, `rwa`, `ai`, `depin`, `interoperability`, `privacy_zk`, and `smart_contract_platforms`. Each value contains `index_id`, `value`, `source_timestamp`, and `live_history_start` with the same meanings as above. Eligibility/admission/review/status internals are not copied.

## Fear & Greed and DVIX

`index_id` (`DPMI-FG` or `DVIX`), `score` (finite number from 0 through 100), `source_timestamp`, and `methodology_version`. Components, raw or aggregated volumes, auxiliary values and retrospective score histories are not copied. The score is a derived indicator within Dudelytics' scope, not a whole-market observation or investment recommendation.

### DVIX public freshness diagnosis (prospective extension)

New DVIX captures additionally retain `data.status` (nullable string: `live`, `stale`, `recovery_window`, or `unavailable`) and `data.freshness` with `fresh` (nullable boolean) and `reason` (nullable string: `observed_hourly_anchor_missing`, `source_timestamp_stale`, or `current_unavailable`). These are the public endpoint's diagnosis at retrieval time, not a recalculation from archive time. Missing source diagnosis is represented by null, never by an inferred fresh status. All other source health fields and unknown fields remain excluded.

This is an additive extension of v1. Earlier dated files are not rewritten; their absent diagnosis means not captured, not fresh. Hugging Face must use an explicit DVIX feature schema to read old and extended files together without changing any archived bytes.

## DPMI leg of the daily benchmark

`index_id` (`DPMI`), `value` (index level), `target_timestamp` (today's 00:00 UTC cutoff), `source_timestamp` (actual DPMI observation selected by the existing benchmark), `observed_at_utc` (benchmark source's capture time), `methodology_version`, and `benchmark_methodology_version`. Only source rows explicitly marked `observed` are accepted. Source timestamp can precede the cutoff under the existing methodology. BTC, ETH, total-market values and normalization are excluded. No claim is made about completeness of the excluded benchmark legs.

## Failure and immutability policy

Missing or invalid numbers/timestamps, an unavailable source, or a missing current-day observed benchmark leg fail the capture before any data files are written. Existing date directories are retained without modification. A stale score's source timestamp remains visible; capture time must never be used as its freshness timestamp.
