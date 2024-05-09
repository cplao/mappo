

agent:每个数据流可以当做是一个agent
action space：转发决策 + 压缩决策（比如转发决策是一个四维的one-hot向量，压缩决策是一个三维的one-hot向量，分别表示对原始EO图片压缩0,5%,8%）
state space：状态实际上主要就是包括当前数据流所在的卫星位置（决定了做什么样的转发决策和压缩决策）以及当前的数据已经被压缩了多少


GNN的主要是作用实际上就是对卫星节点的邻居带宽做一个聚合加权，在每一个round可能都需要运行一次GNN，主要作用就是优化卫星通信路由
但是这里似乎只是起到一个获取加权带宽的一个作用，似乎并没有降维的作用？不过不用降维也是OK，比如GNN的每一层的input和output的特征维度都设为相同即可

The challenge arises in determining whether
to aggregate all the relevant factors into a large state space for
every agent or to partition the state space into subspaces for
each agent. Both approaches prove to be inefficient.

通过GNN对原始的特征维度进行降维，并且可以降为到固定维度，那之前的维度为什么就不一样呢？（ra                                                                                                         obo的论文中）