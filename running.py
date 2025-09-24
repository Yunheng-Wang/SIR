import os
from tqdm import tqdm


from utilize.sir import SIR
from utilize.loader import Graph, load_config, load_betas
from utilize.tool import name_to_path
from utilize.save import save_json, save_networks, create_folder
from tqdm import tqdm


config = load_config("./config.yaml")

networks = os.listdir(config["base"]["networks_path"])

for network_name in tqdm(networks, desc="Networks", unit="net"):

    network_path = name_to_path(network_name, config["base"]["networks_path"])

    G = Graph(network_path)

    betas = load_betas(G, config)

    target_folder, base_name = create_folder(config["base"]["save_path"], network_path)

    for beta in tqdm(betas, desc=f"Betas for {network_name}", leave=False, unit="β"):
        results = SIR(G, beta, config["training"]["gamma"], config["training"]["trials"])
        save_json(target_folder, results, base_name, beta)
        save_networks(network_path, target_folder)
