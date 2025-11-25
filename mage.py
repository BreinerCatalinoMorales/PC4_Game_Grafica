# mage.py
from player import Player
from projectile import Fireball

class Mage(Player):
    def __init__(self, x, y):
        super().__init__(x, y, "mage", "assets/images/player/mage")
        self.cast_cooldown = 0
        self.pending_projectile = None  # ← NUEVO: guardar proyectil pendiente
        self.load_sprites()
    
    def load_sprites(self):
        """Capas específicas del mago"""
        layers = [
            "BODY_male.png",
            "LEGS_robe_skirt.png",
            "TORSO_robe_shirt_brown.png",
            "HEAD_robe_hood.png",
            "BELT_rope.png",
        ]
        
        self.animations = {
            "walk": self._combine_layers(layers, "walkcycle"),
            "spell": self._combine_layers(layers, "spellcast"),
            "hurt": self._combine_layers(layers, "hurt")
        }
        
        self.frame_counts = {
            "walk": self.animations["walk"].get_width() // 64,
            "spell": self.animations["spell"].get_width() // 64,
            "hurt": self.animations["hurt"].get_width() // 64
        }
        
        print(f"✓ Mago cargado - Frames: {self.frame_counts}")
    
    def update(self, keys, platforms):
        """Actualiza mago"""
        # Reducir cooldown
        if self.cast_cooldown > 0:
            self.cast_cooldown -= 1
        
        # Llamar update del padre
        super().update(keys, platforms)
        
        # Crear proyectil en el frame 3-4 de la animación spell
        if self.is_casting and self.current_frame == 3 and self.pending_projectile:
            # Devolver el proyectil para que main.py lo agregue
            proj = self.pending_projectile
            self.pending_projectile = None
            return proj
        
        return None
    
    def use_ability(self):
        """Iniciar animación de lanzar bola de fuego"""
        # Solo si no está en cooldown y no está ya lanzando
        if self.cast_cooldown <= 0 and not self.is_casting:
            self.is_casting = True
            self.current_animation = "spell"
            self.current_frame = 0
            self.frame_counter = 0
            self.cast_cooldown = 30  # 0.5 segundos
            
            # Preparar proyectil (se creará en el frame 3)
            spawn_x = self.rect.centerx
            spawn_y = self.rect.centery
            self.pending_projectile = Fireball(spawn_x, spawn_y, self.direction)
            
            print("⚡ Iniciando animación de spell...")
            return True  # Indica que comenzó a lanzar
        
        return False
    
    def on_spell_complete(self):
        """Cuando termina la animación de spell"""
        print("✨ Animación de spell completada")
        self.pending_projectile = None  # Limpiar si quedó algo
