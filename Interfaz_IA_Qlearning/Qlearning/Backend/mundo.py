import random


class Mundo2D:
    def __init__(self, filas=10, columnas=10):
        self.filas = filas
        self.columnas = columnas
        self.inicio = (0, 0)
        self.meta = (filas - 1, columnas - 1)
        self.tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
        self.tablero[self.meta[0]][self.meta[1]] = 2

    def redimensionar(self, f, c):
        self.filas = f
        self.columnas = c
        self.inicio = (0, 0)
        self.meta = (f - 1, c - 1)
        self.tablero = [[0 for _ in range(c)] for _ in range(f)]
        self.tablero[self.meta[0]][self.meta[1]] = 2

    def actualizar_desde_gui(self, matriz_gui, f, c):
        self.filas = f
        self.columnas = c
        # Recrear el tablero con el nuevo tamaño para evitar el IndexError
        self.tablero = [[0 for _ in range(c)] for _ in range(f)]

        for fila_idx in range(f):
            for col_idx in range(c):
                # Aquí ya no habrá IndexError porque el bucle respeta el nuevo f y c
                self.tablero[fila_idx][col_idx] = matriz_gui[fila_idx][col_idx]

    def generar_mapa_aleatorio(self):
        # 'self.filas' y 'self.columnas' deben ser las actuales
        # Creamos el tablero nuevo
        nuevo_tablero = [[0 for _ in range(self.columnas)] for _ in range(self.filas)]

        # RECALCULAR META DINÁMICAMENTE
        # Esto asegura que si el mapa es 6x6, la meta sea (5,5) y no (9,9)
        self.meta = (self.filas - 1, self.columnas - 1)
        self.inicio = (0, 0)

        # Colocar inicio y meta en el nuevo tablero
        nuevo_tablero[self.inicio[0]][self.inicio[1]] = 0  # Opcional, ya es 0
        nuevo_tablero[self.meta[0]][self.meta[1]] = 2  # <--- AQUÍ YA NO DARÁ ERROR

        # Lógica de muros aleatorios (ejemplo 20%)
        import random
        n_muros = int((self.filas * self.columnas) * 0.2)
        muros_cont = 0
        while muros_cont < n_muros:
            r_f = random.randint(0, self.filas - 1)
            r_c = random.randint(0, self.columnas - 1)
            if (r_f, r_c) != self.inicio and (r_f, r_c) != self.meta:
                if nuevo_tablero[r_f][r_c] == 0:
                    nuevo_tablero[r_f][r_c] = 1
                    muros_cont += 1

        self.tablero = nuevo_tablero

    def existe_camino(self, tablero):
        """Algoritmo BFS para asegurar que el mapa es resoluble."""
        queue = [self.inicio]
        visitados = {self.inicio}
        while queue:
            f, c = queue.pop(0)
            if (f, c) == self.meta: return True
            for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nf, nc = f + df, c + dc
                if 0 <= nf < self.filas and 0 <= nc < self.columnas and \
                        tablero[nf][nc] != 1 and (nf, nc) not in visitados:
                    visitados.add((nf, nc))
                    queue.append((nf, nc))
        return False

    def es_movimiento_valido(self, x, y):
        return 0 <= x < self.filas and 0 <= y < self.columnas

    def obtener_recompensa_visual(self, x, y):
        if (x, y) == self.meta: return 100, True
        if self.tablero[x][y] == 1: return -100, True
        return -1, False