import numpy as np
import random

class QLearningAgent:
    def __init__(self, state_space, action_space,
                 lr=0.1, gamma=0.95,
                 epsilon=1.0, decay=0.995, min_eps=0.05):

        self.Q = np.zeros((state_space, action_space))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay = decay
        self.min_eps = min_eps
        self.actions = action_space

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.actions-1)
        return np.argmax(self.Q[state])

    def update(self, s, a, r, s2):
        self.Q[s,a] += self.lr * (
            r + self.gamma * np.max(self.Q[s2]) - self.Q[s,a]
        )

    def decay_epsilon(self):
        self.epsilon = max(self.min_eps, self.epsilon * self.decay)
