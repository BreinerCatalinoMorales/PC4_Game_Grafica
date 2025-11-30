import pygame
import json
import os
from config import *
from mage import Mage
from level import Level
from camera import Camera

class Game:
    def __init__(self):
        pygame.init()
        
        if DISPLAY_MODE == "fullscreen":
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        elif DISPLAY_MODE == "borderless":
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        else:
            if ALLOW_RESIZE:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            else:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption("Mi Juego de Puzzle")
        self.clock = pygame.time.Clock()
        
        self.width = WIDTH
        self.height = HEIGHT
        
        self.level_order = []
        self.current_level_index = 0
        self.load_level_order()
        
        self.game_state = "menu"
        
        self.projectiles = []
        self.game_over_timer = 0
        self.death_message = ""
        
        self.camera = None
        
        self.current_color = "normal"
        self.color_buttons = self.create_color_buttons()
        
        self.level_message = ""
        self.level_message_timer = 0
        
        self.lives = 3
        try:
            self.life_icon = pygame.image.load("images/vida.png").convert_alpha()
            self.life_icon = pygame.transform.scale(self.life_icon, (32, 32))
        except:
            self.life_icon = None
            
        self.menu_font_title = pygame.font.Font(None, 120)
        self.menu_font_button = pygame.font.Font(None, 60)
        self.play_button_rect = pygame.Rect(0, 0, 300, 80)
        self.levels_button_rect = pygame.Rect(0, 0, 300, 60)
        self.editor_button_rect = pygame.Rect(0, 0, 300, 60)
        
        self.level_buttons = [] 
        self.back_button_rect = pygame.Rect(20, 20, 100, 40)

        self.player = None
        self.level = None

        self.pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.pause_overlay.fill((0, 0, 0, 150))
        
        self.btn_resume = pygame.Rect(0, 0, 200, 50)
        self.btn_restart = pygame.Rect(0, 0, 200, 50)
        self.btn_menu = pygame.Rect(0, 0, 200, 50)
    
    def load_level_order(self):
        if os.path.exists("level_order.json"):
            try:
                with open("level_order.json", "r") as f:
                    self.level_order = json.load(f)
            except:
                self.level_order = []
        else:
            self.level_order = []
    
    def load_level_by_index(self, index):
        if 0 <= index < len(self.level_order):
            level_file = self.level_order[index]
            self.current_level_index = index
            
            self.level = Level(level_file)
            
            if hasattr(self, 'width') and hasattr(self, 'height'):
                self.level.handle_resize(self.width, self.height)
            
            spawn_x, spawn_y = self.level.player_spawn
            self.player = Mage(spawn_x, spawn_y)
            self.change_player_color(self.current_color)
            
            self.projectiles = []
            self.game_state = "playing"
            
            level_width, level_height = self.level.get_dimensions()
            self.camera = Camera(level_width, level_height)
            
            if "level3" in level_file and self.level.monster_spawns:
                self.level.spawn_monsters()
                self.level_message = "Busca la salida como un camaleon"
                self.level_message_timer = 360
        else:
            self.game_state = "game_complete"
    
    def create_color_buttons(self):
        button_width = 90
        button_height = 35
        spacing = 10
        start_x = 10
        start_y = 10
        
        return [
            {"rect": pygame.Rect(start_x, start_y, button_width, button_height), 
             "color": "normal", "text": "Normal", "bg": (100, 100, 100)},
            {"rect": pygame.Rect(start_x + (button_width + spacing), start_y, button_width, button_height),
             "color": "black", "text": "Negro", "bg": (50, 50, 50)},
            {"rect": pygame.Rect(start_x + 2*(button_width + spacing), start_y, button_width, button_height),
             "color": "blue", "text": "Azul", "bg": (0, 50, 150)},
            {"rect": pygame.Rect(start_x + 3*(button_width + spacing), start_y, button_width, button_height),
             "color": "red", "text": "Rojo", "bg": (150, 30, 0)},
            {"rect": pygame.Rect(start_x + 4*(button_width + spacing), start_y, button_width, button_height),
             "color": "background", "text": "Otro", "bg": (80, 60, 100)}
        ]
    
    def create_level_buttons(self):
        self.load_level_order() 
        
        self.level_buttons = []
        
        if not self.level_order:
            return

        cols = 4
        button_size = 80
        spacing = 20
        
        total_grid_width = (cols * button_size) + ((cols - 1) * spacing)
        start_x = (self.width - total_grid_width) // 2
        start_y = 150
        
        for i, level_path in enumerate(self.level_order):
            row = i // cols
            col = i % cols
            
            x = start_x + (col * (button_size + spacing))
            y = start_y + (row * (button_size + spacing))
            
            rect = pygame.Rect(x, y, button_size, button_size)
            name = str(i + 1)
            
            self.level_buttons.append({
                "rect": rect,
                "index": i,
                "text": name,
                "file": level_path
            })

    def change_player_color(self, color):
        if not self.player: return
        try:
            color_paths = {
                "normal": "assets/images/player/Mage",
                "black": "assets/images/player/Mage_Black",
                "blue": "assets/images/player/Mage_Blue",
                "red": "assets/images/player/Mage_Red",
                "background": "assets/images/player/Mage_Background"
            }
            
            if color not in color_paths: return
             
            old_x = self.player.x
            old_y = self.player.y
            old_vel_x = self.player.vel_x
            old_vel_y = self.player.vel_y
            old_animation = self.player.current_animation
            old_frame = self.player.current_frame
            old_direction = self.player.direction
            
            self.player.base_path = color_paths[color]
            self.player.load_sprites()
            
            self.player.x = old_x
            self.player.y = old_y
            self.player.rect.x = int(old_x)
            self.player.rect.y = int(old_y)
            self.player.vel_x = old_vel_x
            self.player.vel_y = old_vel_y
            self.player.current_animation = old_animation
            self.player.current_frame = old_frame  
            self.player.direction = old_direction
            
            self.current_color = color
            
        except Exception:
            pass

    def reset_current_level(self):
        self.lives -= 1
        
        if self.lives < 0:
            self.game_state = "menu"
            self.lives = 3 
            return 

        self.load_level_by_index(self.current_level_index)
        if hasattr(self, 'width'):
            self.level.handle_resize(self.width, self.height)
    
    def draw_menu(self):
        for y in range(0, self.height, 4):
            color_val = int(20 + (y / self.height) * 40)
            pygame.draw.rect(self.screen, (color_val // 3, color_val // 3, color_val), 
                           (0, y, self.width, 4))
        
        time = pygame.time.get_ticks()
        pulse = abs((time % 1000) - 500) / 500.0
        
        center_x = self.width // 2
        center_y = self.height // 3
        
        title_text = "Run to the goal"
        for offset in range(5, 0, -1):
            shadow_color = (offset * 10, offset * 10, offset * 15)
            shadow_surf = self.menu_font_title.render(title_text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect(center=(center_x + offset, center_y + offset))
            self.screen.blit(shadow_surf, shadow_rect)
        
        title_color = (int(200 + pulse * 55), int(200 + pulse * 55), int(50 + pulse * 50))
        title_surf = self.menu_font_title.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(center_x, center_y))
        self.screen.blit(title_surf, title_rect)
        
        button_y = center_y + 150  
        button_width = 400
        button_height = 100
        self.play_button_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_button_rect.center = (center_x, button_y)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.play_button_rect.collidepoint(mouse_pos)
        button_pulse = 1.0 + (pulse * 0.1 if is_hover else pulse * 0.05)
        
        pulsed_width = int(button_width * button_pulse)
        pulsed_height = int(button_height * button_pulse)
        pulsed_rect = pygame.Rect(0, 0, pulsed_width, pulsed_height)
        pulsed_rect.center = (center_x, button_y)
        
        if is_hover:
            glow_rect = pulsed_rect.inflate(20, 20)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surf.set_alpha(80)
            glow_surf.fill((100, 255, 100))
            self.screen.blit(glow_surf, glow_rect.topleft)
        
        button_color = (50, 220, 50) if is_hover else (40, 180, 40)
        pygame.draw.rect(self.screen, button_color, pulsed_rect, border_radius=20)
        pygame.draw.rect(self.screen, (200, 255, 200), pulsed_rect, 5, border_radius=20)
        
        button_font = pygame.font.Font(None, 80)
        text_surf = button_font.render("JUGAR", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(center_x, button_y))
        self.screen.blit(text_surf, text_rect)
        
        levels_y = button_y + 110
        self.levels_button_rect.center = (center_x, levels_y)
        is_hover_levels = self.levels_button_rect.collidepoint(mouse_pos)
        color_levels = (50, 100, 200) if is_hover_levels else (40, 80, 150)
        pygame.draw.rect(self.screen, color_levels, self.levels_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (150, 200, 255), self.levels_button_rect, 3, border_radius=20)
        lvl_text = self.menu_font_button.render("NIVELES", True, (255, 255, 255))
        lvl_rect = lvl_text.get_rect(center=self.levels_button_rect.center)
        self.screen.blit(lvl_text, lvl_rect)

        editor_y = levels_y + 80
        self.editor_button_rect.center = (center_x, editor_y)
        is_hover_editor = self.editor_button_rect.collidepoint(mouse_pos)
        color_editor = (150, 50, 150) if is_hover_editor else (100, 30, 100)
        pygame.draw.rect(self.screen, color_editor, self.editor_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (200, 100, 255), self.editor_button_rect, 3, border_radius=20)
        ed_text = self.menu_font_button.render("EDITOR", True, (255, 255, 255))
        ed_rect = ed_text.get_rect(center=self.editor_button_rect.center)
        self.screen.blit(ed_text, ed_rect)
        
        subtitle_font = pygame.font.Font(None, 30)
        subtitle_text = "Click para comenzar la aventura"
        subtitle_alpha = int(150 + pulse * 105)
        subtitle_surf = subtitle_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_surf.set_alpha(subtitle_alpha)
        subtitle_rect = subtitle_surf.get_rect(center=(center_x, self.height - 50))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        for i in range(20):
            star_x = (i * 100 + time // 10) % self.width
            star_y = (i * 50 + time // 15) % self.height
            star_alpha = int((i % 3) * 85 + pulse * 85)
            if star_alpha > 30:
                pygame.draw.circle(self.screen, (255, 255, 150), (star_x, star_y), 2)
        
        pygame.display.flip()

    def draw_level_selection(self):
        self.screen.fill((30, 30, 40))
        
        title = self.menu_font_button.render("SELECCIONA NIVEL", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title, title_rect)
        
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_button_rect, border_radius=10)
        back_text = pygame.font.Font(None, 30).render("Volver", True, (255, 255, 255))
        text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.Font(None, 40)
        
        for btn in self.level_buttons:
            rect = btn["rect"]
            is_hover = rect.collidepoint(mouse_pos)
            color = (50, 200, 100) if is_hover else (70, 80, 100)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=15)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=15)
            
            text = font.render(btn["text"], True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_pause_menu(self):
        self.draw() 
        
        if self.pause_overlay.get_size() != (self.width, self.height):
            self.pause_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.pause_overlay.fill((0, 0, 0, 150))
        self.screen.blit(self.pause_overlay, (0, 0))
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        font_title = pygame.font.Font(None, 80)
        text = font_title.render("PAUSA", True, (255, 255, 255))
        text_rect = text.get_rect(center=(center_x, center_y - 100))
        self.screen.blit(text, text_rect)
        
        self.btn_resume.center = (center_x, center_y)
        self.btn_restart.center = (center_x, center_y + 70)
        self.btn_menu.center = (center_x, center_y + 140)
        
        mouse_pos = pygame.mouse.get_pos()
        font_btn = pygame.font.Font(None, 40)
        
        buttons = [
            (self.btn_resume, "Continuar", (50, 200, 50)),
            (self.btn_restart, "Reiniciar Nivel", (200, 200, 50)),
            (self.btn_menu, "Ir al Menú", (200, 50, 50))
        ]
        
        for rect, text, color in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            draw_color = color if is_hover else (color[0]//2, color[1]//2, color[2]//2)
            
            pygame.draw.rect(self.screen, draw_color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            txt_surf = font_btn.render(text, True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(center=rect.center)
            self.screen.blit(txt_surf, txt_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    if self.level:
                        self.level.handle_resize(self.width, self.height)
                
                if self.game_state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.play_button_rect.collidepoint(event.pos):
                            self.game_state = "playing"
                            if not hasattr(self, 'level') or not self.level:
                                if self.level_order:
                                    self.load_level_by_index(0)
                                    if hasattr(self, 'width'):
                                        self.level.handle_resize(self.width, self.height)
                                else:
                                    self.load_level(4, 1)
                        
                        elif self.levels_button_rect.collidepoint(event.pos):
                            self.create_level_buttons()
                            self.game_state = "level_selection"

                        elif self.editor_button_rect.collidepoint(event.pos):
                            import level_editor
                            editor = level_editor.LevelEditor()
                            editor.run()
                            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                            pygame.display.set_caption("Mi Juego de Puzzle")

                elif self.game_state == "level_selection":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.back_button_rect.collidepoint(event.pos):
                            self.game_state = "menu"
                        
                        for btn in self.level_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                self.load_level_by_index(btn['index'])
                                self.level.handle_resize(self.width, self.height)
                                self.game_state = "playing"

                elif self.game_state == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "paused"
                        else:
                            self.handle_keypress(event.key)
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if 0 <= self.current_level_index < len(self.level_order):
                            for button in self.color_buttons:
                                if button["rect"].collidepoint(event.pos):
                                    self.change_player_color(button["color"])
                                    break

                elif self.game_state == "paused":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "playing"
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_resume.collidepoint(event.pos):
                            self.game_state = "playing"
                        elif self.btn_restart.collidepoint(event.pos):
                            self.load_level_by_index(self.current_level_index)
                            if hasattr(self, 'width'):
                                self.level.handle_resize(self.width, self.height)
                            self.game_state = "playing"
                        elif self.btn_menu.collidepoint(event.pos):
                            self.game_state = "menu"
                            self.lives = 3
            
            if self.game_state == "menu":
                self.draw_menu()
                self.clock.tick(FPS)
                continue
            
            elif self.game_state == "level_selection":
                self.draw_level_selection()

            elif self.game_state == "paused":
                self.draw_pause_menu()

            elif self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.update_game_over()
                self.draw_game_over()
            elif self.game_state == "game_complete":
                self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def handle_keypress(self, key):
        if self.game_state == "playing":
            if key == pygame.K_f:
                self.player.use_ability()
            elif key == pygame.K_F11:
                self.toggle_fullscreen()
        
        elif self.game_state == "game_over":
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.reset_current_level()
    
    def toggle_fullscreen(self):
        global DISPLAY_MODE
        if DISPLAY_MODE == "windowed":
            DISPLAY_MODE = "fullscreen"
            self.screen = pygame.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.FULLSCREEN)
            self.width = NATIVE_WIDTH
            self.height = NATIVE_HEIGHT
        else:
            DISPLAY_MODE = "windowed"
            windowed_width = int(NATIVE_WIDTH * 0.8)
            windowed_height = int(NATIVE_HEIGHT * 0.8)
            self.screen = pygame.display.set_mode((windowed_width, windowed_height), pygame.RESIZABLE)
            self.width = windowed_width
            self.height = windowed_height
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        projectile = self.player.update(keys, self.level.platforms)
        if projectile:
            self.projectiles.append(projectile)
        
        self.camera.update(self.player.rect)
        level_state = self.level.update(self.player, self)
        
        if level_state == "game_over":
            self.game_state = "game_over"
            self.game_over_timer = 180
            self.death_message = "¡EL JEFE TE ATRAPÓ!" if self.level.boss else "¡UN MONSTRUO TE ATRAPÓ!"
            return
        
        for proj in self.projectiles[:]:
            proj.update(self.level.platforms)
            if not proj.alive:
                self.projectiles.remove(proj)
            else:
                for monster in self.level.monsters[:]:
                    if proj.rect.colliderect(monster.rect) and not monster.is_dying:
                        monster.take_damage()
                        proj.alive = False
                        break
        
        if self.level.check_section_complete(self.player):
            next_index = self.current_level_index + 1
            if next_index < len(self.level_order):
                self.load_level_by_index(next_index)
            else:
                self.level_message = "Felicidades, terminaste el juego"
                self.level_message_timer = 600
                self.game_state = "game_complete"
        
        if self.level_message_timer > 0:
            self.level_message_timer -= 1
            if self.level_message_timer <= 0:
                self.level_message = ""
    
    def update_game_over(self):
        self.game_over_timer -= 1
        if self.game_over_timer <= 0:
            self.reset_current_level()
    
    def draw(self):
        self.level.draw_background(self.screen)
        self.level.draw_with_camera(self.screen, self.camera)
        
        for proj in self.projectiles:
            proj_rect = self.camera.apply(proj.rect)
            proj.draw_at(self.screen, proj_rect.topleft)
        
        player_rect = self.camera.apply(self.player.rect)
        self.player.draw_at(self.screen, player_rect.topleft)
        
        self.draw_ui()
    
    def draw_ui(self):
        font = pygame.font.Font(None, 30)
        message_font = pygame.font.Font(None, 36)
        
        text = font.render(f"Saltos: {self.player.jumps_left}/{self.player.max_jumps}", True, (0, 0, 0))
        self.screen.blit(text, (12, 12))
        text = font.render(f"Saltos: {self.player.jumps_left}/{self.player.max_jumps}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        
        if self.player.cast_cooldown > 0:
            text = font.render(f"Cooldown: {self.player.cast_cooldown}", True, (0, 0, 0))
            self.screen.blit(text, (12, 42))
            text = font.render(f"Cooldown: {self.player.cast_cooldown}", True, (255, 100, 100))
            self.screen.blit(text, (10, 40))
        
        small_font = pygame.font.Font(None, 20)
        level_name = "N/A"
        if 0 <= self.current_level_index < len(self.level_order):
            level_name = self.level_order[self.current_level_index].split("/")[-1].replace(".txt", "")
        mode_text = small_font.render(
            f"Nivel: {level_name} ({self.current_level_index + 1}/{len(self.level_order)}) | F11=Fullscreen | F=Disparar", 
            True, (200, 200, 200)
        )
        self.screen.blit(mode_text, (self.width - 550, 10))
        
        if 0 <= self.current_level_index < len(self.level_order):
            if "level3" in self.level_order[self.current_level_index]:
                if self.life_icon:
                    self.screen.blit(self.life_icon, (20, 50))
                else:
                    pygame.draw.circle(self.screen, (255, 50, 50), (36, 66), 16)
                
                lives_color = (255, 255, 255)
                if self.lives < 0:
                    lives_color = (255, 50, 50)
                lives_surf = message_font.render(f"x {self.lives}", True, lives_color)
                self.screen.blit(lives_surf, (60, 55))
        
        if 0 <= self.current_level_index < len(self.level_order):
            button_font = pygame.font.Font(None, 24)
            for button in self.color_buttons:
                if button["color"] == self.current_color:
                    border_color = (255, 255, 0)
                    border_width = 3
                else:
                    border_color = (200, 200, 200)
                    border_width = 2
                
                pygame.draw.rect(self.screen, button["bg"], button["rect"])
                pygame.draw.rect(self.screen, border_color, button["rect"], border_width)
                text = button_font.render(button["text"], True, (255, 255, 255))
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)
        
        if self.level_message:
            message_surf = message_font.render(self.level_message, True, (255, 255, 100))
            message_rect = message_surf.get_rect(center=(self.width // 2, 50))
            shadow = message_font.render(self.level_message, True, (0, 0, 0))
            self.screen.blit(shadow, (message_rect.x + 2, message_rect.y + 2))
            self.screen.blit(message_surf, message_rect)
    
    def draw_game_over(self):
        self.level.draw_background(self.screen)
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((20, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        big_font = pygame.font.Font(None, 100)
        text = big_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 60))
        self.screen.blit(text, text_rect)
        
        med_font = pygame.font.Font(None, 40)
        msg = med_font.render(self.death_message, True, (255, 200, 200))
        msg_rect = msg.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(msg, msg_rect)
        
        small_font = pygame.font.Font(None, 30)
        if self.game_over_timer > 60:
            timer_text = f"Reiniciando en {self.game_over_timer // 60}..."
            text = small_font.render(timer_text, True, (255, 255, 255))
        else:
            text = small_font.render("Presiona ESPACIO para reiniciar", True, (255, 255, 100))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(text, text_rect)

if __name__ == "__main__":
    game = Game()
    game.run()