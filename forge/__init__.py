# -*- coding: utf-8 -*-
"""forge-optimize: optimization reasoning graded by exact oracles."""
MODULES = {}
for _name in ("min_machines", "interval_selection", "makespan_two",
              "shortest_path", "coin_change"):
    try:
        _m = __import__("forge." + _name, fromlist=["x"])
        MODULES[_m.TYPE] = _m
    except ImportError:
        pass
