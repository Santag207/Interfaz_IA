"""
Módulo coordinador del agente Q-Learning.
Orquesta la interacción entre el mundo, matriz Q y motor de aprendizaje.
"""

# Añade carpeta Backend al path para importar módulos
sys.path.append(os.path.dirname(__file__))

from Qlearning.Backend.configuracion import ConfigIA
from Qlearning.Backend.mundo import Mundo2D
from Qlearning.Backend.matriz_q import MatrizQ
from Qlearning.Backend.motor_aprendizaje import MotorQLearning

class AgenteCoordinador:
    """
    Coordinador central del sistema Q-Learning.
    Gestiona la comunicación entre configuración, mundo, matriz Q y motor de aprendizaje.
    
    Atributos:
        config (ConfigIA): Hiperparámetros del algoritmo.
        mundo (Mundo2D): Ambiente 2D donde se mueve el agente.
        matriz (MatrizQ): Tabla Q que almacena valores de acciones.
        motor (MotorQLearning): Motor que ejecuta el algoritmo Q-Learning.
        posicion_robot (tuple): Posición actual del agente (x, y).
    """
    
    def __init__(self):
        """Inicializa todos los componentes con valores por defecto (10x10)."""
        self.config = ConfigIA()  # Hiperparámetros por defecto
        self.mundo = Mundo2D(10, 10)  # Mundo 10x10 vacío
        self.matriz = MatrizQ(10, 10)  # Matriz Q 10x10 con 4 acciones
        self.motor = MotorQLearning(self.mundo, self.matriz, self.config)  # Motor con referencias
        self.posicion_robot = self.mundo.inicio  # Inicia en (0, 0)

    def reconfigurar_entorno(self, f, c):
        """
        Redimensiona el mundo y reinicia la matriz Q.
        
        Args:
            f (int): Nuevas filas.
            c (int): Nuevas columnas.
        """
        self.mundo.redimensionar(f, c)  # Redimensiona mundo
        self.matriz = MatrizQ(f, c)  # Crea nueva matriz Q con nuevas dimensiones
        self.motor.matriz = self.matriz  # Actualiza referencia en motor
        self.posicion_robot = self.mundo.inicio  # Resetea posición a inicio

    def sincronizar_mapa(self, mapa_data, f, c):
        """
        Carga un mapa desde la interfaz gráfica y sincroniza dimensiones.
        
        Args:
            mapa_data (list): Matriz 2D del mapa desde frontend.
            f (int): Filas del mapa.
            c (int): Columnas del mapa.
        """
        self.mundo.actualizar_desde_gui(mapa_data, f, c)  # Actualiza tablero del mundo
        self.matriz = MatrizQ(f, c)  # Crea nueva matriz Q
        self.motor.matriz = self.matriz  # Actualiza referencia en motor
        self.posicion_agente = self.mundo.inicio  # Resetea posición

    def generar_mapa_valido(self):
        """Genera un mapa aleatorio válido (con solución garantizada)."""
        self.mundo.generar_mapa_aleatorio()  # Genera mapa con ~20% obstáculos
        self.matriz = MatrizQ(self.mundo.filas, self.mundo.columnas)  # Nueva matriz Q
        self.motor.matriz = self.matriz  # Actualiza referencia
        self.posicion_robot = self.mundo.inicio  # Resetea posición

    def actualizar_y_entrenar(self, datos):
        """
        Actualiza configuración y entrena el agente durante N épocas.
        
        Args:
            datos (dict): Diccionario con hiperparámetros y mapa desde frontend.
                - alpha, gamma, epsilon, epocas
                - r_meta, r_muro, r_paso (recompensas)
                - filas, columnas, mapa
        """
        self.config.actualizar(datos)  # Actualiza hiperparámetros
        
        # Obtiene dimensiones del request
        f = int(datos.get('filas', self.mundo.filas))
        c = int(datos.get('columnas', self.mundo.columnas))
        
        # Si las dimensiones cambiaron, reconfigura el entorno
        if f != self.mundo.filas or c != self.mundo.columnas:
            self.reconfigurar_entorno(f, c)
        
        # Obtiene número de épocas
        epocas = int(datos.get('epocas', 1000))
        
        # Bucle de entrenamiento: ejecuta N épocas
        for _ in range(epocas):
            pos = self.mundo.inicio  # Inicia cada época en (0, 0)
            
            # Bucle interno: máximo 200 pasos por época
            for _ in range(200):
                nueva_pos, recompensa = self.motor.ejecutar_paso_aprendizaje(pos)
                
                # Termina la época si llegó a meta o chocó con muro
                if nueva_pos == self.mundo.meta or recompensa < -50:
                    break
                
                pos = nueva_pos
        
        self.posicion_robot = self.mundo.inicio  # Resetea posición al final

    def paso_entrenamiento_visual(self):
        """
        Ejecuta un paso de Q-Learning con visualización en tiempo real.
        
        Returns:
            dict: Estado visual con posición, mapa y dimensiones.
        """
        x, y = self.posicion_robot  # Obtiene posición actual
        
        import random
        # Selecciona acción: 10% exploración (random), 90% explotación (mejor Q)
        accion = random.randint(0, 3) if random.uniform(0, 1) < 0.1 else self.matriz.obtener_mejor_accion(x, y)
        
        # Simula el movimiento
        nx, ny = self.motor.simular_movimiento(x, y, accion)
        
        # Obtiene recompensa por el movimiento
        recompensa, done = self.mundo.obtener_recompensa_visual(nx, ny)
        
        # Calcula máximo Q del siguiente estado (para la fórmula de Q-Learning)
        max_futuro = self.matriz.obtener_max_q(nx, ny)
        
        # Obtiene valor Q actual
        q_actual = self.matriz.obtener_valor(x, y, accion)
        
        # Aplicación de fórmula Q-Learning: Q = Q + α(r + γ·max(Q') - Q)
        nuevo_q = q_actual + self.config.alpha * (recompensa + self.config.gamma * max_futuro - q_actual)
        
        # Actualiza la matriz Q
        self.matriz.actualizar(x, y, accion, nuevo_q)
        
        # Actualiza posición: reinicia si terminó, sino usa nueva posición
        self.posicion_robot = self.mundo.inicio if done else (nx, ny)
        
        # Retorna estado para renderizar
        return self.obtener_estado_visual()

    def paso_prueba(self):
        """
        Ejecuta un paso de simulación sin aprendizaje (solo explotación).
        El agente usa sus conocimientos Q para decidir la mejor acción.
        """
        x, y = self.posicion_robot  # Obtiene posición actual
        
        # Obtiene mejor acción según matriz Q
        accion = self.matriz.obtener_mejor_accion(x, y)
        
        # Simula el movimiento
        nx, ny = self.motor.simular_movimiento(x, y, accion)
        
        # Si llegó a meta o chocó con muro, reinicia posición
        if (nx, ny) == self.mundo.meta or self.mundo.tablero[nx][ny] == 1:
            self.posicion_robot = self.mundo.inicio
        else:
            # Si no, se mueve a la nueva posición
            self.posicion_robot = (nx, ny)

    def obtener_estado_visual(self):
        """
        Retorna el estado actual en formato JSON para renderizar en GUI.
        
        Returns:
            dict: Diccionario con:
                - posicion: tupla (x, y) del agente
                - mapa: lista de nodos con valores Q para cada celda
                - dimensiones: diccionario con filas y columnas
        """
        return {
            "posicion": self.posicion_robot,
            "mapa": self.matriz.estructurar_para_gui(self.mundo),
            "dimensiones": {"f": self.mundo.filas, "c": self.mundo.columnas}
        }