import random
import arcade
import timeit
import math
import os


                       ###################################### 
                       ###############CLASES#################
                       ######################################

class Enemy(arcade.Sprite):
    #Se define la clase enemigo 
    def _init_(self):
        super().__init__()
        self.player = None
        self.curtime = 0
        self.delay = 0
        self.growl = False
        self.sound_list = None
        self.coin_list = None
        self.health = 100
        self.death_animation = 0


    def update(self):
        self.curtime += 1

        # Se define en el update del enemigo la animación en caso de morir
        if self.health <= 0 and self.death_animation == 0:
            self.death_animation = self.curtime + 30
        if self.death_animation - 20 > self.curtime:
            self.set_texture(1)
        elif self.death_animation - 10 > self.curtime:
            self.set_texture(2)
        elif self.death_animation > self.curtime:
            self.kill()


class Player_Sprite(arcade.Sprite):
    def __init__(self):

        # Se crea la clase padre 
        super().__init__()

        # Se pone en default para que el personaje mire a la derecha
        self.character_face_direction = RIGHT_FACING

        # Se define el cur_texture para el cambio de imagen
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Se ajustan las coliciones con las cosas en default se incluye mucho espacio vacio 
        #Genera un cuadrado al rededor del sprite que funciona como el hitbox
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

  
        # Sprites personaje principal
        main_path = "imagenes/Sprites-35.png"
        sound0 = arcade.load_sound("sounds/knife_hit.ogg")
        self.idle_texture_pair = load_texture_pair(main_path)
        self.idle_texture_pair.append("imagenes/Sprites_11.png")
        self.idle_texture_pair.append("imagenes/Sprites_29.png")
        self.player_sprite_alive = True
        self.player_sprite_death_sound = False
        self.knife_delay = 0
        self.knife_rate = 0
        self.curtime = 0
        self.eye_pos = "right"
        self.sound_list = []
        self.sound_list.append(sound0)
        self.box_l = 50
        self.box_r = 50
        self.box_t = 50
        self.box_b = 50

        # Carga las texturas al caminar
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(main_path)
            self.walk_textures.append(texture)

    def update_animation(self, delta_time: float = 1/60):

        # Miramos si se el personaje se mueve a la izquierda o a la derecha 
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
            self.eye_pos = "left"
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
            self.eye_pos = "right"

        # Animación al caminar en si para que al moverse no intente dibujar una textura que no exista
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]
    
    def stab(self):
        if self.player_sprite_alive:
            # Delay para no spamear el boton de stab, en caso tal se demora mas
            if self.curtime < self.knife_rate:
                self.knife_rate += 5

            if self.curtime > self.knife_rate:
                #Al timear perfecto el stab va a ser un hit perfecto y va a ser mas rapido
                self.knife_delay = self.curtime
                self.knife_rate = self.curtime + 20
                arcade.play_sound(self.sound_list[0])

                # Determina si hay algo en frente del jugador
                range = 64
                if self.eye_pos == "right":
                    self.box_l = self.center_x
                    self.box_r = self.center_x + range
                    self.box_t = self.center_y + 16
                    self.box_b = self.center_y - 16
                if self.eye_pos == "left":
                    self.box_l = self.center_x - range
                    self.box_r = self.center_x
                    self.box_t = self.center_y + 16
                    self.box_b = self.center_y - 16

        
class Room:
    """ A room """
    #Generamos la clase de la habitación
    def __init__(self, r, c, h, w):
        self.row = r
        self.col = c
        self.height = h
        self.width = w


class RLDungeonGenerator:
    #La clase de los dungeon generator para que sean aleatorias 
    """Genera la dungeon"""
    def __init__(self, w, h):
        #Definimos el init
        """ Crea el tablero de juego"""
        self.MAX = 15  # Cuando ya hay 15 secciones para de crear habitaciones
        self.width = w
        self.height = h
        self.leaves = []
        self.dungeon = []
        self.rooms = []

        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append('#')

            self.dungeon.append(row)

    def random_split(self, min_row, min_col, max_row, max_col):
        # Lo que hacemos es separar y separar hasta llegar al limite definido
        seg_height = max_row - min_row
        seg_width = max_col - min_col

        if seg_height < self.MAX and seg_width < self.MAX:
            self.leaves.append((min_row, min_col, max_row, max_col))
        elif seg_height < self.MAX <= seg_width:
            self.split_on_vertical(min_row, min_col, max_row, max_col)
        elif seg_height >= self.MAX > seg_width:
            self.split_on_horizontal(min_row, min_col, max_row, max_col)
        else:
            if random.random() < 0.5:
                self.split_on_horizontal(min_row, min_col, max_row, max_col)
            else:
                self.split_on_vertical(min_row, min_col, max_row, max_col)

    def split_on_horizontal(self, min_row, min_col, max_row, max_col):
        #Generamos el split en horizontal
        split = (min_row + max_row) // 2 + random.choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, split, max_col)
        self.random_split(split + 1, min_col, max_row, max_col)

    def split_on_vertical(self, min_row, min_col, max_row, max_col):
        #Generamos el split en vertical
        split = (min_col + max_col) // 2 + random.choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, max_row, split)
        self.random_split(min_row, split + 1, max_row, max_col)

    def carve_rooms(self):
        for leaf in self.leaves:
            # Lo que queremos es que la dungeon no se vea TAN uniforme, entonces intentamos que las dimensiones sean diferentes 
            if random.random() > 0.80:
                continue
            section_width = leaf[3] - leaf[1]
            section_height = leaf[2] - leaf[0]

            # La altura y anchura va a ser entre un 60 y un 100% de lo definido
            # permitido en la sección
            room_width = round(random.randrange(60, 100) / 100 * section_width)
            room_height = round(random.randrange(60, 100) / 100 * section_height)

            # Si la habitación no ocupa enteramente la sección que se esta dibujando
            # Se ajusta esta al cuadrado
            if section_height > room_height:
                room_start_row = leaf[0] + random.randrange(section_height - room_height)
            else:
                room_start_row = leaf[0]

            if section_width > room_width:
                room_start_col = leaf[1] + random.randrange(section_width - room_width)
            else:
                room_start_col = leaf[1]

            self.rooms.append(Room(room_start_row, room_start_col, room_height, room_width))
            for r in range(room_start_row, room_start_row + room_height):
                for c in range(room_start_col, room_start_col + room_width):
                    self.dungeon[r][c] = '.'

    @staticmethod
    def are_rooms_adjacent(room1, room2):
        """ Esto se hace para saber si dos habitaciones estan juntas"""
        adj_rows = []
        adj_cols = []
        for r in range(room1.row, room1.row + room1.height):
            if room2.row <= r < room2.row + room2.height:
                adj_rows.append(r)

        for c in range(room1.col, room1.col + room1.width):
            if room2.col <= c < room2.col + room2.width:
                adj_cols.append(c)

        return adj_rows, adj_cols

    @staticmethod
    def distance_between_rooms(room1, room2):
        """Se agarra la distancia entre dos habitaciones"""
        centre1 = (room1.row + room1.height // 2, room1.col + room1.width // 2)
        centre2 = (room2.row + room2.height // 2, room2.col + room2.width // 2)

        return math.sqrt((centre1[0] - centre2[0]) ** 2 + (centre1[1] - centre2[1]) ** 2)

    def carve_corridor_between_rooms(self, room1, room2):
        """ Una vez se sabe la distancia y si estan juntas o no entonces se crean pasillos entre estas"""
        if room2[2] == 'rows':
            row = random.choice(room2[1])
            # Evalua cual habitacion esta a la derecha
            if room1.col + room1.width < room2[0].col:
                start_col = room1.col + room1.width
                end_col = room2[0].col
            else:
                start_col = room2[0].col + room2[0].width
                end_col = room1.col
            for c in range(start_col, end_col):
                self.dungeon[row][c] = '.'

            if end_col - start_col >= 4:
                self.dungeon[row][start_col] = '+'
                self.dungeon[row][end_col - 1] = '+'
            elif start_col == end_col - 1:
                self.dungeon[row][start_col] = '+'
        else:
            col = random.choice(room2[1])
            # Evalua cual habitación esta arriba
            if room1.row + room1.height < room2[0].row:
                start_row = room1.row + room1.height
                end_row = room2[0].row
            else:
                start_row = room2[0].row + room2[0].height
                end_row = room1.row

            for r in range(start_row, end_row):
                self.dungeon[r][col] = '.'

            if end_row - start_row >= 4:
                self.dungeon[start_row][col] = '+'
                self.dungeon[end_row - 1][col] = '+'
            elif start_row == end_row - 1:
                self.dungeon[start_row][col] = '+'

    def find_closest_unconnect_groups(self, groups, room_dict):
        """
        Encuentra dos habitaciones que esten cerca que esten en diferentes grupos
        y dibuja un corridor entre estos dos
        """
        shortest_distance = 99999
        start = None
        start_group = None
        nearest = None

        for group in groups:
            for room in group:
                key = (room.row, room.col)
                for other in room_dict[key]:
                    if not other[0] in group and other[3] < shortest_distance:
                        shortest_distance = other[3]
                        start = room
                        nearest = other
                        start_group = group

        self.carve_corridor_between_rooms(start, nearest)

        # Crea los diferentes grupos
        other_group = None
        for group in groups:
            if nearest[0] in group:
                other_group = group
                break

        start_group += other_group
        groups.remove(other_group)

    def connect_rooms(self):
        """
        Creamos un diccionario que contiene como entrada cada habitación.
        Cada espacio tendra una lista con las habitaciones adyacentes
        (sean adyacentes por filas o columnas) y las distancias entre ellas
        Ademas creamos los grupos iniciales(el cual inciara como una lista de habitaciones iniciales)
        """
        groups = []
        room_dict = {}
        for room in self.rooms:
            key = (room.row, room.col)
            room_dict[key] = []
            for other in self.rooms:
                other_key = (other.row, other.col)
                if key == other_key:
                    continue
                adj = self.are_rooms_adjacent(room, other)
                if len(adj[0]) > 0:
                    room_dict[key].append((other, adj[0], 'rows', self.distance_between_rooms(room, other)))
                elif len(adj[1]) > 0:
                    room_dict[key].append((other, adj[1], 'cols', self.distance_between_rooms(room, other)))

            groups.append([room])
            
        while len(groups) > 1:
            self.find_closest_unconnect_groups(groups, room_dict)

    def generate_map(self):
        """Hacemos el mapa"""
        self.random_split(1, 1, self.height - 1, self.width - 1)
        self.carve_rooms()
        self.connect_rooms()
            
    
class MyGame(arcade.Window):
    """
    MyGame va a ser nuestro "MAIN"
    """
    
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # seleccionamos el directorio de trabajo que queremos donde esperamos que esten los archivos buscados 
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
         #variables de juego
        self.game_started = False
        
         #lista de sprites
       
        self.wall_list = None
        self.player_list = None
        self.effect_list = None
        self.all_sprites_list = None
        self.enemy_list = None
        self.player_sprite = None
        self.grid = None
        self.enemy_sprite = None
       
         #setup del juego
        
        self.view_bottom = 0
        self.view_left = 0
        self.physics_engine = None
        self.player = None
        self.health = 100
        
        # variables de tiempo
        self.processing_time = 0
        self.draw_time = 0
        
        #pantalla inicial del juego
        self.menu = arcade.load_texture("imagenes/menuf.png")
        
       
        # lista de sonidos del juego
        self.sounds_list = []
        self.sounds_list.append(arcade.load_sound("sounds/Piano.mp3")) #0
        self.sounds_list.append(arcade.load_sound("sounds/demon_die.ogg")) #1
        
        # Generador de fondo
        arcade.set_background_color(arcade.color.BLACK)
        

    def setup(self):
        """Hacemos el setup principal del juego"""
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite = Player_Sprite()
        self.player_sprite_list.append(self.player_sprite)
        self.enemy_list = arcade.SpriteList()
        self.all_sprites_list = arcade.SpriteList()
        self.enemy_sprite = Enemy()
        self.effect_list = arcade.SpriteList()

        self.player_sprite.center_x = GRID_WIDTH // 2
        self.player_sprite.center_y = GRID_HEIGHT // 2
        self.player_sprite.scale = 0.5
        self.all_sprites_list.append(self.player_sprite)
        
        #Texturas del enemigo
        self.demon_die_1 = arcade.load_texture("imagenes/demon_die_1.png")
        self.demon_die_2 = arcade.load_texture("imagenes/demon_die_2.png")
        self.demon_slash = arcade.load_texture("imagenes/demon_slash.png")


        # Se crea el sistema de cavernas usando una cuadricula en 2D
        dg = RLDungeonGenerator(GRID_WIDTH, GRID_HEIGHT)
        dg.generate_map()
        arcade.play_sound(self.sounds_list[0])

        # Se crean los sprites en base a la cuadricula
        if not MERGE_SPRITES:
            #Basicamente cada espacio de la cuadricula va a ser sprite
            for row in range(dg.height):
                for column in range(dg.width):
                    value = dg.dungeon[row][column]
                    if value == '#':
                        wall = arcade.Sprite(":resources:images/tiles/brickTextureWhite.png", WALL_SPRITE_SCALING)
                        wall.center_x = column * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                        wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                        self.wall_list.append(wall)
        else:
            for row in range(dg.height):
                column = 0
                while column < dg.width:
                    while column < dg.width and dg.dungeon[row][column] != '#':
                        column += 1
                    start_column = column
                    while column < dg.width and dg.dungeon[row][column] == '#':
                        column += 1
                    end_column = column - 1

                    column_count = end_column - start_column + 1
                    column_mid = (start_column + end_column) / 2

                    wall = arcade.Sprite(":resources:images/tiles/brickTextureWhite.png", WALL_SPRITE_SCALING,
                                         repeat_count_x=column_count)
                    wall.center_x = column_mid * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.width = WALL_SPRITE_SIZE * column_count
                    self.wall_list.append(wall)

    

        # Poner random al personaje, en caso de que este en una postura relocarlo hasta que no lo este
        placed = False
        while not placed:

            #Posicion random
            self.player_sprite.center_x = random.randrange(AREA_WIDTH)
            self.player_sprite.center_y = random.randrange(AREA_HEIGHT)
            # Se evalua si estamos en una pared
            walls_hit = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)
            if len(walls_hit) == 0:
                #Si no lo estamos posicionamos
                placed = True
        
        for x in range(BR_X):
            for y in range(BR_Y):
                    # Cada vez que entremos a una habitación crece la posibilidad de que los enemigos spawneen 
                enemy = Enemy("imagenes/demon.png", 1.5)
                enemy.center_x = random.randrange(AREA_WIDTH)
                enemy.center_y = random.randrange(AREA_WIDTH)
                enemy.player = self.enemy_sprite
                enemy.curtime = 0
                enemy.delay = 0
                enemy.growl = False
                enemy.health = 100
                enemy.death_animation = 0
                enemy.append_texture(self.demon_die_1)
                enemy.append_texture(self.demon_die_2)
                enemy.append_texture(self.demon_slash)
                walls_hit_enemies = arcade.check_for_collision_with_list(enemy, self.wall_list)
                if len(walls_hit_enemies) == 0:
                    #Evaluamos si un enemigo esta en la pared o no para colocarlo o no respectivmente
                    self.all_sprites_list.append(enemy)
                    self.enemy_list.append(enemy)
        
        placed = False
        while not placed:
            #Agregamos una puerta en algun lugar random
            door = arcade.Sprite("imagenes/castle_door_open.png", 1)
            door.center_x = random.randrange(AREA_WIDTH)
            door.center_y = random.randrange(AREA_WIDTH)
            self.all_sprites_list.append(wall)
            self.wall_list.append(wall)
            walls_hit = arcade.check_for_collision_with_list(door, self.wall_list)
            if len(walls_hit) == 0:
                # En caso de que esta no este en una pared se coloca
                placed = True
                            
        #Esto genera las fisicas con los muros para que el personaje no traspase los muros
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,self.wall_list)

    def on_draw(self):
        """Reenderizamos la imagen y se refrezca por cada frame """

        draw_start_time = timeit.default_timer()

        arcade.start_render()
        self.image = None
        # Dibujamos los sprites
        self.wall_list.draw()
        self.player_sprite_list.draw()
        self.enemy_list.draw()
        self.effect_list.draw()
        
        # Creamos la barra de vida 
        x = self.player_sprite.center_x
        y = self.player_sprite.center_y
        arcade.draw_rectangle_filled(x, y - 16, 24, 4, (255, 0, 0))
        arcade.draw_rectangle_filled(x - math.ceil((24 - (self.health / 4.16)) / 2), y - 16, math.ceil(self.health / 4.16), 4, (0, 255, 0))
    

        # Colocamos la información en la pantalla
        sprite_count = len(self.wall_list)

        output = f"Sprite Count: {sprite_count}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 20 + self.view_bottom,
                         arcade.color.WHITE, 16)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 40 + self.view_bottom,
                         arcade.color.WHITE, 16)

        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 60 + self.view_bottom,
                         arcade.color.WHITE, 16)

        self.draw_time = timeit.default_timer() - draw_start_time
        
        if not self.game_started:
            arcade.draw_texture_rectangle(self.player_sprite.center_x-90,  self.player_sprite.center_y-32, 800, 600, self.menu)

    def on_key_press(self, key, modifiers):
        """El comando on_key_press se va a ejecutar cada vez que el usuario oprime una tecla"""

        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
        self.game_started = True

    def on_key_release(self, key, modifiers):
        """El comando on_key_press se va a ejecutar cada vez que el usuario suelta una tecla """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
       
        if key == arcade.key.Z or key == arcade.key.X:
                self.player_sprite.stab()
           
            
    def on_mouse_press(self, x, y, button, modifier):
        self.game_started = True

    def on_update(self, delta_time):
        """ on_update refrezca y le da el movimiento y  logica al juego """
        self.player_sprite.curtime += 1
        start_time = timeit.default_timer()

       # Mueve el jugador y sus animaciones
        self.physics_engine.update()
        self.player_sprite_list.update()
        self.enemy_list.update()
        self.physics_engine.update()
        self.player_sprite_list.update_animation()

        # ---Scrolling ---
 
        #Crea el objeto invisible cuchillo que elimina enemigos
        for enemy in self.enemy_list:
                    if self.player_sprite.box_l < enemy.center_x < self.player_sprite.box_r and self.player_sprite.box_b < enemy.center_y < self.player_sprite.box_t:
                        enemy.health = 0
                        arcade.play_sound(self.sounds_list[1])

        #Barra de vida del personaje
        for enemy in self.enemy_list:
            enemy_check = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
            for enemy in enemy_check:
                if enemy.health > 0:
                    self.health = 100
                    enemy.set_texture(1)

        changed = False

        # Scroll izquierda, el movimiento hacia la izquierda sea fluido
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll derecha, el movimiento hacia la derecha sea fluido
        right_bndry = self.view_left + WINDOW_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll arriba, el movimiento hacia arriba sea fluido
        top_bndry = self.view_bottom + WINDOW_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll abajo, el movimiento hacia abajo sea fluido       
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        
        if changed:
            arcade.set_viewport(self.view_left,
                                WINDOW_WIDTH + self.view_left,
                                self.view_bottom,
                                WINDOW_HEIGHT + self.view_bottom)


        
        #Nos informa del tiempo en el que se demora en procesa una acción
        self.processing_time = timeit.default_timer() - start_time
        
                        ###############################
                        ###########funciones###########
                        ###############################
                        
def load_texture_pair(Sprites):
    """
    Carga las texturas haciendole mirror a la segunda
    """
    return [
        arcade.load_texture("imagenes/Sprites-35.png"),
        arcade.load_texture("imagenes/Sprites-35.png", flipped_horizontally=True)]

def main():
    """ Nuestro main el cual va a generar el juego """
    game = MyGame(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game.setup()
    arcade.run()

# COMENZAMOS LA EJECUCIÓN
WALL_SPRITE_SCALING = 0.5
PLAYER_SPRITE_SCALING = 0.25
CHARACTER_SCALING = 1

WALL_SPRITE_SIZE = 128 * WALL_SPRITE_SCALING

#Definimos que tan grande la cuadricula del mapa va a ser
GRID_WIDTH = 100
GRID_HEIGHT = 100

RIGHT_FACING = 0
LEFT_FACING = 1
# Definimos con variables enteras el estar mirando a la derecha o a la izquierda

BR_X = 32
BR_Y = 20


AREA_WIDTH = GRID_WIDTH * WALL_SPRITE_SIZE
AREA_HEIGHT = GRID_HEIGHT * WALL_SPRITE_SIZE

# La velocidad del jugador 
MOVEMENT_SPEED = 3
UPDATES_PER_FRAME = 5

#Se define un desplazamiento para que se vea mejor la imagen al mover el jugador
VIEWPORT_MARGIN = 300

#Se define el tamaño de la pantalla junto al nombre de esta(En nuestro caso el nombre del juego)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "SwordArt"

MERGE_SPRITES = False

if __name__ == "__main__":
    main()
# TERMINAMOS LA EJECUCIÓN


