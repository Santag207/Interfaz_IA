class ConfigIA:
    def __init__(self):
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.epocas = 1000

        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        self.recompensa_meta = 100
        self.penalizacion_obstaculo = -10
        self.penalizacion_paso = -1

    def actualizar(self, d):
        self.alpha = float(d.get('alpha', self.alpha))
        self.gamma = float(d.get('gamma', self.gamma))
        self.epsilon = float(d.get('epsilon', self.epsilon))
        self.epocas = int(d.get('epocas', self.epocas))
        self.recompensa_meta = float(d.get('r_meta', self.recompensa_meta))
        self.penalizacion_obstaculo = float(d.get('r_muro', self.penalizacion_obstaculo))
        self.penalizacion_paso = float(d.get('r_paso', self.penalizacion_paso))

    def decaer_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay