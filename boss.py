# boss.py
import pygame

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 64, 128)
        self.attack_pattern = "punch_high"
        self.timer = 0
        self.attack_cooldown = 60  # frames
        
        # Hitbox del ataque (deja 2 bloques libres abajo)
        self.attack_hitbox = None
    
    def update(self):
        self.timer += 1
        
        if self.timer >= self.attack_cooldown:
            self.attack()
            self.timer = 0
        else:
            self.attack_hitbox = None
    
    def attack(self):
        # Crea hitbox que deja espacio de 2 bloques (128px) abajo
        self.attack_hitbox = pygame.Rect(
            self.rect.x - 100, 
            self.rect.y, 
            self.rect.width + 100, 
            self.rect.height - 128  # Deja 2 bloques libres
        )
    
    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
        if self.attack_hitbox:
            pygame.draw.rect(surface, (255, 100, 100), self.attack_hitbox, 2)
