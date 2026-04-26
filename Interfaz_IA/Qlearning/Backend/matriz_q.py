import numpy as np


class MatrizQ:
    def __init__(self, filas, columnas):
        self.tabla = np.zeros((filas, columnas, 4))

    def obtener_mejor_accion(self, x, y):
        return int(np.argmax(self.tabla[x, y]))

    def actualizar(self, x, y, accion, valor):
        self.tabla[x, y, accion] = valor

    def obtener_valor(self, x, y, accion):
        return self.tabla[x, y, accion]

    def obtener_max_q(self, x, y):
        return np.max(self.tabla[x, y])

    def estructurar_para_gui(self, mundo):
        nodos = []
        for f in range(mundo.filas):
            for c in range(mundo.columnas):
                tipo = "libre"
                if mundo.tablero[f][c] == 1:
                    tipo = "muro"
                elif mundo.tablero[f][c] == 2:
                    tipo = "meta"

                nodos.append({
                    "x": f, "y": c,
                    "tipo": tipo,
                    "q_max": float(np.max(self.tabla[f, c])),
                    "q_values": {
                        "up": float(self.tabla[f, c, 0]),
                        "down": float(self.tabla[f, c, 1]),
                        "left": float(self.tabla[f, c, 2]),
                        "right": float(self.tabla[f, c, 3])
                    }
                })
        return nodos