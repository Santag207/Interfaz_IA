let autoPlayInterval = null;
let entrenandoVisualmente = false;
let filas = 10;
let columnas = 10;
let mapaLocal = Array(10).fill().map(() => Array(10).fill(0));

function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg; t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 2500);
}

function getColorForQ(val, min, max) {
    if (val === 0) return 'transparent';
    const ratio = (val - min) / (max - min || 1);
    const r = Math.floor(255 * (1 - ratio));
    const g = Math.floor(255 * ratio);
    return `rgba(${r}, ${g}, 50, 0.5)`;
}

function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    document.getElementById('main-content').classList.toggle('expanded');
}

function navegar(id, btn) {
    detenerTodo();
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
    renderizar();
    if(id === 'diseno') dibujarMapaDiseno();
}

function detenerTodo() {
    entrenandoVisualmente = false;
    clearInterval(autoPlayInterval);
    autoPlayInterval = null;
    document.getElementById('btn-auto').innerText = "Auto-Play";
    document.getElementById('btn-v-train').innerText = "Iniciar Observación";
}

function cambiarDimensiones() {
    filas = parseInt(document.getElementById('dim-f').value);
    columnas = parseInt(document.getElementById('dim-c').value);
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));
    dibujarMapaDiseno();
}

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
    await fetch('/api/actualizar_todo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    showToast("¡Configuración guardada!");
    document.getElementById('btn-v-train').classList.remove('hidden');
    document.getElementById('btn-v-skip').classList.remove('hidden');
    document.getElementById('btn-ir-simular').classList.add('hidden');

    showToast("Configuración cargada. ¡A entrenar!");
    setTimeout(() => navegar('aprendizaje', document.getElementById('nav-aprendizaje')), 1000);
}

async function generarAleatorio() {
    // 1. Obtener lo que el usuario escribió en los inputs
    const f = document.getElementById('dim-f').value;
    const c = document.getElementById('dim-c').value;

    // 2. Enviar esos datos al servidor
    const res = await fetch('/api/generar_aleatorio', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filas: f, columnas: c })
    });

    const data = await res.json();

    // 3. ACTUALIZACIÓN CRÍTICA: Sincronizar dimensiones locales con las del servidor
    filas = data.dimensiones.f;
    columnas = data.dimensiones.c;

    // 4. Reconstruir el mapa local para que coincida con el nuevo tamaño
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));
    data.mapa.forEach(celda => {
        if(celda.tipo === "muro") mapaLocal[celda.x][celda.y] = 1;
    });

    // 5. Dibujar
    dibujarMapaDiseno();
    showToast(`Mapa aleatorio de ${filas}x${columnas} generado`);
}

function dibujarMapaDiseno() {
    const container = document.getElementById('grid-diseno');
    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';
    for(let f=0; f<filas; f++) {
        for(let c=0; c<columnas; c++) {
            const div = document.createElement('div');
            div.className = `cell ${mapaLocal[f][c] === 1 ? 'muro' : ''}`;
            if(f===0 && c===0) div.classList.add('robot');
            if(f===filas-1 && c===columnas-1) div.classList.add('meta');
            div.onclick = () => {
                if((f===0 && c===0) || (f===filas-1 && c===columnas-1)) return;
                mapaLocal[f][c] = mapaLocal[f][c] === 1 ? 0 : 1;
                div.classList.toggle('muro');
            };
            container.appendChild(div);
        }
    }
}

function limpiarMapa() {
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));
    dibujarMapaDiseno();
}

function actualizarLabelVelocidad(val) {
    document.getElementById('speed-label').innerText = `${val}ms`;
}

function toggleEntrenamientoVisual() {
    entrenandoVisualmente = !entrenandoVisualmente;
    const btn = document.getElementById('btn-v-train');
    btn.innerText = entrenandoVisualmente ? "Detener" : "Iniciar Observación";
    if(entrenandoVisualmente) loopEntrenamiento();
}

async function loopEntrenamiento() {
    if(!entrenandoVisualmente) return;
    const res = await fetch('/api/paso_visual', { method: 'POST' });
    const data = await res.json();
    dibujarMapaRealCalor('grid-train', data);
    dibujarMapaDetallado('grid-train-detail', data);
    setTimeout(loopEntrenamiento, document.getElementById('speed-slider').value);
}

async function entrenarRapido() {
    showToast("Entrenando a máxima velocidad...");

    // Enviamos el estado actual del mapa y dimensiones para evitar el IndexError
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
        // Ocultamos controles de entrenamiento visual
        document.getElementById('btn-v-train').classList.add('hidden');
        document.getElementById('btn-v-skip').classList.add('hidden');

        // Renderizamos el resultado final (Valores Q calculados)
        await renderizar();

        // Mostramos el botón de simulación
        document.getElementById('btn-ir-simular').classList.remove('hidden');
        showToast("¡Entrenamiento Completo!");
    }
}

async function renderizar() {
    try {
        const res = await fetch('/api/estado');
        const data = await res.json();

        if (!data || !data.dimensiones) return;

        // Sincronizar variables globales inmediatamente
        filas = data.dimensiones.f;
        columnas = data.dimensiones.c;

        // FORZAR el estilo de columnas en todos los contenedores antes de dibujar
        const grids = ['grid-train', 'grid-uso', 'grid-train-detail'];
        grids.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
                container.style.width = "100%"; // Evita que se desborde
                container.style.maxWidth = "600px"; // O el tamaño máximo que prefieras
            }
        });

        // Lógica del botón de simulación
        const btnIrSimular = document.getElementById('btn-ir-simular');
        if (btnIrSimular && data.mapa) {
            const tieneConocimiento = data.mapa.some(c => c.q_max && Math.abs(c.q_max) > 0.0001);
            if (tieneConocimiento) {
                btnIrSimular.classList.remove('hidden');
            }
        }

        // Dibujar contenido
        dibujarMapaRealCalor('grid-train', data);
        dibujarMapaRealCalor('grid-uso', data);
        dibujarMapaDetallado('grid-train-detail', data);

    } catch (error) {
        console.error("Error en renderizado dinámico:", error);
    }
}

// PANEL IZQUIERDO: Mapa Real con Calor dinámico y obstáculos
function dibujarMapaRealCalor(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

    const allQs = data.mapa.filter(c => c.tipo === "libre").map(c => c.q_max);
    const minQ = Math.min(...allQs);
    const maxQ = Math.max(...allQs);

    data.mapa.forEach(celda => {
        const div = document.createElement('div');
        div.className = `cell ${celda.tipo}`;
        if (celda.tipo === "libre") {
            div.style.backgroundColor = getColorForQ(celda.q_max, minQ, maxQ);
            div.innerHTML = `<span>${celda.q_max.toFixed(0)}</span>`;
        }
        if (data.posicion[0] === celda.x && data.posicion[1] === celda.y) div.classList.add('robot');
        container.appendChild(div);
    });
}

// PANEL DERECHO: Detalle de valores Q (Flechas/Direcciones)
function dibujarMapaDetallado(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;
    container.innerHTML = '';

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
        if (data.posicion[0] === celda.x && data.posicion[1] === celda.y) div.classList.add('robot');
        container.appendChild(div);
    });
}

async function pedirPaso() {
    await fetch('/api/paso_uso', { method: 'POST' });
    renderizar();
}

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

async function reiniciarTodoElProceso() {
    if (!confirm("¿Estás seguro de que quieres borrar el entrenamiento actual y crear un nuevo mapa?")) return;

    detenerTodo(); // Detiene Auto-Play o entrenamiento visual si están activos

    // 1. Avisar al servidor que limpie la Matriz Q y resetee el agente
    // Usaremos la ruta /api/redimensionar que ya tienes, pues esta reinicia la MatrizQ
    await fetch('/api/redimensionar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filas: filas, columnas: columnas })
    });

    // 2. Resetear variables locales
    mapaLocal = Array(filas).fill().map(() => Array(columnas).fill(0));

    // 3. Resetear botones de la pestaña de entrenamiento
    document.getElementById('btn-v-train').classList.remove('hidden');
    document.getElementById('btn-v-skip').classList.remove('hidden');
    document.getElementById('btn-ir-simular').classList.add('hidden');

    // 4. Volver a la pestaña 1
    showToast("Sistema reiniciado. Configura tu nuevo mapa.");
    navegar('diseno', document.getElementById('nav-diseno'));
}

window.onload = () => { dibujarMapaDiseno(); renderizar(); };
