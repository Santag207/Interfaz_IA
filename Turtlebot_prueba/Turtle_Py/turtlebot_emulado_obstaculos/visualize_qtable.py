import numpy as np
import matplotlib.pyplot as plt

Q = np.load("qtable.npy")
plt.imshow(np.max(Q, axis=1).reshape((10, 10)))
plt.title("Mapa de valores Q (max por estado)")
plt.colorbar()
plt.show()
