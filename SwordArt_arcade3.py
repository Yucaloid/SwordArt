import random
import arcade
import timeit
import math
import os
from typing import List, Tuple, Optional

###################################### 
############### CONSTANTS ############
######################################

# Sprites and Scaling
WALL_SPRITE_SCALING = 0.5
PLAYER_SPRITE_SCALING = 0.8 
ENEMY_SPRITE_SCALING = 1.5 

WALL_SPRITE_SIZE = int(128 * WALL_SPRITE_SCALING)

# Grid and Map configuration
GRID_WIDTH = 100
GRID_HEIGHT = 100
AREA_WIDTH = GRID_WIDTH * WALL_SPRITE_SIZE
AREA_HEIGHT = GRID_HEIGHT * WALL_SPRITE_SIZE

# Player mechanics
# --- FIX: Swapped these values to fix inverted directions ---
RIGHT_FACING = 1
LEFT_FACING = 0

MOVEMENT_SPEED = 3
# We don't need updates per frame anymore for the simplified animation
# but we keep constants for consistency if needed later.

# Map Generation parameters
MAX_SPLIT_ITERATIONS = 15

# Window configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "SwordArt Final"

###################################### 
############### CLASSES ##############
######################################

def load_texture_pair(filename: str) -> List[arcade.Texture]:
    """
    Loads a texture and creates a horizontally flipped pair.
    Returns: [Original, Flipped]
    """
    try:
        texture = arcade.load_texture(filename)
        return [texture, texture.flip_left_right()]
    except FileNotFoundError:
        print(f"[ERROR] Missing Resource: {filename}")
        return []

class Enemy(arcade.Sprite):
    """
    Enemy class handling health, death animation and sounds.
    """
    def __init__(self, scale: float):
        super().__init__(scale=scale)
        self.health = 100
        self.curtime = 0
        self.is_dying = False
        
        # Load Textures
        try:
            self.texture = arcade.load_texture("Imagenes/demon.png")
            self.death_textures = [
                arcade.load_texture("Imagenes/demon_die_1.png"),
                arcade.load_texture("Imagenes/demon_die_2.png")
            ]
        except Exception:
             self.texture = arcade.make_soft_circle_texture(30, arcade.color.RED)
             self.death_textures = [self.texture, self.texture]

        # Load Sounds
        try:
            self.sound_die = arcade.load_sound("sounds/demon_die.ogg")
        except FileNotFoundError:
            self.sound_die = None

    def update(self, delta_time: float = 1/60):
        """
        Updates enemy logic.
        """
        self.curtime += 1
        
        # Death Logic
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            if self.sound_die:
                self.sound_die.play()
            self.texture = self.death_textures[0] 
            
        if self.is_dying:
            if self.curtime % 10 == 0:
                self.texture = self.death_textures[1]
            if self.curtime % 30 == 0: 
                self.kill()

class PlayerSprite(arcade.Sprite):
    """
    Player class with simplified animation logic (no cycling).
    """
    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.scale = PLAYER_SPRITE_SCALING
        
        # Hitbox Setup
        self.points = [[-16, -32], [16, -32], [16, 16], [-16, 16]]

        # Load Main Texture (Single image approach to avoid flickering)
        # Using Sprites-11.png as the main side-view
        self.main_texture_pair = load_texture_pair("Imagenes/Sprites-11.png")
        
        # Fallback
        if not self.main_texture_pair:
             self.main_texture_pair = load_texture_pair("Imagenes/Sprites-19.png")

        # Set initial texture
        if self.main_texture_pair:
            self.texture = self.main_texture_pair[self.character_face_direction]

        # Sound Setup
        try:
            self.sound_attack = arcade.load_sound("sounds/knife_hit.ogg")
        except:
            self.sound_attack = None

        # Combat Stats
        self.is_alive = True
        self.knife_delay = 0
        self.knife_rate = 0
        self.curtime = 0
        self.eye_pos = "right"
        self.box_l = 0; self.box_r = 0; self.box_t = 0; self.box_b = 0

    def update_animation(self, delta_time: float = 1/60):
        """
        Simplified animation: Just flips the sprite based on direction.
        """
        if not self.main_texture_pair:
            return

        # 1. Detect Direction based on velocity
        # Using a threshold of 0.1 to avoid floating point jitter
        if self.change_x < -0.1:
            self.character_face_direction = LEFT_FACING
            self.eye_pos = "left"
        elif self.change_x > 0.1:
            self.character_face_direction = RIGHT_FACING
            self.eye_pos = "right"
        
        # 2. Apply Texture
        # This persists the last known direction even when stopped
        self.texture = self.main_texture_pair[self.character_face_direction]

    def stab(self):
        """
        Attack logic.
        """
        if self.is_alive:
            if self.curtime < self.knife_rate:
                return

            self.knife_delay = self.curtime
            self.knife_rate = self.curtime + 30
            
            if self.sound_attack:
                self.sound_attack.play()

            attack_range = 64
            # Update hitbox based on current facing direction
            if self.eye_pos == "right":
                self.box_l = self.center_x
                self.box_r = self.center_x + attack_range
            elif self.eye_pos == "left":
                self.box_l = self.center_x - attack_range
                self.box_r = self.center_x

            self.box_t = self.center_y + 32
            self.box_b = self.center_y - 32

class Room:
    """
    Helper class for Dungeon Generation.
    """
    def __init__(self, r: int, c: int, h: int, w: int):
        self.row = r
        self.col = c
        self.height = h
        self.width = w
        self.center_row = r + h // 2
        self.center_col = c + w // 2

class RLDungeonGenerator:
    """
    BSP Dungeon Generator.
    """
    def __init__(self, w: int, h: int):
        self.max_split = MAX_SPLIT_ITERATIONS
        self.width = w
        self.height = h
        self.leaves = []
        self.rooms = []
        self.dungeon = [['#' for _ in range(self.width)] for _ in range(self.height)]

    def random_split(self, min_row, min_col, max_row, max_col):
        seg_height = max_row - min_row
        seg_width = max_col - min_col

        if seg_height < self.max_split and seg_width < self.max_split:
            self.leaves.append((min_row, min_col, max_row, max_col))
        elif seg_height < self.max_split <= seg_width:
            self.split_on_vertical(min_row, min_col, max_row, max_col)
        elif seg_height >= self.max_split > seg_width:
            self.split_on_horizontal(min_row, min_col, max_row, max_col)
        else:
            if random.random() < 0.5:
                self.split_on_horizontal(min_row, min_col, max_row, max_col)
            else:
                self.split_on_vertical(min_row, min_col, max_row, max_col)

    def split_on_horizontal(self, min_row, min_col, max_row, max_col):
        split = (min_row + max_row) // 2 + random.choice((-2, -1, 0, 1, 2))
        split = max(min_row + 1, min(split, max_row - 1))
        self.random_split(min_row, min_col, split, max_col)
        self.random_split(split + 1, min_col, max_row, max_col)

    def split_on_vertical(self, min_row, min_col, max_row, max_col):
        split = (min_col + max_col) // 2 + random.choice((-2, -1, 0, 1, 2))
        split = max(min_col + 1, min(split, max_col - 1))
        self.random_split(min_row, min_col, max_row, split)
        self.random_split(min_row, split + 1, max_row, max_col)

    def carve_rooms(self):
        for leaf in self.leaves:
            if random.random() > 0.90: continue
            
            section_width = leaf[3] - leaf[1]
            section_height = leaf[2] - leaf[0]
            if section_width < 5 or section_height < 5: continue

            room_width = round(random.randrange(60, 100) / 100 * section_width)
            room_height = round(random.randrange(60, 100) / 100 * section_height)
            room_width = max(3, room_width)
            room_height = max(3, room_height)

            room_start_row = leaf[0] + random.randrange(max(1, section_height - room_height))
            room_start_col = leaf[1] + random.randrange(max(1, section_width - room_width))

            new_room = Room(room_start_row, room_start_col, room_height, room_width)
            self.rooms.append(new_room)
            
            for r in range(new_room.row, new_room.row + new_room.height):
                for c in range(new_room.col, new_room.col + new_room.width):
                    if 0 < r < self.height - 1 and 0 < c < self.width - 1:
                         self.dungeon[r][c] = '.'

    def create_h_tunnel(self, c1, c2, r):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            if 0 < r < self.height - 1 and 0 < c < self.width - 1:
                self.dungeon[r][c] = '.'
                self.dungeon[r+1][c] = '.' 

    def create_v_tunnel(self, r1, r2, c):
        for r in range(min(r1, r2), max(r1, r2) + 1):
            if 0 < r < self.height - 1 and 0 < c < self.width - 1:
                self.dungeon[r][c] = '.'
                self.dungeon[r][c+1] = '.'

    def connect_rooms(self):
        for i in range(len(self.rooms) - 1):
            room_a = self.rooms[i]
            room_b = self.rooms[i + 1]
            prev_r, prev_c = room_a.center_row, room_a.center_col
            curr_r, curr_c = room_b.center_row, room_b.center_col

            if random.choice([True, False]):
                self.create_h_tunnel(prev_c, curr_c, prev_r)
                self.create_v_tunnel(prev_r, curr_r, curr_c)
            else:
                self.create_v_tunnel(prev_r, curr_r, prev_c)
                self.create_h_tunnel(prev_c, curr_c, curr_r)

    def generate_map(self):
        self.random_split(1, 1, self.height - 1, self.width - 1)
        self.carve_rooms()
        self.connect_rooms()

class MyGame(arcade.Window):
    """
    Main Game Class.
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        self.camera_sprites = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()
        
        self.wall_list = None
        self.player_list = None
        self.enemy_list = None
        self.player_sprite = None
        self.physics_engine = None
        
        self.game_started = False
        self.health = 100
        self.menu_texture = None
        self.bgm = None

    def setup(self):
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        
        self.player_sprite = PlayerSprite()
        self.player_list.append(self.player_sprite)

        # Map Generation
        dg = RLDungeonGenerator(GRID_WIDTH, GRID_HEIGHT)
        dg.generate_map()

        # Walls
        for row in range(dg.height):
            for column in range(dg.width):
                if dg.dungeon[row][column] == '#':
                    wall = arcade.Sprite(":resources:images/tiles/brickTextureWhite.png", WALL_SPRITE_SCALING)
                    wall.center_x = column * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    self.wall_list.append(wall)

        # Player Spawn
        placed = False
        attempts = 0
        while not placed and attempts < 1000:
            r = random.randrange(1, GRID_HEIGHT-1)
            c = random.randrange(1, GRID_WIDTH-1)
            if dg.dungeon[r][c] == '.':
                self.player_sprite.center_x = c * WALL_SPRITE_SIZE
                self.player_sprite.center_y = r * WALL_SPRITE_SIZE
                placed = True
            attempts += 1

        # Enemy Spawn (75 large demons)
        if len(dg.rooms) > 0:
            for _ in range(75): 
                room = random.choice(dg.rooms)
                enemy = Enemy(scale=ENEMY_SPRITE_SCALING)
                
                spawn_r = random.randint(room.row, room.row + room.height - 1)
                spawn_c = random.randint(room.col, room.col + room.width - 1)
                
                enemy.center_x = spawn_c * WALL_SPRITE_SIZE
                enemy.center_y = spawn_r * WALL_SPRITE_SIZE
                
                self.enemy_list.append(enemy)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)
        
        # Audio and Menu
        try:
            self.menu_texture = arcade.load_texture("Imagenes/Menuf.png")
            self.bgm = arcade.load_sound("sounds/Piano.mp3")
            if self.bgm:
                self.bgm.play(volume=0.5, loop=True)
        except Exception as e:
            print(f"[WARNING] Asset Error: {e}")

    def on_draw(self):
        self.clear()
        
        self.camera_sprites.use()
        self.wall_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()

        self.camera_gui.use()
        
        # GUI
        arcade.draw_rect_filled(arcade.LBWH(50, WINDOW_HEIGHT - 40, 200, 20), arcade.color.RED)
        health_pct = max(0, self.health / 100)
        arcade.draw_rect_filled(arcade.LBWH(50, WINDOW_HEIGHT - 40, 200 * health_pct, 20), arcade.color.GREEN)
        
        arcade.draw_text(
            text=f"HP: {self.health}", 
            x=55, 
            y=WINDOW_HEIGHT - 38, 
            color=arcade.color.WHITE, 
            font_size=12
        )

        if not self.game_started:
            if self.menu_texture:
                arcade.draw_texture_rect(self.menu_texture, arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            else:
                 arcade.draw_text("PRESS ANY KEY TO START", x=WINDOW_WIDTH/2, y=WINDOW_HEIGHT/2, 
                                  color=arcade.color.WHITE, font_size=24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        self.game_started = True
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = MOVEMENT_SPEED
        
        if key == arcade.key.Z or key == arcade.key.X:
            self.player_sprite.stab()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        self.player_sprite.curtime += 1
        if not self.game_started:
            return

        self.physics_engine.update()
        self.player_list.update_animation(delta_time) 
        self.enemy_list.update(delta_time) 

        for enemy in self.enemy_list:
            if (self.player_sprite.box_l < enemy.center_x < self.player_sprite.box_r and 
                self.player_sprite.box_b < enemy.center_y < self.player_sprite.box_t):
                
                if self.player_sprite.knife_delay == self.player_sprite.curtime: 
                     enemy.health -= 50 
                     print("Enemy Hit!")

        self.scroll_to_player()

    def scroll_to_player(self):
        self.camera_sprites.position = (self.player_sprite.center_x, self.player_sprite.center_y)

if __name__ == "__main__":
    window = MyGame(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.setup()

    arcade.run()
