import sys
import time
import pygame
from game import Game

#############################################
# Classe MainMenu                           #
#############################################

class MainMenu:
    def __init__(self):
        self.game_over = False
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.game_state = "start_menu"
        self.volume = 100
        self.running = True
        pygame.display.set_caption("BlackHoleBot")
        pygame.mixer.music.load("sounds/main_theme.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.volume / 100)
        self.game = Game(self.volume)

    # Dessinez l'écran d'accueil
    def draw_start_menu(self):
        self.screen.fill((0, 0, 0))
        bg = pygame.image.load("images/bg.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        self.screen.blit(bg, (0, 0))
        font = pygame.font.SysFont('Arial', 40)
        # Créez le texte
        title = font.render('BlackHoleBot', True, (255, 255, 255))
        start_button = font.render('Commencer (espace)', True, (255, 255, 255))
        commands_button = font.render('Commandes (C)', True, (255, 255, 255))
        options_button = font.render('Options (O)', True, (255, 255, 255))
        # Affichez le texte
        self.screen.blit(title,
                         (self.screen_width / 2 - title.get_width() / 2,
                          self.screen_height / 2 - title.get_height() / 2))
        self.screen.blit(start_button,
                         (self.screen_width / 2 - start_button.get_width() / 2,
                             self.screen_height / 2 + start_button.get_height() / 2))
        self.screen.blit(commands_button,
                            (self.screen_width / 2 - commands_button.get_width() / 2,
                            self.screen_height / 2 + commands_button.get_height() * 2.5))
        self.screen.blit(options_button,
                         (self.screen_width / 2 - options_button.get_width() / 2,
                          self.screen_height / 2 + options_button.get_height() * 1.5))
        pygame.display.update()

    # Dessinez l'écran de fin de jeu
    def draw_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        bg = pygame.image.load("images/game_over.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        self.screen.blit(bg, (0, 0))
        font = pygame.font.SysFont('arial', 40)
        # Créez le texte
        title = font.render('Game Over', True, (255, 255, 255))
        restart_button = font.render('R - Recommencer', True, (255, 255, 255))
        quit_button = font.render('Q - Revenir sur l\'écran titre', True, (255, 255, 255))
        # Affichez le texte
        self.screen.blit(title, (
            self.screen_width / 2 - title.get_width() / 2, self.screen_height / 2 - title.get_height() / 3))
        self.screen.blit(restart_button,
                         (self.screen_width / 2 - restart_button.get_width() / 2,
                          self.screen_height / 1.9 + restart_button.get_height()))
        self.screen.blit(quit_button,
                         (self.screen_width / 2 - quit_button.get_width() / 2,
                          self.screen_height / 2 + quit_button.get_height() / 2))
        pygame.display.update()

    # Dessinez l'écran d'options
    def draw_options_menu(self, volume_level):
        self.screen.fill((0, 0, 0))
        bg = pygame.image.load("images/bg.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        self.screen.blit(bg, (0, 0))
        font = pygame.font.SysFont('Arial', 40)
        # Créez le texte
        title = font.render('Options', True, (255, 255, 255))
        volume_title = font.render('Volume :', True, (255, 255, 255))
        volume = font.render(volume_level, True, (255, 255, 255))
        return_text = font.render('Echap - Revenir à l\'accueil', True, (255, 255, 255))
        # Affichez le texte
        self.screen.blit(title,
                         (self.screen_width / 2 - title.get_width() / 2, self.screen_height / 2 - title.get_height() / 2))
        self.screen.blit(volume_title,
                         (
                             self.screen_width / 2 - volume_title.get_width() / 2,
                             self.screen_height / 2 + volume_title.get_height() / 2))
        self.screen.blit(volume,
                         (
                             self.screen_width / 2 - volume.get_width() / 2,
                             self.screen_height / 2 + volume.get_height() * 1.5))
        self.screen.blit(return_text,
                         (
                             self.screen_width / 2 - return_text.get_width() / 2,
                             self.screen_height / 2 + return_text.get_height() * 2.5))
        pygame.display.update()

    # Dessinez l'écran des commandes
    def draw_command_menu(self):
        self.screen.fill((0, 0, 0))
        bg = pygame.image.load("images/bg.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        self.screen.blit(bg, (0, 0))
        font = pygame.font.SysFont('Arial', 40)
        # Créez le texte
        title = font.render('Commandes', True, (255, 255, 255))
        move = font.render('LEFT ,RIGHT ,UP ,DOWN - Déplacement', True, (255, 255, 255))
        jump = font.render('Espace - Saut', True, (255, 255, 255))
        sprint = font.render('SHIFT - Sprint', True, (255, 255, 255))
        attack = font.render('Z - Attaque', True, (255, 255, 255))
        interaction = font.render('E - Interaction', True, (255, 255, 255))
        retour = font.render('R - Retour au vaisseau', True, (255, 255, 255))
        return_text = font.render('Echap - Revenir à l\'accueil', True, (255, 255, 255))
        # Affichez le texte
        self.screen.blit(title,
                            (self.screen_width / 2 - title.get_width() / 2, self.screen_height / 2 - title.get_height() / 2))
        self.screen.blit(move,
                            (self.screen_width / 2 - move.get_width() / 2, self.screen_height / 2 + move.get_height() / 2))
        self.screen.blit(jump,
                            (self.screen_width / 2 - jump.get_width() / 2, self.screen_height / 2 + jump.get_height() * 1.5))
        self.screen.blit(sprint,
                            (self.screen_width / 2 - sprint.get_width() / 2, self.screen_height / 2 + sprint.get_height() * 2.5))
        self.screen.blit(attack,
                            (self.screen_width / 2 - attack.get_width() / 2, self.screen_height / 2 + attack.get_height() * 3.5))
        self.screen.blit(interaction,
                            (self.screen_width / 2 - interaction.get_width() / 2, self.screen_height / 2 + interaction.get_height() * 4.5))
        self.screen.blit(retour,
                            (self.screen_width / 2 - retour.get_width() / 2, self.screen_height / 2 + retour.get_height() * 5.5))
        self.screen.blit(return_text,
                            (self.screen_width / 2 - return_text.get_width() / 2, self.screen_height / 2 + return_text.get_height() * 6.5))
        pygame.display.update()

    # Dessinez l'écran d'accueil et gérez les événements
    def start_menu(self):
        self.draw_start_menu()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.run_animation()
            self.play()
        elif keys[pygame.K_o]:
            self.game_state = "options"
            self.game_over = False
        elif keys[pygame.K_c]:
            self.game_state = "commands"
            self.game_over = False

    # Lancez le jeu
    def play(self):
        self.game = Game(self.volume)
        game_instance = self.game.run()
        self.game_state = "game"
        self.game_over = False
        if game_instance == 'game_over':
            self.game_state = "game_over"
            self.game_over = True
            self.gameOver()

    # Gérez l'écran de fin de jeu
    def gameOver(self):
        self.draw_game_over_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.game_state = "game"
            self.game_over = False
        if keys[pygame.K_q]:
            self.game_state = "start_menu"
            self.game_over = False

    # Gérez l'écran d'options
    def options_menu(self):
        keys = pygame.key.get_pressed()
        self.draw_options_menu('< ' + str(self.volume) + ' % >')
        if keys[pygame.K_LEFT]:
            if self.volume > 0:
                self.volume -= 1
                time.sleep(0.15)
        elif keys[pygame.K_RIGHT]:
            if self.volume < 100:
                self.volume += 1
                time.sleep(0.15)
        elif keys[pygame.K_ESCAPE]:
            self.game_state = "start_menu"

        pygame.mixer.music.set_volume(self.volume / 100)


    # Affichez l'écran des commandes
    def command_menu(self):
        keys = pygame.key.get_pressed()
        self.draw_command_menu()
        if keys[pygame.K_ESCAPE]:
            self.game_state = "start_menu"

    # Gérez les événements de fermeture de la fenêtre
    def handle_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # Lancez l'animation d'intro
    def run_animation(self):
        zoom = 1.0
        zoom_vitesse = 0.005
        clock = pygame.time.Clock()
        animation_en_cours = True

        # Chargez l'image du fond
        fond_image = pygame.image.load("images/bg_animation.jpg")
        fond_image = pygame.transform.scale(fond_image, (self.screen_width, self.screen_height))

        # Chargez la police de caractères
        font = pygame.font.Font(None, 36)

        while animation_en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Dessinez le fond d'écran
            self.screen.blit(fond_image, (0, 0))

            # Mise à l'échelle de la fenêtre
            zoom += zoom_vitesse
            fond_zoom = pygame.transform.scale(self.screen, (int(self.screen_width * zoom), int(self.screen_height * zoom)))
            self.screen.blit(fond_zoom, (0, 0))

            pygame.display.update()

            if zoom >= 2.0:  # Lorsque l'animation est terminée
                animation_en_cours = False

        
        text = font.render("Après avoir heurté un trou noir, notre ami le robot a cassé son vaisseau.  ", True, (255, 255, 255))
        text2 = font.render("Il va devoir retrouver certaines pièces en défiant différentes gravités afin de le réparer..", True, (255, 255, 255))
        text3 = font.render("Cependant certains événements bizarres se déroulent dans son vaisseau ", True, (255, 255, 255))
        text4 = font.render("et un pouvoir mystérieux rentre en sa possession.", True, (255, 255, 255))
        self.screen.blit(text, (100, self.screen_height // 1.7))
        self.screen.blit(text2, (100, self.screen_height // 1.5))
        self.screen.blit(text3, (100, self.screen_height // 1.3))
        self.screen.blit(text4, (100, self.screen_height // 1.25))
        pygame.display.update()

        # Attendez un certain temps avant de quitter
        pygame.time.delay(8000)  # 2000 millisecondes (2 secondes)

    def run(self):
        pygame.mixer.music.load("sounds/main_theme.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.volume/100)
        while self.running:
            self.handle_quit()
            if self.game_state == "start_menu":
                self.start_menu()
            elif self.game_state == "options":
                self.options_menu()

            elif self.game_state == 'game':
                self.play()
            elif self.game_state == "commands":
                self.command_menu()
            elif self.game_over:
                self.gameOver()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
