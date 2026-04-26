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


// ================= UTILIDADES UI =================

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


// ================= NAVEGACIÓN =================

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


// ================= CONTROL DE PROCESOS =================

// Detiene entrenamiento visual y autoplay
function detenerTodo() {
    entrenandoVisualmente = false;
    clearInterval(autoPlayInterval);
    autoPlayInterval = null;

    // Reset de botones
    document.getElementById('btn-auto').innerText = "Auto-Play";
    document.getElementById('btn-v-train').innerText = "Iniciar Observación";
}


// ================= CONFIGURACIÓN =================

// Cambia dimensiones del mapa desde inputs
function cambiarDimensiones() {
    filas = parseInt(document.getElementById('dim-f').value);
    columnas = parseInt(document.getElementById('dim-c').value);

    // Crea nueva matriz vacía
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));

    dibujarMapaDiseno();
}


// Envía configuración completa al backend
async function confirmarYPasar() {
    const data = {
        alpha: document.getElementById('alpha').value,
        gamma: document.getElementById('gamma').value,
        epsilon: document.getElementById('epsilon').value,
        epocas: document.getElementById('epocas').value,
        r_meta: document.getElementById('r-meta').value,
        r_muro: document.getElementById('r-muro').value,
        r_paso: document.getElementById('r-paso').value,
        mapa: mapaLocal,
        filas: filas,
        columnas: columnas
    };

    // POST al servidor
    await fetch('/api/actualizar_todo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    showToast("¡Configuración guardada!");

    // Ajuste de botones
    document.getElementById('btn-v-train').classList.remove('hidden');
    document.getElementById('btn-v-skip').classList.remove('hidden');
    document.getElementById('btn-ir-simular').classList.add('hidden');

    showToast("Configuración cargada. ¡A entrenar!");

    // Navega a aprendizaje
    setTimeout(() => navegar('aprendizaje', document.getElementById('nav-aprendizaje')), 1000);
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


// ================= DISEÑO DEL MAPA =================

// Dibuja grid editable
function dibujarMapaDiseno() {
    const container = document.getElementById('grid-diseno');

    // Define columnas del grid
    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

    // BUCLE doble: recorre cada celda
    for(let f=0; f<filas; f++) {
        for(let c=0; c<columnas; c++) {

            const div = document.createElement('div');

            // Clase base + muro si aplica
            div.className = `cell ${mapaLocal[f][c] === 1 ? 'muro' : ''}`;

            // Posiciones especiales
            if(f===0 && c===0) div.classList.add('robot');
            if(f===filas-1 && c===columnas-1) div.classList.add('meta');

            // Evento click: alterna muro/libre
            div.onclick = () => {
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


// ================= ENTRENAMIENTO =================

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


// ================= RENDERIZADO =================

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


// ================= VISUALIZACIÓN =================

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


// ================= SIMULACIÓN =================

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


// ================= RESET =================

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


// ================= INICIALIZACIÓN =================

// Al cargar la página
window.onload = () => { 
    dibujarMapaDiseno(); 
    renderizar(); 
};