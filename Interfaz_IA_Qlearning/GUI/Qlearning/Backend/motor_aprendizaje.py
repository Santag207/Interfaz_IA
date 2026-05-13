"""
Módulo del motor Q-Learning.
Implementa el algoritmo de aprendizaje por refuerzo Q-Learning.
"""
import random


class MotorQLearning:
    """
    Motor que ejecuta el algoritmo Q-Learning.
    
    Implementa la fórmula de actualización:
        Q(s,a) ← Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
    
    Donde:
        s = estado actual (posición x,y)
        a = acción tomada
        r = recompensa recibida
        s' = siguiente estado
        α (alpha) = tasa de aprendizaje
        γ (gamma) = factor de descuento
    
    Atributos:
        mundo (Mundo2D): Referencia al ambiente.
        matriz (MatrizQ): Referencia a la tabla Q.
        config (ConfigIA): Referencia a configuración.
        acciones (list): Lista de movimientos [(x_delta, y_delta), ...]
    """
    
    def __init__(self, mundo, matriz, config):
        """
        Inicializa el motor con referencias a mundo, matriz Q y configuración.
        
        Args:
            mundo (Mundo2D): Ambiente del agente.
            matriz (MatrizQ): Tabla Q del agente.
            config (ConfigIA): Hiperparámetros.
        """
        self.mundo = mundo
        self.matriz = matriz
        self.config = config
        # Define los 4 movimientos posibles: Arriba, Abajo, Izquierda, Derecha
        self.acciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def simular_movimiento(self, x, y, accion_idx):
        """
        Simula un movimiento validando que esté dentro de los límites del mundo.
        Si la posición nueva es inválida, el agente se queda en su lugar.
        
        Args:
            x (int): Fila actual.
            y (int): Columna actual.
            accion_idx (int): Índice de la acción (0-3):
                0 = ARRIBA (-1, 0)
                1 = ABAJO (1, 0)
                2 = IZQUIERDA (0, -1)
                3 = DERECHA (0, 1)
        
        Returns:
            tuple: Nueva posición (nx, ny). Si es inválida, retorna posición actual.
        """
        # Obtiene desplazamiento de la acción
        dx, dy = self.acciones[accion_idx]
        
        # Calcula nueva posición
        nx, ny = x + dx, y + dy
        
        # Valida que nueva posición esté dentro del mundo
        if self.mundo.es_movimiento_valido(nx, ny):
            return nx, ny  # Movimiento válido
        
        # Si es inválido, se queda en lugar
        return x, y

    def ejecutar_paso_aprendizaje(self, estado_actual):
        """
        Ejecuta un paso completo del algoritmo Q-Learning.
        
        Proceso:
            1. Selecciona acción (10% exploración vs 90% explotación)
            2. Simula movimiento
            3. Calcula recompensa
            4. Aplica fórmula Q-Learning
            5. Actualiza matriz Q
        
        Args:
            estado_actual (tuple): Posición actual (x, y).
        
        Returns:
            tuple: (nueva_posicion, recompensa)
                - nueva_posicion: tupla (x, y) de la nueva posición
                - recompensa: float con la recompensa recibida
        """
        x, y = estado_actual  # Desempaqueta estado actual
        
        # SELECCIÓN DE ACCIÓN: Exploración vs Explotación
        # Con 10% de probabilidad elige acción aleatoria (exploración)
        # Con 90% de probabilidad elige mejor acción según Q (explotación)
        random_value = random.uniform(0, 1)
        
        if random_value < 0.1:
            # Exploración: acción aleatoria (10%)
            accion_idx = random.randint(0, 3)
        else:
            # Explotación: mejor acción según matriz Q (90%)
            accion_idx = self.matriz.obtener_mejor_accion(x, y)
        
        # SIMULACIÓN DE MOVIMIENTO
        nx, ny = self.simular_movimiento(x, y, accion_idx)
        
        # CÁLCULO DE RECOMPENSA según lo que sucedió
        if (nx, ny) == self.mundo.meta:
            # Llegó al objetivo: recompensa máxima
            recompensa = 100
        elif self.mundo.tablero[nx][ny] == 1:
            # Chocó con muro: penalización máxima
            recompensa = -100
        else:
            # Movimiento normal: penalización por paso
            recompensa = -1
        
        # FÓRMULA DE Q-LEARNING: Q(s,a) ← Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
        
        # Paso 1: Obtiene máximo Q del siguiente estado
        max_futuro = self.matriz.obtener_max_q(nx, ny)
        
        # Paso 2: Obtiene Q actual de la acción en el estado actual
        q_actual = self.matriz.obtener_valor(x, y, accion_idx)
        
        # Paso 3: Calcula nuevo Q aplicando la fórmula
        # Diferencia temporal: r + γ·max(Q') - Q (lo que aprendemos)
        # Se multiplica por α (qué porcentaje aplicamos del aprendizaje)
        nuevo_q = q_actual + self.config.alpha * (recompensa + self.config.gamma * max_futuro - q_actual)
        
        # ACTUALIZACIÓN DE MATRIZ Q
        self.matriz.actualizar(x, y, accion_idx, nuevo_q)
        
        # Retorna nueva posición y recompensa
        return (nx, ny), recompensa