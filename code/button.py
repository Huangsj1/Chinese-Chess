import pygame
import sys
import show
import chess_const as cc
import chess_board as cb

# 颜色
class Color:
    # 包含了多种不同颜色 (类变量)
    # 自定义颜色
    MY_BROWN = (221, 153, 20, 70)
    MY_QING = (100, 250, 237, 70)
    MY_WHITE_BLUE = (75, 150, 240, 200)
    MY_WHITE_GREEN = (89, 205, 101, 200)
    MY_DARK_GREEN = (18, 79, 24)

    # 固定的颜色
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (128, 128, 128)
    YELLOW = (255, 251, 13)
    TRANSPARENT = (255, 255, 255, 0)    # 白色完全透明

# 显示文本
class Text:
    def __init__(self, text: str, color: Color, font_type: str, font_size: int):
        '''
        text: 文本内容(如'开始')
        color: 文本颜色(如'Color.WHITE')
        font_type: 字体类型(如'KaiTi', 这里使用的是系统的颜色,只用给出有的字符串名称即可)
        font_size: 字体大小(如10)
        '''
        self.text = text
        self.color = color
        self.font_type = font_type
        self.font_size = font_size

        font_name = pygame.font.match_font(font_type)       # 1.获取字体文件
        self.font = pygame.font.Font(font_name, font_size)       # 2.获取font对象
        self.text_image = self.font.render(self.text, True, self.color).convert_alpha()  # 3.生成文字surface对象
        # 后面就可以将文字surface对象放到背景surface对象上

        self.text_width = self.text_image.get_width()
        self.text_height = self.text_image.get_height()

    # 切换显示文字
    def change_text(self, new_text: str):
        self.text = new_text
        self.text_image = self.font.render(self.text, True, self.color).convert_alpha()
        self.text_width = self.text_image.get_width()
        self.text_height = self.text_image.get_height()

    # 绘制
    def draw(self, surface: pygame.Surface, center_x, center_y):
        '''
        surface: 文本放置的表面
        center_x, center_y: 文本放置的 中心 坐标
        '''
        top_left_x = center_x - self.text_width / 2
        top_left_y = center_y - self.text_height / 2
        surface.blit(self.text_image, (top_left_x, top_left_y))


# 按钮文字
class ButtonText(Text):
    def __init__(self, text: str, color: Color, font_type: str, font_size: int):
        super().__init__(text, color, font_type, font_size)
        self.rect = self.text_image.get_rect()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        super().draw(surface, center_x, center_y)
        # 设置按钮中心
        self.rect.center = center_x, center_y

    # 如果鼠标点击了按钮就调用handle_func()处理函数
    def handle_event(self, handle_func):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.hovered:
            handle_func()


# 按钮的背景颜色图层
class ColorSurface:
    def __init__(self, color: Color, width: int, height: int):
        self.color = color
        self.width = width
        self.height = height

        self.color_image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.color_image.fill(self.color)

    def draw(self, surface: pygame.Surface, center_x, center_y):
        top_left_x = center_x - self.width / 2
        top_left_y = center_y - self.height / 2
        surface.blit(self.color_image, (top_left_x, top_left_y))


def test_button():
    print("hit the button!")

if __name__ == "__main__":
    pygame.init()
    # 显示界面的相框(宽，高)
    screen = pygame.display.set_mode(show.bg_size)
    # 显示标题
    pygame.display.set_caption("中国象棋 : )")

    show_image = show.ImageShow(screen)

    black_turn = Text('黑方', Color.BLACK, show.font_name, 50)
    red_turn = Text('红方', Color.RED, show.font_name, 50)

    button_people = ButtonText('玩家PK', Color.BLACK, show.font_name, 30)
    button_computer = ButtonText('电脑PK', Color.BLACK, show.font_name, 30)

    button_bg = ColorSurface(Color.MY_BROWN, 100, 40)

    while True:
        for event in pygame.event.get():
            # 退出程序
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 点击鼠标
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_computer.handle_event(test_button)
        show_image.show_bg()
        show_image.show_chessboard()
        button_computer.draw(screen, 100, 100)

        black_turn.draw(screen, show.bg_size[0] - 100, 180)
        red_turn.draw(screen, show.bg_size[0] - 100, show.bg_size[1] - 100)

        show_image.show_score(cc.BLACK, cb.action((1, 1), (2, 2)), [1, 2, 3, 4], [4, 5, 6, 7], 1.1, 10)
        show_image.show_back(True, True)
        show_image.show_host(True, True, True, False)

        pygame.display.update()