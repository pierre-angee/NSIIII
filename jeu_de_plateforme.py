import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

# Initialisation de la fenêtre 
pygame.display.set_caption("Jeu de plateforme")

# Dimensions 
WIDTH, HEIGHT = 1000, 800
FPS = 60  # Images par seconde
PLAYER_VEL = 5  # Vitesse joueur

window = pygame.display.set_mode((WIDTH, HEIGHT))

# Fonction pour retourner (flip) les sprites horizontalement
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Fonction pour charger les feuilles de sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Chemin 
    path = join("E:", "Python-Platformer-main (1)", "Python-Platformer-main", "assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        # Directions de sprites 
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

# Fonction pour charger un bloc d'environnement
def get_block(size):
    path = join("E:", "Python-Platformer-main (1)", "Python-Platformer-main", "assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

# Classe pour le joueur
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1  # Gravité appliquée au joueur
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)  # Chargement des sprites du joueur
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0  # Vitesse horizontale
        self.y_vel = 0  # Vitesse verticale
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    # Fonction saut
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    # Fonction déplacement joueur
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # Fonction pour enregistrer un coup reçu
    def make_hit(self):
        self.hit = True

    # Mouvement gauche
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    # Mouvement droite
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Boucle pour appliquer les effets de gravité et mettre à jour l'état du joueur
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    # Le joueur atterrit
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    # Le joueur frappe un objet au-dessus de lui
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    # Mise à jour du sprite en fonction du joueur
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # Mise à jour de la position 
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    # Dessin du joueur dans la fenêtre
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# Classe pour les objets 
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    # Dessin de l'objet
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# Classe pour les blocs de terrain
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

# Classe pour les objets feu 
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    # Allumer le feu
    def on(self):
        self.animation_name = "on"

    # Éteindre le feu
    def off(self):
        self.animation_name = "off"

    # Boucle d'animation du feu
    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# Fonction pour le fond d'écran
def get_background(name):
    image = pygame.image.load(join("E:", "Python-Platformer-main (1)", "Python-Platformer-main", "assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

# Fonction pour dessiner tous les éléments du jeu
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

# Collisions verticales
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

# Vérifier les collisions horizontales
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

# Gérer les mouvements du joueur avec les collisions
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

# Classe pour la fin de niveau
class Flag:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(join("E:", "Python-Platformer-main (1)", "Python-Platformer-main", "assets", "Items", "Checkpoints", "End", "End (idle).png")).convert_alpha()
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# Fonction principale du jeu
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96
    flag = Flag(1500, HEIGHT - 96 - 50, 40, 50)  
    player = Player(100, 100, 50, 50)
    fire = Fire(400, HEIGHT - block_size - 350, 16, 32)
    fire2 = Fire(1100, HEIGHT - block_size - 350, 16, 32)
    fire.on()
    fire2.on()
    
    # Création du sol et des autres blocs
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(block_size * 1, HEIGHT - block_size *2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block(block_size * 4, HEIGHT - block_size *4, block_size),
               Block(block_size * 5, HEIGHT - block_size *4, block_size),
               Block(block_size * 7, HEIGHT - block_size *6, block_size),
               Block(block_size * 8, HEIGHT - block_size *6, block_size),
               Block(block_size * 9, HEIGHT - block_size *6, block_size),
               Block(block_size * 10, HEIGHT - block_size *4, block_size),
               Block(block_size * 11, HEIGHT - block_size *4, block_size),
               Block(block_size * 12, HEIGHT - block_size *4, block_size), fire, fire2, flag]

    offset_x = 0
    scroll_area_width = 200

    # Boucle principale du jeu
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        fire2.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # Gestion du défilement de la caméra
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

# Exécution du jeu
if __name__ == "__main__":
    main(window)


