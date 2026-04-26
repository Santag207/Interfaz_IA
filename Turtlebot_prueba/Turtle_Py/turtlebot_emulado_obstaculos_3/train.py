from world import TurtleEnv
from qlearning import QLearningAgent
from utils import state_to_index
import numpy as np

env = TurtleEnv("map50.txt", size=50)
states = env.size * env.size
actions = len(env.actions)

agent = QLearningAgent(states, actions)

episodes = 150000
max_steps = 500

success = 0

for ep in range(episodes):
    pos = env.reset()
    state = state_to_index(pos, env.size)

    for step in range(max_steps):
        action = agent.choose_action(state)
        new_pos, reward, done = env.step(action)
        next_state = state_to_index(new_pos, env.size)
        agent.update(state, action, reward, next_state)
        state = next_state
        if done:
            success += 1
            break

    agent.decay_epsilon()

    if (ep+1) % 1000 == 0:
        print(f"Episode {ep+1} | success rate: {success/1000:.2f}")
        success = 0

np.save("qtable.npy", agent.Q)
print("Entrenamiento terminado.")
