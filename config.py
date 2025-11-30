import pygame

pygame.init()
display_info = pygame.display.Info()
NATIVE_WIDTH = display_info.current_w
NATIVE_HEIGHT = display_info.current_h

DISPLAY_MODE = "windowed"
ALLOW_RESIZE = True

if DISPLAY_MODE == "fullscreen":
    WIDTH = NATIVE_WIDTH
    HEIGHT = NATIVE_HEIGHT
elif DISPLAY_MODE == "borderless":
    WIDTH = NATIVE_WIDTH
    HEIGHT = NATIVE_HEIGHT
else:
    WIDTH = int(NATIVE_WIDTH * 0.8)
    HEIGHT = int(NATIVE_HEIGHT * 0.8)

TILE_SIZE = 64
WIDTH = (WIDTH // TILE_SIZE) * TILE_SIZE
HEIGHT = (HEIGHT // TILE_SIZE) * TILE_SIZE

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

GRAVITY = 0.6
PLAYER_SPEED = 4
JUMP_POWER = 12