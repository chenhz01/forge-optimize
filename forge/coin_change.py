# -*- coding: utf-8 -*-
"""forge.coin-change — minimum coin count (unbounded supply).

Problem: given a coin denomination set and a target amount, find the
minimum number of coins summing to it, or -1 if impossible. Oracle: the
classic O(amount * len(coins)) DP. With 1 in the denominations every
amount is reachable; a knob-controlled probability occasionally drops 1
(or keeps an unsolvable draw) so a small share of -1 cases survives.
"""
import random

from .common import make_id, int_knob, knob

TYPE = "coin-change"

_POOL = (1, 2, 5, 6, 9, 11)


def _solve(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] <= amount else -1


def _draw(rng, difficulty):
    p_no_one = knob(difficulty, 0.05, 0.12)
    if rng.random() < p_no_one:
        pool = [c for c in _POOL if c != 1]
        k = rng.choice((3, 4))
        return sorted(rng.sample(pool, k))
    k = rng.choice((3, 4))
    others = rng.sample([c for c in _POOL if c != 1], k - 1)
    return sorted([1] + others)


def generate(seed, difficulty=0.5):
    rng = random.Random("coin-change|%d" % seed)
    amount = int_knob(difficulty, 11, 60)
    p_keep_unsolvable = knob(difficulty, 0.10, 0.20)
    coins = None
    best = -1
    for _ in range(10):
        cand = _draw(rng, difficulty)
        cand_amount = amount
        got = _solve(cand, cand_amount)
        if got != -1:
            coins, best = cand, got
            break
        if rng.random() < p_keep_unsolvable:
            coins, best = cand, got
            break
    if coins is None:  # deterministic fallback: always solvable
        coins = [1, 5]
        best = _solve(coins, amount)
    return {
        "id": make_id(TYPE, seed),
        "type": TYPE,
        "difficulty": float(difficulty),
        "seed": int(seed),
        "prompt": ("Coin denominations: %s (unlimited supply of each). "
                   "Target amount: %d. What is the minimum number of coins "
                   "that sum exactly to the target? If the amount cannot be "
                   "formed, answer -1." % (coins, amount)),
        "answer": {"min_coins": best},
        "solution": ("Bottom-up DP over amounts 0..%d with unbounded coins "
                     "yields a minimum of %d coins." % (amount, best)),
        "meta": {"coins": coins, "amount": amount},
    }


def verify(problem):
    try:
        coins = [int(c) for c in problem["meta"]["coins"]]
        amount = int(problem["meta"]["amount"])
        return _solve(coins, amount) == problem["answer"]["min_coins"]
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
    p["answer"]["min_coins"] += 1
    cases.append(("verify-false-wrong-count", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["meta"]["amount"] += 1
    cases.append(("verify-false-tampered-amount", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["answer"].pop("min_coins")
    cases.append(("verify-false-missing", lambda p=p: verify(p) is False))
    from .common import schema_ok
    cases.append(("schema-ok", lambda: schema_ok(generate(42, 0.3))))
    cases.append(("classic-11", lambda: _solve([1, 5, 6, 9], 11) == 2))
    cases.append(("unsolvable", lambda: _solve([5, 6, 9], 7) == -1))
    return cases
