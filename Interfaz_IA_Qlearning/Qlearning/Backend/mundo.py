"""
Módulo del ambiente 2D del agente.
Gestiona el mapa con obstáculos, inicio y objetivo.
"""
import random


class Mundo2D:
    """
    Representa el ambiente 2D en el que se mueve el agente.
    Gestiona el tablero, obstáculos, posiciones de inicio y meta.
    
    Valores del tablero:
        0 = Celda libre (el agente puede transitar)
        1 = Muro/Obstáculo (el agente no puede pasar)
        2 = Meta/Objetivo (destino del agente)
    
    Atributos:
        filas (int): Número de filas del mapa.
        columnas (int): Número de columnas del mapa.
        inicio (tuple): Posición inicial del agente (0, 0).
        meta (tuple): Posición del objetivo (filas-1, columnas-1).
        tablero (list): Matriz 2D que representa el mundo.
    """
    
    def __init__(self, filas=10, columnas=10):
        """
        Inicializa un mundo vacío con dimensiones dadas.
        
        Args:
            filas (int, optional): Número de filas. Default: 10.
            columnas (int, optional): Número de columnas. Default: 10.
        """
        self.filas = filas
        self.columnas = columnas
        self.inicio = (0, 0)  # Posición inicial: esquina superior izquierda
        self.meta = (filas - 1, columnas - 1)  # Objetivo: esquina inferior derecha
        
        # Crea tablero vacío (todas las celdas son libres)
        self.tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
        
        # Marca la meta en el tablero
        self.tablero[self.meta[0]][self.meta[1]] = 2

    def redimensionar(self, f, c):
        """
        Redimensiona el mundo a nuevas dimensiones y lo deja vacío.
        Se usa cuando el usuario cambia el tamaño del mapa.
        
        Args:
            f (int): Nuevas filas.
            c (int): Nuevas columnas.
        """
        self.filas = f
        self.columnas = c
        self.inicio = (0, 0)  # Reinicia inicio
        self.meta = (f - 1, c - 1)  # Calcula nueva meta
        
        # Crea nuevo tablero vacío
        self.tablero = [[0 for _ in range(c)] for _ in range(f)]
        
        # Marca meta en nuevo tablero
        self.tablero[self.meta[0]][self.meta[1]] = 2

    def actualizar_desde_gui(self, matriz_gui, f, c):
        """
        Carga un mapa dibujado en la interfaz gráfica.
        Se llama cuando el usuario termina de dibujar el mapa.
        
        Args:
            matriz_gui (list): Matriz 2D del mapa dibujado en frontend (0s y 1s).
            f (int): Filas del mapa.
            c (int): Columnas del mapa.
        """
        self.filas = f
        self.columnas = c
        
        # Crea nuevo tablero vacío
        self.tablero = [[0 for _ in range(c)] for _ in range(f)]

        # Bucle: copia cada celda del GUI al tablero interno
        for fila_idx in range(f):
            for col_idx in range(c):
                # Copia valor de la matriz del GUI (0=libre, 1=muro)
                self.tablero[fila_idx][col_idx] = matriz_gui[fila_idx][col_idx]

    def generar_mapa_aleatorio(self):
        """
        Genera un mapa aleatorio con aproximadamente 20% de obstáculos.
        Garantiza que el mapa sea resoluble (existe camino del inicio a meta).
        
        Proceso:
            1. Crea tablero vacío
            2. Coloca inicio y meta
            3. Genera muros aleatorios (~20% del espacio)
            4. Garantiza que no bloqueen el camino
        """
        # Crea nuevo tablero vacío
        nuevo_tablero = [[0 for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Posiciona inicio y meta
        self.meta = (self.filas - 1, self.columnas - 1)
        self.inicio = (0, 0)
        nuevo_tablero[self.inicio[0]][self.inicio[1]] = 0  # Inicio es libre
        nuevo_tablero[self.meta[0]][self.meta[1]] = 2  # Meta se marca con 2
        
        # Calcula número de muros (~20% del espacio)
        n_muros = int((self.filas * self.columnas) * 0.2)
        muros_cont = 0
        
        # Bucle: genera muros hasta alcanzar el número deseado
        while muros_cont < n_muros:
            # Genera posición aleatoria
            r_f = random.randint(0, self.filas - 1)
            r_c = random.randint(0, self.columnas - 1)
            
            # Valida que no sea inicio ni meta
            if (r_f, r_c) != self.inicio and (r_f, r_c) != self.meta:
                # Si la celda es libre, la convierte en muro
                if nuevo_tablero[r_f][r_c] == 0:
                    nuevo_tablero[r_f][r_c] = 1
                    muros_cont += 1
        
        # Asigna nuevo tablero
        self.tablero = nuevo_tablero

    def existe_camino(self, tablero):
        """
        Verifica si existe un camino válido del inicio a la meta.
        Usa algoritmo BFS (Breadth-First Search).
        
        Lógica BFS:
            1. Comienza en posición de inicio
            2. Explora todas las celdas adyacentes sin visitar
            3. Si encuentra la meta, retorna True
            4. Si agota todas las celdas sin encontrar meta, retorna False
        
        Args:
            tablero (list): Matriz 2D a verificar.
        
        Returns:
            bool: True si existe camino, False si no.
        """
        queue = [self.inicio]  # Cola con celdas por explorar
        visitados = {self.inicio}  # Conjunto de celdas ya visitadas
        
        # Bucle BFS: mientras hay celdas por explorar
        while queue:
            f, c = queue.pop(0)  # Toma primera celda de la cola
            
            # Si encontró la meta, retorna True
            if (f, c) == self.meta:
                return True
            
            # Bucle: explora las 4 direcciones (arriba, abajo, izq, der)
            for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nf, nc = f + df, c + dc
                
                # Condiciones para explorar celda adyacente
                # - Está dentro del tablero
                # - No es un muro
                # - No ha sido visitada
                if 0 <= nf < self.filas and 0 <= nc < self.columnas and \
                        tablero[nf][nc] != 1 and (nf, nc) not in visitados:
                    visitados.add((nf, nc))  # Marca como visitada
                    queue.append((nf, nc))  # Añade a la cola para explorar
        
        # Si salió del bucle sin encontrar meta, no hay camino
        return False

    def es_movimiento_valido(self, x, y):
        """
        Verifica que una posición esté dentro de los límites del mundo.
        
        Args:
            x (int): Fila.
            y (int): Columna.
        
        Returns:
            bool: True si está dentro de límites, False si no.
        """
        # Valida que coordenadas estén en rango válido
        return 0 <= x < self.filas and 0 <= y < self.columnas

    def obtener_recompensa_visual(self, x, y):
        """
        Devuelve la recompensa y si el episodio termina para entrenamiento visual.
        Se usa en paso_entrenamiento_visual para aprendizaje paso-a-paso.
        
        Args:
            x (int): Fila de la posición.
            y (int): Columna de la posición.
        
        Returns:
            tuple: (recompensa, done)
                - recompensa (int): Valor de recompensa
                - done (bool): True si el episodio terminó (meta o obstáculo)
        """
        # Si llegó a la meta: recompensa máxima y termina episodio
        if (x, y) == self.meta:
            return 100, True
        
        # Si chocó con muro: penalización máxima y termina episodio
        if self.tablero[x][y] == 1:
            return -100, True
        
        # Si es paso normal: penalización leve y sigue el episodio
        return -1, False