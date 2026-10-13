# -*- coding: utf-8 -*-
"""forge.makespan-two — partition n jobs on 2 machines, minimize makespan.

Oracle: exact subset-sum. Total S; find the largest subset sum v <= S//2
attainable by some subset; makespan = S - v (the other machine gets the
rest, balanced as tightly as possible). With n <= 10, a bitmask sweep over
all <= 1024 subsets is exact and fast.
"""
import random

from .common import make_id, int_knob

TYPE = "makespan-two"


def _solve(durations):
    total = sum(durations)
    attainable = {0}
    for d in durations:
        attainable |= {v + d for v in attainable}
    v = max(x for x in attainable if x <= total // 2)
    return total - v


def generate(seed, difficulty=0.5):
    rng = random.Random("makespan-two|%d" % seed)
    n = int_knob(difficulty, 4, 10)
    durations = [rng.randint(1, 20) for _ in range(n)]
    best = _solve(durations)
    return {
        "id": make_id(TYPE, seed),
        "type": TYPE,
        "difficulty": float(difficulty),
        "seed": int(seed),
        "prompt": ("Jobs with durations %s must be split between two identical "
                   "machines. Each machine processes its assigned jobs one after "
                   "another. Assign every job to exactly one machine so that the "
                   "larger of the two machine loads is as small as possible. "
                   "What is that minimum makespan?" % durations),
        "answer": {"min_makespan": best},
        "solution": ("Subset-sum DP: best split gives loads %d/%d, so the "
                     "minimum makespan is %d." % (sum(durations) - best, best, best)),
        "meta": {"durations": durations},
    }


def verify(problem):
    try:
        durations = [int(x) for x in problem["meta"]["durations"]]
        return _solve(durations) == int(problem["answer"]["min_makespan"])
    except (KeyError, TypeError, ValueError):
        return False


def self_cases():
    import copy
    from .common import schema_ok
    cases = []
    for sd in range(5):
        cases.append(("gen-deterministic-%d" % sd,
                      lambda sd=sd: generate(sd, 0.5) == generate(sd, 0.5)))
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        cases.append(("verify-true-d%.2f" % d,
                      lambda d=d: verify(generate(123 + int(d * 100), d))))
    base = generate(7, 0.5)
    p = copy.deepcopy(base)
    p["answer"]["min_makespan"] += 1
    cases.append(("verify-false-wrong-makespan", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["meta"]["durations"][0] += 5
    cases.append(("verify-false-tampered-durations", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["answer"].pop("min_makespan")
    cases.append(("verify-false-missing", lambda p=p: verify(p) is False))
    cases.append(("schema-ok", lambda: schema_ok(generate(42, 0.3))))
    # Classic known answers.
    cases.append(("classic-equal-split", lambda: _solve([3, 3, 3, 3]) == 6))
    cases.append(("classic-one-big", lambda: _solve([10, 1, 1, 1, 1]) == 10))
    return cases
