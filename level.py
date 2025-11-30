import pygame
import random
import json
import os
from config import TILE_SIZE, WIDTH, HEIGHT

class Level:
    def __init__(self, level_file):
        self.platforms = []
        self.platform_grid = {}
        self.goal = None
        self.boss = None
        self.player_spawn = (100, 100)
        
        self.monsters = []
        self.monster_spawns = []
        self.dead_monsters_count = 0
        self.spawn_cooldown = 0
        
        self.load_background_layers()
        self.load_tileset()
        self.load_decorations()
        
        self.load_from_file(level_file)
        self.build_autotiles()
        self.place_decorations()
    
    def load_background_layers(self):
        self.bg_decor_original = None
        self.hills_original = None
        
        try:
            extensiones = ['.png', '.jpg']
            
            for ext in extensiones:
                if os.path.exists(f"assets/images/tiles/Mossy/Mossy - Background Decoration{ext}"):
                    self.bg_decor_original = pygame.image.load(f"assets/images/tiles/Mossy/Mossy - Background Decoration{ext}")
                    break
            
            for ext in extensiones:
                if os.path.exists(f"assets/images/tiles/Mossy/Mossy - MossyHills{ext}"):
                    self.hills_original = pygame.image.load(f"assets/images/tiles/Mossy/Mossy - MossyHills{ext}")
                    break

            self.handle_resize(WIDTH, HEIGHT)
            
        except Exception:
            self.bg_decor_original = None
            self.handle_resize(WIDTH, HEIGHT)

    def handle_resize(self, new_width, new_height):
        if self.bg_decor_original:
            self.background = pygame.transform.scale(self.bg_decor_original, (new_width, new_height))
            if self.hills_original:
                hills_scaled = pygame.transform.scale(self.hills_original, (new_width, new_height // 2))
                self.background.blit(hills_scaled, (0, new_height // 2))
        else:
            self.background = pygame.Surface((new_width, new_height))
            for y in range(new_height):
                progress = y / new_height
                r = int(10 + progress * 30)
                g = int(20 + progress * 60)
                b = int(25 + progress * 40)
                pygame.draw.line(self.background, (r, g, b), (0, y), (new_width, y))
    
    def load_tileset(self):
        try:
            extensiones = ['.png', '.jpg']
            tileset = None
            
            for ext in extensiones:
                try:
                    tileset = pygame.image.load(f"assets/images/tiles/Mossy/Mossy - TileSet{ext}")
                    break
                except:
                    continue
            
            if not tileset:
                raise Exception()
            
            tile_size = 512
            
            self.tile_images = {
                'center': self.extract_tile(tileset, 1, 1, tile_size),
                'top': self.extract_tile(tileset, 0, 1, tile_size),
                'bottom': self.extract_tile(tileset, 2, 1, tile_size),
                'left': self.extract_tile(tileset, 1, 0, tile_size),
                'right': self.extract_tile(tileset, 1, 2, tile_size),
                'top_left': self.extract_tile(tileset, 0, 0, tile_size),
                'top_right': self.extract_tile(tileset, 0, 2, tile_size),
                'bottom_left': self.extract_tile(tileset, 2, 0, tile_size),
                'bottom_right': self.extract_tile(tileset, 2, 2, tile_size),
                'stone': self.extract_tile(tileset, 3, 1, tile_size)
            }
            
            self.custom_tiles = {}
            if os.path.exists("tile_map.json"):
                try:
                    with open("tile_map.json", "r") as f:
                        self.custom_tiles = json.load(f)
                        
                        for char, data in self.custom_tiles.items():
                            row = data.get('row', 0)
                            col = data.get('col', 0)
                            self.tile_images[char] = self.extract_tile(tileset, row, col, tile_size)
                except Exception:
                    pass
            
        except Exception:
            self.tile_images = None
    
    def load_decorations(self):
        try:
            extensiones = ['.png', '.jpg']
            
            hanging_plants = None
            for ext in extensiones:
                try:
                    hanging_plants = pygame.image.load(f"assets/images/tiles/Mossy/Mossy - Hanging Plants{ext}")
                    break
                except:
                    continue
            
            decorations = None
            for ext in extensiones:
                try:
                    decorations = pygame.image.load(f"assets/images/tiles/Mossy/Mossy - Decorations&Hazards{ext}")
                    break
                except:
                    continue
            
            self.decorations = []
            
            if hanging_plants:
                plant_size = 256
                for i in range(min(6, hanging_plants.get_width() // plant_size)):
                    try:
                        plant = hanging_plants.subsurface(pygame.Rect(i * plant_size, 0, plant_size, plant_size))
                        plant_scaled = pygame.transform.scale(plant, (48, 48))
                        self.decorations.append(plant_scaled)
                    except:
                        pass
            
            if decorations:
                dec_size = 256
                for i in range(min(4, decorations.get_width() // dec_size)):
                    try:
                        dec = decorations.subsurface(pygame.Rect(i * dec_size, 0, dec_size, dec_size))
                        dec_scaled = pygame.transform.scale(dec, (32, 32))
                        self.decorations.append(dec_scaled)
                    except:
                        pass
            
        except Exception:
            self.decorations = []
    
    def extract_tile(self, sheet, row, col, tile_size):
        x = col * tile_size
        y = row * tile_size
        
        tile = sheet.subsurface(pygame.Rect(x, y, tile_size, tile_size))
        return pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                for row, line in enumerate(lines):
                    for col, char in enumerate(line):
                        x = col * TILE_SIZE
                        y = row * TILE_SIZE
                        
                        if char == '#':
                            self.platform_grid[(col, row)] = True
                            platform = {
                                'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                                'grid_pos': (col, row),
                                'tile_type': 'center',
                                'is_manual': False
                            }
                            self.platforms.append(platform)
                        elif char == 'S':
                            self.platform_grid[(col, row)] = True
                            platform = {
                                'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                                'grid_pos': (col, row),
                                'tile_type': 'stone',
                                'is_manual': True
                            }
                            self.platforms.append(platform)
                        elif char == 'G':
                            self.goal = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                        elif char == 'B':
                            from boss import Boss
                            self.boss = Boss(x, y, boss_type="gnu")
                        elif char == 'U':
                            from undead_executioner import UndeadExecutioner
                            self.boss = UndeadExecutioner(x, y)
                        elif char == 'M':
                            self.monster_spawns.append((x, y))
                        elif char == 'E':
                            from monster import Monster
                            self.monsters.append(Monster(x, y, "flying_eye"))
                        elif char == 'O':
                            from monster import Monster
                            self.monsters.append(Monster(x, y, "goblin"))
                        elif char == 'K':
                            from monster import Monster
                            self.monsters.append(Monster(x, y, "skeleton"))
                        elif char == 'H':
                            from monster import Monster
                            self.monsters.append(Monster(x, y, "mushroom"))
                        elif char == 'P':
                            self.player_spawn = (x, y)
                        elif char in self.custom_tiles:
                            self.platform_grid[(col, row)] = True
                            platform = {
                                'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                                'grid_pos': (col, row),
                                'tile_type': char,
                                'is_manual': True
                            }
                            self.platforms.append(platform)
        except FileNotFoundError:
            raise
    
    def build_autotiles(self):
        for platform in self.platforms:
            if platform.get('is_manual'):
                continue
                
            col, row = platform['grid_pos']
            
            has_top = (col, row - 1) in self.platform_grid
            has_bottom = (col, row + 1) in self.platform_grid
            has_left = (col - 1, row) in self.platform_grid
            has_right = (col + 1, row) in self.platform_grid
            
            if not has_top and not has_left:
                platform['tile_type'] = 'top_left'
            elif not has_top and not has_right:
                platform['tile_type'] = 'top_right'
            elif not has_bottom and not has_left:
                platform['tile_type'] = 'bottom_left'
            elif not has_bottom and not has_right:
                platform['tile_type'] = 'bottom_right'
            elif not has_top:
                platform['tile_type'] = 'top'
            elif not has_bottom:
                platform['tile_type'] = 'bottom'
            elif not has_left:
                platform['tile_type'] = 'left'
            elif not has_right:
                platform['tile_type'] = 'right'
            else:
                platform['tile_type'] = 'center'
    
    def place_decorations(self):
        self.placed_decorations = []
        
        if not self.decorations:
            return
        
        for platform in self.platforms:
            col, row = platform['grid_pos']
            
            if (col, row + 1) not in self.platform_grid:
                if random.random() < 0.3:
                    x = platform['rect'].x + random.randint(0, TILE_SIZE - 48)
                    y = platform['rect'].bottom - 10
                    decoration = random.choice(self.decorations)
                    self.placed_decorations.append({
                        'image': decoration,
                        'pos': (x, y),
                        'layer': 'front'
                    })
    
    def get_dimensions(self):
        if not self.platforms:
            return (WIDTH, HEIGHT)
        
        max_x = max(p['rect'].right if isinstance(p, dict) else p.right 
                    for p in self.platforms)
        max_y = max(p['rect'].bottom if isinstance(p, dict) else p.bottom 
                    for p in self.platforms)
        
        level_width = max(max_x + 200, WIDTH)
        level_height = max(max_y + 200, HEIGHT)
        
        return (level_width, level_height)
    
    def check_section_complete(self, player):
        if self.goal and player.rect.colliderect(self.goal):
            return True
        return False
    
    def spawn_monsters(self):
        from monster import Monster
        
        if not self.monster_spawns:
            return
        
        monster_types = ["flying_eye", "goblin", "skeleton", "goblin"]
        
        monsters_to_spawn = 25
        for i in range(monsters_to_spawn):
            spawn_pos = self.monster_spawns[i % len(self.monster_spawns)]
            monster_type = random.choice(monster_types)
            monster = Monster(spawn_pos[0], spawn_pos[1], monster_type)
            self.monsters.append(monster)
    
    def spawn_new_monsters(self, count=2):
        from monster import Monster
        
        if not self.monster_spawns:
            return
        
        monster_types = ["flying_eye", "goblin", "skeleton", "goblin"]
        
        for _ in range(count):
            spawn_pos = random.choice(self.monster_spawns)
            monster_type = random.choice(monster_types)
            monster = Monster(spawn_pos[0], spawn_pos[1], monster_type)
            self.monsters.append(monster)
    
    def update(self, player, game=None):
        if self.boss:
            self.boss.update()
            
            if self.boss.check_collision_with_player(player):
                return "game_over"
            
            if self.boss.check_hit_player(player):
                player.take_damage()
                return "hit"
        
        if self.monsters and game:
            for monster in self.monsters[:]:
                monster.update_ai(player, game)
                monster.update_movement(self.platforms)
                
                if monster.check_collision_with_player(player):
                    return "game_over"
                
                if not monster.alive:
                    self.monsters.remove(monster)
                    self.dead_monsters_count += 1
                    self.spawn_cooldown = 180
            
            if self.spawn_cooldown > 0:
                self.spawn_cooldown -= 1
                if self.spawn_cooldown == 0:
                    self.spawn_new_monsters(2)
        
        return None
    
    def draw_background(self, surface):
        surface.blit(self.background, (0, 0))
    
    def draw_with_camera(self, surface, camera):
        for dec in self.placed_decorations:
            if dec.get('layer') == 'back':
                pos = camera.apply_pos(dec['pos'][0], dec['pos'][1])
                surface.blit(dec['image'], pos)
        
        for platform in self.platforms:
            rect = platform['rect']
            screen_rect = camera.apply(rect)
            
            tile_type = platform.get('tile_type', 'center')
            if self.tile_images and tile_type in self.tile_images:
                image = self.tile_images[tile_type]
                surface.blit(image, screen_rect)
            else:
                pygame.draw.rect(surface, (0, 0, 0), screen_rect)
                pygame.draw.rect(surface, (50, 50, 50), screen_rect, 1)

        if self.goal:
            goal_rect = camera.apply(self.goal)
            
            pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500.0
            glow_size = int(10 + pulse * 10)
            
            glow_surf = pygame.Surface((goal_rect.width + glow_size * 2, 
                                       goal_rect.height + glow_size * 2))
            glow_surf.set_alpha(int(80 + pulse * 80))
            glow_surf.fill((100, 255, 150))
            surface.blit(glow_surf, (goal_rect.x - glow_size, goal_rect.y - glow_size))
            
            pygame.draw.rect(surface, (50, 255, 150), goal_rect)
            pygame.draw.rect(surface, (0, 200, 100), goal_rect, 5)
            
            font = pygame.font.Font(None, 35)
            text = font.render("GOAL", True, (0, 0, 0))
            text_rect = text.get_rect(center=(goal_rect.centerx + 2, goal_rect.centery + 2))
            surface.blit(text, text_rect)
            
            text = font.render("GOAL", True, (255, 255, 255))
            text_rect = text.get_rect(center=goal_rect.center)
            surface.blit(text, text_rect)
        
        if self.boss:
            self.boss.draw_with_camera(surface, camera)
        
        for monster in self.monsters:
            if monster.alive:
                monster.draw_with_camera(surface, camera)
        
        for dec in self.placed_decorations:
            if dec.get('layer') == 'front':
                pos = camera.apply_pos(dec['pos'][0], dec['pos'][1])
                surface.blit(dec['image'], pos)
    
    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        
        for dec in self.placed_decorations:
            if dec.get('layer') == 'back':
                surface.blit(dec['image'], dec['pos'])
        
        for platform in self.platforms:
            rect = platform['rect']
            pygame.draw.rect(surface, (0, 0, 0), rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)
        
        if self.goal:
            pygame.draw.rect(surface, (50, 255, 150), self.goal)
            pygame.draw.rect(surface, (0, 200, 100), self.goal, 4)
            
            font = pygame.font.Font(None, 30)
            text = font.render("GOAL", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.goal.center)
            surface.blit(text, text_rect)
        
        if self.boss:
            self.boss.draw(surface)
        
        for dec in self.placed_decorations:
            if dec.get('layer') == 'front':
                surface.blit(dec['image'], dec['pos'])