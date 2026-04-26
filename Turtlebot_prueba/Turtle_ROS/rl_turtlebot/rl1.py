#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import numpy as np
import matplotlib.pyplot as plt
import logging
import time

logging.basicConfig(level=logging.INFO)
plt.ion()

prev = "abajo"

class GridWorld:
    """
    GridWorld environment para navegación.
    
    Args:
        width (int): Ancho de la grilla.
        height (int): Alto de la grilla.
        start (tuple): Posición inicial del agente.
        goal (tuple): Posición objetivo.
        obstacles (list): Lista de obstáculos (tuplas).
    """
    def __init__(self, width: int = 5, height: int = 5, 
        start: tuple = (0, 0), goal: tuple = (4, 4), obstacles: list = None):
        self.width = width
        self.height = height
        self.start = np.array(start)
        self.goal = np.array(goal)
        self.obstacles = [np.array(obstacle) for obstacle in obstacles] if obstacles else []
        self.state = self.start
        
        # Acciones con vectores de movimiento (fila, columna)
        self.actions = {
            'up':    np.array([-1, 0]),
            'down':  np.array([1, 0]),
            'left':  np.array([0, -1]),
            'right': np.array([0, 1])
        }

    def reset(self):
        """ 
        Reinicia el estado del ambiente al estado inicial (start).
        
        Returns:
            np.array: El estado inicial.
        """
        self.state = self.start
        return self.state

    def is_valid_state(self, state):
        """
        Verifica si el estado es válido (dentro de límites y no es obstáculo).

        Args:
            state (np.array): Estado a verificar.

        Returns:
            bool: True si el estado es válido, False si no.
        """
        if not (0 <= state[0] < self.height and 0 <= state[1] < self.width):
            return False
        # Verificar que no coincida con obstáculos
        for obs in self.obstacles:
            if (state == obs).all():
                return False
        return True

    def step(self, action: str):
        """
        Aplica una acción en el ambiente.

        Args:
            action (str): Nombre de la acción ('up', 'down', 'left', 'right').

        Returns:
            tuple: (next_state, reward, done)
        """
        next_state = self.state + self.actions[action]
        if self.is_valid_state(next_state):
            self.state = next_state
        
        # Recompensa
        reward = 100 if (self.state == self.goal).all() else -1
        # Verificar si llegamos a la meta
        done = (self.state == self.goal).all()

        return self.state, reward, done


class RobotMovementNode(Node):
    """
    Nodo ROS 2 que publica a /cmd_vel para mover TurtleBot3 en acciones discretas:
    - mover_arriba
    - mover_abajo
    - mover_izquierda
    - mover_derecha
    """
    def __init__(self):
        super().__init__('robot_movement_node')
        self.publisher_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        # Velocidades base (ajusta a tus necesidades)
        self.linear_speed = 0.2
        self.angular_speed = 1.0

    def mover_arriba(self, tiempo=2.0):
        """
        Mueve el robot hacia adelante (lineal.x positivo).
        """
        twist = Twist()
        twist.linear.x = self.linear_speed
        twist.angular.z = 0.0
        self.publicar_por_tiempo(twist, tiempo)

    def mover_abajo(self, tiempo=2.0):
        """
        Mueve el robot hacia atrás (lineal.x negativo).
        """
        global prev
        
        twist = Twist()
        if prev != "abajo":
            twist.linear.x = -self.linear_speed
            twist.angular.z = 0.0
            self.publicar_por_tiempo(twist, tiempo)
            self.mover_arriba
            prev = "abajo"
        else:
            self.mover_arriba(1.2)

    def mover_derecha(self, tiempo=2.0):
        """
        Gira el robot a la izquierda (angular.z positivo).
        """
        global prev
        tiempo_giro = np.pi / (2 * self.angular_speed)
        
        twist = Twist()
        if prev != "izquierda":
            twist.linear.x = 0.0
            twist.angular.z = self.angular_speed
            self.publicar_por_tiempo(twist, tiempo_giro)
            prev = "izquierda"
        self.mover_arriba(1.7)
            
    def mover_izquierda(self, tiempo=2.0):
        """
        Gira el robot a la derecha (angular.z negativo).
        """
        global prev
        tiempo_giro = np.pi / (2 * self.angular_speed)
        
        twist = Twist()
        if prev != "derecha":
            twist.linear.x = 0.0
            twist.angular.z = -self.angular_speed
            self.publicar_por_tiempo(twist, tiempo_giro)
            prev = "derecha"
        self.mover_arriba(1.7)

    def publicar_por_tiempo(self, twist, tiempo):
        start_time = time.time()
        while time.time() - start_time < tiempo:
            self.publisher_cmd_vel.publish(twist)
            time.sleep(0.1)  # Publicar cada 0.1 segundos

        # Detener el robot después del tiempo
        stop_twist = Twist()
        self.publisher_cmd_vel.publish(stop_twist)
        time.sleep(0.5)  # Esperar un poco para asegurar que el robot se detenga


def navigation_policy(state: np.array, goal: np.array, obstacles: list, env: GridWorld):
    """
    Política de navegación que elige la acción que más acerca al goal
    en términos de distancia de Manhattan, 
    siempre que el siguiente estado sea válido.

    Args:
        state (np.array): Estado actual.
        goal (np.array): Estado objetivo.
        obstacles (list): Lista de obstáculos.
        env (GridWorld): El entorno (para usar env.actions o env.is_valid_state).

    Returns:
        str or None: Acción a tomar ('up', 'down', 'left', 'right') o None si no hay acciones válidas.
    """
    actions = ['up', 'down', 'left', 'right']
    valid_actions = {}
    for action in actions:
        next_state = state + env.actions[action]
        if env.is_valid_state(next_state):
            # Distancia de Manhattan al objetivo
            dist = np.sum(np.abs(next_state - goal))
            valid_actions[action] = dist

    # Elegir la acción que minimiza la distancia al goal
    return min(valid_actions, key=valid_actions.get) if valid_actions else None


def ejecutar_accion_fisica(node: RobotMovementNode, action: str, tiempo=2.0):
    """
    Llama la función correspondiente del nodo ROS 2 
    para mover el TurtleBot3 según la acción.
    """
    if action == 'up':
        node.mover_arriba(tiempo)
    elif action == 'down':
        node.mover_abajo(tiempo)
    elif action == 'left':
        node.mover_izquierda(tiempo)
    elif action == 'right':
        node.mover_derecha(tiempo)
    else:
        pass  # Acción desconocida


def run_simulation_with_policy(env: GridWorld, node: RobotMovementNode):
    """
    Corre la simulación con la política de navegación 
    y publica las acciones en /cmd_vel para un TurtleBot3 real.

    Args:
        env (GridWorld): El entorno de la grilla.
        node (RobotMovementNode): Nodo ROS 2 para publicar cmd_vel.
    """
    state = env.reset()
    done = False
    logging.info(f"Start State: {state}, Goal: {env.goal}, Obstacles: {env.obstacles}")

    while not done:
        # Visualización en matplotlib
        grid = np.zeros((env.height, env.width))
        grid[tuple(state)] = 1  # estado actual
        grid[tuple(env.goal)] = 2  # objetivo
        for obstacle in env.obstacles:
            grid[tuple(obstacle)] = -1  # obstáculos

        plt.imshow(grid, cmap='Pastel1', origin='upper')
        plt.title("Simulación GridWorld + TurtleBot3")
        plt.pause(0.5)

        # Decidir acción con la política
        action = navigation_policy(state, env.goal, env.obstacles, env)
        if action is None:
            logging.info("No hay acciones válidas, el agente está atascado.")
            break
        
        # Mover robot FÍSICO en ROS 2
        ejecutar_accion_fisica(node, action, tiempo=2.0)

        # Avanzar la simulación (estado virtual)
        next_state, reward, done = env.step(action)
        logging.info(f"State: {state} -> Action: {action} -> Next State: {next_state}, Reward: {reward}")
        
        state = next_state
        if done:
            logging.info("¡Meta alcanzada!")

    logging.info("Simulación terminada.")
    plt.close()


def main(args=None):
    # Inicializar ROS 2
    rclpy.init(args=args)
    # Crear nodo para movimiento real
    robot_node = RobotMovementNode()

    # Definir obstáculos
    obstacles = [(1, 1), (1, 2), (2, 1), (3, 3)]
    # Crear entorno
    env = GridWorld(width=5, height=5, start=(0, 0), goal=(4, 4), obstacles=obstacles)

    # Ejecutar la simulación
    run_simulation_with_policy(env, robot_node)

    # Cerrar todo
    robot_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()