"""Deterministic transactional world. No renderer, wall clock or outcome fixtures.

The micro-procedures here are deliberately finite. They demonstrate causality,
not unrestricted NPC planning or canonical Vampire rules.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Callable


SCHEMA = "m2-proof-json-1"
CONTRACT = "m2-a-0.2"
RUNTIME = "m2-python-proof-1"
PROFILE = "m2-a-proof-profile-1"
STORES = (
    "actors", "locations", "personas", "institutions", "devices", "grants",
    "events", "observations", "propositions", "beliefs", "memories",
    "relationships", "records", "messages", "processes", "receipts",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


class Rejected(Exception):
    pass


class InvalidSnapshot(ValueError):
    pass


class WorkLimit(RuntimeError):
    pass


class World:
    def __init__(self, fixture):
        # Only initial conditions/profiles enter the runtime. Expected outputs
        # remain exclusively in the runner, never in the authority of the world.
        w = copy.deepcopy(fixture["world"])
        if fixture["fixture_version"] != PROFILE:
            raise Rejected("INCOMPATIBLE_PROFILE")
        self.s = {name: {} for name in STORES}
        self.s.update(schema=SCHEMA, contract=CONTRACT, runtime=RUNTIME,
                      profile_version=fixture["fixture_version"], tick=w["initial_tick"],
                      allocator=0, enqueue_seq=0, handlers_this_tick=0, input_cursor=0,
                      inputs=[], queue=[], rng={"algorithm": "unused-in-A", "seed": fixture["seed"], "draws": 0},
                      config={"case_id": fixture.get("case_id"), "routes": w["routes"], "channels": w["known_channels"],
                              "profile": copy.deepcopy(fixture["scenario_profile"]),
                              "relation": w["relationship_profile"],
                              "max_handlers_per_tick": w["max_handlers_per_tick"]})
        self.presentation = {}  # Disposable, not a domain snapshot field.
        self.extra_handlers: dict[str, Callable] = {}
        for loc in w["locations"]:
            self.put("locations", {"id": loc, "refs": []})
        for a in w["actors"]:
            a.update(refs=[a["location"]], reservation=a.get("initial_reservation", 0), travelling=False)
            self.put("actors", a)
        for store, key in [("personas", "persona"), ("institutions", "institution"),
                           ("devices", "device"), ("grants", "grant")]:
            obj = w[key]
            obj["refs"] = [obj[k] for k in ("owner", "location", "storage", "custodian", "issuer", "holder") if k in obj]
            if store == "institutions":
                obj.update(records=[], cases=[])
            self.put(store, obj)
        self.event("WorldInitialized", "institution:P1")
        # Finite authored policies create attempts, never unconditional results.
        for kind, tick in [("CopyAttempt", self.profile["copy_tick"]),
                           ("ReviewAttempt", self.profile["review_tick"]),
                           ("PlanVisitAttempt", self.profile["visit_planning_tick"])]:
            self.schedule(kind, tick, {}, "institution:P1", [])
        self.validate(self.s)

    @property
    def profile(self):
        return self.s["config"]["profile"]

    def get(self, store, key):
        try:
            return self.s[store][key]
        except KeyError as exc:
            raise Rejected("MISSING_ID:" + key) from exc

    def put(self, store, obj):
        if obj["id"] in self.s[store]:
            raise Rejected("DUPLICATE_ID:" + obj["id"])
        self.s[store][obj["id"]] = obj
        return obj

    def alloc(self, family):
        self.s["allocator"] += 1
        return f"{family}:{self.s['allocator']}"

    def event(self, kind, source, targets=(), causes=(), payload=None):
        obj = {"id": self.alloc("event"), "type": kind, "tick": self.s["tick"],
               "source": source, "targets": list(targets), "causes": list(causes),
               "payload": copy.deepcopy(payload or {}), "refs": [source, *targets, *causes]}
        self.put("events", obj)
        return obj["id"]

    def schedule(self, kind, due_tick, payload, owner, causes):
        if not isinstance(due_tick, int) or isinstance(due_tick, bool) or due_tick < self.s["tick"]:
            raise Rejected("SCHEDULE_IN_PAST_OR_INVALID")
        ev = self.event("WorkScheduled", owner, causes=causes, payload={"kind": kind, "due_tick": due_tick})
        self.s["enqueue_seq"] += 1
        obj = {"id": self.alloc("scheduled"), "kind": kind, "due_tick": due_tick,
               "enqueue_seq": self.s["enqueue_seq"], "lifetime": "WORLD_PROCESS", "owner": owner,
               "payload": copy.deepcopy(payload), "causes": [ev], "refs": [owner, ev]}
        self.s["queue"].append(obj)
        self.s["queue"].sort(key=lambda q: (q["due_tick"], q["enqueue_seq"]))
        return obj["id"]

    def _atomic(self, action):
        before = copy.deepcopy(self.s)
        visual_before = copy.deepcopy(self.presentation)
        try:
            result = action()
            self.validate(self.s)
            return copy.deepcopy(result)
        except Exception:
            self.s = before
            self.presentation = visual_before
            raise

    def command(self, command_id, kind, payload, *, harness=False):
        identity = canonical({"kind": kind, "payload": payload, "harness": harness})
        prior = self.s["receipts"].get(command_id)
        if prior:
            if prior["identity"] != identity:
                return {"ok": False, "reason": "COMMAND_ID_COLLISION"}
            return copy.deepcopy(prior["result"])

        def execute():
            result = self._dispatch_command(kind, copy.deepcopy(payload), harness)
            self.put("receipts", {"id": command_id, "identity": identity,
                                  "result": result, "refs": result.get("events", [])})
            return result
        try:
            return self._atomic(execute)
        except Rejected as exc:
            # A rejection has no effects, including no allocation/receipt/RNG.
            return {"ok": False, "reason": str(exc)}

    def apply_input(self, row):
        if row["input_seq"] != self.s["input_cursor"] + 1:
            raise Rejected("INPUT_SEQUENCE")
        if row["tick"] < self.s["tick"]:
            raise Rejected("INPUT_TIME_REVERSED")
        self.advance_to(row["tick"])
        payload = {k: v for k, v in row.items() if k not in ("input_seq", "tick", "type")}
        result = self.command(f"command:input-{row['input_seq']}", row["type"], payload,
                              harness=row["type"] == "InjectResolvedIncident")
        self.s["input_cursor"] = row["input_seq"]
        self.s["inputs"].append(copy.deepcopy(row))
        self.advance_to(row["tick"])
        return result

    def step(self):
        if not self.s["queue"]:
            return None
        work = self.s["queue"][0]
        new_tick = work["due_tick"] != self.s["tick"]
        count = 0 if new_tick else self.s["handlers_this_tick"]
        if count >= self.s["config"]["max_handlers_per_tick"]:
            raise WorkLimit(f"HANDLER_LIMIT tick={self.s['tick']} next={work['id']} kind={work['kind']}")

        def execute():
            item = self.s["queue"].pop(0)
            if new_tick:
                self.s["tick"] = item["due_tick"]
                self.s["handlers_this_tick"] = 0
            self.s["handlers_this_tick"] += 1
            if item["kind"] in self.extra_handlers:
                self.extra_handlers[item["kind"]](self, item)
            else:
                getattr(self, "on_" + item["kind"])(item)
            return item
        return self._atomic(execute)

    def advance_to(self, tick):
        if not isinstance(tick, int) or isinstance(tick, bool) or tick < self.s["tick"]:
            raise Rejected("TIME_REVERSED_OR_INVALID")
        while self.s["queue"] and self.s["queue"][0]["due_tick"] <= tick:
            self.step()
        if tick > self.s["tick"]:
            self.s["tick"] = tick
            self.s["handlers_this_tick"] = 0

    def snapshot(self):
        return canonical(self.s)

    def load(self, text):
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise InvalidSnapshot("DUPLICATE_JSON_KEY")
                result[key] = value
            return result
        try:
            candidate = json.loads(text, object_pairs_hook=unique_keys,
                                   parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            self.validate(candidate)
        except (ValueError, KeyError, TypeError, AttributeError, Rejected) as exc:
            raise InvalidSnapshot(str(exc)) from exc
        # Publication is a single assignment after all checks; no repair.
        self.s = candidate
        self.presentation = {}

    def digest(self):
        return hashlib.sha256(self.snapshot().encode("utf-8")).hexdigest()

    def schedule_presentation(self, location, token):
        self.get("locations", location)
        self.presentation.setdefault(location, []).append(token)

    def validate(self, s):
        if (s["schema"], s["contract"], s["runtime"]) != (SCHEMA, CONTRACT, RUNTIME):
            raise InvalidSnapshot("INCOMPATIBLE_VERSION")
        if s["profile_version"] != PROFILE:
            raise InvalidSnapshot("INCOMPATIBLE_PROFILE")
        if not isinstance(s["tick"], int) or isinstance(s["tick"], bool) or s["tick"] < 0:
            raise InvalidSnapshot("INVALID_TICK")
        ids = set()
        for store in STORES:
            for key, obj in s[store].items():
                if key != obj["id"] or key in ids:
                    raise InvalidSnapshot("DUPLICATE_OR_MISMATCHED_ID")
                ids.add(key)
        for q in s["queue"]:
            if q["id"] in ids:
                raise InvalidSnapshot("DUPLICATE_WORK_ID")
            ids.add(q["id"])
        seqs = set()
        for obj in [x for name in STORES for x in s[name].values()] + s["queue"]:
            if any(ref not in ids for ref in obj["refs"]):
                raise InvalidSnapshot("MISSING_REFERENCE:" + obj["id"])
        for a in s["actors"].values():
            if a["location"] not in s["locations"] or a["reservation"] < 0 or a.get("task_budget", 0) < 0:
                raise InvalidSnapshot("INVALID_ACTOR")
        for store in STORES:
            for obj in s[store].values():
                # Validate semantic fields independently of cached ref lists.
                for key in ("holder", "owner", "source", "recipient", "sender", "location", "storage",
                            "custody", "custodian", "issuer", "persona", "proposition", "cause",
                            "started_by", "review_cause", "visit_cause", "received_by", "removed_by", "derived_from"):
                    if obj.get(key) is not None and obj[key] not in ids:
                        raise InvalidSnapshot("MISSING_TYPED_REFERENCE:" + key)
        for q in s["queue"]:
            if (not isinstance(q["due_tick"], int) or isinstance(q["due_tick"], bool) or q["due_tick"] < s["tick"]
                    or not isinstance(q["enqueue_seq"], int) or isinstance(q["enqueue_seq"], bool)
                    or q["enqueue_seq"] in seqs or not 1 <= q["enqueue_seq"] <= s["enqueue_seq"]):
                raise InvalidSnapshot("INVALID_QUEUE_ORDER")
            if q["lifetime"] != "WORLD_PROCESS" or not (hasattr(self, "on_" + q["kind"]) or q["kind"] in self.extra_handlers):
                raise InvalidSnapshot("UNSUPPORTED_WORK")
            seqs.add(q["enqueue_seq"])
            # Typed targets in a pending payload must still resolve on load.
            for key in ("actor", "to", "message", "process", "record"):
                if key in q["payload"] and q["payload"][key] not in ids:
                    raise InvalidSnapshot("MISSING_WORK_TARGET")
        if s["queue"] != sorted(s["queue"], key=lambda q: (q["due_tick"], q["enqueue_seq"])):
            raise InvalidSnapshot("UNSORTED_QUEUE")
        if not 0 <= s["handlers_this_tick"] <= s["config"]["max_handlers_per_tick"]:
            raise InvalidSnapshot("INVALID_HANDLER_COUNTER")
        if s["input_cursor"] != len(s["inputs"]):
            raise InvalidSnapshot("INVALID_INPUT_CURSOR")
        if [row["input_seq"] for row in s["inputs"]] != list(range(1, s["input_cursor"] + 1)):
            raise InvalidSnapshot("INVALID_INPUT_SEQUENCE")
        dynamic = [int(key.split(":")[1]) for key in ids if key.split(":")[0] in
                   ("event", "scheduled", "observation", "memory", "proposition", "belief")]
        if dynamic and s["allocator"] < max(dynamic):
            raise InvalidSnapshot("ALLOCATOR_WOULD_REUSE_ID")
        # Causal log is an acyclic, committed order; no missing/pending parent.
        seen = set()
        for ev in sorted(s["events"].values(), key=lambda e: int(e["id"].split(":")[1])):
            if not set(ev["causes"]).issubset(seen) or ev["tick"] > s["tick"]:
                raise InvalidSnapshot("INVALID_CAUSAL_ANCESTRY")
            if any(target not in ids for target in ev["targets"]):
                raise InvalidSnapshot("MISSING_EVENT_TARGET")
            seen.add(ev["id"])

    def ancestors(self, event_id):
        found = set()
        def visit(key):
            if key in found:
                return
            found.add(key)
            for parent in self.s["events"][key]["causes"]:
                visit(parent)
        visit(event_id)
        return [copy.deepcopy(ev) for ev in sorted(self.s["events"].values(), key=lambda e: int(e["id"].split(":")[1])) if ev["id"] in found]

    def why_believes(self, holder, claim):
        return [self.ancestors(b["cause"]) for b in self.s["beliefs"].values()
                if b["holder"] == holder and b["claim"] == claim]

    def why_process_started(self, process):
        return self.ancestors(self.get("processes", process)["started_by"])

    def descendants(self, event):
        return [copy.deepcopy(e) for e in self.s["events"].values()
                if e["id"] != event and event in {p["id"] for p in self.ancestors(e["id"])}]

    def who_accessed(self, record):
        return [copy.deepcopy(e) for e in self.s["events"].values()
                if e["type"] == "RecordAccessed" and record in e["targets"]]

    def pending_world_work(self):
        return copy.deepcopy(self.s["queue"])

    def explain_command(self, command):
        return copy.deepcopy(self.get("receipts", command))

    def player_view(self, actor="actor:V0"):
        # Explicit player projection; never invokes the debug ancestry queries.
        a = self.get("actors", actor)
        actions = ["ChangeAvailability"]
        if a["availability"] not in ("asleep", "unavailable"):
            if "message:DIRECTIVE" not in self.s["messages"] and actor == "actor:V0":
                actions.append("SendMessage")
            if not a["travelling"] and any(r["from"] == a["location"] for r in self.s["config"]["routes"]):
                actions.append("StartTravel")
        return {"actor": actor, "location": a["location"], "availability": a["availability"],
                "memories": [copy.deepcopy(m["content"]) for m in self.s["memories"].values() if m["holder"] == actor],
                "messages": [copy.deepcopy(m["content"]) for m in self.s["messages"].values()
                             if m["recipient"] == actor and m["status"] == "received"],
                "actions": actions}

    def has_claim(self, actor, claim):
        return any(b["holder"] == actor and b["claim"] == claim for b in self.s["beliefs"].values())

    def learn(self, holder, content, provenance, cause, source_refs=()):
        observation = {"id": self.alloc("observation"), "holder": holder, "content": copy.deepcopy(content),
                       "provenance": provenance, "cause": cause, "refs": [holder, cause, *source_refs]}
        self.put("observations", observation)
        memory = {"id": self.alloc("memory"), **{k: copy.deepcopy(v) for k, v in observation.items() if k != "id"}}
        memory["refs"] += [observation["id"]]
        self.put("memories", memory)
        for claim in sorted(content.get("claims", [])):
            prop = self.put("propositions", {"id": self.alloc("proposition"), "claim": claim, "refs": []})
            self.put("beliefs", {"id": self.alloc("belief"), "holder": holder, "claim": claim,
                                  "proposition": prop["id"], "stance": "direct" if provenance == "direct" else "reported_or_recorded",
                                  "cause": cause, "provenance": provenance, "refs": [holder, cause, memory["id"], prop["id"]]})

    def _dispatch_command(self, kind, p, harness):
        if kind == "InjectResolvedIncident":
            if not harness:
                raise Rejected("HARNESS_ONLY")
            return self.incident(p)
        if kind == "SendMessage":
            return self.send_directive(p)
        if kind == "ChangeAvailability":
            a = self.get("actors", p["actor"])
            if p["value"] not in ("awake", "asleep", "active", "unavailable"):
                raise Rejected("INVALID_AVAILABILITY")
            a["availability"] = p["value"]
            ev = self.event("AvailabilityChanged", a["id"], payload={"value": p["value"]})
            if p["value"] == "awake":
                for m in list(self.s["messages"].values()):
                    if m["recipient"] == a["id"] and m["status"] == "waiting":
                        self.receive_message(m["id"], [ev])
            task = self.s["processes"].get("process:CLEANUP")
            if (task and task.get("report_pending") and task["state"] != "cancelled" and a["id"] == "actor:G1"
                    and p["value"] in ("active", "awake")):
                self.schedule("TaskReport", self.s["tick"], {}, a["id"], [ev])
            return {"ok": True, "events": [ev]}
        if kind == "UnloadPresentation":
            self.get("locations", p["location"])
            self.presentation.pop(p["location"], None)
            return {"ok": True, "events": []}
        if kind == "StartTravel":
            ev = self.travel(p["actor"], p["to"], [], None)
            return {"ok": True, "events": [ev]}
        if kind == "InspectRecord":
            ev = self.read_record(p["actor"], p["record"], [])
            return {"ok": True, "events": [ev]}
        if kind == "RemoveRecord":
            ev = self.remove_record(p["actor"], p["record"], [])
            return {"ok": True, "events": [ev]}
        if kind == "CancelTask":
            return self.cancel_task(p)
        raise Rejected("UNSUPPORTED_COMMAND:" + kind)

    def incident(self, p):
        self.get("actors", p["source"])
        self.get("actors", p["victim"])
        if self.get("actors", p["source"])["location"] != p["location"]:
            raise Rejected("INCIDENT_LOCATION")
        ev = self.event("ResolvedIncident", p["source"], [p["victim"], p["location"]], payload={"features": p["resolved_features"]})
        self.s["actors"][p["victim"]]["condition"] = "resolved_incident_victim"
        self.observe_incident(ev, p["location"], p["resolved_features"])
        return {"ok": True, "events": [ev]}

    def observe_incident(self, ev, location, visible_features):
        """Publish perceptible facts from an already committed domain action.

        A supplies a resolved fixture event; B supplies a real feeding event.
        This adapter never owns blood, health, intent or morality.
        """
        features = [f for f in visible_features if f in ("visible_fangs", "anomalous_contact", "contact_details")]
        if self.profile["witness_enabled"] and self.s["actors"]["actor:W1"]["location"] == location:
            claims = ["anomaly"]
            if self.s["actors"]["actor:W1"]["prior_alias_familiarity"]:
                claims.append("alias_attribution")
            content = {"features": sorted(set(features + (["contact_details"] if "anomalous_contact" in features else []))), "claims": claims}
            obs = self.event("IncidentObserved", "actor:W1", causes=[ev], payload=content)
            self.learn("actor:W1", content, "direct", obs)
            relation = self.s["config"]["relation"]
            self.put("relationships", {"id": "relationship:W1-V0", "holder": relation["observer"],
                                        "target": relation["target"], "dimensions": relation["change_on_anomaly"],
                                        "cause": obs, "refs": [relation["observer"], relation["target"], obs]})
            self.schedule("Testimony", self.profile["witness_transmission_tick"], {"content": content}, "actor:W1", [obs])
        cam = self.s["devices"]["device:D_CAM"]
        if cam["capture_enabled"] and cam["location"] == location:
            capture = self.event("CameraCapturedAndArchived", cam["id"], [cam["storage"]], [ev], {"channel": cam["transport"]})
            self.make_record("record:REC_ORIG", "video", {"features": features, "claims": ["anomaly"]}, capture,
                             source_device=cam["id"], captured_tick=self.s["tick"])

    def make_record(self, key, kind, content, cause, derived_from=None, **extra):
        obj = {"id": key, "kind": kind, "content": copy.deepcopy(content), "available": True, "integrity": "intact",
               "custody": "institution:P1", "location": "location:L_REG", "cause": cause,
               "derived_from": derived_from, "refs": ["institution:P1", "location:L_REG", cause], **extra}
        if derived_from:
            obj["refs"].append(derived_from)
        self.put("records", obj)
        self.s["institutions"]["institution:P1"]["records"].append(key)
        return obj

    def channel(self, sender, recipient, channel):
        return any(c == {"sender": sender, "recipient": recipient, "channel": channel} for c in self.s["config"]["channels"])

    def create_message(self, key, sender, recipient, channel, content, causes):
        if not self.channel(sender, recipient, channel):
            raise Rejected("NO_COMMUNICATION_CHANNEL")
        ev = self.event("MessageSent", sender, [recipient], causes, {"channel": channel})
        self.put("messages", {"id": key, "sender": sender, "recipient": recipient, "channel": channel,
                               "content": copy.deepcopy(content), "status": "sent", "cause": ev,
                               "refs": [sender, recipient, ev]})
        return ev

    def receive_message(self, key, causes=()):
        m = self.get("messages", key)
        a = self.get("actors", m["recipient"])
        if a["availability"] in ("asleep", "unavailable"):
            m["status"] = "waiting"
            return None
        if m["status"] == "received":
            return None
        ev = self.event("MessageReceived", a["id"], [key], [m["cause"], *causes])
        m.update(status="received", received_by=ev)
        m["refs"].append(ev)
        self.learn(a["id"], m["content"], "hearsay", ev, [key])
        return ev

    def send_directive(self, p):
        sender = self.get("actors", p["sender"])
        if sender["availability"] in ("asleep", "unavailable"):
            raise Rejected("SENDER_UNAVAILABLE")
        if p["recipient"] != "actor:G1" or p["sender"] != "actor:V0":
            raise Rejected("UNSUPPORTED_DIRECTIVE_RECIPIENT")
        d = p["directive"]
        # Sender communicates only known references. Removing information is legal.
        for ref in (d.get("office"), d.get("grant_reference"), d.get("target_selector", {}).get("source_device")):
            if ref and ref not in sender.get("knows", []):
                raise Rejected("SENDER_INFORMATION_MISSING")
        ev = self.create_message("message:DIRECTIVE", p["sender"], p["recipient"], p["channel"], {"directive": d}, [])
        self.schedule("DirectiveReceived", self.s["tick"], {"message": "message:DIRECTIVE"}, p["recipient"], [ev])
        return {"ok": True, "events": [ev]}

    def on_DirectiveReceived(self, q):
        received = self.receive_message(q["payload"]["message"], q["causes"])
        if not received:
            return
        d = self.s["messages"]["message:DIRECTIVE"]["content"]["directive"]
        task = self.put("processes", {"id": "process:CLEANUP", "owner": "actor:G1", "type": "remove_original",
                                      "state": "offered", "directive": copy.deepcopy(d), "started_by": received,
                                      "result": None, "refs": ["actor:G1", received]})
        if not d.get("office"):
            self.block_task("missing_office_information", [received])
            return
        selector = d.get("target_selector", {})
        if d.get("task") != "remove_original" or not selector.get("source_device") or selector.get("captured_tick") is None or not d.get("grant_reference"):
            self.block_task("missing_target_or_permission_information", [received])
            return
        a = self.s["actors"]["actor:G1"]
        if a.get("task_budget", 0) - a["reservation"] < self.profile["travel_charge"]:
            self.block_task("insufficient_resources", [received])
            return
        a["reservation"] = self.profile["travel_charge"]
        accepted = self.event("DirectiveAccepted", a["id"], [task["id"]], [received])
        task["state"] = "accepted"
        try:
            self.dispatch_cleanup_travel(a["id"], d["office"], [accepted], task["id"])
        except Rejected as exc:
            self.block_task(str(exc), [accepted])

    def dispatch_cleanup_travel(self, actor, destination, causes, process):
        self.travel(actor, destination, causes, process)

    def route(self, origin, destination):
        for route in self.s["config"]["routes"]:
            if route["from"] == origin and route["to"] == destination:
                return route["duration"]
        raise Rejected("NO_ROUTE")

    def travel(self, actor, destination, causes, process):
        a = self.get("actors", actor)
        self.get("locations", destination)
        if a["availability"] in ("asleep", "unavailable") or a["travelling"]:
            raise Rejected("ACTOR_UNAVAILABLE")
        duration = self.route(a["location"], destination)
        if duration < 1:
            raise Rejected("INVALID_ROUTE_DURATION")
        if process:
            cost = self.profile["travel_charge"]
            if a.get("task_budget", 0) < cost or a["reservation"] != cost:
                raise Rejected("RESOURCE_RESERVATION")
            a["task_budget"] -= cost
            a["reservation"] = 0
            self.s["processes"][process]["state"] = "travelling"
        a["travelling"] = True
        ev = self.event("TravelStarted", actor, [destination] + ([process] if process else []), causes,
                        {"from": a["location"], "to": destination, "duration": duration, "charged": self.profile["travel_charge"] if process else 0})
        payload = {"actor": actor, "to": destination}
        if process:
            payload["process"] = process
        self.schedule("Arrival", self.s["tick"] + duration, payload, actor, [ev])
        return ev

    def on_Arrival(self, q):
        p = q["payload"]
        a = self.get("actors", p["actor"])
        a.update(location=p["to"], travelling=False)
        a["refs"] = [a["location"]]
        ev = self.event("TravelArrived", a["id"], [p["to"]], q["causes"])
        if p.get("process"):
            task = self.s["processes"][p["process"]]
            if task["state"] == "cancelled":
                return
            task["state"] = "access_check"
            reason = self.task_access_reason()
            if reason:
                self.block_task(reason, [ev])
            else:
                task["state"] = "acting"
                self.schedule("RemovalAttempt", self.s["tick"] + self.profile["action_delay_after_arrival"], {}, a["id"], [ev])
        if a["id"] == "actor:I1" and "process:CASE" in self.s["processes"]:
            case = self.s["processes"]["process:CASE"]
            inquiry = self.event("AliasInquiry" if case.get("alias_known") else "IncidentInquiry", a["id"], [p["to"], case["id"]], [ev, case["review_cause"]])
            case.update(state="visited", visit_tick=self.s["tick"], visit_cause=inquiry)
            v0 = self.s["actors"]["actor:V0"]
            if (v0["location"] == p["to"] and not v0["travelling"] and v0["availability"] == "awake"
                    and self.profile.get("player_observes_visit", True)):
                content = {"claims": ["alias_inquiry" if case["alias_known"] else "incident_inquiry"], "features": ["public_inquiry"]}
                seen = self.event("InquiryObserved", v0["id"], causes=[inquiry], payload=content)
                self.learn(v0["id"], content, "direct", seen)

    def task_access_reason(self):
        task = self.s["processes"]["process:CLEANUP"]
        d = task["directive"]
        a = self.s["actors"]["actor:G1"]
        if a["availability"] in ("asleep", "unavailable"):
            return "agent_unavailable"
        if self.s["tick"] > d["deadline_tick"]:
            return "deadline_expired"
        grant = self.s["grants"].get(d["grant_reference"])
        if not grant or not grant["enabled"] or grant["holder"] != a["id"] or grant["issuer"] != "institution:P1" or grant["location"] != a["location"]:
            return "access_denied"
        if a["location"] != d["office"]:
            return "wrong_location"
        return None

    def permitted(self, actor, record, action):
        a = self.get("actors", actor)
        r = self.get("records", record)
        if not r["available"] or r["integrity"] != "intact":
            raise Rejected("RECORD_INACCESSIBLE")
        if a["availability"] in ("asleep", "unavailable") or a["travelling"] or a["location"] != r["location"]:
            raise Rejected("ACTOR_NOT_AT_RECORD")
        if action == "InspectRecord" and a.get("role") == "assigned_reviewer":
            if r["custody"] == "institution:P1":
                return
        for g in self.s["grants"].values():
            if (g["holder"] == actor and g["issuer"] == r["custody"] and g["enabled"] and g["location"] == r["location"]
                    and action in g["actions"] and r["kind"] == "video" and not r["derived_from"]
                    and r.get("source_device") == "device:D_CAM"):
                return
        raise Rejected("ACCESS_DENIED")

    def read_record(self, actor, record, causes):
        self.permitted(actor, record, "InspectRecord")
        r = self.s["records"][record]
        ev = self.event("RecordAccessed", actor, [record], [r["cause"], *causes])
        content = copy.deepcopy(r["content"])
        if r["kind"] == "video" and self.s["actors"][actor].get("prior_alias_appearance_sample"):
            if self.profile.get("camera_alias_attribution_requires_reviewer_prior_sample", True):
                content["claims"] = sorted(set(content["claims"] + ["alias_attribution"]))
        self.learn(actor, content, "record:" + r["kind"], ev, [record])
        return ev

    def remove_record(self, actor, record, causes):
        self.permitted(actor, record, "RemoveRecord")
        r = self.s["records"][record]
        ev = self.event("RecordRemoved", actor, [record], [r["cause"], *causes])
        r.update(available=False, removed_by=ev)
        r["refs"].append(ev)
        if self.profile.get("access_log_enabled", False):
            self.make_record("record:ACCESS_LOG", "access_log", {"claims": ["cleanup_by_G1"], "actor": actor,
                             "location": r["location"], "tick": self.s["tick"]}, ev)
        return ev

    def on_RemovalAttempt(self, q):
        task = self.s["processes"]["process:CLEANUP"]
        if task["state"] in ("cancelled", "blocked", "completed"):
            return
        reason = self.task_access_reason()
        if reason:
            self.block_task(reason, q["causes"])
            return
        selector = task["directive"]["target_selector"]
        matches = [r for r in self.s["records"].values() if r["kind"] == selector["record_kind"]
                   and not r["derived_from"] and r.get("source_device") == selector["source_device"]
                   and r.get("captured_tick") == selector["captured_tick"]]
        if len(matches) != 1:
            self.block_task("original_not_found", q["causes"])
            return
        try:
            accessed = self.read_record("actor:G1", matches[0]["id"], q["causes"])
            removed = self.remove_record("actor:G1", matches[0]["id"], [accessed])
        except Rejected as exc:
            self.block_task(str(exc), q["causes"])
            return
        task.update(state="reporting", result="removed_original_no_other_copy_observed")
        self.schedule("TaskReport", self.s["tick"] + self.profile["report_delay_after_action"], {}, "actor:G1", [removed])

    def block_task(self, reason, causes):
        task = self.s["processes"]["process:CLEANUP"]
        self.s["actors"]["actor:G1"]["reservation"] = 0
        ev = self.event("TaskBlocked", "actor:G1", [task["id"]], causes, {"reason": reason})
        task.update(state="blocked", result=reason)
        self.schedule("TaskReport", self.s["tick"] + self.profile["report_delay_after_action"], {}, "actor:G1", [ev])

    def on_TaskReport(self, q):
        task = self.s["processes"]["process:CLEANUP"]
        if task["state"] == "cancelled":
            return
        if self.s["actors"]["actor:G1"]["availability"] in ("asleep", "unavailable"):
            self.event("TaskReportDeferred", "actor:G1", [task["id"]], q["causes"], {"reason": "sender_unavailable"})
            task["report_pending"] = True
            return
        task["report_pending"] = False
        if task["state"] == "reporting":
            task["state"] = "completed"
        ev = self.create_message("message:RESULT", "actor:G1", "actor:V0", "mailbox", {"result": task["result"]}, q["causes"])
        self.receive_message("message:RESULT", [ev])

    def cancel_task(self, p):
        task = self.get("processes", p["process"])
        if task["owner"] != p["actor"]:
            raise Rejected("TASK_OWNER")
        ev = self.event("TaskCancelled", p["actor"], [task["id"]], [task["started_by"]])
        task["state"] = "cancelled"
        self.s["actors"][p["actor"]]["reservation"] = 0
        # Active travel may finish; task work is explicitly cancelled by cause.
        retained = []
        for q in self.s["queue"]:
            if q["kind"] in ("RemovalAttempt", "TaskReport") and q["owner"] == p["actor"]:
                self.event("WorkCancelled", p["actor"], causes=[ev, *q["causes"]], payload={"work_id": q["id"]})
            else:
                retained.append(q)
        self.s["queue"] = retained
        return {"ok": True, "events": [ev]}

    def on_Testimony(self, q):
        a = self.s["actors"]["actor:W1"]
        if a["availability"] in ("asleep", "unavailable") or not self.channel(a["id"], "actor:W2", "phone"):
            self.event("TestimonyBlocked", a["id"], causes=q["causes"])
            return
        content = copy.deepcopy(q["payload"]["content"])
        drop = self.profile["witness_message_transformation"]["drop_features"]
        content["features"] = [f for f in content["features"] if f not in drop]
        sent = self.create_message("message:TESTIMONY", a["id"], "actor:W2", "phone", content, q["causes"])
        received = self.receive_message("message:TESTIMONY", [sent])
        if received and self.profile["recipient_reports"] and self.s["actors"]["actor:W2"].get("role") == "report_submitter":
            submitted = self.event("ReportSubmitted", "actor:W2", ["institution:P1"], [received])
            self.make_record("record:REC_REPORT", "testimony", content, submitted)
            self.open_case("record:REC_REPORT", submitted)

    def open_case(self, record, cause):
        if "anomaly" not in self.s["records"][record]["content"].get("claims", []):
            return
        if "process:CASE" not in self.s["processes"]:
            ev = self.event("CaseOpened", "institution:P1", [record], [cause])
            self.put("processes", {"id": "process:CASE", "owner": "institution:P1", "type": "inquiry",
                                   "state": "open", "started_by": ev, "review_support": [], "alias_known": False,
                                   "refs": ["institution:P1", ev]})
            self.s["institutions"]["institution:P1"]["cases"].append("process:CASE")

    def on_CopyAttempt(self, q):
        cam = self.s["devices"]["device:D_CAM"]
        r = self.s["records"].get("record:REC_ORIG")
        if (not r or not r["available"] or r["integrity"] != "intact" or r["custody"] != cam["custodian"]
                or not self.profile.get("archive_access_enabled", True)):
            self.event("CopyBlocked", "institution:P1", causes=q["causes"], payload={"reason": "no_accessible_original"})
            return
        ev = self.event("RecordCopied", "institution:P1", [r["id"]], [r["cause"], *q["causes"]], {"access": "archive_profile"})
        self.make_record("record:REC_COPY", r["kind"], r["content"], ev, r["id"], source_device=r["source_device"], captured_tick=r["captured_tick"])

    def on_ReviewAttempt(self, q):
        support = []
        acquisitions = []
        # Select only real, available records in custody. No expected outcome IDs.
        for kind in ("testimony", "video", "access_log"):
            candidates = [r for r in self.s["records"].values() if r["kind"] == kind and r["available"]]
            if kind == "video":
                copies = [r for r in candidates if r["derived_from"]]
                candidates = copies or candidates
            for r in candidates:
                try:
                    acquired = self.read_record("actor:I1", r["id"], q["causes"])
                except Rejected:
                    continue
                acquisitions.append(acquired)
                if "anomaly" in r["content"].get("claims", []):
                    support.append(r["id"])
                    self.open_case(r["id"], acquired)
        if not support or "process:CASE" not in self.s["processes"]:
            self.event("ReviewBlocked", "actor:I1", causes=q["causes"], payload={"reason": "no_eligible_evidence"})
            return
        case = self.s["processes"]["process:CASE"]
        reviewed = self.event("CaseReviewed", "actor:I1", [case["id"], *support], [case["started_by"], *acquisitions])
        case.update(state="reviewed", review_support=support, review_cause=reviewed,
                    alias_known=self.has_claim("actor:I1", "alias_attribution"))
        case["refs"] += [reviewed, *support]

    def on_PlanVisitAttempt(self, q):
        case = self.s["processes"].get("process:CASE")
        if not case or not case["review_support"] or "review_cause" not in case:
            self.event("VisitBlocked", "actor:I1", causes=q["causes"], payload={"reason": "no_reviewed_case"})
            return
        ev = self.event("VisitPlanned", "actor:I1", [case["id"], "location:L_INC"], [case["review_cause"], *q["causes"]])
        self.travel("actor:I1", "location:L_INC", [ev], None)
        case["state"] = "visit_planned"
        case["refs"].append(ev)
