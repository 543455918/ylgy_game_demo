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

# 定义层次颜色
LAYER_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # 每层不同的边框颜色
HIGHLIGHT_COLOR = (255, 255, 0)  # 选中后的高亮颜色

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("羊了个羊小游戏")

# 加载图案图片 (pattern_0 到 pattern_6)
patterns = [pygame.image.load(f"pattern_{i}.png") for i in range(7)]
patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in patterns]


# 创建偶数数量的图案，每种图案都生成偶数次
def generate_even_tiles():
    tile_pool = []
    for i in range(7):
        tile_pool.extend([patterns[i]] * 2)  # 每种图案生成 2 次
    random.shuffle(tile_pool)
    return tile_pool


# 生成游戏板（加入第三层）
def generate_boards():
    # 每个图层都有 6x6 的图案
    top_board = random.sample(generate_even_tiles() * 6, ROWS * COLS)
    middle_board = random.sample(generate_even_tiles() * 6, ROWS * COLS)
    bottom_board = random.sample(generate_even_tiles() * 6, ROWS * COLS)

    return [bottom_board, middle_board, top_board]


boards = generate_boards()
selected = []

# 游戏开始时间
start_time = time.time()


def draw_board():
    # 绘制每一层
    for layer in range(3):
        for row in range(ROWS):
            for col in range(COLS):
                tile = boards[layer][row * COLS + col]
                if tile is not None:
                    x_offset = col * TILE_SIZE
                    y_offset = row * TILE_SIZE

                    # 绘制图案
                    screen.blit(tile, (x_offset, y_offset))

                    # 判断是否已选中该图案，选中则高亮
                    if (layer, row, col) in selected:
                        pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                                         pygame.Rect(x_offset, y_offset, TILE_SIZE, TILE_SIZE), 5)
                    else:
                        # 绘制边框，边框厚度为 3 像素
                        pygame.draw.rect(screen, LAYER_COLORS[layer],
                                         pygame.Rect(x_offset, y_offset, TILE_SIZE, TILE_SIZE), 3)


def check_match():
    if len(selected) == 2:
        layer1, r1, c1 = selected[0]
        layer2, r2, c2 = selected[1]
        # 判断两个选中的图案是否是不同的图案，且相同且没有被覆盖
        if (layer1 != layer2 or r1 != r2 or c1 != c2) and boards[layer1][r1 * COLS + c1] == boards[layer2][
            r2 * COLS + c2]:
            # 同时消除两张图
            boards[layer1][r1 * COLS + c1] = None
            boards[layer2][r2 * COLS + c2] = None

        selected.clear()


def get_tile_at_pos(x, y):
    """
    根据鼠标点击的坐标获取相应的图案位置。优先选中最上层图案，如果不存在，则选中下一层图案。
    """
    col = x // TILE_SIZE
    row = y // TILE_SIZE

    # 优先检查第三层
    if boards[2][row * COLS + col] is not None:
        return 2, row, col  # 第三层图案存在，选中第三层
    elif boards[1][row * COLS + col] is not None:
        return 1, row, col  # 第三层图案消除，选中第二层
    elif boards[0][row * COLS + col] is not None:
        return 0, row, col  # 第二层图案消除，选中第一层

    return None


def is_game_over():
    """
    判断游戏是否结束：当所有图案都被消除时，游戏结束
    """
    for layer in boards:
        if any(tile is not None for tile in layer):
            return False  # 还有图案未被消除，游戏未结束
    return True


def draw_timer(time_left):
    font = pygame.font.SysFont(None, 40)
    timer_text = font.render(f"Time Left: {int(time_left)}", True, BLACK)
    screen.blit(timer_text, (10, 10))


def draw_game_over(message):
    font = pygame.font.SysFont(None, 60)
    text = font.render(message, True, BLACK)
    screen.fill(WHITE)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2 - 30))
    pygame.display.flip()
    pygame.time.wait(3000)


# 主游戏循环
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(FPS)

    # 计算剩余时间
    elapsed_time = time.time() - start_time
    time_left = GAME_TIME - elapsed_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and time_left > 0:
            x, y = event.pos
            tile = get_tile_at_pos(x, y)  # 根据点击坐标获取对应的图案位置
            if tile:
                layer, row, col = tile
                if boards[layer][row * COLS + col] is not None:
                    selected.append((layer, row, col))
                if len(selected) == 2:
                    check_match()

    # 检查游戏是否结束
    if is_game_over():
        draw_game_over("You Win!")
        running = False

    # 检查是否超时
    if time_left <= 0:
        draw_game_over("Time's Up!")
        running = False

    screen.fill(BG_COLOR)
    draw_board()
    draw_timer(time_left)
    pygame.display.flip()

pygame.quit()
