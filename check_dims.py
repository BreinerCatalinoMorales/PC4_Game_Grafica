import pygame
import os

pygame.init()
base_path = r"c:\Users\estcm\Music\UNI25-1\PC-GRAFICA\PC4_Game_Grafica\Undead executioner\Undead executioner puppet\png"
files = ["attacking.png", "idle.png", "skill1.png"]

print(f"Checking in {base_path}")
for f in files:
    path = os.path.join(base_path, f)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            print(f"{f}: {img.get_width()}x{img.get_height()}")
        except Exception as e:
            print(f"Error loading {f}: {e}")
    else:
        print(f"File not found: {f}")
