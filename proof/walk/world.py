"""Deterministic map authority: routes, perception, ownership and entrance."""
import copy
import hashlib
import heapq
import json
import math
from pathlib import Path

from proof.m2.world import Rejected, InvalidSnapshot, canonical

MAP_FILE = Path(__file__).with_name('map.json')
SCHEMA = 'm2-walk-save-1'
VECTORS = ((0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1))
STEP_MS = 300


class WalkWorld:
    def __init__(self):
        self.map = json.loads(MAP_FILE.read_text(encoding='utf-8'))
        self.map_hash = hashlib.sha256(canonical(self.map).encode()).hexdigest()
        self.objects = {o['id']: o for o in self.map['objects']}
        self.s = dict(schema=SCHEMA, map_hash=self.map_hash, tick_ms=0, pos=list(self.map['start']),
                      facing=2, path=[], progress_ms=0, steps=0, pending=None, door_open=False,
                      key_owner='ground', inspected=[], seen=[], inventory=[], complete=False,
                      log=[{'tick_ms':0,'text':self.map['intro']}], history=[])
        self.observe()

    def blocked(self, opaque=False):
        result = {tuple(p) for p in self.map['walls']}
        for o in self.objects.values():
            if o['id']=='door' and self.s['door_open']: continue
            if o['opaque' if opaque else 'solid']:
                result.update(tuple(p) for p in o['cells'])
        return result

    def inside(self, cell):
        return 1 <= cell[0] < self.map['width']-1 and 1 <= cell[1] < self.map['height']-1

    def free(self, cell):
        return self.inside(cell) and tuple(cell) not in self.blocked()

    def neighbors(self, cell):
        x,y = cell
        for dx,dy in VECTORS:
            nxt = (x+dx,y+dy)
            if self.free(nxt) and (not (dx and dy) or (self.free((x+dx,y)) and self.free((x,y+dy)))):
                yield nxt, 14 if dx and dy else 10

    def route(self, start, goal):
        start,goal = tuple(start),tuple(goal)
        if not self.free(goal): raise Rejected('Ese lugar está ocupado. Elegí suelo libre.')
        if start==goal: return []
        def heuristic(p):
            dx,dy=abs(p[0]-goal[0]),abs(p[1]-goal[1])
            return 14*min(dx,dy)+10*abs(dx-dy)
        heap=[(heuristic(start),0,start)];cost={start:0};prior={}
        while heap:
            _,g,cell=heapq.heappop(heap)
            if g!=cost[cell]: continue
            if cell==goal:
                route=[]
                while cell!=start: route.append(list(cell));cell=prior[cell]
                return route[::-1]
            for nxt,charge in self.neighbors(cell):
                candidate=g+charge
                if candidate < cost.get(nxt,10**9):
                    cost[nxt]=candidate;prior[nxt]=cell
                    heapq.heappush(heap,(candidate+heuristic(nxt),candidate,nxt))
        raise Rejected('No encontrás un camino hasta ese lugar.')

    def visible(self, obj):
        if obj['id']=='key' and self.s['key_owner']!='ground': return False
        px,py=self.s['pos'];x,y=obj['pos']
        if math.hypot(x-px,y-py)>7: return False
        # Small-map discrete center ray, not a general lighting/stealth system.
        target_cells={tuple(c) for c in obj['cells']};opaque=self.blocked(True)
        count=max(1,int(max(abs(x-px),abs(y-py))*8))
        for i in range(1,count):
            t=i/count;cell=(math.floor(px+(x-px)*t+.5),math.floor(py+(y-py)*t+.5))
            if cell in opaque and cell not in target_cells: return False
        return True

    def note(self, text):
        self.s['log'].append({'tick_ms':self.s['tick_ms'],'text':text})

    def observe(self):
        for o in self.objects.values():
            if o['id'] not in self.s['seen'] and self.visible(o):
                self.s['seen'].append(o['id']);self.note(o['brief'])

    def touch(self, obj, cell=None):
        p=cell or self.s['pos']
        for x,y in obj['cells'] or [obj['pos']]:
            if max(abs(x-p[0]),abs(y-p[1]))>1.01: continue
            dx,dy=x-p[0],y-p[1]
            if abs(dx)>=.99 and abs(dy)>=.99:
                if not (self.free((p[0]+int(dx),p[1])) and self.free((p[0],p[1]+int(dy)))): continue
            return True
        return False

    def approach(self, obj):
        if self.touch(obj): return []
        routes=[]
        x,y=obj['pos']
        for cy in range(math.floor(y)-1,math.ceil(y)+2):
            for cx in range(math.floor(x)-1,math.ceil(x)+2):
                if self.free((cx,cy)) and self.touch(obj,(cx,cy)):
                    try:
                        route=self.route(self.s['pos'],(cx,cy))
                        cost=sum(14 if a[0]!=b[0] and a[1]!=b[1] else 10 for a,b in zip([self.s['pos']]+route,route))
                        routes.append((cost,cy,cx,route))
                    except Rejected: pass
        if not routes: raise Rejected('No podés acercarte a ese objeto desde aquí.')
        return min(routes)[3]

    def interact(self, target):
        obj=self.objects[target]
        if not self.touch(obj): raise Rejected('Necesitás acercarte para hacer eso.')
        if target=='key':
            if self.s['key_owner']!='ground': raise Rejected('Ya llevás esa llave.')
            self.s['key_owner']='player';self.s['inventory']=['key']
            self.note('Recogés la llave de bronce. Ahora está en tu inventario; buscá la puerta del refugio.')
        elif target=='door':
            if 'key' not in self.s['inventory']:
                self.note('La puerta está cerrada. Necesitás tu llave. Buscala junto al contenedor.')
                return
            if not self.s['door_open']:
                self.s['door_open']=True;self.note('La llave gira. Abrís la puerta del refugio.')
            self.s['path']=self.route(self.s['pos'],self.map['entry'])
            self.s['progress_ms']=0
            if not self.s['path']: self.finish()
        elif target=='contact':
            self.note('La mujer baja el cigarrillo: «La llave quedó junto al contenedor. Yo no me quedaría afuera mucho más».')
        else:
            self.note('El contenedor no se mueve. Podés rodearlo y examinar lo que hay a su lado.')

    def finish(self):
        if self.s['pos']==self.map['entry'] and self.s['door_open'] and not self.s['complete']:
            self.s['complete']=True
            self.note('Entrás al refugio. Recorrido completo: caminaste, observaste, recogiste y utilizaste un objeto del mundo.')

    def _apply(self, kind, payload):
        if kind=='move':
            p=payload.get('cell')
            if not isinstance(p,list) or len(p)!=2 or any(type(v) is not int for v in p): raise Rejected('Destino inválido.')
            route=self.route(self.s['pos'],p)
            self.s.update(path=route,progress_ms=0,pending=None)
        elif kind in ('inspect','use'):
            target=payload.get('target');obj=self.objects.get(target)
            if obj is None or not self.visible(obj): raise Rejected('Tu personaje no puede ver eso desde aquí.')
            if kind=='inspect':
                self.note(obj['description']);self.s['inspected']=sorted(set(self.s['inspected']+[target]))
            else:
                self.s.update(path=self.approach(obj),progress_ms=0,pending=target)
                if self.s['path']:
                    self.note('Te acercás a '+obj['name'].lower()+'.')
                else:
                    self.s['pending']=None;self.interact(target)
        elif kind=='advance':
            elapsed=payload.get('ms')
            if type(elapsed) is not int or not 0<=elapsed<=2000: raise Rejected('Avance inválido.')
            if self.s['tick_ms']+elapsed>1800000: raise Rejected('La muestra alcanzó su límite de tiempo. Guardá o reiniciá.')
            remaining=elapsed
            while remaining>0:
                if not self.s['path']:
                    self.s['tick_ms']+=remaining;remaining=0;break
                need=STEP_MS-self.s['progress_ms'];delta=min(remaining,need)
                self.s['tick_ms']+=delta;remaining-=delta;self.s['progress_ms']+=delta
                if self.s['progress_ms']>=STEP_MS:
                    nxt=self.s['path'].pop(0);dx=nxt[0]-self.s['pos'][0];dy=nxt[1]-self.s['pos'][1]
                    if not any(list(c)==nxt for c,_ in self.neighbors(self.s['pos'])): raise Rejected('El camino quedó bloqueado.')
                    self.s.update(pos=nxt,facing=VECTORS.index((dx,dy)),progress_ms=0,steps=self.s['steps']+1)
                    self.observe();self.finish()
                    if not self.s['path'] and self.s['pending']:
                        target=self.s['pending'];self.s['pending']=None;self.interact(target)
        else: raise Rejected('Acción desconocida.')

    def command(self, kind, payload):
        before=copy.deepcopy(self.s)
        try:
            if not isinstance(payload,dict): raise Rejected('Acción inválida.')
            allowed={'move':{'cell'},'inspect':{'target'},'use':{'target'},'advance':{'ms'}}
            if kind not in allowed or set(payload)!=allowed[kind]: raise Rejected('Acción inválida.')
            self._apply(kind,payload)
            self.s['history'].append({'kind':kind,'payload':copy.deepcopy(payload)})
            if len(self.s['history'])>4096: raise Rejected('Esta partida de ensayo es demasiado larga. Reiniciá.')
            self.validate_current()
        except Exception:
            self.s=before;raise

    def validate_current(self):
        if not self.free(self.s['pos']): raise InvalidSnapshot('POSITION_BLOCKED')
        position=self.s['pos']
        for nxt in self.s['path']:
            if not any(list(c)==nxt for c,_ in self.neighbors(position)): raise InvalidSnapshot('INVALID_PATH')
            position=nxt
        if self.s['inventory'] != (['key'] if self.s['key_owner']=='player' else []): raise InvalidSnapshot('ITEM_OWNERSHIP')
        if self.s['door_open'] and 'key' not in self.s['inventory']: raise InvalidSnapshot('DOOR_WITHOUT_KEY')
        if self.s['complete'] and not self.s['door_open']: raise InvalidSnapshot('INVALID_COMPLETION')
        if not 0<=self.s['progress_ms']<STEP_MS or (not self.s['path'] and self.s['progress_ms']): raise InvalidSnapshot('INVALID_PROGRESS')

    def snapshot(self): return canonical(self.s)

    def load(self, text):
        def unique(pairs):
            obj={}
            for key,value in pairs:
                if key in obj: raise InvalidSnapshot('DUPLICATE_KEY')
                obj[key]=value
            return obj
        try:
            data=json.loads(text,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(InvalidSnapshot('NONFINITE')))
            if data['schema']!=SCHEMA or data['map_hash']!=self.map_hash: raise InvalidSnapshot('INCOMPATIBLE_MAP_OR_VERSION')
            if not isinstance(data['history'],list) or len(data['history'])>4096: raise InvalidSnapshot('INVALID_HISTORY')
            replay=WalkWorld()
            for row in data['history']:
                if set(row)!={'kind','payload'}: raise InvalidSnapshot('INVALID_INPUT')
                replay.command(row['kind'],row['payload'])
            if canonical(replay.s)!=canonical(data): raise InvalidSnapshot('STATE_HISTORY_MISMATCH')
        except (ValueError,TypeError,KeyError,Rejected) as exc:
            raise InvalidSnapshot(str(exc)) from exc
        self.s=replay.s

    def view(self):
        return dict(tick_ms=self.s['tick_ms'],pos=self.s['pos'][:],facing=self.s['facing'],path=copy.deepcopy(self.s['path']),
                    progress_ms=self.s['progress_ms'],step_ms=STEP_MS,steps=self.s['steps'],pending=self.s['pending'],
                    door_open=self.s['door_open'],complete=self.s['complete'],
                    inventory=[{'id':'key','name':'Llave de bronce','asset':'key'}] if self.s['inventory'] else [],
                    objects=[dict(id=o['id'],name=o['name'],pos=o['pos'],asset=o['asset']) for o in self.objects.values() if self.visible(o)],
                    log=copy.deepcopy(self.s['log']),
                    map={k:copy.deepcopy(self.map[k]) for k in ('id','width','height','walls','entry')},
                    solids=[list(p) for p in sorted(self.blocked())],objective='Entrá al refugio' if not self.s['complete'] else 'Recorrido completado')
