"""
Módulo principal de la aplicación web Flask.
Gestiona las rutas API y la comunicación entre el frontend y el backend de Q-Learning.
"""
import sys
import os
import json
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Añade la carpeta Qlearning al path para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Qlearning')))
from backend_qlearning import AgenteCoordinador


class ManejadorInterfazWeb:
    def __init__(self):
        """Inicializa la aplicación Flask y el coordinador."""
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.coordinador = AgenteCoordinador()

        # --- CONFIGURACIÓN DE RUTAS (NIVEL RAÍZ) ---
        # Sube un nivel desde 'GUI' para quedar al mismo nivel que Interfaz y Qlearning
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dir_mapas = os.path.join(base_dir, 'mapas')
        self.dir_historial = os.path.join(base_dir, 'Historial')

        # Crear carpetas si no existen fuera de la carpeta GUI[cite: 14]
        os.makedirs(self.dir_mapas, exist_ok=True)
        os.makedirs(self.dir_historial, exist_ok=True)

        self._configurar_rutas()

    def _guardar_historial_csv(self, f, c, accion, detalles):
        """Crea el CSV con el formato solicitado incluyendo hiperparámetros"""
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"{f}X{c}(Casillas)_{fecha_str}.csv"

        subcarpeta = os.path.join(self.dir_historial, f"{f}x{c}")
        os.makedirs(subcarpeta, exist_ok=True)

        ruta_csv = os.path.join(subcarpeta, nombre_archivo)

        with open(ruta_csv, mode='w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            # Modificamos el encabezado para mayor claridad
            writer.writerow(["Fecha", "Acción", "Filas", "Columnas", "Detalles / Hiperparámetros"])
            writer.writerow([fecha_str, accion, f, c, detalles])

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

        # --- RUTAS NUEVAS PARA GESTIÓN DE MAPAS E HISTORIAL ---

        @self.app.route('/api/guardar_mapa', methods=['POST'])
        def guardar_mapa():
            datos = request.json
            f, c = datos.get('filas'), datos.get('columnas')
            hparams = datos.get('hiperparametros', {})  # Obtenemos los hparams

            nombre = f"mapa_{f}x{c}_{datetime.now().strftime('%H%M%S')}.json"

            # 1. Guardar el JSON (contiene mapa e hiperparámetros)
            with open(os.path.join(self.dir_mapas, nombre), 'w') as archivo:
                json.dump(datos, archivo)

            # 2. Formatear los detalles para el CSV
            detalles_csv = (f"Archivo: {nombre} | Alpha: {hparams.get('alpha')} | "
                            f"Gamma: {hparams.get('gamma')} | Eps: {hparams.get('epsilon')} | "
                            f"Épocas: {hparams.get('epocas')}")

            self._guardar_historial_csv(f, c, "Guardado de Mapa", detalles_csv)
            return jsonify({"status": "ok", "mensaje": "Mapa guardado"})

        @self.app.route('/api/listar_mapas', methods=['GET'])
        def listar_mapas():
            mapas = []
            # Verificar si la carpeta existe antes de listar[cite: 14]
            if os.path.exists(self.dir_mapas):
                for arch in os.listdir(self.dir_mapas):
                    if arch.endswith('.json'):
                        ruta_completa = os.path.join(self.dir_mapas, arch)
                        with open(ruta_completa, 'r') as f:
                            try:
                                info = json.load(f)
                                mapas.append({
                                    "nombre": arch,
                                    "filas": info.get('filas'),
                                    "columnas": info.get('columnas')
                                })
                            except:
                                pass  # Ignorar archivos corruptos[cite: 14]
            return jsonify(mapas)

        @self.app.route('/api/cargar_mapa', methods=['POST'])
        def cargar_mapa():
            try:
                nombre = request.json.get('nombre')
                ruta_archivo = os.path.join(self.dir_mapas, nombre)

                if not os.path.exists(ruta_archivo):
                    return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

                with open(ruta_archivo, 'r') as f:
                    datos = json.load(f)

                self._guardar_historial_csv(datos['filas'], datos['columnas'], "Carga de Mapa", f"Archivo: {nombre}")
                return jsonify(datos)
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        # --- RUTAS ORIGINALES DE LA API ---

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
            try:
                config_limpia = {
                    'alpha': float(datos.get('alpha')),
                    'gamma': float(datos.get('gamma')),
                    'epsilon': float(datos.get('epsilon')),
                    'epocas': int(datos.get('epocas')),
                    'r_meta': float(datos.get('r_meta')),
                    'r_muro': float(datos.get('r_muro')),
                    'r_paso': float(datos.get('r_paso'))
                }

                f = int(datos.get('filas', 10))
                c = int(datos.get('columnas', 10))

                # --- AGREGAR ESTO ---
                # Forzar al backend a redimensionar antes de recibir el mapa
                self.coordinador.reconfigurar_entorno(f, c)

                # 1. Actualizar configuración
                self.coordinador.config.actualizar(config_limpia)

                # 2. Sincronizar el mapa (ahora que las dimensiones coinciden)
                self.coordinador.sincronizar_mapa(datos.get('mapa'), f, c)

                # 3. CORRECCIÓN: Reiniciar la tabla Q usando el nuevo método o la referencia correcta
                # Antes buscaba 'self.coordinador.agente', ahora usa el coordinador directamente
                self.coordinador.resetear_aprendizaje()

                return jsonify({"status": "ready"})
            except Exception as e:
                print(f"Error en actualizar_todo: {e}")  # Para debug en consola
                return jsonify({"status": "error", "message": str(e)}), 400

        @self.app.route('/api/entrenar_fast', methods=['POST'])
        def entrenar_fast():
            datos = request.json
            f = int(datos.get('filas', 10))
            c = int(datos.get('columnas', 10))
            mapa = datos.get('mapa')
            self.coordinador.sincronizar_mapa(mapa, f, c)
            self.coordinador.actualizar_y_entrenar(datos) # Usamos datos completos para incluir epocas

            # Registramos el entrenamiento en el historial
            self._guardar_historial_csv(f, c, "Entrenamiento", f"Entrenado {datos.get('epocas', 1000)} épocas")

            return jsonify({"status": "finished"})

        @self.app.route('/api/obtener_historial', methods=['GET'])
        def obtener_historial():
            lista_historial = []
            if os.path.exists(self.dir_historial):
                # Recorrer subcarpetas (ej: 10x10, 5x5)
                for root, dirs, files in os.walk(self.dir_historial):
                    for file in files:
                        if file.endswith('.csv'):
                            # Extraer información básica del nombre del archivo[cite: 2]
                            lista_historial.append({
                                "nombre": file,
                                "ruta": os.path.join(os.path.basename(root), file)
                            })
            # Retornar los últimos 10 movimientos para no saturar el menú
            return jsonify(lista_historial[-10:])

    def ejecutar(self):
        """Inicia el servidor Flask."""
        self.app.run(debug=True, port=5000)

manejador = ManejadorInterfazWeb()
app = manejador.app