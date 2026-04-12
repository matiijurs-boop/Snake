import pygame
import random
import sys
import math

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 640, 420
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Safe Food Edition")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BG = (18,18,18)
GRID = (35,35,35)
SNAKE = (0,200,120)
HEAD = (0,255,160)
FOOD = (255,80,80)
TEXT = (230,230,230)
ACCENT = (255,180,0)
WALL = (120,120,255)
BORDER = (120,120,120)

font_big = pygame.font.SysFont("consolas", 44)
font = pygame.font.SysFont("consolas", 24)

# ---------------- MODES ----------------
MODE_WRAP = 1
MODE_NORMAL = 2
MODE_CHAOS = 3

LEVEL_SPEED = {1:10, 2:15, 3:22}

FOOD_COUNT_OPTIONS = [1, 3, 5, 10]

# ---------------- DRAW ----------------
def draw_text(text, x, y, big=False, center=False, color=TEXT):
    f = font_big if big else font
    img = f.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x,y)
    else:
        rect.topleft = (x,y)
    screen.blit(img, rect)

# ---------------- SNAKE ----------------
class Snake:
    def __init__(self):
        self.body = [(200,200),(180,200),(160,200)]
        self.dir = (CELL,0)

    def move(self):
        head = (self.body[0][0]+self.dir[0], self.body[0][1]+self.dir[1])
        self.body.insert(0, head)
        self.body.pop()

    def grow(self, n=1):
        for _ in range(n):
            self.body.append(self.body[-1])

    def draw(self):
        for i,p in enumerate(self.body):
            color = HEAD if i==0 else SNAKE
            pygame.draw.rect(screen, color, (*p, CELL, CELL), border_radius=6)

    def hit_self(self):
        return self.body[0] in self.body[1:]

# ---------------- FOOD (SAFE SPAWN) ----------------
class Food:
    def __init__(self, snake):
        self.snake = snake
        self.pos = self.spawn()

    def spawn(self):
        while True:
            pos = (
                random.randrange(0, WIDTH, CELL),
                random.randrange(0, HEIGHT, CELL)
            )

            if pos not in self.snake.body:
                return pos

    def draw(self):
        pygame.draw.rect(screen, FOOD, (*self.pos, CELL, CELL), border_radius=8)

# ---------------- GAME ----------------
def game(mode, level, food_count):

    snake = Snake()
    speed = LEVEL_SPEED[level]

    score = 0
    walls = []

    # CHAOS walls
    if mode == MODE_CHAOS:
        for _ in range(30):
            walls.append((
                random.randrange(0, WIDTH, CELL),
                random.randrange(0, HEIGHT, CELL)
            ))

    food_list = [Food(snake) for _ in range(food_count)]

    while True:
        screen.fill(BG)

        # grid
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GRID, (x,0), (x,HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, GRID, (0,y), (WIDTH,y))

        if mode == MODE_CHAOS:
            speed = LEVEL_SPEED[level] + random.randint(0,3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_r:
                    return "retry"

                if event.key == pygame.K_UP and snake.dir!=(0,CELL): snake.dir=(0,-CELL)
                if event.key == pygame.K_DOWN and snake.dir!=(0,-CELL): snake.dir=(0,CELL)
                if event.key == pygame.K_LEFT and snake.dir!=(CELL,0): snake.dir=(-CELL,0)
                if event.key == pygame.K_RIGHT and snake.dir!=(-CELL,0): snake.dir=(CELL,0)

        snake.move()
        hx, hy = snake.body[0]

        # WRAP
        if mode == MODE_WRAP:
            if hx < 0: hx = WIDTH - CELL
            elif hx >= WIDTH: hx = 0
            if hy < 0: hy = HEIGHT - CELL
            elif hy >= HEIGHT: hy = 0
            snake.body[0] = (hx, hy)

        # NORMAL
        elif mode == MODE_NORMAL:
            if hx < 0 or hx >= WIDTH or hy < 0 or hy >= HEIGHT:
                return "dead"

        if snake.hit_self():
            return "dead"

        if mode == MODE_CHAOS and snake.body[0] in walls:
            return "dead"

        # FOOD
        for food in food_list:
            if snake.body[0] == food.pos:
                snake.grow()
                food.pos = food.spawn()
                score += 1

        # DRAW
        snake.draw()

        for food in food_list:
            food.draw()

        if mode == MODE_CHAOS:
            for w in walls:
                pygame.draw.rect(screen, WALL, (*w, CELL, CELL))

        pygame.draw.rect(screen, BORDER, (0,0,WIDTH,HEIGHT), 2)

        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Food: {food_count}", 10, 35)

        pygame.display.flip()
        clock.tick(speed)

# ---------------- MENU ----------------
def menu():
    mode = 1
    level = 1
    food_idx = 2
    selected = 0

    modes = ["Normal", "Walls", "Chaos"]
    levels = ["Easy", "Medium", "Hard"]

    cursor_y = 150
    pulse = 0

    while True:
        screen.fill(BG)

        draw_text("SNAKE SAFE FOOD", WIDTH//2, 60, big=True, center=True, color=ACCENT)

        items = [
            ("Mode", modes[mode-1]),
            ("Level", levels[level-1]),
            ("Food", str(FOOD_COUNT_OPTIONS[food_idx]))
        ]

        target_y = 150 + selected * 60
        cursor_y += (target_y - cursor_y) * 0.25

        pulse += 0.1
        glow = int(180 + 70 * abs(math.sin(pulse)))

        for i,(name,value) in enumerate(items):
            y = 150 + i*60
            is_sel = (i == selected)

            color = (glow, glow, 0) if is_sel else TEXT

            if is_sel:
                pygame.draw.polygon(screen, ACCENT, [
                    (WIDTH//2 - 200, cursor_y - 10),
                    (WIDTH//2 - 200, cursor_y + 10),
                    (WIDTH//2 - 175, cursor_y)
                ])

            offset = 10 if is_sel else 0

            draw_text(name, WIDTH//2 - 120 - offset, y, center=True, color=color)
            draw_text(value, WIDTH//2 + 120 + offset, y, center=True, color=color)

        draw_text("ENTER start | ESC exit", WIDTH//2, 360, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3

                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3

                if event.key == pygame.K_RIGHT:
                    if selected == 0:
                        mode = 1 if mode==3 else mode+1
                    elif selected == 1:
                        level = 1 if level==3 else level+1
                    elif selected == 2:
                        food_idx = (food_idx + 1) % len(FOOD_COUNT_OPTIONS)

                if event.key == pygame.K_LEFT:
                    if selected == 0:
                        mode = 3 if mode==1 else mode-1
                    elif selected == 1:
                        level = 3 if level==1 else level-1
                    elif selected == 2:
                        food_idx = (food_idx - 1) % len(FOOD_COUNT_OPTIONS)

                if event.key == pygame.K_RETURN:
                    return mode, level, FOOD_COUNT_OPTIONS[food_idx]

# ---------------- MAIN ----------------
while True:
    m,l,f = menu()

    while True:
        result = game(m,l,f)

        if result == "retry":
            continue

        if result == "menu":
            break

        if result == "dead":
            screen.fill(BG)
            draw_text("GAME OVER", WIDTH//2, 180, big=True, center=True, color=ACCENT)
            draw_text("R retry | ESC menu", WIDTH//2, 240, center=True)
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            waiting = False
                            m,l,f = menu()
                            break
                clock.tick(30)