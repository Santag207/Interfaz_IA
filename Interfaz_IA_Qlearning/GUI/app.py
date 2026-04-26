import sys
import os
from flask import Flask, render_template, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Qlearning')))
from backend_qlearning import AgenteCoordinador

class ManejadorInterfazWeb:
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.coordinador = AgenteCoordinador()
        self._configurar_rutas()

    def _configurar_rutas(self):
        @self.app.route('/')
        def index(): return render_template('index.html')

        @self.app.route('/api/entrenar', methods=['POST'])
        def entrenar():
            self.coordinador.actualizar_y_entrenar(request.json)
            return jsonify({"status": "entrenado"})

        @self.app.route('/api/paso_uso', methods=['POST'])
        def paso_uso():
            self.coordinador.paso_prueba()
            return jsonify(self.coordinador.obtener_estado_visual())

        @self.app.route('/api/estado', methods=['GET'])
        def estado():
            return jsonify(self.coordinador.obtener_estado_visual())

        @self.app.route('/api/actualizar_mapa', methods=['POST'])
        def actualizar_mapa():
            mapa = request.json.get('mapa')
            self.coordinador.sincronizar_mapa(mapa)
            return jsonify({"status": "mapa_actualizado"})

        @self.app.route('/api/paso_visual', methods=['POST'])
        def paso_visual():
            # Ejecuta un paso y devuelve el estado para la observación
            return jsonify(self.coordinador.paso_entrenamiento_visual())

        @self.app.route('/api/generar_aleatorio', methods=['POST'])
        def generar_aleatorio():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            matriz_vacia = [[0 for _ in range(c)] for _ in range(f)]
            self.coordinador.sincronizar_mapa(matriz_vacia, f, c)
            self.coordinador.generar_mapa_valido()
            return jsonify(self.coordinador.obtener_estado_visual())

        @self.app.route('/api/redimensionar', methods=['POST'])
        def redimensionar():
            f = int(request.json.get('filas', 10))
            c = int(request.json.get('columnas', 10))
            self.coordinador.reconfigurar_entorno(f, c)
            return jsonify({"status": "ok"})

        @self.app.route('/api/actualizar_todo', methods=['POST'])
        def actualizar_todo():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            self.coordinador.config.actualizar(datos)
            self.coordinador.sincronizar_mapa(datos.get('mapa'), f, c)
            return jsonify({"status": "ready"})

        @self.app.route('/api/entrenar_fast', methods=['POST'])
        def entrenar_fast():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            mapa = datos.get('mapa')
            self.coordinador.sincronizar_mapa(mapa, f, c)
            self.coordinador.actualizar_y_entrenar({"epocas": self.coordinador.config.epocas})
            return jsonify({"status": "finished"})

    def ejecutar(self):
        self.app.run(debug=True, port=5000)

if __name__ == '__main__':
    ManejadorInterfazWeb().ejecutar()