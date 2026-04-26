import numpy as np

def state_to_index(pos, size):
    x, y = pos
    return x * size + y

# Recompensa negativa si está cerca de obstáculo
def reward_function(pos, obstacles):
    x, y = pos[:2]
    reward = x  # incentiva moverse hacia +X
    for ox, oy in obstacles:
        dist = np.linalg.norm([x - ox, y - oy])
        if dist < 0.5:
            reward -= 5  # penaliza colisiones
    return reward
