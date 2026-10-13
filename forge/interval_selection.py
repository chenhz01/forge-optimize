# -*- coding: utf-8 -*-
"""forge.interval-selection — classic activity selection.

Problem: given half-open intervals [s, e), pick the maximum number of
pairwise non-overlapping intervals (touching endpoints allowed).
Oracle: greedy by earliest end time (provably optimal) cross-checked
against an O(n^2) DP; a mismatch raises RuntimeError so a broken oracle
can never silently emit wrong ground truth.
"""
import random

from .common import make_id, int_knob

TYPE = "interval-selection"


def _greedy(intervals):
    order = sorted(intervals, key=lambda iv: (iv[1], iv[0]))
    count, last_end = 0, None
    for s, e in order:
        if last_end is None or s >= last_end:
            count += 1
            last_end = e
    return count


def _dp(intervals):
    order = sorted(intervals, key=lambda iv: (iv[1], iv[0]))
    ends = [e for _, e in order]
    n = len(order)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        s = order[i - 1][0]
        take = 1  # at worst pick this interval alone
        for j in range(i - 1, -1, -1):
            if ends[j] <= s:
                take = dp[j + 1] + 1  # intervals 0..j are all eligible
                break
        dp[i] = max(dp[i - 1], take)
    return dp[n]


def _solve(intervals):
    intervals = [(int(s), int(e)) for s, e in intervals]
    g = _greedy(intervals)
    d = _dp(intervals)
    if g != d:
        raise RuntimeError(
            "interval-selection oracle mismatch: greedy=%d dp=%d %r"
            % (g, d, intervals))
    return g


def generate(seed, difficulty=0.5):
    rng = random.Random("interval-selection|%d" % seed)
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
        "prompt": ("Activities as half-open intervals (start, end): %s. "
                   "Select the maximum number of activities so that no two "
                   "selected intervals overlap. Intervals touching at an "
                   "endpoint, e.g. (0, 3) and (3, 5), do NOT overlap. "
                   "How many activities can be selected at most?" % intervals),
        "answer": {"max_count": best},
        "solution": ("Greedy by earliest end time selects %d mutually "
                     "non-overlapping activities." % best),
        "meta": {"intervals": intervals},
    }


def verify(problem):
    try:
        intervals = [tuple(x) for x in problem["meta"]["intervals"]]
        return _solve(intervals) == problem["answer"]["max_count"]
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
    p["answer"]["max_count"] += 1
    cases.append(("verify-false-wrong-count", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["meta"]["intervals"] = [[0, 1], [0, 2], [0, 3]]  # forces max_count=1
    cases.append(("verify-false-tampered-intervals", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["answer"].pop("max_count")
    cases.append(("verify-false-missing", lambda p=p: verify(p) is False))
    from .common import schema_ok
    cases.append(("schema-ok", lambda: schema_ok(generate(42, 0.3))))
    cases.append(("touching-no-overlap",
                  lambda: _solve([(0, 3), (3, 5), (5, 8)]) == 3))
    cases.append(("nested-pick-ends",
                  lambda: _solve([(0, 10), (1, 4), (5, 9), (2, 3)]) == 2))
    return cases
