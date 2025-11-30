import pygame
import os

pygame.init()

# Use relative path or update base_path as needed
base_path = "assets/images/enemies" # Example default path, change as needed
files = ["attacking.png", "idle.png", "skill1.png"] # Add files you want to check here

if not os.path.exists(base_path):
    print(f"Warning: Base path '{base_path}' not found. Checking current directory instead.")
    base_path = "."

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