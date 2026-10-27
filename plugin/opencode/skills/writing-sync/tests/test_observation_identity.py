"""Read-back must not hide duplicate IDs behind metadata filtering."""
from types import SimpleNamespace
from unittest import TestCase
from copy import deepcopy
from drive_sync.original_effects import OriginalEffects
from drive_sync.native_effects import NativeEffects
from drive_sync.executor import Prepared, reconcile
from drive_sync.state import Intent
from drive_sync.google import DOC


class ObservationIdentityTests(TestCase):
    def test_unverified_identity_and_layout_have_precise_pending_results(self):
        for storage, effects_type in [('original', OriginalEffects), ('google-doc', NativeEffects)]:
            good = dict(id='new-object', name='c.html', parents=['folder'],
                        mimeType=DOC if storage == 'google-doc' else 'text/html',
                        appProperties={'source': 'source'})
            bad_name = deepcopy(good)
            bad_name['name'] = 'c'
            bad_source = deepcopy(good)
            bad_source['appProperties']['source'] = 'other'
            wrong_type = deepcopy(good)
            wrong_type['mimeType'] = 'text/html' if storage == 'google-doc' else DOC
            for items, expected in [([], 'creation_not_found'), ([good, bad_name], 'ambiguous_identity'),
                                    ([bad_name], 'remote_layout_mismatch'), ([bad_source], 'remote_identity_mismatch'),
                                    ([wrong_type], 'remote_storage_mismatch')]:
                with self.subTest(storage=storage, expected=expected):
                    remote = SimpleNamespace(inventory=lambda operation_id: items)
                    effects = effects_type(SimpleNamespace(files=[]), (), None, remote, lambda: '')
                    intent = Intent('operation', 'source', 'create', None, 'desired', 'old-object')
                    prepared = Prepared('source', None, 'desired', b'', dict(storage=storage,
                        name='c.html', parent='folder', path='/synthetic/c.html', remote_id='old-object'))
                    # Store intentionally has no methods: failed observations cannot advance state.
                    result = reconcile(object(), effects, intent, prepared)
                    self.assertEqual(result.status, 'pending')
                    self.assertEqual(result.reason, expected)
                    if len(items) == 1:
                        self.assertEqual(result.destination, 'new-object')
                        self.assertNotEqual(result.destination, 'old-object')
