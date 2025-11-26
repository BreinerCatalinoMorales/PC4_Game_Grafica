# player.py - ARCHIVO COMPLETO CORREGIDO
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_type, base_path):
        super().__init__()
        
        # Configuración básica
        self.character_type = character_type
        self.base_path = base_path
        
        # Posición y física
        self.rect = pygame.Rect(x, y, 48, 60)
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4
        self.jump_power = 12
        self.gravity = 0.6
        self.on_ground = False
        
        # Doble salto
        self.max_jumps = 2
        self.jumps_left = self.max_jumps
        
        # Animación
        self.current_animation = "walk"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 8
        self.direction = 2
        
        # Estados
        self.is_casting = False
        self.is_hurt = False
        self.hurt_timer = 0
        
        # Sprites
        self.animations = {}
        self.frame_counts = {}
    
    def _combine_layers(self, layer_files, animation_folder):
        """Combina múltiples capas de sprites"""
        first_layer = pygame.image.load(f"{self.base_path}/{animation_folder}/{layer_files[0]}")
        combined = pygame.Surface(first_layer.get_size(), pygame.SRCALPHA)
        
        for layer_file in layer_files:
            try:
                layer = pygame.image.load(f"{self.base_path}/{animation_folder}/{layer_file}")
                combined.blit(layer, (0, 0))
            except:
                pass
        
        return combined
    
    def update(self, keys, platforms):
        """Actualiza lógica del jugador"""
        
        # Manejo de hurt
        if self.is_hurt:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.is_hurt = False
        
        # Solo permitir control si no está lanzando o herido
        if not self.is_casting and not self.is_hurt:
            # Movimiento horizontal
            self.vel_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -self.speed
                self.direction = 1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.speed
                self.direction = 3
            
            # Salto con doble salto
            if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]):
                if self.jumps_left > 0 and not hasattr(self, '_jump_pressed'):
                    self.vel_y = -self.jump_power
                    self.jumps_left -= 1
                    self.on_ground = False
                    self._jump_pressed = True
            else:
                if hasattr(self, '_jump_pressed'):
                    delattr(self, '_jump_pressed')
        else:
            self.vel_x = 0
        
        # Aplicar gravedad
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Movimiento horizontal
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
        # Colisiones horizontales
        for platform in platforms:
            platform_rect = platform['rect'] if isinstance(platform, dict) else platform
            
            if self.rect.colliderect(platform_rect):
                if self.vel_x > 0:
                    self.rect.right = platform_rect.left
                    self.x = self.rect.x
                elif self.vel_x < 0:
                    self.rect.left = platform_rect.right
                    self.x = self.rect.x
        
        # Movimiento vertical
        self.y += self.vel_y
        self.rect.y = int(self.y)
        
        # Colisiones verticales
        self.on_ground = False
        for platform in platforms:
            platform_rect = platform['rect'] if isinstance(platform, dict) else platform
            
            if self.rect.colliderect(platform_rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform_rect.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumps_left = self.max_jumps
                elif self.vel_y < 0:
                    self.rect.top = platform_rect.bottom
                    self.y = self.rect.y
                    self.vel_y = 0
        
        # Actualizar animación
        self._update_animation()
    
    def _update_animation(self):
        """Actualiza el frame actual de la animación"""
        
        if self.is_hurt:
            self.current_animation = "hurt"
        elif self.is_casting:
            self.current_animation = "spell"
        elif abs(self.vel_x) > 0:
            self.current_animation = "walk"
        else:
            if self.current_animation == "walk":
                self.current_frame = 0
                return
        
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            max_frames = self.frame_counts[self.current_animation]
            
            if self.current_animation in ["spell", "hurt"]:
                if self.current_frame < max_frames - 1:
                    self.current_frame += 1
                else:
                    if self.is_casting:
                        self.is_casting = False
                        self.on_spell_complete()
                    if self.is_hurt:
                        self.is_hurt = False
                    
                    self.current_frame = 0
                    self.current_animation = "walk"
            else:
                self.current_frame = (self.current_frame + 1) % max_frames
            
            self.frame_counter = 0
    
    def on_spell_complete(self):
        """Callback cuando termina animación de spell"""
        pass
    
    def get_current_frame(self):
        """Obtiene el frame actual del sprite sheet"""
        current_sheet = self.animations[self.current_animation]
        
        num_directions = current_sheet.get_height() // 64
        actual_direction = 0 if num_directions == 1 else self.direction
        
        frame_x = self.current_frame * 64
        frame_y = actual_direction * 64
        
        return current_sheet.subsurface(pygame.Rect(frame_x, frame_y, 64, 64))
    
    def draw(self, surface):
        """Dibuja el jugador en pantalla"""
        frame = self.get_current_frame()
        
        draw_x = self.rect.x - 8
        draw_y = self.rect.y - 4
        
        surface.blit(frame, (draw_x, draw_y))
        
    # player.py - Añadir este método a la clase Player

    def draw_at(self, surface, pos):
        """Dibuja el jugador en una posición específica (para cámara)"""
        frame = self.get_current_frame()
        
        # Centrar sprite sobre hitbox
        draw_x = pos[0] - 8
        draw_y = pos[1] - 4
        
        surface.blit(frame, (draw_x, draw_y))

    def use_ability(self):
        """Método abstracto - implementar en clases hijas"""
        pass
    
    def take_damage(self):
        """Recibe daño del jefe"""
        if not self.is_hurt:
            self.is_hurt = True
            self.hurt_timer = 30
            self.current_frame = 0
            print("💔 Jugador recibe daño!")
    