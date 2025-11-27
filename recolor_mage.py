"""
Script para generar versiones recoloreadas del personaje Mage.
Genera tres versiones: Negro, Azul, y Rojo.
"""

from PIL import Image
import os
import shutil

def recolor_to_black(image):
    """Convierte la imagen a escala de grises (negro)"""
    # Convertir a RGBA si no lo está
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Crear copia
    result = image.copy()
    pixels = result.load()
    
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            if a > 0:  # Solo procesar píxeles no transparentes
                # Escala de grises
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                pixels[x, y] = (gray, gray, gray, a)
    
    return result

def recolor_to_blue(image):
    """Convierte la imagen a tonos azules"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    result = image.copy()
    pixels = result.load()
    
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # Mantener luminosidad pero en canal azul
                luminosity = int(0.299 * r + 0.587 * g + 0.114 * b)
                pixels[x, y] = (0, int(luminosity * 0.3), luminosity, a)
    
    return result

def recolor_to_red(image):
    """Convierte la imagen a tonos rojos"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    result = image.copy()
    pixels = result.load()
    
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # Mantener luminosidad pero en canal rojo
                luminosity = int(0.299 * r + 0.587 * g + 0.114 * b)
                pixels[x, y] = (luminosity, int(luminosity * 0.2), 0, a)
    
    return result

def recolor_to_background(image):
    """Convierte la imagen a los colores exactos del fondo del juego"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    result = image.copy()
    pixels = result.load()
    
    # Colores del gradiente del fondo del juego
    # Top: RGB(10, 20, 25)
    # Bottom: RGB(40, 80, 65)
    top_color = (10, 20, 25)
    bottom_color = (40, 80, 65)
    
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # Calcular luminosidad
                luminosity = int(0.299 * r + 0.587 * g + 0.114 * b)
                norm_lum = luminosity / 255.0
                
                # Interpolar entre top y bottom basado en la posición Y
                progress = y / result.size[1]
                
                # Color base interpolado
                base_r = int(top_color[0] + (bottom_color[0] - top_color[0]) * progress)
                base_g = int(top_color[1] + (bottom_color[1] - top_color[1]) * progress)
                base_b = int(top_color[2] + (bottom_color[2] - top_color[2]) * progress)
                
                # Aplicar luminosidad
                final_r = int(base_r + (255 - base_r) * norm_lum * 0.5)
                final_g = int(base_g + (255 - base_g) * norm_lum * 0.5)
                final_b = int(base_b + (255 - base_b) * norm_lum * 0.5)
                
                pixels[x, y] = (final_r, final_g, final_b, a)
    
    return result

def process_mage_folder(source_dir, target_dir, recolor_func):
    """
    Procesa todas las imágenes del Mage y las recolorea.
    
    Args:
        source_dir: Directorio fuente (ej: "Mage")
        target_dir: Directorio destino (ej: "Mage_Black")
        recolor_func: Función de recoloreo a aplicar
    """
    # Crear directorio destino si no existe
    if os.path.exists(target_dir):
        print(f"⚠️  {target_dir} ya existe, será sobrescrito...")
        shutil.rmtree(target_dir)
    
    # Copiar estructura de carpetas
    shutil.copytree(source_dir, target_dir)
    
    print(f"✓ Procesando {target_dir}...")
    
    # Recorrer todas las carpetas (Walk, Spell, Hurt)
    total_images = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                
                # Cargar imagen
                img = Image.open(file_path)
                
                # Aplicar recoloreo
                recolored = recolor_func(img)
                
                # Guardar
                recolored.save(file_path)
                total_images += 1
    
    print(f"  ✓ {total_images} imágenes procesadas")

def main():
    source_dir = "assets/images/player/Mage"
    
    if not os.path.exists(source_dir):
        print(f"❌ Error: No se encontró la carpeta '{source_dir}'")
        return
    
    print("🎨 Generando versiones recoloreadas del Mage...")
    print()
    
    # Generar versión negra
    process_mage_folder(source_dir, "assets/images/player/Mage_Black", recolor_to_black)
    
    # Generar versión azul
    process_mage_folder(source_dir, "assets/images/player/Mage_Blue", recolor_to_blue)
    
    # Generar versión roja
    process_mage_folder(source_dir, "assets/images/player/Mage_Red", recolor_to_red)
    
    # Generar versión del color del fondo
    process_mage_folder(source_dir, "assets/images/player/Mage_Background", recolor_to_background)
    
    print()
    print("✅ ¡Completado!")
    print("   Se crearon las carpetas en assets/images/player/:")
    print("   - Mage_Black (negro)")
    print("   - Mage_Blue (azul)")
    print("   - Mage_Red (rojo)")
    print("   - Mage_Background (color del fondo del juego)")

if __name__ == "__main__":
    main()
