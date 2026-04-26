import pygame
import numpy as np
import os
import random
from world import TurtleEnv
from utils import state_to_index

CELL = 60

env = TurtleEnv("map.txt")
GRID = env.size
WIDTH = CELL * GRID
HEIGHT = CELL * GRID

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,200,0)
BLUE  = (0,0,200)
GRAY  = (150,150,150)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turtlebot RL Simulator")

clock = pygame.time.Clock()

# ---- carga robusta de política ----
if os.path.exists("qtable.npy"):
    Q = np.load("qtable.npy")
    USE_Q = True
    print("Modo: AGENTE ENTRENADO")
else:
    USE_Q = False
    print("Modo: AGENTE SIN ENTRENAR (baseline aleatorio)")

pos = env.reset()
state = state_to_index(pos, env.size)
done = False

def draw():
    screen.fill(WHITE)

    for i in range(GRID):
        for j in range(GRID):
            rect = pygame.Rect(j*CELL, i*CELL, CELL, CELL)

            if env.grid[i,j] == 1:
                pygame.draw.rect(screen, GRAY, rect)
            elif env.grid[i,j] == 2:
                pygame.draw.rect(screen, GREEN, rect)

            pygame.draw.rect(screen, BLACK, rect, 1)

    x,y = env.pos
    robot = pygame.Rect(y*CELL+10, x*CELL+10, CELL-20, CELL-20)
    pygame.draw.rect(screen, BLUE, robot)

    pygame.display.flip()

running = True
while running:
    clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not done:
        draw()

        if USE_Q:
            action = Q[state].argmax()
        else:
            action = random.randint(0,3)

        pos, reward, done = env.step(action)
        state = state_to_index(pos, env.size)

    else:
        draw()

pygame.quit()
