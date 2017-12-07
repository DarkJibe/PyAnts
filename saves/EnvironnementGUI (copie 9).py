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
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #   #
 ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##                                                                          ####
#####           PARAMÈTRES MODIFIABLES PAR L'UTILISATEUR :                  ####
##                                                                          ####
NB_ANTS = 50        # Nombre de fourmis                                     ####
NB_FOOD = 6         # Nombre de points de nourriture                        ####
QT_FOOD = 100       # Quantité de nourriture par point                      ####
NB_OBS = 10         # Nombre l'obstacles                                    ####
PAS = 4             # Rapidité de déplacement des fourmis                   ####
EVAP = 100          # Vitesse d'évaporation des traces de phéromone         ####
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

    def toggle_R(self):
        """
            Modifie le vecteur vitesse pour permettre à la fourmi de
            tourner à droite.
            Ne renvoie rien.
        """
        self.vitesseX = 0.5*(self.vitesseY+self.vitesseX)
        self.vitesseY = 0.5*(self.vitesseY-self.vitesseX)
        self.prev_choice = "R"

    def toggle_L(self):
        """
            Modifie le vecteur vitesse pour permettre à la fourmi de
            tourner à gauche.
            Ne renvoie rien.
        """
        self.vitesseX = 0.5*(self.vitesseX-self.vitesseY)
        self.vitesseY = 0.5*(self.vitesseX+self.vitesseY)
        self.prev_choice = "L"

    def change_dir(self):
        """
            Modifie pseudo-aléatoirement la trajectoire de la fourmi.
            Si elle n'a pas rencontré d'obstacle : 50% de chance d'aller
            à droite et 50% de chance d'aller à gauche.
            Si elle a tourné à droite précédemment : 80% de chance de tourner
            à gauche la fois suivante et vice versa.
            Ne renvoie rien.
        """
        if self.prev_choice == None:
            if randint(0, 1):  
                self.toggle_L()  # 1/2 chance d'aller à gauche
            else:
                self.toggle_R()  # 1/2 chance d'aller à droite
        elif self.prev_choice == "L":
            if random() > 0.8:
                self.toggle_L()
            else:
                self.toggle_R()
        elif self.prev_choice == "R":
            if random() > 0.8:
                self.toggle_R()
            else:
                self.toggle_L()
        self.normalise()  # On normalise les trajectoire

    def change_dir2(self):
        """
            Modifie pseudo-aléatoirement la trajectoire de la fourmi.
            25% de chance d'aller dans une des quatre directions possibles.
            Ne renvoie rien.
        """
        if randint(0, 3):
            self.vitesseX += 0.3
        elif randint(0, 2):
            self.vitesseY -= 0.3
        elif randint(0, 1):
            self.vitesseX -= 0.3
        else:
            self.vitesseY += 0.3
        self.normalise()  # On normalise les trajectoire


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
        if self.posX <= wallXmin+5:
            self.vitesseX += 1
        elif self.posX >= wallXmax-5:
            self.vitesseX -= 1
        if self.posY <= wallYmin+5:
            self.vitesseY += 1 
        elif self.posY >= wallYmax-5:
            self.vitesseY -= 1
        self.normalise()

    def avoid_obstacles(self, obstacles):
        """
            Vérifie la collision de chaque fourmi avec les obstacles.
            Appelle ant.change_dir() si besoin pour modifier la trajectoire de la fourmi.
            Renvoie un booléen.
        """
        for o in obstacles:  # Pour chaque obstacles
            if self.posX >= (o[0]-o[2])-3 and self.posX <= (o[0]+o[2])+3 \
               and self.posY >= (o[1]-o[3])-3 and self.posY <= (o[1]+o[3])+3:
                if self.state == STATE[0]:
                    self.change_dir() # La fourmi change de direction
                else:                 # si elle approche d'un obstacle.
                    self.change_dir2()
                return True
        return False

    def find_food(self, food):
        """
            Vérifie si la fourmi a trouvé de la nouriture.
            Modifie son état en fonction du résultat.
            Enregistre la position du point de nourriture trouvé.
            Renvoie un booléen.
        """
        for f in food:  # Pour chaque points de nourriture
            if self.posX >= (f[0][0]-f[0][2])\
            and self.posX <= (f[0][0]+f[0][2])\
             and self.posY >= (f[0][1]-f[0][3])\
              and self.posY <= (f[0][1]+f[0][3]):
                # La fourmi change d'état si elle atteint un point
                # de nourriture et mémorise sa position.
                self.state = STATE[1]
                self.found_food = [f[0][0], f[0][1]]
                f[1] -= 1
                return True
        return False

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
            if int(self.posX) == t[0] \
               and int(self.posY) == t[1]:
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
        self.go_to(fen.envi.anthill)  # Vers la fourmilière

    def check_pos(self, pos):
        """
            Vérifie si la fourmi a atteint la fourmilière.
            Redéfinit la trajectoire vers le dernier point de nourriture trouvé.
            Renvoie un booléen.
        """
        if self.posX >= pos[0]-5 and self.posX <= pos[0]+5 \
           and self.posY >= pos[1]-5 and self.posY <= pos[1]+5:
            return True
        return False

    def maj_pos(self):
        """
            Met à jour la position de la fourmi en fonction de son vecteur de vitesse et du pas.
            Ne renvoie rien.
        """
        self.posX += PAS * self.vitesseX  # On multiplie la vitesse normée
        self.posY += PAS * self.vitesseY  # par le pas pour avoir un déplacement fluide

    ### COMPORTEMENT GLOBAL DE LA FOURMIS
    ### (actualisé à chaque itération de boucle)
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
        self.avoid_wall(0, 0, largeur, hauteur)  # Elle évite les murs
        food_ok = self.find_food(f)  # Elle recherche la nourriture
        if self.avoid_obstacles(obs):   # S'il y a un obstacle,
            self.maj_pos()              # elle l'évite en priorité
        else:
            if self.state == STATE[0]:  # SI FORAGING :
                self.check_trail()  # Elle verifie les traces de phéromone
                self.maj_pos() # On actualise la position de la fourmi
            elif self.state == STATE[1]:  # SI GOBACK :
                self.go_back()  # Elle rentre à la fourmilière
                if self.check_pos(fen.envi.anthill):  # Elle vérifie si elle y est
                    #self.state = STATE[0]
                ##### À DÉCOMMENTER POUR OBTENIR DE JOLIES LIGNES DE FOURMIS    
                    self.state = STATE[2]
                    self.go_to(self.found_food)
                self.maj_pos() # On actualise la position de la fourmi
            else:  # SI WORKING :
                self.go_to(self.found_food)  # Elle retourne au dernier
                                             # point de nourriture rencontré
                if self.check_pos(self.found_food) and not food_ok:
                    self.found_food = None
                    self.state = STATE[0]
                self.maj_pos() # On actualise la position de la fourmi

class Environment():
    
    def __init__(self, nb_ants, nb_food, obstacles, largeur, hauteur):
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
        for i in range(nb_food):
            self.food.append([self.generator(largeur, hauteur), \
                              QT_FOOD, QT_FOOD])  # Points de nourriture
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
            # On ajoute les positions entières pour permettre une comparaison.
            self.trails.append([int(ant.posX), int(ant.posY)])
        if (len(self.trails) > (EVAP * len(self.ants))):
            # On supprime les traces les plus anciennes à rebour 
            # pour éviter de décaler les indexes des données à supprimer.
            for i in range(len(self.ants)-1, -1, -1):
                del self.trails[i]

    def maj_food(self):
        """
            Met à jour les stock de nourriture en fonction
            des actions des fourmis.
            Dépend des variables NB_FOOD et QT_FOOD.
            Ne renvoie rien.
        """
        for f in self.food:
            if f[1] < f[2]:
                f[2] = f[1]
                f[0][2] -= f[0][2]*0.01
                f[0][3] -= f[0][3]*0.01
            if f[1] <= 0:
                self.food.remove(f)
                
    def maj_envi(self):
        """
            Met à jour l'environnement en appelant les fonctions dédiées à chaque types d'éléments.
            Ne renvoie rien.
        """
        self.maj_ants()  # Met à jour la position de chaque fourmis
        self.maj_trails()  # Met à jour les traces de phéromone
        self.maj_food()  # Met à jour le stock de nourriture


class Window(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QBasicTimer()
        self.timer.start(40, self)  # L'entier définie la vitesse de l'horloge

    def initUI(self):  # Crée la GUI
        self.envi = Environment(NB_ANTS, NB_FOOD, NB_OBS, 800, 600)
        # Nb de fourmis, Nb nourriture, Nb d'obstacles, Largeur, Hauteur
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
            center = QPoint(coord[0][0], coord[0][1])
            qp.drawEllipse(center, coord[0][2], coord[0][3])

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
