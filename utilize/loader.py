import yaml
import networkx as nx
import os

from utilize.tool import beta_threshold


def load_betas(G, config):
    crit = beta_threshold(G)

    multipliers = config["training"]["beta"]

    if crit * 10 > 1:
        betas_head = [float(m * crit) for m in multipliers if m < 1]
        n_tail = sum(1 for m in multipliers if m >= 1)
        if n_tail <= 1:
            betas_tail = [float(crit)]
        else:
            step = (1.0 - crit) / (n_tail - 1)
            betas_tail = [float(crit + i * step) for i in range(n_tail)]
        betas = betas_head + betas_tail

    else:
        betas = [m * crit for m in multipliers]
    
    return betas


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def Graph(path):
    edges = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            parts = s.split()
            if len(parts) < 2:
                continue
            a, b = parts[0], parts[1]
            a = int(a)
            b = int(b)
            edges.append((a, b))
    G = nx.Graph()
    G.add_edges_from(edges)
    return G