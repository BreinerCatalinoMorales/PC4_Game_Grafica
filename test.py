# test.py - CON ROPA Y HURT
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Mago - Animaciones con Ropa")
clock = pygame.time.Clock()

# Función para combinar capas
def combine_layers(layer_files, animation_folder):
    """Carga y combina múltiples capas de sprites"""
    if not layer_files:
        return None
    
    # Cargar primera capa para obtener dimensiones
    first_layer = pygame.image.load(f"assets/images/player/mage/{animation_folder}/{layer_files[0]}")
    
    # Crear surface transparente del mismo tamaño
    combined = pygame.Surface(first_layer.get_size(), pygame.SRCALPHA)
    
    # Dibujar cada capa en orden (de atrás hacia adelante)
    for layer_file in layer_files:
        try:
            layer = pygame.image.load(f"assets/images/player/mage/{animation_folder}/{layer_file}")
            combined.blit(layer, (0, 0))
        except:
            print(f"  ⚠ No se encontró: {layer_file}")
    
    return combined

print("Cargando sprites del mago...")

# Definir las capas para un mago (en orden: fondo -> frente)
# Orden correcto según README: BEHIND, BODY, FEET, LEGS, TORSO, BELT, HEAD, HANDS, WEAPON
# Mago más elaborado
mage_layers = [
    "BODY_male.png",
    "LEGS_robe_skirt.png",           # Falda de túnica
    "TORSO_robe_shirt_brown.png",    # Túnica marrón
    "HEAD_robe_hood.png",            # Capucha
    "BELT_rope.png",                 # Cinturón de cuerda
]


# Intentar también con estas variantes si las tienes:
# "LEGS_robe_skirt.png"
# "TORSO_chain_armor_jacket_purple.png"

try:
    # Combinar capas para cada animación
    print("Combinando walkcycle...")
    walk_combined = combine_layers(mage_layers, "walkcycle")
    
    print("Combinando spellcast...")
    spell_combined = combine_layers(mage_layers, "spellcast")
    
    print("Combinando hurt...")
    hurt_combined = combine_layers(mage_layers, "hurt")
    
    print("✓ Sprites cargados correctamente")
    print(f"  Walk size: {walk_combined.get_size()}")
    print(f"  Spell size: {spell_combined.get_size()}")
    print(f"  Hurt size: {hurt_combined.get_size()}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit()

frame_width = 64
frame_height = 64
current_frame = 0
frame_counter = 0
animation_speed = 8

current_animation = "walk"
current_sheet = walk_combined

direction_map = {
    "up": 0,
    "left": 1,
    "down": 2,
    "right": 3
}

current_direction = "left"
direction = direction_map["left"]

# Detectar automáticamente el número de frames según el ancho del sheet
def get_frame_count(sprite_sheet):
    """Calcula cuántos frames tiene un sprite sheet"""
    sheet_width = sprite_sheet.get_width()
    return sheet_width // frame_width

# Información de frames por animación (auto-detectado)
animation_info = {
    "walk": {
        "frames": get_frame_count(walk_combined), 
        "sheet": walk_combined
    },
    "spell": {
        "frames": get_frame_count(spell_combined), 
        "sheet": spell_combined
    },
    "hurt": {
        "frames": get_frame_count(hurt_combined), 
        "sheet": hurt_combined
    }
}

# Imprimir info para debug
print(f"\nFrames detectados:")
print(f"  Walk: {animation_info['walk']['frames']} frames")
print(f"  Spell: {animation_info['spell']['frames']} frames")
print(f"  Hurt: {animation_info['hurt']['frames']} frames")

max_frames = animation_info[current_animation]["frames"]


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Cambiar animaciones con teclas
            if event.key == pygame.K_SPACE:
                if current_animation == "walk":
                    current_animation = "spell"
                    print("Animación: SPELLCAST")
                elif current_animation == "spell":
                    current_animation = "hurt"
                    print("Animación: HURT")
                else:
                    current_animation = "walk"
                    print("Animación: WALK")
                
                current_sheet = animation_info[current_animation]["sheet"]
                max_frames = animation_info[current_animation]["frames"]
                current_frame = 0
            
            # Cambiar dirección con flechas
            elif event.key == pygame.K_DOWN:
                direction = direction_map["down"]
                current_direction = "down"
            elif event.key == pygame.K_LEFT:
                direction = direction_map["left"]
                current_direction = "left"
            elif event.key == pygame.K_RIGHT:
                direction = direction_map["right"]
                current_direction = "right"
            elif event.key == pygame.K_UP:
                direction = direction_map["up"]
                current_direction = "up"
    
    frame_counter += 1
    if frame_counter >= animation_speed:
        current_frame = (current_frame + 1) % max_frames
        frame_counter = 0
    
    # Detectar cuántas direcciones tiene el sprite actual
    num_directions = current_sheet.get_height() // frame_height
    
    # Si solo tiene 1 dirección, forzar a 0
    if num_directions == 1:
        actual_direction = 0
    else:
        actual_direction = direction
    
    frame_x = current_frame * frame_width
    frame_y = actual_direction * frame_height

    
    sheet_width = current_sheet.get_width()
    sheet_height = current_sheet.get_height()
    
    if frame_x + frame_width <= sheet_width and frame_y + frame_height <= sheet_height:
        frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
        frame = current_sheet.subsurface(frame_rect)
        
        screen.fill((50, 50, 50))
        scaled_frame = pygame.transform.scale(frame, (128, 128))
        screen.blit(scaled_frame, (800//2 - 64, 600//2 - 64))
    else:
        screen.fill((50, 50, 50))
        font = pygame.font.Font(None, 40)
        error_text = font.render("FRAME FUERA DE RANGO", True, (255, 0, 0))
        screen.blit(error_text, (200, 300))
    
    font = pygame.font.Font(None, 30)
    text1 = font.render(f"Animacion: {current_animation.upper()}", True, (255, 255, 255))
    text2 = font.render(f"Frame: {current_frame + 1}/{max_frames}", True, (255, 255, 255))
    text3 = font.render(f"Direccion: {current_direction.upper()}", True, (255, 255, 255))
    text4 = font.render("ESPACIO=cambiar anim | Flechas=direccion", True, (200, 200, 200))
    
    screen.blit(text1, (20, 20))
    screen.blit(text2, (20, 50))
    screen.blit(text3, (20, 80))
    screen.blit(text4, (20, 550))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Test finalizado")
