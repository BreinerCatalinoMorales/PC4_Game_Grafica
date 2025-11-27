import pygame
import os
from undead_executioner import UndeadExecutioner

pygame.init()
pygame.display.set_mode((800, 600))

print(f"CWD: {os.getcwd()}")

try:
    boss = UndeadExecutioner(100, 100)
    print("Boss created successfully")
    print(f"Idle frames: {len(boss.idle_frames)}")
except Exception as e:
    print(f"Failed to create boss: {e}")
    import traceback
    traceback.print_exc()
