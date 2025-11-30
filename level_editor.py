import pygame
import sys
import os
import json
from config import *

EDITOR_WIDTH = 1200
EDITOR_HEIGHT = 700
GRID_WIDTH = 100
GRID_HEIGHT = 50
SCROLL_SPEED = 15

SIDEBAR_WIDTH = 300
TOPBAR_HEIGHT = 50

class LevelEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((EDITOR_WIDTH, EDITOR_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Editor de Niveles - MODO EDICION")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.header_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.palette_monsters = [
            {'char': 'E', 'color': (200, 100, 255), 'name': 'Flying Eye', 'path': 'Flying eye'},
            {'char': 'O', 'color': (50, 150, 50),   'name': 'Goblin',     'path': 'Goblin'},
            {'char': 'H', 'color': (200, 50, 50),   'name': 'Mushroom',   'path': 'Mushroom'},
            {'char': 'K', 'color': (220, 220, 220), 'name': 'Skeleton',   'path': 'Skeleton'},
        ]
        
        self.palette_objects = [
            {'char': 'P', 'color': (0, 255, 0),   'name': 'Jugador'},
            {'char': 'G', 'color': (255, 215, 0), 'name': 'Meta'},
            {'char': 'B', 'color': (200, 0, 0),   'name': 'Jefe (GNU)'},
            {'char': 'U', 'color': (100, 0, 0),   'name': 'Jefe (Undead)'},
        ]

        self.reserved_chars = [m['char'] for m in self.palette_monsters] + \
                              [o['char'] for o in self.palette_objects] + \
                              ['S', 'M']

        self.tile_textures = {}
        self.monsters_textures = {}
        self.autotiles = {} 
        self.load_assets()
        self.load_monster_assets()
        
        self.active_custom_char = None
        self.custom_tiles_list = []
        
        self.load_tile_map()
        
        self.mode = "editor" 
        self.scroll_x = -SIDEBAR_WIDTH - 50 
        self.scroll_y = -TOPBAR_HEIGHT - 50
        
        self.current_tile = '#' 
        self.grid = {}
        
        self.show_dropdown = False
        self.dropdown_scroll_offset = 0  
        self.sidebar_scroll_offset = 0
        
        self.show_file_menu = False
        self.available_levels = []
        self.new_file_name = ""
        self.typing_new_file = False
        self.current_file = "levels/level1_section1.txt"
        self.load_level(self.current_file)

    def load_assets(self):
        try:
            self.tile_image = pygame.image.load("assets/images/tiles/Mossy/Mossy - TileSet.png")
            
            autotile_names = [
                ['top_left', 'top', 'top_right'],
                ['left', 'center', 'right'],
                ['bottom_left', 'bottom', 'bottom_right']
            ]
            
            for r in range(3):
                for c in range(3):
                    tex = self.extract_texture(r, c)
                    name = autotile_names[r][c]
                    self.autotiles[name] = tex
            
            self.tile_textures['#'] = self.autotiles['center']
            
        except Exception:
            self.tile_image = None

    def load_monster_assets(self):
        base_path = "Monsters_Creatures_Fantasy"
        for item in self.palette_monsters:
            try:
                path = os.path.join(base_path, item['path'])
                found = None
                if os.path.exists(path):
                    for f in os.listdir(path):
                        if f.endswith('.png') and ("Idle" in f or "Fly" in f or "Run" in f):
                            found = os.path.join(path, f)
                            break
                    if not found and os.path.exists(path): 
                         for f in os.listdir(path):
                            if f.endswith('.png'): found = os.path.join(path, f); break
                
                if found:
                    img = pygame.image.load(found)
                    if img.get_width() > 150: 
                        img = img.subsurface(0, 0, img.get_height(), img.get_height())
                    
                    self.monsters_textures[item['char']] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                    item['texture'] = pygame.transform.scale(img, (50, 50))
                else:
                    item['texture'] = None
            except:
                item['texture'] = None

    def extract_texture(self, row, col):
        if not self.tile_image: return None
        try:
            rect = pygame.Rect(col * 512, row * 512, 512, 512)
            surf = self.tile_image.subsurface(rect)
            return pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
        except: return None

    def load_tile_map(self):
        self.tile_map = {}
        if os.path.exists("tile_map.json"):
            try:
                with open("tile_map.json", "r") as f:
                    loaded_map = json.load(f)
                    for char, data in loaded_map.items():
                        if char not in self.reserved_chars:
                            self.tile_map[char] = data
            except: pass
        
        my_tiles = {
            "T": { "row": 4, "col": 0, "name": "Tierra" },
            "A": { "row": 1, "col": 4, "name": "Tile A" },
            "C": { "row": 0, "col": 0, "name": "Tile C" },
            "D": { "row": 0, "col": 2, "name": "Tile D" },
            "F": { "row": 1, "col": 2, "name": "Tile F" },
            "I": { "row": 1, "col": 1, "name": "Tile I" },
            "J": { "row": 0, "col": 3, "name": "Tile J" },
            "L": { "row": 3, "col": 2, "name": "Tile L" },
            "N": { "row": 4, "col": 4, "name": "Muro N" },
            "Q": { "row": 3, "col": 0, "name": "Muro Q" }
        }
        
        for char, data in my_tiles.items():
            self.tile_map[char] = data
        
        self.save_tile_map()
        self.update_custom_tiles_list()

    def save_tile_map(self):
        try:
            with open("tile_map.json", "w") as f:
                json.dump(self.tile_map, f, indent=4)
        except: pass

    def update_custom_tiles_list(self):
        self.custom_tiles_list = []
        sorted_items = sorted(self.tile_map.items(), key=lambda item: item[0])
        
        for char, data in sorted_items:
            texture = self.extract_texture(data['row'], data['col'])
            self.custom_tiles_list.append({
                'char': char,
                'name': data.get('name', f"Tile {char}"),
                'texture': texture,
                'row': data['row'],
                'col': data['col']
            })
            if texture:
                self.tile_textures[char] = texture
        
        if self.active_custom_char is None and self.custom_tiles_list:
            self.active_custom_char = self.custom_tiles_list[0]['char']
        elif self.active_custom_char is None and 'T' in self.tile_map:
            self.active_custom_char = 'T'

    def assign_new_tile(self, row, col):
        for char, data in self.tile_map.items():
            if data['row'] == row and data['col'] == col:
                self.active_custom_char = char
                self.current_tile = char
                return

        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        used = list(self.tile_map.keys()) + self.reserved_chars
        new_char = next((c for c in chars if c not in used), None)
        
        if new_char:
            self.tile_map[new_char] = {"row": row, "col": col, "name": f"Custom {new_char}"}
            self.save_tile_map()
            self.update_custom_tiles_list()
            self.active_custom_char = new_char
            self.current_tile = new_char

    def draw_grid(self):
        start_col = int(self.scroll_x // TILE_SIZE) - 1
        end_col = start_col + (EDITOR_WIDTH // TILE_SIZE) + 4
        start_row = int(self.scroll_y // TILE_SIZE) - 1
        end_row = start_row + (EDITOR_HEIGHT // TILE_SIZE) + 4
        
        for col in range(start_col, end_col):
            for row in range(start_row, end_row):
                x = col * TILE_SIZE - self.scroll_x
                y = row * TILE_SIZE - self.scroll_y
                
                if x < SIDEBAR_WIDTH - TILE_SIZE or y < TOPBAR_HEIGHT - TILE_SIZE or x > EDITOR_WIDTH or y > EDITOR_HEIGHT:
                    continue
                
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (20, 20, 20), rect)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)
                
                if (col, row) in self.grid:
                    char = self.grid[(col, row)]
                    
                    if char == '#':
                        has_top = self.grid.get((col, row - 1)) == '#'
                        has_bottom = self.grid.get((col, row + 1)) == '#'
                        has_left = self.grid.get((col - 1, row)) == '#'
                        has_right = self.grid.get((col + 1, row)) == '#'
                        
                        key = 'center'
                        if not has_top and not has_left: key = 'top_left'
                        elif not has_top and not has_right: key = 'top_right'
                        elif not has_bottom and not has_left: key = 'bottom_left'
                        elif not has_bottom and not has_right: key = 'bottom_right'
                        elif not has_top: key = 'top'
                        elif not has_bottom: key = 'bottom'
                        elif not has_left: key = 'left'
                        elif not has_right: key = 'right'
                        else: key = 'center'
                        
                        if key in self.autotiles:
                            self.screen.blit(self.autotiles[key], rect)
                        else:
                            self.screen.blit(self.autotiles['center'], rect)
                            
                    elif char in self.monsters_textures and self.monsters_textures[char]:
                        self.screen.blit(self.monsters_textures[char], rect)
                        pygame.draw.rect(self.screen, (0,0,0), (x, y, 15, 15))
                        self.screen.blit(self.small_font.render(char, True, (255,255,255)), (x+3, y))
                    
                    elif char in self.tile_textures and self.tile_textures[char]:
                        self.screen.blit(self.tile_textures[char], rect)
                    
                    else:
                        color = (150, 150, 150)
                        for m in self.palette_monsters: 
                            if m['char'] == char: color = m['color']
                        for o in self.palette_objects:
                            if o['char'] == char: color = o['color']
                        pygame.draw.rect(self.screen, color, rect)
                        self.screen.blit(self.font.render(char, True, (0,0,0)), (x+20, y+20))

        if not self.show_dropdown and not self.show_file_menu:
            mx, my = pygame.mouse.get_pos()
            if mx > SIDEBAR_WIDTH and my > TOPBAR_HEIGHT:
                col = int((mx + self.scroll_x) // TILE_SIZE)
                row = int((my + self.scroll_y) // TILE_SIZE)
                x = col * TILE_SIZE - self.scroll_x
                y = row * TILE_SIZE - self.scroll_y
                
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 3)
                
                if self.current_tile:
                    tex = None
                    if self.current_tile == '#' and 'center' in self.autotiles:
                        tex = self.autotiles['center']
                    elif self.current_tile in self.monsters_textures: 
                        tex = self.monsters_textures[self.current_tile]
                    elif self.current_tile in self.tile_textures:
                        tex = self.tile_textures[self.current_tile]
                    
                    if tex:
                        ghost = tex.copy()
                        ghost.set_alpha(150)
                        self.screen.blit(ghost, (x, y))
                    else:
                        self.screen.blit(self.font.render(self.current_tile, True, (255,255,255)), (x+25, y+20))
                else:
                    pygame.draw.line(self.screen, (255, 50, 50), (x, y), (x+64, y+64), 5)
                    pygame.draw.line(self.screen, (255, 50, 50), (x+64, y), (x, y+64), 5)

    def draw_ui(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, EDITOR_WIDTH, TOPBAR_HEIGHT))
        pygame.draw.line(self.screen, (100, 100, 100), (0, TOPBAR_HEIGHT), (EDITOR_WIDTH, TOPBAR_HEIGHT), 2)
        
        pygame.draw.rect(self.screen, (70, 70, 70), (0, 0, 120, TOPBAR_HEIGHT))
        self.screen.blit(self.font.render("📂 ARCHIVO", True, (255, 255, 255)), (10, 12))
        
        info = f"Nivel: {self.new_file_name if self.typing_new_file else self.current_file}"
        self.screen.blit(self.small_font.render(info, True, (150, 150, 150)), (140, 15))

        pygame.draw.rect(self.screen, (40, 40, 45), (0, TOPBAR_HEIGHT, SIDEBAR_WIDTH, EDITOR_HEIGHT))
        pygame.draw.line(self.screen, (100, 100, 100), (SIDEBAR_WIDTH, TOPBAR_HEIGHT), (SIDEBAR_WIDTH, EDITOR_HEIGHT), 2)

        borrador_y = TOPBAR_HEIGHT + 10
        rect_borrador = pygame.Rect(10, borrador_y, SIDEBAR_WIDTH - 20, 60)
        col_bor = (200, 60, 60) if self.current_tile is None else (120, 40, 40)
        pygame.draw.rect(self.screen, col_bor, rect_borrador, border_radius=8)
        if self.current_tile is None:
            pygame.draw.rect(self.screen, (255, 255, 0), rect_borrador, 3, border_radius=8)
        
        txt = self.font.render("BORRADOR (Click Der)", True, (255, 255, 255))
        self.screen.blit(txt, (rect_borrador.centerx - txt.get_width()//2, rect_borrador.centery - txt.get_height()//2))

        scroll_area_y = borrador_y + 70
        scroll_area_h = EDITOR_HEIGHT - scroll_area_y
        sidebar_clip = pygame.Rect(0, scroll_area_y, SIDEBAR_WIDTH, scroll_area_h)
        self.screen.set_clip(sidebar_clip)
        
        cursor_y = scroll_area_y + 10 - self.sidebar_scroll_offset

        self.screen.blit(self.header_font.render("MONSTRUOS", True, (100, 200, 255)), (20, cursor_y))
        cursor_y += 35
        for m in self.palette_monsters:
            r = pygame.Rect(15, cursor_y, 50, 50)
            if self.current_tile == m['char']:
                pygame.draw.rect(self.screen, (255, 255, 0), (10, cursor_y - 5, SIDEBAR_WIDTH - 20, 60), 2, border_radius=5)
            
            if m['texture']: self.screen.blit(m['texture'], r)
            else: 
                pygame.draw.rect(self.screen, m['color'], r)
                self.screen.blit(self.font.render(m['char'], True, (0,0,0)), (r.x+15, r.y+10))
            
            self.screen.blit(self.font.render(m['name'], True, (220, 220, 220)), (75, cursor_y + 12))
            cursor_y += 65

        cursor_y += 10
        self.screen.blit(self.header_font.render("OBJETOS", True, (100, 255, 100)), (20, cursor_y))
        cursor_y += 35
        for o in self.palette_objects:
            r = pygame.Rect(15, cursor_y, 50, 50)
            if self.current_tile == o['char']:
                pygame.draw.rect(self.screen, (255, 255, 0), (10, cursor_y - 5, SIDEBAR_WIDTH - 20, 60), 2, border_radius=5)
            
            pygame.draw.rect(self.screen, o['color'], r)
            self.screen.blit(self.font.render(o['name'], True, (220, 220, 220)), (75, cursor_y + 12))
            cursor_y += 65

        cursor_y += 10
        self.screen.blit(self.header_font.render("TEXTURAS / TILES", True, (255, 255, 100)), (20, cursor_y))
        cursor_y += 35
        
        r = pygame.Rect(15, cursor_y, 50, 50)
        if self.current_tile == '#':
            pygame.draw.rect(self.screen, (255, 255, 0), (10, cursor_y - 5, SIDEBAR_WIDTH - 20, 60), 2, border_radius=5)
        
        if 'center' in self.autotiles:
            self.screen.blit(pygame.transform.scale(self.autotiles['center'], (50, 50)), r)
        else: 
            pygame.draw.rect(self.screen, (100, 100, 100), r)
        
        self.screen.blit(self.font.render("Tierra Base (#)", True, (220, 220, 220)), (75, cursor_y + 12))
        cursor_y += 65

        custom_btn_rect = pygame.Rect(15, cursor_y, SIDEBAR_WIDTH - 30, 60)
        pygame.draw.rect(self.screen, (60, 60, 80), custom_btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 150), custom_btn_rect, 2, border_radius=8)
        
        if self.active_custom_char and self.active_custom_char in self.tile_textures:
            prev = pygame.transform.scale(self.tile_textures[self.active_custom_char], (40, 40))
            self.screen.blit(prev, (25, cursor_y + 10))
            
        self.screen.blit(self.font.render("CATÁLOGO DE TILES", True, (255, 255, 255)), (80, cursor_y + 18))
        
        if self.current_tile == self.active_custom_char and self.current_tile not in self.reserved_chars and self.current_tile != '#':
             pygame.draw.rect(self.screen, (255, 255, 0), custom_btn_rect, 3, border_radius=8)

        self.screen.set_clip(None)

        if self.show_dropdown:
            self.draw_picker()

    def draw_file_menu(self):
        overlay = pygame.Surface((EDITOR_WIDTH, EDITOR_HEIGHT))
        overlay.set_alpha(230); overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))
        
        cx, cy = EDITOR_WIDTH//2, EDITOR_HEIGHT//2
        w, h = 600, 500
        panel = pygame.Rect(cx - w//2, cy - h//2, w, h)
        pygame.draw.rect(self.screen, (40,40,40), panel, border_radius=10)
        pygame.draw.rect(self.screen, (100,100,100), panel, 2, border_radius=10)
        
        self.screen.blit(self.header_font.render("GESTION DE NIVELES", True, (255,255,255)), (panel.x+20, panel.y+20))
        
        new_btn = pygame.Rect(panel.x+20, panel.y+60, w-40, 50)
        pygame.draw.rect(self.screen, (60,60,60), new_btn, border_radius=5)
        
        if self.typing_new_file:
            txt = self.new_file_name + "|"
            col = (255,255,200)
        else:
            txt = "+ ESCRIBIR NOMBRE DE NUEVO NIVEL..."
            col = (150,150,150)
        self.screen.blit(self.font.render(txt, True, col), (panel.x+30, panel.y+75))
        
        save_btn_rect = pygame.Rect(panel.x+20, panel.y+120, w-40, 50)
        pygame.draw.rect(self.screen, (50, 100, 50), save_btn_rect, border_radius=5)
        self.screen.blit(self.font.render("💾 GUARDAR NIVEL ACTUAL", True, (200, 255, 200)), (panel.x+30, panel.y+135))
        
        self.screen.blit(self.font.render("Niveles existentes:", True, (200,200,200)), (panel.x+20, panel.y+190))
        
        list_y = panel.y + 220
        for f in self.available_levels:
            r = pygame.Rect(panel.x+20, list_y, w-40, 40)
            
            mx, my = pygame.mouse.get_pos()
            color = (50,50,60)
            if r.collidepoint(mx, my): color = (70,70,80)
            
            pygame.draw.rect(self.screen, color, r, border_radius=5)
            self.screen.blit(self.font.render(f, True, (255,255,255)), (r.x+10, r.y+10))
            list_y += 45

    def draw_picker(self):
        overlay = pygame.Surface((EDITOR_WIDTH, EDITOR_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.tile_image:
            scale = 0.4
            img_w = self.tile_image.get_width()
            img_h = self.tile_image.get_height()
            disp_w = int(img_w * scale)
            disp_h = int(img_h * scale)
            
            pos_x = (EDITOR_WIDTH - disp_w) // 2
            pos_y = (EDITOR_HEIGHT - disp_h) // 2
            
            self.screen.blit(pygame.transform.scale(self.tile_image, (disp_w, disp_h)), (pos_x, pos_y))
            
            tile_s = 512 * scale
            rows = img_h // 512
            cols = img_w // 512
            
            for r in range(rows + 1):
                y = pos_y + r * tile_s
                pygame.draw.line(self.screen, (255, 255, 0), (pos_x, y), (pos_x + disp_w, y), 2)
                if r < rows:
                    lbl = self.small_font.render(f"F{r}", True, (255, 255, 0))
                    self.screen.blit(lbl, (pos_x - 30, y + tile_s//2 - 10))

            for c in range(cols + 1):
                x = pos_x + c * tile_s
                pygame.draw.line(self.screen, (255, 255, 0), (x, pos_y), (x, pos_y + disp_h), 2)
                if c < cols:
                    lbl = self.small_font.render(f"C{c}", True, (255, 255, 0))
                    self.screen.blit(lbl, (x + tile_s//2 - 10, pos_y - 20))

            self.screen.blit(self.font.render("SELECCIONA UN TILE (F=Fila, C=Columna)", True, (255,255,255)), (pos_x, pos_y - 50))
            self.screen.blit(self.font.render("Click fuera para cerrar", True, (150,150,150)), (pos_x, pos_y + disp_h + 10))

    def handle_editor_click(self, event):
        mx, my = event.pos
        if event.button == 1:
            if mx < 120 and my < TOPBAR_HEIGHT:
                self.mode = "file_menu"
                self.refresh_file_list()
                return

            if self.show_dropdown:
                self.handle_picker_click(event)
                return

            if mx < SIDEBAR_WIDTH and my > TOPBAR_HEIGHT:
                rel_y = my - (TOPBAR_HEIGHT + 10)
                if 0 <= rel_y <= 60:
                    self.current_tile = None
                    return
                
                scroll_area_start = 70
                if rel_y < scroll_area_start: return
                scrolled_y = rel_y - scroll_area_start + self.sidebar_scroll_offset
                
                m_start = 35 
                for m in self.palette_monsters:
                    if m_start <= scrolled_y <= m_start + 50:
                        self.current_tile = m['char']
                        return
                    m_start += 65
                
                o_start = m_start + 45
                for o in self.palette_objects:
                    if o_start <= scrolled_y <= o_start + 50:
                        self.current_tile = o['char']
                        return
                    o_start += 65
                
                t_start = o_start + 45
                
                if t_start <= scrolled_y <= t_start + 50:
                    self.current_tile = '#'
                    return
                t_start += 65
                
                if t_start <= scrolled_y <= t_start + 60:
                    self.show_dropdown = True
                    return
                return

            if mx > SIDEBAR_WIDTH and my > TOPBAR_HEIGHT:
                self.paint_tile(event.pos)

        elif event.button == 3:
             if mx > SIDEBAR_WIDTH and my > TOPBAR_HEIGHT:
                self.delete_tile(event.pos)

    def handle_picker_click(self, event):
        if event.button == 1:
            if self.tile_image:
                scale = 0.4
                img_w = self.tile_image.get_width()
                img_h = self.tile_image.get_height()
                disp_w = int(img_w * scale)
                disp_h = int(img_h * scale)
                pos_x = (EDITOR_WIDTH - disp_w) // 2
                pos_y = (EDITOR_HEIGHT - disp_h) // 2
                
                rel_x = event.pos[0] - pos_x
                rel_y = event.pos[1] - pos_y
                
                if 0 <= rel_x <= disp_w and 0 <= rel_y <= disp_h:
                    c = int(rel_x / (512 * scale))
                    r = int(rel_y / (512 * scale))
                    
                    self.assign_new_tile(r, c)
                    self.show_dropdown = False 
                else:
                    self.show_dropdown = False 

    def handle_file_menu_click(self, event):
        mx, my = event.pos
        if event.button == 1:
            cx, cy = EDITOR_WIDTH//2, EDITOR_HEIGHT//2
            w, h = 600, 500
            panel_x, panel_y = cx - w//2, cy - h//2
            
            if panel_x+20 <= mx <= panel_x+w-20 and panel_y+60 <= my <= panel_y+110:
                self.typing_new_file = True
                self.new_file_name = ""
                return
            
            save_btn_rect = pygame.Rect(panel_x+20, panel_y+120, w-40, 50)
            if save_btn_rect.collidepoint(mx, my):
                self.save_level(self.current_file)
                self.mode = "editor"
                return

            list_y = panel_y + 220
            for f in self.available_levels:
                rect_file = pygame.Rect(panel_x+20, list_y, w-40, 40)
                if rect_file.collidepoint(mx, my):
                    self.load_level(f"levels/{f}")
                    self.mode = "editor"
                    return
                list_y += 45
            
            if not (panel_x <= mx <= panel_x+w and panel_y <= my <= panel_y+h):
                self.mode = "editor"

    def update_level_order(self, filename):
        try:
            level_path = f"levels/{filename}" if not filename.startswith("levels/") else filename
            order = []
            if os.path.exists("level_order.json"):
                with open("level_order.json", "r") as f:
                    order = json.load(f)
            
            if level_path not in order:
                order.append(level_path)
                with open("level_order.json", "w") as f:
                    json.dump(order, f, indent=4)
        except Exception:
            pass

    def load_level(self, filename):
        self.grid = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    for r, line in enumerate(f.readlines()):
                        for c, char in enumerate(line.strip('\n')):
                            if char != ' ': self.grid[(c, r)] = char
                self.current_file = filename
            except: pass

    def save_level(self, filename):
        if not self.grid: return
        try:
            os.makedirs("levels", exist_ok=True)
            max_c = max((k[0] for k in self.grid), default=0)
            max_r = max((k[1] for k in self.grid), default=0)
            with open(filename, 'w') as f:
                for r in range(max_r + 1):
                    line = "".join(self.grid.get((c, r), ' ') for c in range(max_c + 1))
                    f.write(line.rstrip() + '\n')
            self.update_level_order(filename)
        except: pass

    def refresh_file_list(self):
        self.available_levels = [f for f in os.listdir("levels") if f.endswith(".txt")] if os.path.exists("levels") else []

    def handle_continuous_input(self):
        if self.typing_new_file: return
        keys = pygame.key.get_pressed()
        if self.mode == "editor":
            if keys[pygame.K_RIGHT]: self.scroll_x += SCROLL_SPEED
            if keys[pygame.K_LEFT]: self.scroll_x -= SCROLL_SPEED
            if keys[pygame.K_DOWN]: self.scroll_y += SCROLL_SPEED
            if keys[pygame.K_UP]: self.scroll_y -= SCROLL_SPEED
            
            if pygame.mouse.get_pressed()[0]:
                if pygame.mouse.get_pos()[0] > SIDEBAR_WIDTH: self.paint_tile(pygame.mouse.get_pos())
            if pygame.mouse.get_pressed()[2]:
                if pygame.mouse.get_pos()[0] > SIDEBAR_WIDTH: self.delete_tile(pygame.mouse.get_pos())

    def paint_tile(self, pos):
        c = int((pos[0] + self.scroll_x) // TILE_SIZE)
        r = int((pos[1] + self.scroll_y) // TILE_SIZE)
        if self.current_tile: self.grid[(c, r)] = self.current_tile
        elif (c,r) in self.grid: del self.grid[(c,r)]

    def delete_tile(self, pos):
        c = int((pos[0] + self.scroll_x) // TILE_SIZE)
        r = int((pos[1] + self.scroll_y) // TILE_SIZE)
        if (c,r) in self.grid: del self.grid[(c,r)]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.mode == "editor": self.handle_editor_click(event)
            elif self.mode == "picker": self.handle_picker_click(event)
            elif self.mode == "file_menu": self.handle_file_menu_click(event)
        elif event.type == pygame.MOUSEWHEEL:
            if self.show_dropdown: pass
            elif pygame.mouse.get_pos()[0] < SIDEBAR_WIDTH:
                self.sidebar_scroll_offset -= event.y * 30
                self.sidebar_scroll_offset = max(0, self.sidebar_scroll_offset)
        elif event.type == pygame.KEYDOWN:
            if self.typing_new_file:
                if event.key == pygame.K_RETURN: 
                    if self.new_file_name: self.current_file = f"levels/{self.new_file_name}.txt"; self.grid={}; self.save_level(self.current_file); self.mode="editor"; self.typing_new_file=False
                elif event.key == pygame.K_BACKSPACE: self.new_file_name = self.new_file_name[:-1]
                elif event.key == pygame.K_ESCAPE: self.typing_new_file = False
                else: self.new_file_name += event.unicode
                return
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL: self.save_level(self.current_file)
            elif event.key == pygame.K_ESCAPE: 
                if self.mode != "editor": self.mode = "editor"

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.VIDEORESIZE: self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.handle_event(event)
            self.handle_continuous_input()
            self.screen.fill((20, 20, 20))
            if self.mode == "editor": 
                self.draw_grid()
                self.draw_ui()
                if self.show_dropdown: self.draw_picker()
            elif self.mode == "picker": self.draw_picker()
            elif self.mode == "file_menu": self.draw_file_menu()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    LevelEditor().run()
    pygame.quit()
    sys.exit()