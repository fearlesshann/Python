import pygame
import time
import random

# 初始化 pygame
pygame.init()

# 游戏的窗口大小
width = 600
height = 400

# 设置游戏窗口
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('贪吃蛇游戏')

# 设置颜色
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# 设置贪吃蛇的速度
clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

# 设置字体
font_style = pygame.font.SysFont('Microsoft YaHei', 25)
score_font = pygame.font.SysFont('Microsoft YaHei', 35)

# 显示分数
def Your_score(score):
    value = score_font.render("你的分数: " + str(score), True, black)
    screen.blit(value, [0, 0])

# 画贪吃蛇
def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, green, [x[0], x[1], snake_block, snake_block])

# 显示消息
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [width / 6, height / 3])

# 游戏主函数
def gameLoop():
    game_over = False
    game_close = False

    # 贪吃蛇的起始位置
    x1 = width / 2
    y1 = height / 2

    # 贪吃蛇的移动速度
    x1_change = 0
    y1_change = 0

    # 贪吃蛇的身体
    snake_List = []
    Length_of_snake = 1

    # 随机生成食物的位置
    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close:
            screen.fill(blue)
            message("你输了! 按 C 重新开始，按 Q 退出游戏。", red)
            Your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(blue)
        pygame.draw.rect(screen, yellow, [foodx, foody, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        # 吃到食物
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
