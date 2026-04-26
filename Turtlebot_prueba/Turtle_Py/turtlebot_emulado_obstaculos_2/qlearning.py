import numpy as np
import random

class QLearningAgent:
    def __init__(self, state_space, action_space,
                 alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):

        self.Q = np.zeros((state_space, action_space))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.action_space = action_space

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_space - 1)
        return np.argmax(self.Q[state])

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.Q[next_state])
        self.Q[state, action] += self.alpha * (
            reward + self.gamma * best_next - self.Q[state, action]
        )

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
