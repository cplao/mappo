from math import exp
from satellite import Satellite
from dataStream import DataStream
import numpy as np
import random
import readcsv

class myEnv:
    # 50个卫星 5个源 1个end
    def __init__(self, args):
        self.time = 0 # 时隙的轮次
        self.timeSlot = 1 # 每个时隙的大小
        self.time_limit = args.episode_limit # 最大时隙
        self.agent_num = args.agent_num
        self.satellite_num = args.satellite_num
        self.adj = args.adj  # 邻接矩阵
        self.satellite_list = []
        self.is_finish = [False for _ in range(self.agent_num)]
        self.agent_list = []
        self.compression_ratio_list = [0, 0.05, 0.1] # 图像压缩率的列表
        self.alpha = 0.2  # 传输时间和数据量之间的权重系数
        self.observation_space = 11  # 状态维度，数据量-1 + 所在卫星ID-1 + 四个邻居卫星的带宽-4
        self.arrive_data = 0
        # self.action_space = 7
        self.action_space = 12
        self.end = 20  # 前agent_num个卫星是EO卫星，从后面的id中随机生成一个终点
        self.min_data_amount = 10
        self.max_data_amount = 30
        self.min_bandwidth = 5
        self.max_bandwidth = 10
        self.min_transTime = self.min_data_amount / self.max_bandwidth
        self.max_transTime = self.max_data_amount / self.min_bandwidth
        self.toal_data_amount = 0 
        print("end:" + str(self.end))
        martrix = readcsv.read_csv('matrix.txt')
        for i in range(self.satellite_num):  # 生成所有的卫星对象
            neighbor_ids = self.adj[i]
            neighbor_bandwidths = []
            for j in range(4):
                neighbor_bandwidths.append(random.randint(self.min_bandwidth, self.max_bandwidth))
            if (i >= 0) and (i < self.agent_num):
                self.satellite_list.append(
                    Satellite(i, martrix[i], neighbor_bandwidths, 0))
            elif i == self.end:
                self.satellite_list.append(
                    Satellite(i, martrix[i], neighbor_bandwidths, 2))
            else:
                self.satellite_list.append(
                    Satellite(i, martrix[i], neighbor_bandwidths, 1))

        for i in range(self.agent_num):  # 生成所有的agent对象
            data_amount = random.randint(self.min_data_amount, self.max_data_amount)
            self.toal_data_amount += data_amount
            self.agent_list.append(DataStream(i, i, data_amount))

    def get_state(self):
        state = np.zeros((self.agent_num, self.observation_space))
        for i in range(self.agent_num):
            if self.agent_list[i] == -1:
                state[i][0] = -1
                state[i][1] = -1
                state[i][2] = -1
                state[i][3] = -1
                state[i][4] = -1
                state[i][5] = -1
                state[i][6] = -1
                state[i][7] = -1
                state[i][8] = -1
                state[i][9] = -1
                state[i][10] = -1
            else:
                state[i][0] = self.agent_list[i].data_amount
                state[i][1] = self.agent_list[i].curr_satellite_id
                state[i][2] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor_bandwidths[0]
                state[i][3] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor_bandwidths[1]
                state[i][4] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor_bandwidths[2]
                state[i][5] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor_bandwidths[3]
                state[i][6] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor[0]
                state[i][7] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor[1]
                state[i][8] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor[2]
                state[i][9] = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor[3]
                state[i][10] = self.end
        return state


    def take_action(self, action):  # 参数的action是从policy中sample出来的策略
        reward = np.zeros(self.agent_num)
        for i in range(self.agent_num):  # 更新agent的下一跳目的和数据量
            if self.agent_list[i] == -1:
                continue

            if self.agent_list[i].arrive_time is not None and self.agent_list[i].arrive_time <= self.time:
                self.agent_list[i].curr_satellite_id = self.agent_list[i].next_satellite_id
                self.agent_list[i].next_satellite_id = None
                self.agent_list[i].isTransmitting = False
                self.agent_list[i].arrive_time = None

            if self.agent_list[i].isTransmitting:
                continue
            i_agent_action = action[i]
            # agent_action_list = [dict(zip(self.compression_ratio_list, [neighbor])) for neighbor in self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor]
            agent_action_list = []
            for neighbor in range(4):
                #这里要改，有些不是4个可能要改一改
                for ratio in self.compression_ratio_list:
                    agent_action_list.append([ratio, neighbor])
            # temp_list = []  # 转发动作和丢弃动作的下标
            # for j, num in enumerate(agent_action_list[int(i_agent_action)]):
            #     if num == 1:
            #         temp_list.append(j)
            target = self.satellite_list[self.agent_list[i].curr_satellite_id].neighbor[agent_action_list[int(i_agent_action)][1]]
            self.agent_list[i].next_satellite_id = target  # 修改下一跳目的
            # print(str(i) + "next:" + str(target))
            self.agent_list[i].data_amount *= (1 - agent_action_list[int(i_agent_action)][0])  # 修改数据量
            if not self.agent_list[i].arrive_satellite_list.get(target):
                self.agent_list[i].arrive_satellite_list[target] = 1
            else:
                self.agent_list[i].arrive_satellite_list[target] = self.agent_list[i].arrive_satellite_list.get(target) + 1

        map = {}
        for i in range(self.agent_num):  # 获取每个agent能分得的带宽
            if self.agent_list[i] == -1:
                continue
            x, y = self.agent_list[i].curr_satellite_id, self.agent_list[i].next_satellite_id
            key = str(x) + "-" + str(y)
            if key in map:
                map[key] += self.agent_list[i].data_amount
            else:
                map[key] = self.agent_list[i].data_amount

        for i in range(self.agent_num):  # 修改到达时间和isTransmitting状态，以及计算reward
            if self.agent_list[i] == -1:
                continue
            if self.agent_list[i].isTransmitting:
                continue
            x, y = self.agent_list[i].curr_satellite_id, self.agent_list[i].next_satellite_id
            key = str(x) + "-" + str(y)
            band = self.satellite_list[x].idToBand[y]
            bandGet = self.agent_list[i].data_amount / map[key] * band
            transTime = self.agent_list[i].data_amount / bandGet
            self.agent_list[i].arrive_time = self.time + transTime / self.timeSlot
            self.agent_list[i].isTransmitting = True
            transTime_normalized = (transTime - self.min_transTime) / (self.max_transTime - self.min_transTime) 
            if self.agent_list[i].isTransmitting is True and self.agent_list[i].next_satellite_id == self.end:
                reward[i] = exp(((self.agent_list[i].data_amount + self.arrive_data)/self.toal_data_amount)) + 1 - exp(self.time / self.time_limit)
                if sum(self.is_finish) == self.agent_num:            
                        reward[i] += 1 + 1
            elif self.time <= self.time_limit - 2:
                if self.agent_list[i].arrive_satellite_list.get(target) is not None and self.agent_list[i].arrive_satellite_list.get(target) > 1:
                    reward[i] = -transTime_normalized +  exp((self.agent_list[i].data_amount/self.agent_list[i].original_data_amount))-1 - exp(self.agent_list[i].arrive_satellite_list.get(target) / self.time)
                else:
                    reward[i] = -transTime_normalized +  exp((self.agent_list[i].data_amount/self.agent_list[i].original_data_amount))-1 + exp(1 / self.time_limit - self.time)
            else:
                reward[i] = sum(self.is_finish) - self.agent_num

        return reward

    def update_agent_state(self):
        for i in range(self.agent_num):
            if self.agent_list[i] == -1:
                break
            if self.agent_list[i].arrive_time <= self.time:
                self.agent_list[i].curr_satellite_id = self.agent_list[i].next_satellite_id
                self.agent_list[i].next_satellite_id = None
                self.agent_list[i].isTransmitting = False
                self.agent_list[i].arrive_time = None

    def update_satellite_state(self):
        if self.time % 5 == 0:
            for i in range(self.satellite_num):
                self.satellite_list[i].changeBandwiths()

    def step(self, action):
        reward = self.take_action(action)
        self.time = self.time + 1
        self.update_satellite_state()
        self.update_agent_state()

        obs_next = self.get_state()

        if self.time <= self.time_limit - 1:
            done_n = self.is_finish
        else:
            print("time done")
            for i in  range(self.agent_num):
                if self.agent_list[i] != -1:
                    print(self.agent_list[i].arrive_satellite_list)
            done_n = np.ones(self.agent_num)

        information = None
        for i in  range(self.agent_num):
            if self.agent_list[i] == -1:
                continue
            if  self.satellite_list[self.agent_list[i].curr_satellite_id].type == 2:
                self.arrive_data = self.agent_list[i].data_amount
                self.is_finish[i] = True
                # print(self.agent_list[i].arrive_satellite_list)
                self.agent_list[i] = -1
                if all(self.is_finish):
                    print("all done")
                    done_n = np.ones(self.agent_num)
                    return obs_next, reward, done_n, information
        return obs_next, reward, done_n, information

    def reset(self):
        # for i in range(self.agent_num):
            # if self.agent_list[i] != -1:
            #     print(self.agent_list[i].arrive_satellite_list)
        self.time = 0
        self.agent_list = []
        self.is_finish = self.is_finish = [False for _ in range(self.agent_num)]
        self.arrive_data = 0
        for i in range(self.agent_num):
            data_amount = random.randint(self.min_data_amount, self.max_data_amount)
            self.agent_list.append(DataStream(i, i, data_amount))
        return self.get_state()





