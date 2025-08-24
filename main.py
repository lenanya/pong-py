import pygame as pg
import copy

type Colour = tuple[int, int, int]
type Direction = int

class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Vec2(self.x * other.x, self.y * other.y)
    
    def __eq__(self, other) -> bool:
        return (self.x == other.x and self.y == other.y)
    
    def as_list(self) -> list[float]:
        return [self.x, self.y]
    
    def __str__(self) -> str:
        return "{" + str(self.x) + ", " + str(self.y) + "}"

RED: Colour = (0xff, 0, 0)
GREEN: Colour = (0, 0xff, 0)
BLUE: Colour = (0, 0, 0xff)
WHITE: Colour = (0xff, 0xff, 0xff)
BLACK: Colour = (0, 0, 0)
GREY: Colour = (0xa0, 0xa0, 0xa0)

W_HEIGHT: float = 600
W_WIDTH: float = 800
W_SIZE: tuple[float, float] = (W_WIDTH, W_HEIGHT)
W_TITLE: str = "Pong"
W_CENTRE: Vec2 = Vec2(W_WIDTH / 2, W_HEIGHT / 2)
FPS: int = 60

UP: Direction = -1
DOWN: Direction = 1

P1_SCORED: int = 1
P2_SCORED: int = 2
NO_SCORED: int = 0

LINE_DASH_COUNT: int = 10


def draw_rectv(surface: pg.Surface, pos: Vec2, size: Vec2, colour: Colour):
    r: pg.Rect = pg.Rect(pos.as_list(), size.as_list())
    pg.draw.rect(surface, colour, r)

def draw_line(surface: pg.Surface):
    for i in range(LINE_DASH_COUNT):
        pos: Vec2 = Vec2(W_WIDTH / 2 - 1, W_WIDTH / LINE_DASH_COUNT * i + i * 5 + 25)
        size: Vec2 = Vec2(2, 45)
        draw_rectv(surface, pos, size, GREY)

class Player:
    score = 0
    def __init__(self, player: int, pos: Vec2, size: Vec2, speed: Vec2, colour: Colour, surface: pg.Surface):
        self.player = player
        self.pos = pos 
        self.size = size
        self.speed = speed 
        self.colour = colour 
        self.surface = surface
        self.rect = pg.Rect(pos.as_list(), size.as_list())
    
    def draw(self):
        draw_rectv(self.surface, self.pos, self.size, self.colour)

    def move(self, direction: Direction):
        if self.pos.y + (self.speed.y * direction) + self.size.y >= W_HEIGHT:
            self.pos.y = W_HEIGHT - self.size.y
        elif self.pos.y + (self.speed.y * direction) < 0:
            self.pos.y = 0
        else:
            self.pos.y += self.speed.y * direction
        self.rect = pg.Rect(self.pos.as_list(), self.size.as_list())

class Ball:
    def __init__(self, pos: Vec2, size: Vec2, speed: Vec2, colour: Colour, surface: pg.Surface):
        self.pos = pos
        self.spawn = copy.deepcopy(pos)
        self.size = size
        self.speed = speed
        self.base_speed = copy.deepcopy(speed)
        self.colour = colour 
        self.surface = surface
        self.rect = pg.Rect(pos.as_list(), size.as_list())
    
    def draw(self):
        draw_rectv(self.surface, self.pos, self.size, self.colour)

    def move(self, p1: Player, p2: Player) -> int:
        scored = 0

        if self.rect.colliderect(p1.rect):
            self.speed.x *= -1
            self.pos.x = p1.pos.x + p1.size.x

        if self.rect.colliderect(p2.rect):
            self.speed.x *= -1
            self.pos.x = p2.pos.x - self.size.x

        if self.pos.x + self.speed.x + self.size.x > W_WIDTH:
            self.pos = copy.copy(self.spawn)
            self.speed = copy.copy(self.base_speed)
            scored = P1_SCORED
        elif self.pos.x + self.speed.x < 0:
            self.pos = copy.copy(self.spawn)
            self.speed = copy.copy(self.base_speed)
            scored = P2_SCORED
        else:
            self.pos.x += self.speed.x
        if self.pos.y + self.speed.y + self.size.y >= W_HEIGHT:
            self.pos.y = W_HEIGHT - self.size.y
            self.speed.y *= -1
        elif self.pos.y + self.speed.y < 0:
            self.pos.y = 0
            self.speed.y *= -1
        else:
            self.pos.y += self.speed.y
        self.rect = pg.Rect(self.pos.as_list(), self.size.as_list())
        return scored

def draw_scores(surface: pg.Surface, font, p1: Player, p2: Player):
    surface.blit(font.render(str(p1.score), True, WHITE), (50, 50))
    surface.blit(font.render(str(p2.score), True, WHITE), (750, 50))

def main():
    pg.init()
    pg.font.init()
    font = pg.font.SysFont("Arial", 40)
    surface: pg.Surface = pg.display.set_mode(W_SIZE)
    pg.display.set_caption(W_TITLE)
    clock = pg.time.Clock()

    ball_size: Vec2 = Vec2(40, 40)
    player_size: Vec2 = Vec2(25, 100)

    ball: Ball = Ball(pos=W_CENTRE - (ball_size * Vec2(0.5, 0.5)), size=ball_size, speed=Vec2(-7, 4), colour=WHITE, surface=surface)
    p1: Player = Player(1, Vec2(50, W_HEIGHT/2 - player_size.y/2), player_size, Vec2(0, 8), WHITE, surface)
    p2: Player = Player(2, Vec2(W_WIDTH - 50 - player_size.x, W_HEIGHT/2 - player_size.y/2), player_size, Vec2(0, 8), WHITE, surface)

    running: bool = True
    started: bool = False

    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False 

        surface.fill(BLACK)

        draw_line(surface)

        p1.draw()
        p2.draw()
        
        ball.draw()

        draw_scores(surface, font, p1, p2)

        keys = pg.key.get_pressed()

        if started:

            if keys[pg.K_w]:
                p1.move(UP)
            if keys[pg.K_s]:
                p1.move(DOWN)

            if keys[pg.K_UP]:
                p2.move(UP)
            if keys[pg.K_DOWN]:
                p2.move(DOWN)

            scored = ball.move(p1, p2)
            if scored == P1_SCORED:
                p1.score += 1
                started = False
            elif scored == P2_SCORED:
                p2.score += 1
                started = False
        
        else:
            if keys[pg.K_SPACE]:
                started = True

        pg.display.flip()
    
    pg.quit()


if __name__ == "__main__":
    main()