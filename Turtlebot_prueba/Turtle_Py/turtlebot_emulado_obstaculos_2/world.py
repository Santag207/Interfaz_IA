import numpy as np

class TurtleEnv:
    def __init__(self, map_file="map.txt"):
        self.map_file = map_file
        self._load_map()

        self.actions = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1)    # right
        }

        self.reset()

    def _load_map(self):
        with open(self.map_file) as f:
            lines = [line.strip().split() for line in f.readlines()]

        self.size = len(lines)
        self.grid = np.zeros((self.size, self.size))

        for i in range(self.size):
            for j in range(self.size):
                if lines[i][j] == "#":
                    self.grid[i,j] = 1
                elif lines[i][j] == "G":
                    self.grid[i,j] = 2
                    self.goal = (i,j)
                elif lines[i][j] == "S":
                    self.start = (i,j)

    def reset(self):
        self.pos = self.start
        return self.pos

    def step(self, action):
        dx, dy = self.actions[action]
        nx = self.pos[0] + dx
        ny = self.pos[1] + dy

        if nx < 0 or nx >= self.size or ny < 0 or ny >= self.size:
            return self.pos, -5, False

        if self.grid[nx, ny] == 1:
            return self.pos, -10, False

        self.pos = (nx, ny)

        if self.pos == self.goal:
            return self.pos, 100, True

        return self.pos, -1, False
