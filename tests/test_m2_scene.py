"""Presentation boundary tests against the real A/B command owners."""
import copy
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from proof.m2.world import InvalidSnapshot, Rejected
from proof.scene.session import Session
from proof.scene.__main__ import make_server


class SceneTests(unittest.TestCase):
    def act(self, session, action, **extra):
        return session.mutate(dict(revision=session.revision, request_id=str(len(session.receipts)) + session.revision, action=action, **extra))

    def test_view_and_action_probes_do_not_mutate_authority(self):
        s = Session('pressure')
        before = s.world.snapshot()
        for _ in range(3):
            view = s.view()
            self.assertIn('feed', [a['id'] for a in view['actions']])
        self.assertEqual(s.world.snapshot(), before)
        self.assertNotIn('lucid_retreat', [a['id'] for a in view['actions']])

    def test_real_lucid_choice_differs_from_uninterrupted_feeding(self):
        safe, lethal = Session('pressure'), Session('pressure')
        for s in (safe, lethal):
            self.act(s, 'feed'); self.act(s, 'advance')
            self.assertEqual(s.world.s['tick'], 3)
            self.assertEqual(s.world.actor['governance'], 'BEAST')
        self.act(safe, 'lucid_retreat')
        for _ in range(4): self.act(safe, 'advance')
        for _ in range(5): self.act(lethal, 'advance')
        self.assertEqual((safe.world.vampire['willpower_current'], safe.world.actor['governance']), (4, 'NORMAL'))
        self.assertEqual(safe.world.s['actors']['actor:M0']['condition'], 'medical_emergency')
        self.assertEqual(lethal.world.s['actors']['actor:M0']['condition'], 'dead')
        self.assertEqual(lethal.world.vampire['humanity'], 6)
        self.assertEqual(safe.world.vampire['humanity'], 7)
        self.assertEqual(sum(e['type']=='WillpowerSpent' for e in safe.world.s['events'].values()), 1)
        self.assertTrue(any('Perdés un punto' in row['text'] for row in lethal.view()['log']))

    def test_mid_action_save_load_preserves_future_and_cost(self):
        s = Session('pressure')
        for action in ('feed', 'advance', 'lucid_retreat'): self.act(s, action)
        saved = s.save()
        restored = Session('control')
        self.act(restored, 'load', snapshot=saved)
        self.assertEqual(restored.mode, 'pressure')
        self.assertEqual(restored.world.snapshot(), s.world.snapshot())
        for action in ('advance', 'advance', 'advance', 'advance'):
            self.act(s, action); self.act(restored, action)
        self.assertEqual(restored.world.snapshot(), s.world.snapshot())
        self.assertEqual(restored.world.vampire['willpower_current'], 4)

    def test_duplicate_paid_request_and_stale_view(self):
        s = Session('pressure')
        self.act(s, 'feed'); self.act(s, 'advance')
        request = dict(revision=s.revision, request_id='payment', action='lucid_retreat')
        first = s.mutate(request); before = s.world.snapshot()
        self.assertEqual(s.mutate(request), first)
        self.assertEqual(s.world.snapshot(), before)
        with self.assertRaisesRegex(Rejected, 'REQUEST_ID_COLLISION'):
            s.mutate(dict(request, action='lucid_wait'))
        with self.assertRaisesRegex(Rejected, 'STALE_VIEW'):
            s.mutate(dict(request, request_id='stale'))
        self.assertEqual(s.world.snapshot(), before)

    def test_forged_save_and_forbidden_commands_leave_session_intact(self):
        s = Session('pressure'); self.act(s, 'feed'); self.act(s, 'advance')
        before = s.world.snapshot(); revision = s.revision
        data = json.loads(s.save()); data['world']['actors']['actor:V0']['vampire']['willpower_current'] = 99
        with self.assertRaises(InvalidSnapshot): self.act(s, 'load', snapshot=json.dumps(data))
        for action in ('SeedMoralFacts', 'retreat', 'minute'):
            with self.assertRaises(Rejected): self.act(s, action)
        self.assertEqual(s.world.snapshot(), before)
        self.assertEqual(s.revision, revision)
        with self.assertRaises(InvalidSnapshot):
            self.act(s, 'load', snapshot='{"format":"a","format":"b","mode":"control","world":{}}')
        self.assertEqual(s.world.snapshot(), before)

    def test_player_projection_hides_rng_offscreen_actors_and_institution(self):
        s = Session('pressure')
        self.act(s, 'feed'); self.act(s, 'advance')
        view = s.view()
        self.assertEqual(next(a for a in view['visible'] if a['id']=='actor:M0')['condition'], 'medical_emergency')
        encoded = json.dumps(view)
        for private in ('seed_hex','counter_before','dice','blood_current','record:REC','review_support','process:CASE','actor:I1','actor:W2','actor:G1'):
            self.assertNotIn(private, encoded)
        self.act(s, 'lucid_retreat'); self.act(s, 'advance')
        view = s.view()
        self.assertNotIn('actor:M0', [a['id'] for a in view['visible']])
        self.assertFalse(view['camera_visible'])
        self.assertTrue(any('emergencia médica' in r['text'] for r in view['log']))
        self.assertIn('rng', json.loads(s.save())['world'])  # Private save is explicit.

    def test_daytime_world_and_acquired_inquiry_without_omniscience(self):
        s = Session()
        for action in ('feed','advance','seal','advance','cleanup','retreat','advance','sleep'):
            self.act(s, action)
        self.assertEqual(s.world.actor['availability'], 'asleep')
        self.act(s, 'wake')
        view = s.view()
        self.assertEqual(view['location'], 'location:L_HAV')
        self.assertNotIn('record:REC_COPY', json.dumps(view))
        self.assertIn('record:REC_COPY', s.world.s['records'])
        self.assertFalse(any('Observaste una visita' in row['text'] for row in view['log']))
        self.assertTrue(any('Tu contacto informa' in row['text'] for row in view['log']))
        self.act(s, 'return'); self.act(s, 'advance'); self.act(s, 'minute')
        view = s.view()
        self.assertEqual(view['tick'], 86460)
        self.assertIn('actor:I1', [a['id'] for a in view['visible']])
        self.assertTrue(any('pregunta por tu alias' in row['text'] for row in view['log']))
        self.assertEqual(view['actions'], [])
        with self.assertRaisesRegex(Rejected, 'SCENE_TIME_LIMIT'): self.act(s, 'advance')

    def test_reset_is_explicit_and_no_hidden_scenario_decisions(self):
        s = Session('pressure')
        self.assertEqual(len(s.world.s['inputs']), 1)
        self.assertIsNone(s.world.feeding())
        self.act(s, 'feed'); self.act(s, 'advance')
        self.act(s, 'reset', mode='control')
        self.assertEqual(s.world.s['tick'], 0)
        self.assertEqual(s.world.actor['governance'], 'NORMAL')
        self.assertEqual(s.world.vampire['willpower_current'], 5)
        self.assertNotIn('message:DIRECTIVE', s.world.s['messages'])

    def test_http_get_post_save_origin_and_malformed_boundaries(self):
        server = make_server(0)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base+'/') as response:
                self.assertIn(b'<canvas', response.read())
            with urlopen(base+'/api/view') as response:
                view = json.load(response)
            row = dict(revision=view['revision'], request_id='http-feed', action='feed')
            request = Request(base+'/api/action', data=json.dumps(row).encode(), headers={'Content-Type':'application/json'})
            with urlopen(request) as response: result = json.load(response)
            self.assertEqual(result['governance'], 'RESISTING')
            with urlopen(request) as response: self.assertEqual(json.load(response), result)
            before = server.scene_session.world.snapshot()
            with urlopen(base+'/api/save') as response:
                self.assertIn('attachment', response.headers['Content-Disposition'])
                self.assertEqual(json.load(response)['world'], json.loads(before))
            rejected = Request(base+'/api/action', data=json.dumps(row).encode(), headers={'Content-Type':'application/json', 'Origin':'http://foreign.invalid'})
            with self.assertRaises(HTTPError) as exc: urlopen(rejected)
            self.assertEqual(exc.exception.code, 403); exc.exception.close()
            bad = Request(base+'/api/action', data=b'[]', headers={'Content-Type':'application/json'})
            with self.assertRaises(HTTPError) as exc: urlopen(bad)
            self.assertEqual(exc.exception.code, 409); exc.exception.close()
            bad = Request(base+'/api/action', data=b'{"action":"feed","action":"load"}', headers={'Content-Type':'application/json'})
            with self.assertRaises(HTTPError) as exc: urlopen(bad)
            self.assertEqual(exc.exception.code, 409); exc.exception.close()
            hostile = Request(base+'/api/view', headers={'Host':'foreign.invalid'})
            with self.assertRaises(HTTPError) as exc: urlopen(hostile)
            self.assertEqual(exc.exception.code, 403); exc.exception.close()
            self.assertEqual(server.scene_session.world.snapshot(), before)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)


if __name__ == '__main__': unittest.main()
