# monster.py - Sistema de monstruos con IA, camuflaje y tipos voladores/terrestres
import pygame
import random
import math

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, monster_type="goblin"):
        super().__init__()
        
        self.monster_type = monster_type
        self.base_path = f"Monsters_Creatures_Fantasy/Monsters_Creatures_Fantasy"
        
        # Posición y física
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x), int(y), 80, 80)  # Aún más grande: 80x80
        
        # Velocidad (reducida aún más para mejor jugabilidad)
        self.speed = 1.0  # Reducido de 1.25
        self.vel_x = 0
        self.vel_y = 0
        
        # Física según tipo
        if monster_type == "flying_eye":
            self.is_flying = True
            self.gravity = 0
        else:
            self.is_flying = False
            self.gravity = 0.4
        
        # Estado
        self.alive = True
        self.health = 1  # Muere con un disparo
        self.on_ground = False
        
        # Animación
        self.current_animation = "idle" if not self.is_flying else "flight"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 8
        self.direction = 1  # 0=arriba, 1=izquierda, 2=abajo, 3=derecha
        
        # Estados de animación
        self.is_attacking = False
        self.is_dying = False
        self.death_timer = 0
        
        # Detección del jugador
        self.detection_range = 400
        self.is_tracking = False
        
        # Movimiento aleatorio (para cuando está camuflado)
        self.wander_timer = 0
        self.wander_direction = random.choice([-1, 1])  # -1 = izquierda, 1 = derecha
        
        # Sprites
        self.animations = {}
        self.frame_counts = {}
        self.load_sprites()
    
    def load_sprites(self):
        """Carga sprites según tipo de monstruo"""
        try:
            type_folders = {
                "flying_eye": "Flying eye",
                "goblin": "Goblin",
                "skeleton": "Skeleton",
                "mushroom": "Mushroom"
            }
            
            folder = type_folders.get(self.monster_type, "Goblin")
            base = f"{self.base_path}/{folder}"
            
            # Animaciones según tipo
            if self.monster_type == "flying_eye":
                anim_map = {
                    "flight": "Flight.png",
                    "attack": "Attack.png",
                    "death": "Death.png",
                    "hurt": "Take Hit.png"
                }
            elif self.monster_type == "goblin":
                anim_map = {
                    "idle": "Idle.png",
                    "walk": "Run.png",
                    "attack": "Attack.png",
                    "death": "Death.png",
                    "hurt": "Take Hit.png"
                }
            elif self.monster_type == "skeleton":
                anim_map = {
                    "idle": "Idle.png",
                    "walk": "Walk.png",
                    "attack": "Attack.png",
                    "death": "Death.png",
                    "hurt": "Take Hit.png"
                }
            else:  # mushroom por defecto usa skeleton
                anim_map = {
                    "idle": "Idle.png",
                    "walk": "Walk.png",
                    "attack": "Attack.png",
                    "death": "Death.png",
                    "hurt": "Take Hit.png"
                }
            
            # Cargar animaciones
            for anim_name, filename in anim_map.items():
                try:
                    sprite = pygame.image.load(f"{base}/{filename}")
                    self.animations[anim_name] = sprite
                    
                    # Calcular frames (asumiendo 150px por frame horizontalmente)
                    frame_width = 150
                    num_frames = max(1, sprite.get_width() // frame_width)
                    self.frame_counts[anim_name] = num_frames
                    
                except Exception as e:
                    print(f"⚠ No se pudo cargar {filename}: {e}")
            
            if not self.animations:
                raise Exception("No se cargaron animaciones")
                
            print(f"✓ Monstruo {self.monster_type} cargado con {len(self.animations)} animaciones")
            
        except Exception as e:
            print(f"❌ Error cargando sprites de {self.monster_type}: {e}")
            # Crear sprite de fallback
            self.animations = {"idle": pygame.Surface((150, 150))}
            self.animations["idle"].fill((255, 0, 255))
            self.frame_counts = {"idle": 1}
    
    def update_ai(self, player, game):
        """Actualiza IA del monstruo: detección y persecución del jugador"""
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.alive = False
            return
        
        # Sistema de camuflaje: ignorar al jugador si tiene color "background"
        player_is_camouflaged = game.current_color == "background"
        
        if player_is_camouflaged:
            # Jugador invisible, moverse aleatoriamente
            self.is_tracking = False
            
            # Sistema de vagabundeo aleatorio
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                # Cambiar dirección aleatoriamente cada 60-120 frames
                self.wander_timer = random.randint(60, 120)
                self.wander_direction = random.choice([-1, 0, 1])  # -1=izquierda, 0=quieto, 1=derecha
            
            if self.is_flying:
                # Voladores también se mueven en Y
                if self.wander_direction != 0:
                    self.vel_x = self.speed * 0.5 * self.wander_direction
                    self.direction = 3 if self.wander_direction > 0 else 1
                else:
                    self.vel_x = 0
                
                # Movimiento vertical aleatorio
                if random.random() < 0.02:  # 2% de chance de cambiar Y
                    self.vel_y = random.choice([-self.speed * 0.5, 0, self.speed * 0.5])
                
                self.current_animation = "flight"
            else:
                # Terrestres solo en X
                if self.wander_direction != 0:
                    self.vel_x = self.speed * 0.5 * self.wander_direction
                    self.direction = 3 if self.wander_direction > 0 else 1
                    self.current_animation = "walk"
                else:
                    self.vel_x = 0
                    self.current_animation = "idle"
        else:
            # Calcular distancia al jugador
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            # Detectar jugador si está en rango
            if distance < self.detection_range:
                self.is_tracking = True
                
                # Perseguir jugador
                if self.is_flying:
                    # Voladores: seguir en X e Y
                    if abs(dx) > 10:
                        self.vel_x = self.speed if dx > 0 else -self.speed
                        self.direction = 3 if dx > 0 else 1
                    else:
                        self.vel_x = 0
                    
                    if abs(dy) > 10:
                        self.vel_y = self.speed if dy > 0 else -self.speed
                    else:
                        self.vel_y = 0
                    
                    self.current_animation = "flight"
                else:
                    # Terrestres: solo seguir en X
                    if abs(dx) > 20:
                        self.vel_x = self.speed if dx > 0 else -self.speed
                        self.direction = 3 if dx > 0 else 1
                        self.current_animation = "walk"
                    else:
                        self.vel_x = 0
                        self.current_animation = "idle"
            else:
                self.is_tracking = False
                self.vel_x = 0
                self.current_animation = "idle" if not self.is_flying else "flight"
        
        # Aplicar física
        if not self.is_flying:
            self.vel_y += self.gravity
            if self.vel_y > 15:
                self.vel_y = 15
        
        # Actualizar animación
        self._update_animation()
    
    def update_movement(self, platforms):
        """Actualiza posición del monstruo con colisiones"""
        # Movimiento horizontal
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
        # Colisiones horizontales (solo terrestres)
        if not self.is_flying:
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
        
        # Colisiones verticales (solo terrestres)
        if not self.is_flying:
            self.on_ground = False
            for platform in platforms:
                platform_rect = platform['rect'] if isinstance(platform, dict) else platform
                
                if self.rect.colliderect(platform_rect):
                    if self.vel_y > 0:
                        self.rect.bottom = platform_rect.top
                        self.y = self.rect.y
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = platform_rect.bottom
                        self.y = self.rect.y
                        self.vel_y = 0
    
    def _update_animation(self):
        """Actualiza el frame actual de la animación"""
        if self.is_dying:
            self.current_animation = "death"
        
        if self.current_animation not in self.frame_counts:
            return
        
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            max_frames = self.frame_counts[self.current_animation]
            
            if self.current_animation == "death":
                if self.current_frame < max_frames - 1:
                    self.current_frame += 1
                # No resetear, quedarse en último frame
            else:
                self.current_frame = (self.current_frame + 1) % max_frames
            
            self.frame_counter = 0
    
    def check_collision_with_player(self, player):
        """Verifica colisión con el jugador"""
        return self.rect.colliderect(player.rect) and not self.is_dying
    
    def take_damage(self):
        """Recibe daño de proyectil"""
        if not self.is_dying:
            self.health -= 1
            if self.health <= 0:
                self.is_dying = True
                self.death_timer = 30  # Duración de animación de muerte
                self.current_frame = 0
                print(f"💀 {self.monster_type} eliminado!")
                return True  # Murió
        return False
    
    def get_current_frame(self):
        """Obtiene el frame actual del sprite sheet"""
        if self.current_animation not in self.animations:
            # Fallback a primera animación disponible
            self.current_animation = list(self.animations.keys())[0]
        
        current_sheet = self.animations[self.current_animation]
        
        # Frame dimensions (asumiendo 150x150)
        frame_width = 150
        frame_height = 150
        
        frame_x = self.current_frame * frame_width
        frame_y = 0  # La mayoría de estos sprites tienen una sola fila
        
        try:
            return current_sheet.subsurface(pygame.Rect(frame_x, frame_y, frame_width, frame_height))
        except:
            return current_sheet
    
    def draw_with_camera(self, surface, camera):
        """Dibuja el monstruo con sistema de cámara"""
        screen_rect = camera.apply(self.rect)
        
        frame = self.get_current_frame()
        
        # Escalar de 150x150 a tamaño del hitbox
        scaled_frame = pygame.transform.scale(frame, (self.rect.width + 20, self.rect.height + 20))
        
        # Voltear si mira a la izquierda
        if self.direction == 1:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
        
        # Centrar sprite sobre hitbox
        draw_x = screen_rect.x - 10
        draw_y = screen_rect.y - 10
        
        surface.blit(scaled_frame, (draw_x, draw_y))
