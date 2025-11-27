# main.py - COMPLETO CON CÁMARA Y SISTEMA DE GAME OVER
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
        
        # Configurar pantalla según modo
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
        
        # Load level order
        self.level_order = []
        self.current_level_index = 0
        self.load_level_order()
        
        self.game_state = "playing"
        
        self.projectiles = []
        self.game_over_timer = 0
        self.death_message = ""
        
        self.camera = None
        
        # Color switcher system
        self.current_color = "normal"
        self.color_buttons = self.create_color_buttons()
        
        # Sistema de mensajes de nivel
        self.level_message = ""
        self.level_message_timer = 0
        
        # Load first level from list
        if self.level_order:
            self.load_level_by_index(0)
        else:
            print("No levels found in level_order.json!")
    
    def load_level_order(self):
        """Load level order from JSON file"""
        if os.path.exists("level_order.json"):
            try:
                with open("level_order.json", "r") as f:
                    self.level_order = json.load(f)
                print(f"Loaded {len(self.level_order)} levels from level_order.json")
            except Exception as e:
                print(f"Error loading level_order.json: {e}")
                self.level_order = []
        else:
            print("level_order.json not found!")
            self.level_order = []
    
    def load_level_by_index(self, index):
        """Load level by index from level_order list"""
        if 0 <= index < len(self.level_order):
            level_file = self.level_order[index]
            self.current_level_index = index
            
            self.level = Level(level_file)
            spawn_x, spawn_y = self.level.player_spawn
            self.player = Mage(spawn_x, spawn_y)
            
            self.projectiles = []
            self.game_state = "playing"
            
            # Create camera
            level_width, level_height = self.level.get_dimensions()
            self.camera = Camera(level_width, level_height)
            print(f"📷 Cámara creada para nivel {level_width}x{level_height}")
            print(f"Nivel cargado: {level_file} ({index + 1}/{len(self.level_order)})")
            
            # Spawnear monstruos si es nivel 3+ (detectar por nombre de archivo)
            if "level3" in level_file and self.level.monster_spawns:
                self.level.spawn_monsters()
                # Mostrar mensaje de nivel 3
                self.level_message = "Busca la salida como un camaleon"
                self.level_message_timer = 360  # 6 segundos a 60 FPS
        else:
            print("Game Complete!")
            self.game_state = "game_complete"
    
    def create_color_buttons(self):
        """Crea los botones de cambio de color"""
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
    
    def change_player_color(self, color):
        """Cambia el color del jugador en tiempo real"""
        try:
            color_paths = {
                "normal": "assets/images/player/Mage",
                "black": "assets/images/player/Mage_Black",
                "blue": "assets/images/player/Mage_Blue",
                "red": "assets/images/player/Mage_Red",
                "background": "assets/images/player/Mage_Background"
            }
            
            if color not in color_paths:
                print(f"⚠️ Color inválido: {color}")
                return
            
            print(f"🎨 Cambiando color a: {color}")
            
            # Guardar estado actual del jugador  
            old_x = self.player.x
            old_y = self.player.y
            old_vel_x = self.player.vel_x
            old_vel_y = self.player.vel_y
            old_animation = self.player.current_animation
            old_frame = self.player.current_frame
            old_direction = self.player.direction
            
            # Cambiar ruta base y recargar sprites
            self.player.base_path = color_paths[color]
            self.player.load_sprites()
            
            # Restaurar estado
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
            print(f"✓ Color cambiado exitosamente a: {color}")
            
        except Exception as e:
            print(f"❌ Error al cambiar color: {e}")
            import traceback
            traceback.print_exc()
    
    def reset_current_level(self):
        """Reinicia el nivel actual"""
        print("GAME OVER - Reiniciando nivel...")
        self.load_level_by_index(self.current_level_index)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), 
                        pygame.RESIZABLE
                    )
                
                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event.key)
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Detectar clics en botones de color (solo en nivel 3)
                    if "level3" in self.level_order[self.current_level_index]:
                        mouse_pos = event.pos
                        for button in self.color_buttons:
                            if button["rect"].collidepoint(mouse_pos):
                                self.change_player_color(button["color"])
                                break
            
            if self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.update_game_over()
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def handle_keypress(self, key):
        """Maneja teclas especiales"""
        if self.game_state == "playing":
            if key == pygame.K_f:
                self.player.use_ability()
            elif key == pygame.K_F11:
                self.toggle_fullscreen()
        
        elif self.game_state == "game_over":
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.reset_current_level()
    
    def toggle_fullscreen(self):
        """Alterna entre ventana y pantalla completa"""
        global DISPLAY_MODE
        
        if DISPLAY_MODE == "windowed":
            DISPLAY_MODE = "fullscreen"
            self.screen = pygame.display.set_mode(
                (NATIVE_WIDTH, NATIVE_HEIGHT), 
                pygame.FULLSCREEN
            )
            self.width = NATIVE_WIDTH
            self.height = NATIVE_HEIGHT
        else:
            DISPLAY_MODE = "windowed"
            windowed_width = int(NATIVE_WIDTH * 0.8)
            windowed_height = int(NATIVE_HEIGHT * 0.8)
            self.screen = pygame.display.set_mode(
                (windowed_width, windowed_height),
                pygame.RESIZABLE
            )
            self.width = windowed_width
            self.height = windowed_height
    
    def update(self):
        """Update con cámara"""
        keys = pygame.key.get_pressed()
        
        # Actualizar jugador
        projectile = self.player.update(keys, self.level.platforms)
        if projectile:
            self.projectiles.append(projectile)
        
        # Actualizar cámara
        self.camera.update(self.player.rect)
        
        # Actualizar nivel (pasar referencia del juego para camuflaje)
        level_state = self.level.update(self.player, self)
        
        # Verificar game over
        if level_state == "game_over":
            self.game_state = "game_over"
            self.game_over_timer = 180
            self.death_message = "¡EL JEFE TE ATRAPÓ!" if self.level.boss else "¡UN MONSTRUO TE ATRAPÓ!"
            return
        
        # Actualizar proyectiles del jugador
        for proj in self.projectiles[:]:
            proj.update(self.level.platforms)
            if not proj.alive:
                self.projectiles.remove(proj)
            else:
                # Verificar colisión con monstruos
                for monster in self.level.monsters[:]:
                    if proj.rect.colliderect(monster.rect) and not monster.is_dying:
                        monster.take_damage()
                        proj.alive = False
                        break
        
        # Verificar victoria
        if self.level.check_section_complete(self.player):
            next_index = self.current_level_index + 1
            if next_index < len(self.level_order):
                print(f"✓ Nivel completado! Cargando siguiente...")
                self.load_level_by_index(next_index)
            else:
                print("🎉 ¡JUEGO COMPLETADO!")
                self.level_message = "Felicidades, terminaste el juego"
                self.level_message_timer = 600  # 10 segundos
                self.game_state = "game_complete"
        
        # Actualizar timer de mensaje de nivel
        if self.level_message_timer > 0:
            self.level_message_timer -= 1
            if self.level_message_timer <= 0:
                self.level_message = ""
    
    def update_game_over(self):
        """Update durante game over"""
        self.game_over_timer -= 1
        if self.game_over_timer <= 0:
            self.reset_current_level()
    
    def draw(self):
        """Dibuja el juego con cámara"""
        # 1. Fondo fijo (sin cámara)
        self.level.draw_background(self.screen)
        
        # 2. Nivel con cámara
        self.level.draw_with_camera(self.screen, self.camera)
        
        # 3. Proyectiles del jugador con cámara
        for proj in self.projectiles:
            proj_rect = self.camera.apply(proj.rect)
            proj.draw_at(self.screen, proj_rect.topleft)
        
        # 4. Jugador con cámara
        player_rect = self.camera.apply(self.player.rect)
        self.player.draw_at(self.screen, player_rect.topleft)
        
        # 5. UI fija (sin cámara)
        self.draw_ui()
    
    def draw_ui(self):
        """Dibuja UI fija en pantalla"""
        font = pygame.font.Font(None, 30)
        
        # Saltos con sombra
        text = font.render(f"Saltos: {self.player.jumps_left}/{self.player.max_jumps}", True, (0, 0, 0))
        self.screen.blit(text, (12, 12))
        text = font.render(f"Saltos: {self.player.jumps_left}/{self.player.max_jumps}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        
        # Cooldown
        if self.player.cast_cooldown > 0:
            text = font.render(f"Cooldown: {self.player.cast_cooldown}", True, (0, 0, 0))
            self.screen.blit(text, (12, 42))
            text = font.render(f"Cooldown: {self.player.cast_cooldown}", True, (255, 100, 100))
            self.screen.blit(text, (10, 40))
        
        # Info nivel
        small_font = pygame.font.Font(None, 20)
        level_name = "N/A"
        if 0 <= self.current_level_index < len(self.level_order):
            level_name = self.level_order[self.current_level_index].split("/")[-1].replace(".txt", "")
        mode_text = small_font.render(
            f"Nivel: {level_name} ({self.current_level_index + 1}/{len(self.level_order)}) | F11=Fullscreen | F=Disparar", 
            True, (200, 200, 200)
        )
        self.screen.blit(mode_text, (self.width - 550, 10))
        
        # Dibujar botones de color (solo en nivel 3)
        if 0 <= self.current_level_index < len(self.level_order) and "level3" in self.level_order[self.current_level_index]:
            button_font = pygame.font.Font(None, 24)
            for button in self.color_buttons:
                # Destacar botón activo
                if button["color"] == self.current_color:
                    border_color = (255, 255, 0)
                    border_width = 3
                else:
                    border_color = (200, 200, 200)
                    border_width = 2
                
                # Fondo del botón
                pygame.draw.rect(self.screen, button["bg"], button["rect"])
                # Borde
                pygame.draw.rect(self.screen, border_color, button["rect"], border_width)
                # Texto
                text = button_font.render(button["text"], True, (255, 255, 255))
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)
        
        # Mensaje de nivel (si existe)
        if self.level_message:
            message_font = pygame.font.Font(None, 36)
            
            # Mensaje en la parte superior
            message_surf = message_font.render(self.level_message, True, (255, 255, 100))
            message_rect = message_surf.get_rect(center=(self.width // 2, 50))
            
            # Sombra
            shadow = message_font.render(self.level_message, True, (0, 0, 0))
            self.screen.blit(shadow, (message_rect.x + 2, message_rect.y + 2))
            
            # Texto principal
            self.screen.blit(message_surf, message_rect)
    
    def draw_game_over(self):
        """Dibuja pantalla de game over"""
        # Fondo
        self.level.draw_background(self.screen)
        
        # Overlay oscuro
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((20, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto GAME OVER
        big_font = pygame.font.Font(None, 100)
        text = big_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 60))
        self.screen.blit(text, text_rect)
        
        # Mensaje de muerte
        med_font = pygame.font.Font(None, 40)
        msg = med_font.render(self.death_message, True, (255, 200, 200))
        msg_rect = msg.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(msg, msg_rect)
        
        # Instrucciones
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
