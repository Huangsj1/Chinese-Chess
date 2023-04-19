import pygame
import sys
import time
import chess_const as cc
from chess_board import *
import show
import repeat as rp
import zobrist_code as zc

COMPUTER = 0
PEOPLE = 1

class game:
    # p1是红方，p2是黑方
    def __init__(self):
        # board是一个chess_board类型
        self.board: chess_board = chess_board(init_board())
        self.max_depth = cc.MAX_DEPTH_HARD
        # 用来展示图片的对象
        self.show_image: show.ImageShow = None

        # 电脑/人
        self.player1 = PEOPLE
        self.player2 = PEOPLE
        # 人是否在托管中(等效于电脑)(按托管按钮时playe变成COMPUTER,按取消托管时变成PEOPLE)
        self.host1 = False
        self.host2 = False
        # 轮到哪一方走（红方/黑方）根据颜色判断那一个player走
        self.turn = cc.RED      # 红方先走

        # 是否结束游戏
        self.over = False

        # 是否选中了棋子以及棋子坐标
        self.select = False
        self.select_pos = None
        # 如果选中了棋子就缓存可以走的位置
        self.select_action = None

        # 是否还在菜单页
        self.in_menu = True
        # 与电脑PK时菜单页的选项
        self.to_choose = False
        self.level = None        # 游戏难度
        self.side = None         # 玩家选择哪一方

        # 与电脑PK时电脑走完了的信息
        self.who = None     # 电脑属于哪一方(每走一步都重新设置)
        self.score = 0
        self.cost_time = 0
        self.last_action = None
        self.length = None
        self.cnt = None

        # 记录下走的步骤,使得可以悔棋(对方没下时/对方下了 都可以悔棋,但只能悔棋一次)
        self.p1_last_action = None
        self.p1_last_chess = None
        self.p2_last_action = None
        self.p2_last_chess = None

        # 记录最近走的棋局,防止电脑一直走相同的步骤
        self.red_queue = rp.RepeatQueue()
        self.black_queue = rp.RepeatQueue()

    # 初始化pygame
    def initialize(self):
        pygame.init()
        # 显示界面的相框(宽，高)
        screen = pygame.display.set_mode(show.bg_size)
        # 显示标题
        pygame.display.set_caption("中国象棋 : )")
        self.show_image = show.ImageShow(screen)
    
    # ------------------------------------页面菜单------------------------------------------------------

    # 进入与电脑PK的各种选项(红/黑方、难度)(供按钮使用)
    def goto_choose(self):
        print('goto_choose')
        self.to_choose = True

    # 设置可以进入游戏(供按钮使用)
    def goto_game(self):
        self.in_menu = False            # 退出菜单
        if self.side == cc.RED:         # 设置哪一方是人
            self.player2 = COMPUTER
            print("你选择了 红方")
        elif self.side == cc.BLACK:
            self.player1 = COMPUTER
            print("你选择了 黑方")
        print('开始游戏')  

    # 选择简单难度(供按钮使用)
    def choose_level1(self):
        print("选择easy")
        self.level = cc.EASY
        self.max_depth = cc.MAX_DEPTH_EASY
    
    # 选择中等难度(供按钮使用)
    def choose_level2(self):
        print("选择middle")
        self.level = cc.MIDDLE
        self.max_depth = cc.MAX_DEPTH_MIDDLE

    # 选择困难难度(供按钮使用)
    def choose_level3(self):
        print("选择hard")
        self.level = cc.HARD
        self.max_depth = cc.MAX_DEPTH_HARD

    # 选择黑方(供按钮使用)
    def choose_side_black(self):
        print("选择黑色棋子")
        self.side = cc.BLACK

    # 选择红方(供按钮使用)
    def choose_side_red(self):
        print("选择红色棋子")
        self.side = cc.RED

    # ------------------------------------悔棋------------------------------------------------------
    # 黑色方想要悔棋(供按钮使用)    
    def go_back_black(self):
        if self.p2_last_action != None:     # 如果可以悔棋(有上一步储存)
            if self.turn == cc.BLACK:      # 如果现在轮到黑方走,那么要恢复红方和黑方的上一步
                # 先恢复红色
                from_x, from_y = self.p1_last_action.from_pos[0], self.p1_last_action.from_pos[1]
                to_x, to_y = self.p1_last_action.to_pos[0], self.p1_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p1_last_chess
                self.p1_last_action, self.p1_last_chess = None, None     
                self.board.zval = self.red_queue.pop()        # 弹出上一个棋局 
                # 再恢复黑色
                from_x, from_y = self.p2_last_action.from_pos[0], self.p2_last_action.from_pos[1]
                to_x, to_y = self.p2_last_action.to_pos[0], self.p2_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p2_last_chess
                self.p2_last_action, self.p2_last_chess = None, None
                self.board.zval = self.black_queue.pop()        # 弹出上一个棋局 
            elif self.turn == cc.RED:      # 如果现在轮到红方走,那么要恢复黑方的上一步,同时转换回黑方走
                from_x, from_y = self.p2_last_action.from_pos[0], self.p2_last_action.from_pos[1]
                to_x, to_y = self.p2_last_action.to_pos[0], self.p2_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p2_last_chess
                self.p2_last_action, self.p2_last_chess = None, None
                self.turn = cc.BLACK    # 转回黑方走
                self.board.zval = self.black_queue.pop()        # 弹出上一个棋局 
    
    # 红色方想要悔棋(供按钮使用)
    def go_back_red(self):
        if self.p1_last_action != None:     # 如果可以悔棋(有上一步储存)
            if self.turn == cc.RED:      # 如果现在轮到红方走,那么要恢复黑方和红方的上一步
                # 先恢复黑色
                from_x, from_y = self.p2_last_action.from_pos[0], self.p2_last_action.from_pos[1]
                to_x, to_y = self.p2_last_action.to_pos[0], self.p2_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p2_last_chess
                self.p2_last_action, self.p2_last_chess = None, None     
                self.board.zval = self.black_queue.pop()        # 弹出上一个棋局  
                # 再恢复红色
                from_x, from_y = self.p1_last_action.from_pos[0], self.p1_last_action.from_pos[1]
                to_x, to_y = self.p1_last_action.to_pos[0], self.p1_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p1_last_chess
                self.p1_last_action, self.p1_last_chess = None, None
                self.board.zval = self.red_queue.pop()        # 弹出上一个棋局 
            elif self.turn == cc.BLACK:      # 如果现在轮到黑方走,那么要恢复红方的上一步,同时转换回红方走
                from_x, from_y = self.p1_last_action.from_pos[0], self.p1_last_action.from_pos[1]
                to_x, to_y = self.p1_last_action.to_pos[0], self.p1_last_action.to_pos[1]
                self.board.board[from_x][from_y] = self.board.board[to_x][to_y]
                self.board.board[to_x][to_y] = self.p1_last_chess
                self.p1_last_action, self.p1_last_chess = None, None
                self.turn = cc.RED    # 转回红方走
                self.board.zval = self.red_queue.pop()        # 弹出上一个棋局 

    # ------------------------------------托管------------------------------------------------------
    def red_to_computer(self):
        self.player1 = COMPUTER
        self.host1 = True
    
    def red_to_people(self):
        self.player1 = PEOPLE
        self.host1 = False

    def black_to_computer(self):
        self.player2 = COMPUTER
        self.host2 = True

    def black_to_people(self):
        self.player2 = PEOPLE
        self.host2 = False

    # ----------------------------------记录下一个局面----------------------------------------------
    def record_next(self, from_x, from_y, to_x, to_y, now_who):
        self.board.zval = self.board.zobrist.next_value(self.board.zval, from_x, from_y, to_x, to_y, \
                                            self.board.board[from_x][from_y], self.board.board[to_x][to_y])
        if now_who == cc.BLACK:
            self.black_queue.push(self.board.zval)
        elif now_who == cc.RED:
            self.red_queue.push(self.board.zval)

    # -------------------------------------pygame开始游戏---------------------------------------
    def start_game(self):
        self.initialize()

        self.draw_image()
        pygame.display.update()
        time.sleep(0.5)

        while True:
            # 如果还处在menu中
            if self.in_menu == True:
                self.get_event()
                self.draw_image()
                pygame.display.update()
                continue

            # 电脑是否要走
            self.computer_play()

            # 获取事件信息（退出/人走）
            self.get_event()

            # 根据不同的情况绘制不同的图片(menu1, menu2, start)
            self.draw_image()

            self.delay()

            time.sleep(0.1)

            # 一方获胜
            if self.board.win(cc.RED if self.turn == cc.BLACK else cc.BLACK):
                print("Game Over! %s win" % (cc.COLOR_MAP[cc.RED if self.turn == cc.BLACK else cc.BLACK]))
                self.over = True
                self.draw_image()
                pygame.display.update()
                time.sleep(3)
                break

            # 显示这个screen的内容
            pygame.display.update()

    # 当双方都为电脑的时候,速度过快,需要延时久一些; 否则就延迟一小会
    def delay(self):
        if self.player1 == COMPUTER and self.player2 == COMPUTER:
            if self.max_depth == cc.MAX_DEPTH_EASY:
                time.sleep(0.3)
            elif self.max_depth == cc.MAX_DEPTH_MIDDLE:
                time.sleep(0.3)
        time.sleep(0.1)

    # 切换行动方
    def switch_player(self):
        self.turn = cc.RED if self.turn == cc.BLACK else cc.BLACK

    # 轮到哪一方走(人/电脑)
    def whose_turn(self):
        return self.player1 if self.turn == cc.RED else self.player2

    # 电脑判断是否走
    def computer_play(self):
        # 轮到电脑
        if self.whose_turn() == COMPUTER:
            self.who = self.turn
            self.score, self.cost_time, self.last_action, self.length, self.cnt = \
                self.board.alpha_beta(self.max_depth, self.turn, True, self.red_queue if self.turn == cc.RED else self.black_queue)
            from_x, from_y = self.last_action.from_pos[0], self.last_action.from_pos[1]
            to_x, to_y = self.last_action.to_pos[0], self.last_action.to_pos[1]
            # 在move_to之前先记录新的棋盘的值
            self.record_next(from_x, from_y, to_x, to_y, self.turn)
            to_chess = self.board.move_to((from_x, from_y), (to_x, to_y))
            #print("电脑(%s)走的步骤: (%d, %d)->(%d, %d), 得分：%d" % (cc.COLOR_MAP[self.turn], from_x, from_y, to_x, to_y, self.score))
            # 电脑走完，记录走的步骤
            if self.turn == cc.RED:
                self.p1_last_action = self.last_action
                self.p1_last_chess = to_chess
            elif self.turn == cc.BLACK:
                self.p2_last_action = self.last_action
                self.p2_last_chess = to_chess
            # 切换到另一方（如果是人就切换到人，否则还是电脑）
            self.switch_player()

    # 获取并处理事件
    def get_event(self):
        # 事件检测（点击了键盘、鼠标等）
        for event in pygame.event.get():
            # 退出程序
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 点击鼠标
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 如果处在menu中就看是否点击了开始
                if self.in_menu:
                    # 如果还处在菜单第一个界面
                    if self.to_choose == False:
                        self.show_image.button_computer.handle_event(self.goto_choose)
                        self.show_image.button_people.handle_event(self.goto_game)      # 第一个页面点击玩家PK可以直接开始
                    # 如果选择了与电脑PK，进入菜单第二个选择界面
                    else:
                        self.show_image.button_level1.handle_event(self.choose_level1)
                        self.show_image.button_level2.handle_event(self.choose_level2)
                        self.show_image.button_level3.handle_event(self.choose_level3)
                        self.show_image.button_side1.handle_event(self.choose_side_black)
                        self.show_image.button_side2.handle_event(self.choose_side_red)
                        if self.level != None and self.side != None:        # 在第二个界面中选择了难度和颜色后才可以开始
                            self.show_image.button_start.handle_event(self.goto_game)
                    continue

                # 是否要处理悔棋(注意这里不要用elif,否则就不会调用button_black_black的handle)
                if self.player1 == PEOPLE:
                    self.show_image.button_back_red.handle_event(self.go_back_red)
                if self.player2 == PEOPLE:
                    self.show_image.button_back_black.handle_event(self.go_back_black)

                # 处理托管
                if self.player1 == PEOPLE:                                            # 红方托管
                    self.show_image.button_host_red.handle_event(self.red_to_computer)
                elif self.player1 == COMPUTER and self.host1 == True:                 # 红方取消托管
                    self.show_image.button_unhost_red.handle_event(self.red_to_people)
                if self.player2 == PEOPLE:                                            # 黑方托管
                    self.show_image.button_host_black.handle_event(self.black_to_computer)
                elif self.player2 == COMPUTER and self.host2 == True:                 # 黑方取消托管
                    self.show_image.button_unhost_black.handle_event(self.black_to_people)


                # 先判断是否轮到玩家行动，否则点击无效
                if self.whose_turn() == PEOPLE:
                    pos = pygame.mouse.get_pos()
                    mouse_pos = (pos[0], pos[1])
                    # 判断是否可以移动
                    # 鼠标点击的点到对应点的中心坐标的距离相差不超过(56*(3/8),即21)(central_pos为chess_board.board上的坐标)
                    central_pos = (abs(pos[0] - show.left_top_pos[0]) // show.width, abs(pos[1] - show.left_top_pos[1]) // show.width)
                    if central_pos[0] >= 0 and central_pos[0] <= 8 and central_pos[1] >= 0 and central_pos[1] <= 9 \
                    and abs(mouse_pos[0] - (show.left_top_central_pos[0] + central_pos[0] * show.width)) <= (show.width* 3 / 8) \
                    and abs(mouse_pos[1] - (show.left_top_central_pos[1] + central_pos[1] * show.width)) <= (show.width* 3 / 8):
                        # 转换成数组的坐标
                        central_pos = self.change_pos(central_pos)
                        select_chess = self.board.board[central_pos[0]][central_pos[1]]
                        # 1&2.点击的是空格/敌方棋子 -> 判断是否已经选择棋子 -> 判断是否可以放下 -> move_to
                        if select_chess.type == cc.NULL or select_chess.who != self.turn:
                            if self.select and self.board.can_move(central_pos, self.select_action):
                                # print("Peopel: (%d, %d)->(%d, %d)" % (self.select_pos[0], self.select_pos[1], central_pos[0], central_pos[1]))
                                to_chess = self.board.move_to(self.select_pos, central_pos)
                                # 记录走的步骤
                                if self.turn == cc.RED:
                                    self.p1_last_action = action(self.select_pos, central_pos)
                                    self.p1_last_chess = to_chess
                                elif self.turn == cc.BLACK:
                                    self.p2_last_action = action(self.select_pos, central_pos)
                                    self.p2_last_chess = to_chess
                                self.record_next(self.select_pos[0], self.select_pos[1], central_pos[0], central_pos[1], self.turn)
                                self.switch_player()
                            # 如果没选择/选择了但不可以放下 -> 取消选择
                            self.select = False
                        # 3.点击的是己方的棋子 -> 选中该棋子（并且保存可以走的路径）
                        elif select_chess.who == self.turn:
                            self.select, self.select_pos = True, central_pos
                            self.select_action = self.board.get_chess_action(central_pos[0], central_pos[1], self.turn)

    # 将图像显示坐标改成位置坐标
    def change_pos(self, image_pos: tuple):
        return (image_pos[1], image_pos[0])

    # 显示图像
    def draw_image(self):
        # 显示背景
        self.show_image.show_bg()

        # 1.处在menu中选择
        if self.in_menu:
            if self.to_choose:      # 选择菜单页
                self.show_image.show_menu2()
            else:                   # 初始菜单页
                self.show_image.show_menu1()
        # 2.开始游戏
        else:
            # 显示棋盘
            self.show_image.show_chessboard()
            # 显示棋子
            self.show_image.show_chess(self.board.board)
            # 显示可以走的位置
            if self.select:
                self.show_image.show_action(self.select_action)
            # 显示轮到谁进攻
            self.show_image.show_who_turn(self.turn)
            # 如果是电脑走完了就显示电脑走的信息
            if self.who != None:
                self.show_image.show_score(self.who, self.last_action, self.length, self.cnt, self.cost_time, self.score)
            # 显示悔棋的图片
            self.show_image.show_back(self.player2 == PEOPLE, self.player1 == PEOPLE)
            # 显示托管的图片
            people_red = True if self.player1 == PEOPLE or self.host1 == True else False
            people_black = True if self.player2 == PEOPLE or self.host2 == True else False
            self.show_image.show_host(people_black, people_red, self.host2, self.host1)

            # 如果胜利
            if self.over:
                self.show_image.show_win(cc.BLACK if self.turn == cc.RED else cc.RED)


if __name__ == "__main__":
    my_game = game()
    my_game.start_game()