import pyxel
import numpy as np
import random

class Labyrinthe:
    def __init__(self, largeur=31, hauteur=21, taille_case=5):
        self.largeur = largeur if largeur % 2 == 1 else largeur + 1
        self.hauteur = hauteur if hauteur % 2 == 1 else hauteur + 1
        self.taille_case = taille_case

        self.labyrinthe = np.zeros((self.hauteur, self.largeur), dtype=np.uint8)
        self._generer_labyrinthe()

        self.fils_pos = [1, 1]
        self.traces = []
        self.max_traces = 4
        self.sortie = [self.largeur - 2, self.hauteur - 2]

        self.frame_count = 0
        self.frame_delay_fils = 4
        self.last_move_frame = 0

        pyxel.init(self.largeur * self.taille_case, self.hauteur * self.taille_case, title="Labyrinthe Pyxel - Fils")
        pyxel.run(self.update, self.draw)

    def _generer_labyrinthe(self):
        self.labyrinthe.fill(0)
        
        for _ in range(self.largeur * self.hauteur // 3):
            x = random.randint(1, self.largeur - 2)
            y = random.randint(1, self.hauteur - 2)
            
            if random.choice([True, False]):
                longueur = random.randint(2, 6)
                for i in range(longueur):
                    if x + i < self.largeur - 1:
                        self.labyrinthe[y, x + i] = 1
            else:
                longueur = random.randint(2, 6)
                for i in range(longueur):
                    if y + i < self.hauteur - 1:
                        self.labyrinthe[y + i, x] = 1
        
        self.labyrinthe[1, 1] = 1
        self.labyrinthe[self.hauteur - 2, self.largeur - 2] = 1
        
        x, y = 1, 1
        while x < self.largeur - 2 or y < self.hauteur - 2:
            if x < self.largeur - 2 and random.choice([True, False]):
                x += 1
            elif y < self.hauteur - 2:
                y += 1
            self.labyrinthe[y, x] = 1

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.frame_count += 1

        moved = False
        dx, dy = 0, 0

        if pyxel.btn(pyxel.KEY_UP):
            dy = -1
            moved = True
        elif pyxel.btn(pyxel.KEY_DOWN):
            dy = 1
            moved = True
        elif pyxel.btn(pyxel.KEY_LEFT):
            dx = -1
            moved = True
        elif pyxel.btn(pyxel.KEY_RIGHT):
            dx = 1
            moved = True

        if moved and (self.frame_count - self.last_move_frame >= self.frame_delay_fils):
            nx = self.fils_pos[0] + dx
            ny = self.fils_pos[1] + dy
            if 0 <= nx < self.largeur and 0 <= ny < self.hauteur and self.labyrinthe[ny, nx] == 1:
                self.fils_pos = [nx, ny]
                self.traces.append({"pos": tuple(self.fils_pos), "vie": self.max_traces})

                for trace in self.traces:
                    trace["vie"] -= 1
                self.traces = [trace for trace in self.traces if trace["vie"] > 0]

                if self.fils_pos == self.sortie:
                    pyxel.quit()
                    print("Et c'est gagné!")
                    return

                self.last_move_frame = self.frame_count

    def draw(self):
        pyxel.cls(0)
        for y in range(self.hauteur):
            for x in range(self.largeur):
                couleur = 7 if self.labyrinthe[y, x] == 0 else 0
                pyxel.rect(x * self.taille_case, y * self.taille_case, self.taille_case, self.taille_case, couleur)

        for trace in self.traces:
            intensity = 3 + (trace["vie"] * 2)
            pyxel.rect(trace["pos"][0] * self.taille_case, trace["pos"][1] * self.taille_case, self.taille_case, self.taille_case, intensity)

        pyxel.rect(self.sortie[0] * self.taille_case, self.sortie[1] * self.taille_case, self.taille_case, self.taille_case, 8)

        pyxel.rect(self.fils_pos[0] * self.taille_case, self.fils_pos[1] * self.taille_case, self.taille_case, self.taille_case, 11)

Labyrinthe()