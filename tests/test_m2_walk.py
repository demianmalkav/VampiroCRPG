import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from proof.m2.world import Rejected, InvalidSnapshot
from proof.walk.world import WalkWorld
from proof.walk.session import Session
from proof.walk.__main__ import make_server


def finish_route(w):
    while w.s['path']: w.command('advance', {'ms':2000})


def reach_key(w):
    w.command('move', {'cell':[7,6]});finish_route(w)
    w.command('use', {'target':'key'});finish_route(w)


class WalkTests(unittest.TestCase):
    def test_route_respects_solids_and_diagonal_corners(self):
        w=WalkWorld();route=w.route(w.s['pos'],[7,5]);p=w.s['pos']
        self.assertEqual(route,w.route(p,[7,5]))
        for nxt in route:
            self.assertNotIn(tuple(nxt),w.blocked())
            self.assertIn(tuple(nxt),[c for c,_ in w.neighbors(p)])
            p=nxt
        self.assertEqual(route[-1],[7,5])

    def test_hidden_key_not_in_view_or_actionable(self):
        w=WalkWorld();before=w.snapshot()
        self.assertNotIn('key',[o['id'] for o in w.view()['objects']])
        with self.assertRaises(Rejected):w.command('use',{'target':'key'})
        self.assertEqual(before,w.snapshot())
        w.command('move',{'cell':[7,6]});finish_route(w)
        self.assertIn('key',[o['id'] for o in w.view()['objects']])

    def test_inspection_does_not_teleport_or_acquire(self):
        w=WalkWorld();w.command('inspect',{'target':'contact'})
        self.assertEqual(w.s['pos'],[3,10]);self.assertEqual(w.s['inventory'],[])
        self.assertIn('botas gastadas',w.s['log'][-1]['text'])

    def test_autoapproach_can_be_cancelled(self):
        w=WalkWorld();w.command('use',{'target':'contact'})
        self.assertTrue(w.s['path']);self.assertEqual(w.s['pending'],'contact')
        w.command('advance',{'ms':120});w.command('move',{'cell':w.s['pos'][:]})
        self.assertEqual(w.s['pending'],None);self.assertEqual(w.s['progress_ms'],0)
        self.assertEqual(w.s['path'],[])

    def test_key_owned_once_and_removed_from_ground(self):
        w=WalkWorld();reach_key(w)
        self.assertEqual(w.s['inventory'],['key']);self.assertEqual(w.s['key_owner'],'player')
        self.assertNotIn('key',[o['id'] for o in w.view()['objects']])
        before=w.snapshot()
        with self.assertRaises(Rejected):w.command('use',{'target':'key'})
        self.assertEqual(before,w.snapshot())

    def test_door_locked_without_key(self):
        w=WalkWorld();w.command('move',{'cell':[10,8]});finish_route(w)
        w.command('use',{'target':'door'});finish_route(w)
        self.assertFalse(w.s['door_open']);self.assertFalse(w.s['complete'])
        self.assertIn('cerrada',w.s['log'][-1]['text'])

    def test_unlock_is_not_completion_until_entry(self):
        w=WalkWorld();reach_key(w);w.command('move',{'cell':[10,8]});finish_route(w)
        w.command('use',{'target':'door'})
        while not w.s['door_open']:w.command('advance',{'ms':300})
        self.assertFalse(w.s['complete']);self.assertTrue(w.s['path'])
        finish_route(w);self.assertEqual(w.s['pos'],w.map['entry']);self.assertTrue(w.s['complete'])

    def test_save_mid_approach_replays_and_continues_identically(self):
        w=WalkWorld();w.command('use',{'target':'contact'});w.command('advance',{'ms':175})
        v=WalkWorld();v.load(w.snapshot());self.assertEqual(w.snapshot(),v.snapshot())
        finish_route(w);finish_route(v);self.assertEqual(w.snapshot(),v.snapshot())
        self.assertIn('La mujer baja',w.s['log'][-1]['text'])

    def test_forged_save_rejected_without_changes(self):
        w=WalkWorld();data=json.loads(w.snapshot());data['inventory']=['key'];data['key_owner']='player'
        before=w.snapshot()
        with self.assertRaises(InvalidSnapshot):w.load(json.dumps(data))
        self.assertEqual(before,w.snapshot())
        for text in ['{"schema":1,"schema":2}', '{"tick_ms":NaN}']:
            with self.assertRaises(InvalidSnapshot):w.load(text)
            self.assertEqual(before,w.snapshot())

    def test_invalid_move_rolls_back(self):
        w=WalkWorld();before=w.snapshot()
        for cell in [[5,5],[0,0],[True,4],[100,100]]:
            with self.assertRaises(Rejected):w.command('move',{'cell':cell})
            self.assertEqual(before,w.snapshot())

    def test_revision_and_retry_do_not_duplicate(self):
        s=Session();req={'revision':s.revision,'request_id':'a','action':'inspect','payload':{'target':'contact'}}
        one=s.mutate(req);two=s.mutate(req);self.assertEqual(one,two)
        self.assertEqual(len(s.world.s['history']),1)
        with self.assertRaises(Rejected):s.mutate(dict(req,request_id='b'))
        with self.assertRaises(Rejected):s.mutate(dict(req,action='reset'))

    def test_http_assets_origin_and_rejected_command(self):
        server=make_server(0);threading.Thread(target=server.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(url+'/art/index.json') as r:self.assertIn('player',json.load(r)['assets'])
            with urlopen(url+'/art/player.png') as r:self.assertEqual(r.read(8),b'\x89PNG\r\n\x1a\n')
            with self.assertRaises(HTTPError) as error:urlopen(Request(url+'/api/view',headers={'Origin':'https://other.example'}))
            self.assertEqual(error.exception.code,403)
            with self.assertRaises(HTTPError) as error:urlopen(url+'/art/../source/style.json')
            self.assertEqual(error.exception.code,404)
            before=server.walk_session.save()
            req=Request(url+'/api/command',data=b'{"action":NaN}',headers={'Content-Type':'application/json'})
            with self.assertRaises(HTTPError):urlopen(req)
            self.assertEqual(before,server.walk_session.save())
        finally:server.shutdown();server.server_close()


if __name__=='__main__':unittest.main()
