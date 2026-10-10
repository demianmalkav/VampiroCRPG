"""Revision/receipt adapter. Presentation never authors world state."""
import copy
import uuid
from proof.m2.world import Rejected, canonical
from .world import WalkWorld


class Session:
    def __init__(self):
        self.world=WalkWorld();self.revision=uuid.uuid4().hex;self.receipts={}

    def view(self):
        return dict(self.world.view(),revision=self.revision)

    def save(self): return self.world.snapshot()

    def mutate(self, request):
        if not isinstance(request,dict) or set(request)-{'revision','request_id','action','payload','snapshot'}: raise Rejected('Solicitud inválida.')
        rid=request.get('request_id')
        if not isinstance(rid,str) or not 1<=len(rid)<=80: raise Rejected('Solicitud inválida.')
        identity=canonical(request)
        if rid in self.receipts:
            previous=self.receipts[rid]
            if previous['identity']!=identity: raise Rejected('Solicitud repetida con otra acción.')
            return copy.deepcopy(previous['response'])
        if request.get('revision')!=self.revision: raise Rejected('STALE_VIEW')
        candidate=copy.deepcopy(self.world);action=request.get('action')
        if action=='reset': candidate=WalkWorld()
        elif action=='load': candidate.load(request.get('snapshot'))
        else: candidate.command(action,request.get('payload',{}))
        self.world=candidate;self.revision=uuid.uuid4().hex
        response=self.view();self.receipts[rid]=dict(identity=identity,response=copy.deepcopy(response))
        if len(self.receipts)>256: del self.receipts[next(iter(self.receipts))]
        return response
