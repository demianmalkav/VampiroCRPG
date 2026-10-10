"""Pinned identity for the recorded CE Linux DAT-only experiments.

Kept independent of live-process/capture tools so archived evidence checks
need only Python's standard library. This is a measured reference identity,
not a production engine choice or a Windows-equivalence claim.
"""
CE_REVISION = "e97087b9582f37075db347a89898887320753f8b"
INPUTS = {
    "master.dat": "9b096d3035edafd4077deeb8ee7877a803b9db98497aa4596624b5c058a84711",
    "critter.dat": "da83d615967c0bac41fbc50e6b86b3088401ff69ed9d8b2e5be1d6ac0c125bcd",
    "patch000.dat": "d24788cf50294a27713a368f06cedb9b30c00ba709c2f1e0662ca2f6dddf2fc1",
}
