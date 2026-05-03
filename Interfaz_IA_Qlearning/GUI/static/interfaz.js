// ================= VARIABLES GLOBALES =================

// Intervalo para ejecución automática (simulación paso a paso)
let autoPlayInterval = null;

// Bandera para saber si el entrenamiento visual está activo
let entrenandoVisualmente = false;

// Dimensiones del mapa
let filas = 10;
let columnas = 10;

// Matriz local del mapa (0 = libre, 1 = muro)
let mapaLocal = Array(10).fill().map(() => Array(10).fill(0));

// Muestra un mensaje temporal tipo "toast"
function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.style.display = 'block';

    // Oculta el mensaje después de 2.5s
    setTimeout(() => t.style.display = 'none', 2500);
}

// Convierte un valor Q en un color (gradiente rojo-verde)
function getColorForQ(val, min, max) {
    if (val === 0) return 'transparent'; // Sin información

    // Normaliza el valor entre 0 y 1
    const ratio = (val - min) / (max - min || 1);

    // Genera color: rojo (bajo) → verde (alto)
    const r = Math.floor(255 * (1 - ratio));
    const g = Math.floor(255 * ratio);

    return `rgba(${r}, ${g}, 50, 0.5)`;
}

// Abre/cierra el menú lateral
function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    document.getElementById('main-content').classList.toggle('expanded');
}

// Cambia de vista/pestaña
function navegar(id, btn) {
    detenerTodo(); // Detiene procesos activos

    // Quita clases activas de todas las vistas y botones
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    // Activa la vista seleccionada
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');

    renderizar();

    // Si es vista de diseño, redibuja el mapa editable
    if(id === 'diseno') dibujarMapaDiseno();
}

// Detiene entrenamiento visual y autoplay
function detenerTodo() {
    entrenandoVisualmente = false;
    clearInterval(autoPlayInterval);
    autoPlayInterval = null;

    // Reset de botones
    document.getElementById('btn-auto').innerText = "Auto-Play";
    document.getElementById('btn-v-train').innerText = "Iniciar Observación";
}

// Cambia dimensiones del mapa desde inputs
function cambiarDimensiones() {
    filas = parseInt(document.getElementById('dim-f').value);
    columnas = parseInt(document.getElementById('dim-c').value);

    // Solo creamos matriz vacía si el mapaLocal no coincide con las dimensiones
    // o si se llama explícitamente para resetear.
    if (!mapaLocal || mapaLocal.length !== filas || (mapaLocal[0] && mapaLocal[0].length !== columnas)) {
        mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));
    }

    dibujarMapaDiseno();
}

// Envía configuración completa al backend
async function confirmarYPasar(navegarAuto = true) {
    // 1. Captura y conversión de tipos para asegurar decimales correctos
    const data = {
        alpha: parseFloat(document.getElementById('alpha').value),
        gamma: parseFloat(document.getElementById('gamma').value),
        epsilon: parseFloat(document.getElementById('epsilon').value),
        epocas: parseInt(document.getElementById('epocas').value),
        r_meta: parseFloat(document.getElementById('r-meta').value),
        r_muro: parseFloat(document.getElementById('r-muro').value),
        r_paso: parseFloat(document.getElementById('r-paso').value),
        mapa: mapaLocal,
        filas: filas,
        columnas: columnas
    };

    // 2. Bloque de validaciones
    let errores = [];
    if (isNaN(data.gamma) || data.gamma >= 1 || data.gamma < 0) {
        errores.push("⚠️ Gamma debe ser un decimal menor a 1 (ej: 0.99).");
    }
    if (isNaN(data.alpha) || data.alpha <= 0 || data.alpha > 1) {
        errores.push("⚠️ Alpha debe estar entre 0.01 y 1.");
    }
    if (data.r_paso >= 0 && data.r_meta > 0) {
        errores.push("⚠️ El 'Paso' debería ser negativo para incentivar la ruta corta.");
    }
    if (isNaN(data.epocas) || data.epocas <= 0) {
        errores.push("⚠️ El número de épocas debe ser mayor a 0.");
    }

    if (errores.length > 0) {
        alert("🚨 Configuración no válida:\n\n" + errores.join("\n"));
        return;
    }

    // 3. Envío al servidor
    try {
        await fetch('/api/actualizar_todo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        showToast("¡Configuración sincronizada con el motor!");

        // 4. Navegación condicional
        if (navegarAuto) {
            document.getElementById('btn-v-train').classList.remove('hidden');
            document.getElementById('btn-v-skip').classList.remove('hidden');
            document.getElementById('btn-ir-simular').classList.add('hidden');

            setTimeout(() => {
                const navBtn = document.getElementById('nav-aprendizaje');
                navegar('aprendizaje', navBtn);
            }, 1000);
        }
    } catch (error) {
        console.error("Error al sincronizar:", error);
        showToast("Error de conexión con el servidor");
    }
}

// Genera un mapa aleatorio desde el backend
async function generarAleatorio() {

    // 1. Leer dimensiones
    const f = document.getElementById('dim-f').value;
    const c = document.getElementById('dim-c').value;

    // 2. Solicitar mapa al servidor
    const res = await fetch('/api/generar_aleatorio', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filas: f, columnas: c })
    });

    const data = await res.json();

    // 3. Sincronizar dimensiones
    filas = data.dimensiones.f;
    columnas = data.dimensiones.c;

    // 4. Reconstruir matriz local
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));

    // Recorrer celdas devueltas
    data.mapa.forEach(celda => {
        if(celda.tipo === "muro") mapaLocal[celda.x][celda.y] = 1;
    });

    // 5. Dibujar
    dibujarMapaDiseno();
    showToast(`Mapa aleatorio de ${filas}x${columnas} generado`);
}

// Dibuja grid editable
function dibujarMapaDiseno() {
    const container = document.getElementById('grid-diseno');
    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

    for(let f=0; f<filas; f++) {
        for(let c=0; c<columnas; c++) {
            const div = document.createElement('div');
            div.className = `cell ${mapaLocal[f][c] === 1 ? 'muro' : ''}`;

            // Inicio siempre en 0,0
            if(f === 0 && c === 0) div.classList.add('robot');

            // META siempre en el extremo opuesto
            if(f === filas - 1 && c === columnas - 1) {
                div.classList.add('meta');
                mapaLocal[f][c] = 0; // La meta nunca debe ser un muro
            }

            div.onclick = () => {
                // Impedir poner muros en inicio o meta
                if((f===0 && c===0) || (f===filas-1 && c===columnas-1)) return;
                mapaLocal[f][c] = mapaLocal[f][c] === 1 ? 0 : 1;
                div.classList.toggle('muro');
            };
            container.appendChild(div);
        }
    }
}

// Limpia todo el mapa
function limpiarMapa() {
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));
    dibujarMapaDiseno();
}

// Actualiza label de velocidad
function actualizarLabelVelocidad(val) {
    document.getElementById('speed-label').innerText = `${val}ms`;
}

// Activa/desactiva entrenamiento visual
function toggleEntrenamientoVisual() {
    entrenandoVisualmente = !entrenandoVisualmente;

    const btn = document.getElementById('btn-v-train');
    btn.innerText = entrenandoVisualmente ? "Detener" : "Iniciar Observación";

    if(entrenandoVisualmente) loopEntrenamiento();
}

// Loop recursivo de entrenamiento visual
async function loopEntrenamiento() {

    // Condición de salida
    if(!entrenandoVisualmente) return;

    // Solicita siguiente paso
    const res = await fetch('/api/paso_visual', { method: 'POST' });
    const data = await res.json();

    // Dibuja resultados
    dibujarMapaRealCalor('grid-train', data);
    dibujarMapaDetallado('grid-train-detail', data);

    // Repite con delay dinámico
    setTimeout(loopEntrenamiento, document.getElementById('speed-slider').value);
}

// Entrenamiento rápido sin visualización
async function entrenarRapido() {
    showToast("Entrenando a máxima velocidad...");

    const payload = {
        filas: filas,
        columnas: columnas,
        mapa: mapaLocal
    };

    const res = await fetch('/api/entrenar_fast', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });

    if (res.ok) {

        // Oculta controles
        document.getElementById('btn-v-train').classList.add('hidden');
        document.getElementById('btn-v-skip').classList.add('hidden');

        // Renderiza resultado final
        await renderizar();

        // Muestra simulación
        document.getElementById('btn-ir-simular').classList.remove('hidden');
        showToast("¡Entrenamiento Completo!");
    }
}

// Obtiene estado global del backend y actualiza UI
async function renderizar() {
    try {
        const res = await fetch('/api/estado');
        const data = await res.json();

        if (!data || !data.dimensiones) return;

        // Sincronización global
        filas = data.dimensiones.f;
        columnas = data.dimensiones.c;

        // Ajuste de grids
        const grids = ['grid-train', 'grid-uso', 'grid-train-detail'];

        grids.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
                container.style.width = "100%";
                container.style.maxWidth = "600px";
            }
        });

        // Mostrar botón simulación si hay conocimiento
        const btnIrSimular = document.getElementById('btn-ir-simular');
        if (btnIrSimular && data.mapa) {
            const tieneConocimiento = data.mapa.some(c => c.q_max && Math.abs(c.q_max) > 0.0001);
            if (tieneConocimiento) {
                btnIrSimular.classList.remove('hidden');
            }
        }

        // Dibujar mapas
        dibujarMapaRealCalor('grid-train', data);
        dibujarMapaRealCalor('grid-uso', data);
        dibujarMapaDetallado('grid-train-detail', data);

    } catch (error) {
        console.error("Error en renderizado dinámico:", error);
    }
}

// Mapa con valores Q (heatmap)
function dibujarMapaRealCalor(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

    // Extrae todos los Q
    const allQs = data.mapa.filter(c => c.tipo === "libre").map(c => c.q_max);

    const minQ = Math.min(...allQs);
    const maxQ = Math.max(...allQs);

    // Recorre cada celda
    data.mapa.forEach(celda => {
        const div = document.createElement('div');
        div.className = `cell ${celda.tipo}`;

        if (celda.tipo === "libre") {
            div.style.backgroundColor = getColorForQ(celda.q_max, minQ, maxQ);
            div.innerHTML = `<span>${celda.q_max.toFixed(0)}</span>`;
        }

        // Posición del robot
        if (data.posicion[0] === celda.x && data.posicion[1] === celda.y) {
            div.classList.add('robot');
        }

        container.appendChild(div);
    });
}

// Mapa detallado (valores Q por dirección)
function dibujarMapaDetallado(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

    // Recorre cada celda
    data.mapa.forEach(celda => {
        const div = document.createElement('div');
        div.className = `q-detail-cell ${celda.tipo}`;

        if (celda.tipo === "libre" && celda.q_values) {
            div.innerHTML = `
                <div class="q-val q-up">${celda.q_values.up.toFixed(0)}</div>
                <div class="q-val q-down">${celda.q_values.down.toFixed(0)}</div>
                <div class="q-val q-left">${celda.q_values.left.toFixed(0)}</div>
                <div class="q-val q-right">${celda.q_values.right.toFixed(0)}</div>
                <div class="q-center">${celda.q_max.toFixed(0)}</div>
            `;
        }

        if (data.posicion[0] === celda.x && data.posicion[1] === celda.y) {
            div.classList.add('robot');
        }

        container.appendChild(div);
    });
}

// Ejecuta un paso en modo uso
async function pedirPaso() {
    await fetch('/api/paso_uso', { method: 'POST' });
    renderizar();
}

// Activa/desactiva autoplay
function toggleAutoPlay() {
    const btn = document.getElementById('btn-auto');

    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        btn.innerText = "Auto-Play";
    } else {
        autoPlayInterval = setInterval(pedirPaso, 300);
        btn.innerText = "Detener Auto-Play";
    }
}

// Reinicia todo el sistema
async function reiniciarTodoElProceso() {

    if (!confirm("¿Estás seguro de que quieres borrar el entrenamiento actual y crear un nuevo mapa?")) return;

    detenerTodo();

    // Reset backend
    await fetch('/api/redimensionar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filas: filas, columnas: columnas })
    });

    // Reset local
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));

    // Reset UI
    document.getElementById('btn-v-train').classList.remove('hidden');
    document.getElementById('btn-v-skip').classList.remove('hidden');
    document.getElementById('btn-ir-simular').classList.add('hidden');

    showToast("Sistema reiniciado. Configura tu nuevo mapa.");

    navegar('diseno', document.getElementById('nav-diseno'));
}

function abrirModalMapas() {
    const modal = document.getElementById('modal-mapas');
    if (modal) {
        modal.classList.remove('hidden');
        cargarListaMapas();
    }
}

function cerrarModalMapas() {
    document.getElementById('modal-mapas').classList.add('hidden');
}

// Guarda el mapa Y los valores de los inputs actuales
async function guardarMapaActual() {
    // 1. Capturar valores de los inputs
    const alpha = parseFloat(document.getElementById('alpha').value);
    const gamma = parseFloat(document.getElementById('gamma').value);
    const epsilon = parseFloat(document.getElementById('epsilon').value);
    const epocas = parseInt(document.getElementById('epocas').value);
    const rMeta = parseFloat(document.getElementById('r-meta').value);

    // 2. Lógica de Alertas (Validaciones)
    let errores = [];

    if (gamma >= 1) {
        errores.push("⚠️ Gamma debe ser menor a 1 (ej: 0.99). Si es 1 o más, los valores Q crecerán hasta el infinito (Overflow).");
    }
    if (alpha <= 0 || alpha > 1) {
        errores.push("⚠️ Alpha (Learning Rate) debe estar entre 0.01 y 1.");
    }
    if (epocas <= 0 || epocas > 50000) {
        errores.push("⚠️ El número de épocas debe ser positivo y razonable (máx 50,000 para evitar bloqueos).");
    }
    if (rMeta > 1000) {
        errores.push("⚠️ Una recompensa de Meta demasiado alta (>1000) puede causar inestabilidad numérica.");
    }
    if (epsilon < 0 || epsilon > 1) {
        errores.push("⚠️ Epsilon debe estar entre 0 y 1 (probabilidad de exploración).");
    }

    // 3. Si hay errores, detener el proceso y avisar
    if (errores.length > 0) {
        alert("Configuración no recomendada:\n\n" + errores.join("\n"));
        return; // Bloquea el guardado
    }

    // 4. Si todo está bien, proceder con el guardado
    const datos = {
        filas: filas,
        columnas: columnas,
        mapa: mapaLocal,
        hiperparametros: {
            alpha: alpha,
            gamma: gamma,
            epsilon: epsilon,
            epocas: epocas,
            r_meta: rMeta,
            r_muro: document.getElementById('r-muro').value,
            r_paso: document.getElementById('r-paso').value
        }
    };

    try {
        const res = await fetch('/api/guardar_mapa', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(datos)
        });

        if(res.ok) {
            showToast("¡Mapa y configuración validados y guardados!");
            cargarListaMapas();
        }
    } catch (error) {
        console.error("Error al guardar:", error);
    }
}

async function cargarListaMapas() {
    const res = await fetch('/api/listar_mapas');
    const mapas = await res.json();
    const contenedor = document.getElementById('lista-mapas');

    if (!contenedor) return;

    if (mapas.length === 0) {
        contenedor.innerHTML = '<p style="color:var(--text-dim); text-align:center; padding:20px;">No hay mapas guardados.</p>';
        return;
    }

    contenedor.innerHTML = mapas.map(m => `
        <div class="mapa-item" style="display: flex; justify-content: space-between; align-items: center; background: #2a2a2a; padding: 10px; margin-bottom: 5px; border-radius: 5px;">
            <span>💾 ${m.nombre} <small>(${m.filas}x${m.columnas})</small></span>
            <button class="btn-gemini" style="padding: 5px 10px; width: auto; font-size: 12px;" onclick="cargarMapaServidor('${m.nombre}')">Cargar</button>
        </div>
    `).join('');
}

async function cargarMapaServidor(nombre) {
    const res = await fetch('/api/cargar_mapa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ nombre: nombre })
    });
    const datos = await res.json();

    aplicarMapaCargado(datos);
    cerrarModalMapas();
}

// Función crítica: Actualiza la lógica Y los inputs de la pantalla
function aplicarMapaCargado(datos) {
    // 1. Actualizar variables globales
    filas = parseInt(datos.filas);
    columnas = parseInt(datos.columnas);
    mapaLocal = datos.mapa;

    // 2. Actualizar inputs de Dimensiones en la UI
    document.getElementById('dim-f').value = filas;
    document.getElementById('dim-c').value = columnas;

    // 3. Restaurar Hiperparámetros en los inputs
    if (datos.hiperparametros) {
        const hp = datos.hiperparametros;
        document.getElementById('alpha').value = hp.alpha || 0.1;
        document.getElementById('gamma').value = hp.gamma || 0.9;
        document.getElementById('epsilon').value = hp.epsilon || 0.1;
        document.getElementById('epocas').value = hp.epocas || 1000;
        document.getElementById('r-meta').value = hp.r_meta || 100;
        document.getElementById('r-muro').value = hp.r_muro || -100;
        document.getElementById('r-paso').value = hp.r_paso || -1;
    }

    // 4. Asegurar que la meta sea transitable
    mapaLocal[filas - 1][columnas - 1] = 0;

    // 5. LLAMADA CRÍTICA: Forzar redimensión de la cuadrícula usando la lógica manual
    cambiarDimensiones();

    // 6. Sincronizar con el backend y refrescar visualmente todos los grids
    confirmarYPasar(false).then(() => {
        renderizar(); // Esto asegura que grid-train, grid-uso, etc., se ajusten
    });

    showToast("Mapa cargado y cuadrícula redimensionada");
}

// Función para cargar y mostrar el historial en el sidebar
// Función para cargar y mostrar el historial en el sidebar con scroll independiente
async function cargarHistorialSidebar() {
    try {
        const res = await fetch('/api/obtener_historial');
        const datos = await res.json();
        const contenedor = document.getElementById('lista-historial-sidebar');

        if (!contenedor) return;

        if (!datos || datos.length === 0) {
            contenedor.innerHTML = '<p style="font-size: 0.7rem; color: var(--text-dim); text-align: center;">Sin actividad reciente</p>';
            return;
        }

        // Renderizar los elementos (los más recientes primero)
        contenedor.innerHTML = datos.reverse().map(item => {
            // Limpiamos el nombre: quitamos .csv y separamos por guiones bajos
            const nombreLimpio = item.nombre.replace('.csv', '');
            const partes = nombreLimpio.split('_');

            // Ejemplo: 10X10_2026-05-02 -> Título: 10X10, Detalle: 2026-05-02
            const titulo = partes[0] || "Registro";
            const fecha = partes[1] || "";
            const hora = partes[2] ? partes[2].replace(/-/g, ':') : "";

            return `
                <div class="historial-box-item" style="
                    font-size: 0.7rem; 
                    background: rgba(255, 255, 255, 0.03); 
                    padding: 10px; 
                    border-radius: 6px; 
                    color: #e0e0e0; 
                    border-left: 3px solid #4285f4;
                    transition: background 0.2s;
                    cursor: default;">
                    <div style="color: #4285f4; font-weight: bold; margin-bottom: 3px; display: flex; justify-content: space-between;">
                        <span>${titulo}</span>
                        <span style="font-size: 0.6rem; opacity: 0.5;">${hora}</span>
                    </div>
                    <div style="opacity: 0.7; font-size: 0.65rem;">${fecha}</div>
                </div>
            `;
        }).join('');

    } catch (e) {
        console.error("Error al cargar el historial del sidebar:", e);
    }
}

// Aseguramos que se cargue al iniciar la página
window.addEventListener('load', () => {
    if (typeof dibujarMapaDiseno === 'function') dibujarMapaDiseno();
    if (typeof renderizar === 'function') renderizar();
    cargarHistorialSidebar();
});

// Inicialización de la página
window.addEventListener('load', () => {
    // Asegúrate de que estas funciones existan en tu archivo
    if (typeof dibujarMapaDiseno === 'function') dibujarMapaDiseno();
    if (typeof renderizar === 'function') renderizar();

    // Cargar el historial en el menú lateral
    cargarHistorialSidebar();
});

// Modifica la inicialización para que cargue el historial al abrir la página[cite: 3]
window.addEventListener('load', () => {
    dibujarMapaDiseno();
    renderizar();
    cargarHistorialSidebar();
});

// Al cargar la página
window.onload = () => {
    dibujarMapaDiseno();
    renderizar();
};