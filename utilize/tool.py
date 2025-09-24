import numpy as np
import os
import networkx as nx
import math

"""
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
"""


def beta_threshold(G):
    A = nx.to_numpy_array(G, dtype=float, weight=None)
    if A.size == 0:
        return math.inf

    if np.allclose(A, A.T):          # 对称 -> 实特征值，直接取最大
        lam_max = float(np.linalg.eigvalsh(A).max())
    else:                             # 非对称 -> 取最大模长
        evals = np.linalg.eigvals(A)
        lam_max = float(np.max(np.abs(evals)))

    if lam_max <= 0:
        return math.inf
    return float(1 / lam_max)



def name_to_path(network_name, path):
    folder = os.path.join(path, network_name)
    f = os.listdir(folder)[0]
    file_path = os.path.join(folder, f)
    return file_path