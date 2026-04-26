import random

class MotorQLearning:
    def __init__(self, mundo, matriz, config):
        self.mundo = mundo
        self.matriz = matriz
        self.config = config
        self.acciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Arriba, Abajo, Izq, Der

    def simular_movimiento(self, x, y, accion_idx):
        dx, dy = self.acciones[accion_idx]
        nx, ny = x + dx, y + dy
        if self.mundo.es_movimiento_valido(nx, ny):
            return nx, ny
        return x, y  # Choca con el borde

    def ejecutar_paso_aprendizaje(self, estado_actual):
        x, y = estado_actual
        # Epsilon-greedy
        accion_idx = random.randint(0, 3) if random.uniform(0, 1) < 0.1 else self.matriz.obtener_mejor_accion(x, y)

        nx, ny = self.simular_movimiento(x, y, accion_idx)

        # Recompensa
        if (nx, ny) == self.mundo.meta:
            recompensa = 100
        elif self.mundo.tablero[nx][ny] == 1:
            recompensa = -100
        else:
            recompensa = -1

        # Bellman
        max_futuro = self.matriz.obtener_max_q(nx, ny)
        q_actual = self.matriz.obtener_valor(x, y, accion_idx)
        nuevo_q = q_actual + self.config.alpha * (recompensa + self.config.gamma * max_futuro - q_actual)
        self.matriz.actualizar(x, y, accion_idx, nuevo_q)

        return (nx, ny), recompensa