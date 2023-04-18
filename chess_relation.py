'''
一个结构relation_table来记录对应位置的棋子被攻击或者被保护
'''

class relation_table:
    def __init__(self):
        self.attacked_num = 0
        self.guarded_num = 0
        # 最多被7个子攻击（很少超过3个）
        self.attacked = [0, 0, 0, 0, 0, 0, 0]
        # 最多大概被7个子保护（这里的保护是指别人吃了我，我队友可以吃回去）
        self.guarded = [0, 0, 0, 0, 0, 0, 0]