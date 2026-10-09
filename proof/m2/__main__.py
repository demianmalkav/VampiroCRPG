"""Run the naked proof: python3 -m proof.m2 [--suite] [--case ...]."""
import argparse
import datetime
import json
from pathlib import Path
import platform
import sys
import unittest

from .scenario import observe, prepare, read_fixture, run_until
from .world import CONTRACT, PROFILE, RUNTIME, World


LABELS = {
    "late_copy": "Retirada tardía",
    "early_removal": "Retirada temprana",
    "denied_access": "Acceso denegado",
    "insufficient_directive": "Información insuficiente",
}
NARRATION = {
    "ResolvedIncident": "Ocurre el incidente resuelto de prueba.",
    "IncidentObserved": "El testigo percibe el incidente y adquiere memoria propia.",
    "CameraCapturedAndArchived": "La cámara registra y transmite al archivo autorizado.",
    "DirectiveAccepted": "El agente acepta el encargo comunicado.",
    "RecordCopied": "El archivo crea una copia independiente.",
    "CopyBlocked": "El archivo no encuentra un original accesible para copiar.",
    "RecordRemoved": "El agente retira el original; los recuerdos y copias siguen existiendo.",
    "ReportSubmitted": "El receptor presenta un informe testimonial.",
    "CaseOpened": "Los indicios recibidos abren un caso institucional.",
    "TaskBlocked": "El encargo queda bloqueado.",
    "TaskReportDeferred": "El agente no puede informar mientras está indisponible.",
    "CaseReviewed": "El investigador accede a los indicios y revisa el caso.",
    "VisitPlanned": "La revisión justifica una visita; el investigador inicia el viaje.",
    "AliasInquiry": "El investigador llega y pregunta públicamente por el alias.",
    "IncidentInquiry": "El investigador llega y pregunta por el incidente sin identificar el alias.",
    "InquiryObserved": "El protagonista percibe la indagación; aprende sólo lo visible.",
}


def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args):
        super().__init__(*args)
        self.evidence = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.evidence.append({"test": test.id(), "status": "PASS"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.evidence.append({"test": test.id(), "status": "FAIL", "detail": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.evidence.append({"test": test.id(), "status": "ERROR", "detail": self._exc_info_to_string(err, test)})

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            self.evidence.append({"test": test.id(), "subtest": str(subtest), "status": "FAIL",
                                  "detail": self._exc_info_to_string(err, test)})


def execute_suite(report_path):
    root = Path(__file__).resolve().parents[2]
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_m2_core_a.py")
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, resultclass=EvidenceResult).run(suite)
    cases = []
    for spec in read_fixture()["cases"]:
        f, expected = prepare(spec["id"])
        w = run_until(World(f), f)
        actual = observe(w)
        cases.append({"case": spec["id"], "status": "PASS" if actual == expected else "FAIL",
                      "seed": f["seed"], "overrides": spec["overrides"], "tick": w.s["tick"],
                      "actual": actual, "expected": expected, "state_sha256": w.digest(),
                      "domain_events": len(w.s["events"]), "pending_work": len(w.s["queue"]),
                      "inputs": f["external_inputs"]})
    coverage = {}
    for prefix, count in (("NQR", 9), ("F", 7)):
        for number in range(1, count + 1):
            key = f"{prefix}-{number:02d}"
            matches = [e for e in result.evidence if f"test_{prefix}{number:02d}_" in e["test"]]
            coverage[key] = {"status": "PASS" if matches and all(e["status"] == "PASS" for e in matches) else "FAIL_OR_MISSING",
                             "tests": [e["test"] for e in matches]}
    passed = (result.wasSuccessful() and all(c["status"] == "PASS" for c in cases)
              and all(c["status"] == "PASS" for c in coverage.values()))
    report = {"status": "PASS" if passed else "FAIL", "runtime": RUNTIME, "contract": CONTRACT,
              "profile": PROFILE, "python": platform.python_version(),
              "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "command": "python3 -m proof.m2 --suite --report tests/results/m2_core_a_run.json",
              "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "snapshot_comparison": "semantic JSON at every atomic boundary, before and after save/load",
              "canonicalization": "UTF-8 JSON; sorted object keys; preserved list order; SHA-256",
              "test_results": result.evidence, "coverage": coverage, "cases": cases,
              "deferred": {"NQR-10": "NOT_IMPLEMENTED_STAGE_B", "NQR-11": "NOT_IMPLEMENTED_STAGE_B", "NQR-12": "NOT_IMPLEMENTED_STAGE_B"}}
    if report_path:
        write_json(report_path, report)
    print(f"Resultado: {report['status']}; {result.testsRun} pruebas; {len(cases)} escenarios.")
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description="La Noche que Recuerda — prueba causal sin gráficos")
    parser.add_argument("--suite", action="store_true", help="Ejecutar los ensayos de aceptación")
    parser.add_argument("--case", choices=LABELS, default="late_copy")
    parser.add_argument("--until", type=int, default=12)
    parser.add_argument("--report", help="Guardar resultados de la suite como JSON")
    parser.add_argument("--trace", help="Guardar hechos/causas y vista autorizada del protagonista")
    parser.add_argument("--save", help="Guardar snapshot de ensayo al terminar")
    parser.add_argument("--load", help="Reanudar snapshot con el mismo perfil y escenario")
    args = parser.parse_args()
    if args.suite:
        return execute_suite(args.report)
    f, expected = prepare(args.case)
    w = World(f)
    if args.load:
        w.load(Path(args.load).read_text(encoding="utf-8"))
        # A snapshot contains its own conditions. Do not resume against a different input stream.
        if w.s["config"]["case_id"] != args.case or w.s["inputs"] != f["external_inputs"][:w.s["input_cursor"]]:
            parser.error("El snapshot no coincide con las entradas del escenario elegido.")
        if w.s["config"]["routes"] != f["world"]["routes"] or w.profile != f["scenario_profile"]:
            parser.error("El snapshot usa condiciones de otro escenario.")
    run_until(w, f, args.until)
    print(f"La Noche que Recuerda — {LABELS[args.case]} — tick {w.s['tick']}")
    ordered = sorted(w.s["events"].values(), key=lambda e: int(e["id"].split(":")[1]))
    for ev in ordered:
        if ev["type"] in NARRATION:
            reason = f" ({ev['payload']['reason']})" if "reason" in ev["payload"] else ""
            print(f"t{ev['tick']:02d} · {NARRATION[ev['type']]}{reason}")
    actual = observe(w)
    if args.until == 12:
        print("Expectativas: " + ("PASS" if actual == expected else "FAIL"))
    print("Vista del protagonista: " + json.dumps(w.player_view(), ensure_ascii=False))
    if args.trace:
        write_json(args.trace, {"case": args.case, "runtime": RUNTIME, "actual": actual, "expected_at_tick12": expected,
                               "events": ordered, "player_view": w.player_view(), "state_sha256": w.digest()})
    if args.save:
        Path(args.save).write_text(w.snapshot() + "\n", encoding="utf-8")
    return int(args.until == 12 and actual != expected)


if __name__ == "__main__":
    raise SystemExit(main())
