import math
import random
import time
import pygame
import sys

#############################################
# Classe Player                             #
#############################################

class Player:
    def __init__(self, x, y, width, height, screen, flying=False):
        self.width, self.height = width, height
        self.rect = pygame.Rect(x, y, width/2, height/2) # hitbox du joueur 
        self.imagebox = pygame.Rect(x, y, width, height) # box de l'image du joueur
        self.speed = 5
        self.sprint_speed = 10
        self.is_sprinting = False
        self.flying = flying
        self.screen = screen
        self.index = 0
        self.orientation = 1 # 1 = droite, -1 = gauche
        self.jump = False
        self.jump_count = 10 # nombre de frames pendant lesquelles le joueur saute
        self.charging_attack = False
        self.attack = False
        self.attack_count = 10 # nombre de frames pendant lesquelles le joueur charge son attaque
        self.hole = None
        self.animation_delay = 200 # délai entre chaque frame de l'animation
        self.last_animation_time = pygame.time.get_ticks() # temps de la dernière frame de l'animation

        # Chargez les images du joueur
        if self.flying:
            self.player_images = [pygame.image.load(f"images/jetpack{i}.png") for i in range(1, 4)] # images de l'animation du joueur en vol
        else:
            self.player_images = [pygame.image.load(f"images/walk{i}.png") for i in range(1, 5)] # images de l'animation du joueur au sol
        self.images = [pygame.transform.scale(image, (self.width, self.height)) for image in self.player_images] # images redimensionnées
        self.image = pygame.image.load("images/walk1.png") # image par défaut

        # Chargez la musique du jeu
        pygame.mixer.music.load("sounds/spaceship_music.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
        self.step_noise = pygame.mixer.Sound("sounds/step.mp3")

    # Déplacez le joueur en fonction des touches appuyées
    def move(self, keys):
        if keys[pygame.K_LEFT]:
            # Utilisez la vitesse de sprint si le joueur sprinte
            speed = self.sprint_speed if self.is_sprinting else self.speed
            self.rect.x -= speed
            self.orientation = -1
            self.step_noise.play()
        if keys[pygame.K_RIGHT]:
            # Utilisez la vitesse de sprint si le joueur sprinte
            speed = self.sprint_speed if self.is_sprinting else self.speed
            self.rect.x += speed
            self.orientation = 1
            self.step_noise.play()

    # Gère le sprint
    def hanle_sprint(self, keys):
        if keys[pygame.K_LSHIFT]:
            self.is_sprinting = True
            self.animation_delay = 100
        else:
            self.is_sprinting = False
            self.animation_delay = 200

    # Gère le saut
    def handle_jump(self, keys, gravity=True):
        # Dans le monde sans gravité
        if not gravity:
            if keys[pygame.K_UP]:
                self.rect.y -= 5
                self.imagebox.y -= 5
            if keys[pygame.K_DOWN]:
                self.rect.y += 5
                self.imagebox.y += 5

        else:
            if not self.jump and self.jump_count == 11:
                if keys[pygame.K_SPACE]:
                    self.jump = True

            else:
                # si le joueur est en train de monter
                if self.jump_count >= -10:
                    neg = 1
                    if self.jump_count < 0:
                        neg = -1
                    self.rect.y -= (self.jump_count ** 2) * 0.5 * neg
                    self.imagebox.y -= (self.jump_count ** 2) * 0.5 * neg
                    self.jump_count -= 1
                # si le joueur est en train de descendre
                else:
                    self.jump = False
                    self.jump_count = 11

    # Gère l'attaque
    def handle_attack(self, keys):
        if not self.charging_attack and self.attack_count == 10:
            if keys[pygame.K_z]:
                self.charging_attack = True
                self.shoot()

        else:
            # si le joueur est en train de charger son attaque
            if self.attack_count >= -10:
                self.attack_count -= 1
            # si le joueur lance son attaque
            elif self.attack_count >= -30:
                self.charging_attack = False
                self.attack = True
                self.attack_count -= 1
                self.shoot()
            # si le joueur a fini son attaque
            else:
                self.charging_attack = False
                self.attack = False
                self.attack_count = 10

    # Applique la gravité au joueur
    def apply_gravity(self, gravity):
        self.rect.y += gravity

    # Gère l'animation de shoot du joueur
    def shoot(self):
        # Son de shoot
        shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
        pygame.mixer.Sound.set_volume(shoot_sound, 0.5)
        shoot_sound.play()

        if self.charging_attack:
            # Faire apparaître le trou noir au-dessus lui
            self.hole = Hole(self.imagebox.x, self.imagebox.y - self.imagebox.height, self.orientation)
            self.hole_timer = 10  # Durée de vie du trou noir
        elif self.attack:
            # Faire apparaître le trou noir devant lui
            self.hole = Hole(self.imagebox.x + self.imagebox.width * self.orientation, self.imagebox.y, self.orientation)
            self.hole_timer = 200  # Durée de vie du trou noir

    # Gère l'animation du joueur
    def update_animation(self, keys):
        current_time = pygame.time.get_ticks()

        # Si le joueur est en vol, utiliser les images avec le jetpack
        if self.flying:

            if self.attack:
                self.image = pygame.image.load("images/jetpackattack.png")
                self.index = -1

            elif self.charging_attack:
                self.image = pygame.image.load("images/jetpackcharging.png")
                self.index = -1

            # Si le joueur ne bouge pas ou se déplace, avancer dans l'animation
            else:
                self.index = (self.index + 1) % len(self.images)

            # Si le trou noir existe, l'afficher
            if self.hole is not None:
                self.screen.blit(self.hole.image, (self.hole.rect.x, self.hole.rect.y))

        # Si le joueur est au sol, utiliser les images de marche
        else:
            
            if self.jump:
                self.image = pygame.image.load("images/jump.png")
                self.index = -1

            elif self.attack:
                self.image = pygame.image.load("images/attack.png")
                self.index = -1

            elif self.charging_attack:
                self.image = pygame.image.load("images/charging.png")
                self.index = -1

            elif current_time - self.last_animation_time > self.animation_delay:
                keys = pygame.key.get_pressed()

                # Si le joueur se déplace, avancer dans l'animation
                if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                    self.index = (self.index + 1) % len(self.images)
                else:
                    self.index = 0

                self.last_animation_time = current_time

        # Si le trou noir existe, l'afficher
        if self.hole is not None:
            if self.charging_attack:
                # Le trou noir apparaît au-dessus du joueur et se déplace avec lui
                self.hole.rect.x = self.imagebox.x
                self.hole.rect.y = self.imagebox.y - self.imagebox.height
            self.hole.move()
            self.hole_timer -= 1
            if self.hole_timer <= 0:
                # Le trou noir disparaît
                self.hole = None

    # Dessine le joueur
    def draw(self, surface):
        # Lie l'image à la hitbox et l'aligne en bas
        self.imagebox.midbottom = self.rect.midbottom

        # Si le joueur est animé, afficher l'image correspondante
        if self.index >= 0:
            image = self.images[self.index]
            if self.orientation == -1:
                image = pygame.transform.flip(image, True, False)
            surface.blit(image, (self.imagebox.x, self.imagebox.y))

        # Sinon, afficher l'image définie
        else:
            image = pygame.transform.scale(self.image, (self.width, self.height))
            if self.orientation == -1:
                image = pygame.transform.flip(image, True, False)
            surface.blit(image, (self.imagebox.x, self.imagebox.y))


#############################################
# Classe Projectile                         #
#############################################

class Projectile:
    def __init__(self, surface, y, screen_width):
        if random.randint(0, 1) == 1:
            self.x = -80
            self.orientation = 1
        else:
            self.x = screen_width + 80
            self.orientation = -1
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 60, 60)
        self.image = pygame.image.load("images/asteroid.png")
        self.image = pygame.transform.scale(self.image, (80, 60))
        self.screen_width = screen_width
        if self.orientation == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        surface.blit(self.image, (self.x, self.y))

    # Dessine le projectile
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    # Déplace le projectile
    def move(self):
        self.rect.x += 5 * self.orientation
        self.x += 5 * self.orientation
        if self.orientation == 1 and self.x > self.screen_width:
            return False
        elif self.orientation == -1 and self.x + 85 < 0:
            return False
        else:
            return True

#############################################
# Classe Meteor                             #
#############################################

class Meteor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/meteor.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = pygame.Rect(self.x, self.y, 50, 50)

    # Dessine le météore
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

#############################################
# Classe FinishItem                         #
#############################################

class FinishItem:
    def __init__(self, x, y, image_source, width, height):
        self.x = x
        self.y = y
        self.image = pygame.image.load(f"images/{image_source}.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = pygame.Rect(self.x, self.y, width, height)

    # Dessine l'item de fin
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

#############################################
# Classe Platform                           #
#############################################

class Platform:
    def __init__(self, x, y, width, height, texture_image):
        self.rect = pygame.Rect(x, y, width, height)
        self.texture = pygame.transform.scale(texture_image, (width, height))
        self.y = y
        self.x = x

    # Dessine la plateforme
    def draw(self, surface):
        surface.blit(self.texture, (self.rect.x, self.rect.y))

#############################################
# Classe Portal                             #
#############################################

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, destination, text):
        super().__init__()
        self.image = pygame.image.load("images/open_portal.png")
        self.image = pygame.transform.scale(self.image, (100, 100))  # Redimensionnez l'image à 100x100
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.destination = destination
        self.text = text

    # Dessine le portail
    def teleport(self, player, game):
        text_display = Text(30, (255, 255, 255))
        text_display.display(game, self.text, (self.rect.x, self.rect.y - 20))
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            if self.text == 'E - Niveau 1':
                self.level1 = Level1()
                result = self.level1.run()
                if result == 'finished':
                    return 0  # Retourne l'indice du portail à afficher (voir le tableau créé dans la classe Game pour les index)
                pygame.display.flip()
            elif self.text == 'E - Niveau 2':
                self.level2 = Level2()
                result = self.level2.run()
                if result == 'finished':
                    return 2
                pygame.display.flip()
            elif self.text == 'E - Niveau 3':
                self.level3 = Level3()
                result = self.level3.run()
                if result == 'finished':
                    return 'game_finished'
                pygame.display.flip()
        return None

#############################################
# Classe Text                               #
#############################################

class Text:
    def __init__(self, font_size, font_color):
        dialogue_font = pygame.font.SysFont('arial', 30)
        self.font = dialogue_font
        self.color = font_color

    # Affiche le texte
    def display(self, surface, text, position):
        text_render = self.font.render(text, True, self.color)
        surface.blit(text_render, position)

#############################################
# Classe Hole                               #
#############################################

class Hole:
    def __init__(self, x, y, direction):
        self.image = pygame.transform.scale(pygame.image.load("images/hole.png"), (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.speed = 5
        self.direction = direction

    # Déplace le trou noir 
    def move(self):
        self.rect.x += self.speed * self.direction
        self.speed += 1

#############################################
# Classe Timer                              #
#############################################

class Timer:
    def __init__(self, max):
        self.max = max * 1000  # Temps récupéré via max en secondes converti en millisecondes
        self.start = pygame.time.get_ticks()

    # Renvoie le temps écoulé
    def elapsed(self):
        if pygame.time.get_ticks() >= self.start + self.max:
            return 'Temps écoulé'
        return math.floor((pygame.time.get_ticks() - self.start) / 1000)

###################################################
# Classe Level 1                                  #
###################################################

class Level1:
    def __init__(self):
        pygame.init()
        self.projectiles = []
        self.background = pygame.image.load("images/background_space.png")
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.player = Player(600, 300, 100, 100, self.screen, True)
        self.meteors = [
            Meteor(random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT)),
            Meteor(random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT)),
            Meteor(random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT)),
            Meteor(random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT))
        ]
        self.timer = Timer(60)
        self.text_display = Text(50, (255, 255, 255))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.finished = False
        self.finishItem = FinishItem(self.screen.get_width() / 2 - 50, 50, 'propulseur', 100, 50)
        self.itemCaught = False

    # Gère les évènements
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # Dessine les éléments
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.player.draw(self.screen)

        for meteor in self.meteors:
            meteor.draw(self.screen)
        if self.projectiles:
            for projectile in self.projectiles:
                projectile.draw(self.screen)
        if self.finished:
            self.finishItem.draw(self.screen)

        pygame.display.flip()

    # Met à jour les éléments
    def update(self):
        self.handle_events()

    # Gère le game over
    def handle_game_over(self):
        # Vérifie si le joueur est tombé trop bas
        if self.player.rect.y < 0:
            self.player.rect.x = self.player.rect.x
            self.player.rect.y = 0

        if self.player.rect.x > self.WIDTH:
            self.player.rect.x = self.WIDTH - self.player.rect.width
            self.player.rect.y = self.player.rect.y

        if self.player.rect.x < 0:
            self.player.rect.x = 0
            self.player.rect.y = self.player.rect.y
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            return True
        if self.player.rect.y > self.WIDTH:
            return True
        else:
            return False

    # Vérifie les collisions
    def check_collisions(self):
        if self.projectiles:
            for projectile in self.projectiles:
                if projectile.rect.colliderect(self.player):
                    self.player.index = -1
                    pygame.mixer.Sound("sounds/death.mp3").play()
                    self.player.image = pygame.image.load("images/jetpackdead1.png")
                    self.draw()
                    time.sleep(0.5)
                    self.player.image = pygame.image.load("images/jetpackdead2.png")
                    self.draw()
                    time.sleep(1)
                    self.game_over = True
                    return
        for meteor in self.meteors:
            if meteor and self.player.rect.colliderect(meteor):
                if meteor.y <= self.player.rect.y + self.player.height <= meteor.y + meteor.rect.height:
                    self.player.rect.y = meteor.y - self.player.rect.height
                elif self.player.rect.x <= meteor.x >= self.player.rect.x - self.player.width - 50:
                    self.player.rect.x = meteor.x - self.player.rect.width
                elif meteor.x <= self.player.rect.x:
                    self.player.rect.x = meteor.x + meteor.rect.width
            if self.projectiles:
                for projectile in self.projectiles:
                    if projectile.rect.colliderect(meteor):
                        self.projectiles.remove(projectile)
                        projectile = None

        if self.player.hole:
            if self.projectiles:
                for projectile in self.projectiles:
                    if projectile.rect.colliderect(self.player.hole):
                        self.projectiles.remove(projectile)
                        projectile = None

        if self.projectiles:
            for projectile in self.projectiles:
                if projectile.rect.colliderect(self.player):
                    self.player.index = -1
                    pygame.mixer.Sound("sounds/death.mp3").play()
                    self.player.image = pygame.image.load("images/dead1.png")
                    self.draw()
                    time.sleep(0.5)
                    self.player.image = pygame.image.load("images/dead2.png")
                    self.draw()
                    time.sleep(1)
                    self.game_over = True
                    return
        if self.finished:
            for projectile in self.projectiles:
                self.projectiles.remove(projectile)
                projectile = None
            if self.player.rect.colliderect(self.finishItem.rect):
                text_finish = Text(50, (255, 255, 255))
                pygame.mixer.Sound("sounds/collected_item.mp3").play()
                text_finish.display(self.screen, 'Bravo, vous avez récupéré un propulseur !', (100, 50))
                pygame.display.flip()
                time.sleep(2)
                self.itemCaught = True
    def run(self):
        self.player.flying = True
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.draw()
            self.update()
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.hanle_sprint(keys)
            self.player.handle_jump(keys, False)
            self.player.handle_attack(keys)
            self.player.apply_gravity(0)
            self.player.update_animation(keys)
            if not self.finished:
                if random.randint(0, 30) == 0:
                    height = random.randint(0, self.HEIGHT)
                    while height in range(self.player.rect.y - 250, self.player.rect.y + 350):
                        height = random.randint(0, self.HEIGHT)
                    self.projectiles.append(Projectile(self.screen, random.randint(0, self.HEIGHT), self.WIDTH))
                if self.projectiles:
                    for projectile in self.projectiles:
                        result = projectile.move()
                        if not result:
                            self.projectiles.remove(projectile)
                            projectile = None
            self.game_over = self.handle_game_over()
            self.check_collisions()
            if self.game_over:
                self.running = False
                return 'game_over'
            self.elapsed = self.timer.elapsed()
            if self.elapsed == "Temps écoulé":
                self.finished = True
            self.text_display.display(self.screen, 'Survivez 60 secondes pour récupérer la pièce', (50, 50))
            self.text_display.display(self.screen, str(self.elapsed), (50, 100))
            pygame.display.flip()
            if self.itemCaught:
                self.running = False
                return 'finished'

###################################################
# Classe Level 2                                  #
###################################################

class Level2:
    def __init__(self):
        pygame.init()
        self.game_over = False
        self.projectiles = []
        self.background = pygame.image.load("images/black_hole.jpg")
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.finishItem = FinishItem(self.screen.get_width() / 2 - 50, 50, 'fuel', 75, 75)
        self.player = Player(100, 100, 100, 100, self.screen, True)
        self.screen.fill("black")
        self.text_display = Text(50, (255, 255, 255))
        self.clock = pygame.time.Clock()
        self.running = True
        self.gravity_vector = pygame.Vector2(self.WIDTH // 2, self.HEIGHT // 2)
        self.itemCaught = False
        self.black_hole_position = pygame.Vector2(self.WIDTH // 2, self.HEIGHT // 2)
        self.finished = False
        # Distance limite pour la détection du trou noir
        self.black_hole_limit = 80
        self.timer = Timer(60)
        self.text_display = Text(50, (255, 255, 255))

    # Vérifie les collisions
    def check_collisions(self):
        if self.player.rect.y < 0:
            self.player.rect.x = self.player.rect.x
            self.player.rect.y = 0

        if self.player.rect.x > self.WIDTH:
            self.player.rect.x = self.WIDTH - self.player.rect.width
            self.player.rect.y = self.player.rect.y

        if self.player.rect.x < 0:
            self.player.rect.x = 0
            self.player.rect.y = self.player.rect.y

        if self.player.hole:
            if self.projectiles:
                for projectile in self.projectiles:
                    if projectile.rect.colliderect(self.player.hole):
                        self.projectiles.remove(projectile)
                        projectile = None

        if self.projectiles:
            for projectile in self.projectiles:

                if projectile.rect.colliderect(self.player):
                    self.player.index = -1
                    pygame.mixer.Sound("sounds/death.mp3").play()
                    self.player.image = pygame.image.load("images/jetpackdead1.png")
                    self.draw()
                    time.sleep(0.5)
                    self.player.image = pygame.image.load("images/jetpackdead2.png")
                    self.draw()
                    time.sleep(1)
                    self.game_over = True
                    return

    # Gère les évènements
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # Dessine les éléments
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.player.draw(self.screen)
        if self.finished:
            self.finishItem.draw(self.screen)
        if self.projectiles:
            for projectile in self.projectiles:
                projectile.draw(self.screen)
        if self.finished:
            self.finishItem.draw(self.screen)
        pygame.display.flip()

    # Met à jour les éléments
    def update(self):
        self.handle_events()

    # Gère le game over
    def handle_game_over(self):
        # Vérifie si le joueur est tombé trop bas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            return True
        if self.player.rect.x > self.WIDTH:
            return True

        player_center = pygame.Vector2(self.player.rect.center)
        distance_to_black_hole = player_center.distance_to(self.black_hole_position)

        # Si la distance est inférieure à la limite, c'est un "game over"
        if distance_to_black_hole < self.black_hole_limit:
            self.player.index = -1
            pygame.mixer.Sound("sounds/death.mp3").play()
            self.player.image = pygame.image.load("images/dead1.png")
            self.draw()
            time.sleep(0.5)
            self.player.image = pygame.image.load("images/dead2.png")
            self.draw()
            time.sleep(1)
            self.game_over = True
            return True
        else:
            return False

    # Vérifie si le joueur a récupéré l'item de fin
    def checkFinished(self):
        if self.finished:
            for projectile in self.projectiles:
                self.projectiles.remove(projectile)
                projectile = None
            if self.player.rect.colliderect(self.finishItem.rect):
                text_finish = Text(50, (255, 255, 255))
                pygame.mixer.Sound("sounds/collected_item.mp3").play()
                text_finish.display(self.screen, 'Bravo, vous avez récupéré du carburant !', (100, 50))
                pygame.display.flip()
                time.sleep(2)
                self.itemCaught = True

    # Applique la gravité au joueur
    def apply_gravity_to_player(self):
        # Calcul de la direction de la gravité
        self.gravity_direction = self.gravity_vector - pygame.Vector2(self.player.rect.center)
        self.gravity_direction.normalize_ip()  # Normaliser pour obtenir une direction unitaire

        # Appliquer la gravité en ajustant les coordonnées du joueur
        self.player.rect.x += self.gravity_direction.x * 2  # Ajustez la force de gravité ici
        self.player.rect.y += self.gravity_direction.y * 2

    def run(self):
        self.player.flying = True
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.draw()
            self.update()
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.hanle_sprint(keys)
            self.player.handle_jump(keys, False)
            self.player.handle_attack(keys)
            self.apply_gravity_to_player()
            self.player.update_animation(keys)
            if not self.finished:
                if random.randint(0, 50) == 0:
                    height = random.randint(0, self.HEIGHT)
                    while height in range(self.player.rect.y - 250, self.player.rect.y + 350):
                        height = random.randint(0, self.HEIGHT)
                    self.projectiles.append(Projectile(self.screen, random.randint(0, self.HEIGHT), self.WIDTH))
                if self.projectiles:
                    for projectile in self.projectiles:
                        result = projectile.move()
                        if not result:
                            self.projectiles.remove(projectile)
                            projectile = None
            self.game_over = self.handle_game_over()
            self.check_collisions()
            if self.game_over:
                self.running = False
                return 'game_over'
            self.elapsed = self.timer.elapsed()
            if self.elapsed == "Temps écoulé":
                self.finished = True
            self.checkFinished()
            if self.itemCaught:
                self.running = False
                return 'finished'
            else:  # Permets de ne pas avoir les textes qui s'empilent
                self.text_display.display(self.screen, 'Survivez 60 secondes pour récupérer la pièce', (50, 50))
                self.text_display.display(self.screen, str(self.elapsed), (50, 100))
                pygame.display.flip()

###################################################
# Classe Level 3                                  #
###################################################

class Level3:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("BlackHoleBot")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(600, 500, 100, 100, self.screen)
        # Chargez l'image "platforme.jpg" et spécifiez sa position initiale
        self.platform_texture = pygame.image.load("images/platforme.jpg")
        self.platforms = [
            Platform(0, 600, 200, 20, self.platform_texture),
            Platform(400, 600, 200, 20, self.platform_texture),
            Platform(200, 600, 200, 20, self.platform_texture),
            Platform(600, 600, 200, 20, self.platform_texture),
            Platform(800, 600, 200, 20, self.platform_texture),
            Platform(1000, 600, 200, 20, self.platform_texture),
            Platform(1200, 600, 200, 20, self.platform_texture)
        ]
        self.background = pygame.image.load("images/b_bg.png")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        # Chargez l'image "hole.png" et spécifiez sa position initiale
        self.hole_image = pygame.image.load("images/hole.png")
        self.hole_image = pygame.transform.scale(self.hole_image, (100, 100))  # Ajustez la taille selon vos besoins
        self.hole_x, self.hole_y = 100, 100  # Position initiale de l'image "hole.png"
        self.animation_done = False
        # Dialogue et image "b.png"
        self.dialogue = ["Bonjour et bienvenue dans ce lieu, je suis le Professeur Baluchon.",
                        "Je vous ai donné ce pouvoir afin de voir si vous en étiez digne.",
                        "Maintenant que j'en ai le coeur net, voici la pièce manquante pour votre vaisseau."]
        self.dialogue_font = pygame.font.Font(None, 36)
        self.b_image = pygame.image.load("images/b.png")
        self.b_image = pygame.transform.scale(self.b_image, (100, 100))  # Ajustez la taille selon vos besoins
        self.b_x, self.b_y = 600, 100  # Position initiale de l'image "b.png"
        self.display_dialogue = False
        self.displayItem = False
        self.current_dialogue_index = 0
        self.dialogue_timer = 0

        # Charger l'image "objet_3.gif" et spécifier sa position initiale
        self.objet_image = pygame.image.load("images/objet_3.gif")
        self.finishItem = FinishItem(self.screen.get_width() / 2 - 50, 50, 'electronic_card', 100, 46)
        self.itemCaught = False
        self.objet_image = pygame.transform.scale(self.objet_image, (100, 100))  # Ajustez la taille selon vos besoins
        self.objet_x, self.objet_y = -100, -100  # Position initiale de l'image de l'objet
        self.objet_animation_done = False

    # Gère les évènements
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # Vérifie les collisions
    def check_collisions(self):
        for platform in self.platforms:
            if self.player.rect.colliderect(platform):
                self.player.rect.y = platform.y - self.player.rect.height
                self.jump = False
                self.jump_count = 10
        if self.player.rect.y < 0:
            self.player.rect.x = self.player.rect.x
            self.player.rect.y = 0

        if self.player.rect.x > self.WIDTH:
            self.player.rect.x = self.WIDTH - self.player.rect.width
            self.player.rect.y = self.player.rect.y

        if self.player.rect.x < 0:
            self.player.rect.x = 0
            self.player.rect.y = self.player.rect.y

        if self.displayItem and self.player.rect.colliderect(self.finishItem.rect):
            text_finish = Text(50, (255, 255, 255))
            pygame.mixer.Sound("sounds/collected_item.mp3").play()
            text_finish.display(self.screen, 'Bravo, vous avez récupéré une carte électronique !', (100, 50))
            pygame.display.flip()
            time.sleep(2)
            self.itemCaught = True

    # Dessine les éléments
    def draw_objects(self):
        self.screen.blit(self.background, (0, 0))
        self.player.draw(self.screen)
        for platform in self.platforms:
            platform.draw(self.screen)

        # Si l'animation de "hole.png" est terminée, on affiche l'image "b.png" et le dialogue
        if self.animation_done:
            self.screen.blit(self.b_image, (self.b_x, self.b_y))
            dialogue_surface = self.dialogue_font.render(self.dialogue[self.current_dialogue_index], True,
                                                         (255, 255, 255))
            dialogue_rect = dialogue_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(dialogue_surface, dialogue_rect)

            # Incrémentez le dialogue_timer
            self.dialogue_timer += 1

            # Changez le dialogue après un certain délai
            if self.dialogue_timer >= 120:  # Changez de dialogue toutes les 2 secondes (60 FPS)

                # Vérifiez si tous les dialogues ont été affichés
                if self.current_dialogue_index >= 2:
                    self.display_dialogue = False  # Arrêtez l'affichage du dialogue
                    self.displayItem = True
                else:
                    self.dialogue_timer = 0
                    self.current_dialogue_index += 1
        else:
            # Sinon, dessinez l'image "hole.png" à sa position actuelle
            self.screen.blit(self.hole_image, (self.hole_x, self.hole_y))
        if self.displayItem:  # Affiche l'item à récupérer si le dialogue est fini
            if self.finishItem.y <= 550:
                self.finishItem.y += 3
                self.finishItem.rect.y += 3
            self.finishItem.draw(self.screen)
        pygame.display.flip()

    # Met à jour les éléments
    def handle_game_over(self):

        # Vérifie si le joueur est tombé trop bas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            return True
        if self.player.rect.x > self.WIDTH:
            return True

    def run(self):
        while self.running:
            self.handle_events()
            self.game_over = self.handle_game_over()
            if self.game_over:
                self.running = False
                return 'game_over'
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.hanle_sprint(keys)
            self.player.handle_jump(keys)
            self.player.handle_attack(keys)
            self.player.apply_gravity(10)
            self.player.update_animation(keys)
            self.check_collisions()
            if not self.animation_done:
                # Animation : déplacez progressivement l'image "hole.png"
                self.hole_x += 2  # Ajustez la vitesse de déplacement selon vos besoins

                # Vérifiez si l'animation est terminée
                if self.hole_x >= 600:  # Position finale de l'image "hole.png"
                    self.animation_done = True
                    self.display_dialogue = True
            self.draw_objects()
            self.clock.tick(self.FPS)
            if self.itemCaught:
                self.running = False
                return 'finished'
            if self.game_over:
                self.running = False
                return 'game_over'


###################################################
# Classe GameFinished                             #
###################################################

class GameFinished:
    def __init__(self, sound_volume):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("BlackHoleBot")
        self.clock = pygame.time.Clock()
        self.running = True
        self.x = 100
        self.y = 100
        self.background = pygame.image.load("images/bg.jpg")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        self.vaisseau = pygame.image.load("images/ship_big.gif")
        self.vaisseau = pygame.transform.scale(self.vaisseau, (400, 300))
        self.vaisseau = pygame.transform.flip(self.vaisseau, 1, 0)
        self.volume = sound_volume
        pygame.mixer.music.load("sounds/main_theme.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.volume/100)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.vaisseau, (self.x, self.y))

    def move_ship(self):
        self.x += 0.5

    def run(self):
        while self.x <= self.WIDTH + 5:  # Attends que le vaisseau sorte de l'écran
            self.move_ship()
            self.draw(self.screen)
            pygame.display.flip()
        final_text = Text(40, (255, 255, 255))
        final_text.display(self.screen, 'Bravo, vous avez fini le jeu !', (100, 50))
        pygame.display.flip()
        time.sleep(3)
        final_text.display(self.screen, 'Crédits : ', (100, 100))
        final_text.display(self.screen, 'Développement : Ehrler Ethan, Belgrand Laureen, Morreel Noah, Sabatier Aymeric', (100, 150))
        final_text.display(self.screen, 'Level design : Sabatier Aymeric', (100, 200))
        final_text.display(self.screen, 'Character Design et Débug : Belgrand Laureen', (100, 250))
        final_text.display(self.screen, 'Gestion des intéractions : Morreel Noah', (100, 300))
        final_text.display(self.screen, 'Gestion du projet et Sound Design : Ehrler Ethan', (100, 350))
        final_text.display(self.screen, 'Crédits sons : Pixabay, download.khinsider.com', (100, 400))
        final_text.display(self.screen, 'Merci d\'avoir joué ! ', (100, 500))
        pygame.display.flip()
        time.sleep(20)

###################################################
# Classe Game                                     #
###################################################

class Game:
    def __init__(self, sound_volume):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.volume = sound_volume
        pygame.mixer.music.set_volume(self.volume/100)

        pygame.display.set_caption("BlackHoleBot")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.player = Player(600, 500, 100, 100, self.screen)
        self.projectile = None
        self.render = 1  # Affiche le portail du niveau 1
        self.platform_texture = pygame.image.load("images/platforme.jpg")
        self.platforms = [
            Platform(50, 500, 200, 20, self.platform_texture),
            Platform(400, 550, 200, 20, self.platform_texture),
            Platform(200, 300, 200, 20, self.platform_texture),
            Platform(600, 550, 200, 20, self.platform_texture),
            Platform(800, 350, 200, 20, self.platform_texture),
            Platform(1000, 200, 200, 20, self.platform_texture),
            Platform(500, 100, 200, 20, self.platform_texture)
        ]
        self.background = pygame.image.load("images/background_1.gif")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        self.portals = [Portal(320, 200, (200, 200), 'E - Niveau 2'),
                        Portal(20, 400, (200, 200), 'E - Niveau 1'),
                        Portal(1100, 100, (200, 200), 'E - Niveau 3'), ]

    # Gère les évènements
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # Vérifie les collisions
    def check_collisions(self):
        if self.projectile and self.player.rect.colliderect(self.projectile):
            self.player.index = -1
            pygame.mixer.Sound("sounds/death.mp3").play()
            self.player.image = pygame.image.load("images/dead1.png")
            self.draw_objects()
            time.sleep(0.5)
            self.player.image = pygame.image.load("images/dead2.png")
            self.draw_objects()
            time.sleep(1)
            self.game_over = True
            return
        for platform in self.platforms:
            if self.projectile and self.projectile.rect.colliderect(platform):
                self.projectile = None
            if self.player.rect.colliderect(platform):
                self.player.rect.y = platform.y - self.player.rect.height
                self.jump = False
                self.jump_count = 10
        if self.player.rect.y < 0:
            self.player.rect.x = self.player.rect.x
            self.player.rect.y = 0

        if self.player.rect.x > self.WIDTH:
            self.player.rect.x = self.WIDTH - self.player.rect.width
            self.player.rect.y = self.player.rect.y

        if self.player.rect.x < 0:
            self.player.rect.x = 0
            self.player.rect.y = self.player.rect.y

    # Vérifie la collision avec le portail
    def check_portal_collision(self):
        player_rect = self.player.rect  # Récupérez le rectangle de collision du joueur
        if player_rect.colliderect(self.portals[self.render].rect):
            # Si le joueur entre en collision avec le portail, effectuez l'action du portail
            new = self.portals[self.render].teleport(self.player, self.screen)
            if new is not None and new != 'game_finished':
                self.render = new
                return None
            elif new == 'game_finished':
                finished = GameFinished(self.volume)
                finished.run()
                self.running = False

    # Dessine les éléments
    def draw_objects(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.portals[self.render].image, self.portals[self.render].rect.topleft)
        self.player.draw(self.screen)
        if self.projectile:
            self.projectile.draw(self.screen)
        for platform in self.platforms:
            platform.draw(self.screen)
        pygame.display.flip()

    # Met à jour les éléments
    def handle_game_over(self):
        # Vérifie si le joueur est tombé trop bas
        if self.player.rect.y > self.WIDTH:
            return True
        else:
            return False

    # Boucle principale
    def run(self):
        while self.running:
            self.handle_events()
            self.game_over = self.handle_game_over()
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.hanle_sprint(keys)
            self.player.handle_jump(keys)
            self.player.handle_attack(keys)
            self.player.apply_gravity(10)
            self.player.update_animation(keys)
            self.check_collisions()
            if self.game_over:
                self.running = False
                return 'game_over'
            self.check_portal_collision()
            self.draw_objects()
            if self.player.hole is not None:
                self.screen.blit(self.player.hole.image, self.player.hole.rect)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()
