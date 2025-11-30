# boss.py - COMPLETO CON MOVIMIENTO, PATRÓN Y CÁMARA
import pygame

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, boss_type="andromalius"):
        super().__init__()
        
        self.boss_type = boss_type
        self.sprite_path = f"assets/images/enemies/{boss_type}.png"
        self.load_sprite()
        
        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, self.display_width, self.display_height)
        
        # MOVIMIENTO
        self.move_speed = 2
        self.patrol_distance = 200
        self.direction = 1
        self.move_timer = 0
        self.is_moving = True
        
        # PATRÓN DE ATAQUE
        self.attack_pattern = [
            {'delay': 60, 'count': 3, 'spread': 20},
            {'delay': 90, 'count': 1, 'spread': 0},
            {'delay': 60, 'count': 5, 'spread': 15},
            {'delay': 120, 'count': 1, 'spread': 0},
        ]
        self.current_pattern_index = 0
        self.attack_timer = 0
        self.telegraph_timer = 0
        
        self.projectiles = []
        self.projectile_type = self.get_projectile_type()
        
        self.safe_zone_height = 128
        
        self.current_frame = 0
        self.animation_speed = 10
        self.animation_counter = 0
        
        self.health = 100
        self.facing_left = True
    
    def get_projectile_type(self):
        projectile_map = {
            "andromalius": "acid2",
            "gnu": "flameball",
            "mage-1": "mage-bullet",
            "mage-2": "mage-bullet",
            "mage-3": "mage-bullet",
            "disciple": "acid2",
            "shadow": "flameball",
            "tentacles": "acid2",
            "minion": "flameball"
        }
        return projectile_map.get(self.boss_type, "flameball")
    
    def load_sprite(self):
        try:
            self.sprite_sheet = pygame.image.load(self.sprite_path)
            self.frame_width, self.frame_height = self.get_frame_dimensions()
            self.num_frames = self.sprite_sheet.get_width() // self.frame_width
            self.scale_factor = 5.0
            self.display_width = int(self.frame_width * self.scale_factor)
            self.display_height = int(self.frame_height * self.scale_factor)
        except Exception:
            # Fallback en silencio
            self.sprite_sheet = None
            self.frame_width = 64
            self.frame_height = 128
            self.num_frames = 1
            self.display_width = 64
            self.display_height = 128
    
    def get_frame_dimensions(self):
        dimensions = {
            "andromalius": (57, 88),
            "disciple": (45, 51),
            "gnu": (120, 100),
            "mage-1": (85, 94),
            "mage-2": (122, 110),
            "mage-3": (87, 110),
            "shadow": (80, 70),
            "tentacles": (25, 90),
            "minion": (45, 66)
        }
        return dimensions.get(self.boss_type, (64, 64))
    
    def update(self):
        # MOVIMIENTO
        if self.is_moving:
            self.move_timer += 1
            self.rect.x += self.move_speed * self.direction
            
            if abs(self.rect.x - self.spawn_x) >= self.patrol_distance:
                self.direction *= -1
                self.facing_left = not self.facing_left
        
        # PATRÓN DE ATAQUE
        self.attack_timer += 1
        current_pattern = self.attack_pattern[self.current_pattern_index]
        
        if self.attack_timer >= current_pattern['delay'] - 30:
            self.telegraph_timer = 30 - (self.attack_timer - (current_pattern['delay'] - 30))
        else:
            self.telegraph_timer = 0
        
        if self.attack_timer >= current_pattern['delay']:
            self.execute_attack_pattern(current_pattern)
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_pattern)
            self.attack_timer = 0
        
        # ANIMACIÓN
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.animation_counter = 0
        
        # PROYECTILES
        for proj in self.projectiles[:]:
            proj.update()
            if not proj.alive:
                self.projectiles.remove(proj)
    
    def execute_attack_pattern(self, pattern):
        count = pattern['count']
        spread = pattern['spread']
        
        for i in range(count):
            if count == 1:
                angle_offset = 0
            else:
                angle_offset = (i - (count - 1) / 2) * spread
            
            proj_x = self.rect.centerx
            proj_y = self.rect.centery
            
            projectile = BossProjectile(
                proj_x, proj_y,
                direction=-1,
                projectile_type=self.projectile_type,
                angle_offset=angle_offset
            )
            self.projectiles.append(projectile)
    
    def check_collision_with_player(self, player):
        boss_hitbox = self.rect.inflate(-20, -20)
        if player.rect.colliderect(boss_hitbox):
            return True
        return False
    
    def check_hit_player(self, player):
        for proj in self.projectiles:
            if player.rect.colliderect(proj.rect):
                proj.alive = False
                return True
        return False
    
    def get_current_frame(self):
        if not self.sprite_sheet:
            return None
        
        frame_x = self.current_frame * self.frame_width
        frame = self.sprite_sheet.subsurface(
            pygame.Rect(frame_x, 0, self.frame_width, self.frame_height)
        )
        
        scaled_frame = pygame.transform.scale(
            frame,
            (self.display_width, self.display_height)
        )
        
        if self.facing_left:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
        
        return scaled_frame
    
    def draw(self, surface):
        """Dibuja sin cámara"""
        if self.telegraph_timer > 0:
            intensity = int(255 * (self.telegraph_timer / 30))
            flash_surf = pygame.Surface((self.display_width + 20, self.display_height + 20))
            flash_surf.set_alpha(intensity // 2)
            flash_surf.fill((255, 100, 100))
            surface.blit(flash_surf, (self.rect.x - 10, self.rect.y - 10))
        
        frame = self.get_current_frame()
        if frame:
            surface.blit(frame, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, (200, 50, 50), self.rect)
        
        for proj in self.projectiles:
            proj.draw(surface)
        
        safe_zone = pygame.Rect(
            self.rect.x - 250,
            self.rect.y + (self.display_height - self.safe_zone_height),
            250,
            self.safe_zone_height
        )
        pygame.draw.rect(surface, (0, 255, 0), safe_zone, 2)
        
        font = pygame.font.Font(None, 20)
        text = font.render("SAFE ZONE", True, (0, 255, 0))
        surface.blit(text, (safe_zone.x + 70, safe_zone.centery))
    
    def draw_with_camera(self, surface, camera):
        """Dibuja con cámara"""
        boss_screen_rect = camera.apply(self.rect)
        
        if self.telegraph_timer > 0:
            intensity = int(255 * (self.telegraph_timer / 30))
            flash_surf = pygame.Surface((self.display_width + 20, self.display_height + 20))
            flash_surf.set_alpha(intensity // 2)
            flash_surf.fill((255, 100, 100))
            surface.blit(flash_surf, (boss_screen_rect.x - 10, boss_screen_rect.y - 10))
        
        frame = self.get_current_frame()
        if frame:
            surface.blit(frame, (boss_screen_rect.x, boss_screen_rect.y))
        else:
            pygame.draw.rect(surface, (200, 50, 50), boss_screen_rect)
        
        for proj in self.projectiles:
            proj_screen_rect = camera.apply(proj.rect)
            proj_frame = proj.get_current_frame()
            if proj_frame:
                surface.blit(proj_frame, (proj_screen_rect.x, proj_screen_rect.y))
            else:
                pygame.draw.circle(surface, (255, 100, 0), proj_screen_rect.center, 10)
        
        safe_zone = pygame.Rect(
            self.rect.x - 250,
            self.rect.y + (self.display_height - self.safe_zone_height),
            250,
            self.safe_zone_height
        )
        safe_zone_screen = camera.apply(safe_zone)
        pygame.draw.rect(surface, (0, 255, 0), safe_zone_screen, 2)
        
        font = pygame.font.Font(None, 20)
        text = font.render("SAFE ZONE", True, (0, 255, 0))
        surface.blit(text, (safe_zone_screen.x + 70, safe_zone_screen.centery))


class BossProjectile:
    def __init__(self, x, y, direction, projectile_type="flameball", angle_offset=0):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.projectile_type = projectile_type
        
        self.load_sprite()
        
        self.speed = 6
        import math
        angle_rad = math.radians(angle_offset)
        
        self.vel_x = self.speed * direction
        self.vel_y = self.speed * math.sin(angle_rad)
        
        self.rect = pygame.Rect(int(x), int(y), self.display_width, self.display_height)
        
        self.current_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0
        
        self.lifetime = 180
        self.alive = True
    
    def load_sprite(self):
        try:
            sprite_path = f"assets/images/enemies/{self.projectile_type}.png"
            self.sprite_sheet = pygame.image.load(sprite_path)
            
            dimensions = {
                "acid2": (14, 67),
                "flameball": (32, 32),
                "mage-bullet": (13, 13)
            }
            
            self.frame_width, self.frame_height = dimensions.get(
                self.projectile_type, (32, 32)
            )
            
            sheet_width = self.sprite_sheet.get_width()
            self.num_frames = sheet_width // self.frame_width
            
            self.scale_factor = 2.0
            self.display_width = int(self.frame_width * self.scale_factor)
            self.display_height = int(self.frame_height * self.scale_factor)
            
        except:
            self.sprite_sheet = None
            self.display_width = 20
            self.display_height = 20
            self.num_frames = 1
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
        
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.animation_counter = 0
    
    def get_current_frame(self):
        if not self.sprite_sheet:
            return None
        
        frame_x = self.current_frame * self.frame_width
        frame = self.sprite_sheet.subsurface(
            pygame.Rect(frame_x, 0, self.frame_width, self.frame_height)
        )
        
        return pygame.transform.scale(
            frame,
            (self.display_width, self.display_height)
        )
    
    def draw(self, surface):
        frame = self.get_current_frame()
        if frame:
            surface.blit(frame, (self.rect.x, self.rect.y))
        else:
            pygame.draw.circle(surface, (255, 100, 0), self.rect.center, 10)