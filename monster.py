import pygame
import random
import math

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, monster_type="goblin"):
        super().__init__()
        
        self.monster_type = monster_type
        self.base_path = f"Monsters_Creatures_Fantasy/Monsters_Creatures_Fantasy"
        
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x), int(y), 80, 80)
        
        self.speed = 1.0
        self.vel_x = 0
        self.vel_y = 0
        
        if monster_type == "flying_eye":
            self.is_flying = True
            self.gravity = 0
        else:
            self.is_flying = False
            self.gravity = 0.4
        
        self.alive = True
        self.health = 1
        self.on_ground = False
        
        self.current_animation = "idle" if not self.is_flying else "flight"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 8
        self.direction = 1
        
        self.is_attacking = False
        self.is_dying = False
        self.death_timer = 0
        
        self.detection_range = 400
        self.is_tracking = False
        
        self.wander_timer = 0
        self.wander_direction = random.choice([-1, 1])
        
        self.animations = {}
        self.frame_counts = {}
        self.load_sprites()
    
    def load_sprites(self):
        try:
            type_folders = {
                "flying_eye": "Flying eye",
                "goblin": "Goblin",
                "skeleton": "Skeleton",
                "mushroom": "Mushroom"
            }
            
            folder = type_folders.get(self.monster_type, "Goblin")
            base = f"{self.base_path}/{folder}"
            
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
            else:
                anim_map = {
                    "idle": "Idle.png",
                    "walk": "Walk.png",
                    "attack": "Attack.png",
                    "death": "Death.png",
                    "hurt": "Take Hit.png"
                }
            
            for anim_name, filename in anim_map.items():
                try:
                    sprite = pygame.image.load(f"{base}/{filename}")
                    self.animations[anim_name] = sprite
                    
                    frame_width = 150
                    num_frames = max(1, sprite.get_width() // frame_width)
                    self.frame_counts[anim_name] = num_frames
                    
                except Exception:
                    pass
            
            if not self.animations:
                raise Exception()
                
        except Exception:
            self.animations = {"idle": pygame.Surface((150, 150))}
            self.animations["idle"].fill((255, 0, 255))
            self.frame_counts = {"idle": 1}
    
    def update_ai(self, player, game):
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.alive = False
            return
        
        player_is_camouflaged = game.current_color == "background"
        
        if player_is_camouflaged:
            self.is_tracking = False
            
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                self.wander_timer = random.randint(60, 120)
                self.wander_direction = random.choice([-1, 0, 1])
            
            if self.is_flying:
                if self.wander_direction != 0:
                    self.vel_x = self.speed * 0.5 * self.wander_direction
                    self.direction = 3 if self.wander_direction > 0 else 1
                else:
                    self.vel_x = 0
                
                if random.random() < 0.02:
                    self.vel_y = random.choice([-self.speed * 0.5, 0, self.speed * 0.5])
                
                self.current_animation = "flight"
            else:
                if self.wander_direction != 0:
                    self.vel_x = self.speed * 0.5 * self.wander_direction
                    self.direction = 3 if self.wander_direction > 0 else 1
                    self.current_animation = "walk"
                else:
                    self.vel_x = 0
                    self.current_animation = "idle"
        else:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.detection_range:
                self.is_tracking = True
                
                if self.is_flying:
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
        
        if not self.is_flying:
            self.vel_y += self.gravity
            if self.vel_y > 15:
                self.vel_y = 15
        
        self._update_animation()
    
    def update_movement(self, platforms):
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
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
        
        self.y += self.vel_y
        self.rect.y = int(self.y)
        
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
            else:
                self.current_frame = (self.current_frame + 1) % max_frames
            
            self.frame_counter = 0
    
    def check_collision_with_player(self, player):
        return self.rect.colliderect(player.rect) and not self.is_dying
    
    def take_damage(self):
        if not self.is_dying:
            self.health -= 1
            if self.health <= 0:
                self.is_dying = True
                self.death_timer = 30
                self.current_frame = 0
                return True
        return False
    
    def get_current_frame(self):
        if self.current_animation not in self.animations:
            self.current_animation = list(self.animations.keys())[0]
        
        current_sheet = self.animations[self.current_animation]
        
        frame_width = 150
        frame_height = 150
        
        frame_x = self.current_frame * frame_width
        frame_y = 0
        
        try:
            return current_sheet.subsurface(pygame.Rect(frame_x, frame_y, frame_width, frame_height))
        except:
            return current_sheet
    
    def draw_with_camera(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        
        frame = self.get_current_frame()
        
        scaled_frame = pygame.transform.scale(frame, (self.rect.width + 20, self.rect.height + 20))
        
        if self.direction == 1:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
        
        draw_x = screen_rect.x - 10
        draw_y = screen_rect.y - 10
        
        surface.blit(scaled_frame, (draw_x, draw_y))