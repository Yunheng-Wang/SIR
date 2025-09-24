import yaml
import networkx as nx


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