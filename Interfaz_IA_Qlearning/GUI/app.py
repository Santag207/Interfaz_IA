"""
Módulo principal de la aplicación web Flask.
Gestiona las rutas API y la comunicación entre el frontend y el backend de Q-Learning.
"""
import sys
import os
from flask import Flask, render_template, request, jsonify

# Añade la carpeta Qlearning al path para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Qlearning')))
from backend_qlearning import AgenteCoordinador


class ManejadorInterfazWeb:
    def __init__(self):
        """Inicializa la aplicación Flask y el coordinador."""
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.coordinador = AgenteCoordinador()
        self._configurar_rutas()

    def _configurar_rutas(self):
        """Define todas las rutas API que comunican frontend-backend."""

        # 1. RUTA DE INICIO (La Landing Page con explicaciones)
        @self.app.route('/')
        def index():
            return render_template('index.html')

        # 2. RUTA DEL LABORATORIO (Donde está toda la herramienta de diseño)
        @self.app.route('/interfaz')
        def interfaz():
            return render_template('interfaz.html')

        # --- RUTAS DE LA API ---

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
            self.coordinador.actualizar_y_entrenar(datos) # Usamos datos completos para incluir epocas
            return jsonify({"status": "finished"})

    def ejecutar(self):
        """Inicia el servidor Flask."""
        self.app.run(debug=True, port=5000)

if __name__ == '__main__':
    ManejadorInterfazWeb().ejecutar()