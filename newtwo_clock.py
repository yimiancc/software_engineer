import sys
import pygame
import random
import math
import os

# 初始化pygame
pygame.init()

# 设置窗口大小
WINDOW_SIZE = (600, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Sheep! ')

# 加载资源
back_image = pygame.image.load('images/back3.png').convert()
tile_images = {f'tile{i}': pygame.image.load(f'images/tile{i}.png').convert_alpha() for i in
               range(1, 13)}
mask_image = pygame.image.load('images/mask.png').convert_alpha()  # 遮罩图片
win_image = pygame.image.load('images/win.png').convert_alpha()  # 胜利图片
end_image = pygame.image.load('images/end.png').convert_alpha()  # 失败图片
back_game_image = pygame.image.load('images/back.png').convert()  # 游戏背景图片

# 设置字体
font = pygame.font.SysFont(None, 48)

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66

# 牌堆位置
DOCK_POS = (90, 564)
DOCK_WIDTH = T_WIDTH * 7


# 游戏状态
GAME_STATE = 'MENU'


# 开始菜单
class StartMenu:
    def __init__(self):
        # 初始化按钮的宽度、高度和间距
        self.button_width = 200
        self.button_height = 50
        self.button_margin = 20
        # 创建一个字典来存储按钮的位置和尺寸，这些按钮包括'settings'、'start'和'quit'
        self.buttons = {
            'settings': pygame.Rect((WINDOW_SIZE[0] - self.button_width) // 2,
                                    (WINDOW_SIZE[1] // 2) - self.button_height - self.button_margin, self.button_width,
                                    self.button_height),
            'start': pygame.Rect((WINDOW_SIZE[0] - self.button_width) // 2, WINDOW_SIZE[1] // 2, self.button_width,
                                 self.button_height),
            'quit': pygame.Rect((WINDOW_SIZE[0] - self.button_width) // 2,
                                (WINDOW_SIZE[1] // 2) + self.button_height + self.button_margin, self.button_width,
                                self.button_height)
        }
        # 创建一个标题文本对象，用于显示在屏幕
        self.title = font.render("Sheep!", True, (255, 255, 255))

    # 处理事件的方法，主要用于检测鼠标点击
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['start'].collidepoint(event.pos): # 检查鼠标点击是否落在'start'按钮上
                print("Start game!")
                # 更改游戏状态为'GAME'
                global GAME_STATE
                GAME_STATE = 'GAME'
            # 检查鼠标点击是否落在'quit'按钮上
            elif self.buttons['quit'].collidepoint(event.pos):
                # pygame.draw.rect (screen, (255, 255, 255), dialog_rect)
                # screen.blit(dialog_title, (dialog_x + 50, dialog_y + 50))
                # screen.blit(dialog_text, (dialog_x + 50, dialog_y + 100))
                # pygame.display.update()
                # pygame.time.wait (1000)
                print("Quit game!")
                pygame.quit()
                sys.exit()
            # 检查鼠标点击是否落在'settings'按钮上
            elif self.buttons['settings'].collidepoint(event.pos):
                print("Setting clicked!")

    # 绘制菜单的方法
    def draw(self):
        # 绘制背景图像
        screen.blit(back_image, (0, 0))
        # 遍历所有按钮，绘制它们
        for name, rect in self.buttons.items():
            pygame.draw.rect(screen, (255, 255, 255), rect)  # 绘制白色按钮
            text = font.render(name.capitalize(), True, (0, 0, 0))  # 渲染按钮上的文本
            screen.blit(text, (rect.x + 50, rect.y + 10))   # 将文本绘制到按钮上
        # 绘制标题
        screen.blit(self.title, (300, 200))
        # 更新屏幕显示
        pygame.display.update()




# 游戏类
class Game:
    def __init__(self):  #AIGC
        self.tiles = []
        self.docks = []
        self.init_game()
        self.timer = 120  # 初始化倒计时为120秒
        self.last_time = pygame.time.get_ticks()  # 上次更新时间
    def init_game(self):
        ts = list(range(1, 13)) * 12
        random.shuffle(ts)
        n = 0
        for k in range(7):      # 设置7层方块
            for i in range(7 - k):       #每层减1行
                for j in range(7 - k):
                    t = ts[n]            #获取方块的种类
                    n += 1
                    x = 120 + (k * 0.5 + j) * T_WIDTH
                    y = 100 + (k * 0.5 + i) * T_HEIGHT * 0.9
                    tile = {'image': tile_images[f'tile{t}'], 'tag': t, 'pos': (x, y), 'status': 1 if k == 6 else 0,
                            'layer': k}   #记录方块的类型、位置、状态（状态为1为顶层，为0则不是）
                    self.tiles.append(tile)

        for i in range(4):      #剩余的4张牌放下面，确保能凑整通关
            t = ts[n]
            n += 1
            x = 210 + i * T_WIDTH
            y = 516
            tile = {'image': tile_images[f'tile{t}'], 'tag': t, 'pos': (x, y), 'status': 1, 'layer': 0}   #状态都为可点击
            self.tiles.append(tile)



    def draw(self):

        # 绘制倒计时（AIGC)
        font = pygame.font.SysFont(None, 48)  # 创建字体对象
        timer_text = font.render(f"{int(self.timer)}", True, (255, 255, 255))  # 渲染文本
        screen.blit(timer_text, (WINDOW_SIZE[0] - timer_text.get_width() - 20, 20))  # 绘制到屏幕右上角

        for tile in self.tiles:
            # 绘制上方牌组
            screen.blit(tile['image'], tile['pos'])
            if tile['status'] == 0:#不可点的添加遮罩
                mask_rect = pygame.Rect(tile['pos'], (T_WIDTH, T_HEIGHT))
                screen.blit(mask_image, mask_rect)

        for i, tile in enumerate(self.docks):
            # 绘制排队，先调整一下位置（可能有牌被消掉）
            x = DOCK_POS[0] + i * T_WIDTH
            y = DOCK_POS[1]
            screen.blit(tile['image'], (x, y))
        # 超过7张，失败
        if len(self.docks) >= 7:
            screen.blit(end_image, (0, 0))
        # 没有剩牌，胜利
        if len(self.tiles) == 0:
            screen.blit(win_image, (0, 0))
        #倒计时结束，失败
        if self.timer <= 0:
            screen.blit(end_image, (0, 0))
        pygame.display.update()
    def update_timer(self):#AIGC
        screen.blit(back_image, (0, 0))
        # 获取当前时间
        current_time = pygame.time.get_ticks()
        # 计算自上次更新以来的时间差
        elapsed_time = current_time - self.last_time
        # 更新时间
        self.timer -= elapsed_time / 1000  # 将毫秒转换为秒
        # 更新上次更新时间
        self.last_time = current_time
    def handle_events(self, event):
         if event.type == pygame.MOUSEBUTTONDOWN:
            if len(self.docks) >= 7 or len(self.tiles) == 0:     #游戏结束不响应
                return
            for tile in reversed(self.tiles):    #逆序循环是为了先判断上方的牌，如果点击了就直接跳出，避免重复判定
                if tile['status'] == 1 and pygame.Rect(tile['pos'], (T_WIDTH, T_HEIGHT)).collidepoint(event.pos):
                    # 状态1可点，并且鼠标在范围内
                    tile['status'] = 2
                    self.tiles.remove(tile)

                    diff = [t for t in self.docks if t['tag'] != tile['tag']]     #获取牌堆内不相同的牌
                    if len(self.docks) - len(diff) < 2:    #如果相同的牌数量<2，就加进牌堆
                        self.docks.append(tile)
                    else:                             #否则用不相同的牌替换牌堆（即消除相同的牌）
                        self.docks = diff

                        # 更新下方牌的可见性
                    for down in self.tiles:     #遍历所有的牌
                        if down['layer'] == tile['layer'] - 1 and pygame.Rect(down['pos'],
                                                                              (T_WIDTH, T_HEIGHT)).colliderect(
                                pygame.Rect(tile['pos'], (T_WIDTH, T_HEIGHT))):   #如果在此牌的下一层，并且有重叠
                            for up in self.tiles:    #有则再反过来判断这种被覆盖的牌，是否还有其他牌覆盖它
                                if up['layer'] == down['layer'] + 1 and pygame.Rect(up['pos'],
                                                                                    (T_WIDTH, T_HEIGHT)).colliderect(
                                        pygame.Rect(down['pos'], (T_WIDTH, T_HEIGHT))):    #如果有就跳出
                                    break
                            else:      #如果全都没有，说明它变成了可点状态
                                down['status'] = 1

                    return



# 游戏主循环
def main_loop():   #主循环用AIGC编写成
    # 创建菜单和游戏对象
    menu = StartMenu()
    game = Game()

    # 无限循环，直到游戏被关闭
    while True:   #AIGC
        # 处理所有pygame事件（如按键、鼠标移动、窗口关闭等）
        for event in pygame.event.get():
            # 如果事件是关闭窗口
            if event.type == pygame.QUIT:
                #print("Quit Game!")
                # 退出pygame并结束程序
                pygame.quit()
                sys.exit()
            # 根据当前的游戏状态（菜单或游戏）来处理事件
            if GAME_STATE == 'MENU':
                menu.handle_events(event)
            elif GAME_STATE == 'GAME':
                game.handle_events(event)

        # 根据当前的游戏状态来绘制界面
        if GAME_STATE == 'MENU':
            menu.draw()
        elif GAME_STATE == 'GAME':
            game.draw()
            game.update_timer()  # 更新倒计时

#调用main_loop函数开始游戏
if __name__ == '__main__':
    main_loop()