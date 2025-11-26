# main.py - COMPLETO CON CÁMARA Y SISTEMA DE GAME OVER
import pygame
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
        
        self.current_level = 1
        self.current_section = 1
        self.game_state = "playing"
        
        self.projectiles = []
        self.game_over_timer = 0
        self.death_message = ""
        
        self.camera = None
        
        self.load_level(1, 1)
    
    def load_level(self, level_num, section_num):
        """Carga nivel y crea el personaje"""
        self.level = Level(f"levels/level{level_num}_section{section_num}.txt")
        
        spawn_x, spawn_y = self.level.player_spawn
        
        if level_num <= 2:
            self.player = Mage(spawn_x, spawn_y)
        
        self.projectiles = []
        self.game_state = "playing"
        
        # Crear cámara
        level_width, level_height = self.level.get_dimensions()
        self.camera = Camera(level_width, level_height)
        print(f"📷 Cámara creada para nivel {level_width}x{level_height}")
    
    def reset_current_level(self):
        """Reinicia el nivel actual"""
        print("💀 GAME OVER - Reiniciando nivel...")
        self.load_level(self.current_level, 1)
        self.current_section = 1
    
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
        
        # Actualizar nivel
        level_state = self.level.update(self.player)
        
        # Verificar game over
        if level_state == "game_over":
            self.game_state = "game_over"
            self.game_over_timer = 180
            self.death_message = "¡EL JEFE TE ATRAPÓ!"
            return
        
        # Actualizar proyectiles del jugador
        for proj in self.projectiles[:]:
            proj.update(self.level.platforms)
            if not proj.alive:
                self.projectiles.remove(proj)
        
        # Verificar victoria
        if self.level.check_section_complete(self.player):
            self.current_section += 1
            print(f"✓ Sección {self.current_section - 1} completada!")
            self.load_level(self.current_level, self.current_section)
    
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
        mode_text = small_font.render(
            f"Nivel {self.current_level}-{self.current_section} | F11=Fullscreen | F=Disparar", 
            True, (200, 200, 200)
        )
        self.screen.blit(mode_text, (self.width - 450, 10))
    
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
