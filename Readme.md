# Interfaz IA Q-Learning 🤖

Una interfaz gráfica interactiva para visualizar y entrenar un agente de **Q-Learning** en un mundo 2D con obstáculos.

## 📋 Tabla de Contenidos
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Documentación Técnica](#documentación-técnica)

---

## ✨ Características

- 🎨 **Interfaz Web moderna** - Construcción visual del mapa
- 🧠 **Algoritmo Q-Learning** - Entrenamiento de agente inteligente
- 📊 **Visualización en tiempo real** - Observa el aprendizaje paso a paso
- 🎛️ **Parámetros ajustables** - Controla alpha, gamma, epsilon y más
- ⚡ **Entrenamiento rápido** - Opción de entrenamiento sin visualización
- 🗺️ **Mapas aleatorios** - Genera mapas válidos automáticamente
- 🎮 **Simulación interactiva** - Prueba el agente entrenado

---

## 📦 Requisitos

- **Python 3.7+**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

---

## 💻 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Santag207/Interfaz_IA.git
cd Interfaz_IA_Qlearning
```

### 2. Crear un Ambiente Virtual (Recomendado)

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install flask numpy
```

O instala desde el archivo de requisitos (si existe):
```bash
pip install -r requirements.txt
```

---

## 🚀 Cómo Iniciar la Aplicación

### Ejecutar el Servidor

Navega a la carpeta `GUI` e inicia la aplicación:

```bash
cd Interfaz_IA_Qlearning/GUI
python app.py
```

Deberías ver en la consola:
```
 * Running on http://127.0.0.1:5000
```

### Acceder a la Interfaz

1. Abre tu navegador web
2. Ve a: **http://localhost:5000**
3. ¡La interfaz está lista para usar!

---

## 📖 Cómo Usar la Aplicación

### Paso 1: Configuración del Mapa

1. **Define dimensiones**: Ajusta filas y columnas (10x10 recomendado)
2. **Dibuja obstáculos**: Haz clic en las celdas para añadir muros
3. **Punto de inicio** (verde): Siempre en (0,0)
4. **Objetivo** (rojo): Siempre en la esquina inferior derecha
5. Opciones:
   - **Mapa Aleatorio Válido**: Genera un mapa con ~20% obstáculos
   - **Limpiar Todo**: Reinicia el mapa

### Paso 2: Configurar Hiperparámetros

Ajusta estos valores según necesites:

| Parámetro | Valor Default | Rango | Significado |
|-----------|---------------|-------|------------|
| **Alpha (LR)** | 0.1 | 0.01-1.0 | Tasa de aprendizaje |
| **Gamma (Disc)** | 0.9 | 0.1-1.0 | Factor de descuento futuro |
| **Epsilon** | 0.1 | 0.01-1.0 | Factor de exploración |
| **Épocas** | 1000 | 100-10000 | Iteraciones de entrenamiento |
| **Meta (+)** | 100 | Número | Recompensa por objetivo |
| **Muro (-)** | -10 | Número | Penalización por obstáculo |
| **Paso (-)** | -1 | Número | Penalización por movimiento |

### Paso 3: Entrenar el Agente

**Opción A - Entrenamiento Visual:**
1. Haz clic en **"Confirmar y Entrenar"**
2. Ve a la pestaña "Entrenamiento"
3. Haz clic en **"Iniciar Observación"**
4. Observa cómo el agente aprende en tiempo real
5. Ajusta la velocidad con el slider

**Opción B - Entrenamiento Rápido:**
1. Haz clic en **"Confirmar y Entrenar"**
2. Ve a la pestaña "Entrenamiento"
3. Haz clic en **"Entrenamiento Rápido (Skip)"**
4. El entrenamiento se ejecuta al máximo sin visualización

### Paso 4: Simular el Agente

1. Una vez entrenado, ve a la pestaña **"Simulación"**
2. El mapa muestra los valores Q (colores representan confianza)
3. Opciones:
   - **Dar un Paso**: Avanza un movimiento
   - **Auto-Play**: El agente avanza automáticamente
   - **Nuevo Escenario**: Reinicia todo el proceso

---

## 📁 Estructura del Proyecto

```
Interfaz_IA_Qlearning/
├── GUI/
│   ├── app.py                 # Servidor Flask y rutas API
│   ├── static/
│   │   ├── style.css          # Estilos de la interfaz
│   │   └── script.js          # Lógica del frontend
│   └── templates/
│       └── index.html         # Página principal
│
├── Qlearning/
│   ├── backend_qlearning.py   # Coordinador principal
│   └── Backend/
│       ├── configuracion.py   # Hiperparámetros
│       ├── matriz_q.py        # Tabla Q (IA)
│       ├── motor_aprendizaje.py # Algoritmo Q-Learning
│       └── mundo.py           # Ambiente 2D
│
└── DOCUMENTACION_CLASES.md    # Documentación técnica detallada
```

---

## 🔧 Documentación Técnica de Clases

### 1. **ManejadorInterfazWeb** (`GUI/app.py`)
**Propósito**: Gestiona la interfaz web y las rutas API usando Flask.

**Atributos**:
- `app`: Instancia de Flask
- `coordinador`: Instancia de AgenteCoordinador

**Métodos principales**:
- `__init__()`: Inicializa la aplicación y el coordinador
- `_configurar_rutas()`: Define todas las rutas API
- `ejecutar()`: Inicia el servidor en puerto 5000

**Rutas API**:
- `GET /` - Renderiza página principal
- `POST /api/entrenar` - Entrena el agente
- `POST /api/paso_uso` - Avanza un paso en simulación
- `GET /api/estado` - Obtiene estado actual
- `POST /api/actualizar_mapa` - Sincroniza mapa desde GUI
- `POST /api/paso_visual` - Avanza entrenamiento visual
- `POST /api/generar_aleatorio` - Genera mapa aleatorio
- `POST /api/redimensionar` - Cambia dimensiones del mundo
- `POST /api/actualizar_todo` - Actualiza configuración y mapa
- `POST /api/entrenar_fast` - Entrenamiento sin visualización

---

## 2. **AgenteCoordinador** (`Qlearning/backend_qlearning.py`)
**Propósito**: Coordina la interacción entre el mundo, matriz Q y motor de aprendizaje.

**Atributos**:
- `config`: Configuración de hiperparámetros (ConfigIA)
- `mundo`: Ambiente 2D (Mundo2D)
- `matriz`: Tabla Q (MatrizQ)
- `motor`: Motor de Q-Learning (MotorQLearning)
- `posicion_robot`: Posición actual del agente (x, y)

**Métodos principales**:
- `reconfigurar_entorno(f, c)` - Redimensiona mundo y matriz Q
- `sincronizar_mapa(mapa_data, f, c)` - Actualiza mundo desde GUI
- `generar_mapa_valido()` - Crea mapa aleatorio
- `actualizar_y_entrenar(datos)` - Ejecuta N épocas de entrenamiento
- `paso_entrenamiento_visual()` - Ejecuta un paso visible
- `paso_prueba()` - Ejecuta un paso de simulación sin aprender
- `obtener_estado_visual()` - Retorna estado para renderizar

---

## 3. **ConfigIA** (`Qlearning/Backend/configuracion.py`)
**Propósito**: Almacena y gestiona los hiperparámetros del algoritmo.

**Atributos**:
- `alpha` (0.1): Tasa de aprendizaje
- `gamma` (0.9): Factor de descuento futuro
- `epsilon` (0.1): Factor de exploración
- `epocas` (1000): Número de iteraciones de entrenamiento
- `epsilon_min` (0.01): Límite mínimo de epsilon
- `epsilon_decay` (0.995): Decaimiento de epsilon
- `recompensa_meta` (100): Reward por alcanzar objetivo
- `penalizacion_obstaculo` (-10): Penalty por muro
- `penalizacion_paso` (-1): Penalty por paso normal

**Métodos**:
- `actualizar(d)` - Actualiza parámetros desde diccionario
- `decaer_epsilon()` - Reduce epsilon gradualmente

---

## 4. **MatrizQ** (`Qlearning/Backend/matriz_q.py`)
**Propósito**: Almacena y gestiona la tabla Q del agente.

**Atributos**:
- `tabla`: Array NumPy 3D (filas × columnas × 4 acciones)

**Métodos**:
- `obtener_mejor_accion(x, y)` - Retorna acción con mayor valor Q
- `actualizar(x, y, accion, valor)` - Actualiza valor Q
- `obtener_valor(x, y, accion)` - Obtiene valor Q específico
- `obtener_max_q(x, y)` - Obtiene máximo Q de una celda
- `estructurar_para_gui(mundo)` - Convierte matriz Q a formato JSON para GUI

**Mapeo de acciones**:
- 0: Arriba (-1, 0)
- 1: Abajo (1, 0)
- 2: Izquierda (0, -1)
- 3: Derecha (0, 1)

---

## 5. **MotorQLearning** (`Qlearning/Backend/motor_aprendizaje.py`)
**Propósito**: Implementa la lógica del algoritmo Q-Learning.

**Atributos**:
- `mundo`: Instancia de Mundo2D
- `matriz`: Instancia de MatrizQ
- `config`: Instancia de ConfigIA
- `acciones`: Lista de movimientos [arriba, abajo, izq, der]

**Métodos**:
- `simular_movimiento(x, y, accion_idx)` - Valida y ejecuta movimiento
- `ejecutar_paso_aprendizaje(estado_actual)` - Paso completo de Q-Learning:
  - Selecciona acción (exploración 10% vs explotación)
  - Simula movimiento
  - Calcula recompensa
  - Actualiza valor Q: `Q = Q + α(R + γ·max(Q') - Q)`

---

## 6. **Mundo2D** (`Qlearning/Backend/mundo.py`)
**Propósito**: Representa el ambiente 2D donde se mueve el agente.

**Atributos**:
- `filas`, `columnas`: Dimensiones del mapa
- `inicio`: Posición inicial (0, 0)
- `meta`: Posición objetivo (filas-1, columnas-1)
- `tablero`: Matriz 2D donde 0=libre, 1=muro, 2=meta

**Métodos**:
- `redimensionar(f, c)` - Cambia tamaño del mundo
- `actualizar_desde_gui(matriz_gui, f, c)` - Carga mapa desde interfaz
- `generar_mapa_aleatorio()` - Crea mapa con ~20% de muros
- `existe_camino(tablero)` - Verifica solucionabilidad con BFS
- `es_movimiento_valido(x, y)` - Comprueba límites
- `obtener_recompensa_visual(x, y)` - Retorna recompensa e indicador de fin

**Valores del tablero**:
- 0: Celda libre
- 1: Muro (obstáculo)
- 2: Meta (objetivo)

---

## Flujo General del Sistema

```
1. Usuario configura parámetros → ManejadorInterfazWeb recibe datos
2. AgenteCoordinador actualiza ConfigIA y sincroniza Mundo2D
3. Motor Q-Learning entrena en múltiples épocas
4. MatrizQ acumula conocimiento
5. Simulación usa matriz Q para tomar decisiones óptimas
6. Estado se visualiza en GUI mediante estructurar_para_gui()
```

---

## Relaciones entre Clases

```
ManejadorInterfazWeb
    ↓
AgenteCoordinador
    ├─→ ConfigIA (hiperparámetros)
    ├─→ Mundo2D (ambiente)
    ├─→ MatrizQ (tabla Q)
    └─→ MotorQLearning
            ├─→ Mundo2D (referencias)
            ├─→ MatrizQ (referencias)
            └─→ ConfigIA (referencias)
```

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask
```

### Error: "ModuleNotFoundError: No module named 'numpy'"
```bash
pip install numpy
```

### El servidor no inicia en puerto 5000
El puerto podría estar ocupado. Modifica `app.py`:
```python
self.app.run(debug=True, port=5001)  # Usa otro puerto
```

### La interfaz no carga en el navegador
1. Verifica que el servidor esté ejecutándose
2. Intenta limpiar el caché: `Ctrl+Shift+Delete`
3. Abre en una ventana de incógnito

### El agente no aprende correctamente
- Aumenta las **Épocas** (mínimo 1000)
- Reduce **Epsilon** para más explotación
- Aumenta **Alpha** para aprender más rápido
- Asegúrate de que el mapa tenga un camino válido

---

## 🎓 Entendiendo Q-Learning

**Q-Learning** es un algoritmo de aprendizaje por refuerzo donde el agente aprende el valor de cada acción en cada estado:

**Fórmula de actualización:**
```
Q(s,a) ← Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
```

- **s**: Estado actual
- **a**: Acción tomada
- **r**: Recompensa recibida
- **γ (gamma)**: Factor de descuento del futuro
- **α (alpha)**: Tasa de aprendizaje

---

## 📝 Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo, modificarlo y distribuirlo.

---

## 👨‍💻 Autor

Creado por: **Santiago Castro Zuluaga** - [GitHub](https://github.com/Santag207)

---

**¿Preguntas o sugerencias?** Abre un issue en GitHub.

