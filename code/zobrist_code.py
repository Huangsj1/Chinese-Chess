'''
Zobrist效验码(用于记录棋局)
将棋局转换成一串数字: 不同棋子在不同位置有不同的值,将他们异或起来得到棋局值
'''

import random
import chess_board as cb
import chess_const as cc

class Zobrist:
    def __init__(self):
        self.value_table = []
        self.MinVal = 0
        self.MaxVal = 0xffffffffffffffff    # 64位
    
    # 初始化随机数表14*10*9(有2种颜色,7种棋子)
    def initialize(self):
        for _ in range(14):
            t = []
            for _ in range(10):
                row = []
                for _ in range(9):
                    row.append(random.randint(self.MinVal, self.MaxVal))
                t.append(row)
            self.value_table.append(t)
    
    # 返回棋盘的值(只用来返回初始化的棋盘的值)
    def init_value(self, board: list):
        ans = 0
        for i in range(10):
            for j in range(9):
                chess = board[i][j]
                if chess.type != cc.NULL:
                    ans ^= self.value_table[chess.who * 7 + (chess.type - 1)][i][j]
        return ans
    
    # 棋子走了一步,根据异或性质可以很快得到走后的棋盘的值
    def next_value(self, val, from_x, from_y, to_x, to_y, from_chess, to_chess):
        # 棋子原位置的值 和 去的位置的值
        from_val = self.value_table[from_chess.who * 7 + (from_chess.type - 1)][from_x][from_y]
        to_val = self.value_table[from_chess.who * 7 + (from_chess.type - 1)][to_x][to_y]
        # 棋子去的位置原来可能有棋子
        enemy_val = 0 if to_chess.type == cc.NULL else self.value_table[to_chess.who * 7 + (to_chess.type - 1)][to_x][to_y]
        return val ^ from_val ^ to_val ^ enemy_val

            
if __name__ == "__main__":
    cboard = cb.chess_board(cb.init_board())
    zb = Zobrist()
    zb.initialize()
    iv = zb.init_value(cboard)
    print(hex(iv))
    nv = zb.next_value(iv, 7, 1, 0, 1, cboard.board[7][1], cboard.board[0][1])
    print(hex(nv))
    from_ =zb.value_table[(cc.RED) * 7 + cc.PAO - 1][7][1]
    to_ = zb.value_table[(cc.RED) * 7 + cc.PAO - 1][0][1]
    ene_ = zb.value_table[(cc.BLACK) * 7 + cc.MA - 1][0][1]
    print(hex(from_))
    print(hex(to_))
    print(hex(ene_))
    print(hex(iv ^ from_ ^ to_ ^ ene_))
    