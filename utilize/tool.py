import numpy as np
import os

def beta_threshold(G):
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    k_mean = degrees.mean()
    k2_mean = (degrees**2).mean()
    denom = k2_mean - k_mean
    return k_mean / denom


def network_critical(G):
    k = 1.0
    net_nodes = len(G.nodes())
    net_endge = sum([i[1] for i in G.degree()])
    first_order = net_endge*k/net_nodes

    #  计算网络的二阶平均度
    endge_list = [i[1] for i in G.degree()]
    list_temp = []
    for i in endge_list:
        list_temp.append(i*i)
    second_order = sum(list_temp) * k / net_nodes
    # print second_order

    #  返回节点的的感染临界值
    print("The network first is: %s " % str(net_endge*1.0 / net_nodes))
    print("The network critial is: %s " % str(first_order/second_order))
    #a=first_order/second_order
    #print(a)


def name_to_path(network_name, path):
    folder = os.path.join(path, network_name)
    f = os.listdir(folder)[0]
    file_path = os.path.join(folder, f)
    return file_path