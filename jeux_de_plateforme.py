import os
import pygame
from os.path import join

pygame.init()
pygame.display.set_caption("Jeu de plateforme")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    
    def __init__(self, x, y, width, height):
        super().__init__() 
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None 
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0       #pr celui qui fait jump, jlai juste add pr pas decaler
        self.hit = False
        self.hit_count = 0


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self): 
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps): 
        self.y_vel = min(5, (self.fall_count / fps ) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count +=1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        
        self.fall_count +=1
        self.update_sprite()


    def update_sprite(self) :       # Celui qui fait jump ou cett fonction, dans hit on modif la fonction dcp tu reprend a : elif self.y_vel >0  (le if c'est transfo en elif par rapport a toi)
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel >0
    
    
    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, self.rect)

class Fire(Object):                                                               # pixel perfect collision horriz dams
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self): 
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("E:", "Python-Platformer-main (1)", "Python-Platformer-main", "assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image
 
    #celui qui fera la fonction handle_vertical_collision ici, la derniere lignge : collided_object.append(obj) je croit il oubli de l'indenté et il est hors de if/elif

def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)
    player.draw(window)  # Dessine le joueur par-dessus le fond
    pygame.display.update()  # Met à jour l'affichage

def collide(player, objects, dx):                          # pixel perfect collision horriz dams
    player.move(dx, 0)
    player.update()
    collide_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)          # pixel perfect collision horriz dams
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
       player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handel_vertical_collision(player, objects, player.y_vel)      #celui qui raj la ligne a la fin pas besoin de la recopier, c la modif du hit j'ai just raj vertical collide
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name =="fire":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    player = Player(100, 100, 50, 50)  # Instanciation correcte de Player
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)                                  #adding trap/fire dam BIEN METTRE LA BONNE RESOLUTION DE LIMAGE SINN SA CHARGERA PAS
    fire.on()

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]          #pixel perfect colision horriz dams               

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left(PLAYER_VEL)
        elif keys[pygame.K_RIGHT]:
            player.move_right(PLAYER_VEL)
        else:
            player.x_vel = 0  # Stop le joueur s'il n'y a pas d'entrée


        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)                     
        draw(window, background, bg_image, player, objects)  # Redessine l'écran avec le fond et le joueur            
 
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
