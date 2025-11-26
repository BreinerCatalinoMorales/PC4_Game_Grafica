# config.py
import pygame

# Configuración de pantalla
pygame.init()
display_info = pygame.display.Info()
NATIVE_WIDTH = display_info.current_w
NATIVE_HEIGHT = display_info.current_h

# Modos disponibles: "windowed", "fullscreen", "borderless"
DISPLAY_MODE = "windowed"
ALLOW_RESIZE = True  # ← AÑADIR: Habilita botón maximizar/redimensionar

if DISPLAY_MODE == "fullscreen":
    WIDTH = NATIVE_WIDTH
    HEIGHT = NATIVE_HEIGHT
elif DISPLAY_MODE == "borderless":
    WIDTH = NATIVE_WIDTH
    HEIGHT = NATIVE_HEIGHT
else:  # windowed
    # 80% del tamaño de pantalla
    WIDTH = int(NATIVE_WIDTH * 0.8)
    HEIGHT = int(NATIVE_HEIGHT * 0.8)

# Asegurar múltiplos de TILE_SIZE
TILE_SIZE = 64
WIDTH = (WIDTH // TILE_SIZE) * TILE_SIZE
HEIGHT = (HEIGHT // TILE_SIZE) * TILE_SIZE

FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Física
GRAVITY = 0.6
PLAYER_SPEED = 4
JUMP_POWER = 12

print(f"🖥️ Monitor: {NATIVE_WIDTH}x{NATIVE_HEIGHT}")
print(f"🎮 Modo: {DISPLAY_MODE.upper()} - Ventana: {WIDTH}x{HEIGHT}")
