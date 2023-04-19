import time
import chess_const as cc
import history_heuristic as hh
import chess_relation as cr
import repeat as rp
import zobrist_code as zc

# chess结构
class chess:
    def __init__(self, type: int, who: int):
        self.type = type
        self.who = who

    def __str__(self):
        return "(%-5s, %s)" % (cc.TYPE_MAP_SHOW[self.type], cc.COLOR_MAP[self.who])

# action结构（动作）
class action:
    def __init__(self, from_pos: tuple, to_pos: tuple):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.score = 0      # score记录从from到to的历史得分

    # list.sort的比较函数(大到小)
    def __lt__(self, other):
        return self.score > other.score
    
    def __str__(self):
        return "(%d, %d)->(%d, %d) " % (self.from_pos[0], self.from_pos[1], self.to_pos[0], self.to_pos[1])


# 棋盘类（每一个位置一个chess棋子）
class chess_board:
    def __init__(self, board: list):
        # 棋盘
        self.board = board
        # 历史启发表
        self.history_table = hh.history_table()
        # 记录初始棋盘的zobrist
        self.zobrist = zc.Zobrist()
        self.zobrist.initialize()
        self.zval = self.zobrist.init_value(self.board)

    def print_board(self):
        print("=" * 120)
        for i in range(10):
            for j in range(9):
                print(self.board[i][j], end=' | ')
            print()
            if i == 4:
                print("= "*60)
            elif i <= 8:
                print("-" * 120)
        print("=" * 120)
        print()

    # who一方走完一步就判断该方是否获胜
    def win(self, who):
        if who == cc.BLACK:
            for i in range(7, 10):
                for j in range(3, 6):
                    if self.board[i][j].type == cc.KING and self.board[i][j].who == cc.RED:
                        return False
            return True
        elif who == cc.RED:
            for i in range(0, 3):
                for j in range(3, 6):
                    if self.board[i][j].type == cc.KING and self.board[i][j].who == cc.BLACK:
                        return False
            return True

    # # 普通深度受限alpha_beta算法(求who一方的最大得分和action)
    # # 叶子节点求的全都是who一方的得分，Max最大化who的得分，Min最小化who的得分
    # def alpha_beta(self, max_depth, who, show_time=True):
    #     start_time = time.time()
    #     # 用来计算每一层搜索的数量(传入参数cnt)
    #     cnt = [0 for _ in range(max_depth)]
    #     length = [0 for _ in range(max_depth)]
    #     score, best_action = self.Max_Value(cc.MIN_VAL, cc.MAX_VAL, 1, max_depth, who, cnt, length)
    #     cost_time = time.time() - start_time
    #     if show_time:
    #         print("-" * 50)
    #         print("共搜索了 %f s" % (cost_time))
    #         for i in range(1, max_depth):
    #             print("第 %d 层共有了 %d 个节点" % (i + 1, length[i]))
    #         print('-' * 50)
    #         print("-" * 50)
    #         for i in range(1, max_depth):
    #             print("第 %d 层搜索了 %d 个节点" % (i + 1, cnt[i]))
    #         print('-' * 50)
    #     #
    #     return score, cost_time, best_action, length, cnt
    
    # 迭代加深的alpha-beta算法
    # # 叶子节点求的全都是who一方的得分，Max最大化who的得分，Min最小化who的得分
    # def alpha_beta(self, max_depth, who):
    def alpha_beta(self, max_depth, who, show_time=True, repeat_queue: rp.RepeatQueue=None):
        start_time = time.time()
        max_time, cost_time = cc.MAX_TIME, 0
        for mdepth in range(2, max_depth + 1):
            cnt = [0 for _ in range(mdepth)]
            length = [0 for _ in range(mdepth)]
            score, best_action = self.Max_Value(cc.MIN_VAL, cc.MAX_VAL, 1, mdepth, who, cnt, length, repeat_queue)
            cost_time = time.time() - start_time
            if cost_time > max_time:
                break
        if show_time:
            print('-' * 50)
            print("深度为 %d 搜索了 %f s" % (mdepth, cost_time))
            for i in range(1, mdepth):
                print("第 %d 层共有 %d 个节点" % (i + 1, length[i]))
            print("-" * 50)
            for i in range(1, mdepth):
                print("第 %d 层搜索了 %d 个节点" % (i + 1, cnt[i]))
            print('-' * 50)
        return score, cost_time, best_action, length, cnt
    
    # Max_Value算法(α)（who为当前行动的颜色）
    def Max_Value(self, alpha, beta, depth, max_depth, who, cnt: list, length: list, repeat_queue: rp.RepeatQueue=None):
        # 敌方吃掉了帅
        if self.win(cc.BLACK if who == cc.RED else cc.RED):
            return cc.MIN_VAL + depth, None             # 这里+depth是一个优化，使得可以赢的时候，选择深度浅的
        # 到达深度就返回
        if depth == max_depth:
            return self.utility(who, who), None
        all_actions = self.get_all_action(who)
        # 根据历史启发表获取所有步骤的得分并进行排序，来达到更好地剪枝
        for ac in all_actions:
            ac.score = self.history_table.get_score(who, ac)
        all_actions.sort()
        best_action = all_actions[0]        # 如果不赋值一个当出现必死局时就没有best_action就会报错
        v = cc.MIN_VAL
        length[depth] = length[depth] + len(all_actions)
        for step in all_actions:
            cnt[depth] = cnt[depth] + 1
            # 移动之前检查是否出现过该局面,若出现过,返回最小得分
            next_val = self.zobrist.next_value(self.zval, step.from_pos[0], step.from_pos[1], step.to_pos[0], step.to_pos[1], \
                                               self.board[step.from_pos[0]][step.from_pos[1]], self.board[step.to_pos[0]][step.to_pos[1]])
            if repeat_queue != None and repeat_queue.has_repeat(next_val):
                score = cc.MIN_VAL + 1
            else:
                #因为要移动,所以此时board变了,则zval也要变
                pre_zval = self.zval
                self.zval = next_val
                # 移动self.board中的chess，后面再改回来
                to_chess = self.move_to(step.from_pos, step.to_pos)
                score, _ = self.Min_Value(alpha, beta, depth + 1, max_depth, cc.BLACK if who == cc.RED else cc.RED, cnt, length)
                self.move_to(step.to_pos, step.from_pos, to_chess)
                # 移动回来,zval也要变回来
                self.zval = pre_zval
            # 如果估计值更大：
            if score > v:
                v = score
                best_action = step
            alpha = max(alpha, v)
            # 剪枝
            if alpha >= beta:
                break
        # 将最优的步骤更新到历史启发表
        self.history_table.update_score(who, best_action, depth)
        return v, best_action
    
    # Min_Value算法(β)（who为当前行动的颜色）
    def Min_Value(self, alpha, beta, depth, max_depth, who, cnt: list, length: list, repeat_queue: rp.RepeatQueue=None):
        # 如果经过了Max(己方走完)后己方已经获胜，那么直接返回最大效益值
        if self.win(cc.BLACK if who == cc.RED else cc.RED):
            return cc.MAX_VAL - depth, None         # 这里-depth是一个优化，使得可以赢的时候，选择深度浅的
        if depth == max_depth:
            return self.utility(cc.BLACK if who == cc.RED else cc.RED, who), None        # 因为Min的是另一方,获取的utility都是己方的值
        all_actions = self.get_all_action(who)
        # 根据历史启发表获取所有步骤的得分并进行排序，来达到更好地剪枝
        for ac in all_actions:
            ac.score = self.history_table.get_score(who, ac)
        all_actions.sort()
        best_action = all_actions[0]
        v = cc.MAX_VAL
        length[depth] = length[depth] + len(all_actions)
        for step in all_actions:
            cnt[depth] = cnt[depth] + 1
            # 移动之前检查是否出现过该局面,若出现过,返回最小得分
            next_val = self.zobrist.next_value(self.zval, step.from_pos[0], step.from_pos[1], step.to_pos[0], step.to_pos[1], \
                                               self.board[step.from_pos[0]][step.from_pos[1]], self.board[step.to_pos[0]][step.to_pos[1]])
            if repeat_queue != None and repeat_queue.has_repeat(next_val):
                score = cc.MAX_VAL - 1
            else:
                #因为要移动,所以此时board变了,则zval也要变
                pre_zval = self.zval
                self.zval = next_val
                # 移动self.board中的chess，后面再改回来
                to_chess = self.move_to(step.from_pos, step.to_pos)
                score, _ = self.Max_Value(alpha, beta, depth + 1, max_depth, cc.BLACK if who == cc.RED else cc.RED, cnt, length)
                self.move_to(step.to_pos, step.from_pos, to_chess)
                # 移动回来,zval也要变回来
                self.zval = pre_zval
            # 如果估计值更小：
            if score < v:
                v = score
                best_action = step
            beta = min(beta, v)
            # 剪枝
            if alpha >= beta:
                break
        # 将最优的步骤更新到历史启发表
        self.history_table.update_score(who, best_action, depth)
        return v, best_action
    
    # 移动到下一个状态（直接改变self.board,默认from的位置置空）
    def move_to(self, from_pos: tuple, to_pos: tuple, recover=chess(cc.NULL, cc.BLACK)):
        chess_tmp = self.board[to_pos[0]][to_pos[1]]
        self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
        self.board[from_pos[0]][from_pos[1]] = recover
        return chess_tmp
    
    # who一方的得分和另一方的得分差值(棋子棋力+位置+机动性+关系)(在深度最深的时候才调用)
    # 现在轮到turn一方走!!(不是who走)
    def utility(self, who, turn):
        # 黑和红各自的得分 (1.棋子棋力, 2.位置, 3.机动性, 4.关联性)
        base_val = [0, 0]
        pos_val = [0, 0]
        mobile_val = [0, 0]
        relation_val = [0, 0]
        # 棋子之间的关系表组成的列表(每个棋子都有一个关系表)
        relation_list = self.init_relation_list()
        for i in range(10):
            for j in range(9):
                # 当前棋子类型（可能为己方，也可能为敌方）
                now_chess = self.board[i][j]
                if now_chess.type == cc.NULL:
                    continue
                # 获取当前棋子能走的地方（包括空、吃敌方棋子、保护己方棋子）
                all_actions = self.get_chess_action(i, j, now_chess.who, True)
                # 1.棋子对应的一方的base_val增加-----------------------------------------------------------
                base_val[now_chess.who] += cc.base_value[now_chess.type]
                # 2.棋子对应方的位置pos_val增加------------------------------------------------------------
                if now_chess.who == cc.BLACK:
                    pos_val[now_chess.who] += cc.pos_value[now_chess.type][i][j]
                elif now_chess.who == cc.RED:
                    pos_val[now_chess.who] += cc.pos_value[now_chess.type][9 - i][8 - j]
                # 遍历所有可行的动作（包括空、吃、保），计算机动性和记录关系表
                for ac in all_actions:
                    des_chess = self.board[ac.to_pos[0]][ac.to_pos[1]]
                    # 3.计算机动性------------------------------------------------------------------------------
                    if des_chess.type == cc.NULL:
                        mobile_val[now_chess.who] += cc.mobile_value[now_chess.type]
                    # 4.记录关系表(后面再用循环记录关系值)--------------------------------------------------------
                    # ①如果对面棋子是被now_chess攻击的棋子，增加des棋子关系表中的被攻击attacked值
                    elif des_chess.who != now_chess.who:
                        # 可以吃将(可能是turn被吃，也可能是turn吃，但现在轮到turn走)
                        if des_chess.type == cc.KING:
                            if des_chess.who != turn:    # turn吃 -> 结束
                                if who == turn:     # turn获胜, 若who方是turn方,则返回很大的值
                                    return cc.MAX_VAL - 10  # 返回的值是最大还要小，因为当前走到了最深处，若前面能更快结束就走前面
                                else:               # turn获胜, 若who不是turn方,则返回很小的值
                                    return cc.MIN_VAL + 10
                            else:                       # turn被将军(因为现在轮到turn走)
                                relation_val[turn] -= 20 # 被将军扣一点分
                                continue
                        # 除了吃将以外其他情况，记录被攻击者和攻击者的关系表
                        relation_list[ac.to_pos[0]][ac.to_pos[1]].attacked[
                            relation_list[ac.to_pos[0]][ac.to_pos[1]].attacked_num] = now_chess.type
                        relation_list[ac.to_pos[0]][ac.to_pos[1]].attacked_num += 1
                    # ②如果对面棋子是被now_chess保护的，增加des棋子关系表中被保护的guarded值
                    elif des_chess.who == now_chess.who:
                        # 保护将没有用(如果将被吃了就结束了)
                        if des_chess.type == cc.KING:
                            continue
                        relation_list[ac.to_pos[0]][ac.to_pos[1]].guarded[
                            relation_list[ac.to_pos[0]][ac.to_pos[1]].guarded_num] = now_chess.type
                        relation_list[ac.to_pos[0]][ac.to_pos[1]].guarded_num += 1
        # 到此，base_val、pos_val、mobile_val和关系表已经记录完毕
        # 接下来根据关系表计算relation_val(攻击与防守的得分不是直接就是base_value，而是预测的，所以得分减少一点)
        for i in range(10):
            for j in range(9):
                now_chess = self.board[i][j]
                now_who, enemy_who = now_chess.who, cc.BLACK if now_chess.who == cc.RED else cc.RED 
                unit_val = cc.base_value[now_chess.type] >> 3   # 棋子棋力的基本值(这只是预测的，所以小一些)
                attacked_num = relation_list[i][j].attacked_num     # 攻击者的棋子数量
                guarded_num = relation_list[i][j].guarded_num       # 保护者的棋子数量
                attacked_sum = 0                                    # 攻击者的棋力和
                guarded_sum = 0                                     # 保护者的棋力和
                min_attacked = cc.MAX_VAL                           # 攻击者最小棋力
                max_attacked = 0                                    # 攻击者最大棋力
                max_guarded = 0                                     # 保护着最大棋力
                min_flag = cc.MAX_VAL                               # 用于标记攻击者是否有小于被攻击者的棋子的棋力
                if now_chess.type == cc.NULL:
                    continue
                # 统计攻击者的棋子棋力
                for k in range(attacked_num):
                    attack_val = cc.base_value[relation_list[i][j].attacked[k]]
                    # 如果攻击方的棋子棋力小于被攻击的棋子，就记录攻击方的最小棋力
                    if attack_val < cc.base_value[now_chess.type] and attack_val < min_flag:
                        min_flag = attack_val
                    # min_flag = min(min_flag, min(cc.base_value[now_chess.type], attack_val))  # 理论上上面的方法更优，但这个更快
                    min_attacked = min(min_attacked, attack_val)
                    max_attacked = max(max_attacked, attack_val)
                    attacked_sum += attack_val
                # 统计防守方的棋子棋力
                for k in range(guarded_num):
                    guard_val = cc.base_value[relation_list[i][j].guarded[k]]
                    max_guarded = max(max_guarded, guard_val)
                    guarded_sum += guard_val
                # 一、如果攻击方的数量为0，直接记录防守值(因为没被吃子,所以防守的base_value没用，增加防守棋子数量即可)
                if attacked_num == 0:
                    relation_val[now_who] += 5 * guarded_num
                # 二、now_chess被攻击
                else:
                    # 若是now_chess的敌方行动，那么可以直接吃，值就接近真实值；若是now_chess方行动，那么就只是被威胁，被吃的值就小一点
                    multi_val = 5 if turn != now_who else 1  
                    # 如果没有保护
                    if guarded_num == 0:
                        relation_val[now_who] -= multi_val * unit_val
                    # 如果有保护
                    else:
                        # 1.攻击者存在棋力小于被攻击者棋力,对方打算换子(用最小棋力的换)
                        if min_flag != cc.MAX_VAL:
                            relation_val[now_who] -= multi_val * unit_val                   # 被攻击的棋子
                            relation_val[enemy_who] -= multi_val * (min_attacked >> 3)      # 攻击者守卫被吃
                        # 接下来攻击者的棋力最小的都 >= 被攻击者棋力
                        # 2.对方一换二: 若只有一个守卫,攻击方可能会考虑攻击 (当攻击方最小棋力 < 被攻击者棋力+保护者棋力时攻击)
                        elif guarded_num == 1 and attacked_num > 1 and min_attacked < cc.base_value[now_chess.type] + guarded_sum:
                            relation_val[now_who] -= multi_val * unit_val               # 被攻击的棋子
                            relation_val[now_who] -= multi_val * (guarded_sum >> 3)     # 唯一的守卫吃掉攻击者,但也被吃掉
                            relation_val[enemy_who] -= multi_val * (min_attacked >> 3)      # 攻击者损失一个攻击的棋子
                        # 3.对方二换三: 若只有两个守卫,攻击方可能会考虑攻击 (当攻击方最小的两个棋力 < 被攻击者棋力+保护者棋力时攻击)
                        elif guarded_num == 2 and attacked_num == 3 and attacked_sum - max_attacked < cc.base_value[now_chess.type] + guarded_sum:
                            relation_val[now_who] -= multi_val * unit_val               # 被攻击的棋子
                            relation_val[now_who] -= multi_val * (guarded_sum >> 3)     # 两个守卫吃掉攻击者,但也被吃掉
                            relation_val[enemy_who] -= multi_val * ((attacked_sum - max_attacked) >> 3)      # 攻击者损失两个攻击的棋子
                        # 4.对方n换n: 若攻击方的棋子与保护方相同,攻击方可能会考虑攻击 (当攻击方棋力总和 < 被攻击者棋力+(保护者总棋力-保护者最大棋力)时攻击)
                        elif guarded_num == attacked_num and attacked_sum < cc.base_value[now_chess.type] + guarded_sum - max_guarded:
                            relation_val[now_who] -= multi_val * unit_val               # 被攻击的棋子
                            relation_val[now_who] -= multi_val * ((guarded_sum - max_guarded) >> 3)     # 除了最大的守卫之外的守卫都互换了
                            relation_val[enemy_who] -= multi_val * (attacked_sum >> 3)      # 攻击者损失所有攻击棋子
        #------------------返回得分差值-------------------
        # #
        # print('-------------------------')
        # print(base_val[0], pos_val[0], mobile_val[0], relation_val[0])
        # print(base_val[1], pos_val[1], mobile_val[1], relation_val[1])
        # #
        enemy_who = cc.BLACK if who == cc.RED else cc.RED
        who_sum = base_val[who] + pos_val[who] + mobile_val[who] + relation_val[who]
        enemy_sum = base_val[enemy_who] + pos_val[enemy_who] + mobile_val[enemy_who] + relation_val[enemy_who]
        return who_sum - enemy_sum


    # 初始化棋盘棋子的关系表
    def init_relation_list(self):
        relation_list = []
        for i in range(10):
            relation_list.append([])
            for _ in range(9):
                relation_list[i].append(cr.relation_table())
        return relation_list

    # 判断是否可以移动到对应位置(给定要移动到的位置 和 可以移动到的位置)
    def can_move(self, des: tuple, all_actions: list):
        for ac in all_actions:
            if des == ac.to_pos:
                return True
        return False

    # 获取who方所有可移动的action，返回一个列表
    def get_all_action(self, who):
        all_actions = []
        for i in range(10):
            for j in range(9):
                # 没有棋子或者是敌方的棋子
                if self.board[i][j].type == cc.NULL or self.board[i][j].who != who:
                    continue
                all_actions.extend(self.get_chess_action(i, j, who))
        return all_actions
    
    # # 获取一个chess可移动的action，返回一个列表(ignore_friend指无视友方棋子,用来查找所有方向)
    def get_chess_action(self, x, y, who, ignore_friend=False):
        recent_chess = self.board[x][y]
        if recent_chess.type == cc.KING:
            return self.King_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.CHE:
            return self.Che_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.MA:
            return self.Ma_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.PAO:
            return self.Pao_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.XIANG:
            return self.Xiang_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.SHI:
            return self.Shi_move(x, y, who, ignore_friend)
        elif recent_chess.type == cc.ZU:
            return self.Zu_move(x, y, who, ignore_friend)
    
    # 1.KING可移动的位置
    def King_move(self, x, y, who, ignore_friend):
        chess_actions = []
        if who == cc.BLACK:
            # ①可以飞将
            can_fly = False
            for x1 in range(x + 1, 10):
                # 是将就可飞，否则被阻挡不可飞
                if self.board[x1][y].type != cc.NULL:
                    if self.board[x1][y].type == cc.KING:
                        can_fly = True
                    break
            if can_fly:
                chess_actions.append(action((x, y), (x1, y)))
            # 四个方向：未超出范围且位置为空或者可以吃
            # ②向前
            if x + 1 <= 2 and (self.board[x + 1][y].type == cc.NULL or self.board[x + 1][y].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x + 1, y)))
            # ③向后
            if x - 1 >= 0 and (self.board[x - 1][y].type == cc.NULL or self.board[x - 1][y].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x - 1, y)))
            # ④向左(面向红方方向)
            if y + 1 <= 5 and (self.board[x][y + 1].type == cc.NULL or self.board[x][y + 1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x, y + 1)))
            # ⑤向右
            if y - 1 >= 3 and (self.board[x][y - 1].type == cc.NULL or self.board[x][y - 1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x, y - 1)))
        elif who == cc.RED:
            # ①可以飞将
            can_fly = False
            for x1 in range(x - 1, -1, -1):
                # 是将就可飞，否则被阻挡不可飞
                if self.board[x1][y].type != cc.NULL:
                    if self.board[x1][y].type == cc.KING:
                        can_fly = True
                    break
            if can_fly:
                chess_actions.append(action((x, y), (x1, y)))
            # 四个方向：未超出范围且位置为空或者可以吃
            # ②向前
            if x - 1 >= 7 and (self.board[x - 1][y].type == cc.NULL or self.board[x - 1][y].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x - 1, y)))
            # ③向后
            if x + 1 <= 9 and (self.board[x + 1][y].type == cc.NULL or self.board[x + 1][y].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x + 1, y)))
            # ④向左(面向黑方方向)
            if y - 1 >= 3 and (self.board[x][y - 1].type == cc.NULL or self.board[x][y - 1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x, y - 1)))
            # ⑤向右
            if y + 1 <= 5 and (self.board[x][y + 1].type == cc.NULL or self.board[x][y + 1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x, y + 1)))
        return chess_actions

    # 2.CHE可以移动的位置
    def Che_move(self, x, y, who, ignore_friend):
        chess_actions = []
        # 四个方向：未超出范围且位置为空或者可以吃
        if who == cc.BLACK:
            # ①向前
            for x1 in range(x + 1, 10):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x1][y].who == cc.RED or ignore_friend:
                        chess_actions.append(action((x, y), (x1, y)))
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ②向后
            for x1 in range(x - 1, -1, -1):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x1][y].who == cc.RED or ignore_friend:
                        chess_actions.append(action((x, y), (x1, y)))
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ③向左
            for y1 in range(y + 1, 9):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x][y1].who == cc.RED or ignore_friend:
                        chess_actions.append(action((x, y), (x, y1)))
                    break
                chess_actions.append(action((x, y), (x, y1)))
            # ④向右
            for y1 in range(y - 1, -1, -1):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x][y1].who == cc.RED or ignore_friend:
                        chess_actions.append(action((x, y), (x, y1)))
                    break
                chess_actions.append(action((x, y), (x, y1)))
        elif who == cc.RED:
            # ①向前
            for x1 in range(x - 1, -1, -1):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x1][y].who == cc.BLACK or ignore_friend:
                        chess_actions.append(action((x, y), (x1, y)))
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ②向后
            for x1 in range(x + 1, 10):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x1][y].who == cc.BLACK or ignore_friend:
                        chess_actions.append(action((x, y), (x1, y)))
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ③向左
            for y1 in range(y - 1, -1, -1):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x][y1].who == cc.BLACK or ignore_friend:
                        chess_actions.append(action((x, y), (x, y1)))
                    break
                chess_actions.append(action((x, y), (x, y1)))
            # ④向右
            for y1 in range(y + 1, 9):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 自己人就停止向前，敌人就可以吃
                    if self.board[x][y1].who == cc.BLACK or ignore_friend:
                        chess_actions.append(action((x, y), (x, y1)))
                    break
                chess_actions.append(action((x, y), (x, y1)))
        return chess_actions

    # 3.MA可以移动的位置
    def Ma_move(self, x, y, who, ignore_friend):
        chess_actions = []
        # 四个方向，八个位置: 未超出范围 且 不被卡马脚 位置为空或者可以吃
        if who == cc.BLACK:
            # ①前2格
            if x + 2 <= 9 and self.board[x + 1][y].type == cc.NULL:
                # 前左方
                x1, y1 = x + 2, y + 1
                if y1 <= 8 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 前右方
                x1, y1 = x + 2, y - 1
                if y1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ②后2格
            if x - 2 >= 0 and self.board[x - 1][y].type == cc.NULL:
                # 后左方
                x1, y1 = x - 2, y + 1
                if y1 <= 8 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 后右方
                x1, y1 = x - 2, y - 1
                if y1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ③左2格
            if y + 2 <= 8 and self.board[x][y + 1].type == cc.NULL:
                # 左前方
                x1, y1 = x + 1, y + 2
                if x1 <= 9 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 左后方
                x1, y1 = x - 1, y + 2
                if x1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ④右2格
            if y - 2 >= 0 and self.board[x][y - 1].type == cc.NULL:
                # 右前方
                x1, y1 = x + 1, y - 2
                if x1 <= 9 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 右后方
                x1, y1 = x - 1, y - 2
                if x1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
        elif who == cc.RED:
            # ①前2格
            if x - 2 >= 0 and self.board[x - 1][y].type == cc.NULL:
                # 前左方
                x1, y1 = x - 2, y - 1
                if y1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 前右方
                x1, y1 = x - 2, y + 1
                if y1 <= 8 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ②后2格
            if x + 2 <= 9 and self.board[x + 1][y].type == cc.NULL:
                # 后左方
                x1, y1 = x + 2, y - 1
                if y1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 后右方
                x1, y1 = x + 2, y + 1
                if y1 <= 8 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ③左2格
            if y - 2 >= 0 and self.board[x][y - 1].type == cc.NULL:
                # 左前方
                x1, y1 = x - 1, y - 2
                if x1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 左后方
                x1, y1 = x + 1, y - 2
                if x1 <= 9 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
            # ④右2格
            if y + 2 <= 8 and self.board[x][y + 1].type == cc.NULL:
                # 右前方
                x1, y1 = x - 1, y + 2
                if x1 >= 0 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
                # 右后方
                x1, y1 = x + 1, y + 2
                if x1 <= 9 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                    chess_actions.append(action((x, y), (x1, y1)))
        return chess_actions

    # 4.PAO可以移动的方向
    def Pao_move(self, x, y, who, ignore_friend):
        chess_actions = []
        # 四个方向，停在障碍棋子前或者吃掉障碍棋子后
        if who == cc.BLACK:
            # ①向前
            for x1 in range(x + 1, 10):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 判断是否可以吃
                    for x2 in range(x1 + 1, 10):
                        if self.board[x2][y].type != cc.NULL:
                            if self.board[x2][y].who == cc.RED or ignore_friend:
                                chess_actions.append(action((x, y), (x2, y)))
                            break
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ②向后
            for x1 in range(x - 1, -1, -1):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 判断是否可以吃
                    for x2 in range(x1 - 1, -1, -1):
                        if self.board[x2][y].type != cc.NULL:
                            if self.board[x2][y].who == cc.RED or ignore_friend:
                                chess_actions.append(action((x, y), (x2, y)))
                            break
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ③向左
            for y1 in range(y + 1, 9):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 判断是否可以吃
                    for y2 in range(y1 + 1, 9):
                        if self.board[x][y2].type != cc.NULL:
                            if self.board[x][y2].who == cc.RED or ignore_friend:
                                chess_actions.append(action((x, y), (x, y2)))
                            break
                    break
                chess_actions.append(action((x, y), (x, y1)))
            # ④向右
            for y1 in range(y - 1, -1, -1):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 判断是否可以吃
                    for y2 in range(y1 - 1, -1, -1):
                        if self.board[x][y2].type != cc.NULL:
                            if self.board[x][y2].who == cc.RED or ignore_friend:
                                chess_actions.append(action((x, y), (x, y2)))
                            break
                    break
                chess_actions.append(action((x, y), (x, y1)))
        elif who == cc.RED:
            # ①向前
            for x1 in range(x - 1, -1, -1):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 判断是否可以吃
                    for x2 in range(x1 - 1, -1, -1):
                        if self.board[x2][y].type != cc.NULL:
                            if self.board[x2][y].who == cc.BLACK or ignore_friend:
                                chess_actions.append(action((x, y), (x2, y)))
                            break
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ②向后
            for x1 in range(x + 1, 10):
                # 有棋子挡住
                if self.board[x1][y].type != cc.NULL:
                    # 判断是否可以吃
                    for x2 in range(x1 + 1, 10):
                        if self.board[x2][y].type != cc.NULL:
                            if self.board[x2][y].who == cc.BLACK or ignore_friend:
                                chess_actions.append(action((x, y), (x2, y)))
                            break
                    break
                chess_actions.append(action((x, y), (x1, y)))
            # ③向左
            for y1 in range(y - 1, -1, -1):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 判断是否可以吃
                    for y2 in range(y1 - 1, -1, -1):
                        if self.board[x][y2].type != cc.NULL:
                            if self.board[x][y2].who == cc.BLACK or ignore_friend:
                                chess_actions.append(action((x, y), (x, y2)))
                            break
                    break
                chess_actions.append(action((x, y), (x, y1)))
            # ④向右
            for y1 in range(y + 1, 9):
                # 有棋子挡住
                if self.board[x][y1].type != cc.NULL:
                    # 判断是否可以吃
                    for y2 in range(y1 + 1, 9):
                        if self.board[x][y2].type != cc.NULL:
                            if self.board[x][y2].who == cc.BLACK or ignore_friend:
                                chess_actions.append(action((x, y), (x, y2)))
                            break
                    break
                chess_actions.append(action((x, y), (x, y1)))
        return chess_actions

    # 5.XIANG可以移动的位置
    def Xiang_move(self, x, y, who, ignore_friend):
        chess_actions = []
        # 四个方向斜着走（田字眼被堵不可走，不能过河）
        if who == cc.BLACK:
            # ①左前方
            x1, y1 = x + 2, y + 2
            # 不超过边界, 不过河, 且不被堵
            if x1 <= 4 and y1 <= 8 and self.board[x + 1][y + 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ②右前方
            x1, y1 = x + 2, y - 2
            # 不超过边界, 不过河, 且不被堵
            if x1 <= 4 and y1 >= 0 and self.board[x + 1][y - 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ③左后方
            x1, y1 = x - 2, y + 2
            # 不超过边界, 不过河, 且不被堵
            if x1 >= 0 and y1 <= 8 and self.board[x - 1][y + 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ④右后方
            x1, y1 = x - 2, y - 2
            # 不超过边界, 不过河, 且不被堵
            if x1 >= 0 and y1 >= 0 and self.board[x - 1][y - 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
        elif who == cc.RED:
            # ①左前方
            x1, y1 = x - 2, y - 2
            # 不超过边界, 不过河, 且不被堵
            if x1 >= 5 and y1 >= 0 and self.board[x - 1][y - 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ②右前方
            x1, y1 = x - 2, y + 2
            # 不超过边界, 不过河, 且不被堵
            if x1 >= 5 and y1 <= 8 and self.board[x - 1][y + 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ③左后方
            x1, y1 = x + 2, y - 2
            # 不超过边界, 不过河, 且不被堵
            if x1 <= 9 and y1 >= 0 and self.board[x + 1][y - 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
            # ④右后方
            x1, y1 = x + 2, y + 2
            # 不超过边界, 不过河, 且不被堵
            if x1 <= 9 and y1 <= 8 and self.board[x + 1][y + 1].type == cc.NULL:
                if self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend:
                    chess_actions.append(action((x, y), (x1, y1)))
        return chess_actions

    # 6.SHI可移动的位置
    def Shi_move(self, x, y, who, ignore_friend):
        chess_actions = []
        # 四个方向斜着走，不超出限制位置
        if who == cc.BLACK:
            # ①左前方
            x1, y1 = x + 1, y + 1
            if x1 <= 2 and y1 <= 5 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ②右前方
            x1, y1 = x + 1, y - 1
            if x1 <= 2 and y1 >= 3 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ③左后方
            x1, y1 = x - 1, y + 1
            if x1 >= 0 and y1 <= 5 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ④右后方
            x1, y1 = x - 1, y - 1
            if x1 >= 0 and y1 >= 3 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
        elif who == cc.RED:
            # ①左前方
            x1, y1 = x - 1, y - 1
            if x1 >= 7 and y1 >= 3 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ②右前方
            x1, y1 = x - 1, y + 1
            if x1 >= 7 and y1 <= 5 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ③左后方
            x1, y1 = x + 1, y - 1
            if x1 <= 9 and y1 >= 3 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
            # ④右后方
            x1, y1 = x + 1, y + 1
            if x1 <= 9 and y1 <= 5 and (self.board[x1][y1].type == cc.NULL or self.board[x1][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x1, y1)))
        return chess_actions

    # 7.ZU可以移动的位置
    def Zu_move(self, x, y, who, ignore_friend):
        chess_actions = []
        if who == cc.BLACK:
            # 过河之前只能往前，过河之后可以往前或者左右
            # ①往前
            x1 = x + 1
            if x1 <= 9 and (self.board[x1][y].type == cc.NULL or self.board[x1][y].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x1, y)))
            # ②往左
            y1 = y + 1
            if x >= 5 and y1 <= 8 and (self.board[x][y1].type == cc.NULL or self.board[x][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x, y1)))
            # ③往右
            y1 = y - 1
            if x >= 5 and y1 >= 0 and (self.board[x][y1].type == cc.NULL or self.board[x][y1].who == cc.RED or ignore_friend):
                chess_actions.append(action((x, y), (x, y1)))
        elif who == cc.RED:
            # ①往前
            x1 = x - 1
            if x1 >= 0 and (self.board[x1][y].type == cc.NULL or self.board[x1][y].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x1, y)))
            # ②往左
            y1 = y - 1
            if x <= 4 and y1 >= 0 and (self.board[x][y1].type == cc.NULL or self.board[x][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x, y1)))
            # ③往右
            y1 = y + 1
            if x <= 4 and y1 <= 8 and (self.board[x][y1].type == cc.NULL or self.board[x][y1].who == cc.BLACK or ignore_friend):
                chess_actions.append(action((x, y), (x, y1)))
        return chess_actions



# 初始化构建chess_board的函数
def init_board():
    board = []
    for i in range(len(cc.init_board)):
        board_row = []
        for j in range(len(cc.init_board[i])):
            if i <= 4:
                board_row.append(chess(cc.init_board[i][j], cc.BLACK))
            elif i <= 9:
                board_row.append(chess(cc.init_board[i][j], cc.RED))
        board.append(board_row)
    return board


def test_utility():
    cb = chess_board(init_board())
    cb.print_board()
    print(cb.utility(cc.BLACK, cc.BLACK))
    score, _, best_action, _, _= cb.alpha_beta(2, cc.BLACK, False)
    print(score)
    print("(%d, %d)->(%d, %d)" % (best_action.from_pos[0], best_action.from_pos[1], best_action.to_pos[0], best_action.to_pos[1]))


if __name__ == '__main__':
    test_utility()
    # cb = chess_board(init_board())
    # cb.print_board()
    # cb.get_all_action(cc.BLACK)
    # print()
    # cb.get_all_action(cc.RED)

    # all_actions = cb.get_all_action(cc.BLACK)
    # print("length of all actions: %d" % (len(all_actions)))
    # for at in all_actions:
    #     print(at, end=' ')
    # print()
    # all_actions = cb.get_all_action(cc.RED)
    # print("length of all actions: %d" % (len(all_actions)))
    # for at in all_actions:
    #     print(at, end=' ')
    # print()