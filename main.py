import pygame
import random
import sys


def show_menu():
    new_menu = Menu()
    new_menu.run()


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 330, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Крутой тетрис")

        self.BLACK = pygame.Color('black')
        self.WHITE = pygame.Color('white')
        self.colors = [pygame.Color('red'), pygame.Color('blue'), pygame.Color('yellow'), pygame.Color('green')]

        self.block_size = 30
        self.grid_width = self.width // self.block_size
        self.grid_height = self.height // self.block_size

        self.grid = [[0] * self.grid_width for _ in range(self.grid_height)]

        self.tetrominos = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1, 1], [1, 1, 0]],
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1, 1], [0, 0, 1]]
        ]
        self.current_tetromino = random.choice(self.tetrominos)
        self.current_x = self.grid_width // 2 - len(self.current_tetromino[0]) // 2
        self.current_y = 0
        self.fall_timer = 0
        self.fall_speed = 10
        self.score = 0
        self.final_score = 0
        self.running = True
        self.clock = pygame.time.Clock()

    def set_fallen_color(self):
        for y in range(len(self.current_tetromino)):
            for x in range(len(self.current_tetromino[y])):
                if self.current_tetromino[y][x]:
                    self.grid[self.current_y + y][self.current_x + x] = self.color_tetromino

    def update_grid_size(self):
        self.grid_width = self.width // self.block_size
        self.grid_height = self.height // self.block_size
        self.grid = [[0] * self.grid_width for _ in range(self.grid_height)]

    def is_valid_move(self, move_x, move_y):
        for y in range(len(self.current_tetromino)):
            for x in range(len(self.current_tetromino[y])):
                if self.current_tetromino[y][x]:
                    new_x = self.current_x + x + move_x
                    new_y = self.current_y + y + move_y
                    if (
                            new_x < 0
                            or new_x >= self.grid_width
                            or new_y >= self.grid_height
                            or new_y < 0
                            or (move_x > 0 and new_x >= self.grid_width)
                            or self.grid[new_y][new_x]
                    ):
                        return False
        return True

    def rotate_tetromino(self):
        new_tetromino = []
        for x in range(len(self.current_tetromino[0])):
            new_row = []
            for y in range(len(self.current_tetromino) - 1, -1, -1):
                new_row.append(self.current_tetromino[y][x])
            new_tetromino.append(new_row)
        if self.current_x + len(new_tetromino[0]) > self.grid_width:
            offset = self.current_x + len(new_tetromino[0]) - self.grid_width
            self.current_x -= offset
        if self.current_x < 0:
            self.current_x = 0
        if self.current_y + len(new_tetromino) > self.grid_height:
            offset = self.current_y + len(new_tetromino) - self.grid_height
            self.current_y -= offset
        for y in range(len(new_tetromino)):
            for x in range(len(new_tetromino[y])):
                if new_tetromino[y][x] and (
                        self.current_x + x < 0
                        or self.current_x + x >= self.grid_width
                        or self.current_y + y >= self.grid_height
                        or (self.current_y + y >= 0 and self.grid[self.current_y + y][self.current_x + x])
                ):
                    return self.current_tetromino
        return new_tetromino

    def clear_full_rows(self):
        full_rows = [i for i, row in enumerate(self.grid) if all(row)]
        for row in full_rows:
            del self.grid[row]
            self.grid.insert(0, [0] * self.grid_width)
            self.score += 10

    def save_score(self):
        with open('tetris_records.txt', 'a') as file:
            file.write(f"{self.score}\n")

    def handle_events(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.is_valid_move(-1, 0):
                self.current_x -= 1
        elif keys[pygame.K_RIGHT]:
            if self.is_valid_move(1, 0):
                self.current_x += 1
        elif keys[pygame.K_DOWN] and self.is_valid_move(0, 1):
            self.current_y += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    rotated_tetromino = self.rotate_tetromino()
                    if self.is_valid_move(0, 0):
                        self.current_tetromino = rotated_tetromino

    def update(self):
        if self.current_y == 0 and self.fall_timer == 0:
            self.set_color()
        self.fall_timer += 1
        if self.fall_timer >= self.fall_speed:
            if self.is_valid_move(0, 1):
                self.current_y += 1
            else:
                for y in range(len(self.current_tetromino)):
                    for x in range(len(self.current_tetromino[y])):
                        if self.current_tetromino[y][x]:
                            self.grid[self.current_y + y][
                                self.current_x + x] = self.color_tetromino
                self.clear_full_rows()
                if self.current_y <= 0:
                    self.game_over()
                self.current_tetromino = random.choice(self.tetrominos)
                self.current_x = self.grid_width // 2 - len(self.current_tetromino[0]) // 2
                self.current_y = 0
                self.set_color()

            self.fall_timer = 0

    def game_over(self):
        self.final_score = self.score
        self.save_score()  #
        self.running = False
        game_over_screen = GameOver(show_menu, self.final_score)
        game_over_screen.run()

    def draw(self):
        self.screen.fill(self.BLACK)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Счёт: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(topleft=(10, 10))
        self.screen.blit(score_text, score_rect)

        for x in range(self.grid_width):
            pygame.draw.line(self.screen, self.WHITE, (x * self.block_size, 0), (x * self.block_size, self.height))
        for y in range(self.grid_height):
            pygame.draw.line(self.screen, self.WHITE, (0, y * self.block_size), (self.width, y * self.block_size))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.WHITE,
                        (x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    )

        for y in range(len(self.current_tetromino)):
            for x in range(len(self.current_tetromino[y])):
                if self.current_tetromino[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.WHITE,
                        (
                            (self.current_x + x) * self.block_size,
                            (self.current_y + y) * self.block_size,
                            self.block_size,
                            self.block_size
                        )
                    )

        pygame.display.flip()

    def color_draw(self):
        self.screen.fill(self.BLACK)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Счёт: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(topleft=(10, 10))
        self.screen.blit(score_text, score_rect)

        for x in range(self.grid_width):
            pygame.draw.line(self.screen, self.WHITE, (x * self.block_size, 0), (x * self.block_size, self.height))
        for y in range(self.grid_height):
            pygame.draw.line(self.screen, self.WHITE, (0, y * self.block_size), (self.width, y * self.block_size))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.grid[y][x],
                        (x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    )

        for y in range(len(self.current_tetromino)):
            for x in range(len(self.current_tetromino[y])):
                if self.current_tetromino[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.color_tetromino,
                        (
                            (self.current_x + x) * self.block_size,
                            (self.current_y + y) * self.block_size,
                            self.block_size,
                            self.block_size
                        )
                    )

        pygame.display.flip()

    def run(self, mode):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.update()
            if mode == 0:
                self.draw()
            if mode == 1:
                self.color_draw()
        pygame.quit()

    def set_color(self):
        self.color_tetromino = random.choice(self.colors)
        print(self.color_tetromino)


class Theme:
    def __init__(self):
        pygame.init()
        self.width, self.height = 330, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Menu")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.title_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)

        self.title_text = self.title_font.render("Выбор темы", True, self.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 100))

        self.play_button_text = self.button_font.render("Классика", True, self.WHITE)
        self.play_button_rect = self.play_button_text.get_rect(center=(self.width // 2, 300))

        self.quit_button_text = self.button_font.render("Цветной", True, self.WHITE)
        self.quit_button_rect = self.quit_button_text.get_rect(center=(self.width // 2, 400))

        self.records_button_text = self.button_font.render("Хз", True, self.WHITE)
        self.records_button_rect = self.records_button_text.get_rect(center=(self.width // 2, 350))

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    tetris = TetrisGame()
                    tetris.run(0)
                    self.running = False
                    sys.exit()
                elif self.quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    tetris = TetrisGame()
                    tetris.run(1)
                    self.running = False
                    sys.exit()
                elif self.records_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    tetris = TetrisGame()
                    tetris.run(0)
                    self.running = False
                    sys.exit()

    def draw(self):
        self.screen.fill(self.BLACK)
        self.screen.blit(self.title_text, self.title_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.play_button_rect, 2)
        self.screen.blit(self.play_button_text, self.play_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.quit_button_rect, 2)
        self.screen.blit(self.quit_button_text, self.quit_button_rect)

        pygame.draw.rect(self.screen, self.WHITE, self.records_button_rect, 2)
        self.screen.blit(self.records_button_text, self.records_button_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw()


class Menu:
    def __init__(self):
        pygame.init()
        self.width, self.height = 330, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Menu")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.title_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)

        self.title_text = self.title_font.render("Крутой тетрис", True, self.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 100))

        self.play_button_text = self.button_font.render("Играть", True, self.WHITE)
        self.play_button_rect = self.play_button_text.get_rect(center=(self.width // 2, 300))

        self.quit_button_text = self.button_font.render("Выйти", True, self.WHITE)
        self.quit_button_rect = self.quit_button_text.get_rect(center=(self.width // 2, 400))

        self.records_button_text = self.button_font.render("Таблица рекордов", True, self.WHITE)
        self.records_button_rect = self.records_button_text.get_rect(center=(self.width // 2, 350))

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    theme_menu = Theme()
                    theme_menu.run()
                    self.running = False
                    sys.exit()
                elif self.quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif self.records_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    table_records = TableRecords()
                    table_records.run()
                    self.running = False
                    sys.exit()

    def draw(self):
        self.screen.fill(self.BLACK)
        self.screen.blit(self.title_text, self.title_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.play_button_rect, 2)
        self.screen.blit(self.play_button_text, self.play_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.quit_button_rect, 2)
        self.screen.blit(self.quit_button_text, self.quit_button_rect)

        pygame.draw.rect(self.screen, self.WHITE, self.records_button_rect, 2)
        self.screen.blit(self.records_button_text, self.records_button_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw()


class GameOver:
    def __init__(self, menu_callback, final_score):
        pygame.init()
        self.final_score = final_score
        self.width, self.height = 330, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game Over")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.title_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)

        self.title_text = self.title_font.render("Game Over!!", True, self.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 100))

        self.menu_button_text = self.button_font.render("Меню", True, self.WHITE)
        self.menu_button_rect = self.menu_button_text.get_rect(center=(self.width // 2, 300))

        self.quit_button_text = self.button_font.render("Выйти", True, self.WHITE)
        self.quit_button_rect = self.quit_button_text.get_rect(center=(self.width // 2, 400))

        self.menu_callback = menu_callback

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.menu_callback()
                    self.running = False
                elif self.quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    def draw(self):
        self.screen.fill(self.BLACK)
        self.screen.blit(self.title_text, self.title_rect)

        font = pygame.font.Font(None, 36)
        final_score_text = font.render(f"Счет: {self.final_score}", True, self.WHITE)
        final_score_rect = final_score_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(final_score_text, final_score_rect)

        pygame.draw.rect(self.screen, self.WHITE, self.menu_button_rect, 2)
        self.screen.blit(self.menu_button_text, self.menu_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.quit_button_rect, 2)
        self.screen.blit(self.quit_button_text, self.quit_button_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw()


class TableRecords:
    def __init__(self):
        pygame.font.init()
        self.menu = menu
        self.width, self.height = 330, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Таблица рекордов")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.title_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)

        self.title_text = self.title_font.render("Топ 10 рекордов", True, self.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 100))

        self.menu_button_text = self.button_font.render("Меню", True, self.WHITE)
        self.menu_button_rect = self.menu_button_text.get_rect(center=(self.width // 2, 500))

        self.records_file_path = 'tetris_records.txt'
        self.top_records = self.get_top_records()
        self.clock = pygame.time.Clock()
        self.running = True

    def show_menu(self):
        self.menu = Menu()
        self.menu.run()

    def get_top_records(self, limit=10):
        try:
            with open(self.records_file_path, 'r') as file:
                records = [int(line.strip()) for line in file.readlines()]
        except FileNotFoundError:
            records = []

        records.sort(reverse=True)
        if len(records) < 10:
            return records
        return records[:limit]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.show_menu()
                    self.running = False

    def draw(self):
        self.screen.fill(self.BLACK)
        self.screen.blit(self.title_text, self.title_rect)

        font = pygame.font.Font(None, 28)
        y_position = 150
        for record in self.top_records:
            record_text = font.render(f"Счет: {record}", True, self.WHITE)
            record_rect = record_text.get_rect(center=(self.width // 2, y_position))
            self.screen.blit(record_text, record_rect)
            y_position += 30

        pygame.draw.rect(self.screen, self.WHITE, self.menu_button_rect, 2)
        self.screen.blit(self.menu_button_text, self.menu_button_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw()


if __name__ == '__main__':
    menu = Menu()
    menu.run()
