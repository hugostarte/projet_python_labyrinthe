import pyxel
import numpy as np
import random

class Labyrinthe:
    def __init__(self, largeur=31, hauteur=21, taille_case=32):
        self.largeur = largeur if largeur % 2 == 1 else largeur + 1
        self.hauteur = hauteur if hauteur % 2 == 1 else hauteur + 1
        self.taille_case = taille_case

        self.labyrinthe = np.zeros((self.hauteur, self.largeur), dtype=np.uint8)
        self.generer_labyrinthe()

        self.fils_pos = [1, 1]
        self.fils_direction = "haut"
        self.pere_pos = [1, 1]
        self.pere_direction = "haut"
        
        self.sortie = [self.largeur - 2, self.hauteur - 2]
        self.traces = []
        
        self.compteur_frames = 0
        self.delai_pere = 8
        self.delai_debut_pere = 80
        self.delai_fils = 6  
        self.derniere_frame_fils = 0
        
        self.portee_vision = 4

        largeur_fenetre = min(1280, self.largeur * self.taille_case)
        hauteur_fenetre = min(720, self.hauteur * self.taille_case)
        pyxel.init(largeur_fenetre, hauteur_fenetre, title="Labyrinthe")
        pyxel.load("labyrinth_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def generer_labyrinthe(self):
        self.labyrinthe.fill(1)
        pile = [(1, 1)]
        self.labyrinthe[1, 1] = 0

        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        while pile:
            x, y = pile[-1]
            voisins = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.largeur - 1 and 1 <= ny < self.hauteur - 1:
                    if self.labyrinthe[ny, nx] == 1:
                        voisins.append((nx, ny, dx, dy))

            if voisins:
                nx, ny, dx, dy = random.choice(voisins)
                self.labyrinthe[y + dy // 2, x + dx // 2] = 0
                self.labyrinthe[ny, nx] = 0
                pile.append((nx, ny))
            else:
                pile.pop()

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.compteur_frames += 1
    
        if self.compteur_frames - self.derniere_frame_fils >= self.delai_fils:
            self.deplacer_fils()
        
        if self.compteur_frames >= self.delai_debut_pere:
            if self.compteur_frames % self.delai_pere == 0:
                self.deplacer_pere()

            if self.fils_pos == self.pere_pos:
                print("Perdu ! Le père vous a attrapé !")
                pyxel.quit()
                return

    def deplacer_fils(self):
        dx, dy = 0, 0

        if pyxel.btn(pyxel.KEY_UP):
            dy = -1
            self.fils_direction = "haut"
        elif pyxel.btn(pyxel.KEY_DOWN):
            dy = 1
            self.fils_direction = "bas"
        elif pyxel.btn(pyxel.KEY_LEFT):
            dx = -1
            self.fils_direction = "gauche"
        elif pyxel.btn(pyxel.KEY_RIGHT):
            dx = 1
            self.fils_direction = "droite"

        if dx != 0 or dy != 0:
            nouvelle_x = self.fils_pos[0] + dx
            nouvelle_y = self.fils_pos[1] + dy
            
            if (0 <= nouvelle_x < self.largeur and 
                0 <= nouvelle_y < self.hauteur and 
                self.labyrinthe[nouvelle_y, nouvelle_x] == 0):
                
                self.fils_pos = [nouvelle_x, nouvelle_y]
                self.traces.append({"pos": (nouvelle_x, nouvelle_y)})
                self.derniere_frame_fils = self.compteur_frames

                if self.fils_pos == self.sortie:
                    print("Gagné ! Vous avez atteint la sortie !")
                    pyxel.quit()
                    return

    def deplacer_pere(self):
        if not self.traces:
            return
            
        trace_cible = self.traces[0]["pos"]
        
        dx = trace_cible[0] - self.pere_pos[0]
        dy = trace_cible[1] - self.pere_pos[1]
     
        if dx == 0 and dy == 0:
            self.traces.pop(0)
            return
            
        # horizontal
        if dx != 0:
            nouvelle_x = self.pere_pos[0] + (1 if dx > 0 else -1)
            if (0 <= nouvelle_x < self.largeur and 
                self.labyrinthe[self.pere_pos[1], nouvelle_x] == 0):
                self.pere_pos[0] = nouvelle_x
                if dx > 0:
                    self.pere_direction = "droite"
                else:
                    self.pere_direction = "gauche"
                return
                
        # vertical
        if dy != 0:
            nouvelle_y = self.pere_pos[1] + (1 if dy > 0 else -1)
            if (0 <= nouvelle_y < self.hauteur and 
                self.labyrinthe[nouvelle_y, self.pere_pos[0]] == 0):
                self.pere_pos[1] = nouvelle_y
                if dy > 0:
                    self.pere_direction = "bas"
                else:
                    self.pere_direction = "haut"
                return

    def est_dans_vision(self, x, y):
        dx = abs(x - self.fils_pos[0])
        dy = abs(y - self.fils_pos[1])
        return dx * dx + dy * dy <= self.portee_vision * self.portee_vision

    def draw(self):
        pyxel.cls(0)

        camera_x = max(0, min(self.fils_pos[0] * self.taille_case - pyxel.width // 2,
                            self.largeur * self.taille_case - pyxel.width))
        camera_y = max(0, min(self.fils_pos[1] * self.taille_case - pyxel.height // 2,
                            self.hauteur * self.taille_case - pyxel.height))

        debut_x = max(0, camera_x // self.taille_case)
        fin_x = min(self.largeur, (camera_x + pyxel.width + self.taille_case - 1) // self.taille_case)
        debut_y = max(0, camera_y // self.taille_case)
        fin_y = min(self.hauteur, (camera_y + pyxel.height + self.taille_case - 1) // self.taille_case)
       
        # labyrinthe
        for y in range(debut_y, fin_y):
            for x in range(debut_x, fin_x):
                if self.est_dans_vision(x, y):
                    ecran_x = x * self.taille_case - camera_x
                    ecran_y = y * self.taille_case - camera_y
                    if self.labyrinthe[y, x] == 0:
                        pyxel.blt(ecran_x, ecran_y, 0, 0, 0, self.taille_case, self.taille_case, 0)
                    else:
                        pyxel.blt(ecran_x, ecran_y, 0, self.taille_case, 0, self.taille_case, self.taille_case, 0)

        # traces
        for trace in self.traces:
            tx, ty = trace["pos"]
            if self.est_dans_vision(tx, ty):
                ecran_x = tx * self.taille_case - camera_x
                ecran_y = ty * self.taille_case - camera_y
                pyxel.blt(ecran_x, ecran_y, 0, 0, 3*self.taille_case, self.taille_case, self.taille_case, 0)

        # sortie
        sx, sy = self.sortie
        if self.est_dans_vision(sx, sy):
            ecran_x = sx * self.taille_case - camera_x
            ecran_y = sy * self.taille_case - camera_y
            pyxel.blt(ecran_x, ecran_y, 0, 2*self.taille_case, 0, self.taille_case, self.taille_case, 0)

        # Le Padré
        px, py = self.pere_pos
        if self.est_dans_vision(px, py):
            ecran_x = px * self.taille_case - camera_x
            ecran_y = py * self.taille_case - camera_y
            sprite_pere = {
                "haut": 0,
                "bas": self.taille_case,
                "gauche": 2*self.taille_case,
                "droite": 3*self.taille_case
            }.get(self.pere_direction, 0)
            pyxel.blt(ecran_x, ecran_y, 0, sprite_pere, 2*self.taille_case, self.taille_case, self.taille_case, 0)

        # Filston
        fx, fy = self.fils_pos
        ecran_x = fx * self.taille_case - camera_x
        ecran_y = fy * self.taille_case - camera_y
        sprite_fils = {
            "haut": self.taille_case,
            "bas": 0,
            "gauche": 2*self.taille_case,
            "droite": 2*self.taille_case
        }.get(self.fils_direction, 0)
        largeur = -self.taille_case if self.fils_direction == "droite" else self.taille_case
        pyxel.blt(ecran_x, ecran_y, 0, sprite_fils, self.taille_case, largeur, self.taille_case, 0)

Labyrinthe()
