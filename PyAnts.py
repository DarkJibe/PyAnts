# #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##################### Simulateur de colonies de fourmis ########################
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# #  #  #  #  #  #  #  #  #  !!! NÉCESSITE PyQt5 !!! #  #  #  #  #  #  #  #  # #
################################################################################
####################### Réalisé par JB Manchon (2134945) #######################
########################### M1 S8 Sciences Cognitives ##########################
############################## Licence GPL (2017) ##############################
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##                                                                          ####
####            RÈGLES DU JEU :                                             ####
##                                                                          ####
## Si une fourmi cherchant de la nouriture tombe sur une trace de phéromone ####
## elle la suit selon une probabilité définit par FOLLOW_PB.                ####
## Si une fourmi trouve de la nourriture, elle la rapporte à la fourmilière ####
##    -> puis elle recommence à chercher. (MODE 0)                          ####
## OU -> elle retourne directement au point de nourriture trouvé. (MODE 1)  ####
##                                                                          ####
#####           PARAMÈTRES MODIFIABLES PAR L'UTILISATEUR :                  ####
##                                                                          ####
NB_ANTS = 50        # Nombre de fourmis                                     ####
NB_FOOD = 20        # Nombre de points de nourriture                        ####
QT_FOOD = 100       # Quantité de nourriture par point                      ####
NB_OBS = 15         # Nombre l'obstacles                                    ####
PAS = 4             # Rapidité de déplacement des fourmis                   ####
EVAP = 50           # Vitesse d'évaporation des traces de phéromone         ####
ACUITY = 1          # Accuité de détéction des traces de phéromone (0-2)    ####
FOLLOW_PB = 0.75    # Probabilité de suivre une trace de phéromone          ####
MODE = 1            # Mode 0 : Fourmis classiques | Mode 1 : Super-fourmis  ####
##                                                                          ####
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
################################################################################
##                                                                          ####
#####           CRITIQUES / AMÉLIORATIONS POSSIBLES :                       ####
##                                                                          ####
## Les obstacles ne sont pas toujours très bien évités, il arrive parfois   ####
## que des groupes de fourmis restent bloqués dessus à cause des phéromones ####
## (surtout lorsque ACUITY = 2).                                            ####
##                                                                          ####
## Il n'y a actuellement aucune pondération de la probabilité de suivre une ####
## trace de phéromone en fonction de sa force (du nombre de fourmis passées ####
## par là récemment), ce qui est contraire au comportement des fourmis.     ####
##                                                                          ####
#####           NE PAS MODIFIER :                                           ####
##                                                                          ####
STATE = ["FORAGING", "GOBACK", "WORKING"]  # États possibles des fourmi     ####
##                                                                          ####
################################################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #

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
        self.direction = direction  # Direction de départ (aléatoire)
        self.vitesseX = cos(self.direction)  # Vecteur de vitesse
        self.vitesseY = sin(self.direction)
        self.state = STATE[0]  # État de la fourmi
        self.prev_choice = None  # Précédent choix de trajectoire
                                 # lors d'un évitement d'obstacle
        self.found_food = None  # Cordonnées du point de nourriture trouvé

    def __repr__(self):
        return "[{}, {}]".format(self.posX, self.posY)  # Pour le debug

    def normalise(self):
        """
            Normalise la vitesse de la fourmi pour conserver sa taille.
            Ne renvoie rien.
        """
        norme = sqrt(self.vitesseX**2 + self.vitesseY**2)
        try:
            self.vitesseX /= norme
            self.vitesseY /= norme
        except ZeroDivisionError:  # Permet d'éviter un plantage du programme
            self.vitesseX /= 0.001  # si la norme devient trop petite et est 
            self.vitesseY /= 0.001  # assimilée à 0.

    def toggle_R(self):
        """
            Modifie le vecteur vitesse pour permettre à la fourmi de
            tourner vers la droite.
            Ne renvoie rien.
        """
        self.vitesseX = 0.5*(self.vitesseY+self.vitesseX)
        self.vitesseY = 0.5*(self.vitesseY-self.vitesseX)
        self.prev_choice = "R"

    def toggle_L(self):
        """
            Modifie le vecteur vitesse pour permettre à la fourmi de
            tourner vers la gauche.
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
        if self.prev_choice == None:  # Si pas de choix précédent :
            if randint(0, 1):  
                self.toggle_L()  # 1/2 chance d'aller vers la gauche
            else:
                self.toggle_R()  # 1/2 chance d'aller vers la droite.
        elif self.prev_choice == "R":
            if random() > 0.8:  # Si droite : 80% va à gauche
                self.toggle_L()
            else:               #             20% va à droite.
                self.toggle_R()
        elif self.prev_choice == "L":
            if random() > 0.8:  # Si gauche : 80% va à droite
                self.toggle_R()
            else:               #             20% va à gauche.
                self.toggle_L()
        self.normalise()  # On normalise les trajectoire.

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
        self.normalise()  # On normalise les trajectoire.

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
        for o in obstacles:  # Pour chaque obstacles :
            if self.posX >= (o[0]-o[2])-3 and self.posX <= (o[0]+o[2])+3 \
               and self.posY >= (o[1]-o[3])-3 and self.posY <= (o[1]+o[3])+3:
                if self.state == STATE[0]:  # La fourmi change de fortement de
                    self.change_dir()  # direction si elle approche d'un
                else:  # obstacle en mode FORAGING ou moins brusquement sinon.
                    self.change_dir2()  # Permet des trajectoires (un peu)
                return True             # plus smooth lors des évitements.
        return False

    def find_food(self, food):
        """
            Vérifie si la fourmi a trouvé de la nouriture.
            Modifie son état en fonction du résultat.
            Enregistre la position du point de nourriture trouvé.
            Renvoie un booléen.
        """
        for f in food:  # Pour chaque point de nourriture :
            if self.posX >= (f[0][0]-f[0][2])\
            and self.posX <= (f[0][0]+f[0][2])\
             and self.posY >= (f[0][1]-f[0][3])\
              and self.posY <= (f[0][1]+f[0][3]):
                # La fourmi change d'état si elle atteint un point
                # de nourriture et mémorise sa position.
                self.state = STATE[1]  # État GOBACK
                self.found_food = [f[0][0], f[0][1]]
                f[1] -= 1  # On décrémente la quantité de nourriture du point.
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
        try:
            self.vitesseX = (pos[0] - self.posX) / f
            self.vitesseY = (pos[1] - self.posY) / f
        except ZeroDivisionError:  # Permet d'éviter un plantage du programme
            self.vitesseX = (pos[0] - self.posX) / 0.001  # si le f devient 
            self.vitesseY = (pos[1] - self.posY) / 0.001  # trop petit (~=0).
        self.normalise()  # On normalise les trajectoire.

    def go_to_food(self):
        """
            Appelle self.go_to().
            Détermine la trajectoire vers le dernier point de nourriture trouvé.
            Ne renvoie rien.
        """
        self.go_to(self.found_food)  # Vers le dernier point de nourriture

    def go_back(self):
        """
            Appelle self.go_to().
            Détermine la trajectoire vers la fourmilière.
            Ne renvoie rien.
        """
        self.go_to(fen.envi.anthill)  # Vers la fourmilière

    def check_trail(self):
        """
            Vérifie si la fourmi passe près d'une trace de phéromone.
            Si oui, appelle self.go_to() pour déterminer la nouvelle trajectoire.
            Dépend de FOLLOW_PB pour la robabilité de suivre la trace.
            Renvoie un booléen.
        """
        for t in fen.envi.trails:  # Pour chaque trace de phéromone :
            # Si la position de la fourmi correspond à une trace :
            if int(self.posX) >= t[0]-ACUITY \
            and int(self.posX) <= t[0]+ACUITY \
             and int(self.posY) >= t[1]-ACUITY \
              and int(self.posY) <= t[1]+ACUITY:
                if random() < FOLLOW_PB:  # La fourmi suit la trace selon une
                    try:                  # certaine probabilité (FOLLOW_PB)
                        # Si possible, la fourmi definit comme nouveau cap
                        # la position suivante de la fourmi dont elle a capté
                        # la trace actuelle.
                        next_trail = fen.envi.trails[fen.envi.trails.index(t) \
                                                     + NB_ANTS]
                        # (index de la trace captée + nb de fourmis
                        #                         = index de la trace suivante)
                        self.go_to(next_trail)
                    except IndexError:
                        pass
                    return True
        return False

    def check_others(self):
        """
            Vérifie la collision de la fourmi avec les autres.
            Permet d'éviter que des groupes de fourmis chaotiques ne se forment.
            Appelle check_pos().
            Ne renvoie rien.
        """
        # Crée un liste de toutes les fourmis sauf elle-même.
        other_ants = [ant for ant in fen.envi.ants if ant != self]
        for ant in other_ants:  # Pour chaque autre fourmi :
            if self.check_pos([ant.posX, ant.posY]):  # Si la pos est identique
                self.change_dir2()                    # on modifie la direction.

    def check_pos(self, pos):
        """
            Vérifie si la fourmi a atteint la position passée en argument.
            Renvoie un booléen.
        """
        if int(self.posX) >= pos[0]-3 and int(self.posX) <= pos[0]+3 \
           and int(self.posY) >= pos[1]-3 and int(self.posY) <= pos[1]+3:
            return True
        return False

    def maj_pos(self):
        """
            Met à jour la position de la fourmi en fonction de
            son vecteur de vitesse et du PAS.
            Ne renvoie rien.
        """
        self.posX += PAS * self.vitesseX  # On multiplie la vitesse normée 
        #self.posX = int(self.posX)       # par le PAS
        self.posY += PAS * self.vitesseY  # pour avoir un déplacement fluide.
        #self.posY = int(self.posY)


    ############### COMPORTEMENT GLOBAL DE LA FOURMIS ##########################
    ############### (actualisé à chaque itération de boucle) ###################
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
        self.avoid_wall(0, 0, largeur, hauteur)  # Elle évite les murs.
        food_ok = self.find_food(f)  # Elle recherche la nourriture.
        if self.avoid_obstacles(obs):   # S'il y a un obstacle,
            self.maj_pos()              # elle l'évite en priorité.
        else:                           # Sinon, elle effectue ses tâches.
            self.prev_choice = None  # Réinitialise le gestionnaire d'obstacles
            if self.state == STATE[0]:  # SI FORAGING :
                if self.check_trail():  # Elle verifie les traces de phéromone
                    self.check_others()  # puis la collision avec les autres.
                self.maj_pos() # On actualise la position de la fourmi.
            elif self.state == STATE[1]:  # SI GOBACK :
                self.go_back()  # Elle rentre à la fourmilière.
                if self.check_pos(fen.envi.anthill):  # Elle vérifie
                                                      # si elle y est.
                    if MODE:                 # Si super-fourmi
                        self.state = STATE[2]  # État WORKING
                        self.go_to_food()  # Elle retourne au point
                                           # de nourriture trouvé.
                    else:                    # Si fourmi classique
                        self.state = STATE[0]  # État FORAGING
                self.maj_pos() # On actualise la position de la fourmi.
            else:  # SI WORKING :
                if MODE:  # Si super-fourmi
                    # Elle retourne au dernier point de nourriture rencontré.
                    self.go_to_food()
                    # Si il n'y a plus de nourriture à ce point :
                    if self.check_pos(self.found_food) and not food_ok:
                        self.found_food = None  # Réinitialise le point
                        self.state = STATE[0]  # État FORAGING
                self.maj_pos() # On actualise la position de la fourmi
    ############################################################################

class Environment():
    
    def __init__(self, nb_ants, nb_food, obstacles, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.obstacles = []
        self.food = []
        self.ants = []
        self.trails = []
        self.anthill = [randint(200, largeur-200),  # posX et
                       randint(200, hauteur-200)]   # posY de la fourmilière
        for i in range(nb_ants):
            self.ants.append(Ants(self.anthill[0], self.anthill[1],  # Position de départ des fourmis
                                  random() * 2. * pi ))  # Direction aléatoire
        for i in range(nb_food):  # Points de nourriture
            self.food.append([self.generator(largeur, hauteur), \
                              QT_FOOD, QT_FOOD])
        for i in range(obstacles):  # Obstacles
            self.obstacles.append(self.generator(largeur, hauteur))

    def generator(self, largeur, hauteur):
        """
            Génère une position (x, y) qui ne soit pas trop proche
            de la fourmilière afin d'éviter un comportement chaotique.
            Renvoie une liste de deux entiers.
        """
        while True:
            new = [randint(0, largeur), randint(0, hauteur), # Position du nouvel élément
                   randint(20, 50), randint(20, 50)]  # Diamètre du nouvel élément
            if (self.anthill[0]-100 > new[0] or new[0] > self.anthill[0]+100) \
               or (self.anthill[1]+100 < new[1] or new[1] < self.anthill[1]-100):
                # Vérifie que les coordonnées aléatoires ne se trouvent pas
                # dans un rayon de 200 autour des coordonnées de la fourmilière.
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
        for ant in self.ants:  # Pour chaque fourmi :
            # On ajoute sa position (entière) pour permettre une comparaison.
            self.trails.append([int(ant.posX), int(ant.posY)])
        if (len(self.trails) > (EVAP * NB_ANTS)):
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
        for f in self.food:  # Pour chaque point de nourriture :
            if f[1] < f[2]:  # Si le point a diminué depuis la dernière fois :
                f[2] = f[1]  # On actualise la nouvelle valeur de référence
                f[0][2] -= 20*0.01  # On diminue la taille de l'elipse.
                f[0][3] -= 20*0.01
            if f[1] <= 0:  # Si le point est vide, on le supprime.
                self.food.remove(f)
                
    def maj_envi(self):
        """
            Met à jour l'environnement en appelant les fonctions dédiées
            à chaque types d'éléments.
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
        self.timer.start(50, self)  # L'entier définie la vitesse de l'horloge

    def initUI(self):  # Crée la GUI
        self.envi = Environment(NB_ANTS, NB_FOOD, NB_OBS, 800, 600)
        # Nb de fourmis, Nb nourriture, Nb d'obstacles, Largeur, Hauteur
        self.setFixedSize(self.envi.largeur, self.envi.hauteur)
        self.setWindowTitle('Colonie de fourmis')
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
                        ant.posX - 3 * ant.vitesseX,
                        ant.posY - 3 * ant.vitesseY)

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
    sys.exit(app.exec_())
