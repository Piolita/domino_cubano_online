/* ==========================================================================
   1. CONFIGURACIÓN INICIAL Y VARIABLES GLOBALES
   ========================================================================== */
const socket = io();
const pantallaInicio = document.getElementById('pantalla-inicio');
const mesaJuego = document.getElementById('mesa-juego');
const btnIniciar = document.getElementById('btn-iniciar');

// Variable crítica: guarda el asiento que elegiste 
let asientoSeleccionado = null;

function obtenerPosicionVisual(asientoRival) {
    const total = 6;
    const s = parseInt(asientoSeleccionado);
    const r = parseInt(asientoRival);

    // Esta fórmula garantiza que tú siempre seas el centro (Posición 1)
    // y los demás giren a tu alrededor correctamente.
    let posRelativa = (r - s + total) % total;
    
    // Retornamos del 1 al 6 para coincidir con los nuevos IDs del CSS
    return posRelativa + 1;
}

/* ==========================================================================
   2. FUNCIONES DEL LOBBY (ANTES DE ENTRAR A LA MESA)
   ========================================================================== */

// --- A. Seleccionar el asiento visualmente ---
function seleccionarAsiento(numero) {
    asientoSeleccionado = String(numero);
    
    // Solo gestionamos la "etiqueta" (clase), no el color
    document.querySelectorAll('#seleccion-asiento button').forEach(btn => {
        // Quitamos la clase de activo a todos
        btn.classList.remove('asiento-activo');
        
        // Se la ponemos solo al botón que coincide con el número elegido
        if (btn.getAttribute('onclick').includes(numero)) {
            btn.classList.add('asiento-activo');
        }
    });
}

// --- B. Confirmar nombre y asiento para entrar ---
function confirmarAsiento() {
    const nombreInput = document.getElementById('nombre-jugador');
    const nombre = nombreInput.value;
    
    if (!asientoSeleccionado || !nombre) {
        alert("Escoje un lugar y escriba tu nombre.");
        return;
    }

    // ESTA ES LA LLAVE QUE ABRE LA MESA:
    document.body.classList.add('juego-activo');

    socket.emit('unirse_juego', {
        nombre: nombre,
        asiento: asientoSeleccionado
    });

    socket.emit('solicitar_lista_jugadores');
}

/* ==========================================================================
   3. EVENTOS DE JUGADORES (QUIÉN ENTRA Y SE SIENTA)
   ========================================================================== */

socket.on('jugador_sentado', (data) => { 
   
    const botones = document.querySelectorAll('#seleccion-asiento button');
    botones.forEach(btn => {
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(data.asiento)) {
            btn.disabled = true;
            
            btn.classList.add('asiento-ocupado');
            btn.innerText = `Ocupado por ${data.nombre}`;
        }
    });

    // B. LÓGICA DE DIBUJO EN MESA
    const esMiPropioAsiento = String(data.asiento) === String(asientoSeleccionado);
    
    if (esMiPropioAsiento) {
        const miZona = document.getElementById('mi-mano');
        if (miZona) {
            const previa = document.getElementById('etiqueta-yo');
            if (previa) previa.remove();
            const etiquetaYo = document.createElement('div');
            etiquetaYo.id = 'etiqueta-yo';
            etiquetaYo.className = 'mi-nombre-etiqueta';
            etiquetaYo.innerText = "YO: " + data.nombre;
            miZona.parentNode.insertBefore(etiquetaYo, miZona);
        }
    } else {
        const numeroPos = obtenerPosicionVisual(data.asiento);
        const contenedorEnMesa = document.getElementById(`pos-visual-${numeroPos}`);

        if (contenedorEnMesa) {
            
            contenedorEnMesa.classList.add('rival-activo'); 

            const etiquetasViejas = contenedorEnMesa.querySelectorAll('.nombre-rival-etiqueta');
            etiquetasViejas.forEach(el => el.remove());

            const etiquetaRival = document.createElement('div');
            etiquetaRival.className = 'nombre-rival-etiqueta';
            etiquetaRival.innerText = data.nombre;
            contenedorEnMesa.prepend(etiquetaRival);
        }
    }
});

// --- C. SOLICITAR ACTUALIZACIÓN AL ENTRAR ---
socket.on('connect', () => {
    if (asientoSeleccionado) {
        socket.emit('solicitar_lista_jugadores');
    }
});


/* ==========================================================================
   4. CONTROL DE LA PARTIDA, FICHAS Y TABLERO
   ========================================================================== */

socket.on('mostrar_boton_inicio', () => {
    if (btnIniciar) {
        btnIniciar.classList.add('visible');
    }
});

btnIniciar.onclick = () => { 
    socket.emit('iniciar_partida'); 
};

socket.on('partida_iniciada', () => { 
    console.log("¡Llegó la orden del servidor! Escondiendo botón...");
    if (btnIniciar) {
        btnIniciar.classList.remove('visible');
    }
});



/* ==========================================================================
   5. RECEPCIÓN DE FICHAS (TUS FICHAS CON CLIC)
   ========================================================================== */
socket.on('recibir_fichas', (data) => {
    const contenedor = document.getElementById('mi-mano');
    if (!contenedor) return;
    
    contenedor.innerHTML = ""; // Limpiamos la mano anterior
    
    data.mano.forEach(ficha => {
        const div = document.createElement('div');
        div.className = 'ficha-domino';
        
        // 1. Guardamos los números de forma invisible dentro del DIV
        div.dataset.lado1 = ficha.lado1;
        div.dataset.lado2 = ficha.lado2;

        // 2. Creamos el aspecto visual con los colores
        div.innerHTML = `
            <div class="numero numero-${ficha.lado1}">${ficha.lado1}</div>
            <div class="divisor"></div>
            <div class="numero numero-${ficha.lado2}">${ficha.lado2}</div>
        `;

        // 3. LA LLAVE DEL ÉXITO: Le decimos qué hacer cuando le des clic
        div.onclick = () => seleccionarFicha(div);

        contenedor.appendChild(div);
    });
});

/* ==========================================================================
   6. FUNCIÓN PARA RESALTAR LA FICHA ELEGIDA
   ========================================================================== */
function seleccionarFicha(elementoFicha) {
    // Primero quitamos el brillo de cualquier otra ficha que hayamos tocado antes
    document.querySelectorAll('.ficha-domino').forEach(f => {
        f.classList.remove('ficha-seleccionada');
    });

    // Luego le ponemos el brillo dorado a la ficha que acabamos de tocar
    elementoFicha.classList.add('ficha-seleccionada');
    
    // Esto es para que tú veas en la consola que el programa sí sabe qué ficha tocaste
    console.log("Has elegido la ficha: " + elementoFicha.dataset.lado1 + " - " + elementoFicha.dataset.lado2);
}

/* ==========================================================================
   7. ACTUALIZAR MANO RIVALES
   ========================================================================== */


socket.on('actualizar_manos_rivales', (data) => {
    // 1. Si soy yo, no me dibujo fichas ocultas (yo ya veo las mías en mi-mano)
    if (String(data.asiento) === String(asientoSeleccionado)) return; 

    // 2. Calculamos la posición visual relativa
    const numeroPos = obtenerPosicionVisual(data.asiento);
    const contenedor = document.getElementById(`pos-visual-${numeroPos}`);

    if (contenedor) {
        // Borramos solo las fichas viejas para no borrar el nombre del primo
        const fichasViejas = contenedor.querySelectorAll('.ficha-rival');
        fichasViejas.forEach(f => f.remove());
        
        // Dibujamos la cantidad de fichas que el servidor nos reportó
        for (let i = 0; i < data.cantidad; i++) {
            const fichaOculta = document.createElement('div');
            fichaOculta.className = 'ficha-rival'; 
            contenedor.appendChild(fichaOculta);
        }
    }
});