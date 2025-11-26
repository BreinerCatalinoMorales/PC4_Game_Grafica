# projectile.py
import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        
        self.x = float(x)
        self.y = float(y)
        
        self.direction = direction
        
        self.speed = 8
        if direction == 1:
            self.vel_x = -self.speed
            self.vel_y = 0
        elif direction == 3:
            self.vel_x = self.speed
            self.vel_y = 0
        elif direction == 0:
            self.vel_x = 0
            self.vel_y = -self.speed
        elif direction == 2:
            self.vel_x = 0
            self.vel_y = self.speed
        
        self.rect = pygame.Rect(int(x), int(y), 16, 16)
        
        self.color = (255, 100, 0)
        self.lifetime = 120
        self.alive = True
    
    def update(self, platforms):
        """Actualiza posición del proyectil"""
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return
        
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Colisión con plataformas - FIX AQUÍ
        for platform in platforms:
            # ← CAMBIO: Manejar ambos formatos
            platform_rect = platform['rect'] if isinstance(platform, dict) else platform
            
            if self.rect.colliderect(platform_rect):
                self.alive = False
                print("💥 Impacto!")
    
    def draw(self, surface):
        """Dibuja el proyectil"""
        pygame.draw.circle(surface, self.color, self.rect.center, 8)
        pygame.draw.circle(surface, (255, 200, 0), self.rect.center, 4)

    # projectile.py - Añadir este método a la clase Projectile

    def draw_at(self, surface, pos):
        """Dibuja proyectil en posición específica (para cámara)"""
        pygame.draw.circle(surface, self.color, (pos[0] + 8, pos[1] + 8), 8)
        pygame.draw.circle(surface, (255, 200, 0), (pos[0] + 8, pos[1] + 8), 4)



class Fireball(Projectile):
    """Bola de fuego del mago"""
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.speed = 10
        self.color = (255, 69, 0)
        
        if direction == 1:
            self.vel_x = -self.speed
        elif direction == 3:
            self.vel_x = self.speed
        elif direction == 0:
            self.vel_y = -self.speed
        elif direction == 2:
            self.vel_y = self.speed
