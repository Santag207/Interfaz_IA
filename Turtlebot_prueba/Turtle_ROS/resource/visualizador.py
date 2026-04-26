import pickle
import numpy as np

# 1. Carga el archivo .pkl
with open('q_table.pkl', 'rb') as f:
    q_table = pickle.load(f)

# 2. Asumiendo que q_table.shape = (size, size, 4):
size = q_table.shape[0]

# 3. Imprimir la Q-table en texto
for i in range(size):
    for j in range(size):
        up    = q_table[i, j, 0]
        right = q_table[i, j, 1]
        down  = q_table[i, j, 2]
        left  = q_table[i, j, 3]
        print(f"Estado ({i},{j}): Up={up:.2f}, Right={right:.2f}, Down={down:.2f}, Left={left:.2f}")

# Espera antes de cerrar
input("\nPresiona Enter para salir...")
