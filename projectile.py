# projectile.py
import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        
        # Posición inicial (centro del jugador)
        self.x = float(x)
        self.y = float(y)
        
        # Dirección (1=izq, 3=der, 0=arriba, 2=abajo)
        self.direction = direction
        
        # Velocidad según dirección
        self.speed = 8
        if direction == 1:  # Izquierda
            self.vel_x = -self.speed
            self.vel_y = 0
        elif direction == 3:  # Derecha
            self.vel_x = self.speed
            self.vel_y = 0
        elif direction == 0:  # Arriba
            self.vel_x = 0
            self.vel_y = -self.speed
        elif direction == 2:  # Abajo
            self.vel_x = 0
            self.vel_y = self.speed
        
        # Hitbox
        self.rect = pygame.Rect(int(x), int(y), 16, 16)
        
        # Visual
        self.color = (255, 100, 0)  # Naranja/fuego
        self.lifetime = 120  # 2 segundos a 60 FPS
        self.alive = True
    
    def update(self, platforms):
        """Actualiza posición del proyectil"""
        # Reducir tiempo de vida
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return
        
        # Mover
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Colisión con plataformas
        for platform in platforms:
            if self.rect.colliderect(platform):
                self.alive = False
                # Aquí puedes añadir efecto de explosión
                print("💥 Impacto!")
    
    def draw(self, surface):
        """Dibuja el proyectil"""
        # Bola de fuego simple (círculo)
        pygame.draw.circle(surface, self.color, self.rect.center, 8)
        # Brillo interior
        pygame.draw.circle(surface, (255, 200, 0), self.rect.center, 4)


class Fireball(Projectile):
    """Bola de fuego del mago"""
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.speed = 10
        self.color = (255, 69, 0)  # Rojo fuego
        
        # Recalcular velocidad con nuevo speed
        if direction == 1:
            self.vel_x = -self.speed
        elif direction == 3:
            self.vel_x = self.speed
        elif direction == 0:
            self.vel_y = -self.speed
        elif direction == 2:
            self.vel_y = self.speed
