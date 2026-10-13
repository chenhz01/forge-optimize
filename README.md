# forge-optimize

> **Two independent algorithms must agree before a problem ships.** Optimization-reasoning problems (scheduling, packing, routing) where the answer is certified by exact dynamic programming — and where the oracle cross-checks itself.

Part of the [forge family](https://github.com/chenhz01/forge-kit): [scireason-forge](https://github.com/chenhz01/scireason-forge) · [forge-agentic](https://github.com/chenhz01/forge-agentic) · [forge-code](https://github.com/chenhz01/forge-code) · [forge-sql](https://github.com/chenhz01/forge-sql) · [forge-security](https://github.com/chenhz01/forge-security).

## Why this exists

Optimization is where small models confidently produce "an answer" instead of "the answer". Grading here is exact: sweep-lines, subset-sum DP, longest-path DP — and in `interval-selection`, the greedy oracle is *double-checked by an independent DP at generation time*. If the two ever disagree, the problem refuses to exist.

## Five task types (W1: 250 problems)

| Type | What it drills | Oracle |
|---|---|---|
| `min-machines` | Minimum rooms/machines for overlapping intervals | Sweep-line peak |
| `interval-selection` | Max non-overlapping intervals | Greedy + DP cross-check |
| `makespan-two` | Split tasks on 2 machines, minimize the heavier load | Subset-sum exact DP |
| `shortest-path` | Shortest path on a random DAG | Topological DP + path-chain validation |
| `coin-change` | Minimum coins for an amount | Classic DP |

## Quickstart

```bash
python cli.py generate --type all --per-type 50 --seed0 1000 --out data/w1.jsonl
python cli.py grade --file data/w1.jsonl        # SUMMARY: 250/250 passed
python self_test.py                             # SUMMARY: PASS 162/162
python -m bench.harness --file data/w1.jsonl --backend random   # chance: 0.0%
```

## When NOT to use

NP-hard instances at scale (instances stay small enough for *exact* oracles — that's the point); continuous optimization.

## License & contact

MIT — © zhengming contributors. Developer tooling, not professional advice. Contact: hcac4735@agent.qq.com
