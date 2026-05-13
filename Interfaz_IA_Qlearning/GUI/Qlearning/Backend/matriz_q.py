"""
Módulo de la Tabla Q del agente Q-Learning.
Almacena y gestiona los valores Q de acciones en cada posición del mapa.
"""
import numpy as np


class MatrizQ:
    """
    Almacena y gestiona la tabla Q del agente Q-Learning.
    La tabla Q es un array 3D: [filas][columnas][4 acciones]
    
    Cada celda (x,y) contiene 4 valores Q, uno para cada acción:
        - Q[x][y][0] = Valor de acción ARRIBA
        - Q[x][y][1] = Valor de acción ABAJO
        - Q[x][y][2] = Valor de acción IZQUIERDA
        - Q[x][y][3] = Valor de acción DERECHA
    
    Un valor Q más alto indica que esa acción es mejor en esa posición.
    
    Atributos:
        tabla (np.ndarray): Array NumPy 3D de shape (filas, columnas, 4).
                           Inicializado con ceros (estado ignorante).
    """
    
    def __init__(self, filas, columnas):
        """
        Inicializa la matriz Q con ceros (el agente no conoce nada).
        
        Args:
            filas (int): Número de filas del mapa.
            columnas (int): Número de columnas del mapa.
        """
        # Crea array 3D inicializado con ceros: (filas x columnas x 4 acciones)
        self.tabla = np.zeros((filas, columnas, 4))

    def obtener_mejor_accion(self, x, y):
        """
        Obtiene la acción con mayor valor Q para una posición.
        Esta es la acción que el agente cree que es mejor (explotación).
        
        Args:
            x (int): Fila de la posición.
            y (int): Columna de la posición.
            
        Returns:
            int: Índice de la mejor acción (0-3):
                0 = ARRIBA, 1 = ABAJO, 2 = IZQUIERDA, 3 = DERECHA
        """
        # np.argmax retorna el índice del valor máximo
        return int(np.argmax(self.tabla[x, y]))

    def actualizar(self, x, y, accion, valor):
        """
        Actualiza el valor Q de una acción específica en una posición.
        Se llama después de cada paso para aplicar la fórmula Q-Learning.
        
        Args:
            x (int): Fila de la posición.
            y (int): Columna de la posición.
            accion (int): Índice de la acción (0-3).
            valor (float): Nuevo valor Q calculado.
        """
        self.tabla[x, y, accion] = valor

    def obtener_valor(self, x, y, accion):
        """
        Obtiene el valor Q actual de una acción en una posición.
        
        Args:
            x (int): Fila de la posición.
            y (int): Columna de la posición.
            accion (int): Índice de la acción (0-3).
            
        Returns:
            float: Valor Q de esa acción en esa posición.
        """
        return self.tabla[x, y, accion]

    def obtener_max_q(self, x, y):
        """
        Obtiene el máximo valor Q de una posición (entre todas sus acciones).
        Se usa en la fórmula Q-Learning: max(Q(s',a'))
        
        Args:
            x (int): Fila de la posición.
            y (int): Columna de la posición.
            
        Returns:
            float: Valor máximo Q de todas las 4 acciones en esa posición.
        """
        # np.max retorna el valor máximo de las 4 acciones
        return np.max(self.tabla[x, y])

    def estructurar_para_gui(self, mundo):
        """
        Convierte la matriz Q a formato JSON para renderizar en la interfaz gráfica.
        Prepara datos que incluyen valores Q, tipos de celda y posiciones.
        
        Args:
            mundo (Mundo2D): Referencia al mundo para obtener tipos de celdas.
            
        Returns:
            list: Lista de diccionarios, uno por cada celda:
                {
                    "x": fila,
                    "y": columna,
                    "tipo": "libre" | "muro" | "meta",
                    "q_max": valor Q máximo en esa celda,
                    "q_values": {
                        "up": valor Q acción arriba,
                        "down": valor Q acción abajo,
                        "left": valor Q acción izquierda,
                        "right": valor Q acción derecha
                    }
                }
        """
        nodos = []
        
        # Bucle por cada celda del mapa
        for f in range(mundo.filas):
            for c in range(mundo.columnas):
                # Determina tipo de celda según el tablero del mundo
                tipo = "libre"  # Por defecto es libre
                
                # Si es un muro (1), actualiza tipo
                if mundo.tablero[f][c] == 1:
                    tipo = "muro"
                # Si es la meta (2), actualiza tipo
                elif mundo.tablero[f][c] == 2:
                    tipo = "meta"

                # Construye diccionario con información de la celda
                nodos.append({
                    "x": f,
                    "y": c,
                    "tipo": tipo,
                    "q_max": float(np.max(self.tabla[f, c])),  # Máximo Q de la celda
                    "q_values": {
                        "up": float(self.tabla[f, c, 0]),      # Q para ARRIBA
                        "down": float(self.tabla[f, c, 1]),    # Q para ABAJO
                        "left": float(self.tabla[f, c, 2]),    # Q para IZQUIERDA
                        "right": float(self.tabla[f, c, 3])    # Q para DERECHA
                    }
                })
        
        return nodos