# player.py - ARCHIVO COMPLETO
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
        
        # Animación
        self.current_animation = "walk"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 8
        self.direction = 2  # 0=up, 1=left, 2=down, 3=right
        
        # Estados
        self.is_casting = False
        self.is_hurt = False
        self.hurt_timer = 0
        
        # Sprites (se cargan en clases hijas)
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
            
            # Salto
            if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = -self.jump_power
                self.on_ground = False
        else:
            # No moverse si está lanzando hechizo
            self.vel_x = 0
        
        # Aplicar gravedad
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Actualizar posición
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Colisiones con plataformas
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Colisión desde arriba
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                # Colisión desde abajo
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.y = self.rect.y
                    self.vel_y = 0
        
        # Actualizar animación
        self._update_animation()
    
    def _update_animation(self):
        """Actualiza el frame actual de la animación"""
        
        # Determinar qué animación usar
        if self.is_hurt:
            self.current_animation = "hurt"
        elif self.is_casting:
            self.current_animation = "spell"
        elif abs(self.vel_x) > 0:
            self.current_animation = "walk"
        else:
            # Idle = primer frame de walk
            if self.current_animation == "walk":
                self.current_frame = 0
                return
        
        # Avanzar frame
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            max_frames = self.frame_counts[self.current_animation]
            
            # Animaciones que NO hacen loop (una sola vez)
            if self.current_animation in ["spell", "hurt"]:
                # Avanzar sin loop
                if self.current_frame < max_frames - 1:
                    self.current_frame += 1
                else:
                    # Llegó al final, terminar animación
                    if self.is_casting:
                        self.is_casting = False
                        self.on_spell_complete()
                    if self.is_hurt:
                        self.is_hurt = False
                    
                    # Volver a idle
                    self.current_frame = 0
                    self.current_animation = "walk"
            else:
                # Walk sí hace loop
                self.current_frame = (self.current_frame + 1) % max_frames
            
            self.frame_counter = 0
    
    def on_spell_complete(self):
        """Callback cuando termina animación de spell"""
        pass  # Sobrescrito por clases hijas
    
    def get_current_frame(self):
        """Obtiene el frame actual del sprite sheet"""
        current_sheet = self.animations[self.current_animation]
        
        # Detectar si tiene múltiples direcciones
        num_directions = current_sheet.get_height() // 64
        actual_direction = 0 if num_directions == 1 else self.direction
        
        # Extraer frame
        frame_x = self.current_frame * 64
        frame_y = actual_direction * 64
        
        return current_sheet.subsurface(pygame.Rect(frame_x, frame_y, 64, 64))
    
    def draw(self, surface):
        """Dibuja el jugador en pantalla"""
        frame = self.get_current_frame()
        
        # Centrar sprite sobre hitbox
        draw_x = self.rect.x - 8
        draw_y = self.rect.y - 4
        
        surface.blit(frame, (draw_x, draw_y))
        
        # Debug: dibujar hitbox (comentar después)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
    
    def use_ability(self):
        """Método abstracto - implementar en clases hijas"""
        pass
