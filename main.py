# -*- coding: utf-8 -*-
import pygame
import random
import sys
import time
from pygame.locals import *
from PIL import Image, ImageSequence  # 添加Pillow库支持

# Initialize pygame
pygame.init()

# Game constants
CELL_SIZE = 20  # Smaller cell size for better display
WALL_THICKNESS = 2
PLAYER_SIZE = 15
PLAYER_COLOR = (255, 192, 203)
WALL_COLOR = (128, 128, 128)
PATH_COLOR = (255, 255, 255)
EXIT_COLOR = (0, 255, 0)
MONSTER_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)
BG_COLOR = (240, 240, 240)
AI_COLOR = (0, 0, 255)
INVINCIBLE_COLOR = (255, 100, 100)

# Maze dimensions (kept large)
MAZE_WIDTH = 30
MAZE_HEIGHT = 30

# Screen dimensions (smaller window)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Maze Game - Monster Edition')

# Direction constants
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


class AnimatedGIF:
    def __init__(self, filename, size):
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.last_update = 0

        # 使用Pillow加载GIF
        pil_image = Image.open(filename)
        for frame in ImageSequence.Iterator(pil_image):
            # 转换为RGBA模式（确保有alpha通道）
            frame = frame.convert("RGBA")
            # 调整大小
            frame = frame.resize(size, Image.LANCZOS)
            # 转换为Pygame Surface
            pygame_image = pygame.image.fromstring(
                frame.tobytes(), frame.size, frame.mode
            ).convert_alpha()
            self.frames.append(pygame_image)
            # 获取帧延迟（毫秒）
            try:
                self.durations.append(frame.info['duration'] / 1000)  # 转换为秒
            except:
                self.durations.append(0.1)  # 默认0.1秒

        if not self.durations:
            self.durations = [0.1] * len(self.frames)

    def update(self):
        now = time.time()
        if now - self.last_update > self.durations[self.current_frame]:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def get_current_frame(self):
        return self.frames[self.current_frame]


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.start_pos = (1, 1)
        self.exit_pos = (width - 2, height - 2)

        # 加载GIF动画作为出口
        try:
            self.exit_gif = AnimatedGIF("exit.gif", (CELL_SIZE, CELL_SIZE))
        except:
            self.exit_gif = None
            try:
                self.exit_image = pygame.image.load("exit.png").convert_alpha()
                self.exit_image = pygame.transform.scale(self.exit_image, (CELL_SIZE, CELL_SIZE))
            except:
                self.exit_image = None

        # 加载GIF动画作为墙
        try:
            self.wall_gif = AnimatedGIF("wall.gif", (CELL_SIZE, CELL_SIZE))
        except:
            self.wall_gif = None

        self.generate_maze()

        # Generate monsters - increased to 5
        self.monsters = []
        self.generate_monsters(5)

    def generate_maze(self):
        # Use depth-first search to generate maze
        stack = [self.start_pos]
        visited = set([self.start_pos])

        while stack:
            x, y = stack[-1]
            neighbors = []

            # Check four directions
            if y > 1 and (x, y - 2) not in visited:
                neighbors.append((x, y - 2, UP))
            if x < self.width - 2 and (x + 2, y) not in visited:
                neighbors.append((x + 2, y, RIGHT))
            if y < self.height - 2 and (x, y + 2) not in visited:
                neighbors.append((x, y + 2, DOWN))
            if x > 1 and (x - 2, y) not in visited:
                neighbors.append((x - 2, y, LEFT))

            if neighbors:
                nx, ny, direction = random.choice(neighbors)
                # Break the wall
                if direction == UP:
                    self.grid[y - 1][x] = 0
                elif direction == RIGHT:
                    self.grid[y][x + 1] = 0
                elif direction == DOWN:
                    self.grid[y + 1][x] = 0
                elif direction == LEFT:
                    self.grid[y][x - 1] = 0

                self.grid[ny][nx] = 0
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        # Create multiple paths to exit
        self.create_additional_paths()

        # Ensure exit is reachable
        self.ensure_exit_reachable()

    def create_additional_paths(self):
        # Create 3 additional exit paths
        for _ in range(3):
            side = random.randint(0, 3)  # 0:top, 1:right, 2:bottom, 3:left
            if side == 0:  # top
                x = random.randint(1, self.width - 2)
                y = 0
                self.grid[y + 1][x] = 0
            elif side == 1:  # right
                x = self.width - 1
                y = random.randint(1, self.height - 2)
                self.grid[y][x - 1] = 0
            elif side == 2:  # bottom
                x = random.randint(1, self.width - 2)
                y = self.height - 1
                self.grid[y - 1][x] = 0
            else:  # left
                x = 0
                y = random.randint(1, self.height - 2)
                self.grid[y][x + 1] = 0

    def ensure_exit_reachable(self):
        # Use BFS to ensure exit is reachable from start
        queue = [self.start_pos]
        visited = set([self.start_pos])

        while queue:
            x, y = queue.pop(0)

            # Check if we reached exit
            if (x, y) == self.exit_pos:
                return True

            # Check four directions
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.grid[ny][nx] == 0 and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # If exit not reachable, regenerate maze
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.generate_maze()

    def generate_monsters(self, count):
        for _ in range(count):
            while True:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                # Ensure monster is on path and not near start/exit
                if (self.grid[y][x] == 0 and
                        (x, y) != self.start_pos and
                        (x, y) != self.exit_pos and
                        abs(x - self.start_pos[0]) + abs(y - self.start_pos[1]) > 10):
                    # Load monster image
                    try:
                        monster_img = pygame.image.load("monster.png").convert_alpha()
                        monster_img = pygame.transform.scale(monster_img, (CELL_SIZE // 2, CELL_SIZE // 2))
                    except:
                        monster_img = None

                    self.monsters.append({
                        'x': x,
                        'y': y,
                        'image': monster_img,
                        'speed': random.randint(1, 2),
                        'direction': random.randint(0, 3)
                    })
                    break

    def draw(self, surface):
        # Calculate scale factors
        scale_x = SCREEN_WIDTH / (self.width * CELL_SIZE)
        scale_y = SCREEN_HEIGHT / (self.height * CELL_SIZE)
        scale = min(scale_x, scale_y)

        # Calculate offset to center the maze
        offset_x = (SCREEN_WIDTH - self.width * CELL_SIZE * scale) / 2
        offset_y = (SCREEN_HEIGHT - self.height * CELL_SIZE * scale) / 2

        # 更新GIF动画
        if self.wall_gif:
            self.wall_gif.update()
        if self.exit_gif:
            self.exit_gif.update()

        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE * scale,
                    offset_y + y * CELL_SIZE * scale,
                    CELL_SIZE * scale,
                    CELL_SIZE * scale
                )
                if self.grid[y][x] == 1:  # Wall
                    if self.wall_gif:
                        # 绘制GIF动画作为墙
                        frame = self.wall_gif.get_current_frame()
                        scaled_frame = pygame.transform.scale(
                            frame,
                            (int(CELL_SIZE * scale), int(CELL_SIZE * scale))
                        )
                        surface.blit(scaled_frame, rect)
                    else:
                        pygame.draw.rect(surface, WALL_COLOR, rect)
                else:  # Path
                    pygame.draw.rect(surface, PATH_COLOR, rect)

        # Draw exit
        exit_rect = pygame.Rect(
            offset_x + self.exit_pos[0] * CELL_SIZE * scale,
            offset_y + self.exit_pos[1] * CELL_SIZE * scale,
            CELL_SIZE * scale,
            CELL_SIZE * scale
        )

        if self.exit_gif:
            # 绘制GIF动画作为出口
            frame = self.exit_gif.get_current_frame()
            scaled_frame = pygame.transform.scale(
                frame,
                (int(CELL_SIZE * scale), int(CELL_SIZE * scale))
            )
            surface.blit(scaled_frame, exit_rect)
        elif self.exit_image:
            scaled_exit = pygame.transform.scale(self.exit_image,
                                                 (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))
            surface.blit(scaled_exit, exit_rect)
        else:
            pygame.draw.rect(surface, EXIT_COLOR, exit_rect)

        # Draw monsters
        for monster in self.monsters:
            center_x = offset_x + monster['x'] * CELL_SIZE * scale + CELL_SIZE * scale // 2
            center_y = offset_y + monster['y'] * CELL_SIZE * scale + CELL_SIZE * scale // 2

            if monster['image']:
                scaled_monster = pygame.transform.scale(monster['image'],
                                                        (int(CELL_SIZE * scale // 2),
                                                         int(CELL_SIZE * scale // 2)))
                img_rect = scaled_monster.get_rect(center=(center_x, center_y))
                surface.blit(scaled_monster, img_rect)
            else:
                pygame.draw.circle(
                    surface, MONSTER_COLOR,
                    (int(center_x), int(center_y)),
                    int(CELL_SIZE * scale // 4)
                )

        return offset_x, offset_y, scale

    def move_monsters(self):
        for monster in self.monsters:
            # 10% chance to change direction
            if random.random() < 0.1:
                monster['direction'] = random.randint(0, 3)

            # Attempt to move
            for _ in range(monster['speed']):
                new_x, new_y = monster['x'], monster['y']

                if monster['direction'] == UP:
                    new_y -= 1
                elif monster['direction'] == RIGHT:
                    new_x += 1
                elif monster['direction'] == DOWN:
                    new_y += 1
                elif monster['direction'] == LEFT:
                    new_x -= 1

                # Check if can move
                if (0 <= new_x < self.width and 0 <= new_y < self.height and
                        self.grid[new_y][new_x] == 0):
                    monster['x'], monster['y'] = new_x, new_y
                else:
                    # Hit wall, change direction
                    monster['direction'] = random.randint(0, 3)

    def check_monster_collision(self, player_x, player_y):
        for monster in self.monsters:
            if monster['x'] == player_x and monster['y'] == player_y:
                return True
        return False


class Player:
    def __init__(self, maze):
        self.x = maze.start_pos[0]
        self.y = maze.start_pos[1]
        self.maze = maze
        self.steps = 0
        self.lives = 3
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 2  # 2 seconds invincibility
        try:
            self.image = pygame.image.load("player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        except:
            self.image = None

    def move(self, direction):
        new_x, new_y = self.x, self.y

        if direction == UP:
            new_y -= 1
        elif direction == RIGHT:
            new_x += 1
        elif direction == DOWN:
            new_y += 1
        elif direction == LEFT:
            new_x -= 1

        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height:
            if self.maze.grid[new_y][new_x] == 0:
                self.x, self.y = new_x, new_y
                self.steps += 1

                # Check monster collision
                if self.maze.check_monster_collision(self.x, self.y):
                    if not self.invincible:
                        self.lives -= 1
                        self.invincible = True
                        self.invincible_start_time = time.time()
                        return "hit"
                return True
        return False

    def update(self):
        # Update invincibility status
        if self.invincible and time.time() - self.invincible_start_time > self.invincible_duration:
            self.invincible = False

    def draw(self, surface, offset_x, offset_y, scale):
        center_x = offset_x + self.x * CELL_SIZE * scale + CELL_SIZE * scale // 2
        center_y = offset_y + self.y * CELL_SIZE * scale + CELL_SIZE * scale // 2

        # Flash red if invincible
        if self.invincible:
            flash_interval = 0.2  # 0.2 seconds per flash
            flash_on = int((time.time() - self.invincible_start_time) / flash_interval) % 2 == 0
            if flash_on:
                color = INVINCIBLE_COLOR
                if self.image:
                    colored_img = self.image.copy()
                    colored_img.fill(color, special_flags=pygame.BLEND_MULT)
                    scaled_img = pygame.transform.scale(colored_img,
                                                        (int(PLAYER_SIZE * scale),
                                                         int(PLAYER_SIZE * scale)))
                    img_rect = scaled_img.get_rect(center=(center_x, center_y))
                    surface.blit(scaled_img, img_rect)
                    return
                else:
                    pygame.draw.circle(surface, color, (int(center_x), int(center_y)),
                                       int(PLAYER_SIZE * scale // 2))
                    return

        if self.image:
            scaled_img = pygame.transform.scale(self.image,
                                                (int(PLAYER_SIZE * scale),
                                                 int(PLAYER_SIZE * scale)))
            img_rect = scaled_img.get_rect(center=(center_x, center_y))
            surface.blit(scaled_img, img_rect)
        else:
            pygame.draw.circle(
                surface, PLAYER_COLOR,
                (int(center_x), int(center_y)),
                int(PLAYER_SIZE * scale // 2)
            )

    def is_at_exit(self):
        return (self.x, self.y) == self.maze.exit_pos


class AI:
    def __init__(self, maze):
        self.x = maze.start_pos[0]
        self.y = maze.start_pos[1]
        self.maze = maze
        self.steps = 0
        self.path = []
        self.move_timer = 0
        self.move_interval = 30  # Move every 10 frames
        self.find_path_to_exit()

    def find_path_to_exit(self):
        # Use A* algorithm to find path
        open_set = [(self.x, self.y)]
        came_from = {}
        g_score = {(x, y): float('inf') for y in range(self.maze.height) for x in range(self.maze.width)}
        g_score[(self.x, self.y)] = 0
        f_score = {(x, y): float('inf') for y in range(self.maze.height) for x in range(self.maze.width)}
        f_score[(self.x, self.y)] = self.heuristic(self.x, self.y)

        while open_set:
            current = min(open_set, key=lambda pos: f_score[pos])
            if current == self.maze.exit_pos:
                self.reconstruct_path(came_from, current)
                return

            open_set.remove(current)
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < self.maze.width and
                        0 <= neighbor[1] < self.maze.height and
                        self.maze.grid[neighbor[1]][neighbor[0]] == 0):
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor[0], neighbor[1])
                        if neighbor not in open_set:
                            open_set.append(neighbor)

    def heuristic(self, x, y):
        # Manhattan distance
        return abs(x - self.maze.exit_pos[0]) + abs(y - self.maze.exit_pos[1])

    def reconstruct_path(self, came_from, current):
        self.path = []
        while current in came_from:
            self.path.append(current)
            current = came_from[current]
        self.path.reverse()

    def move(self):
        if self.path:
            next_pos = self.path[0]
            self.x, self.y = next_pos
            self.steps += 1
            self.path.pop(0)
            return True
        return False

    def update(self):
        self.move_timer += 1
        if self.move_timer >= self.move_interval and self.path:
            self.move()
            self.move_timer = 0

    def draw(self, surface, offset_x, offset_y, scale):
        center_x = offset_x + self.x * CELL_SIZE * scale + CELL_SIZE * scale // 2
        center_y = offset_y + self.y * CELL_SIZE * scale + CELL_SIZE * scale // 2
        pygame.draw.circle(
            surface, AI_COLOR,
            (int(center_x), int(center_y)),
            int(PLAYER_SIZE * scale // 2)
        )

    def is_at_exit(self):
        return (self.x, self.y) == self.maze.exit_pos


def draw_text(surface, text, size, x, y, color=TEXT_COLOR):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def show_message(surface, message, color=(255, 0, 0)):
    font = pygame.font.SysFont(None, 72)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((255, 255, 255, 180))
    surface.blit(s, (0, 0))

    surface.blit(text, text_rect)
    pygame.display.flip()


def show_menu():
    screen.fill(BG_COLOR)

    # 加载并显示菜单图片
    try:
        menu_image = pygame.image.load("menu_image.png").convert_alpha()
        # 调整图片大小到合适尺寸（200x150）
        menu_image = pygame.transform.scale(menu_image, (200, 150))
        # 计算图片位置（水平居中，垂直位置偏上）
        image_rect = menu_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(menu_image, image_rect)
    except:
        pass  # 如果图片加载失败，忽略

    # 只绘制菜单选项（删除"Maze Game"标题）
    draw_text(screen, "1. Single Player", 48, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30)
    draw_text(screen, "2. Versus AI", 48, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    return "single"
                elif event.key == K_2:
                    return "versus"
        pygame.time.Clock().tick(60)


def main():
    game_mode = show_menu()

    clock = pygame.time.Clock()
    maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
    player = Player(maze)
    ai = None
    if game_mode == "versus":
        ai = AI(maze)
    running = True
    game_over = False
    win = False
    monster_move_timer = 0

    try:
        background = pygame.image.load("background.png").convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = None

    while running:
        monster_move_timer += 1
        if monster_move_timer >= 15:  # Monsters move every 15 frames
            maze.move_monsters()
            monster_move_timer = 0

            if maze.check_monster_collision(player.x, player.y) and not player.invincible:
                player.lives -= 1
                player.invincible = True
                player.invincible_start_time = time.time()
                if player.lives <= 0:
                    game_over = True
                    win = False

        player.update()
        if ai:
            ai.update()
            if ai.is_at_exit():
                game_over = True
                win = False

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and not game_over:
                moved = False
                if event.key == K_UP or event.key == K_w:
                    result = player.move(UP)
                elif event.key == K_RIGHT or event.key == K_d:
                    result = player.move(RIGHT)
                elif event.key == K_DOWN or event.key == K_s:
                    result = player.move(DOWN)
                elif event.key == K_LEFT or event.key == K_a:
                    result = player.move(LEFT)
                else:
                    continue

                if result == "hit":
                    if player.lives <= 0:
                        game_over = True
                        win = False
                elif result:
                    if player.is_at_exit():
                        game_over = True
                        win = True

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BG_COLOR)

        # Draw maze and get offset/scale
        offset_x, offset_y, scale = maze.draw(screen)

        # Draw player and AI with correct scaling
        player.draw(screen, offset_x, offset_y, scale)
        if ai:
            ai.draw(screen, offset_x, offset_y, scale)

        # Draw UI elements
        draw_text(screen, f"Steps: {player.steps}", 24, 10, 10)
        draw_text(screen, f"Lives: {player.lives}", 24, 10, 40)
        if ai:
            draw_text(screen, f"AI Steps: {ai.steps}", 24, SCREEN_WIDTH - 150, 10)

        if game_over:
            if win:
                show_message(screen, "You Win!", (0, 200, 0))
            else:
                if ai and ai.is_at_exit():
                    show_message(screen, "You Lose!", (200, 0, 0))
                else:
                    show_message(screen, "Game Over", (200, 0, 0))

            draw_text(screen, "Press R to restart", 24, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)
            draw_text(screen, "Press M for menu", 24, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80)
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        waiting = False
                        running = False
                    elif event.type == KEYDOWN:
                        if event.key == K_r:
                            maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
                            player = Player(maze)
                            if game_mode == "versus":
                                ai = AI(maze)
                            game_over = False
                            win = False
                            monster_move_timer = 0
                            waiting = False
                        elif event.key == K_m:
                            waiting = False
                            running = False
                            main()
                            return
                clock.tick(60)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()