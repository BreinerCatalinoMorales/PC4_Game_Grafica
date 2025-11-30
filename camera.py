import pygame
from config import WIDTH, HEIGHT

class Camera:
    def __init__(self, level_width, level_height):
        self.camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.width = level_width
        self.height = level_height
        
        self.deadzone_width = WIDTH // 3
        self.deadzone_height = HEIGHT // 3
        
    def apply(self, entity_rect):
        return entity_rect.move(-self.camera.x, -self.camera.y)
    
    def apply_pos(self, x, y):
        return (x - self.camera.x, y - self.camera.y)
    
    def update(self, target_rect):
        player_center_x = target_rect.centerx
        player_center_y = target_rect.centery
        
        camera_center_x = self.camera.x + WIDTH // 2
        camera_center_y = self.camera.y + HEIGHT // 2
        
        if player_center_x > camera_center_x + self.deadzone_width // 2:
            self.camera.x += player_center_x - (camera_center_x + self.deadzone_width // 2)
        elif player_center_x < camera_center_x - self.deadzone_width // 2:
            self.camera.x += player_center_x - (camera_center_x - self.deadzone_width // 2)
        
        if player_center_y > camera_center_y + self.deadzone_height // 2:
            self.camera.y += player_center_y - (camera_center_y + self.deadzone_height // 2)
        elif player_center_y < camera_center_y - self.deadzone_height // 2:
            self.camera.y += player_center_y - (camera_center_y - self.deadzone_height // 2)
        
        self.camera.x = max(0, min(self.camera.x, self.width - WIDTH))
        self.camera.y = max(0, min(self.camera.y, self.height - HEIGHT))