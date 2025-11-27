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
        # Sistema de mensajes de nivel
        self.level_message = ""
        self.level_message_timer = 0
        
        # Sistema de vidas (Nivel 3)
        self.lives = 3
        try:
            self.life_icon = pygame.image.load("images/vida.png").convert_alpha()
            self.life_icon = pygame.transform.scale(self.life_icon, (32, 32))
        except:
            print("⚠ No se encontró images/vida.png, usando placeholder")
            self.life_icon = None
            
        # Estado inicial: Menú
        self.game_state = "menu"
        self.menu_font_title = pygame.font.Font(None, 120)
        self.menu_font_button = pygame.font.Font(None, 60)
        self.play_button_rect = pygame.Rect(0, 0, 300, 80)
        
        # Inicializar player y level como None (se cargarán al hacer click en JUGAR)
        self.player = None
        self.level = None
        
        # NO cargar nivel automáticamente - esperar a que usuario haga click en menú
        # if self.level_order:
        #     self.load_level_by_index(0)
        # else:
        #     print("No levels found in level_order.json!")
    
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
        
        # Decrementar vidas si estamos en nivel 3
        if 0 <= self.current_level_index < len(self.level_order):
            if "level3" in self.level_order[self.current_level_index]:
                self.lives -= 1
                print(f"💔 Vidas restantes: {self.lives}")
                
        self.load_level_by_index(self.current_level_index)
    
    def draw_menu(self):
        """Dibuja la pantalla de inicio estilo retro"""
        # Fondo con gradiente retro
        for y in range(0, self.height, 4):
            color_val = int(20 + (y / self.height) * 40)
            pygame.draw.rect(self.screen, (color_val // 3, color_val // 3, color_val), 
                           (0, y, self.width, 4))
        
        # Variables para animaciones
        time = pygame.time.get_ticks()
        pulse = abs((time % 1000) - 500) / 500.0  # 0 a 1 y vuelta
        
        center_x = self.width // 2
        center_y = self.height // 3
        
        # ============ TÍTULO CON EFECTO PIXELADO ============
        title_text = "Run to the goal"
        
        # Sombra con desplazamiento retro
        for offset in range(5, 0, -1):
            shadow_color = (offset * 10, offset * 10, offset * 15)
            shadow_surf = self.menu_font_title.render(title_text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect(center=(center_x + offset, center_y + offset))
            self.screen.blit(shadow_surf, shadow_rect)
        
        # Texto principal con efecto de brillo
        title_color = (
            int(200 + pulse * 55),
            int(200 + pulse * 55),
            int(50 + pulse * 50)
        )
        title_surf = self.menu_font_title.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(center_x, center_y))
        self.screen.blit(title_surf, title_rect)
        
        # Líneas decorativas retro
        line_y = center_y + 70
        for i in range(10):
            x_offset = int(pulse * 20) if i % 2 == 0 else int(-pulse * 20)
            start_x = center_x - 200 + x_offset
            end_x = center_x + 200 + x_offset
            color = (100 + i * 10, 100 + i * 10, 150 + i * 5)
            pygame.draw.line(self.screen, color, (start_x, line_y + i * 3), (end_x, line_y + i * 3), 2)
        
        # ============ BOTÓN JUGAR GIGANTE ============
        button_y = center_y + 250
        button_width = 400
        button_height = 100
        self.play_button_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_button_rect.center = (center_x, button_y)
        
        # Efecto hover
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.play_button_rect.collidepoint(mouse_pos)
        
        # Efecto de pulsación del botón
        button_pulse = 1.0 + (pulse * 0.1 if is_hover else pulse * 0.05)
        
        # Calcular tamaño con pulso
        pulsed_width = int(button_width * button_pulse)
        pulsed_height = int(button_height * button_pulse)
        pulsed_rect = pygame.Rect(0, 0, pulsed_width, pulsed_height)
        pulsed_rect.center = (center_x, button_y)
        
        # Resplandor del botón
        if is_hover:
            glow_size = int(20 + pulse * 15)
            glow_rect = pulsed_rect.inflate(glow_size, glow_size)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surf.set_alpha(int(80 + pulse * 50))
            glow_surf.fill((100, 255, 100))
            self.screen.blit(glow_surf, glow_rect.topleft)
        
        # Capas del botón (efecto 3D retro)
        for i in range(5, 0, -1):
            layer_color = (30 + i * 10, 100 + i * 15, 30 + i * 10) if is_hover else (20 + i * 8, 80 + i * 12, 20 + i * 8)
            layer_rect = pulsed_rect.inflate(-i * 2, -i * 2)
            layer_rect.y += i
            pygame.draw.rect(self.screen, layer_color, layer_rect, border_radius=20)
        
        # Botón principal
        button_color = (50, 220, 50) if is_hover else (40, 180, 40)
        pygame.draw.rect(self.screen, button_color, pulsed_rect, border_radius=20)
        
        # Borde brillante
        border_color = (200, 255, 200) if is_hover else (150, 255, 150)
        pygame.draw.rect(self.screen, border_color, pulsed_rect, 5, border_radius=20)
        
        # Texto del botón con efecto de brillo
        button_font = pygame.font.Font(None, 80)
        button_text = "JUGAR"
        
        # Sombra del texto
        text_shadow = button_font.render(button_text, True, (0, 0, 0))
        text_shadow_rect = text_shadow.get_rect(center=(center_x + 3, button_y + 3))
        self.screen.blit(text_shadow, text_shadow_rect)
        
        # Texto principal con brillo
        text_color = (255, 255, 255) if is_hover else (230, 255, 230)
        text_surf = button_font.render(button_text, True, text_color)
        text_rect = text_surf.get_rect(center=(center_x, button_y))
        self.screen.blit(text_surf, text_rect)
        
        # ============ SUBTÍTULO / INSTRUCCIÓN ============
        subtitle_font = pygame.font.Font(None, 30)
        subtitle_text = "Click para comenzar la aventura"
        subtitle_alpha = int(150 + pulse * 105)
        subtitle_surf = subtitle_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_surf.set_alpha(subtitle_alpha)
        subtitle_rect = subtitle_surf.get_rect(center=(center_x, self.height - 50))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Partículas decorativas (estrellas parpadeantes)
        for i in range(20):
            star_x = (i * 100 + time // 10) % self.width
            star_y = (i * 50 + time // 15) % self.height
            star_alpha = int((i % 3) * 85 + pulse * 85)
            if star_alpha > 30:
                pygame.draw.circle(self.screen, (255, 255, 150), (star_x, star_y), 2)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            # Manejo de eventos
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
                
                # Eventos específicos del MENÚ
                if self.game_state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.play_button_rect.collidepoint(event.pos):
                            print("▶ Iniciando juego...")
                            self.game_state = "playing"
                            # Cargar nivel inicial si no se ha cargado
                            if not hasattr(self, 'level') or not self.level:
                                if self.level_order:
                                    self.load_level_by_index(0)
                                else:
                                    # Fallback
                                    self.load_level(4, 1)
                    continue  # Saltar resto del loop si estamos en menú
                
                # Eventos de JUEGO
                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event.key)
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Detectar clics en botones de color (solo en nivel 3)
                    if 0 <= self.current_level_index < len(self.level_order) and "level3" in self.level_order[self.current_level_index]:
                        mouse_pos = event.pos
                        for button in self.color_buttons:
                            if button["rect"].collidepoint(mouse_pos):
                                self.change_player_color(button["color"])
                                break
            
            # Lógica de actualización (solo si estamos jugando)
            if self.game_state == "menu":
                self.draw_menu()
                self.clock.tick(FPS)
                continue
                
            if self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.update_game_over()
                self.draw_game_over()
            elif self.game_state == "game_complete":
                # Mostrar pantalla de completado (reutilizar UI por ahora)
                self.draw()
            
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
        message_font = pygame.font.Font(None, 36)
        
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
        
        # Contador de VIDAS (Solo Nivel 3)
        if 0 <= self.current_level_index < len(self.level_order):
            if "level3" in self.level_order[self.current_level_index]:
                # Dibujar icono
                if self.life_icon:
                    self.screen.blit(self.life_icon, (20, 50))
                else:
                    pygame.draw.circle(self.screen, (255, 50, 50), (36, 66), 16)
                
                # Dibujar número (puede ser negativo)
                lives_color = (255, 255, 255)
                if self.lives < 0:
                    lives_color = (255, 50, 50)  # Rojo si es negativo
                    
                lives_surf = message_font.render(f"x {self.lives}", True, lives_color)
                self.screen.blit(lives_surf, (60, 55))
        
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
