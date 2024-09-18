import pygame
import random
import time

# 初始化 Pygame
pygame.init()

# 定义常量
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 100
ROWS, COLS = 6, 6
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (200, 200, 200)
GAME_TIME = 360  # 倒计时 360 秒

# 定义层次颜色，包括第四层颜色
LAYER_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 165, 0)]  # 为第四层添加橙色边框
HIGHLIGHT_COLOR = (255, 255, 0)  # 选中后的高亮颜色（黄色）

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Match the Tiles")

# 加载图案图片 (pattern_0 到 pattern_6)
patterns = [pygame.image.load(f"pattern_{i}.png") for i in range(7)]
patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in patterns]


# 定义按钮函数
def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    font = pygame.font.SysFont(None, 36)
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x + (w - text_surface.get_width()) // 2, y + (h - text_surface.get_height()) // 2))


# 主菜单
def main_menu():
    menu = True
    while menu:
        screen.fill(WHITE)
        font = pygame.font.SysFont(None, 50)
        text = font.render("Select Difficulty", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        # 绘制难度按钮
        draw_button("Easy (2 layers)", WIDTH // 2 - 100, HEIGHT // 2 - 100, 200, 50, (200, 200, 200), (150, 150, 150),
                    lambda: start_game(2))
        draw_button("Medium (3 layers)", WIDTH // 2 - 100, HEIGHT // 2, 200, 50, (200, 200, 200), (150, 150, 150),
                    lambda: start_game(3))
        draw_button("Hard (4 layers)", WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, (200, 200, 200), (150, 150, 150),
                    lambda: start_game(4))
        draw_button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 50, (200, 200, 200), (150, 150, 150), quit_game)

        pygame.display.update()

        # 处理退出事件，避免未响应
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


# 退出游戏函数
def quit_game():
    pygame.quit()
    quit()


# 生成游戏板，确保每种图案生成偶数次
def generate_boards(layers):
    # 创建所有图案的成对列表
    total_tiles = ROWS * COLS
    if total_tiles % 2 != 0:
        raise ValueError("Total number of tiles must be even to ensure pairing.")

    tile_pool = []
    for i in range(total_tiles // 2):
        tile = patterns[i % len(patterns)]  # 使用模式索引避免越界
        tile_pool.extend([tile, tile])  # 每种图案成对出现

    random.shuffle(tile_pool)

    boards = []
    for _ in range(layers):
        board = random.sample(tile_pool, ROWS * COLS)  # 随机生成每层的图案
        boards.append(board)

    return boards


# 游戏逻辑
def start_game(layers):
    boards = generate_boards(layers)
    selected = []
    game_over = False
    start_time = time.time()

    # 游戏循环
    while not game_over:
        screen.fill(BG_COLOR)

        elapsed_time = time.time() - start_time
        time_left = GAME_TIME - elapsed_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and time_left > 0:
                x, y = event.pos
                tile = get_tile_at_pos(x, y, boards, layers)  # 修改为传递 boards 作为参数
                if tile:
                    layer, row, col = tile
                    if boards[layer][row * COLS + col] is not None:
                        selected.append((layer, row, col))
                    if len(selected) == 2:
                        check_match(selected, boards)

        # 绘制图案和计时器
        draw_board(boards, layers, selected)
        draw_timer(time_left)

        if is_game_over(boards):
            draw_game_over("You Win!")
            game_over = True

        if time_left <= 0:
            draw_game_over("Time's Up!")
            game_over = True

        pygame.display.update()
        pygame.time.Clock().tick(FPS)  # 控制帧率，避免过载


# 检查是否消除成功
def check_match(selected, boards):
    layer1, r1, c1 = selected[0]
    layer2, r2, c2 = selected[1]
    if boards[layer1][r1 * COLS + c1] == boards[layer2][r2 * COLS + c2]:
        boards[layer1][r1 * COLS + c1] = None
        boards[layer2][r2 * COLS + c2] = None
    selected.clear()


# 绘制游戏板
def draw_board(boards, layers, selected):
    for layer in range(layers):
        for row in range(ROWS):
            for col in range(COLS):
                tile = boards[layer][row * COLS + col]
                if tile is not None:
                    x_offset = col * TILE_SIZE
                    y_offset = row * TILE_SIZE
                    screen.blit(tile, (x_offset, y_offset))
                    if (layer, row, col) in selected:
                        # 增加高亮边框厚度，使其更加明显
                        pygame.draw.rect(screen, HIGHLIGHT_COLOR, pygame.Rect(x_offset, y_offset, TILE_SIZE, TILE_SIZE),
                                         8)
                    pygame.draw.rect(screen, LAYER_COLORS[layer % len(LAYER_COLORS)],
                                     pygame.Rect(x_offset, y_offset, TILE_SIZE, TILE_SIZE), 4)


# 获取点击的图案位置
def get_tile_at_pos(x, y, boards, layers):  # 修改为接受 boards 作为参数
    col = x // TILE_SIZE
    row = y // TILE_SIZE

    for layer in reversed(range(layers)):  # 从上到下检查
        if boards[layer][row * COLS + col] is not None:
            return layer, row, col
    return None


# 检查游戏是否结束
def is_game_over(boards):
    return all(tile is None for layer in boards for tile in layer)


# 显示计时器
def draw_timer(time_left):
    font = pygame.font.SysFont(None, 40)
    timer_text = font.render(f"Time Left: {int(time_left)}", True, BLACK)
    screen.blit(timer_text, (10, 10))


# 游戏结束界面
def draw_game_over(message):
    font = pygame.font.SysFont(None, 60)
    text = font.render(message, True, BLACK)
    screen.fill(WHITE)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2 - 30))

    # 添加退出按钮
    draw_button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, (200, 200, 200), (150, 150, 150), quit_game)

    pygame.display.flip()
    pygame.time.wait(3000)
    main_menu()


# 启动主菜单
main_menu()

pygame.quit()
