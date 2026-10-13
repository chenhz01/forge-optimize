# -*- coding: utf-8 -*-
"""forge.min-machines — reference implementation.

Problem: given meeting intervals, find the minimum number of rooms (or
machines) needed so no two overlapping intervals share one. Oracle: the
classic sweep-line — sort events, +1 at start, -1 at end, peak = answer.
For intervals that touch at endpoints (end == start), the room frees up
exactly then, so we process -1 before +1 at equal times.
"""
import random

from .common import make_id, int_knob

TYPE = "min-machines"


def _solve(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))  # start: +1
        events.append((e, 0))  # end: -1, processed before starts at ties
    events.sort()
    cur = best = 0
    for _, kind in events:
        cur += 1 if kind else -1
        best = max(best, cur)
    return best


def generate(seed, difficulty=0.5):
    rng = random.Random("min-machines|%d" % seed)
    n = int_knob(difficulty, 4, 10)
    span = int_knob(difficulty, 10, 40)
    intervals = []
    for _ in range(n):
        s = rng.randrange(0, span)
        e = s + rng.randrange(1, max(2, span // 3))
        intervals.append((s, e))
    best = _solve(intervals)
    return {
        "id": make_id(TYPE, seed),
        "type": TYPE,
        "difficulty": float(difficulty),
        "seed": int(seed),
        "prompt": ("Meetings (start, end): %s. What is the minimum number of "
                   "rooms so that no two overlapping meetings share a room? "
                   "A meeting ending at time t frees the room for one starting "
                   "at t." % intervals),
        "answer": {"min_machines": best},
        "solution": "Sweep-line over start/end events peaks at %d concurrent meetings." % best,
        "meta": {"intervals": intervals},
    }


def verify(problem):
    try:
        intervals = [tuple(x) for x in problem["meta"]["intervals"]]
        return _solve(intervals) == problem["answer"]["min_machines"]
    except (KeyError, TypeError, ValueError):
        return False


def self_cases():
    import copy
    cases = []
    for sd in range(5):
        cases.append(("gen-deterministic-%d" % sd,
                      lambda sd=sd: generate(sd, 0.5) == generate(sd, 0.5)))
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        cases.append(("verify-true-d%.2f" % d,
                      lambda d=d: verify(generate(123 + int(d * 100), d))))
    base = generate(7, 0.5)
    p = copy.deepcopy(base)
    p["answer"]["min_machines"] += 1
    cases.append(("verify-false-wrong-count", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["meta"]["intervals"].append([0, 999])
    cases.append(("verify-false-tampered-intervals", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["answer"].pop("min_machines")
    cases.append(("verify-false-missing", lambda p=p: verify(p) is False))
    from .common import schema_ok
    cases.append(("schema-ok", lambda: schema_ok(generate(42, 0.3))))
    cases.append(("disjoint-one-room", lambda: _solve([(0, 1), (1, 2), (2, 3)]) == 1))
    cases.append(("all-overlap", lambda: _solve([(0, 10), (1, 9), (2, 8)]) == 3))
    return cases
