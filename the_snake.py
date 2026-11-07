from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Объект игрового поля с позицией и цветом."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Нарисовать одну клетку объекта с границей."""
        self.draw_cell(self.position)

    def draw_cell(self, position):
        """Нарисовать клетку по заданным координатам цветом объекта."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко, которое появляется на свободной клетке поля."""

    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied_positions=()):
        """Выбрать случайную клетку, не занятую змейкой."""
        occupied = set(occupied_positions)
        free_positions = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                position = (x * GRID_SIZE, y * GRID_SIZE)
                if position not in occupied:
                    free_positions.append(position)

        if free_positions:
            self.position = choice(free_positions)
        else:
            self.position = None

    def draw(self):
        """Нарисовать яблоко, если на поле есть свободное место."""
        if self.position is not None:
            super().draw()


class Snake(GameObject):
    """Змейка, хранящая сегменты от головы к хвосту."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применить допустимый поворот перед следующим шагом."""
        if self.next_direction is not None:
            opposite = (-self.direction[0], -self.direction[1])
            if self.next_direction != opposite:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвинуть голову на клетку и перенести её через границу поля."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.position = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, self.position)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def grow(self):
        """Увеличить длину, сохранив хвост текущего шага."""
        self.length += 1
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def reset(self):
        """Начать новую игру с одним сегментом в центре поля."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def draw(self):
        """Нарисовать все сегменты змейки."""
        for position in self.positions:
            self.draw_cell(position)


def handle_keys(game_object):
    """Обработать выход и выбрать не более одного поворота за шаг."""
    directions = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type != pygame.KEYDOWN:
            continue
        if event.key not in directions:
            continue
        if game_object.next_direction is not None:
            continue

        direction = directions[event.key]
        opposite = (-game_object.direction[0], -game_object.direction[1])
        if direction != game_object.direction and direction != opposite:
            game_object.next_direction = direction


def main():
    """Инициализация PyGame"""
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        # Тут опишите основную логику игры.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() == apple.position:
            snake.grow()
            if snake.length == GRID_WIDTH * GRID_HEIGHT:
                snake.reset()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
