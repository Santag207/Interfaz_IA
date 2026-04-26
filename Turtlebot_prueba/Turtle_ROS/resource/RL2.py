import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import os
import sys

# Función para detectar la ruta base (funciona en .py y .exe)
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# GridWorld Environment
class GridWorld:
    def __init__(self, size=5, obstacles=[(1, 1), (1, 2), (2, 1), (3, 3)]):
        self.size = size
        self.obstacles = obstacles
        self.state_space = np.zeros((self.size, self.size))
        self.state = (0, 0)
        self.goal = (self.size - 1, self.size - 1)

    def step(self, action):
        x, y = self.state
        if action == 0:
            x = max(0, x - 1)
        elif action == 1:
            y = min(self.size - 1, y + 1)
        elif action == 2:
            x = min(self.size - 1, x + 1)
        elif action == 3:
            y = max(0, y - 1)
        self.state = (x, y)
        if self.state in self.obstacles:
            return self.state, -1, True
        if self.state == self.goal:
            return self.state, 1, True
        return self.state, -0.01, False

    def reset(self):
        self.state = (0, 0)
        return self.state

# Q-Learning
class QLearning:
    def __init__(self, env, alpha=0.5, gamma=0.95, epsilon=0.1, episodes=10):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episodes = episodes
        self.q_table = np.zeros((self.env.size, self.env.size, 4))

    def choose_action(self, state, robot=0):
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.choice([0, 1, 2, 3])
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, new_state):
        self.q_table[state][action] = (1 - self.alpha) * self.q_table[state][action] + \
            self.alpha * (reward + self.gamma * np.max(self.q_table[new_state]))

    def train(self, robot=0):
        rewards = []
        states = []
        starts = []
        steps_per_episode = []
        steps = 0
        episode = 0
        while episode < self.episodes:
            state = self.env.reset()
            total_reward = 0
            done = False
            while not done:
                action = self.choose_action(state, robot)
                new_state, reward, done = self.env.step(action)
                self.update_q_table(state, action, reward, new_state)
                state = new_state
                total_reward += reward
                states.append(state)
                steps += 1
                if done and state == self.env.goal:
                    starts.append(len(states))
                    rewards.append(total_reward)
                    steps_per_episode.append(steps)
                    steps = 0
                    episode += 1
        return rewards, states, starts, steps_per_episode

    def save_q_table(self, filename):
        filepath = os.path.join(get_base_path(), filename)
        with open(filepath, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self, filename):
        filepath = os.path.join(get_base_path(), filename)
        with open(filepath, 'rb') as f:
            self.q_table = pickle.load(f)

# Función principal robot()
def robot():
    env = GridWorld(size=5)
    agent = QLearning(env)

    q_table_path = os.path.join(get_base_path(), 'q_table.pkl')
    if os.path.exists(q_table_path):
        agent.load_q_table('q_table.pkl')

    rewards, states, starts, steps_per_episode = agent.train(1)

    agent.save_q_table('q_table.pkl')

    fig, ax = plt.subplots()

    def update(i):
        ax.clear()
        cumulative_reward = sum(rewards[:i+1])
        current_episode = next((j for j, start in enumerate(starts) if start > i), len(starts)) - 1
        if current_episode < 0:
            steps = i + 1
        else:
            steps = i - starts[current_episode] + 1
        ax.set_title(f"Iteration: {current_episode+1}, Total Reward: {cumulative_reward:.2f}, Steps: {steps}")
        grid = np.zeros((env.size, env.size))
        for obstacle in env.obstacles:
            grid[obstacle] = -1
        grid[env.goal] = 1
        grid[states[i]] = 0.5
        ax.imshow(grid, cmap='cool')

    ani = animation.FuncAnimation(fig, update, frames=range(len(states)), repeat=False)

    print("Robot execution")
    for i, steps in enumerate(steps_per_episode, 1):
        print(f"Iteration {i}: {steps} steps")
    print(f"Total reward: {sum(rewards):.2f}\n")
    plt.show()

# Leer parámetros desde archivo
params_path = os.path.join(get_base_path(), 'params.txt')
with open(params_path, 'r') as file1:
    lines = file1.readlines()
    alpha = float(lines[0])
    gama = float(lines[1])
    epsilon = float(lines[2])
    episodes = int(lines[3])

# Entrenamiento y visualización
for i in range(10):
    env = GridWorld(size=5)
    agent = QLearning(env, alpha, gama, epsilon, episodes)

    q_table_path = os.path.join(get_base_path(), 'q_table.pkl')
    if os.path.exists(q_table_path):
        agent.load_q_table('q_table.pkl')

    rewards, states, starts, steps_per_episode = agent.train()

    agent.save_q_table('q_table.pkl')

    fig, ax = plt.subplots()

    def update(i):
        ax.clear()
        cumulative_reward = sum(rewards[:i+1])
        current_episode = next((j for j, start in enumerate(starts) if start > i), len(starts)) - 1
        if current_episode < 0:
            steps = i + 1
        else:
            steps = i - starts[current_episode] + 1
        ax.set_title(f"Iteration: {current_episode+1}, Total Reward: {cumulative_reward:.2f}, Steps: {steps}")
        grid = np.zeros((env.size, env.size))
        for obstacle in env.obstacles:
            grid[obstacle] = -1
        grid[env.goal] = 1
        grid[states[i]] = 0.5
        ax.imshow(grid, cmap='cool')

    ani = animation.FuncAnimation(fig, update, frames=range(len(states)), repeat=False)

    print(f"Environment number {i+1}")
    for j, steps in enumerate(steps_per_episode, 1):
        print(f"Iteration {j}: {steps} steps")
    print(f"Total reward: {sum(rewards):.2f}\n")

    plt.show()

# Ejecutar el robot
robot()
