import os


from utilize.sir import SIR
from utilize.loader import Graph,load_config


def main(path):

    config = load_config("./config.yaml")

    for name in os.listdir(path):

        folder = os.path.join(path, name)
        f = os.listdir(folder)[0]
        file_path = os.path.join(folder, f)

        G = Graph(file_path)
        print(config)
        break
        



main("/home/dreams/Users/yunhengwang/DataSet_SIR/Networks/Animal_Social_Networks")

