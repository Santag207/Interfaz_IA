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
    """
    Gestiona la interfaz web usando Flask.
    Coordina las rutas API que comunican el navegador con el motor de Q-Learning.
    
    Atributos:
        app (Flask): Instancia de la aplicación Flask.
        coordinador (AgenteCoordinador): Coordinador del agente Q-Learning.
    """
    
    def __init__(self):
        """Inicializa la aplicación Flask y el coordinador."""
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.coordinador = AgenteCoordinador()
        self._configurar_rutas()

    def _configurar_rutas(self):
        """Define todas las rutas API que comunican frontend-backend."""
        
        # Ruta GET /: Renderiza la página HTML principal
        @self.app.route('/')
        def index(): 
            return render_template('index.html')

        # Ruta POST /api/entrenar: Entrena el agente con los parámetros recibidos
        @self.app.route('/api/entrenar', methods=['POST'])
        def entrenar():
            self.coordinador.actualizar_y_entrenar(request.json)
            return jsonify({"status": "entrenado"})

        # Ruta POST /api/paso_uso: Ejecuta un paso de simulación (sin aprendizaje)
        @self.app.route('/api/paso_uso', methods=['POST'])
        def paso_uso():
            self.coordinador.paso_prueba()
            return jsonify(self.coordinador.obtener_estado_visual())

        # Ruta GET /api/estado: Devuelve el estado actual del agente y mapa
        @self.app.route('/api/estado', methods=['GET'])
        def estado():
            return jsonify(self.coordinador.obtener_estado_visual())

        # Ruta POST /api/actualizar_mapa: Sincroniza el mapa desde la interfaz gráfica
        @self.app.route('/api/actualizar_mapa', methods=['POST'])
        def actualizar_mapa():
            mapa = request.json.get('mapa')
            self.coordinador.sincronizar_mapa(mapa)
            return jsonify({"status": "mapa_actualizado"})

        # Ruta POST /api/paso_visual: Ejecuta un paso de entrenamiento con visualización
        @self.app.route('/api/paso_visual', methods=['POST'])
        def paso_visual():
            return jsonify(self.coordinador.paso_entrenamiento_visual())

        # Ruta POST /api/generar_aleatorio: Genera un mapa aleatorio válido
        @self.app.route('/api/generar_aleatorio', methods=['POST'])
        def generar_aleatorio():
            datos = request.json
            f = int(datos.get('filas', 10))  # Obtiene filas del request
            c = int(datos.get('columnas', 10))  # Obtiene columnas del request
            matriz_vacia = [[0 for _ in range(c)] for _ in range(f)]  # Crea matriz vacía
            self.coordinador.sincronizar_mapa(matriz_vacia, f, c)  # Sincroniza dimensiones
            self.coordinador.generar_mapa_valido()  # Genera mapa aleatorio
            return jsonify(self.coordinador.obtener_estado_visual())

        # Ruta POST /api/redimensionar: Redimensiona el mundo a nuevas dimensiones
        @self.app.route('/api/redimensionar', methods=['POST'])
        def redimensionar():
            f = int(request.json.get('filas', 10))
            c = int(request.json.get('columnas', 10))
            self.coordinador.reconfigurar_entorno(f, c)
            return jsonify({"status": "ok"})

        # Ruta POST /api/actualizar_todo: Actualiza configuración y sincroniza mapa
        @self.app.route('/api/actualizar_todo', methods=['POST'])
        def actualizar_todo():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            self.coordinador.config.actualizar(datos)  # Actualiza hiperparámetros
            self.coordinador.sincronizar_mapa(datos.get('mapa'), f, c)  # Sincroniza mapa
            return jsonify({"status": "ready"})

        # Ruta POST /api/entrenar_fast: Entrena sin visualización a máxima velocidad
        @self.app.route('/api/entrenar_fast', methods=['POST'])
        def entrenar_fast():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            mapa = datos.get('mapa')
            self.coordinador.sincronizar_mapa(mapa, f, c)  # Sincroniza mapa
            # Entrena con épocas configuradas
            self.coordinador.actualizar_y_entrenar({"epocas": self.coordinador.config.epocas})
            return jsonify({"status": "finished"})


    def ejecutar(self):
        """Inicia el servidor Flask en puerto 5000."""
        self.app.run(debug=True, port=5000)


# Punto de entrada de la aplicación
if __name__ == '__main__':
    # Crea instancia de ManejadorInterfazWeb e inicia el servidor
    ManejadorInterfazWeb().ejecutar()