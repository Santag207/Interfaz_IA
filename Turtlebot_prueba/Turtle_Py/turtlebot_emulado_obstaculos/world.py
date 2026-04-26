import numpy as np

class TurtleEnv:
    def __init__(self, size=10):
        self.size = size

        self.grid = np.zeros((size, size))

        self.obstacles = [
            (2,2), (2,3), (2,4),
            (5,5), (6,5), (7,5),
            (4,8), (5,8)
        ]

        for o in self.obstacles:
            self.grid[o] = 1

        self.goal = (9,9)
        self.grid[self.goal] = 2

        self.actions = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1)    # right
        }

        self.reset()

    def reset(self):
        self.pos = (0,0)
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
