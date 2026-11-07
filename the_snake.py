from random import choice, randint

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

OBSTACLE_COLOR = (135, 145, 160)

TEXT_COLOR = (235, 240, 245)

BUTTON_COLOR = (35, 65, 75)
# Скорость движения змейки:
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 30
SPEED_STEP = 5
OBSTACLE_COUNT = 8
SAFE_DISTANCE = 3 * GRID_SIZE
MAX_APPLES = 5
MENU_FPS = 30

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def get_free_positions(occupied_positions):
    """Собрать координаты всех свободных клеток поля."""
    occupied = set(occupied_positions)
    free_positions = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            position = (x * GRID_SIZE, y * GRID_SIZE)
            if position is not occupied:
                free_positions.append(position)
    return free_positions


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

    def __init__(self, occupied_positions=()):
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбрать случайную клетку, не занятую змейкой."""
        free_positions = get_free_positions(occupied_positions)
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


class Obstacle(GameObject):
    """Неподвижное препятствие размером в одну клетку."""

    def __init__(self, position):
        super().__init__(OBSTACLE_COLOR)


def create_obstacles(snake):
    """Разместить препятствия, оставив свободную зону вокруг старта."""
    head_x, head_y = snake.get_head_position()
    free_positions = get_free_positions(snake.positions)
    candidates = []
    for x, y in free_positions:
        if abs(x - head_x) > SAFE_DISTANCE:
            candidates.append((x, y))
        elif abs(y - head_y) > SAFE_DISTANCE:
            candidates.append((x, y))
    obstacles = []
    for _ in range(min(OBSTACLE_COUNT, len(candidates))):
        position = choice(candidates)
        candidates.remove(position)
        obstacles.append(Obstacle(position))
    return obstacles


def create_apples(snake, obstacles):
    """Создать случайное количество яблок на свободных клетках."""
    occupied = snake.positions.copy()
    for obstacle in obstacles:
        occupied.append(obstacle.position)
    count = min(randint(1, MAX_APPLES), len(get_free_positions(occupied)))
    apples = []
    for _ in range(count):
        apple = Apple(occupied)
        apples.append(apple)
        occupied.append(apple.position)
    return apples


def has_collision(snake, obstacles):
    """Проверить столкновение головы с телом или препятствием."""
    head = snake.get_head_position()
    if head in snake.positions[1:]:
        return True
    for obstacle in obstacles:
        if head == obstacle.position:
            return True
    return False


def quit_game():
    """Закрыть окно и завершить программу."""
    pygame.quit
    raise SystemExit


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


def get_menu_action(event, buttons):
    """Определить действие по клику или нажатию клавиши в меню."""
    if event.type == pygame.QUIT:
        quit_game()
    if event.type == pygame.KEYDOWN:
        actions = {
            pygame.K_RETURN: 'start',
            pygame.K_ESCAPE: 'quit',
            pygame.K_LEFT: 'slower',
            pygame.K_RIGHT: 'faster',
        }
        return actions.get(event.key)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for action, rect in buttons.items():
            if rect.collidepoint(event.pos):
                return action
    return None


def draw_text(text, font, center):
    """Написать текст с центром в заданной точке."""
    image = font.render(text, True, TEXT_COLOR)
    screen.blit(image, image.get_rect(center=center))


def draw_menu(buttons, speed, score, font, title_font, small_font):
    """Нарисовать стартовое меню или результаты завершённой игры."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = 'Змейка'
    subtitle = 'Яблоки дают очки, препятствия завершают игру'
    start_label = 'Старт'
    if score is not None:
        title = 'Игра окончена'
        subtitle = f'Твой счёт: {score}'
        start_label = 'Начать сначала'
    draw_text(title, title_font, (SCREEN_WIDTH // 2, 70))
    draw_text(subtitle, small_font, (SCREEN_WIDTH // 2, 125))
    draw_text(f'Скорость: {speed}', font, (SCREEN_WIDTH // 2, 192))
    labels = {
        'start': start_label,
        'quit': 'Выход',
        'slower': '-',
        'faster': '+',
    }
    for action, rect in buttons.items():
        pygame.draw.rect(screen, BUTTON_COLOR, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        draw_text(labels[action], font, rect.center)
    draw_text('Enter — начать, ← / → — скорость, Esc — выход',
              small_font, (SCREEN_WIDTH // 2, 430))


def show_menu(speed, score=None):
    """Дождаться старта и вернуть выбранную скорость движения."""
    pygame.display.set_caption('Змейка — меню')
    font = pygame.font.SysFont('arial', 28)
    title_font = pygame.font.SysFont('arial', 46)
    small_font = pygame.font.SysFont('arial', 20)
    buttons = {
        'start': pygame.Rect(150, 250, 340, 60),
        'quit': pygame.Rect(150, 330, 340, 60),
        'slower': pygame.Rect(135, 170, 50, 45),
        'faster': pygame.Rect(455, 170, 50, 45),
    }
    while True:
        clock.tick(MENU_FPS)
        for event in pygame.event.get():
            action = get_menu_action(event, buttons)
            if action == 'quit':
                quit_game()
            if action == 'start':
                return speed
            if action == 'slower':
                speed = max(MIN_SPEED, speed - SPEED_STEP)
            if action == 'faster':
                speed = min(MAX_SPEED, speed + SPEED_STEP)

        draw_menu(buttons, speed, score, font, title_font, small_font)
        pygame.display.update()


def play_step(snake, apples, obstacles):
    """Выполнить шаг игры и сообщить, можно ли продолжать раунд."""
    snake.update_direction()
    snake.move()
    if has_collision(snake, obstacles):
        return False

    for apple in apples:
        if snake.get_head_position() == apple.position:
            snake.grow()
            apples.remove(apple)
            break
    if not apples:
        apples.extend(create_apples(snake, obstacles))
    return bool(apples)


def draw_game(snake, apples, obstacles, speed):
    """Обновить игровое поле и показать счёт в заголовке окна."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for obstacle in obstacles:
        obstacle.draw()
    for apple in apples:
        apple.draw()
    snake.draw()
    pygame.display.set_caption(
        f'Змейка | Счёт: {snake.length - 1} | Скорость: {speed}'
    )
    pygame.display.update()


def main():
    """Инициализация PyGame"""
    pygame.init()
    speed = show_menu(SPEED)
    # Тут нужно создать экземпляры классов.

    while True:
        snake = Snake()
        obstacles = create_obstacles(snake)
        apples = create_apples(snake, obstacles)
        playing = True
        while playing:
            clock.tick(speed)
            handle_keys(snake)
            playing = play_step(snake, apples, obstacles)
            draw_game(snake, apples, obstacles, speed)


if __name__ == '__main__':
    main()
