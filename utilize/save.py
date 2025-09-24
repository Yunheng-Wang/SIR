import os
import json
import shutil


def create_folder(save_path, network_path):
    base_name = os.path.splitext(os.path.basename(network_path))[0]

    target_folder = os.path.join(save_path, base_name)
    os.makedirs(target_folder, exist_ok=True)
    return target_folder, base_name


def save_json(target_folder, data, base_name, beta):
    
    json_path = os.path.join(target_folder, base_name + "_" + str(beta) + ".json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    

def save_networks(src_file, dst_file):
    shutil.copy(src_file, dst_file)