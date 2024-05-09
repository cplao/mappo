import numpy as np




def generateAdj():
    # 创建一个50x50的全零矩阵
    adj_matrix = np.zeros((50, 50), dtype=int)

    # 根据规则设置邻接关系
    for i in range(50):
        orbit = i // 10  # 计算卫星所在的轨道
        satellite_in_orbit = i % 10  # 计算卫星在轨道上的位置

        # 添加与同轨道的两颗卫星相连的边
        if satellite_in_orbit > 0:
            adj_matrix[i, i - 1] = 1
            adj_matrix[i - 1, i] = 1

        # 添加与相邻轨道的两颗卫星相连的边
        if orbit > 0:
            adj_matrix[i, i - 10] = 1
            adj_matrix[i - 10, i] = 1
        if orbit < 4:
            adj_matrix[i, i + 10] = 1
            adj_matrix[i + 10, i] = 1

    # 确保每一行刚好有四个1
    for i in range(50):
        row_sum = np.sum(adj_matrix[i])
        if row_sum < 4:
            indices = np.where(adj_matrix[i] == 0)[0]
            np.random.shuffle(indices)
            for j in range(4 - row_sum):
                adj_matrix[i, indices[j]] = 1

    # 设置打印选项，打印全部内容
    np.set_printoptions(threshold=np.inf)

    # 打印整个邻接矩阵，不换行显示
    # for row in adj_matrix:
    #     #     print(row.sum())
    #     for elem in row:
    #         print(elem, end=' ')
    #     print("")

    ans = []
    m, n = adj_matrix.shape
    for i in range(m):
        neighbors = []
        for j in range(n):
            if adj_matrix[i][j] == 1.0:
                neighbors.append(j)
        ans.append(neighbors)
    return ans

if __name__ == '__main__':
    ans = generateAdj()
    for row in ans:
        print(row)
