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

if __name__ == '__main__':
    unittest.main()
