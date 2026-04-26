import numpy as np

class TurtleEnv:
    def __init__(self, map_file, size=50):
        self.size = size
        self.map_file = map_file

        self.actions = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1)    # right
        }

        self.load_map()
        self.reset()

    def load_map(self):
        self.grid = np.loadtxt(self.map_file, dtype=int)
        self.goal = (self.size-1, self.size-1)
        self.grid[self.goal] = 2

    def reset(self):
       
        # Modo Aleatorio
        self.pos = (0, 0)   # siempre empieza aquí
        return self.pos

        #Modo Fijo
        """
        ===============================
        MODO ALEATORIO (COMENTAR LO DE ARRIBA
        Y DESCOMENTAR ESTO)
        ===============================
        while True:
            x = np.random.randint(0, self.size)
            y = np.random.randint(0, self.size)
            if self.grid[x, y] == 0:
                self.pos = (x, y)
                break
        return self.pos
        """

    def step(self, action):
        dx, dy = self.actions[action]
        nx = self.pos[0] + dx
        ny = self.pos[1] + dy

        # fuera del mapa
        if nx < 0 or nx >= self.size or ny < 0 or ny >= self.size:
            return self.pos, -5, False

        # colisión con obstáculo
        if self.grid[nx, ny] == 1:
            return self.pos, -10, False

        self.pos = (nx, ny)

        # meta
        if self.pos == self.goal:
            return self.pos, 100, True

        # shaping suave
        dist = abs(self.goal[0] - nx) + abs(self.goal[1] - ny)
        reward = -0.01 * dist
        return self.pos, reward, False
