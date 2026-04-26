"""
Módulo de configuración de hiperparámetros para Q-Learning.
Almacena y gestiona todos los parámetros ajustables del algoritmo.
"""


class ConfigIA:
    """
    Almacena y gestiona los hiperparámetros del algoritmo Q-Learning.
    Permite actualizar parámetros dinámicamente desde la interfaz gráfica.
    
    Atributos de Aprendizaje:
        alpha (float): Tasa de aprendizaje (0.1 por defecto) - qué tan rápido aprende
        gamma (float): Factor de descuento (0.9 por defecto) - importancia del futuro
        epsilon (float): Factor de exploración (0.1 por defecto) - 10% acciones aleatorias
        
    Atributos de Control:
        epocas (int): Número de iteraciones de entrenamiento (1000 por defecto)
        epsilon_min (float): Límite mínimo de epsilon (0.01) - no explora menos del 1%
        epsilon_decay (float): Factor de decaimiento (0.995) - reduce exploración con el tiempo
        
    Atributos de Recompensa:
        recompensa_meta (float): Recompensa por alcanzar objetivo (+100)
        penalizacion_obstaculo (float): Penalización por chocar con muro (-10)
        penalizacion_paso (float): Penalización por cada movimiento normal (-1)
    """
    
    def __init__(self):
        """Inicializa todos los hiperparámetros con valores por defecto."""
        # Parámetros de aprendizaje
        self.alpha = 0.1  # Tasa de aprendizaje
        self.gamma = 0.9  # Factor de descuento futuro
        self.epsilon = 0.1  # Factor de exploración
        self.epocas = 1000  # Número de épocas de entrenamiento

        # Parámetros de control de exploración
        self.epsilon_min = 0.01  # Límite mínimo
        self.epsilon_decay = 0.995  # Factor de decaimiento

        # Parámetros de recompensa
        self.recompensa_meta = 100  # Reward por objetivo
        self.penalizacion_obstaculo = -10  # Penalty por muro
        self.penalizacion_paso = -1  # Penalty por paso

    def actualizar(self, d):
        """
        Actualiza los parámetros desde un diccionario (típicamente del frontend).
        Solo actualiza valores presentes en el diccionario, mantiene los demás.
        
        Args:
            d (dict): Diccionario con claves opcionales:
                - 'alpha': tasa de aprendizaje
                - 'gamma': factor de descuento
                - 'epsilon': factor de exploración
                - 'epocas': número de épocas
                - 'r_meta': recompensa de meta
                - 'r_muro': penalización de muro
                - 'r_paso': penalización de paso
        """
        # Actualiza cada parámetro si existe en el diccionario, sino mantiene el valor anterior
        self.alpha = float(d.get('alpha', self.alpha))
        self.gamma = float(d.get('gamma', self.gamma))
        self.epsilon = float(d.get('epsilon', self.epsilon))
        self.epocas = int(d.get('epocas', self.epocas))
        self.recompensa_meta = float(d.get('r_meta', self.recompensa_meta))
        self.penalizacion_obstaculo = float(d.get('r_muro', self.penalizacion_obstaculo))
        self.penalizacion_paso = float(d.get('r_paso', self.penalizacion_paso))

    def decaer_epsilon(self):
        """
        Reduce gradualmente epsilon para balancear exploración-explotación.
        Conforme avanzan épocas, el agente explora menos y explota más.
        
        Lógica:
            - Si epsilon > epsilon_min, lo multiplica por decay (0.995)
            - Esto reduce epsilon lentamente: 0.1 → 0.0995 → 0.0990...
            - Nunca baja por debajo de epsilon_min
        """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay