import pygame
import random

pygame.init()

width, height = 750, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

block_size = 30
grid_width = width // block_size
grid_height = height // block_size

grid = [[0] * grid_width for _ in range(grid_height)]

tetrominos = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

current_tetromino = random.choice(tetrominos)
current_x = grid_width // 2 - len(current_tetromino[0]) // 2
current_y = 0
fall_timer = 0
fall_speed = 10


def is_valid_move(move_x, move_y):
    for y in range(len(current_tetromino)):
        for x in range(len(current_tetromino[y])):
            if current_tetromino[y][x]:
                new_x = current_x + x + move_x
                new_y = current_y + y + move_y
                if (
                        new_x < 0
                        or new_x >= grid_width
                        or new_y >= grid_height
                        or grid[new_y][new_x]
                ):
                    return False
    return True


def rotate_tetromino():
    new_tetromino = []
    for x in range(len(current_tetromino[0])):
        new_row = []
        for y in range(len(current_tetromino) - 1, -1, -1):
            new_row.append(current_tetromino[y][x])
        new_tetromino.append(new_row)
    return new_tetromino


def clear_full_rows():
    full_rows = [i for i, row in enumerate(grid) if all(row)]
    for row in full_rows:
        del grid[row]
        grid.insert(0, [0] * grid_width)


running = True
clock = pygame.time.Clock()
while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and is_valid_move(-1, 0):
                current_x -= 1
            elif event.key == pygame.K_RIGHT and is_valid_move(1, 0):
                current_x += 1
            elif event.key == pygame.K_DOWN and is_valid_move(0, 1):
                current_y += 1
            elif event.key == pygame.K_UP:
                rotated_tetromino = rotate_tetromino()
                if is_valid_move(0, 0):
                    current_tetromino = rotated_tetromino

    fall_timer += 1
    if fall_timer >= fall_speed:
        if is_valid_move(0, 1):
            current_y += 1
        else:
            for y in range(len(current_tetromino)):
                for x in range(len(current_tetromino[y])):
                    if current_tetromino[y][x]:
                        grid[current_y + y][current_x + x] = 1
            clear_full_rows()
            current_tetromino = random.choice(tetrominos)
            current_x = grid_width // 2 - len(current_tetromino[0]) // 2
            current_y = 0
        fall_timer = 0

    screen.fill(BLACK)

    for x in range(grid_width):
        pygame.draw.line(screen, WHITE, (x * block_size, 0), (x * block_size, height))
    for y in range(grid_height):
        pygame.draw.line(screen, WHITE, (0, y * block_size), (width, y * block_size))

    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x]:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (x * block_size, y * block_size, block_size, block_size)
                )

    for y in range(len(current_tetromino)):
        for x in range(len(current_tetromino[y])):
            if current_tetromino[y][x]:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        (current_x + x) * block_size,
                        (current_y + y) * block_size,
                        block_size,
                        block_size
                    )
                )

    pygame.display.flip()
pygame.quit()
