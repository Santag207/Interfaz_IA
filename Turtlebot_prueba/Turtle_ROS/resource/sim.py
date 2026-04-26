#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import os

# -------------------------------
# 1. Definimos la clase GridWorld
# -------------------------------
class GridWorld:
    """Entorno GridWorld con obstáculos y una meta.
    
    El agente inicia en la esquina superior izquierda (0,0) y su objetivo es 
    llegar a la esquina inferior derecha (size-1, size-1).
    
    Recompensas:
    - Estado normal: -0.01 por paso
    - Estado obstáculo: -1 (termina el episodio)
    - Estado meta: +1 (termina el episodio)
    """
    def __init__(self, size=5, obstacles=[(1, 1), (1, 2), (2, 1), (3, 3)]):
        self.size = size
        self.obstacles = obstacles
        self.state_space = np.zeros((self.size, self.size))
        self.state = (0, 0)
        self.goal = (self.size - 1, self.size - 1)

    def step(self, action):
        """
        Avanza un paso en el entorno según la acción elegida.
        
        Args:
            action (int): 0=up, 1=right, 2=down, 3=left
        
        Returns:
            state (tuple): Nuevo estado
            reward (float): Recompensa recibida
            done (bool): True si terminó el episodio
        """
        x, y = self.state
        
        if action == 0:  # up
            x = max(0, x-1)
        elif action == 1:  # right
            y = min(self.size-1, y+1)
        elif action == 2:  # down
            x = min(self.size-1, x+1)
        elif action == 3:  # left
            y = max(0, y-1)

        self.state = (x, y)
        
        # Si cae en un obstáculo
        if self.state in self.obstacles:
            return self.state, -1, True

        # Si llega a la meta
        if self.state == self.goal:
            return self.state, 1, True
        
        # Si no ha terminado
        return self.state, -0.01, False

    def reset(self):
        """
        Reinicia el entorno (el agente regresa a (0,0)).
        """
        self.state = (0, 0)
        return self.state

# ------------------------------------
# 2. Definimos la clase de Q-Learning
# ------------------------------------
class QLearning:
    """Clase Q-Learning para GridWorld, solo con fines de cargar y usar la Q-table."""
    def __init__(self, env):
        self.env = env
        # La Q-table debe tener dimensiones [env.size, env.size, 4]
        # Se inicializa a cero, pero se sobreescribe al cargar:
        self.q_table = np.zeros((self.env.size, self.env.size, 4))

    def load_q_table(self, filename):
        """
        Carga la Q-table de un archivo .pkl
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'rb') as f:
            self.q_table = pickle.load(f)

    def choose_greedy_action(self, state):
        """
        Elige la acción con mayor valor Q para el estado dado (exploitation pura).
        """
        return np.argmax(self.q_table[state])

# -----------------------------------------------------
# 3. Función para ejecutar un ÚNICO EPISODIO (recorrido)
# -----------------------------------------------------
def run_single_episode(env, agent):
    """
    Corre un único episodio usando la Q-table cargada.
    
    Returns:
        states (list): lista de estados recorridos
        total_reward (float): suma de recompensas hasta terminar
    """
    states = []
    total_reward = 0
    done = False
    
    # Reiniciamos el entorno
    state = env.reset()
    states.append(state)
    
    while not done:
        # El agente elige la acción con mayor valor Q en la Q-table
        action = agent.choose_greedy_action(state)
        
        # Realizamos el paso
        new_state, reward, done = env.step(action)
        
        # Acumulamos y guardamos
        total_reward += reward
        state = new_state
        states.append(state)
        
    return states, total_reward

# ------------------------------------------------------------------
# 4. Función principal: cargar la Q-table y mostrar un único episodio
# ------------------------------------------------------------------
def main():
    # Creamos el entorno
    env = GridWorld(size=5)
    
    # Creamos el agente Q-Learning
    agent = QLearning(env)
    
    # Cargamos la Q-table entrenada (asegúrate de que 'q_table.pkl' exista)
    agent.load_q_table('q_table.pkl')
    
    # Ejecutamos un único recorrido
    states, total_reward = run_single_episode(env, agent)
    
    # Imprimimos resultados en consola
    print("Recorrido completado.")
    print(f"Estados visitados: {states}")
    print(f"Recompensa total: {total_reward:.2f}")
    
    # Visualizamos el recorrido con una animación
    fig, ax = plt.subplots()
    
    def update(frame):
        """
        Función que actualiza la visualización en cada frame de la animación.
        """
        ax.clear()
        # Título informativo
        ax.set_title(f"Paso {frame+1} / {len(states)}")
        
        # Construimos la matriz para dibujar
        grid = np.zeros((env.size, env.size))
        
        # Marcamos los obstáculos con -1
        for obstacle in env.obstacles:
            grid[obstacle] = -1
        
        # Marcamos la meta con +1
        grid[env.goal] = 1
        
        # Marcamos la posición actual del agente con 0.5
        # (frame indica el índice del estado en la lista states)
        current_position = states[frame]
        grid[current_position] = 0.5
        
        # Mostramos el grid
        ax.imshow(grid, cmap='cool', vmin=-1, vmax=1)
    
    ani = animation.FuncAnimation(
        fig, update, frames=range(len(states)), interval=500, repeat=False
    )
    
    plt.show()

# ---------------------------------------------
# Llamamos a main() solo si se ejecuta este guion
# ---------------------------------------------
if __name__ == "__main__":
    main()
