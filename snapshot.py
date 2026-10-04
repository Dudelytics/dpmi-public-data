#!/usr/bin/env python3
"""Archive an explicit projection of existing public Dudelytics JSONs."""
import argparse
import datetime as dt
import json
import math
import os
import tempfile
import pathlib
import re
import urllib.request

ENDPOINTS = {
    'dpmi': 'https://dudelytics.com/data/dpmi/current.json',
    'dpmi-hq': 'https://dudelytics.com/data/dpmi-holder-quality/current.json',
    'sectors': 'https://dudelytics.com/data/dpmi/sector-family.php',
    'fear-greed': 'https://dudelytics.com/data/dpmi/fear-greed.php',
    'dvix': 'https://dudelytics.com/data/dpmi/dvix.php',
    'benchmark-dpmi': 'https://dudelytics.com/data/dpmi/benchmark.json',
}
SECTORS = ('defi', 'rwa', 'ai', 'depin', 'interoperability', 'privacy_zk', 'smart_contract_platforms')

def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Missing or invalid derived index value')
    return value

def stamp(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|\+00:00)', value):
        raise ValueError('Invalid UTC source timestamp')
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat().replace('+00:00', 'Z')

def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', value):
        raise ValueError('Invalid methodology version')
    return value

def dvix_diagnosis(source):
    """Only public health labels; never copy the complete health or source object."""
    status = source.get('status')
    if status not in (None, 'live', 'stale', 'recovery_window', 'unavailable'):
        raise ValueError('Invalid DVIX public status')
    health = source.get('freshness')
    fresh = reason = None
    if health is not None:
        if not isinstance(health, dict) or type(health.get('fresh')) is not bool:
            raise ValueError('Invalid DVIX freshness diagnosis')
        fresh = health['fresh']
        reason = health.get('reason')
        if reason not in (None, 'observed_hourly_anchor_missing', 'source_timestamp_stale', 'current_unavailable'):
            raise ValueError('Invalid DVIX public freshness reason')
        if health.get('status') != status or fresh != (status == 'live'):
            raise ValueError('Inconsistent DVIX freshness status')
        if stamp(health.get('source_timestamp')) != stamp(source['timestamp']):
            raise ValueError('DVIX diagnosis describes a different observation')
    return {'status': status, 'freshness': {'fresh': fresh, 'reason': reason}}

def project(name, source):
    """No recursion or pass-through: only these named, validated fields leave memory."""
    if name in ('dpmi', 'dpmi-hq'):
        expected = 'DPMI' if name == 'dpmi' else 'DPMI-HQ'
        if source.get('index_id') != expected:
            raise ValueError('Unexpected index identifier')
        return {'index_id': expected, 'value': number(source['value']),
                'source_timestamp': stamp(source['timestamp']),
                'methodology_version': version(source['methodology_version']),
                'live_history_start': stamp(source['live_history_start'])}
    if name == 'sectors':
        return {'methodology_version': version(source['methodology_version']), 'sectors': {
            key: {'index_id': version(source['sectors'][key]['index_id']),
                  'value': number(source['sectors'][key]['value']),
                  'source_timestamp': stamp(source['sectors'][key]['timestamp']),
                  'live_history_start': stamp(source['sectors'][key]['live_history_start'])}
            for key in SECTORS}}
    if name in ('fear-greed', 'dvix'):
        score = number(source['score'])
        if not 0 <= score <= 100:
            raise ValueError('Score outside 0–100')
        projected = {'index_id': 'DPMI-FG' if name == 'fear-greed' else 'DVIX', 'score': score,
                'source_timestamp': stamp(source['timestamp']),
                'methodology_version': version(source['methodology_version'])}
        if name == 'dvix':
            projected.update(dvix_diagnosis(source))
        return projected
    if name == 'benchmark-dpmi':
        row = source['latest']
        own = row['series']['dpmi']
        if row.get('kind') != 'observed' or own.get('status') != 'observed':
            raise ValueError('Benchmark DPMI point is not observed')
        target = stamp(row['target_timestamp'])
        if target[11:] != '00:00:00Z':
            raise ValueError('Unexpected benchmark cutoff')
        return {'index_id': 'DPMI', 'value': number(own['value']),
                'target_timestamp': target,
                'source_timestamp': stamp(own['source_timestamp']),
                'observed_at_utc': stamp(row['observed_at_utc']),
                'methodology_version': version(own['methodology_version']),
                'benchmark_methodology_version': version(row.get('benchmark_methodology_version', source['methodology_version']))}
    raise ValueError('Unknown dataset')

def capture(root):
    now = dt.datetime.now(dt.timezone.utc)
    day = now.date().isoformat()
    destination = root / 'data' / day
    if destination.exists():
        expected = {f'{name}.json' for name in ENDPOINTS}
        if {f.name for f in destination.iterdir()} != expected:
            raise ValueError('Existing date is incomplete; do not overwrite or commit it')
        for filename in expected:
            existing = json.loads((destination / filename).read_text())
            if existing.get('capture_date_utc') != day:
                raise ValueError('Existing capture has invalid date')
        print(f'{day}: existing complete capture retained; no overwrite')
        return
    payloads = {}
    for name, url in ENDPOINTS.items():
        request = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Dudelytics-public-derived-archive/1.0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            # Only the fixed, public HTTPS endpoints; never authenticate or persist raw bodies.
            if response.geturl().split('?')[0] != url or response.status != 200:
                raise ValueError('Unexpected response or redirect')
            body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError('Public response exceeds size limit')
        projected = project(name, json.loads(body))
        if name == 'benchmark-dpmi' and projected['target_timestamp'][:10] != day:
            raise ValueError('Today’s observed DPMI cutoff is not available; retry later')
        payloads[name] = {'archive_schema': 'dudelytics.public-derived.v1',
                          'capture_date_utc': day,
                          'captured_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                          'source_url': url, 'data': projected}
    # Fail the entire capture before writing if any dataset is unavailable or invalid.
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Build outside data/: a failed write cannot leave a committable partial date.
    with tempfile.TemporaryDirectory(prefix='dpmi-capture-', dir=root) as temporary:
        stage = pathlib.Path(temporary) / day
        stage.mkdir()
        for name, payload in payloads.items():
            (stage / f'{name}.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
        os.rename(stage, destination)
    print(f'{day}: wrote {len(payloads)} derived-only datasets')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent)
    capture(parser.parse_args().root)
