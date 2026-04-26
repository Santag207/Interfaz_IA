import sys
import os

sys.path.append(os.path.dirname(__file__))

from Backend.configuracion import ConfigIA
from Backend.mundo import Mundo2D
from Backend.matriz_q import MatrizQ
from Backend.motor_aprendizaje import MotorQLearning


class AgenteCoordinador:
    def __init__(self):
        self.config = ConfigIA()
        self.mundo = Mundo2D(10, 10)
        self.matriz = MatrizQ(10, 10)
        self.motor = MotorQLearning(self.mundo, self.matriz, self.config)
        self.posicion_robot = self.mundo.inicio

    def reconfigurar_entorno(self, f, c):
        self.mundo.redimensionar(f, c)
        self.matriz = MatrizQ(f, c)
        self.motor.matriz = self.matriz
        self.posicion_robot = self.mundo.inicio

    def sincronizar_mapa(self, mapa_data, f, c):
        # Avisar al mundo que cambie de tamaño antes de procesar la matriz
        self.mundo.actualizar_desde_gui(mapa_data, f, c)

        # Reiniciar la Matriz Q para el nuevo tamaño
        from Backend.matriz_q import MatrizQ
        self.matriz = MatrizQ(f, c)

        # Reasignar la matriz al motor de entrenamiento
        self.motor.matriz = self.matriz
        self.posicion_agente = self.mundo.inicio

    def generar_mapa_valido(self):
        self.mundo.generar_mapa_aleatorio()
        self.matriz = MatrizQ(self.mundo.filas, self.mundo.columnas)
        self.motor.matriz = self.matriz
        self.posicion_robot = self.mundo.inicio

    def actualizar_y_entrenar(self, datos):
        self.config.actualizar(datos)

        # Extraer dimensiones del diccionario recibido
        f = int(datos.get('filas', self.mundo.filas))
        c = int(datos.get('columnas', self.mundo.columnas))

        # Forzar redimensión si hay discrepancia
        if f != self.mundo.filas or c != self.mundo.columnas:
            self.reconfigurar_entorno(f, c)

        epocas = int(datos.get('epocas', 1000))
        for _ in range(epocas):
            pos = self.mundo.inicio  # Siempre (0,0) del mundo actual
            for _ in range(200):
                nueva_pos, recompensa = self.motor.ejecutar_paso_aprendizaje(pos)
                if nueva_pos == self.mundo.meta or recompensa < -50:
                    break
                pos = nueva_pos

        # CRÍTICO: Resetear la posición del robot para la visualización posterior
        self.posicion_robot = self.mundo.inicio

    def paso_entrenamiento_visual(self):
        x, y = self.posicion_robot
        import random
        accion = random.randint(0, 3) if random.uniform(0, 1) < 0.1 else self.matriz.obtener_mejor_accion(x, y)
        nx, ny = self.motor.simular_movimiento(x, y, accion)
        recompensa, done = self.mundo.obtener_recompensa_visual(nx, ny)

        max_futuro = self.matriz.obtener_max_q(nx, ny)
        q_actual = self.matriz.obtener_valor(x, y, accion)
        nuevo_q = q_actual + self.config.alpha * (recompensa + self.config.gamma * max_futuro - q_actual)
        self.matriz.actualizar(x, y, accion, nuevo_q)

        self.posicion_robot = self.mundo.inicio if done else (nx, ny)
        return self.obtener_estado_visual()

    def paso_prueba(self):
        x, y = self.posicion_robot
        accion = self.matriz.obtener_mejor_accion(x, y)
        nx, ny = self.motor.simular_movimiento(x, y, accion)
        if (nx, ny) == self.mundo.meta or self.mundo.tablero[nx][ny] == 1:
            self.posicion_robot = self.mundo.inicio
        else:
            self.posicion_robot = (nx, ny)

    def obtener_estado_visual(self):
        return {
            "posicion": self.posicion_robot,
            "mapa": self.matriz.estructurar_para_gui(self.mundo),
            "dimensiones": {"f": self.mundo.filas, "c": self.mundo.columnas}
        }