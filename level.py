# level.py
import pygame
from config import TILE_SIZE  # ← AÑADIR ESTA LÍNEA

class Level:
    def __init__(self, level_file):
        self.platforms = []
        self.goal = None
        self.boss = None
        self.load_from_file(level_file)
    
    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            for row, line in enumerate(lines):
                for col, char in enumerate(line):
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    
                    if char == '#':  # Plataforma
                        platform = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                        self.platforms.append(platform)
                    elif char == 'G':  # Meta (goal)
                        self.goal = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    elif char == 'B':  # Spawn del Boss
                        from boss import Boss
                        self.boss = Boss(x, y)
    
    def check_section_complete(self, player):
        if self.goal and player.rect.colliderect(self.goal):
            return True
        return False
    
    def update(self, player):
        """Actualizar lógica del nivel"""
        if self.boss:
            self.boss.update()
            # Verificar si el jugador pasó al jefe
            if player.rect.x > self.boss.rect.x + 100:
                return "level_complete"
    
    def draw(self, surface):
        """Dibujar el nivel"""
        # Dibujar plataformas
        for platform in self.platforms:
            pygame.draw.rect(surface, (100, 100, 100), platform)
        
        # Dibujar meta
        if self.goal:
            pygame.draw.rect(surface, (0, 255, 0), self.goal, 3)
        
        # Dibujar boss
        if self.boss:
            self.boss.draw(surface)
