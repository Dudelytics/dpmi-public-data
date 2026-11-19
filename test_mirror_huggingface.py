"""Offline checks against the real committed public archive."""
import copy
import json
import unittest
from mirror_huggingface import collect, plan, validate

class MirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = collect()

    def test_existing_archive_is_noop(self):
        self.assertEqual(plan(self.payloads, set(self.payloads), self.payloads.__getitem__), [])

    def test_missing_file_is_added_unchanged(self):
        path = sorted(self.payloads)[0]
        remote = dict(self.payloads)
        del remote[path]
        self.assertEqual(plan(self.payloads, remote, remote.__getitem__), [(path, self.payloads[path])])

    def test_different_history_blocks_entire_plan(self):
        remote = dict(self.payloads)
        remote[sorted(remote)[0]] += b' '
        with self.assertRaises(ValueError):
            plan(self.payloads, remote, remote.__getitem__)

    def test_extra_remote_data_blocks(self):
        with self.assertRaises(ValueError):
            plan(self.payloads, set(self.payloads) | {'data/secret.json'}, self.payloads.__getitem__)

    def test_raw_fields_block_at_every_level(self):
        path = 'data/2026-10-03/sectors.json'
        row = json.loads(self.payloads[path])
        for location in ((), ('data',), ('data', 'sectors', 'defi')):
            injected = copy.deepcopy(row)
            target = injected
            for key in location:
                target = target[key]
            target['market_cap'] = 123456
            with self.assertRaises(ValueError):
                validate(path, json.dumps(injected).encode())

    def test_partial_capture_blocks(self):
        import mirror_huggingface as module
        from unittest.mock import patch
        original = module.git
        def incomplete(*args):
            if args[0] == 'ls-tree':
                return '\n'.join(sorted(self.payloads)[1:]).encode()
            return original(*args)
        with patch.object(module, 'git', incomplete), self.assertRaises(ValueError):
            collect()

    def test_old_and_extended_dvix_diagnosis(self):
        path = 'data/2026-10-03/dvix.json'
        row = json.loads(self.payloads[path])
        validate(path, json.dumps(row).encode())
        for status, fresh, reason in [('live', True, None), ('recovery_window', False, 'observed_hourly_anchor_missing'), ('stale', False, 'source_timestamp_stale'), ('live', None, None)]:
            new = copy.deepcopy(row)
            new['data'].update(status=status, freshness={'fresh': fresh, 'reason': reason})
            validate(path, json.dumps(new).encode())
            new['data']['freshness']['api_key'] = 'forbidden'
            with self.assertRaises(ValueError):
                validate(path, json.dumps(new).encode())

    def test_late_export_requires_evidence_from_target_day(self):
        path = 'data/2026-11-18/dpmi.json'
        row = json.loads(self.payloads['data/2026-11-19/dpmi.json'])
        row['capture_date_utc'] = '2026-11-18'
        row['data']['source_timestamp'] = '2026-11-18T07:47:13Z'
        self.assertEqual(validate(path, json.dumps(row).encode()), ('2026-11-18', 'dpmi'))
        row['data']['source_timestamp'] = '2026-11-19T07:47:13Z'
        with self.assertRaisesRegex(ValueError, 'Late export source date mismatch'):
            validate(path, json.dumps(row).encode())
        row['captured_at_utc'] = '2026-11-17T12:00:00Z'
        with self.assertRaisesRegex(ValueError, 'Capture date mismatch'):
            validate(path, json.dumps(row).encode())

    def test_contradictory_dvix_diagnosis_rejected(self):
        path = 'data/2026-10-03/dvix.json'
        row = json.loads(self.payloads[path])
        row['data'].update(status='stale', freshness={'fresh': True, 'reason': None})
        with self.assertRaises(ValueError):
            validate(path, json.dumps(row).encode())

if __name__ == '__main__':
    unittest.main()
