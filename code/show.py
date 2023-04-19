'''
包含了按钮类以及如何展示界面
'''

import time
import pygame
import sys
import chess_const as cc
import chess_board as cb
import button


# 图像的路径及名称
image_path = "images/"
image_menu_name = "menu.png"
image_bg_name = "bg.jpg"
image_chessboard_name = "chessboard.png"
image_chess_name = [
    ["", "b_j.png", "b_c.png", "b_m.png", "b_p.png", "b_x.png", "b_s.png", "b_z.png"],
    ["", "r_j.png", "r_c.png", "r_m.png", "r_p.png", "r_x.png", "r_s.png", "r_z.png"],
]
image_action = "r_box.png"

# 背景边框的长宽
bg_size = (800, 700)

# 字体(楷体)
font_name = "KaiTi"

# 棋子显示的相对坐标(左上角坐标和棋子间宽度)
left_top_pos = (50, 50)     # 棋盘左上角坐标
left_top_central_pos = (72, 72)   # 棋盘左上角顶点中心位置
width = 56


# 显示各种图像(bg、chessboard、chess)
class ImageShow:
    def __init__(self, screen):
        self.screen = screen
        # 初始页面菜单
        # 背景图片
        self.background_img = pygame.image.load(image_path + image_bg_name)
        self.menu_img = pygame.image.load(image_path + image_menu_name)
        # 玩家间PK还是与电脑PK
        self.button_people = button.ButtonText('玩家PK', button.Color.BLACK, font_name, 30)
        self.button_computer = button.ButtonText('电脑PK', button.Color.BLACK, font_name, 30)
        # 与电脑PK的话就要选择 难度、颜色、开始
        self.button_level1 = button.ButtonText('easy', button.Color.WHITE, font_name, 24)
        self.button_level2 = button.ButtonText('middle', button.Color.BLACK, font_name, 24)
        self.button_level3 = button.ButtonText('hard', button.Color.RED, font_name, 24)
        self.button_side1 = button.ButtonText('黑方', button.Color.BLACK, font_name, 24)
        self.button_side2 = button.ButtonText('红方', button.Color.RED, font_name, 24)
        self.button_start = button.ButtonText('开始', button.Color.YELLOW, font_name, 30)

        # 按钮背景
        self.button_bg_big = button.ColorSurface(button.Color.MY_BROWN, 100, 40)
        self.button_bg_small = button.ColorSurface(button.Color.MY_BROWN, 74, 25)

        # 游戏开始后的界面
        # 棋盘图片
        self.chessboard_img = pygame.image.load(image_path + image_chessboard_name)
        # 棋子图片
        # 先加载所有的pygame.image到一个列表里，再输出
        self.chess_img = []
        for i in range(2):
            row = []
            for j in range(8):
                if j == 0:
                    row.append("")
                else:
                    row.append(pygame.image.load(image_path + image_chess_name[i][j]))
            self.chess_img.append(row)
        # 棋子可以走的地方的图片
        self.action_img = pygame.image.load(image_path + image_action)
        
        # 输出轮到哪一方
        self.black_turn = button.Text('黑方', button.Color.BLACK, font_name, 50)
        self.red_turn = button.Text('红方', button.Color.RED, font_name, 50)

        # 电脑计算的信息背景框
        self.compute_info_bg = button.ColorSurface(button.Color.MY_QING, 186, 250)
        self.compute_info = button.Text('电脑计算信息', button.Color.BLACK, font_name, 12)

        # 悔棋边框
        self.button_back_bg = button.ColorSurface(button.Color.MY_WHITE_BLUE, 74, 25)
        self.button_back_black = button.ButtonText('悔棋', button.Color.BLACK, font_name, 24)
        self.button_back_red = button.ButtonText('悔棋', button.Color.RED, font_name, 24)

        # 托管(要托管/取消托管)
        self.button_host_bg = button.ColorSurface(button.Color.MY_WHITE_GREEN, 138, 30)
        self.button_unhost_bg = button.ColorSurface(button.Color.MY_DARK_GREEN, 138, 30)
        self.button_host_black = button.ButtonText('托管', button.Color.BLACK, font_name, 30)
        self.button_unhost_black = button.ButtonText('取消托管', button.Color.BLACK, font_name, 30)
        self.button_host_red = button.ButtonText('托管', button.Color.RED, font_name, 30)
        self.button_unhost_red = button.ButtonText('取消托管', button.Color.RED, font_name, 30)

        # 胜利
        self.win_red = button.Text('红方胜利', button.Color.RED, font_name, 100)
        self.win_black = button.Text('黑方胜利', button.Color.BLACK, font_name, 100)

    # 显示游戏背景
    def show_bg(self):    
        self.screen.blit(self.background_img, (0, 0))   
        self.screen.blit(self.background_img, (400, 0))

    # 显示菜单栏1
    def show_menu1(self):
        self.screen.blit(self.menu_img, (242, 100))
        self.button_bg_big.draw(self.screen, 390, 330)
        self.button_bg_big.draw(self.screen, 390, 400)
        self.button_computer.draw(self.screen, 390, 330)
        self.button_people.draw(self.screen, 390, 400)

    # 显示菜单栏2
    def show_menu2(self):
        self.screen.blit(self.menu_img, (242, 100))
        self.button_bg_big.draw(self.screen, 390, 310)
        self.button_computer.draw(self.screen, 390, 310)
        # 绘制难度
        self.button_bg_small.draw(self.screen, 300, 380)
        self.button_level1.draw(self.screen, 300, 380)
        self.button_bg_small.draw(self.screen, 390, 380)
        self.button_level2.draw(self.screen, 390, 380)
        self.button_bg_small.draw(self.screen, 480, 380)
        self.button_level3.draw(self.screen, 480, 380)
        # 绘制颜色选择
        self.button_bg_small.draw(self.screen, 350, 420)
        self.button_side1.draw(self.screen, 350, 420)
        self.button_bg_small.draw(self.screen, 450, 420)
        self.button_side2.draw(self.screen, 450, 420)
        # 绘制开始按钮
        self.button_bg_big.draw(self.screen, 390, 470)
        self.button_start.draw(self.screen, 390, 470)

    # 显示棋盘
    def show_chessboard(self):
        self.screen.blit(self.chessboard_img, (50, 50))

    # 显示棋盘的所有棋子（传入一个chess_board.board）
    def show_chess(self, board: list):
        # 显示棋盘
        for i in range(10):
            for j in range(9):
                # 空棋盘，跳过
                if board[i][j].type == cc.NULL:
                    continue
                self.screen.blit(self.chess_img[board[i][j].who][board[i][j].type],
                            (left_top_pos[0] + j * width, left_top_pos[1] + i * width))
    
    # 显示所有可以走的位置
    def show_action(self, all_actions: list):
        for ac in all_actions:
            self.screen.blit(self.action_img, (left_top_pos[0] + ac.to_pos[1] * width, left_top_pos[1] + ac.to_pos[0] * width))

    # 显示轮到哪一方走
    def show_who_turn(self, turn):
        if turn == cc.BLACK:
            self.black_turn.draw(self.screen, bg_size[0] - 100, 160)
        elif turn == cc.RED:
            self.red_turn.draw(self.screen, bg_size[0] - 100, bg_size[1] - 190)

    # 显示电脑行动(哪一方)的得分
    def show_score(self, who, action: cb.action, length: list, cnt: list, time: float, score: int):
        # 绘制背景框
        self.compute_info_bg.draw(self.screen, bg_size[0] - 100, 350)
        # 绘制所有内容
        start_pos = (bg_size[0] - 100, 240)
        dy = 16
        self.compute_info.change_text("电脑(%s)的步骤: (%d, %d)->(%d, %d)" % \
                                      (cc.COLOR_MAP[who], action.from_pos[0], action.from_pos[1], action.to_pos[0], action.to_pos[1]))
        self.compute_info.draw(self.screen, start_pos[0], start_pos[1])
        self.compute_info.change_text("时间: %6fs    得分: %d" % (time, score))
        self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + dy)
        self.compute_info.change_text("-" * 30)
        self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + 2 * dy)
        for i in range(1, len(length)):
            self.compute_info.change_text("第 %d 层共有 %d 个节点" % (i + 1, length[i]))
            self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + (2 + i) * dy)
        self.compute_info.change_text("-" * 30)
        self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + (2 + len(length)) * dy)
        for i in range(1, len(cnt)):
            self.compute_info.change_text("第 %d 层共搜索了 %d 个节点" % (i + 1, cnt[i]))
            self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + (2 + len(length) + i) * dy)
        self.compute_info.change_text("-" * 30)
        self.compute_info.draw(self.screen, start_pos[0], start_pos[1] + (2 + len(length) + len(cnt)) * dy)
    
    # 显示悔棋按钮
    def show_back(self, black=False, red=False):
        if black:
            self.button_back_bg.draw(self.screen, bg_size[0] - 100, 110)
            self.button_back_black.draw(self.screen, bg_size[0] - 100, 110)
        if red:
            self.button_back_bg.draw(self.screen, bg_size[0] - 100, bg_size[1] - 140)
            self.button_back_red.draw(self.screen, bg_size[0] - 100, bg_size[1] - 140)
        
    # 显示托管(people是否是玩家,black/red是否是托管中)
    def show_host(self, people_black=False, people_red=False, black_host=False, red_host=False):
        if people_black:
            if black_host:
                self.button_unhost_bg.draw(self.screen, bg_size[0] - 100, 70)
                self.button_unhost_black.draw(self.screen, bg_size[0] - 100, 70)
            else:
                self.button_host_bg.draw(self.screen, bg_size[0] - 100, 70)
                self.button_host_black.draw(self.screen, bg_size[0] - 100, 70)
        if people_red:
            if red_host:
                self.button_unhost_bg.draw(self.screen, bg_size[0] - 100, bg_size[1] - 100)
                self.button_unhost_red.draw(self.screen, bg_size[0] - 100, bg_size[1] - 100)
            else:
                self.button_host_bg.draw(self.screen, bg_size[0] - 100, bg_size[1] - 100)
                self.button_host_red.draw(self.screen, bg_size[0] - 100, bg_size[1] - 100)
            
        
    # 显示胜利
    def show_win(self, who):
        if who == cc.BLACK:
            self.win_black.draw(self.screen, bg_size[0] / 2, bg_size[1] / 2)
        elif who == cc.RED:
            self.win_red.draw(self.screen, bg_size[0] / 2, bg_size[1] / 2)

if __name__ == "__main__":
    pygame.init()
    # 显示界面的相框(宽，高)
    screen = pygame.display.set_mode((800, 700))
    # 显示标题
    pygame.display.set_caption("中国象棋 : )")
    show_image = ImageShow(screen)

    while True:
        # 事件检测（点击了键盘、鼠标等）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # 退出程序
                sys.exit()

        show_image.show_bg()
        show_image.show_chessboard()
        
        show_image.show_chess(cb.chess_board(cb.init_board()).board)

        show_image.show_back(True, True)
        show_image.show_score(cc.BLACK, cb.action((1, 2), (3, 4)), [1,2,3,4,5], [9,8,7,6,5], 1.6, 6)
        show_image.show_host(True, True, True, True)
        show_image.show_who_turn(cc.BLACK)
        show_image.show_who_turn(cc.RED)

        # 显示这个screen的内容
        pygame.display.update()