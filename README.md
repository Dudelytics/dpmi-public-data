# Dudelytics DPMI — public derived data

The Dudelytics Productive Market Index (DPMI) measures the performance of the productive crypto asset universe defined by Dudelytics. It is an index published by Dudelytics, not by CoinGecko. Asset selection, weighting and index calculations follow the existing methodology; this archive changes none of them.

Methodology: https://dudelytics.com/dpmi/methodik/
English data entry point: https://dudelytics.com/en/dpmi/data/

**Data provided by [CoinGecko](https://www.coingecko.com/en/api)**: CoinGecko supplies underlying market observations. Dudelytics creates and publishes the index levels and scores.

## Scope

Six daily JSON files contain only existing, publicly published Dudelytics outputs: main DPMI, DPMI-HQ, seven sector index levels, Fear & Greed score, DVIX score and the observed DPMI leg of the daily benchmark. No BTC/ETH prices, market capitalizations, volumes, provider payloads, holdings, eligibility reviews, candidate/shadow data, admin data, configuration or credentials are archived. The benchmark file deliberately contains only the DPMI leg, not a full benchmark dataset. See [SCHEMA.md](SCHEMA.md).

Snapshots are captured after the UTC benchmark cutoff (scheduled at 00:30 UTC, with retries). Main/HQ/sector/score files preserve the source's actual timestamp; they are not represented as midnight observations. A stale source retains its actual timestamp. No missing values are invented, backfilled or interpolated. Historical percentage-change fields are excluded because some include backfill.

## History and provenance

The archive starts on **2026-10-03**. It does not retrospectively certify earlier publication. The main DPMI's live history begins on **2026-08-17T16:06:32Z**; each index can have a different observation start. Earlier reconstructed/backfilled history is not included. Scores may be derived from observed history, which is different from having been published contemporaneously in the past.

Files under `data/YYYY-MM-DD/` record their capture time and public source URL. Existing capture dates are never overwritten by the job. Scheduled GitHub Actions can run late; the source and capture timestamps make that delay explicit. A failed run does not commit a partial capture. Corrections, if needed, must be published separately with an explanation.

Git commits provide externally inspectable evidence of publication and changes. They are **not immutable proof**: repository owners can rewrite history. The capture record proves what this archive collected at that time, not that all earlier source history was contemporaneously published.

## Citation

> Dudelytics (YYYY-MM-DD), DPMI / [specific index], source timestamp [UTC timestamp], methodology [version], public derived data archive, [permanent GitHub commit URL]. Underlying market data provided by CoinGecko.

Cite the particular dated JSON file at a commit permalink. Dudelytics is the publisher; CoinGecko is the underlying data provider.

## License

Data and documentation: copyright Dudelytics / Axel Lämmle. All rights reserved except the quotation and attribution permissions described at https://dudelytics.com/lizenzen/. Public availability does not grant unrestricted redistribution, mirroring, resale or white-label rights. This repository does not grant rights to CoinGecko raw data, which it does not contain.

The collection script and workflow are operational code supplied for this official archive; no additional license is granted. The existing CoinGecko Commercial License has not been treated as an explicit authorization for a perpetual derived-data archive.
