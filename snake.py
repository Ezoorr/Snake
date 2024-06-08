import sys
import random
import pygame
import sqlite3

pygame.init()

# Paramètres du jeu
largeur, hauteur = 640, 480
taille_case = 20
vitesse_initiale = 10
niveaux = {'Facile': 8, 'Normal': 12, 'Difficile': 16}
obstacles_actifs = False
couleur_obstacle = (100, 100, 100)
temps_animation_perte_vie = 1000

couleur_fond = (255, 87, 51)
couleur_serpent = (0, 255, 0)
couleur_pomme = (4, 4, 4)

# Classes du jeu
class Serpent:
    def __init__(self):
        self.longueur = 1
        self.corps = [(largeur // 2, hauteur // 2)]
        self.direction = (1, 0)
        self.carrés_rouges_mangés = 0
        self.vies = 1
        self.vitesse = vitesse_initiale

    def deplacer(self):
        tete_x, tete_y = self.corps[0]
        dx, dy = self.direction
        nouvelle_tete = ((tete_x + dx * taille_case) % largeur, (tete_y + dy * taille_case) % hauteur)
        self.corps.insert(0, nouvelle_tete)
        if len(self.corps) > self.longueur:
            self.corps.pop()

    def manger_pomme(self):
        self.longueur += 1
        self.carrés_rouges_mangés += 1

    def collision(self):
        return self.corps[0] in self.corps[1:]

    def perdre_vie(self):
        self.vies -= 1
        self.vitesse = vitesse_initiale
        pygame.time.delay(temps_animation_perte_vie)
        self.corps = [(largeur // 2, hauteur // 2)]

class Pomme:
    def __init__(self):
        self.position = (random.randint(0, (largeur - taille_case) // taille_case) * taille_case,
                         random.randint(0, (hauteur - taille_case) // taille_case) * taille_case)

    def placer(self):
        self.position = (random.randint(0, (largeur - taille_case) // taille_case) * taille_case,
                         random.randint(0, (hauteur - taille_case) // taille_case) * taille_case)

class Obstacle:
    def __init__(self):
        self.position = (random.randint(0, (largeur - taille_case) // taille_case) * taille_case,
                         random.randint(0, (hauteur - taille_case) // taille_case) * taille_case)

    def placer(self):
        self.position = (random.randint(0, (largeur - taille_case) // taille_case) * taille_case,
                         random.randint(0, (hauteur - taille_case) // taille_case) * taille_case)

# Connexion à la base de données (un fichier sera créé s'il n'existe pas)
connexion_bdd = sqlite3.connect('scores.db')
curseur = connexion_bdd.cursor()

# Création de la table scores si elle n'existe pas
curseur.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        joueur TEXT NOT NULL,
        points INTEGER NOT NULL
    )
''')
connexion_bdd.commit()

# Interface utilisateur
def interface_utilisateur():
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(200, 200, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    user_name = ""
    active = False

    level_selected = False
    selected_level = None

    while not level_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if user_name:
                            level_selected = True
                        else:
                            print("Veuillez entrer votre nom.")
                    elif event.key == pygame.K_BACKSPACE:
                        user_name = user_name[:-1]
                    else:
                        user_name += event.unicode

        fenetre.fill(couleur_fond)

        txt_surface = font.render(user_name, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        fenetre.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(fenetre, color, input_box, 2)

        pygame.display.flip()

    return user_name

# Interface de sélection de niveau
def interface_selection_niveau():
    font = pygame.font.Font(None, 36)
    niveau_selected = False
    selected_level = None

    while not niveau_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for niveau, rect in niveau_rects.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        niveau_selected = True
                        selected_level = niveau

        fenetre.fill(couleur_fond)

        text = font.render("Choisissez un niveau :", True, (255, 255, 255))
        fenetre.blit(text, (200, 100))

        niveau_rects = {}
        for i, niveau in enumerate(niveaux):
            text = font.render(f"{niveau}: {niveaux[niveau]} carrés par seconde", True, (255, 255, 255))
            rect = pygame.Rect(200, 150 + i * 40, text.get_width(), text.get_height())
            fenetre.blit(text, (200, 150 + i * 40))
            niveau_rects[niveau] = rect

        pygame.display.flip()

    return selected_level

# Fonction pour afficher tous les scores
def afficher_tous_les_scores():
    print("Tous les scores enregistrés :")
    scores = curseur.execute('SELECT joueur, points FROM scores ORDER BY points DESC').fetchall()
    for score in scores:
        print(f"Joueur : {score[0]}, Points : {score[1]}")

# Initialisation de la fenêtre et des objets du jeu
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Jeu de Serpent")

nom_joueur = interface_utilisateur()

# Sélection du niveau
choix_niveau = interface_selection_niveau()

serpent = Serpent()
pomme = Pomme()
obstacle = Obstacle()

# Appliquer la vitesse sélectionnée
if choix_niveau in niveaux:
    serpent.vitesse = niveaux[choix_niveau]
else:
    print("Niveau par défaut sélectionné.")

clock = pygame.time.Clock()

# Boucle principale du jeu
while serpent.vies > 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and serpent.direction != (0, 1):
                serpent.direction = (0, -1)
            elif event.key == pygame.K_DOWN and serpent.direction != (0, -1):
                serpent.direction = (0, 1)
            elif event.key == pygame.K_LEFT and serpent.direction != (1, 0):
                serpent.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and serpent.direction != (-1, 0):
                serpent.direction = (1, 0)

    serpent.deplacer()

    if serpent.corps[0] == pomme.position:
        serpent.manger_pomme()
        pomme.placer()
        serpent.vitesse += 1

    if obstacles_actifs and serpent.corps[0] == obstacle.position:
        serpent.perdre_vie()

    if serpent.collision():
        serpent.perdre_vie()

    fenetre.fill(couleur_fond)

    for segment in serpent.corps:
        pygame.draw.rect(fenetre, couleur_serpent, (segment[0], segment[1], taille_case, taille_case))

    pygame.draw.rect(fenetre, couleur_pomme, (pomme.position[0], pomme.position[1], taille_case, taille_case))

    if obstacles_actifs:
        pygame.draw.rect(fenetre, couleur_obstacle, (obstacle.position[0], obstacle.position[1], taille_case, taille_case))

    font = pygame.font.Font(None, 36)
    text = font.render(f"Joueur : {nom_joueur} | Points : {serpent.carrés_rouges_mangés} | Vies : {serpent.vies} | Vitesse : {serpent.vitesse}",
                       True, (255, 255, 255))
    fenetre.blit(text, (10, 10))

    pygame.display.flip()

    clock.tick(serpent.vitesse)

# Enregistrement du score dans la base de données
curseur.execute('INSERT INTO scores (joueur, points) VALUES (?, ?)', (nom_joueur, serpent.carrés_rouges_mangés))
connexion_bdd.commit()

# Affichage de tous les scores
afficher_tous_les_scores()

# Fermeture de la connexion à la base de données
connexion_bdd.close()

pygame.quit()
sys.exit()
