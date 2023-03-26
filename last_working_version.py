import pygame as pg
import random
import math
from PIL import Image, ImageFilter

MAX_FPS = 60

RES_X = 1280
RES_Y = 720

# SCREEN_RECT = pg.rect.Rect(0, 0, 800, 500)
SCREEN_RECT = pg.rect.Rect(0, 0, RES_X, RES_Y)

SCREEN_RECT_LEFT_LINE = (SCREEN_RECT.x, SCREEN_RECT.y, SCREEN_RECT.x, SCREEN_RECT.y + SCREEN_RECT.height)
SCREEN_RECT_RIGHT_LINE = (SCREEN_RECT.x + SCREEN_RECT.width, SCREEN_RECT.y, SCREEN_RECT.x + SCREEN_RECT.width, SCREEN_RECT.y + SCREEN_RECT.height)
SCREEN_RECT_TOP_LINE = (SCREEN_RECT.x, SCREEN_RECT.y, SCREEN_RECT.x + SCREEN_RECT.width, SCREEN_RECT.y)
SCREEN_RECT_BOTTOM_LINE = (SCREEN_RECT.x, SCREEN_RECT.y + SCREEN_RECT.height, SCREEN_RECT.x + SCREEN_RECT.width, SCREEN_RECT.y + SCREEN_RECT.height)

# Left wall
SCREEN_RECT_LEFT = SCREEN_RECT.copy()
SCREEN_RECT_LEFT.width = 1

# Right wall
SCREEN_RECT_RIGHT = SCREEN_RECT.copy()
SCREEN_RECT_RIGHT.x += SCREEN_RECT.width
SCREEN_RECT_RIGHT.width = 1

# Top wall
SCREEN_RECT_TOP = SCREEN_RECT.copy()
SCREEN_RECT_TOP.height = 1

# Bottom wall
SCREEN_RECT_BOTTOM = SCREEN_RECT.copy()
SCREEN_RECT_BOTTOM.y += SCREEN_RECT.height
SCREEN_RECT_BOTTOM.height = 1

BALL_SPEED = 10

# Arcanoid texture pack is from https://opengameart.org/content/arcanoid-starter-set
TEXTURES_FILE = "textures.svg"

# Background file is from https://www.pexels.com/photo/green-parchment-paper-in-close-up-photography-7233117/
BACKGROUND_FILE = "bg.jpg"

BALL_TEXTURE_RECT = pg.rect.Rect(202, 584, 23, 23)
PADDLE_TEXTURE_RECT = pg.rect.Rect(18, 807, 149, 22)

BRICK_TEXTURES_WIDTH = 72
BRICK_TEXTURES_HEIGHT = 32

PURPLE_BRICK_TEXTURE_RECT = pg.rect.Rect(19, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)
ORANGE_BRICK_TEXTURE_RECT = pg.rect.Rect(137, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)
BLUE_BRICK_TEXTURE_RECT = pg.rect.Rect(267, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)
RED_BRICK_TEXTURE_RECT = pg.rect.Rect(400, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)
YELLOW_BRICK_TEXTURE_RECT = pg.rect.Rect(526, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)
GREEN_BRICK_TEXTURE_RECT = pg.rect.Rect(653, 298, BRICK_TEXTURES_WIDTH, BRICK_TEXTURES_HEIGHT)

BRICK_TEXTURES = [
    PURPLE_BRICK_TEXTURE_RECT, ORANGE_BRICK_TEXTURE_RECT, BLUE_BRICK_TEXTURE_RECT,
    RED_BRICK_TEXTURE_RECT,    YELLOW_BRICK_TEXTURE_RECT, GREEN_BRICK_TEXTURE_RECT
]


class Ball(pg.sprite.Sprite):
    def __init__(self, screen, texture, bricks, paddle):
        pg.sprite.Sprite.__init__(self)

        self.screen = screen
        self.texture = texture
        self.image = self.texture
        self.rect = self.image.get_rect()

        # Starting position
        self.default_x = (SCREEN_RECT.x + SCREEN_RECT.width) / 2
        self.default_y = (SCREEN_RECT.y + SCREEN_RECT.height) - 100
        self.default_angle = 45

        self.x = self.default_x
        self.y = self.default_y
        self.angle = self.default_angle

        self.rect.x = self.x
        self.rect.y = self.y

        self.speed = BALL_SPEED
        self.reverse_x = False
        self.reverse_y = False

        self.bricks = bricks
        self.paddle = paddle

        self.delete_counter = 0

    def move(self):
        if self.rect.colliderect(SCREEN_RECT_BOTTOM):
            self.x = self.default_x
            self.y = self.default_y
            self.angle = random.choice([-1, 1]) * self.default_angle
            self.rect.centerx = self.x
            self.rect.centery = self.y
            self.reverse_x = False
            self.reverse_y = False
            return

        (collided_with_left_side_paddle, collided_with_right_side_paddle,
            collided_with_top_side_paddle, collided_with_bottom_side_paddle) = self.check_collision_with_paddle()

        (collided_with_left_side_brick, collided_with_right_side_brick,
            collided_with_top_side_brick, collided_with_bottom_side_brick) = self.check_collision_with_bricks()

        (collided_with_left_side_wall, collided_with_right_side_wall,
            collided_with_top_side_wall, collided_with_bottom_side_wall) = self.check_collision_with_walls()

        # If collided with walls or bricks or paddle on left or right sides
        if (collided_with_left_side_wall or collided_with_right_side_wall or
                collided_with_left_side_paddle or collided_with_right_side_paddle or
                collided_with_left_side_brick or collided_with_right_side_brick):

            self.angle += random.randint(-5, 5)
            self.reverse_x = not self.reverse_x

        sin = math.sin(math.radians(self.angle)) * self.speed

        if self.reverse_x:
            self.x += sin
        else:
            self.x -= sin

        # If collided with ceiling or floor or bricks or paddle on top or bottom sides
        if (collided_with_top_side_wall or collided_with_top_side_paddle or
                collided_with_bottom_side_paddle or collided_with_top_side_brick or
                collided_with_bottom_side_brick):

            self.angle += random.randint(-5, 5)
            self.reverse_y = not self.reverse_y

        cos = math.cos(math.radians(self.angle)) * self.speed

        if self.reverse_y:
            self.y += cos
        else:
            self.y -= cos

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def check_collision_with_bricks(self):
        left, right, top, bottom = False, False, False, False

        i = 0
        while i < len(self.bricks):
            collision = self.rect.clipline(self.bricks[i].leftline)
            should_delete = False
            if collision:
                left = True
                self.rect.midright = (collision[0][0], self.rect.midright[1])
                self.x = self.rect.x
                self.y = self.rect.y
                should_delete = True

            collision = self.rect.clipline(self.bricks[i].rightline)
            if collision:
                right = True
                self.rect.midleft = (collision[0][0], self.rect.midleft[1])
                self.x = self.rect.x
                self.y = self.rect.y
                should_delete = True

            collision = self.rect.clipline(self.bricks[i].topline)
            if collision:
                top = True
                self.rect.midbottom = (self.rect.midbottom[0], collision[0][1])
                self.x = self.rect.x
                self.y = self.rect.y
                should_delete = True

            collision = self.rect.clipline(self.bricks[i].bottomline)
            if collision:
                bottom = True
                self.rect.midtop = (self.rect.midtop[0], collision[0][1])
                self.x = self.rect.x
                self.y = self.rect.y
                should_delete = True

            if should_delete:
                del self.bricks[i]
                i = 0
            else:
                i += 1

        return left, right, top, bottom

    def check_collision_with_paddle(self):
        left, right, top, bottom = False, False, False, False

        collision = self.rect.clipline(self.paddle.leftline)
        if collision:
            left = True
            self.rect.midright = (collision[0][0], self.rect.midright[1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(self.paddle.rightline)
        if collision:
            right = True
            self.rect.midleft = (collision[0][0], self.rect.midleft[1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(self.paddle.topline)
        if collision:
            top = True
            self.rect.midbottom = (self.rect.midbottom[0], collision[0][1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(self.paddle.bottomline)
        if collision:
            bottom = True
            self.rect.midtop = (self.rect.midtop[0], collision[0][1])
            self.x = self.rect.x
            self.y = self.rect.y

        return left, right, top, bottom

    def check_collision_with_walls(self):
        left, right, top, bottom = False, False, False, False

        collision = self.rect.clipline(SCREEN_RECT_LEFT_LINE)
        if collision:
            left = True
            self.rect.midleft = (collision[0][0], self.rect.midleft[1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(SCREEN_RECT_RIGHT_LINE)
        if collision:
            right = True
            self.rect.midright = (collision[0][0], self.rect.midright[1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(SCREEN_RECT_TOP_LINE)
        if collision:
            top = True
            self.rect.midtop = (self.rect.midtop[0], collision[0][1])
            self.x = self.rect.x
            self.y = self.rect.y

        collision = self.rect.clipline(SCREEN_RECT_BOTTOM_LINE)
        if collision:
            bottom = True
            self.rect.midbottom = (self.rect.midbottom[0], collision[0][1])
            self.x = self.rect.x
            self.y = self.rect.y

        return left, right, top, bottom


class Brick(pg.sprite.Sprite):
    def __init__(self, screen, texture, x, y):
        pg.sprite.Sprite.__init__(self)

        self.screen = screen
        self.texture = texture
        self.image = self.texture
        self.rect = self.image.get_rect()

        # Starting position
        self.x = x
        self.y = y

        self.rect.x = self.x
        self.rect.y = self.y

        self.topline = (
            self.rect.x,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y)

        self.bottomline = (
            self.rect.x,
            self.rect.y + self.rect.height,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )

        self.leftline = (
            self.rect.x,
            self.rect.y,
            self.rect.x,
            self.rect.y + self.rect.height
        )

        self.rightline = (
            self.rect.x + self.rect.width,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )

    def draw(self):
        self.screen.blit(self.image, self.rect)


class Paddle(pg.sprite.Sprite):
    def __init__(self, screen, texture):
        pg.sprite.Sprite.__init__(self)

        self.screen = screen
        self.texture = texture
        self.image = self.texture
        self.rect = self.image.get_rect()

        # Starting position
        self.x = (SCREEN_RECT.x + SCREEN_RECT.width) / 2
        self.y = (SCREEN_RECT.y + SCREEN_RECT.height) - 50
        self.speed = 10

        self.rect.x = self.x
        self.rect.y = self.y

        self.topline = (
            self.rect.x,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y)

        self.bottomline = (
            self.rect.x,
            self.rect.y + self.rect.height,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )

        self.leftline = (
            self.rect.x,
            self.rect.y,
            self.rect.x,
            self.rect.y + self.rect.height
        )

        self.rightline = (
            self.rect.x + self.rect.width,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def move_left(self):
        self.x -= self.speed

        if self.x < SCREEN_RECT.x:
            self.x = SCREEN_RECT.x

        self.rect.x = self.x

    def move_right(self):
        self.x += self.speed

        if self.x + self.rect.width > SCREEN_RECT.x + SCREEN_RECT.width:
            self.x = SCREEN_RECT.x + SCREEN_RECT.width - self.rect.width

        self.rect.x = self.x

    def update(self):
        pressed_keys = pg.key.get_pressed()

        if pressed_keys[pg.K_LEFT]:
            self.move_left()
        elif pressed_keys[pg.K_RIGHT]:
            self.move_right()

        self.topline = (
            self.rect.x,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y)

        self.bottomline = (
            self.rect.x,
            self.rect.y + self.rect.height,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )

        self.leftline = (
            self.rect.x,
            self.rect.y,
            self.rect.x,
            self.rect.y + self.rect.height
        )

        self.rightline = (
            self.rect.x + self.rect.width,
            self.rect.y,
            self.rect.x + self.rect.width,
            self.rect.y + self.rect.height
        )


def main():
    pg.init()

    # create a PIL image and blur it
    pil_bg = Image.open(BACKGROUND_FILE).filter(ImageFilter.GaussianBlur(radius=6))

    # Convert it to pygame surface
    background = pg.image.fromstring(pil_bg.tobytes(), pil_bg.size, pil_bg.mode)

    screen = pg.display.set_mode((RES_X, RES_Y))
    clock = pg.time.Clock()
    textures = pg.image.load(TEXTURES_FILE)

    bricks = list()

    y = SCREEN_RECT.y
    for k in range(5):
        indent = 50
        x = SCREEN_RECT.x + indent
        y += BRICK_TEXTURES_HEIGHT
        for i in range(int((SCREEN_RECT.width - indent * 2) / BRICK_TEXTURES_WIDTH)):
            # Choose random texture
            brick_texture = textures.subsurface(BRICK_TEXTURES[random.randint(0, len(BRICK_TEXTURES) - 1)])
            bricks.append(Brick(screen, brick_texture, x, y))
            x += BRICK_TEXTURES_WIDTH

    paddle_texture = textures.subsurface(PADDLE_TEXTURE_RECT)
    ball_texture = textures.subsurface(BALL_TEXTURE_RECT)

    paddle = Paddle(screen, paddle_texture)
    ball = Ball(screen, ball_texture, bricks, paddle)

    while True:
        # Process player inputs.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

        # Do logical updates here.
        # ...
        ball.move()
        paddle.update()

        # Render the graphics here.
        # ...
        screen.blit(background, background.get_rect())

        ball.draw()
        paddle.draw()

        for brick in bricks:
            brick.draw()

        # Debug screen outline
        """
        pg.draw.line(screen, "red", SCREEN_RECT_TOP_LINE[:2], SCREEN_RECT_TOP_LINE[2:], 4)
        pg.draw.line(screen, "red", SCREEN_RECT_BOTTOM_LINE[:2], SCREEN_RECT_BOTTOM_LINE[2:], 4)
        pg.draw.line(screen, "red", SCREEN_RECT_LEFT_LINE[:2], SCREEN_RECT_LEFT_LINE[2:], 4)
        pg.draw.line(screen, "red", SCREEN_RECT_RIGHT_LINE[:2], SCREEN_RECT_RIGHT_LINE[2:], 4)
        """

        pg.display.flip()  # Refresh on-screen display
        clock.tick(MAX_FPS)  # wait until next frame (at MAX_FPS)


if __name__ == "__main__":
    main()
