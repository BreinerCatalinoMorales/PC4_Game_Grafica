import pygame
import sys
import os
import json
from config import *

# Configuración del editor
EDITOR_WIDTH = 1024  # Resolución reducida
EDITOR_HEIGHT = 600
GRID_WIDTH = 100
GRID_HEIGHT = 50
SCROLL_SPEED = 15

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((EDITOR_WIDTH, EDITOR_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Editor de Niveles - PC4 Game")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Cargar tileset
        self.load_assets()
        self.load_tile_map()
        
        # Estado del editor
        self.mode = "editor" # "editor", "picker", "file_menu"
        self.scroll_x = 0
        self.scroll_y = 0
        self.current_tile = '#'
        self.grid = {}
        
        # Estado UI
        self.show_dropdown = False
        self.dropdown_scroll_offset = 0  # Para scroll en dropdown
        self.active_custom_char = None
        self.custom_tiles_list = []
        self.show_file_menu = False
        self.available_levels = []
        self.new_file_name = ""
        self.typing_new_file = False
        
        # Paleta base (Fija)
        self.fixed_palette = [
            {'char': '#', 'color': (100, 100, 100), 'name': 'Plataforma'},
            {'char': 'P', 'color': (0, 255, 0), 'name': 'Jugador'},
            {'char': 'G', 'color': (255, 215, 0), 'name': 'Meta'},
            {'char': 'B', 'color': (255, 0, 0), 'name': 'Jefe'},
        ]
        
        self.palette = []
        self.update_palette_from_map()
        
        self.selected_palette_idx = 0
        
        # Archivo actual
        self.current_file = "levels/level1_section1.txt"
        self.load_level(self.current_file)

    def load_assets(self):
        try:
            self.tile_image = pygame.image.load("assets/images/tiles/Mossy/Mossy - TileSet.png")
            self.tile_textures = {}
            self.tile_textures['#'] = self.extract_texture(1, 1)
        except Exception as e:
            print(f"Error cargando assets: {e}")
            self.tile_image = None
            self.tile_textures = {}

    def extract_texture(self, row, col):
        if not self.tile_image: return None
        try:
            rect = pygame.Rect(col * 512, row * 512, 512, 512)
            surf = self.tile_image.subsurface(rect)
            return pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
        except:
            return None

    def load_tile_map(self):
        self.tile_map = {}
        if os.path.exists("tile_map.json"):
            try:
                with open("tile_map.json", "r") as f:
                    self.tile_map = json.load(f)
            except: pass

    def save_tile_map(self):
        try:
            with open("tile_map.json", "w") as f:
                json.dump(self.tile_map, f, indent=4)
        except: pass

    def update_palette_from_map(self):
        self.custom_tiles_list = []
        for char, data in self.tile_map.items():
            texture = self.extract_texture(data['row'], data['col'])
            self.custom_tiles_list.append({
                'char': char,
                'name': data.get('name', char),
                'texture': texture,
                'row': data['row'],
                'col': data['col']
            })
            if texture:
                self.tile_textures[char] = texture

        if self.active_custom_char is None and self.custom_tiles_list:
            self.active_custom_char = self.custom_tiles_list[0]['char']
        
        self.palette = list(self.fixed_palette)
        
        custom_slot = {
            'char': self.active_custom_char,
            'color': (150, 100, 50),
            'name': 'Textura',
            'is_custom_slot': True
        }
        if self.active_custom_char and self.active_custom_char in self.tile_textures:
            custom_slot['texture'] = self.tile_textures[self.active_custom_char]
            
        self.palette.append(custom_slot)
        self.palette.append({'char': None, 'color': (50, 50, 50), 'name': 'Borrar'})

    def load_level(self, filename):
        self.grid = {}
        if not os.path.exists(filename): return
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                for row, line in enumerate(lines):
                    for col, char in enumerate(line.strip('\n')):
                        if char != ' ':
                            self.grid[(col, row)] = char
            self.current_file = filename
            print(f"Nivel cargado: {filename}")
        except: pass

    def save_level(self, filename):
        if not self.grid: return
        max_col = max(pos[0] for pos in self.grid.keys())
        max_row = max(pos[1] for pos in self.grid.keys())
        try:
            with open(filename, 'w') as f:
                for row in range(max_row + 1):
                    line = ""
                    for col in range(max_col + 1):
                        char = self.grid.get((col, row), ' ')
                        line += char
                    f.write(line.rstrip() + '\n')
            print(f"Nivel guardado en {filename}")
        except: pass

    def refresh_file_list(self):
        self.available_levels = []
        if os.path.exists("levels"):
            for f in os.listdir("levels"):
                if f.endswith(".txt"):
                    self.available_levels.append(f)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.mode == "editor":
                self.handle_editor_click(event)
            elif self.mode == "picker":
                self.handle_picker_click(event)
            elif self.mode == "file_menu":
                self.handle_file_menu_click(event)
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll en dropdown
            if self.show_dropdown:
                self.dropdown_scroll_offset -= event.y * 30  # event.y es positivo al scroll up
                # Limitar scroll
                max_scroll = max(0, (len(self.custom_tiles_list) + 1) * 50 - 300)  # 300 = altura visible
                self.dropdown_scroll_offset = max(0, min(self.dropdown_scroll_offset, max_scroll))
                
        elif event.type == pygame.KEYDOWN:
            if self.typing_new_file:
                if event.key == pygame.K_RETURN:
                    if self.new_file_name:
                        if not self.new_file_name.endswith(".txt"):
                            self.new_file_name += ".txt"
                        self.current_file = f"levels/{self.new_file_name}"
                        self.grid = {} # Limpiar grid para nuevo nivel
                        self.save_level(self.current_file) # Crear archivo
                        self.mode = "editor"
                        self.typing_new_file = False
                elif event.key == pygame.K_BACKSPACE:
                    self.new_file_name = self.new_file_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.typing_new_file = False
                else:
                    self.new_file_name += event.unicode
                return

            if self.mode == "editor":
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.save_level(self.current_file)
                elif event.key == pygame.K_t:
                    self.mode = "picker"
            elif self.mode == "picker":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_t:
                    self.mode = "editor"
            elif self.mode == "file_menu":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "editor"

    def handle_continuous_input(self):
        if self.typing_new_file: return
        
        keys = pygame.key.get_pressed()
        if self.mode == "editor":
            if keys[pygame.K_RIGHT]: self.scroll_x += SCROLL_SPEED
            if keys[pygame.K_LEFT]: self.scroll_x -= SCROLL_SPEED
            if keys[pygame.K_DOWN]: self.scroll_y += SCROLL_SPEED
            if keys[pygame.K_UP]: self.scroll_y -= SCROLL_SPEED
            
            if pygame.mouse.get_pressed()[0] and not self.show_dropdown and not self.show_file_menu:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] > 200 and mouse_pos[1] > 40: # Respetar barra superior y lateral
                    self.paint_tile(mouse_pos)
            
            if pygame.mouse.get_pressed()[2]:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] > 200 and mouse_pos[1] > 40:
                    self.delete_tile(mouse_pos)

    def paint_tile(self, mouse_pos):
        world_x = mouse_pos[0] + self.scroll_x
        world_y = mouse_pos[1] + self.scroll_y
        col = int(world_x // TILE_SIZE)
        row = int(world_y // TILE_SIZE)
        if self.current_tile: self.grid[(col, row)] = self.current_tile
        elif (col, row) in self.grid: del self.grid[(col, row)]

    def delete_tile(self, mouse_pos):
        world_x = mouse_pos[0] + self.scroll_x
        world_y = mouse_pos[1] + self.scroll_y
        col = int(world_x // TILE_SIZE)
        row = int(world_y // TILE_SIZE)
        if (col, row) in self.grid: del self.grid[(col, row)]

    def handle_editor_click(self, event):
        mouse_pos = event.pos
        button = event.button
        
        if button == 1:
            # 0. Botón Archivo (Top Left)
            if 0 <= mouse_pos[0] <= 100 and 0 <= mouse_pos[1] <= 30:
                self.mode = "file_menu"
                self.refresh_file_list()
                return

            # 1. Dropdown
            if self.show_dropdown:
                dd_x = 60
                dd_y = 4 * 60 + 10 + 40 # Ajuste por barra superior
                dd_w = 200
                dd_h = min(300, (len(self.custom_tiles_list) + 1) * 50)  # Altura máxima 300px
                
                if dd_x <= mouse_pos[0] <= dd_x + dd_w and dd_y <= mouse_pos[1] <= dd_y + dd_h:
                    # Ajustar por scroll
                    relative_y = mouse_pos[1] - dd_y + self.dropdown_scroll_offset
                    idx = relative_y // 50
                    if idx < len(self.custom_tiles_list):
                        self.active_custom_char = self.custom_tiles_list[idx]['char']
                        self.update_palette_from_map()
                        self.selected_palette_idx = 4
                        self.current_tile = self.active_custom_char
                        self.show_dropdown = False
                        self.dropdown_scroll_offset = 0
                    elif idx == len(self.custom_tiles_list):
                        self.mode = "picker"
                        self.show_dropdown = False
                        self.dropdown_scroll_offset = 0
                    return
                else:
                    self.show_dropdown = False
                    self.dropdown_scroll_offset = 0
                    return

            # 2. Paleta (Sidebar)
            if mouse_pos[0] < 200 and mouse_pos[1] > 40:
                idx = (mouse_pos[1] - 40) // 60
                if 0 <= idx < len(self.palette):
                    item = self.palette[idx]
                    if item.get('is_custom_slot'):
                        self.show_dropdown = not self.show_dropdown
                        self.selected_palette_idx = idx
                        if not self.active_custom_char:
                            self.mode = "picker"
                            self.show_dropdown = False
                        else:
                            self.current_tile = self.active_custom_char
                    else:
                        self.selected_palette_idx = idx
                        self.current_tile = item['char']
                        self.show_dropdown = False
                return

            # 3. Grid
            if mouse_pos[0] > 200 and mouse_pos[1] > 40:
                self.paint_tile(mouse_pos)

        elif button == 3:
            if mouse_pos[0] > 200 and mouse_pos[1] > 40:
                self.delete_tile(mouse_pos)

    def handle_picker_click(self, event):
        if event.button == 1:
            mouse_pos = event.pos
            scale = 0.2
            img_x, img_y = 50, 50
            
            rel_x = (mouse_pos[0] - img_x) / scale
            rel_y = (mouse_pos[1] - img_y) / scale
            col = int(rel_x // 512)
            row = int(rel_y // 512)
            
            if 0 <= col < 7 and 0 <= row < 7:
                self.assign_new_tile(row, col)
                self.mode = "editor"

    def handle_file_menu_click(self, event):
        if event.button == 1:
            mouse_pos = event.pos
            
            # Botón Nuevo Nivel
            if 50 <= mouse_pos[0] <= 250 and 50 <= mouse_pos[1] <= 90:
                self.typing_new_file = True
                self.new_file_name = ""
                return
                
            # Lista de archivos
            start_y = 110
            for i, f in enumerate(self.available_levels):
                y = start_y + i * 40
                if 50 <= mouse_pos[0] <= 400 and y <= mouse_pos[1] <= y + 30:
                    self.load_level(f"levels/{f}")
                    self.mode = "editor"
                    return
            
            # Click fuera -> cerrar
            self.mode = "editor"

    def assign_new_tile(self, row, col):
        for char, data in self.tile_map.items():
            if data['row'] == row and data['col'] == col:
                print(f"Tile existente: {char}")
                self.active_custom_char = char
                self.update_palette_from_map()
                self.selected_palette_idx = 4
                self.current_tile = char
                return

        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        used = list(self.tile_map.keys()) + [p['char'] for p in self.fixed_palette]
        new_char = next((c for c in chars if c not in used), None)
        
        if new_char:
            self.tile_map[new_char] = {
                "row": row, "col": col, "name": f"Tile {new_char}"
            }
            self.save_tile_map()
            self.active_custom_char = new_char
            self.update_palette_from_map()
            self.selected_palette_idx = 4
            self.current_tile = new_char
            print(f"Nuevo tile: {new_char}")

    def draw_grid(self):
        start_col = int(self.scroll_x // TILE_SIZE)
        end_col = start_col + (EDITOR_WIDTH // TILE_SIZE) + 2
        start_row = int(self.scroll_y // TILE_SIZE)
        end_row = start_row + (EDITOR_HEIGHT // TILE_SIZE) + 2
        
        for col in range(start_col, end_col):
            for row in range(start_row, end_row):
                x = col * TILE_SIZE - self.scroll_x
                y = row * TILE_SIZE - self.scroll_y
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)
                
                if (col, row) in self.grid:
                    char = self.grid[(col, row)]
                    if char in self.tile_textures:
                        self.screen.blit(self.tile_textures[char], rect)
                    else:
                        color = (200, 200, 200)
                        for p in self.palette:
                            if p['char'] == char: color = p['color']; break
                        pygame.draw.rect(self.screen, color, rect)
                        
                    text = self.font.render(char, True, (255, 255, 255))
                    self.screen.blit(text, (x + 10, y + 10))
        
        if not self.show_dropdown and not self.show_file_menu:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > 200 and mouse_pos[1] > 40:
                world_x = mouse_pos[0] + self.scroll_x
                world_y = mouse_pos[1] + self.scroll_y
                col = int(world_x // TILE_SIZE)
                row = int(world_y // TILE_SIZE)
                x = col * TILE_SIZE - self.scroll_x
                y = row * TILE_SIZE - self.scroll_y
                
                preview_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (255, 255, 255), preview_rect, 2)
                
                if self.current_tile and self.current_tile in self.tile_textures:
                    ghost = self.tile_textures[self.current_tile].copy()
                    ghost.set_alpha(128)
                    self.screen.blit(ghost, preview_rect)

    def draw_ui(self):
        # Barra Superior
        pygame.draw.rect(self.screen, (60, 60, 60), (0, 0, EDITOR_WIDTH, 40))
        
        # Botón Archivo
        pygame.draw.rect(self.screen, (80, 80, 80), (0, 0, 100, 40))
        text = self.font.render("Archivo", True, (255, 255, 255))
        self.screen.blit(text, (15, 10))
        
        # Nombre archivo actual
        text = self.font.render(f"Editando: {self.current_file}", True, (200, 200, 200))
        self.screen.blit(text, (120, 10))

        # Barra Lateral
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 40, 200, EDITOR_HEIGHT - 40))
        
        for i, item in enumerate(self.palette):
            y = 40 + i * 60
            rect = pygame.Rect(10, y + 10, 40, 40)
            
            if i == self.selected_palette_idx:
                pygame.draw.rect(self.screen, (255, 255, 0), (5, y + 5, 190, 50), 2)
            
            if 'texture' in item and item['texture']:
                self.screen.blit(pygame.transform.scale(item['texture'], (40, 40)), rect)
            else:
                pygame.draw.rect(self.screen, item['color'], rect)
            
            name = item['name']
            if item.get('is_custom_slot') and self.active_custom_char:
                name = f"Tile {self.active_custom_char}"
                pygame.draw.polygon(self.screen, (255, 255, 255), [(180, y+25), (190, y+25), (185, y+35)])
                
            text = self.font.render(name, True, (255, 255, 255))
            self.screen.blit(text, (60, y + 20))

        if self.show_dropdown:
            dd_x = 60
            dd_y = 40 + 4 * 60 + 10
            dd_w = 200
            dd_h = min(300, (len(self.custom_tiles_list) + 1) * 50)  # Altura máxima visible
            
            # Fondo del dropdown
            pygame.draw.rect(self.screen, (60, 60, 60), (dd_x, dd_y, dd_w, dd_h))
            pygame.draw.rect(self.screen, (200, 200, 200), (dd_x, dd_y, dd_w, dd_h), 1)
            
            # Crear superficie para clipping
            dropdown_surface = pygame.Surface((dd_w, dd_h))
            dropdown_surface.fill((60, 60, 60))
            
            # Dibujar items con offset de scroll
            for i, tile in enumerate(self.custom_tiles_list):
                item_y = i * 50 - self.dropdown_scroll_offset
                
                # Solo dibujar si está visible
                if -50 < item_y < dd_h:
                    # Highlight hover
                    mx, my = pygame.mouse.get_pos()
                    screen_y = dd_y + item_y
                    if dd_x <= mx <= dd_x + dd_w and screen_y <= my <= screen_y + 50 and dd_y <= my <= dd_y + dd_h:
                        pygame.draw.rect(dropdown_surface, (80, 80, 80), (0, item_y, dd_w, 50))
                    
                    if tile['texture']:
                        dropdown_surface.blit(pygame.transform.scale(tile['texture'], (40, 40)), (5, item_y + 5))
                    
                    text = self.font.render(f"Tile {tile['char']}", True, (255, 255, 255))
                    dropdown_surface.blit(text, (55, item_y + 15))
            
            # Botón "+"
            plus_y = len(self.custom_tiles_list) * 50 - self.dropdown_scroll_offset
            if -50 < plus_y < dd_h:
                mx, my = pygame.mouse.get_pos()
                screen_y = dd_y + plus_y
                if dd_x <= mx <= dd_x + dd_w and screen_y <= my <= screen_y + 50 and dd_y <= my <= dd_y + dd_h:
                    pygame.draw.rect(dropdown_surface, (80, 80, 80), (0, plus_y, dd_w, 50))
                text = self.font.render("+ NUEVO TILE", True, (100, 255, 100))
                dropdown_surface.blit(text, (50, plus_y + 15))
            
            # Blit superficie con clipping
            self.screen.blit(dropdown_surface, (dd_x, dd_y))
            
            # Indicador de scroll si hay más contenido
            total_content_h = (len(self.custom_tiles_list) + 1) * 50
            if total_content_h > dd_h:
                # Barra de scroll
                scrollbar_h = max(20, dd_h * dd_h // total_content_h)
                scrollbar_y = dd_y + (self.dropdown_scroll_offset * dd_h // total_content_h)
                pygame.draw.rect(self.screen, (150, 150, 150), (dd_x + dd_w - 5, scrollbar_y, 5, scrollbar_h))

    def draw_file_menu(self):
        overlay = pygame.Surface((EDITOR_WIDTH, EDITOR_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = self.font.render("SELECCIONAR NIVEL", True, (255, 255, 255))
        self.screen.blit(title, (50, 20))
        
        # Botón Nuevo
        pygame.draw.rect(self.screen, (50, 150, 50), (50, 50, 200, 40))
        text = self.font.render("+ Crear Nuevo Nivel", True, (255, 255, 255))
        self.screen.blit(text, (60, 60))
        
        if self.typing_new_file:
            pygame.draw.rect(self.screen, (255, 255, 255), (260, 50, 300, 40), 2)
            text = self.font.render(self.new_file_name + "|", True, (255, 255, 255))
            self.screen.blit(text, (270, 60))
            help_text = self.small_font.render("Escribe nombre y presiona ENTER", True, (150, 150, 150))
            self.screen.blit(help_text, (270, 95))
        
        # Lista
        start_y = 110
        for i, f in enumerate(self.available_levels):
            y = start_y + i * 40
            
            mx, my = pygame.mouse.get_pos()
            color = (60, 60, 60)
            if 50 <= mx <= 400 and y <= my <= y + 30:
                color = (100, 100, 100)
            
            pygame.draw.rect(self.screen, color, (50, y, 350, 30))
            text = self.font.render(f, True, (200, 200, 200))
            self.screen.blit(text, (60, y + 5))

    def draw_picker(self):
        overlay = pygame.Surface((EDITOR_WIDTH, EDITOR_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.tile_image:
            scale = 0.2
            w = int(self.tile_image.get_width() * scale)
            h = int(self.tile_image.get_height() * scale)
            scaled_img = pygame.transform.scale(self.tile_image, (w, h))
            self.screen.blit(scaled_img, (50, 50))
            
            rows = 7
            cols = 7
            tile_s = 512 * scale
            for r in range(rows):
                for c in range(cols):
                    rect = pygame.Rect(50 + c*tile_s, 50 + r*tile_s, tile_s, tile_s)
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
            
            text = self.font.render("Haz CLICK en un tile para añadirlo", True, (255, 255, 255))
            self.screen.blit(text, (50, 20))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.handle_event(event)

            self.handle_continuous_input()
            self.screen.fill((20, 20, 20))
            
            if self.mode == "editor":
                self.draw_grid()
                self.draw_ui()
            elif self.mode == "picker":
                self.draw_picker()
            elif self.mode == "file_menu":
                self.draw_file_menu()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
