# -*- coding: utf-8 -*-
"""forge.shortest-path — shortest path on a DAG from jN back to j1.

Edges only go from higher-numbered nodes to lower-numbered nodes, so the
graph is a DAG and node order 1..N is already a valid topological order.
Weights are 1..20; density is a difficulty knob. Reachability of j1 from
jN is guaranteed by a direct edge fallback (re-drawn edges, then forced
jN->j1 if still unreachable).
"""
import random

from .common import make_id, int_knob, knob

TYPE = "shortest-path"


def _solve(n, edges):
    adj = {}
    for a, b, w in edges:
        adj.setdefault(a, []).append((b, w))
    INF = float("inf")
    dist = {i + 1: INF for i in range(n)}
    dist[n] = 0
    for u in range(n, 0, -1):  # topological order: high -> low
        if dist[u] == INF:
            continue
        for v, w in adj.get(u, ()):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist[1]


def _solve_with_path(n, edges):
    adj = {}
    for a, b, w in edges:
        adj.setdefault(a, []).append((b, w))
    INF = float("inf")
    dist = {i + 1: INF for i in range(n)}
    parent = {i + 1: None for i in range(n)}
    dist[n] = 0
    for u in range(n, 0, -1):
        if dist[u] == INF:
            continue
        for v, w in adj.get(u, ()):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
    path = []
    cur = 1
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()  # report as jN -> ... -> j1
    return dist[1], path


def _gen_edges(rng, n, density):
    edges = []
    for u in range(n, 1, -1):
        for v in range(u - 1, 0, -1):
            if rng.random() < density:
                edges.append((u, v, rng.randint(1, 20)))
    return edges


def generate(seed, difficulty=0.5):
    rng = random.Random("shortest-path|%d" % seed)
    n = int_knob(difficulty, 4, 8)
    density = knob(difficulty, 0.3, 0.7)
    edges = _gen_edges(rng, n, density)
    # Guarantee j1 reachable from jN.
    while _solve(n, edges) == float("inf"):
        edges.append((n, rng.randint(1, n - 1), rng.randint(1, 20)))
    if _solve(n, edges) == float("inf"):
        edges.append((n, 1, rng.randint(1, 20)))  # fallback direct edge
    dist, path = _solve_with_path(n, edges)
    return {
        "id": make_id(TYPE, seed),
        "type": TYPE,
        "difficulty": float(difficulty),
        "seed": int(seed),
        "prompt": ("A directed acyclic graph has nodes j1..j%d; every edge goes "
                   "from a higher-numbered node to a lower-numbered one. Edges "
                   "(from, to, weight): %s. Find the minimum total weight of a "
                   "path from j%d to j1 and report the sequence of nodes on that "
                   "path (including both endpoints). Any shortest path is "
                   "acceptable." % (n, edges, n)),
        "answer": {"shortest": dist, "path": path},
        "solution": ("Topological DP over j%d..j1 gives dist[j1] = %d." % (n, dist)),
        "meta": {"edges": edges, "start": "j%d" % n, "end": "j1", "n": n},
    }


def verify(problem):
    try:
        n = int(problem["meta"]["n"])
        edges = [(int(a), int(b), int(w)) for a, b, w in problem["meta"]["edges"]]
        if not (2 <= n) or not edges:
            return False
        dist = _solve(n, edges)
        if dist == float("inf"):
            return False
        if int(problem["answer"]["shortest"]) != dist:
            return False
        path = problem["answer"]["path"]
        if not isinstance(path, list) or len(path) < 2:
            return False
        nodes = []
        for x in path:
            if isinstance(x, str):
                if not (x.startswith("j") and x[1:].isdigit()):
                    return False
                nodes.append(int(x[1:]))
            else:
                nodes.append(int(x))
        if nodes[0] != n or nodes[-1] != 1:
            return False
        if any(not (1 <= v <= n) for v in nodes):
            return False
        weight = 0
        edge_set = {(a, b): w for a, b, w in edges}
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            if (a, b) not in edge_set:
                return False
            weight += edge_set[(a, b)]
        return weight == dist
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
    p["answer"]["shortest"] += 1
    cases.append(("verify-false-wrong-dist", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    p["answer"]["path"] = p["answer"]["path"][:-1]
    cases.append(("verify-false-broken-chain", lambda p=p: verify(p) is False))
    p = copy.deepcopy(base)
    a, b0 = p["answer"]["path"][0], p["answer"]["path"][1]
    p["meta"]["edges"] = [e for e in p["meta"]["edges"] if not (e[0] == a and e[1] == b0)]
    cases.append(("verify-false-tampered-edges", lambda p=p: verify(p) is False))
    cases.append(("schema-ok", lambda: schema_ok(generate(42, 0.3))))
    # Classic known answers.
    cases.append(("classic-chain", lambda: _solve(3, [(3, 2, 2), (2, 1, 3), (3, 1, 10)]) == 5))
    cases.append(("classic-direct-vs-detour", lambda: _solve(4, [(4, 1, 9), (4, 2, 1), (2, 1, 2), (4, 3, 1), (3, 1, 1)]) == 2))
    return cases
