import numpy as np
import random

class QLearningAgent:
    def __init__(self, state_space, action_space):
        self.Q = np.zeros((state_space, action_space))

        self.alpha = 0.1
        self.gamma = 0.95

        self.epsilon = 1.0
        self.epsilon_decay = 0.9995
        self.epsilon_min = 0.05

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.Q.shape[1]-1)
        return np.argmax(self.Q[state])

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.Q[next_state])
        self.Q[state, action] += self.alpha * (
            reward + self.gamma * best_next - self.Q[state, action]
        )

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
