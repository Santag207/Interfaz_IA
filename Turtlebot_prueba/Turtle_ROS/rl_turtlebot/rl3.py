#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from ament_index_python.packages import get_package_share_directory

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import os
import time

prev = "abajo"  # Variable global para recordar la orientación previa

# Nombre de tu paquete
package_name = 'rl_turtlebot'
# Obtener la ruta absoluta a la carpeta share/rl_turtlebot
share_dir = get_package_share_directory(package_name)
# Ruta al q_table.pkl dentro de resource
path_archivo = os.path.join(share_dir, 'resource', 'q_table.pkl')

# -----------------------------------------------------------------------------
# 1. Entorno GridWorld
# -----------------------------------------------------------------------------
class GridWorld:
    """Entorno GridWorld con obstáculos y meta."""
    def __init__(self, size=5, obstacles=[(1, 1), (1, 2), (2, 1), (3, 3)]):
        self.size = size
        self.obstacles = obstacles
        self.state_space = np.zeros((self.size, self.size))
        self.state = (0, 0)
        self.goal = (self.size - 1, self.size - 1)

    def step(self, action):
        """
        Avanza un paso en el entorno según la acción elegida.
        action: 0=up, 1=right, 2=down, 3=left
        """
        x, y = self.state

        if action == 0:  # up
            x = max(0, x - 1)
        elif action == 1:  # right
            y = min(self.size - 1, y + 1)
        elif action == 2:  # down
            x = min(self.size - 1, x + 1)
        elif action == 3:  # left
            y = max(0, y - 1)

        self.state = (x, y)

        # Obstáculo => -1 y fin
        if self.state in self.obstacles:
            return self.state, -1, True

        # Meta => +1 y fin
        if self.state == self.goal:
            return self.state, 1, True

        # Estado normal => -0.01
        return self.state, -0.01, False

    def reset(self):
        self.state = (0, 0)
        return self.state


# -----------------------------------------------------------------------------
# 2. Clase QLearning (sólo para cargar Q-Table y elegir acción)
# -----------------------------------------------------------------------------
class QLearning:
    def __init__(self, env):
        self.env = env
        # Dimensiones: [env.size, env.size, 4]
        self.q_table = np.zeros((env.size, env.size, 4))

    def load_q_table(self, filepath):
        with open(filepath, 'rb') as f:
            self.q_table = pickle.load(f)

    def choose_greedy_action(self, state):
        """
        Elige la acción con el valor Q más alto en la Q-table.
        """
        return np.argmax(self.q_table[state])


# -----------------------------------------------------------------------------
# 3. Clase RobotMovementNode: nodo ROS2 para mover el TurtleBot3
# -----------------------------------------------------------------------------
class RobotMovementNode(Node):
    def __init__(self):
        super().__init__('robot_movement_node')
        self.publisher_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.2
        self.angular_speed = 1.0

    def avanzar(self, tiempo=2.0):
        twist = Twist()
        twist.linear.x = self.linear_speed
        twist.angular.z = 0.0
        self.publicar_por_tiempo(twist, tiempo)

    def girar_180(self):
        twist = Twist()
        twist.angular.z = self.angular_speed
        tiempo_180 = np.pi / self.angular_speed
        self.publicar_por_tiempo(twist, tiempo_180)

    def girar_90_derecha(self):
        twist = Twist()
        twist.angular.z = -self.angular_speed
        tiempo_90 = (np.pi / 2) / self.angular_speed
        self.publicar_por_tiempo(twist, tiempo_90-0.2)

    def girar_90_izquierda(self):
        twist = Twist()
        twist.angular.z = self.angular_speed
        tiempo_90 = (np.pi / 2) / self.angular_speed
        self.publicar_por_tiempo(twist, tiempo_90-0.2)

    def mover_arriba(self, tiempo=2.0):
        global prev
        if prev is None:
            pass
        elif prev == "arriba":
            pass
        elif prev == "abajo":
            self.girar_180()
        elif prev == "izquierda":
            self.girar_90_derecha()
        elif prev == "derecha":
            self.girar_90_izquierda()

        self.avanzar(1.2)
        prev = "arriba"

    def mover_abajo(self, tiempo=2.0):
        global prev
        if prev is None:
            self.girar_180()
        elif prev == "abajo":
            pass
        elif prev == "arriba":
            self.girar_180()
        elif prev == "izquierda":
            self.girar_90_izquierda()
        elif prev == "derecha":
            self.girar_90_derecha()

        self.avanzar(1.2)
        prev = "abajo"

    def mover_izquierda(self, tiempo=2.0):
        global prev
        if prev is None:
            self.girar_90_izquierda()
        elif prev == "izquierda":
            pass
        elif prev == "derecha":
            self.girar_180()
        elif prev == "arriba":
            self.girar_90_izquierda()
        elif prev == "abajo":
            self.girar_90_derecha()

        self.avanzar(1.7)
        prev = "izquierda"

    def mover_derecha(self, tiempo=2.0):
        global prev
        if prev is None:
            self.girar_90_derecha()
        elif prev == "derecha":
            pass
        elif prev == "izquierda":
            self.girar_180()
        elif prev == "arriba":
            self.girar_90_derecha()
        elif prev == "abajo":
            self.girar_90_izquierda()

        self.avanzar(1.7)
        prev = "derecha"

    def publicar_por_tiempo(self, twist, tiempo):
        start_time = time.time()
        while time.time() - start_time < tiempo:
            self.publisher_cmd_vel.publish(twist)
            time.sleep(0.1)

        # Al terminar, enviar velocidad 0 para parar
        stop_twist = Twist()
        self.publisher_cmd_vel.publish(stop_twist)
        time.sleep(0.3)


# -----------------------------------------------------------------------------
# 4. Generador de episodios: rinde un estado cada vez que se llama
# -----------------------------------------------------------------------------
def episode_generator(env, agent, node: RobotMovementNode):
    """
    Generador que ejecuta un paso del entorno FÍSICO (robot) cada vez que se lo llama.
    - Se inicia con un reset()
    - Mientras no done, se elige acción greedy, se mueve el robot, se hace step()
    - Se 'yield' el estado para que la animación lo pinte
    Cuando el episodio termina, se detiene la iteración.
    """
    state = env.reset()
    total_reward = 0.0
    done = False
    yield (state, total_reward, done)  # Primer frame (estado inicial)

    while not done:
        # 1) Elegir acción con la Q-table
        action = agent.choose_greedy_action(state)
        # 3) Step en el GridWorld
        new_state, reward, done = env.step(action)
        total_reward += reward
        state = new_state
        # 2) Mover robot en ROS
        ejecutar_accion_fisica(node, action, 2.0)
        # 4) Entregar el nuevo estado
        yield (state, total_reward, done)


def ejecutar_accion_fisica(node: RobotMovementNode, action: int, tiempo=2.0):
    if action == 0:
        node.mover_arriba(tiempo)
    elif action == 1:
        node.mover_derecha(tiempo)
    elif action == 2:
        node.mover_abajo(tiempo)
    elif action == 3:
        node.mover_izquierda(tiempo)
    else:
        print("Acción desconocida:", action)


# -----------------------------------------------------------------------------
# 5. main(): Inicializamos ROS, cargamos Q-table, lanzamos la animación "en tiempo real"
# -----------------------------------------------------------------------------
def main(args=None):
    global path_archivo

    # Iniciar ROS
    rclpy.init(args=args)
    robot_node = RobotMovementNode()

    # Crear entorno y agente
    env = GridWorld(size=5)
    agent = QLearning(env)
    agent.load_q_table(path_archivo)

    # Crear la figura y ejes
    fig, ax = plt.subplots()

    # Generador de pasos (cada frame de la animación será 1 acción)
    gen = episode_generator(env, agent, robot_node)

    def update(frame_data):
        """
        Función que se llama con cada 'frame' proveniente del generador.
        frame_data = (state, total_reward, done)
        """
        (state, total_reward, done) = frame_data
        ax.clear()
        ax.set_title(f"Estado: {state}, Reward Acum: {total_reward:.2f}")

        # Construir la matriz para dibujar
        grid = np.zeros((env.size, env.size))
        for obs in env.obstacles:
            grid[obs] = -1
        grid[env.goal] = 1
        grid[state] = 0.5

        # Mostrar grid
        ax.imshow(grid, cmap='cool', vmin=-1, vmax=1)

        # Si se terminó el episodio, podemos imprimir algo o detener la animación
        if done:
            print("¡Episodio terminado!")
            print(f"Recompensa total = {total_reward:.2f}")
            # Opción: detener la animación (no más frames)
            ani.event_source.stop()

    # Crear la animación usando el generador como 'frames'
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=gen,         # Va llamando a next(gen) en cada frame
        interval=500,       # Intervalo de refresco en ms (ajústalo)
        repeat=False
    )

    plt.show()

    # Al cerrar la ventana, destruimos el nodo
    robot_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
