#!/usr/bin/env python3
"""Mirror committed, validated public projections; never replace historic data."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess

from snapshot import ENDPOINTS, SECTORS, project, stamp

REPO = 'Dudelytics/dpmi-public-data'
ENVELOPE = {'archive_schema', 'capture_date_utc', 'captured_at_utc', 'source_url', 'data'}

def git(*args):
    return subprocess.check_output(['git', *args])

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result

def validate(path, body):
    match = re.fullmatch(r'data/(\d{4}-\d{2}-\d{2})/([a-z-]+)\.json', path)
    if not match or match[2] not in ENDPOINTS:
        raise ValueError('Unexpected archive path: ' + path)
    day, name = match.groups()
    dt.date.fromisoformat(day)
    if len(body) > 100_000:
        raise ValueError('Archive file exceeds size limit')
    row = json.loads(body, object_pairs_hook=unique)
    if set(row) != ENVELOPE or row['archive_schema'] != 'dudelytics.public-derived.v1':
        raise ValueError('Unexpected archive envelope')
    if row['capture_date_utc'] != day or stamp(row['captured_at_utc'])[:10] != day:
        raise ValueError('Capture date mismatch')
    if row['source_url'] != ENDPOINTS[name]:
        raise ValueError('Unexpected public source')
    data = row['data']
    source = dict(data)
    if name == 'sectors':
        if set(data['sectors']) != set(SECTORS):
            raise ValueError('Unexpected sectors')
        source['sectors'] = {k: dict(v, timestamp=v['source_timestamp']) for k, v in data['sectors'].items()}
    elif name == 'benchmark-dpmi':
        source = {'methodology_version': data['benchmark_methodology_version'], 'latest': {
            'kind': 'observed', 'target_timestamp': data['target_timestamp'],
            'observed_at_utc': data['observed_at_utc'],
            'series': {'dpmi': dict(data, status='observed')}}}
        if data['index_id'] != 'DPMI' or data['target_timestamp'][:10] != day:
            raise ValueError('Unexpected benchmark')
    else:
        source['timestamp'] = data['source_timestamp']
    projected = project(name, source)
    if json.dumps(data, sort_keys=True, allow_nan=False) != json.dumps(projected, sort_keys=True, allow_nan=False):
        raise ValueError('Unexpected fields or values in public projection')
    return day, name

def collect():
    payloads, dates = {}, {}
    paths = git('ls-tree', '-r', '--name-only', 'HEAD', '--', 'data/').decode().splitlines()
    for path in paths:
        body = git('show', 'HEAD:' + path)
        day, name = validate(path, body)
        dates.setdefault(day, set()).add(name)
        payloads[path] = body
    if not dates or any(names != set(ENDPOINTS) for names in dates.values()):
        raise ValueError('Archive contains no complete captures or a partial capture')
    return payloads

def committed_card():
    path = 'HUGGINGFACE_DATASET_CARD.md'
    if path not in git('ls-tree', '-r', '--name-only', 'HEAD', '--', path).decode().splitlines():
        return None
    body = git('show', 'HEAD:' + path)
    if len(body) > 30_000:
        raise ValueError('Dataset card exceeds size limit')
    text = body.decode('utf-8')
    if not text.startswith('---\n') or '\nlicense: other\n' not in text or '\nlicense_link: https://dudelytics.com/lizenzen/\n' not in text:
        raise ValueError('Dataset card must retain the approved license')
    return body

def plan(payloads, remote_paths, read_remote):
    # A partial previous upload is repaired, but differing history is never overwritten.
    additions = []
    for path, body in payloads.items():
        if path in remote_paths:
            if read_remote(path) != body:
                raise ValueError('Historic snapshot differs; refusing overwrite: ' + path)
        else:
            additions.append((path, body))
    unexpected = {p for p in remote_paths if p.startswith('data/')} - set(payloads)
    if unexpected:
        raise ValueError('Hugging Face contains data absent from canonical archive')
    return additions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    payloads = collect()
    card = committed_card()
    revision = git('rev-parse', 'HEAD').decode().strip()
    if args.check_only:
        print(f'Validated {len(payloads)} committed public files at {revision}')
        return
    token = os.environ.get('HF_TOKEN')
    if not token:
        raise RuntimeError('Required GitHub Actions repository secret HF_TOKEN is missing')
    from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
    api = HfApi(token=token)
    api.auth_check(REPO, repo_type='dataset', write=True)
    info = api.repo_info(REPO, repo_type='dataset', revision='main')
    if info.private:
        raise ValueError('Expected an existing public dataset')
    remote_revision = info.sha
    remote_paths = api.list_repo_files(REPO, repo_type='dataset', revision=remote_revision)
    def read_remote(path, rev=remote_revision):
        return Path(hf_hub_download(REPO, path, repo_type='dataset', revision=rev, token=token)).read_bytes()
    additions = plan(payloads, remote_paths, read_remote)
    # Metadata is canonical GitHub content; dated snapshot bytes remain immutable.
    if card is not None:
        from huggingface_hub import DatasetCard
        metadata = DatasetCard(card.decode('utf-8')).data
        if metadata.get('license') != 'other' or {c['config_name'] for c in metadata.get('configs', [])} != set(ENDPOINTS):
            raise ValueError('Unexpected dataset card license or configurations')
        if 'README.md' not in remote_paths or read_remote('README.md') != card:
            additions.append(('README.md', card))
    if additions:
        commit = api.create_commit(REPO, repo_type='dataset', revision='main',
            parent_commit=remote_revision,
            operations=[CommitOperationAdd(path_in_repo=p, path_or_fileobj=b) for p, b in additions],
            commit_message='Mirror public derived archive ' + revision[:12],
            commit_description='Canonical source: https://github.com/' + REPO + '/commit/' + revision)
        remote_revision = commit.oid
        # Read every newly uploaded file at the resulting immutable revision.
        for path, body in additions:
            if read_remote(path, remote_revision) != body:
                raise RuntimeError('Post-upload verification failed: ' + path)
    print(f'Confirmed {len(payloads)} public files; added {len(additions)}; HF revision {remote_revision}; GitHub {revision}')

if __name__ == '__main__':
    main()
