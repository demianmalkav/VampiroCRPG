"""Measure scene integration and A/B regressions without rewriting old reports."""
import datetime
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from proof.m2.__main__ import EvidenceResult
from proof.m2b.__main__ import matches
from proof.m2b.scenario import prepare, run_until, observe
from proof.m2b.world import SurvivalWorld


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_m2_*.py')
    result = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult).run(suite)
    cases = []
    for spec in json.loads((ROOT/'tests/specs/m2_core_b_cases.json').read_text())['cases']:
        f = prepare(spec['id']); world = run_until(SurvivalWorld(f), f, spec['until'])
        actual = observe(world)
        cases.append({'case':spec['id'], 'status':'PASS' if matches(actual,spec) else 'FAIL', 'state_sha256':world.digest()})
    report = {'status':'PASS' if result.wasSuccessful() and all(c['status']=='PASS' for c in cases) else 'FAIL',
              'command':'python3 qa/scene/check.py', 'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'tests_run':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors),
              'scene_tests':sum('test_m2_scene.' in row['test'] for row in result.evidence),
              'core_regression_tests':sum('test_m2_core_' in row['test'] for row in result.evidence),
              'test_results':result.evidence, 'b_scenarios':cases,
              'browser_layout':'UNVERIFIED: browser executable absent; download failed',
              'frontend_event_check':'Separate Node DOM/canvas harness report: m2_scene_ui_run.json',
              'limitations':['one visible scene assumption; no general perception/lighting/occlusion system','presentation geometry does not own spatial simulation','private saves include whole world; ordinary view excludes it','no production engine, art, inventory or combat']}
    (ROOT/'tests/results/m2_scene_run.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Resultado: {report['status']}; {result.testsRun} pruebas; {len(cases)} escenarios B.")
    return int(report['status']!='PASS')


if __name__ == '__main__': raise SystemExit(main())
