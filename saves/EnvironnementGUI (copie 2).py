import sys
from math import *
from random import *
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QBasicTimer, QPoint

PAS = 4  # Rapidité de déplacement des fourmis
STATE = ["FORAGING", "GOBACK"]  # États possibles pour chaque fourmi

class Mobile(object):
    def __init__(self, x, y):
        self.posX = float(x)
        self.posY = float(y)

    def __str__(self):
        return "x = {}, y = {}".format(self.posX, self.posY)
    
    def distance(self, other):
        return sqrt((self.posX-other.posX)**2 + (self.posY-other.posY)**2)

    def distanceCarre(self, other):
        return (self.posX-other.posX)**2 + (self.posY-other.posY)**2


class Ants(Mobile):
    
    def __init__(self, x, y, direction):
        
        super(Ants, self).__init__(x, y)  # Coordonnées
        self.direction = direction
        self.vitesseX = cos(self.direction)  # Direction
        self.vitesseY = sin(self.direction)
        self.state = STATE[0]

    def change_dir(self):
        if randint(0, 3):
            self.vitesseX += 0.3
        elif randint(0, 2):
            self.vitesseY -= 0.3
        elif randint(0, 1):
            self.vitesseX -= 0.3
        else:
            self.vitesseY += 0.3

    def normalise(self):
        """
            Normalise la vitesse des fourmis pour concerver leur taille à l'écran.
            Ne renvoie rien.
        """
        norme = sqrt(self.vitesseX**2 + self.vitesseY**2)
        self.vitesseX /= norme
        self.vitesseY /= norme

    def distance_wall(self, wallXmin, wallYmin, wallXmax, wallYmax):
        distance = [0, 0, 0, 0]
        poswall = [wallXmin, wallYmin, wallXmax, wallYmax]
        distance[0] = abs(wallXmin - self.posX)
        distance[1] = abs(wallYmin - self.posY)
        distance[2] = abs(wallXmax - self.posX)
        distance[3] = abs(wallYmax - self.posY)
        return distance

    def avoid_wall(self, wallXmin, wallYmin, wallXmax, wallYmax):
        """
            Vérifie la colision de chaque fourmis avec les murs.
            Modifie vitesseX ou vitesseY en fonction du résultat.
            Ne renvoie rien.
        """
        if self.posX <= wallXmin+15:
            self.vitesseX += 1
            self.normalise()
        elif self.posX >= wallXmax-15:
            self.vitesseX -= 1
            self.normalise()
        if self.posY <= wallYmin+15:
            self.vitesseY += 1 
            self.normalise()
        elif self.posY >= wallYmax-15:
            self.vitesseY -= 1
            self.normalise()

    def avoid_obstacles(self, obstacles):
        """
            Vérifie la collision de chaque fourmi avec les obstacles.
            Appelle ant.change_dir() si besoin pour modifier la trajectoire de la fourmi.
            Ne renvoie rien.
        """
        for o in obstacles:  # Pour chaque obstacles
            if self.posX >= (o[0]-o[2])-15 and self.posX <= (o[0]+o[2])+15 \
               and self.posY >= (o[1]-o[3])-15 and self.posY <= (o[1]+o[3])+15:
                self.change_dir() # La fourmi change de direction si elle approche d'un obstacle
                self.normalise()  # On normalise les trajectoire

    def find_food(self, food):
        """
            Vérifie si la fourmi a trouvé de la nouriture.
            Modifie son état en fonction du résultat.
            Ne renvoie rien.
        """
        for f in food:  # Pour chaque obstacles
            if self.posX >= (f[0]-f[2]) and self.posX <= (f[0]+f[2]) \
               and self.posY >= (f[1]-f[3]) and self.posY <= (f[1]+f[3]):
                self.state == STATE[1] # La fourmi change d'état si elle atteint un point de nourriture

    def maj_pos(self):
        self.posX += PAS * self.vitesseX  # On multiplie la vitesse normée
        self.posY += PAS * self.vitesseY  # par le pas pour avoir un déplacement fluide

    ########## COMPORTEMENT GLOBAL DE LA FOURMIS ########### (qu'on actualise à chaque itération de boucle)
    def MAJ(self, largeur, hauteur, f, obs):
        if self.state == STATE[0]:
            self.avoid_wall(0, 0, largeur, hauteur)  # Elle évite le mur
            self.avoid_obstacles(obs)  # Elle évite les obstacles
            self.find_food(f)
            self.maj_pos() # On actualise la position de la fourmi


class Environnement():
    
    def __init__(self, nb_ants, qt_food, obstacles, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.obstacles = []
        self.food = []
        self.ants = []
        self.anthill = [random()*float(largeur),  # posX et
                       random()*float(hauteur)]   # posY de la fourmillière
        for i in range(nb_ants):
            self.ants.append(Ants(self.anthill[0], self.anthill[1],  # Position de départ des fourmis
                                  random() * 2. * pi ))  # Direction aléatoire
        for i in range(qt_food):
            self.food.append([randint(0, largeur), randint(0, hauteur),
                              randint(20, 50), randint(20, 50)])
        for i in range(obstacles):
            self.obstacles.append([randint(0, largeur), randint(0, hauteur),
                                   randint(20, 50), randint(20, 50)])

    def maj_ants(self):
        """
            Met à jour la position de chaque fourmis en appelant ant.MAJ()
        """
        for ant in self.ants:
            ant.MAJ(self.largeur, self.hauteur, self.food,
                    self.obstacles)

    def maj_envi(self):
        """
            Met à jour l'environnement en appelant les fonctions dédiées à chaque types d'éléments
        """
        self.maj_ants()  # Met à jour la position de chaque fourmis
# À ÉCRIRE self.maj_food()  # Met à jour le stock de nourriture

class Fenetre(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QBasicTimer()
        self.timer.start(40, self)  # L'entier définie la vitesse de l'horloge

    def initUI(self):  # Crée la GUI
        self._envi = Environnement(5, 5, 10, 800, 600)
        # Nb de fourmis, Qt nourriture, Nb d'obstacles, Largeur, Hauteur
        self.setFixedSize(self._envi.largeur, self._envi.hauteur)
        self.setWindowTitle('Colonies de fourmis')
        self.show()

    def timerEvent(self, e):
        self._envi.maj_envi()
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
        for ant in self._envi.ants:
            qp.drawLine(ant.posX,
                        ant.posY,
                        ant.posX - 2 * ant.vitesseX,
                        ant.posY - 2 * ant.vitesseY)

        food_color = QColor(34, 124, 4)  # Dessine la nourriture (verte)
        qp.setPen(food_color)
        qp.setBrush(food_color)
        for coord in self._envi.food:
            center = QPoint(coord[0], coord[1])
            qp.drawEllipse(center, coord[2], coord[3])

        qp.setPen(Qt.black)  # Dessine les obstacles (noirs)
        qp.setBrush(Qt.black)
        for coord in self._envi.obstacles:
            center = QPoint(coord[0], coord[1])
            qp.drawEllipse(center, coord[2], coord[3])

        anthill_color = Qt.red  # Dessine la foumillière (rouge)
        qp.setPen(anthill_color)
        qp.setBrush(anthill_color)
        center = QPoint(self._envi.anthill[0], self._envi.anthill[1])
        qp.drawEllipse(center, 10, 10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fen = Fenetre()
#    print(fen.obstacles)
    sys.exit(app.exec_())
