#------------------------#
#     Julien Vanherf     #
#   Nicolas Schneiders   #
#------------------------#

import math
import pygame
import sys
from pygame import sprite
from pygame.event import clear
from pygame.time import Clock

# Constantes

NOIR = (0, 0, 0)
GRIS = (69, 90, 100)
ROUGE= (255,0 ,0)
ORANGE = (255,140,0)
BLEU = (0, 187, 255)
VIOLET = (84, 54, 145)

WINDOW_WIDTH =1080 #800
WINDOW_HEIGHT = 720#534

ACTUAL_WINDOW_WIDTH = 800
ACTUAL_WINDOW_HEIGHT = 534

GAUCHE = pygame.K_LEFT
DROITE = pygame.K_RIGHT
HAUT = pygame.K_UP
BAS = pygame.K_DOWN
ESPACE = pygame.K_SPACE
ENTER = pygame.K_RETURN
BACK = pygame.K_BACKSPACE
ESC = pygame.K_ESCAPE
Z = pygame.K_z
Q = pygame.K_q
S = pygame.K_s
D = pygame.K_d
V = pygame.K_v
L = pygame.K_l

GROUND_HEIGHT = 64
P_1_JUMP_POWER = 17
P_2_JUMP_POWER = 17

MAX_ALCOOL = 100


# Paramètres et initialisation

dimensions_fenetre = (WINDOW_WIDTH, WINDOW_HEIGHT)  # en pixels
images_par_seconde = 60
vect = pygame.math.Vector2

pygame.init()

display = pygame.display.set_mode((ACTUAL_WINDOW_WIDTH,ACTUAL_WINDOW_HEIGHT))

#fenetre = pygame.display.set_mode(dimensions_fenetre)

fenetre = pygame.Surface(dimensions_fenetre)

icon = pygame.image.load('sprites/menu_images/icon.pg.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("Pastis Quest")

# Fonctions

# - CREATION LISTE D'ANIMATIONS - #
def create_anim_list(dir_img, anim_type ):
    anim = []
    if anim_type == 'w':
        file_list = ('walk_1.png','walk_2.png', 'walk_3.png','walk_4.png','walk_5.png','walk_6.png','walk_7.png')
    if anim_type == 'w_l':
        file_list = ('walk_1_l.png','walk_2_l.png', 'walk_3_l.png','walk_4_l.png','walk_5_l.png','walk_6_l.png','walk_7_l.png')
    if anim_type == 'i':
        file_list = ('idle_1.png','idle_2.png', 'idle_3.png','idle_4.png')
    if anim_type == 'i_l':
        file_list = ('idle_1_l.png','idle_2_l.png', 'idle_3_l.png','idle_4_l.png')
    if anim_type == 'b':
        file_list = ('button_1.png','button_2.png','button_3.png','button_3.png')
    if anim_type == 'l':
        file_list = ('lever_0.png', 'lever_1.png', 'lever_2.png')

    for file_name in file_list:
        image = dir_img + file_name
        sprite = pygame.image.load(image).convert_alpha(fenetre)
        anim.append(sprite)

    return anim

# - SPRITES - #

def dessine(entite, ecran):
    ecran.blit(entite.sprite, entite.pos)

def collider():
    #Permet de gérer les collisions entre les Dinosaures et les Objets sur le plateau de jeu
    global lvl, anim_speed, win, player_list, stand_list, past_list, wall_list, button_list, can_press, lever_can_press
    for player in player_list:
        # COLLIDER PLATEFORME #
        hits = pygame.sprite.spritecollide(player, stand_list, False)
        for stand in hits:
            if stand.state != None and stand.state == 'white':
                stand = change_stand_state(player, stand)
            if stand.state == 'movable':
                if stand.orientation == 'sideway' :
                    if move_left:
                        player.pos.x -= 4
                    if move_right:
                        player.pos.x += 4
            if (stand.state != player.color or stand.state == None) and player.pos.y + 56< stand.pos[1]:
                if not player.down:
                    player.vel.y = 0
                    player.pos.y = stand.rect.top-player.rect[3]
                    player.has_jumped = False
                else:
                    player.down = False
        # COLLIDER PLATEFORME #

        # COLLIDER MUR #
        hits_wall = pygame.sprite.spritecollide(player, wall_list, False)
        for wall in hits_wall:
            if wall.state != None and wall.state == 'white':
                wall = change_wall_state(player, wall)
            if (wall.state != player.color or wall.state == None):
                if player.pos.y +56 < wall.pos[1]:
                    player.vel.y = 0
                    player.pos.y = wall.rect.top-player.rect[3]
                    player.has_jumped = False
                elif player.vel.x < 0 and player.pos.y < wall.pos[1] + 240:
                    player.pos.x = wall.pos[0]+32
                    player.vel.y += 0.4
                elif player.vel.x > 0:
                    player.pos.x = wall.pos[0]-player.rect[2]
                    player.vel.y += 0.4
                
                player.vel.x = 0

        # COLLIDER MUR #

        # COLLIDER SOL #
        if player.vel.y > 0:
            hit_g = pygame.sprite.spritecollide(player ,ground_list, False)

            if hit_g:
                player.vel.y = 0
                player.pos.y = hit_g[0].rect.top -player.rect[3]
                player.has_jumped = False
        # COLLIDER SOL #

        # COLLIDER BORDURE DE LA FENETRE #
        if player.pos.x > WINDOW_WIDTH:
            player.pos.x = -32
        if player.pos.x < -32:
            player.pos.x = WINDOW_WIDTH
        # COLLIDER BORDURE DE LA FENETRE #

    # COLLIDER PASTIS #
    if pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[0], past_list, False) and pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[1], past_list, False) and not player_2.has_jumped and not player_1.has_jumped :
        anim_speed = 0.9
        win = True
        fenetre.blit(win_message,(WINDOW_WIDTH//2- win_messageLargeur//2,WINDOW_HEIGHT//2))
    # COLLIDER PASTIS #

    # COLLIDER BOUTONS #
    if pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[0], button_list, False) or pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[1], button_list, False):
        can_press = True
        fenetre.blit(V_SIGN,(10,10))
    else:
        can_press = False
    # COLLIDER BOUTONS #

    # COLLIDER LEVIER #
    hit_l = pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[0], lever_list, False) or pygame.sprite.spritecollide(pygame.sprite.Group.sprites(player_list)[1], lever_list, False)
    if hit_l and hit_l[0].color == player.color:
        lever_can_press = True

    else :
        lever_can_press = False

    # COLLIDER LEVIER #

    if player_1.pos.y > WINDOW_HEIGHT and player_2.pos.y > WINDOW_HEIGHT:
        lvl -=1
        load_level(scene)

def update_rect_pos(scene):
    #permet de mettre à jour les rectangles de tout les sprites sur la scene
    for each in scene:
        each.rect.x = each.pos[0]
        each.rect.y = each.pos[1]

# GESTION DES ANIMATIONS 
def animator():
    global anim_speed, lever_activated
    for player in player_list:
        if player.move:
            # Gestion animation Mouvement
            if player.direc == 'l':
                player.current_sprite += anim_speed

                if player.current_sprite >= len(player.sprites_move_l):
                    player.current_sprite = 0

                player.sprite = player.sprites_move_l[int(player.current_sprite)]

                player.move = False

            elif player.direc == 'r':
                player.current_sprite += anim_speed

                if player.current_sprite >= len(player.sprites_move_r):
                    player.current_sprite = 0

                player.sprite = player.sprites_move_r[int(player.current_sprite)]

                player.move = False

        else:
            # Gestion animation Idle
            if player.direc_idle == 'r':

                player.current_sprite += anim_speed

                if player.current_sprite >= len(player.sprites_idle_r):
                    player.current_sprite = 0

                player.sprite = player.sprites_idle_r[int(player.current_sprite)]

            elif player.direc_idle == 'l':

                player.current_sprite += anim_speed

                if player.current_sprite >= len(player.sprties_idle_l):
                    player.current_sprite = 0

                player.sprite = player.sprties_idle_l[int(player.current_sprite)]
    if lever_activated:
        for lever in lever_list:
            if lever.current_sprite < len(lever.images)-1:
                lever.current_sprite += 0.1

            lever.sprite = lever.images[int(lever.current_sprite)]
# - SPRITES - #

# - SCENE - #
def ajouteEntite(scene, entite):
    scene.add(entite)

def acteurs(scene):
    return pygame.sprite.Group.sprites(scene)

def affiche(scene, ecran):
    entites = acteurs(scene)
    for objet in entites:
        dessine(objet, ecran)

def affiche_hud(fenetre):
    global taux_alcool
    police_caractere = pygame.font.Font('font/upheavtt.ttf', 32)
    txt = str(taux_alcool)
    alcool_percent = police_caractere.render('{} %'.format(txt) , True, ORANGE)
    alcool_percent_largeur, alcool_percent_hauteur = police_caractere.size(txt)
    fenetre.blit(alcool_percent, (WINDOW_WIDTH-64-alcool_percent_largeur, WINDOW_HEIGHT-48))

# - SCENE - #

# - INPUT - #
# Gestions des touches des joueur pendant la partie
def action():
    global scene, lvl, win, fenetre, can_press, taux_alcool, flip, lever_activated
    player_2.vel.x = 0
    player_1.vel.x = 0
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == V and win :
                lvl +=1
                taux_alcool += 7.5
                load_level(scene)

            if evenement.key == V and can_press:
                switch_color()
            
            if evenement.key == L and lever_can_press:
                lever_activated = True
                open_wall()

    keys = pygame.key.get_pressed()
    if not win:
        if keys[HAUT] :
            if not player_2.has_jumped:
                player_2.vel.y -= P_2_JUMP_POWER
                player_2.has_jumped = True
                JUMP_SOUND.play()
            player_2.move = True

        if keys[BAS]:
            player_2.vel.y += 0.6
            player_2.move = True
            player_2.down = True
        else:
            player_2.down = False

        if keys[DROITE]:
            player_2.vel.x = 3.5
            player_2.move = True
            player_2.direc = 'r'
            player_2.direc_idle = 'r'

        if keys[GAUCHE]:
            player_2.vel.x -= 3.5
            player_2.move = True
            player_2.direc = 'l'
            player_2.direc_idle = 'l'

        if keys[ESPACE]:
            taux_alcool += 2.5
            load_level(scene)


        if keys[Z]:
            if not player_1.has_jumped:
                player_1.vel.y -= P_1_JUMP_POWER
                player_1.has_jumped = True
                JUMP_SOUND.play()
            player_1.move = True

        if keys[S]:
            player_1.vel.y += 0.6
            player_1.move = True
            player_1.down = True
        else:
            player_1.down = False

        if keys[Q]:
            player_1.vel.x -= 3.5
            player_1.move = True
            player_1.direc = 'l'
            player_1.direc_idle = 'l'

        if keys[D]:
            player_1.vel.x +=3.5
            player_1.move = True
            player_1.direc = 'r'
            player_1.direc_idle = 'r'
#Ajoute un d'index a la variable index qui permet de savoir sur quel menu le curseur se trouve
def menu_add(index, color_list, cursor):
    if index >= len(color_list)-1:
        index = 0
        cursor = color_list[index]
    else:
        index += 1
        cursor = color_list[index]
    return cursor, index
#Retire un d'index a la variable index qui permet de savoir sur quel menu le curseur se trouve
def menu_min(index, color_list, cursor):
    if index <= 0:
        index = len(color_list)-1
        cursor = color_list[index]
    else:
        index -= 1
        cursor = color_list[index]
    return cursor, index
# Gestions des touches dans les menus
def menu_input():
    global scene, in_game, p_1_cursor_state, p_2_cursor_state, p_1_chose, p_2_chose, color_list, p1_i,p2_i, actual_menu, cursor, selected_level, lvl, win_game, death
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evenement.type == pygame.VIDEORESIZE:
            global fenetre, WINDOW_WIDTH, WINDOW_HEIGHT
            fenetre = pygame.display.set_mode((evenement.w, evenement.h), pygame.RESIZABLE)
            WINDOW_WIDTH  = evenement.w
            WINDOW_HEIGHT = evenement.h
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == GAUCHE:
                if actual_menu == 'select_menu':
                    if not p_2_chose:
                        (p_2_cursor_state, p2_i) = menu_min(p2_i, color_list, p_2_cursor_state)
                elif actual_menu == 'select_level':
                    if selected_level != 1:
                        selected_level -= 1


            if evenement.key == DROITE:
                if actual_menu == 'select_menu':
                    if not p_2_chose:
                        (p_2_cursor_state, p2_i) = menu_add(p2_i, color_list, p_2_cursor_state)
                elif actual_menu == 'select_level':
                    if selected_level != 7:
                        selected_level += 1

            if evenement.key == Q:
                if actual_menu == 'select_menu':
                    if not p_1_chose:
                        (p_1_cursor_state, p1_i) = menu_min(p1_i, color_list, p_1_cursor_state)

            if evenement.key == D:
                if actual_menu == 'select_menu':
                    if not p_1_chose:
                        (p_1_cursor_state, p1_i) = menu_add(p1_i, color_list, p_1_cursor_state)

            if evenement.key == ENTER:
                if player_1.color != p_2_cursor_state or p_2_cursor_state != p_1_cursor_state:
                    chose_skin(player_2, p_2_cursor_state)
                    p_2_chose = True


            if evenement.key == ESPACE:
                if actual_menu == 'select_menu':
                    if player_2.color != p_1_cursor_state or p_2_cursor_state != p_1_cursor_state:
                        chose_skin(player_1, p_1_cursor_state)
                        p_1_chose = True
                elif actual_menu == 'start_screen':
                    JP_MEME.stop()
                    fade()
                    actual_menu = 'main_menu'

                elif actual_menu == 'main_menu':
                    fade()
                    actual_menu = cursor
                
                elif actual_menu == 'select_level':
                    fade()
                    lvl = selected_level
                    actual_menu = 'select_menu'
                    print('test')
                
                elif actual_menu == 'win' or actual_menu == 'death':
                    fade()
                    win_game = False
                    death = False
                    actual_menu = 'main_menu'


            if evenement.key == BAS:
                if cursor == 'select_menu':
                    cursor = 'select_level'

                elif cursor == 'select_level':
                    cursor = 'select_menu'

            if evenement.key == HAUT:
                if cursor == 'select_level':
                    cursor = 'select_menu'

                elif cursor == 'select_menu':
                    cursor = 'select_level'



            if evenement.key == BACK:
                p_2_chose = False

            if evenement.key == ESC:
                p_1_chose = False


            if evenement.key == V:
                if p_1_chose and p_2_chose:
                    load_level(scene)
                    in_game = True
# - INPUT - #

# - ENTITY - #
# CREATION DES PLATEFORMES, MURS, BOUTONS ET LEVIER, JOUEURS
def create_player(player_list,pos, color):
    global objects_to_add
    player = pygame.sprite.Sprite()
    player.sprite = PLAYER_1
    player.color = color

    player.pos = vect(pos)
    player.vel = vect(0,0)
    player.acc = vect(0,0)
    player.has_jumped = False
    player.direc = 'l'
    player.direc_idle = 'l'
    player.move = False
    player.down = False

    player.sprites_move_l = GREEN_WALK_L
    player.sprites_move_r = GREEN_WALK
    player.sprties_idle_l = GREEN_IDLE_L
    player.sprites_idle_r = GREEN_IDLE
    player.current_sprite = 0

    player.rect = player.sprite.get_rect()

    player_list.add(player)
    objects_to_add.append(player)

    return player

def create_stand(stand_list, pos, state='white', player = None, orientation = None):
    global objects_to_add
    stand = pygame.sprite.Sprite()
    if state == 'white':
        stand.sprite = WHITE_STAND
    elif state == 'movable':
        stand.sprite = MOVING_STAND
        if orientation == 'sideway':
            stand.max_pos_x = pos[0]+320
            
        if orientation == 'upway':
            stand.max_pos_y = pos[1]+240
        stand.orientation = orientation
    else:
        stand.sprite = WOOD_STAND
    stand.pos = pos
    stand.state = state
    stand.rect = stand.sprite.get_rect()
    if player != None:
        change_stand_state(player, stand)

    stand_list.add(stand)
    objects_to_add.append(stand)

def create_wall(wall_list, pos, state='white', player = None, openable = False):
    global objects_to_add
    wall = pygame.sprite.Sprite()
    if state == 'white':
        wall.sprite = WHITE_WALL
    elif state == None:
        wall.sprite = WOOD_WALL
    wall.pos = pos
    wall.state = state
    wall.rect = wall.sprite.get_rect()
    if player != None:
        change_wall_state(player, wall)
    wall.openable = openable

    wall_list.add(wall)
    objects_to_add.append(wall)

def create_past(past_list, pos):
    global objects_to_add
    past = pygame.sprite.Sprite()
    past.sprite = PASTIS
    past.pos = pos
    past.rect = past.sprite.get_rect()

    past_list.add(past)
    objects_to_add.append(past)

def create_ground(ground_list, pos):
    global objects_to_add

    ground = pygame.sprite.Sprite()
    ground.sprite = GROUND
    ground.sprite = pygame.transform.scale(ground.sprite, (WINDOW_WIDTH + 64 , 64))
    ground.rect = ground.sprite.get_rect()
    ground.pos = pos

    ground_list.add(ground)
    objects_to_add.append(ground)

def create_button(button_list, pos):
    global objects_to_add
    button = pygame.sprite.Sprite()
    button.sprite = BUTTON[0]
    button.rect = button.sprite.get_rect()
    button.pos = pos

    button_list.add(button)
    objects_to_add.append(button)

def create_lever(lever_list, pos, player):
    global objects_to_add
    lever = pygame.sprite.Sprite()
    lever.images = change_lever_color(player)
    lever.sprite = lever.images[0]
    lever.pos = pos
    lever.rect = lever.sprite.get_rect()
    lever.color = player.color

    lever_list.add(lever)
    objects_to_add.append(lever)
    lever.current_sprite = 0

def create_rail(rail_list, pos, orientation):
    global objects_to_add
    rail = pygame.sprite.Sprite()
    if orientation == 'upway':
        rail.sprite = STAND_RAIL_V
    if orientation == 'sideway':
        rail.sprite = STAND_RAIL_H
    rail.pos = pos
    rail.rect = rail.sprite.get_rect()
    rail_list.add(rail)
    objects_to_add.append(rail)

def moving_stand(stand_list, rail_list, pos,  orientation):
    if orientation == 'sideway':
        create_rail(rail_list, [pos[0]+32,pos[1]], orientation)
        create_stand(stand_list, [pos[0], pos[1]], 'movable', None, orientation)

    else:
        create_rail(rail_list, [pos[0]+48,pos[1]], orientation)
        create_stand(stand_list, [pos[0], pos[1]], 'movable', None, orientation)

#CHANGEUR DE COULEUR POUR LES LEVIER, LA COULEUR DU LEVIER DEPEND DU DINO 
def change_lever_color(player):
    if player.color == 'red':
        return RED_LEVER
    
    elif player.color == 'blue':
        return BLUE_LEVER
    
    elif player.color == 'green':
        return GREEN_LEVER
    
    elif player.color == 'yellow':
        return YELLOW_LEVER

#LOGIQUE DE DEPLACEMENT DES DINO
def move_player():
    for player in player_list:
        player.acc = vect(0,((WINDOW_HEIGHT/720)*0.6))
        action()
        player.acc.x += player.vel.x
        if player.vel.y > 13:
            player.vel.y = 13
        else:
            player.vel += player.acc
        player.pos += player.vel + 0.5 * player.acc

#CHOIX DU SKIN DU DINO
def chose_skin(player, color):
    if color == 'blue':
        player.color = 'blue'
        player.sprites_move_l = BLUE_WALK_L
        player.sprites_move_r = BLUE_WALK
        player.sprties_idle_l = BLUE_IDLE_L
        player.sprites_idle_r = BLUE_IDLE

    if color == 'green':
        player.color = 'green'
        player.sprites_move_l = GREEN_WALK_L
        player.sprites_move_r = GREEN_WALK
        player.sprties_idle_l = GREEN_IDLE_L
        player.sprites_idle_r = GREEN_IDLE

    if color == 'red':
        player.color = 'red'
        player.sprites_move_l = RED_WALK_L
        player.sprites_move_r = RED_WALK
        player.sprties_idle_l = RED_IDLE_L
        player.sprites_idle_r = RED_IDLE

    if color == 'yellow':
        player.color = 'yellow'
        player.sprites_move_l = YELLOW_WALK_L
        player.sprites_move_r = YELLOW_WALK
        player.sprties_idle_l = YELLOW_IDLE_L
        player.sprites_idle_r = YELLOW_IDLE

# - GESTION STAND ET MUR - #
# CHANGEMENT DES COULEURS DES MURS ET STANDS
def change_stand_color(stand):
    if stand.state == 'red' :
        return RED_STAND

    if stand.state == 'blue' :
        return BLUE_STAND

    if stand.state == 'green':
        return GREEN_STAND

    if stand.state == 'yellow':
        return YELLOW_STAND

def change_stand_state(player, stand):
    if player.color == 'red':
        stand.state = 'red'
        stand.sprite = change_stand_color(stand)

    if player.color == 'blue':
        stand.state = 'blue'
        stand.sprite = change_stand_color(stand)

    if player.color == 'green' :
        stand.state = 'green'
        stand.sprite = change_stand_color(stand)

    if player.color == 'yellow':
        stand.state = 'yellow'
        stand.sprite = change_stand_color(stand)

    return stand

def change_wall_color(wall):
    if wall.state == 'red' :
        return RED_WALL

    if wall.state == 'blue' :
        return BLUE_WALL

    if wall.state == 'green':
        return GREEN_WALL

    if wall.state == 'yellow':
        return YELLOW_WALL

def change_wall_state(player, wall):
    if player.color == 'red' :
        wall.state = 'red'
        wall.sprite = change_wall_color(wall)

    if player.color == 'blue' :
        wall.state = 'blue'
        wall.sprite = change_wall_color(wall)

    if player.color == 'green' :
        wall.state = 'green'
        wall.sprite = change_wall_color(wall)

    if player.color == 'yellow':
        wall.state = 'yellow'
        wall.sprite = change_wall_color(wall)

    return wall
#INVERSION DES COULEURS DE TOUT 
def switch_color():
    global stand_list, wall_list
    for stand in stand_list:
        if stand.state != None:
            if stand.state == player_1.color:
                stand = change_stand_state(player_2, stand)
            elif stand.state == player_2.color:
                stand = change_stand_state(player_1, stand)
    for wall in wall_list:
        if wall.state != None:
            if wall.state == player_1.color:
                wall = change_wall_state(player_2, wall)
            elif wall.state == player_2.color:
                wall = change_wall_state(player_1, wall)
#OUVRE LES MURS
def open_wall():
    global wall_list
    for each in wall_list:
        if each.openable == True:
            each.kill()
#MOUVEMENT DES PLATEFORMES AMOVIBLES
def moving_plateforme():
    global move_left, move_right, move_up, move_down
    for each in stand_list:
        if each.state == 'movable':
            if each.orientation == 'sideway':
                if each.pos[0] <= each.max_pos_x and move_right:
                    each.pos[0] +=2
                else:
                    move_left = True
                    move_right = False
                
                if each.pos[0] > each.max_pos_x-320 and move_left:
                    each.pos[0] -=2
                
                else:
                    move_left = False
                    move_right = True

            if each.orientation == 'upway':
                if each.pos[1] <= each.max_pos_y and move_down:
                    each.pos[1] +=2
                else:
                    move_up = True
                    move_down = False
                
                if each.pos[1] > each.max_pos_y-256 and move_up:
                    each.pos[1] -=2
                
                else:
                    move_up = False
                    move_down = True
            
# - GESTION STAND ET MUR - #

# - CLEAR SCENE - #
def clear_scene():
    scene.empty()

def clear_stand():
    stand_list.empty()

def clear_past():
    past_list.empty()

def clear_ground():
    ground_list.empty()

def clear_button():
    button_list.empty()

def clear_wall():
    wall_list.empty()

def clear_buttons():
    button_list.empty()

def clear_lever():
    lever_list.empty()

def clear_objects():
    objects_to_add.clear()

def add_players():
    objects_to_add.append(player_1)
    objects_to_add.append(player_2)

def clear_all():
    global objects_to_add
    clear_scene()
    clear_stand()
    clear_past()
    clear_ground()
    clear_button()
    clear_wall()
    clear_objects()
    clear_lever()

def reset_player(coord_p_1, coord_p_2):
    player_1.pos = coord_p_1
    player_2.pos = coord_p_2
    player_1.vel = vect(0,0)
    player_2.vel = vect(0,0)
# - CLEAR SCENE - #

# - GESTIONNAIRE MENU - #
#SELECTION DE NIVEAU
def draw_level_selector(selected_level):
    fenetre.fill(GRIS)
    if selected_level == 1:
        fenetre.blit(LVL_1_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 2:
        fenetre.blit(LVL_2_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 3:
        fenetre.blit(LVL_3_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 4:
        fenetre.blit(LVL_4_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 5:
        fenetre.blit(LVL_5_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 6:
        fenetre.blit(LVL_6_SCREEN, [WINDOW_WIDTH/8,32])

    if selected_level == 7:
        fenetre.blit(LVL_7_SCREEN, [WINDOW_WIDTH/8,32])

    lvl = police_caractere.render("Niveau {}".format(str(selected_level)), True, ORANGE)
    lvlLargeur, lvlHauteur = police_caractere.size("Niveau {}".format(str(selected_level)))
    fenetre.blit(lvl, (WINDOW_WIDTH//2 - lvlLargeur//2,WINDOW_HEIGHT-lvlHauteur-64))
    fenetre.blit(LEFT_MENU_ARROW, ((WINDOW_WIDTH//2-lvlLargeur//2-100),WINDOW_HEIGHT-lvlHauteur-80))
    fenetre.blit(RIGHT_MENU_ARROW, ((WINDOW_WIDTH//2+lvlLargeur//2+30),WINDOW_HEIGHT-lvlHauteur-80))
#SELECTION DU DINO
def draw_player_selector():
    global p_1_cursor_pos, p_2_cursor_pos, p_1_chose, p_2_chose
    fenetre.fill(GRIS)

    fenetre.blit(SHADOW, ((WINDOW_WIDTH//4+12), (WINDOW_HEIGHT//2 -132)))
    fenetre.blit(SHADOW, ((WINDOW_WIDTH - WINDOW_WIDTH//4 - 140), (WINDOW_HEIGHT//2 -132)))
    fenetre.blit(level_animator(UI_COLOR_LIST[p1_i], 'dino'), ((WINDOW_WIDTH//4+8), (WINDOW_HEIGHT//2 -108)))
    fenetre.blit(level_animator(UI_COLOR_LIST[p2_i], 'dino'), ((WINDOW_WIDTH - WINDOW_WIDTH//4 - 144), (WINDOW_HEIGHT//2 -108)))
    fenetre.blit(level_animator(P_1_FRAME, 'frame'), (WINDOW_WIDTH//4, WINDOW_HEIGHT//2 -116))
    fenetre.blit(level_animator(P_2_FRAME, 'frame'), ((WINDOW_WIDTH - WINDOW_WIDTH//4 - 152), (WINDOW_HEIGHT//2 - 116)))
    P_1_FRAME_RECT = P_1_FRAME[0].get_rect()
    P_2_FRAME_RECT = P_2_FRAME[0].get_rect()
    fenetre.blit(LEFT_MENU_ARROW, ((WINDOW_WIDTH - WINDOW_WIDTH//4-P_2_FRAME_RECT[2]-76),WINDOW_HEIGHT//2 - 116+P_2_FRAME_RECT[3]//4))
    fenetre.blit(RIGHT_MENU_ARROW, ((WINDOW_WIDTH - WINDOW_WIDTH//4+12),WINDOW_HEIGHT//2 - 116+P_2_FRAME_RECT[3]//4))
    fenetre.blit(Q_MENU_ARROW, (WINDOW_WIDTH//4-76,WINDOW_HEIGHT//2 - 116+P_2_FRAME_RECT[3]//4))
    fenetre.blit(D_MENU_ARROW, (WINDOW_WIDTH//4 + P_1_FRAME_RECT[2]+12 ,WINDOW_HEIGHT//2 - 116+P_2_FRAME_RECT[3]//4))


    #fenetre.blit(Q_MENU_ARROW)
    #fenetre.blit(D_MENU_ARROW)
    fenetre.blit(select_message_p1, (WINDOW_WIDTH//4 + 76 - select_message_p1_largeur//2 ,WINDOW_HEIGHT//2 +120))
    fenetre.blit(select_message_p2, (WINDOW_WIDTH - WINDOW_WIDTH//4 + 76 - 152 - select_message_p2_largeur//2,WINDOW_HEIGHT//2 +120))
    fenetre.blit(lock_message, (WINDOW_WIDTH//4 + 76 - lock_message_largeur//2 ,WINDOW_HEIGHT//2 +145))
    fenetre.blit(lock_message, (WINDOW_WIDTH - WINDOW_WIDTH//4 + 76 - 152 - lock_message_largeur//2, WINDOW_HEIGHT//2 +145))


    offset = SELECT_PLAYER.get_rect()
    fenetre.blit(SELECT_PLAYER, (WINDOW_WIDTH//2-offset[2]/2, (WINDOW_HEIGHT//6)))


    if p_1_chose and p_2_chose:
        fenetre.blit(message, ((WINDOW_WIDTH - messageLargeur) // 2,200))

    if p_1_cursor_state == player_2.color and p_2_chose:
        fenetre.blit(warning_p_1,((WINDOW_WIDTH - warnLargeur) // 2,200))

    if p_2_cursor_state == player_1.color and p_1_chose:
        fenetre.blit(warning_p_2,((WINDOW_WIDTH - warnLargeur) // 2,200))
#MENU DE DEPART
def start_menu():
    global menu_dino_pos, hauteur, music_up
    if music_up:
        JP_MEME.play()
        music_up = False
    for each in menu_dino_pos:
        each[0] += 4
        if each[0] > WINDOW_WIDTH:
            each[0] = 0
    draw_start_menu(menu_dino_pos[0],menu_dino_pos[1], menu_dino_pos[2],menu_dino_pos[3])

def draw_start_menu(g_pos, r_pos, b_pos, y_pos):
    fenetre.fill(GRIS)
    offset = START_MENU_P_QUEST.get_rect()
    fenetre.blit(START_MENU_P_QUEST, (WINDOW_WIDTH//2-offset[2]/2, (WINDOW_HEIGHT//6)))
    img = pygame.transform.scale(GROUND, (WINDOW_WIDTH, 64))
    fenetre.blit(img, [0,WINDOW_HEIGHT - GROUND_HEIGHT])
    fenetre.blit(level_animator(GREEN_WALK[1:], 'frame'), (g_pos))
    fenetre.blit(level_animator(RED_WALK[1:], 'frame'), (r_pos))
    fenetre.blit(level_animator(BLUE_WALK[1:], 'frame'), (b_pos))
    fenetre.blit(level_animator(YELLOW_WALK[1:], 'frame'), (y_pos))
    fenetre.blit(WOOD_STAND, [WINDOW_WIDTH//2-64,462])
    fenetre.blit(PASTIS, [WINDOW_WIDTH//2-20,406])
    fenetre.blit(start_message, (WINDOW_WIDTH//2 - start_largeur//2,WINDOW_HEIGHT//2.1))
#MENU PRINCIPAL
def draw_main_menu():
    global cursor
    fenetre.fill(GRIS)
    offset_main_menu = MAIN_MENU.get_rect()
    fenetre.blit(MAIN_MENU, (WINDOW_WIDTH//2-offset_main_menu[2]/2, (WINDOW_HEIGHT//6)))
    offset_play = PLAY.get_rect()
    fenetre.blit(PLAY, (WINDOW_WIDTH//2-offset_play[2]/2, (WINDOW_HEIGHT//6+offset_play[3]*4)))
    offset_lvl = NIVEAU.get_rect()
    fenetre.blit(NIVEAU, (WINDOW_WIDTH//2-offset_lvl[2]/2, (WINDOW_HEIGHT//6+offset_lvl[3]*6)))
    if cursor == 'select_menu':
        fenetre.blit(PASTIS, ((WINDOW_WIDTH//2-offset_play[2]/2-100), (WINDOW_HEIGHT//6+offset_play[3]*4)))

    if cursor == 'select_level':
        fenetre.blit(PASTIS, ((WINDOW_WIDTH//2-offset_lvl[2]/2-100), (WINDOW_HEIGHT//6+offset_lvl[3]*6)))
#ANIMATIONS DANS LES MENUS
def level_animator(img_list, anim_type):
    global anim_menu_dino, anim_menu_frame
    if anim_type == 'dino':
        anim_menu_dino += 0.1
        if anim_menu_dino >= len(img_list):
            anim_menu_dino = 0
        return img_list[int(anim_menu_dino)]

    if anim_type == 'frame':
        anim_menu_frame += 0.07
        if anim_menu_frame >= len(img_list):
            anim_menu_frame = 0
        return img_list[int(anim_menu_frame)]
#CHARGEMENT DU NIVEAU
def load_level(scene):
    global in_game, lvl, anim_speed, win
    fade()
    clear_all()
    anim_speed = 0.1
    win = False
    test_taux_alcool()
    lvl_generator(scene, lvl)
#AFFICHAGE QUAND PERDU
def draw_lose_screen():
    fenetre.fill(GRIS)
    
    lose_offset = LOSE.get_rect()
    fenetre.blit(LOSE, (WINDOW_WIDTH//2-lose_offset[2]//2, (WINDOW_HEIGHT//2-lose_offset[3]//2)))
    fenetre.blit(pygame.transform.scale(GROUND, (WINDOW_WIDTH + 64 , 64)), (-16, WINDOW_HEIGHT-GROUND_HEIGHT))

    message = police_caractere.render("Vous avez trop bu !", True, ORANGE)
    messageLargeur, messageHauteur = police_caractere.size("Vous avez trop bu !")
    fenetre.blit(message, (WINDOW_WIDTH//2-messageLargeur/2,WINDOW_HEIGHT-256))
#AFFICHAGE QUAND GAGNER
def draw_win_sceen():
    fenetre.fill(GRIS)
    
    win_offset = WIN.get_rect()
    fenetre.blit(WIN, (WINDOW_WIDTH//2-win_offset[2]//2, WINDOW_HEIGHT//2-win_offset[3]//2))
    fenetre.blit(pygame.transform.scale(GROUND, (WINDOW_WIDTH + 64 , 64)), (-16, WINDOW_HEIGHT-GROUND_HEIGHT))

    
# - GESTIONNAIRE MENU - #
#CREATION D'UN FONDU
def fade():
    fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade.fill((0,0,0))
    for alpha in range(0, 200):
        fade.set_alpha(alpha)
        display.blit(fade, (0,0))
        pygame.display.update()
#INVERSIONS DES TOUCHES DROITE ET GAUCHE
def button_swap_LR(): ###NOUVEAU###
    global GAUCHE,DROITE,D,Q
    GAUCHE = pygame.K_RIGHT
    DROITE = pygame.K_LEFT
    D = pygame.K_q
    Q = pygame.K_d
#INVERSION DES TOUCHES HAUT ET BAS
def button_swap_UD():
    global HAUT,BAS,Z,S
    HAUT = pygame.K_DOWN
    BAS = pygame.K_UP
    Z = pygame.K_s
    S = pygame.K_z
# REINITIALISE LES BOUTONS AU VALEURS DE DEFAUT
def reset_buttons():
    global GAUCHE,DROITE,D,Q,HAUT,BAS,Z,S
    GAUCHE = pygame.K_LEFT
    DROITE = pygame.K_RIGHT
    HAUT = pygame.K_UP
    BAS = pygame.K_DOWN
    Z = pygame.K_z
    Q = pygame.K_q
    S = pygame.K_s
    D = pygame.K_d
# TEST DU TAUX D'ALCOOL POUR APPLIQUER LEURS EFFETS
def test_taux_alcool():###NOUVEAU###
    global flip, taux_alcool, auto_rotate
    if taux_alcool > 60:
        flip = True 
    if taux_alcool > 45 and lvl == 7:
        auto_rotate = True
    else:
        auto_rotate = False
    if taux_alcool > 14:
        button_swap_LR()
    if taux_alcool > 45:
        button_swap_UD()
#VERIFIE SI LES PERSONNAGES ON SOIT TROP BU OU ON FINI TOUT LES NIVEAU
def death_or_win_check():
    global taux_alcool, death, win_game, actual_menu
    if taux_alcool >= 100:
        reset_to_start()
        death = True
        actual_menu = 'death'
        
    
    if lvl > 7:
        reset_to_start()
        win_game = True
        actual_menu = 'win'
    
#AFFICHAGE SOIT DU MENU DE VICTOIRE SOIT LE MENU DE DEFAITE

def show_end_menu():
    global death, win_game
    if death:
        draw_lose_screen()
    
    elif win_game :
        draw_win_sceen()
#REMETTRE TOUTES LES VALEURS IMPORTANTES A 0 POUR RELANCER UNE NOUVELLE PARTIE
def reset_to_start():
    global win_game, lvl, death, auto_rotate, taux_alcool,in_game, actual_menu, p_1_chose, p_2_chose, flip
    clear_all()
    auto_rotate = False
    taux_alcool = 0
    in_game = False
    p_1_chose = False
    p_2_chose = False
    flip = False
    reset_buttons()
        


# - IMAGES - #
PLAYER_1 = pygame.image.load("sprites/green_dino/walk_1.png").convert_alpha()
PLAYER_2 = pygame.image.load("sprites/block.png").convert_alpha()
GREEN_IDLE = create_anim_list('sprites/green_dino/', 'i' )
GREEN_WALK = create_anim_list('sprites/green_dino/', 'w' )
GREEN_IDLE_L = create_anim_list('sprites/green_dino/', 'i_l' )
GREEN_WALK_L = create_anim_list('sprites/green_dino/', 'w_l' )
GREEN_UI = [pygame.image.load("sprites/green_dino/dino_1.png").convert_alpha(), pygame.image.load("sprites/green_dino/dino_2.png").convert_alpha(), pygame.image.load("sprites/green_dino/dino_3.png").convert_alpha(), pygame.image.load("sprites/green_dino/dino_4.png").convert_alpha()]

RED_IDLE = create_anim_list('sprites/red_dino/', 'i' )
RED_WALK = create_anim_list('sprites/red_dino/', 'w' )
RED_IDLE_L = create_anim_list('sprites/red_dino/', 'i_l' )
RED_WALK_L = create_anim_list('sprites/red_dino/', 'w_l' )
RED_UI = [pygame.image.load("sprites/red_dino/dino_1.png").convert_alpha(), pygame.image.load("sprites/red_dino/dino_2.png").convert_alpha(), pygame.image.load("sprites/red_dino/dino_3.png").convert_alpha(), pygame.image.load("sprites/red_dino/dino_4.png").convert_alpha()]

BLUE_IDLE = create_anim_list('sprites/blue_dino/', 'i' )
BLUE_WALK = create_anim_list('sprites/blue_dino/', 'w' )
BLUE_IDLE_L = create_anim_list('sprites/blue_dino/', 'i_l' )
BLUE_WALK_L = create_anim_list('sprites/blue_dino/', 'w_l' )
BLUE_UI = [pygame.image.load("sprites/blue_dino/dino_1.png").convert_alpha(), pygame.image.load("sprites/blue_dino/dino_2.png").convert_alpha(), pygame.image.load("sprites/blue_dino/dino_3.png").convert_alpha(), pygame.image.load("sprites/blue_dino/dino_4.png").convert_alpha()]

YELLOW_IDLE = create_anim_list('sprites/yellow_dino/', 'i' )
YELLOW_WALK = create_anim_list('sprites/yellow_dino/', 'w' )
YELLOW_IDLE_L = create_anim_list('sprites/yellow_dino/', 'i_l' )
YELLOW_WALK_L = create_anim_list('sprites/yellow_dino/', 'w_l' )
YELLOW_UI = [pygame.image.load("sprites/yellow_dino/dino_1.png").convert_alpha(), pygame.image.load("sprites/yellow_dino/dino_2.png").convert_alpha(), pygame.image.load("sprites/yellow_dino/dino_3.png").convert_alpha(), pygame.image.load("sprites/yellow_dino/dino_4.png").convert_alpha()]

WHITE_STAND = pygame.image.load("sprites/stands/white_stand.png").convert_alpha()
RED_STAND = pygame.image.load("sprites/stands/red_stand.png").convert_alpha()
BLUE_STAND = pygame.image.load("sprites/stands/blue_stand.png").convert_alpha()
YELLOW_STAND = pygame.image.load("sprites/stands/yellow_stand.png").convert_alpha()
GREEN_STAND = pygame.image.load("sprites/stands/green_stand.png").convert_alpha()
WOOD_STAND = pygame.image.load("sprites/stands/all_stand.png").convert_alpha()
MOVING_STAND = pygame.image.load("sprites/stands/moving_stand.png").convert_alpha()
STAND_RAIL_V = pygame.image.load('sprites/stands/stand_rail_v.png')
STAND_RAIL_H = pygame.image.load('sprites/stands/stand_rail_h.png')
WHITE_WALL = pygame.image.load("sprites/walls/white_wall.png").convert_alpha()
RED_WALL =pygame.image.load("sprites/walls/red_wall.png").convert_alpha()
BLUE_WALL = pygame.image.load("sprites/walls/blue_wall.png").convert_alpha()
YELLOW_WALL =pygame.image.load("sprites/walls/yellow_wall.png").convert_alpha()
GREEN_WALL = pygame.image.load("sprites/walls/green_wall.png").convert_alpha()
WOOD_WALL = pygame.image.load("sprites/walls/wood_wall.png").convert_alpha()

PASTIS = pygame.image.load("sprites/pastis.png").convert_alpha()
GROUND = pygame.image.load("sprites/stands/stand_ground.png").convert_alpha()

P_1_CURSOR = pygame.image.load("sprites/cursors/cursor_p1.png").convert_alpha()
P_2_CURSOR = pygame.image.load("sprites/cursors/cursor_p2.png").convert_alpha()
P_1_FRAME = [pygame.image.load("sprites/menu_images/player_frame/p1_1.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_2.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_3.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_4.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_5.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_6.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_7.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p1_8.png").convert_alpha()]
P_2_FRAME = [pygame.image.load("sprites/menu_images/player_frame/p2_1.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_2.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_3.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_4.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_5.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_6.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_7.png").convert_alpha(),pygame.image.load("sprites/menu_images/player_frame/p2_8.png").convert_alpha()]
SELECT_PLAYER = pygame.image.load("sprites/menu_images/select_player.png").convert_alpha()
START_MENU_P_QUEST = pygame.image.load("sprites/menu_images/pastis_quest.png").convert_alpha()
LOSE = pygame.image.load("sprites/menu_images/perdu.png").convert_alpha()
WIN = pygame.image.load("sprites/menu_images/victoire.png").convert_alpha()
MAIN_MENU = pygame.image.load("sprites/menu_images/main_menu.png").convert_alpha()
PLAY = pygame.image.load("sprites/menu_images/play.png").convert_alpha()
NIVEAU = pygame.image.load("sprites/menu_images/niveaux.png").convert_alpha()
SHADOW = pygame.image.load("sprites/shadow_2.png").convert_alpha()
UI_COLOR_LIST = [GREEN_UI, RED_UI, BLUE_UI, YELLOW_UI]
LEFT_MENU_ARROW = pygame.image.load("sprites/menu_images/arrow/left_arrow.png").convert_alpha()
RIGHT_MENU_ARROW = pygame.image.load("sprites/menu_images/arrow/right_arrow.png").convert_alpha()
Q_MENU_ARROW = pygame.image.load("sprites/menu_images/arrow/q_arrow.png").convert_alpha()
D_MENU_ARROW = pygame.image.load("sprites/menu_images/arrow/d_arrow.png").convert_alpha()

BUTTON = create_anim_list('sprites/buttons/', 'b')
RED_LEVER = create_anim_list('sprites/lever/red/', 'l' ) 
GREEN_LEVER = create_anim_list('sprites/lever/green/', 'l' )
YELLOW_LEVER = create_anim_list('sprites/lever/yellow/', 'l' )
BLUE_LEVER = create_anim_list('sprites/lever/blue/', 'l' )
V_SIGN = pygame.image.load('sprites/v_sign.png')

LVL_1_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_1.PNG'),(800,533))
LVL_2_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_2.PNG'),(800,533))
LVL_3_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_3.PNG'),(800,533))
LVL_4_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_4.PNG'),(800,533))
LVL_5_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_5.PNG'),(800,533))
LVL_6_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_6.PNG'),(800,533))
LVL_7_SCREEN =  pygame.transform.scale(pygame.image.load('capture/Capture_LVL_7.PNG'),(800,533))

# - IMAGES - #
# - SONS - #
JUMP_SOUND = pygame.mixer.Sound('sound/jump.wav')
JP_MEME = pygame.mixer.Sound('sound/JP_MEME.wav')

# - NIVEAU - #
# CREATION DES NIVEAUX #
def lvl_generator(scene, lvl):
    global objects_to_add, auto_rotate
    if lvl == 1:
        add_players()

        create_stand(stand_list, [WINDOW_WIDTH//2-256,300])
        create_stand(stand_list, [WINDOW_WIDTH//2+128,300])
        create_stand(stand_list, [WINDOW_WIDTH//2-256,450])
        create_stand(stand_list, [WINDOW_WIDTH//2+128,450])

        reset_player(vect(300,WINDOW_HEIGHT -GROUND_HEIGHT-1), vect(600,WINDOW_HEIGHT -GROUND_HEIGHT-1))

        create_past(past_list, [WINDOW_WIDTH//2-16, 88])#[450),100)]
        create_stand(stand_list, [WINDOW_WIDTH//2-64,144],None)
        create_ground(ground_list, [int((-WINDOW_WIDTH/1080)*32),WINDOW_HEIGHT - GROUND_HEIGHT])

    if lvl == 2:
        create_stand(stand_list, [384,462])
        create_stand(stand_list, [736,256])
        create_stand(stand_list, [864,462])
        create_stand(stand_list, [0,256])
        create_stand(stand_list, [128,256])

        reset_player(vect(100,WINDOW_HEIGHT -GROUND_HEIGHT-1),vect(600,WINDOW_HEIGHT -GROUND_HEIGHT-1))
        add_players()

        create_past(past_list, [108,200])
        create_ground(ground_list, [-32,WINDOW_HEIGHT - GROUND_HEIGHT])
        create_wall(wall_list, [224,0], None)
    
    if lvl == 3:
        reset_player(vect(10, WINDOW_HEIGHT - GROUND_HEIGHT-70 ),vect(WINDOW_WIDTH - player_2.rect[3] ,WINDOW_HEIGHT - GROUND_HEIGHT-70))
        create_button(button_list, [32, WINDOW_HEIGHT - 465-64])
        add_players()

        create_stand(stand_list, [WINDOW_WIDTH//4,425]) #SOL COLOR
        create_stand(stand_list, [WINDOW_WIDTH//4 + WINDOW_WIDTH//2 - 64,450]) #SOL COLOR
        create_stand(stand_list, [0,WINDOW_HEIGHT - GROUND_HEIGHT], None) #SOL GAUCHE
        create_stand(stand_list, [0,WINDOW_HEIGHT - 465], None) #SOL GAUCHE


        create_stand(stand_list, [WINDOW_WIDTH - 128,WINDOW_HEIGHT - GROUND_HEIGHT], None) #SOL DROIT

        create_wall(wall_list, [WINDOW_WIDTH-126, 0], None)
        create_stand(stand_list, [WINDOW_WIDTH - 128,256], None)

        create_past(past_list, [WINDOW_WIDTH - 64,200])

    if lvl == 4:
        reset_player(vect(WINDOW_WIDTH//2-32, 56 ),vect(WINDOW_WIDTH - player_2.rect[3] ,WINDOW_HEIGHT - GROUND_HEIGHT-70))
        create_button(button_list, [WINDOW_WIDTH//2-32, 64])


        create_stand(stand_list, [WINDOW_WIDTH-512,WINDOW_HEIGHT-32], None, player_1) #SOL COLOR
        create_stand(stand_list, [WINDOW_WIDTH-128,WINDOW_HEIGHT-32], None, player_1) #SOL COLOR
        create_stand(stand_list, [WINDOW_WIDTH-768,WINDOW_HEIGHT -196])
        create_stand(stand_list, [WINDOW_WIDTH//2-64,128], None) #SOL GAUCHE
        create_stand(stand_list, [WINDOW_WIDTH-320, 256])
        create_stand(stand_list, [0, WINDOW_HEIGHT-32], None)
        create_stand(stand_list, [0, WINDOW_HEIGHT-240])
        create_stand(stand_list, [0, WINDOW_HEIGHT-464])
        create_stand(stand_list, [WINDOW_WIDTH//2-224,128], None)

        create_lever(lever_list, [WINDOW_WIDTH//2-192, 64], player_2)


        create_wall(wall_list, [WINDOW_WIDTH//2-96, -96], None)
        create_wall(wall_list, [WINDOW_WIDTH//2+64, -96], None, None, True)
        create_wall(wall_list, [WINDOW_WIDTH-272, WINDOW_HEIGHT-320], None, player_1)
        create_stand(stand_list, [WINDOW_WIDTH - 128,128], None)
        create_wall(wall_list, [-16, -256], None)
        create_wall(wall_list, [-16, 0], None)
        create_wall(wall_list, [-16, 256], None)
        create_wall(wall_list, [-16, 512], None)

        create_wall(wall_list, [WINDOW_WIDTH-16, 0], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 256], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 512], None)

        create_past(past_list, [WINDOW_WIDTH - 64,72])
    
    if lvl == 5:
        reset_player(vect(WINDOW_WIDTH - 128,300),vect(WINDOW_WIDTH - 72,300))
        
        create_wall(wall_list, [WINDOW_WIDTH-16, 0], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 256], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 512], None)
        create_wall(wall_list, [-16, -256], None)
        create_wall(wall_list, [-16, 0], None)
        create_wall(wall_list, [-16, 256], None)
        create_wall(wall_list, [-16, 512], None)
        create_stand(stand_list, [128, 296], None) 
        create_button(button_list, [160, 224])
        create_wall(wall_list, [256,32])

        create_stand(stand_list, [WINDOW_WIDTH//2,WINDOW_HEIGHT-32], None)
        create_wall(wall_list, [WINDOW_WIDTH//2+128, WINDOW_HEIGHT-256], None)
        create_wall(wall_list, [WINDOW_WIDTH//2-32, WINDOW_HEIGHT-256], None)
        create_stand(stand_list, [WINDOW_WIDTH//2,WINDOW_HEIGHT-256])
        create_past(past_list, [WINDOW_WIDTH//2+48, WINDOW_HEIGHT-88])

        create_stand(stand_list, [WINDOW_WIDTH - 128,384], None)

        create_stand(stand_list, [WINDOW_WIDTH-256, 256])

        create_stand(stand_list, [WINDOW_WIDTH-512, 196])
        create_stand(stand_list, [16, 512])
        create_stand(stand_list, [256, WINDOW_HEIGHT-32], None)

    if lvl == 6:
        reset_player(vect(WINDOW_WIDTH-96,WINDOW_HEIGHT-96),vect(WINDOW_WIDTH-96,32))

        moving_stand(stand_list, rail_list, [WINDOW_WIDTH-128,96],  'upway')
        create_stand(stand_list, [WINDOW_WIDTH-128, WINDOW_HEIGHT-32], None)
        create_wall(wall_list, [WINDOW_WIDTH-156, 176], None)
        create_button(button_list, [WINDOW_WIDTH-96, WINDOW_HEIGHT-96])
        create_wall(wall_list, [WINDOW_WIDTH-156, WINDOW_HEIGHT-288], None, None, True)
        create_wall(wall_list, [WINDOW_WIDTH//2+256, 0],None)

        create_stand(stand_list, [WINDOW_WIDTH-284, WINDOW_HEIGHT-32], None)
        create_stand(stand_list, [WINDOW_WIDTH-284, WINDOW_HEIGHT-196], None, player_2)
        create_stand(stand_list, [WINDOW_WIDTH-284, WINDOW_HEIGHT-464], None, player_1)

        moving_stand(stand_list, rail_list, [348,WINDOW_HEIGHT-32],  'sideway')
        create_wall(wall_list, [256, WINDOW_HEIGHT - 320], None, player_1)
        create_stand(stand_list, [128, WINDOW_HEIGHT-64], None, player_1)
        moving_stand(stand_list, rail_list, [128, 256], 'upway')

        create_stand(stand_list, [388, 196], None, player_1)
        create_stand(stand_list, [516, 196], None)
        create_stand(stand_list, [644, 196], None)
        create_past(past_list, [688, 138])
        create_stand(stand_list, [516, WINDOW_HEIGHT/2])
        create_wall(wall_list, [356, 0], None, player_1)
        create_lever(lever_list, [516, 128], player_2)

        
        
    if lvl == 7:
        reset_player(vect(32,WINDOW_HEIGHT-192),vect(32,WINDOW_HEIGHT-192))
        create_wall(wall_list, [-16, 0], None)
        create_wall(wall_list, [-16, 256], None)
        create_wall(wall_list, [-16, 512], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 0], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 256], None)
        create_wall(wall_list, [WINDOW_WIDTH-16, 512], None)
        create_stand(stand_list, [0,WINDOW_HEIGHT-96], None)
        create_wall(wall_list, [256, WINDOW_HEIGHT-256], None)
        create_wall(wall_list, [400, WINDOW_HEIGHT-384], None)
        create_wall(wall_list, [544, WINDOW_HEIGHT-288], None, player_1)
        create_wall(wall_list, [544, WINDOW_HEIGHT-128], None)
        create_wall(wall_list, [544, 196], None)
        create_wall(wall_list, [544, 0], None)
        create_wall(wall_list, [688, WINDOW_HEIGHT-256], None)
        create_button(button_list, [800, 256])
        create_wall(wall_list, [WINDOW_WIDTH-160, 256], None, player_2)
        create_wall(wall_list, [WINDOW_WIDTH-160, WINDOW_HEIGHT-288], None)
        create_wall(wall_list, [WINDOW_WIDTH-160, 0], None)

        create_stand(stand_list, [WINDOW_WIDTH-128, WINDOW_HEIGHT-32], None)
        create_past(past_list, [WINDOW_WIDTH-80,WINDOW_HEIGHT-96 ])

        auto_rotate=True
       
        
    add_players()

    for objects in objects_to_add:
        ajouteEntite(scene, objects)
    
# - NIVEAU - #


# Initialisation

horloge = pygame.time.Clock()

objects_to_add = []

stand_list =  pygame.sprite.Group()
player_list = pygame.sprite.Group()
past_list =   pygame.sprite.Group()
ground_list = pygame.sprite.Group()
button_list = pygame.sprite.Group()
wall_list =   pygame.sprite.Group()
lever_list =  pygame.sprite.Group()
rail_list = pygame.sprite.Group()

color_list = ['green','red','blue','yellow']
p1_i = 0
p2_i = 0

anim_speed = 0.1

player_1 = create_player(player_list, [300,WINDOW_HEIGHT -GROUND_HEIGHT-1], 'green')
player_2 = create_player(player_list, [600,WINDOW_HEIGHT -GROUND_HEIGHT-1], 'red')

scene = pygame.sprite.Group()

wait_dist = 0
tmps_avant = 0

anim_menu_dino = 0
anim_menu_frame = 0
p_1_cursor_pos = (WINDOW_WIDTH//5-16, WINDOW_HEIGHT// 2+100)
p_1_cursor_state = color_list[p1_i]
p_1_chose = False
p_2_cursor_pos = (WINDOW_WIDTH//5-16, WINDOW_HEIGHT// 2-100)
p_2_cursor_state = color_list[p2_i]
p_2_chose = False
cursor = 'select_menu'
hauteur = WINDOW_HEIGHT - GROUND_HEIGHT - 72
menu_dino_pos = [[0 - wait_dist ,hauteur], [-128- wait_dist ,hauteur], [-256 - wait_dist ,hauteur],[-384 - wait_dist ,hauteur]]

win = False
win_game = False
death = False
can_press = False
lever_can_press = False
music_up = True
move_left = False
move_right = True
move_up = False
move_down = True
lever_activated = False


police_caractere = pygame.font.Font('font/upheavtt.ttf', 32)
message = police_caractere.render("Appuyez sur V pour confirmé le choix de vos personnages", True, ORANGE)
warning_p_1 = police_caractere.render("Le joueur 2 à déjà chosi ce personnage", True, ORANGE)
warning_p_2 = police_caractere.render("Le joueur 1 à déjà chosi ce personnage", True, ORANGE)
win_message = police_caractere.render("Appuyez sur V pour changer de niveau", True, ORANGE)
start_message = police_caractere.render("Appuyer sur ESPACE pour démarrer", True, ORANGE)
select_message_p1 = police_caractere.render("Espace pour" , True, ORANGE)
select_message_p2 = police_caractere.render("Enter pour" , True, ORANGE)
lock_message = police_caractere.render("verrouiller" , True, ORANGE)
win_messageLargeur, win_messageHauteur = police_caractere.size("Appuyez sur V pour changer de niveau")
select_message_p1_largeur , select_message_p1_hauteur = police_caractere.size("Espace pour")
select_message_p2_largeur , select_message_p2_hauteur = police_caractere.size("Enter pour")
lock_message_largeur , lock_message_hauteur = police_caractere.size("verrouiller")
messageLargeur, messageHauteur = police_caractere.size("Appuyez sur V pour confirmé le choix de vos personnages")
warnLargeur, warnHauteur = police_caractere.size("Le joueur 2 à déjà chosi ce personnage")
win_largeur, win_hauteur = police_caractere.size("Appuyez sur V pour confirmé le choix de vos personnages")
start_largeur, start_hauteur =  police_caractere.size("Appuyer sur ESPACE pour démarrer")
actual_menu = 'start_screen'

lvl = 1
selected_level = 1
in_game = False
taux_alcool = 0
flip = False
forced_flip = False
auto_rotate = False

load_level(scene)
#BOUCLE PRINCIPALE
while True:
    if not in_game:
        if actual_menu == 'start_screen':
            start_menu()
        elif actual_menu == 'main_menu':
            draw_main_menu()
        elif actual_menu == 'select_menu':
            draw_player_selector()
        
        elif actual_menu == 'select_level':
            draw_level_selector(selected_level)


        menu_input()

    if in_game:

        fenetre.fill(GRIS)
        animator()
        move_player()
        moving_plateforme()

        update_rect_pos(scene)

        temps_maintenant = pygame.time.get_ticks()
        collider()
        affiche(scene, fenetre)
        affiche_hud(fenetre)
        if flip:
            fenetre = pygame.transform.rotate(fenetre, 180)
        if auto_rotate:
            tmps_avant += horloge.get_time()
            print(tmps_avant)
            if tmps_avant > 2000:
                fade()
                if not flip:
                    flip = True
                elif flip:
                    flip = False
                tmps_avant = 0
                print(flip)
        
        death_or_win_check()
    if death or win_game:
        show_end_menu()

    print(actual_menu)
           

    
    #AFFICHAGE D'UNE SURFACE DE LA TAILLE DEMANDEE (PEUT IMPORTE LA TAILLE)

    tmp = pygame.transform.scale(fenetre,(ACTUAL_WINDOW_WIDTH,ACTUAL_WINDOW_HEIGHT))

    display.blit(tmp,(0,0))    
    
    pygame.display.flip()


    horloge.tick(images_par_seconde)
