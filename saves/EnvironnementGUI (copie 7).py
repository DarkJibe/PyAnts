  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##################### Simulateur de colonies de fourmis ########################
################################################################################
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # 
 #  #  #  #  #  #  #  #  #  !!! NÉCESSITE PyQt5 !!!  #  #  #  #  #  #  #  #  #  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
################################################################################
################## Réalisé dans le cadre du TD d'Info/Prog #####################
########################### par JB Manchon (2134945) ###########################
########################### M1 S8 Sciences Cognitives ##########################
############################## Licence GNU (2017) ##############################
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
 ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##                                                                          ####
#####           PARAMÈTRES MODIFIABLES PAR L'UTILISATEUR :                  ####
##                                                                          ####
NB_ANTS = 50        # Nombre de fourmis                                     ####
QT_FOOD = 6         # Quantité de nourriture                                ####
NB_OBS = 10         # Nombre l'obstacles                                    ####
PAS = 4             # Rapidité de déplacement des fourmis                   ####
EVAP = 20           # Vitesse d'évaporation des traces de phéromone         ####
FOLLOW_PB = 0.75    # Probabilité de suivre une trace de phéromone          ####
##                                                                          ####
################################################################################
################################################################################
##                                                                          ####
#####           NE PAS MODIFIER :                                           ####
##                                                                          ####
STATE = ["FORAGING", "GOBACK", "WORKING"]  # États possibles des fourmi     ####
##                                                                          ####
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

import sys
from math import *
from random import *
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QBasicTimer, QPoint


class Ants():
    
    def __init__(self, x, y, direction):
        self.posX = float(x)  # Position (X, Y) dans l'environnement
        self.posY = float(y)
        self.direction = direction
        self.vitesseX = cos(self.direction)  # Vecteur de vitesse
        self.vitesseY = sin(self.direction)
        self.state = STATE[0]  # État de la fourmi
        self.prev_choice = None  # Précédent choix de trajectoire
                                 # lors d'un évitement d'obstacle
        self.found_food = None  # Cordonnées du point de nourriture trouvé 

    def change_dir(self):
        """
            Modifie pseudo-aléatoirement la trajectoire de la fourmi.
            Ne renvoie rien.
        """
        if self.prev_choice = None:
            if randint(0, 1):
                self.vitesseX = -self.vitesseY
                self.vitesseY = self.vitesseX
                self.prev_choice = "G"
            else:
                self.vitesseX = self.vitesseY
                self.vitesseY = -self.vitesseX
                self.prev_choice = "D"
            
##        if randint(0, 3):
##            self.vitesseX += 0.3
##        elif randint(0, 2):
##            self.vitesseY -= 0.3
##        elif randint(0, 1):
##            self.vitesseX -= 0.3
##        else:
##            self.vitesseY += 0.3
    def normalise(self):
        """
            Normalise la vitesse des fourmis pour concerver leur taille à l'écran.
            Ne renvoie rien.
        """
        norme = sqrt(self.vitesseX**2 + self.vitesseY**2)
        self.vitesseX /= norme
        self.vitesseY /= norme

    def avoid_wall(self, wallXmin, wallYmin, wallXmax, wallYmax):
        """
            Vérifie l'éventuelle collision de la fourmi avec les murs.
            Modifie vitesseX ou vitesseY en fonction du résultat.
            Ne renvoie rien.
        """
        if self.posX <= wallXmin+15:
            self.vitesseX += 1
        elif self.posX >= wallXmax-15:
            self.vitesseX -= 1
        if self.posY <= wallYmin+15:
            self.vitesseY += 1 
        elif self.posY >= wallYmax-15:
            self.vitesseY -= 1
        self.normalise()

    def avoid_obstacles(self, obstacles):
        """
            Vérifie la collision de chaque fourmi avec les obstacles.
            Appelle ant.change_dir() si besoin pour modifier la trajectoire de la fourmi.
            Renvoie un booléen.
        """
        for o in obstacles:  # Pour chaque obstacles
            if self.posX >= (o[0]-o[2])-15 and self.posX <= (o[0]+o[2])+15 \
               and self.posY >= (o[1]-o[3])-15 and self.posY <= (o[1]+o[3])+15:
                self.change_dir() # La fourmi change de direction
                                  # si elle approche d'un obstacle.
                self.normalise()  # On normalise les trajectoire
                return True
        return False

    def find_food(self, food):
        """
            Vérifie si la fourmi a trouvé de la nouriture.
            Modifie son état en fonction du résultat.
            Enregistre la position du point de nourriture trouvé.
            Ne renvoie rien.
        """
        for f in food:  # Pour chaque points de nourriture
            if self.posX >= (f[0]-f[2]) and self.posX <= (f[0]+f[2]) \
               and self.posY >= (f[1]-f[3]) and self.posY <= (f[1]+f[3]):
                self.state = STATE[1]  # La fourmi change d'état si elle atteint un point
                self.found_food = [f[0], f[1]]  # de nourriture et mémorise sa position.

    def go_to(self, pos):
        """
            Détermine la trajectoire directe vers un point donné du plan.
            Ne renvoie rien.
        """
        distance = sqrt((pos[0]-self.posX)**2
                       +(pos[1]-self.posY)**2)  # Distance fourmi-pt d'arrivée
        f = distance / PAS  # Nb d'itérations pour atteindre le pt d'arrivée
        self.vitesseX = (pos[0] - self.posX) / f
        self.vitesseY = (pos[1] - self.posY) / f
        self.normalise()  # On normalise les trajectoire

    def check_trail(self):
        """
            Vérifie si la fourmi passe près d'une trace de phéromone.
            Si oui, appelle self.go_to() pour déterminer la nouvelle trajectoire.
            Ne renvoie rien.
        """
        for t in fen.envi.trails:
            if round(self.posX, 6) == round(t[0], 6) \
               and round(self.posY, 6) == round(t[1], 6):
                if random() < FOLLOW_PB:
                    try:
                        next_trail = fen.envi.trails[fen.envi.trails.index(t) \
                                                     + len(fen.envi.ants)]
                        self.go_to(next_trail)
                    except IndexError:
                        pass

    def go_back(self):
        """
            Détermine la trajectoire vers la fourmilière.
            Ne renvoie rien.
        """
        anthill_pos = fen.envi.anthill  # Pos de la fourmilière
        self.go_to(anthill_pos)  # Vers la fourmilière

    def check_pos(self):
        """
            Vérifie si la fourmi a atteint la fourmilière.
            Redéfinit la trajectoire vers le dernier point de nourriture trouvé.
            Ne renvoie rien.
        """
        if self.posX >= fen.envi.anthill[0]-5 and self.posX <= fen.envi.anthill[0]+5 \
           and self.posY >= fen.envi.anthill[1]-5 and self.posY <= fen.envi.anthill[1]+5:
            self.state = STATE[2]
            self.go_to(self.found_food)

    def maj_pos(self):
        """
            Met à jour la position de la fourmi en fonction de son vecteur de vitesse et du pas.
            Ne renvoie rien.
        """
        self.posX += PAS * self.vitesseX  # On multiplie la vitesse normée
        self.posY += PAS * self.vitesseY  # par le pas pour avoir un déplacement fluide

    # COMPORTEMENT GLOBAL DE LA FOURMIS (actualisé à chaque itération de boucle)
    def MAJ(self, largeur, hauteur, f, obs):
        """
            Définit le comportement global de la fourmi en fonction de son état.
            Appelle les différentes fonctions comportementales :
            self.avoid_wall() ; self.avoid_obstacles() ; self.find_food()
            self.check_trail() ; self.go_back() ; self.go_to()
            & self.check_pos().
            Appelle self.maj_pos() pour mettre à jour la position de la fourmi.
            Ne renvoie rien.
        """
        self.avoid_wall(0, 0, largeur, hauteur)  # Elle évite le mur
        ob = self.avoid_obstacles(obs)  # Elle évite les obstacles
        self.find_food(f)
        if self.state == STATE[0]:
            self.check_trail()  # Elle verifie les traces de phéromone
            self.maj_pos() # On actualise la position de la fourmi
        elif self.state == STATE[1]:
            if ob:  # 
                self.maj_pos() # On actualise la position de la fourmi
            else:
                self.go_back()
                self.check_pos()
                self.maj_pos() # On actualise la position de la fourmi
        else:
            self.go_to(self.found_food)
            self.maj_pos() # On actualise la position de la fourmi


class Environment():
    
    def __init__(self, nb_ants, qt_food, obstacles, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.obstacles = []
        self.food = []
        self.ants = []
        self.trails = []
        self.anthill = [randint(0, largeur),  # posX et
                       randint(0, hauteur)]   # posY de la fourmilière
        for i in range(nb_ants):
            self.ants.append(Ants(self.anthill[0], self.anthill[1],  # Position de départ des fourmis
                                  random() * 2. * pi ))  # Direction aléatoire
        for i in range(qt_food):
            self.food.append(self.generator(largeur, hauteur))  # Points de nourriture
        for i in range(obstacles):
            self.obstacles.append(self.generator(largeur, hauteur))  # Obstacles

    def generator(self, largeur, hauteur):
        """
            Génère une position (X, Y) qui ne soit pas trop proche
            de la fourmilière afin d'éviter un comportement chaotique.
            Renvoie une liste de deux entiers.
        """
        while True:
            new = [randint(0, largeur), randint(0, hauteur), # Position du nouvel élément
                   randint(20, 50), randint(20, 50)]  # Diamètre du nouvel élément
            if (self.anthill[0]-50 > new[0] or new[0] > self.anthill[0]+50) \
               and (self.anthill[1]+50 < new[1] or new[1] < self.anthill[1]-50):
                # Vérifie que les coordonnées aléatoires ne se trouvent pas
                # dans un rayon de 50 autour des coordonnées de la fourmilière.
                return new  # Renvoie les coordonnées si c'est le cas,
                            # recommence sinon.
    
    def maj_ants(self):
        """
            Met à jour la position de chaque fourmis en appelant ant.MAJ()
            Ne renvoie rien.
        """
        for ant in self.ants:
            ant.MAJ(self.largeur, self.hauteur, self.food,
                    self.obstacles)  # Fonction de mise à jour des fourmis

    def maj_trails(self):
        """
            Met à jour les traces de phéromone laissées par les fourmis.
            Dépend de la variable EVAP.
            Ne renvoie rien.
        """
        for ant in self.ants:
            self.trails.append([ant.posX, ant.posY])  # On ajoute les positions
        if (len(self.trails) > (EVAP * len(self.ants))):
            for i in range(len(self.ants)-1, -1, -1):  # Supprime les traces les plus anciennes
                del self.trails[i]  # à rebour pour éviter de décaler les indexes des données à supprimer

    def maj_envi(self):
        """
            Met à jour l'environnement en appelant les fonctions dédiées à chaque types d'éléments.
            Ne renvoie rien.
        """
        self.maj_ants()  # Met à jour la position de chaque fourmis
        self.maj_trails()  # Met à jour les traces de phéromone
# À ÉCRIRE self.maj_food()  # Met à jour le stock de nourriture


class Window(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QBasicTimer()
        self.timer.start(40, self)  # L'entier définie la vitesse de l'horloge

    def initUI(self):  # Crée la GUI
        self.envi = Environment(NB_ANTS, QT_FOOD, NB_OBS, 800, 600)
        # Nb de fourmis, Qt nourriture, Nb d'obstacles, Largeur, Hauteur
        self.setFixedSize(self.envi.largeur, self.envi.hauteur)
        self.setWindowTitle('Colonies de fourmis')
        self.show()

    def timerEvent(self, e):
        self.envi.maj_envi()
        self.repaint()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_envi(qp)
        qp.end()     

    def draw_envi(self, qp):
        qp.setBrush(QColor(170, 93, 37))  # Couleur de fond
        qp.drawRect(0, 0, 1200, 800)  # Dessine le fond
        qp.setPen(Qt.black)
        size = self.size()
        
        qp.setPen(Qt.black)  # Dessine les fourmis (noires)
        for ant in self.envi.ants:
            qp.drawLine(ant.posX,
                        ant.posY,
                        ant.posX - 2 * ant.vitesseX,
                        ant.posY - 2 * ant.vitesseY)

        food_color = QColor(34, 124, 4)  # Dessine la nourriture (verte)
        qp.setPen(food_color)
        qp.setBrush(food_color)
        for coord in self.envi.food:
            center = QPoint(coord[0], coord[1])
            qp.drawEllipse(center, coord[2], coord[3])

        qp.setPen(Qt.black)  # Dessine les obstacles (noirs)
        qp.setBrush(Qt.black)
        for coord in self.envi.obstacles:
            center = QPoint(coord[0], coord[1])
            qp.drawEllipse(center, coord[2], coord[3])

        anthill_color = Qt.red  # Dessine la foumillière (rouge)
        qp.setPen(anthill_color)
        qp.setBrush(anthill_color)
        center = QPoint(self.envi.anthill[0], self.envi.anthill[1])
        qp.drawEllipse(center, 10, 10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fen = Window()
#    print(fen.obstacles)
    sys.exit(app.exec_())
