'''
历史启发表 (可以改变搜索的顺序, 更好的先搜索)
记录了who方从src走到des的得分(因为从一个坐标src到des, 也有包含了对应棋子的信息(不同棋子的移动方式不同))
每次Max/Min之前都根据启发表排序all_actions, 并在结尾更新最优步骤到历史启发表中
'''
class history_table:
    def __init__(self):
        # 三维列表(2, 90, 90)(who, src_x * 9 + src_y, des_x * 9 + des_y)
        self.table = [[[0 for _ in range(90)] for _ in range(90)] for _ in range(2)]

    # 返回who的action的历史得分
    def get_score(self, who, action):
        return self.table[who][action.from_pos[0] * 9 + action.from_pos[1]][action.to_pos[0] * 9 + action.to_pos[1]]
    
    # 更新(深度越深越可靠，能得到更准确的估计值，使得更加倾向与搜索深的节点)
    def update_score(self, who, action, depth):
        self.table[who][action.from_pos[0] * 9 + action.from_pos[1]][action.to_pos[0] * 9 + action.to_pos[1]] += depth * depth
