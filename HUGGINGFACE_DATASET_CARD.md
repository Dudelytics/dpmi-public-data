---
pretty_name: Dudelytics DPMI Public Index Values
language:
- en
license: other
license_name: dudelytics-public-index-values
license_link: https://dudelytics.com/lizenzen/
tags:
- finance
- cryptocurrency
- time-series
- market-index
- observed-data
configs:
- config_name: dpmi
  default: true
  data_files:
  - split: train
    path: data/*/dpmi.json
- config_name: dpmi-hq
  data_files:
  - split: train
    path: data/*/dpmi-hq.json
- config_name: sectors
  data_files:
  - split: train
    path: data/*/sectors.json
- config_name: fear-greed
  data_files:
  - split: train
    path: data/*/fear-greed.json
- config_name: dvix
  data_files:
  - split: train
    path: data/*/dvix.json
- config_name: benchmark-dpmi
  data_files:
  - split: train
    path: data/*/benchmark-dpmi.json
dataset_info:
- config_name: dvix
  features:
  - name: archive_schema
    dtype: string
  - name: capture_date_utc
    dtype: string
  - name: captured_at_utc
    dtype: string
  - name: source_url
    dtype: string
  - name: data
    struct:
    - name: index_id
      dtype: string
    - name: score
      dtype: float64
    - name: source_timestamp
      dtype: string
    - name: methodology_version
      dtype: string
    - name: status
      dtype: string
    - name: freshness
      struct:
      - name: fresh
        dtype: bool
      - name: reason
        dtype: string
---

# Dudelytics DPMI Public Index Values

This dataset is a mirror of the Dudelytics public index-value archive at [GitHub](https://github.com/Dudelytics/dpmi-public-data). The GitHub repository is the canonical source. Dataset files on Hugging Face should be copied **only from that repository**, after the repository's [sanitizing rules](https://github.com/Dudelytics/dpmi-public-data/blob/main/SANITIZING.md) pass. Do not mirror production JSON endpoints directly.

## What it contains

Daily captures of Dudelytics' own derived levels and scores for the main DPMI, its own benchmark leg, sector indices, Fear & Greed, DVIX, and DPMI Holder Quality, as available in the canonical archive. Each dated capture records both its collection time and the source observation timestamp. Consult the [archive schema](https://github.com/Dudelytics/dpmi-public-data/blob/main/SCHEMA.md) for the exact fields and coverage of each file.

This mirror excludes raw CoinGecko prices, market capitalizations, trading volumes, constituent-level data, composition exports, and any admin, candidate, shadow, configuration, or credential material. CoinGecko is a supplier of underlying market data. Dudelytics publishes the derived index values.

## Provenance and interpretation

The main DPMI's observed history begins on **17 August 2026, 16:06:32 UTC**. Earlier main-index history, where present in the original public endpoint, is labeled as backfill and is not a contemporaneous observation. Other indices and indicators have their own starts and provenance; do not infer a shared observation start from the main DPMI. The dated public GitHub archive begins on **3 October 2026**. A captured source timestamp may predate the capture, including during a data recovery window. Captures do not certify that older observations were publicly available when they were originally computed.

The archive is a collection of observed captures, not a tamper-proof ledger. Repository owners can rewrite Git history. For a reproducible citation, link to the specific dated GitHub file at its commit permalink and cite its `source_timestamp` and `captured_at_utc` separately.

## Methodology

The DPMI is the Dudelytics Productive Market Index, an index of the selected productive crypto market according to its published rules. The sector family and derived indicators are distinct series with their own definitions and limitations. Read the [official methodology](https://dudelytics.com/dpmi/methodik/) and the [public data guide](https://dudelytics.com/dpmi/data/) before comparing values or drawing conclusions.

## Rights and citation

**License: other.** The applicable Dudelytics rights and permitted citation scope are described at [Licenses & Rights](https://dudelytics.com/lizenzen/). Public access does not imply an open-data, Creative Commons, or general redistribution license. Third-party data-provider rights remain separate. This is an official mirror operated by Dudelytics. Its publication by the rights holder does not grant third parties a general redistribution or mirroring license.

Suggested citation: Dudelytics ([year]), [index/indicator], value [value], source observation [source_timestamp UTC], captured [captured_at_utc UTC], methodology [methodology_version if available], canonical GitHub commit permalink. Accessed [date].

## Updates and limitations

The canonical GitHub archive is updated by a daily capture workflow after the 00:00 UTC benchmark cutoff. An initial or delayed capture may occur at another time; use each file's actual capture timestamp. A Hugging Face mirror may lag GitHub. No accuracy, investment, or trading claim follows from a value's presence in the archive. This dataset is not investment advice.
