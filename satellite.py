import random


class Satellite:
    def __init__(self, id, neighbor_ids, neighbor_bandwidths, type):
        self.id = id
        self.neighbor = neighbor_ids
        self.neighbor_bandwidths = neighbor_bandwidths
        self.idToBand = {}
        for i in range(4):
            self.idToBand[self.neighbor[i]] = self.neighbor_bandwidths[i]
        self.type = type #三个取值：0，1，2 0表示他是生成数据的卫星，2表示他是终止卫星， 1表示他是中继卫星

    def changeBandwiths(self):
        for i in range(4):
            self.neighbor_bandwidths[i] += random.randint(-10, 10)






