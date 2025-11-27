import pygame
from boss import Boss

class UndeadExecutioner(Boss):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.boss_type = "undead_executioner"
        self.spawn_x = x
        self.spawn_y = y
        
        # 1. HACERLO ENORME
        self.scale_factor = 5.0
        self.display_width = int(100 * self.scale_factor)   # 500px
        self.display_height = int(100 * self.scale_factor)  # 500px
        
        # Configuración de assets
        self.base_path = "Undead executioner/Undead executioner puppet/png"
        self.load_sprites()
        
        # 2. FIX COLISIÓN CUERPO
        # La hitbox física (body) la movemos MUY ARRIBA para que el jugador pase por debajo
        # Solo bloquea si saltas muy alto (o ni eso)
        # AJUSTE: Bajamos el boss 100px visualmente (y su hitbox)
        y_offset = 100
        self.rect = pygame.Rect(x, y - self.display_height + y_offset, self.display_width // 3, 100)
        self.rect.centerx = x
        
        # Guardamos la posición del suelo para dibujar
        self.ground_y = y + y_offset
        
        # Estado
        self.state = "idle"
        self.current_frame = 0
        self.animation_speed = 10
        self.animation_counter = 0
        self.facing_left = True
        
        # Ataque CONSTANTE
        self.attack_timer = 0
        self.attack_interval = 60
        self.is_attacking = False
        self.damage_rect = None
        
        # Hitbox segura (el truco)
        # Player mide 60px de altura. Necesitamos al menos 100px de zona segura
        # para que pueda caminar sin problema pero saltar cause colisión.
        self.safe_height = 100
        
        # 3. VIDA Y DAÑO
        self.max_health = 10000
        self.health = self.max_health
        
        self.projectiles = [] 
        self.telegraph_timer = 0

    def load_sprites(self):
        try:
            idle_sheet = pygame.image.load(f"{self.base_path}/idle.png")
            self.idle_frames = []
            for i in range(5):
                frame = idle_sheet.subsurface(pygame.Rect(i*100, 0, 100, 100))
                scaled = pygame.transform.scale(frame, (int(100*self.scale_factor), int(100*self.scale_factor)))
                self.idle_frames.append(scaled)
                
            attack_sheet = pygame.image.load(f"{self.base_path}/attacking.png")
            self.attack_frames = []
            for i in range(6):
                frame = attack_sheet.subsurface(pygame.Rect(i*100, 0, 100, 300))
                scaled_w = int(100 * self.scale_factor)
                scaled_h = int(300 * self.scale_factor)
                scaled = pygame.transform.scale(frame, (scaled_w, scaled_h))
                self.attack_frames.append(scaled)
                
            print(f"✓ Undead Executioner assets loaded. Scale: {self.scale_factor}")
            
        except Exception as e:
            print(f"Error loading Undead Executioner assets: {e}")
            self.idle_frames = []
            self.attack_frames = []

    def update(self):
        self.animation_counter += 1
        
        if self.state == "idle":
            if self.animation_counter >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                self.animation_counter = 0
            
            self.attack_timer += 1
            if self.attack_timer >= self.attack_interval:
                self.start_attack()
                
        elif self.state == "attack":
            if self.animation_counter >= self.animation_speed:
                self.current_frame += 1
                self.animation_counter = 0
                
                if 2 <= self.current_frame <= 4:
                    self.create_damage_hitbox()
                else:
                    self.damage_rect = None
                
                if self.current_frame >= len(self.attack_frames):
                    self.state = "idle"
                    self.current_frame = 0
                    self.attack_timer = 0
                    self.damage_rect = None

    def start_attack(self):
        self.state = "attack"
        self.current_frame = 0
        self.animation_counter = 0

    def create_damage_hitbox(self):
        # Hitbox mortal que cubre todo MENOS la zona segura abajo
        kill_zone_bottom = self.ground_y - self.safe_height
        
        self.damage_rect = pygame.Rect(
            self.rect.centerx - 200,
            -1000,
            400,
            kill_zone_bottom + 1000
        )

    def check_collision_with_player(self, player):
        # Solo colisión con ataque mata
        if self.damage_rect:
            if self.damage_rect.colliderect(player.rect):
                print("💀 Jugador golpeado por la guadaña (saltó o muy alto)")
                return True
        return False

    def check_hit_player(self, player):
        return self.check_collision_with_player(player)
        
    def take_damage(self):
        # Daño minúsculo
        self.health -= 10  # 10 de 10000 = 0.1%
        if self.health < 0: self.health = 0
        print(f"🛡️ Boss recibe daño mínimo. Vida: {self.health}/{self.max_health}")

    def draw(self, surface):
        self.draw_with_camera(surface, None)

    def draw_with_camera(self, surface, camera):
        # Dibujar sprite
        if self.state == "idle":
            if not self.idle_frames: return
            frame = self.idle_frames[self.current_frame]
        else:
            if not self.attack_frames: return
            frame = self.attack_frames[self.current_frame]

        # Posición de dibujo basada en el suelo (ground_y), no en el rect físico
        draw_rect = frame.get_rect()
        draw_rect.midbottom = (self.rect.centerx, self.ground_y)

        if camera:
            screen_rect = camera.apply(draw_rect)
            surface.blit(frame, screen_rect)
            
            # Dibujar barra de vida
            self.draw_health_bar(surface, camera)
        else:
            surface.blit(frame, draw_rect)

    def draw_health_bar(self, surface, camera):
        # Barra de vida flotante sobre el boss
        bar_w = 400
        bar_h = 20
        
        # Posición en el mundo
        # Ajustamos Y para que se vea (el boss es muy alto, 500px)
        # Lo ponemos a una altura fija relativa al suelo o más abajo del top
        world_x = self.rect.centerx - bar_w // 2
        world_y = self.ground_y - 400  # 400px arriba del suelo (el boss mide 500px)
        
        # Convertir a pantalla
        if camera:
            pos = camera.apply_pos(world_x, world_y)
            screen_x, screen_y = pos
        else:
            screen_x, screen_y = world_x, world_y
            
        # Fondo rojo
        pygame.draw.rect(surface, (100, 0, 0), (screen_x, screen_y, bar_w, bar_h))
        
        # Vida actual verde
        health_pct = self.health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y, int(bar_w * health_pct), bar_h))
        
        # Borde blanco
        pygame.draw.rect(surface, (255, 255, 255), (screen_x, screen_y, bar_w, bar_h), 2)
        
        # Texto nombre
        font = pygame.font.Font(None, 30)
        text = font.render("UNDEAD EXECUTIONER", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_x + bar_w//2, screen_y - 15))
        surface.blit(text, text_rect)
