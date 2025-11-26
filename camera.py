# camera.py
import pygame
from config import WIDTH, HEIGHT

class Camera:
    def __init__(self, level_width, level_height):
        self.camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.width = level_width
        self.height = level_height
        
        # Zona muerta (el jugador puede moverse aquí sin mover la cámara)
        self.deadzone_width = WIDTH // 3
        self.deadzone_height = HEIGHT // 3
        
    def apply(self, entity_rect):
        """Aplica el offset de cámara a un rect"""
        return entity_rect.move(-self.camera.x, -self.camera.y)
    
    def apply_pos(self, x, y):
        """Aplica el offset de cámara a una posición"""
        return (x - self.camera.x, y - self.camera.y)
    
    def update(self, target_rect):
        """Actualiza la posición de la cámara siguiendo al jugador"""
        # Calcular el centro del jugador
        player_center_x = target_rect.centerx
        player_center_y = target_rect.centery
        
        # Centro de la cámara
        camera_center_x = self.camera.x + WIDTH // 2
        camera_center_y = self.camera.y + HEIGHT // 2
        
        # Mover cámara horizontalmente si el jugador sale de la zona muerta
        if player_center_x > camera_center_x + self.deadzone_width // 2:
            self.camera.x += player_center_x - (camera_center_x + self.deadzone_width // 2)
        elif player_center_x < camera_center_x - self.deadzone_width // 2:
            self.camera.x += player_center_x - (camera_center_x - self.deadzone_width // 2)
        
        # Mover cámara verticalmente
        if player_center_y > camera_center_y + self.deadzone_height // 2:
            self.camera.y += player_center_y - (camera_center_y + self.deadzone_height // 2)
        elif player_center_y < camera_center_y - self.deadzone_height // 2:
            self.camera.y += player_center_y - (camera_center_y - self.deadzone_height // 2)
        
        # Limitar la cámara a los bordes del nivel
        self.camera.x = max(0, min(self.camera.x, self.width - WIDTH))
        self.camera.y = max(0, min(self.camera.y, self.height - HEIGHT))
