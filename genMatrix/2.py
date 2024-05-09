import numpy as np
import networkx as nx

# 创建一个空的无向图
G = nx.Graph()

# 添加50个节点（卫星）
for i in range(50):
    G.add_node(i)

# 根据连接规则添加边
for i in range(50):
    row = i // 10  # 计算卫星所在的轨道号
    col = i % 10   # 计算卫星在轨道上的位置

    # 添加同一轨道上相邻的两颗卫星的边
    if col > 0:
        G.add_edge(i, i - 1)
    if col < 9:
        G.add_edge(i, i + 1)

    # 添加相邻轨道上的两颗卫星的边
    if row > 0:
        G.add_edge(i, i - 10)
    if row < 4:
        G.add_edge(i, i + 10)

# 生成邻接矩阵
adj_matrix = nx.to_numpy_matrix(G)

# 设置打印选项，打印全部内容
np.set_printoptions(threshold=np.inf)
# 打印整个邻接矩阵，不换行显示
for row in adj_matrix:
    for elem in row:
        print(elem, end=' ')
    print("")