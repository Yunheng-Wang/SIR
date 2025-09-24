import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
import numpy as np
import multiprocessing as mp


def simulate(G, beta, gamma, node):
    model = ep.SIRModel(G)
    cfg = mc.Configuration()
    cfg.add_model_parameter("beta", beta)    
    cfg.add_model_parameter("gamma", gamma)  
    cfg.add_model_initial_configuration("Infected", [node])
    model.set_initial_status(cfg)

    while True:
        it = model.iteration()
        cnt = it["node_count"]  
        I_t = cnt.get(1, 0)
        R_t = cnt.get(2, 0)

        if I_t == 0:
            return R_t


def _simulate_trials(args):
    G, beta, gamma, node, num_trials = args
    N = G.number_of_nodes()

    results = []
    for _ in range(num_trials):
        R = simulate(G, beta, gamma, node)  
        results.append(R / N)
    
    return results


def sir_node(G, beta, gamma, node, trials):
    cpu_count = mp.cpu_count() 
    n_workers = min(cpu_count, trials) 
    base, extra = divmod(trials, n_workers)
    trial_splits = [base + (1 if i < extra else 0) for i in range(n_workers)]
    
    with mp.Pool(processes=n_workers) as pool:
        tasks = [(G, beta, gamma, node, t) for t in trial_splits if t > 0]
        results = pool.map(_simulate_trials, tasks)
    all_results = np.concatenate(results)

    return float(all_results.mean())
    
    

def SIR(G, beta, gamma, trials):
    details = {}
    nodes = list(G.nodes())

    for u in nodes:
        mean = sir_node(G, beta, gamma, u, trials)
        details[u] = {"mean": mean}
    
    return dict(sorted(((u, details[u]["mean"]) for u in nodes), key=lambda x: x[1], reverse=True))

