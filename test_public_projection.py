import unittest
from pathlib import Path
from snapshot import project

class PublicProjectionTests(unittest.TestCase):
    def test_existing_snapshots_exclude_internal_metadata(self):
        for path in Path('data').glob('*/*.json'):
            body = path.read_text()
            for marker in ('historical_recomputed', 'recomputed_inputs', 'recovery_release', '"reconstruction"', '"backfill_notice"'):
                self.assertNotIn(marker, body, str(path))

    def test_index_projection_discards_internal_metadata(self):
        source = dict(index_id='DPMI', value=122.073434, timestamp='2026-11-04T15:10:00Z', methodology_version='DPMI-1.0', live_history_start='2026-08-17T16:06:32Z', kind='historical_recomputed', recovery={'interpolated': False}, reconstruction='exact_archived_prices', backfill_notice='internal')
        result = project('dpmi', source)
        self.assertEqual(result['value'], source['value'])
        self.assertEqual(result['source_timestamp'], source['timestamp'])
        self.assertEqual(set(result), {'index_id','value','source_timestamp','methodology_version','live_history_start'})

    def test_benchmark_without_internal_kind(self):
        own = dict(value=122.073434, status='observed', source_timestamp='2026-11-04T00:00:00Z', methodology_version='DPMI-1.0')
        row = dict(target_timestamp='2026-11-04T00:00:00Z', observed_at_utc='2026-11-04T00:02:00Z', series={'dpmi':own})
        source = dict(methodology_version='benchmark-1.0', latest=row)
        result = project('benchmark-dpmi', source)
        row['kind'] = 'observed'
        self.assertEqual(result, project('benchmark-dpmi', source))
        row['kind'] = 'invalid'
        with self.assertRaises(ValueError): project('benchmark-dpmi', source)
