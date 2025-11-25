# main.py
import pygame
from config import *
from mage import Mage
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.current_level = 1
        self.current_section = 1
        self.game_state = "playing"
        
        self.projectiles = []  # ← AÑADIR lista de proyectiles
        
        self.load_level(1, 1)
    
    def load_level(self, level_num, section_num):
        """Carga nivel y crea el personaje correspondiente"""
        self.level = Level(f"levels/level{level_num}_section{section_num}.txt")
        
        # Crear personaje según el nivel
        if level_num <= 2:
            self.player = Mage(100, 100)
        
        # Limpiar proyectiles al cambiar de nivel
        self.projectiles = []
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event.key)
            
            if self.game_state == "playing":
                self.update()
                self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    # main.py - Solo la parte que cambia
    def handle_keypress(self, key):
        """Maneja teclas especiales"""
        if key == pygame.K_f:
            self.player.use_ability()  # Solo inicia la animación
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Actualizar jugador y obtener proyectil si se creó
        projectile = self.player.update(keys, self.level.platforms)
        if projectile:
            self.projectiles.append(projectile)
            print(f"🔥 Bola de fuego disparada! Total: {len(self.projectiles)}")
        
        self.level.update(self.player)
        
        # Actualizar proyectiles
        for proj in self.projectiles[:]:
            proj.update(self.level.platforms)
            if not proj.alive:
                self.projectiles.remove(proj)
        
        # Verificar transición de sección
        if self.level.check_section_complete(self.player):
            self.current_section += 1
            self.load_level(self.current_level, self.current_section)

    
    def draw(self):
        self.screen.fill((20, 20, 20))
        self.level.draw(self.screen)
        
        # Dibujar proyectiles
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        self.player.draw(self.screen)
        
        # UI: Cooldown indicator
        if self.player.cast_cooldown > 0:
            font = pygame.font.Font(None, 25)
            text = font.render(f"Cooldown: {self.player.cast_cooldown}", True, (255, 0, 0))
            self.screen.blit(text, (10, 40))


# Punto de entrada
if __name__ == "__main__":
    game = Game()
    game.run()
