"""Pure Revised dice mathematics and portable counter-based random draws."""
import hashlib
import re

from proof.m2.world import Rejected

ALGORITHM = 'sha256_counter_d10_v1'
LIMIT = 4294967290


def classify(dice, difficulty):
    if (not isinstance(difficulty, int) or isinstance(difficulty, bool) or not 2 <= difficulty <= 10
            or not dice or any(type(d) is not int or not 1 <= d <= 10 for d in dice)):
        raise Rejected('INVALID_DICE')
    raw = sum(d >= difficulty for d in dice)
    ones = dice.count(1)
    net = max(0, raw - ones)
    result = 'SUCCESS' if net else ('BOTCH' if raw == 0 and ones else 'FAILURE')
    return dict(dice=list(dice), difficulty=difficulty, raw_successes=raw,
                one_count=ones, net_successes=net, result=result)


def draw(seed_hex, stream, counter):
    if not re.fullmatch(r'[0-9a-f]{64}', seed_hex) or not re.fullmatch(r'[A-Za-z0-9:/.\-_]{1,128}', stream):
        raise Rejected('INVALID_RNG_IDENTITY')
    while True:
        if type(counter) is not int or not 0 <= counter < 2**64 - 1:
            raise Rejected('RNG_EXHAUSTED')
        message = f'M2B-D10-v1\n{seed_hex}\n{stream}\n{counter:020d}'.encode('ascii')
        candidate = int.from_bytes(hashlib.sha256(message).digest()[:4], 'big')
        counter += 1
        if candidate < LIMIT:
            return 1 + candidate % 10, counter
