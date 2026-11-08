"""Игра «Змейка» с меню, выбором скорости, яблоками и препятствиями."""

from random import choice, randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
ALL_POSITIONS = frozenset(
    (x, y)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE)
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE_DIRECTIONS = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
KEY_DIRECTIONS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
    pg.K_w: UP,
    pg.K_s: DOWN,
    pg.K_a: LEFT,
    pg.K_d: RIGHT,
}

BOARD_BACKGROUND_COLOR = (225, 225, 225)
BORDER_COLOR = (75, 95, 105)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (30, 150, 70)
OBSTACLE_COLOR = (100, 110, 125)
TEXT_COLOR = (30, 40, 50)
BUTTON_COLOR = (190, 210, 220)

SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 30
SPEED_STEP = 5
MENU_FPS = 30
MAX_APPLES = 5
OBSTACLE_COUNT = 8
SAFE_DISTANCE = 3 * GRID_SIZE
START_SAFE_POSITIONS = frozenset(
    (x, y) for x, y in ALL_POSITIONS
    if abs(x - CENTER_POSITION[0]) <= SAFE_DISTANCE
    and abs(y - CENTER_POSITION[1]) <= SAFE_DISTANCE
)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка | Esc — выход')
clock = pg.time.Clock()


class GameObject:
    """Объект игрового поля с позицией и цветом."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        self.position = CENTER_POSITION
        self.body_color = body_color

    def draw(self):
        """Задать интерфейс отрисовки для игровых объектов."""

    def draw_cell(self, position, body_color=None):
        """Закрасить клетку, добавив рамку только при необходимости."""
        color = self.body_color if body_color is None else body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color not in (BOARD_BACKGROUND_COLOR, BORDER_COLOR):
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Одноклеточный объект: яблоко или препятствие в зависимости от цвета."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбрать позицию, если на поле есть хотя бы одна свободная клетка."""
        self.position = choice(tuple(ALL_POSITIONS - set(occupied_positions)))

    def draw(self):
        """Нарисовать одну клетку объекта."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, хранящая сегменты от головы к хвосту."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Применить поворот без разворота назад; вернуть признак изменения."""
        if new_direction in (self.direction,
                             OPPOSITE_DIRECTIONS[self.direction]):
            return False
        self.direction = new_direction
        return True

    def move(self):
        """Сдвинуть голову на клетку и перенести её через границу поля."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(0, (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

    def grow(self):
        """Увеличить длину, сохранив хвост текущего шага."""
        self.length += 1
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def reset(self):
        """Начать новую игру с одним сегментом в центре поля."""
        self.positions = [CENTER_POSITION]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.last = None

    def draw(self):
        """Стереть освободившийся хвост и нарисовать новую голову."""
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        self.draw_cell(self.get_head_position())


def create_apples(snake, obstacles):
    """Создать случайную партию яблок на свободных клетках."""
    occupied = set(snake.positions)
    for obstacle in obstacles:
        occupied.add(obstacle.position)

    count = min(randint(1, MAX_APPLES), len(ALL_POSITIONS - occupied))
    apples = []
    for _ in range(count):
        apple = Apple(occupied)
        apples.append(apple)
        occupied.add(apple.position)
    return apples


def has_collision(snake, obstacles):
    """Проверить столкновение головы с телом или препятствием."""
    head = snake.get_head_position()
    if head in snake.positions[2:]:
        return True
    for obstacle in obstacles:
        if head == obstacle.position:
            return True
    return False


def handle_keys(snake):
    """Обработать выход и выбрать не более одного поворота за шаг."""
    turned = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type != pg.KEYDOWN:
            continue
        if event.key == pg.K_ESCAPE:
            raise SystemExit
        if event.key not in KEY_DIRECTIONS or turned:
            continue
        turned = snake.update_direction(KEY_DIRECTIONS[event.key])


def get_menu_action(event, buttons):
    """Определить действие по клику или нажатию клавиши в меню."""
    if event.type == pg.QUIT:
        return 'quit'
    if event.type == pg.KEYDOWN:
        actions = {
            pg.K_RETURN: 'start',
            pg.K_ESCAPE: 'quit',
            pg.K_LEFT: 'slower',
            pg.K_RIGHT: 'faster',
        }
        return actions.get(event.key)
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        for action, rect in buttons.items():
            if rect.collidepoint(event.pos):
                return action
    return None


def draw_text(text, font, center):
    """Нарисовать текст меню с центром в заданной точке."""
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
        'slower': '−',
        'faster': '+',
    }
    for action, rect in buttons.items():
        pg.draw.rect(screen, BUTTON_COLOR, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)
        draw_text(labels[action], font, rect.center)
    draw_text('Enter — начать, ← / → — скорость, Esc — выход',
              small_font, (SCREEN_WIDTH // 2, 430))


def show_menu(speed, score=None):
    """Дождаться старта и вернуть выбранную скорость движения."""
    pg.display.set_caption('Змейка — меню | Enter — старт | Esc — выход')
    font = pg.font.SysFont('arial', 28)
    title_font = pg.font.SysFont('arial', 46)
    small_font = pg.font.SysFont('arial', 20)
    buttons = {
        'start': pg.Rect(150, 250, 340, 60),
        'quit': pg.Rect(150, 330, 340, 60),
        'slower': pg.Rect(135, 170, 50, 45),
        'faster': pg.Rect(455, 170, 50, 45),
    }
    while True:
        clock.tick(MENU_FPS)
        for event in pg.event.get():
            action = get_menu_action(event, buttons)
            if action == 'quit':
                raise SystemExit
            if action == 'start':
                return speed
            if action == 'slower':
                speed = max(MIN_SPEED, speed - SPEED_STEP)
            if action == 'faster':
                speed = min(MAX_SPEED, speed + SPEED_STEP)

        draw_menu(buttons, speed, score, font, title_font, small_font)
        pg.display.update()


def play_step(snake, apples, obstacles):
    """Выполнить шаг игры и сообщить, можно ли продолжать раунд."""
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
    for obstacle in obstacles:
        obstacle.draw()
    for apple in apples:
        apple.draw()
    snake.draw()
    pg.display.set_caption(
        f'Змейка | Счёт: {snake.length - 1} | Скорость: {speed}'
        ' | Стрелки / WASD | Esc — выход'
    )
    pg.display.update()


def main():
    """Показать меню, запустить раунд и предложить повтор после проигрыша."""
    pg.init()
    try:
        speed = show_menu(SPEED)
        while True:
            snake = Snake()
            occupied = set(snake.positions) | START_SAFE_POSITIONS
            obstacles = []
            for _ in range(min(OBSTACLE_COUNT, len(ALL_POSITIONS - occupied))):
                obstacle = Apple(occupied, OBSTACLE_COLOR)
                obstacles.append(obstacle)
                occupied.add(obstacle.position)
            apples = create_apples(snake, obstacles)
            screen.fill(BOARD_BACKGROUND_COLOR)
            draw_game(snake, apples, obstacles, speed)
            playing = True
            while playing:
                clock.tick(speed)
                handle_keys(snake)
                playing = play_step(snake, apples, obstacles)
                draw_game(snake, apples, obstacles, speed)
            speed = show_menu(speed, snake.length - 1)
    finally:
        pg.quit()


if __name__ == '__main__':
    main()
