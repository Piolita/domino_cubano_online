/* ==========================================================================
    CONFIGURACIÓN INICIAL Y VARIABLES GLOBALES Navegador
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

    // tú siempre seas el centro (Posición 1)
    let posRelativa = (r - s + total) % total;
    
    // Retornamos del 1 al 6 para coincidir con los nuevos IDs del CSS
    return posRelativa + 1;
}

/* ==========================================================================
    FUNCIONES DEL LOBBY (ANTES DE ENTRAR A LA MESA)
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

    //  ABRE LA MESA
    document.body.classList.add('juego-activo');

    socket.emit('unirse_juego', {
        nombre: nombre,
        asiento: asientoSeleccionado
    });

    socket.emit('solicitar_lista_jugadores');
}

/* ==========================================================================
    EVENTOS DE JUGADORES (QUIÉN ENTRA Y SE SIENTA)
   ========================================================================== */

socket.on('jugador_sentado', (data) => { 
    // --- 1. LÓGICA DE BOTONES EN EL LOBBY ---
    const botones = document.querySelectorAll('#seleccion-asiento button');
    botones.forEach(btn => {
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(data.asiento)) {
            
            // Si el nombre es "DISPONIBLE", dejamos el botón libre
            if (data.nombre === "DISPONIBLE") {
                btn.disabled = false; // ¡PUEDES HACER CLIC!
                btn.classList.remove('asiento-ocupado');
                btn.innerText = `Asiento ${data.asiento} (Libre)`;
            } else {
                // Si es un nombre real, lo bloqueamos como siempre
                btn.disabled = true;
                btn.classList.add('asiento-ocupado');
                btn.innerText = `Ocupado por ${data.nombre}`;
            }
        }
    });

    // LÓGICA DE DIBUJO EN MESA
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


// --- LIBERAR ASIENTO CUANDO ALGUIEN SE VA ---
socket.on('asiento_liberado', (data) => {
    console.log(`Lobby: Liberando el asiento ${data.asiento}`);
    
    const botones = document.querySelectorAll('#seleccion-asiento button');
    botones.forEach(btn => {
        // Buscamos el botón que tiene el número de asiento que se liberó
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(data.asiento)) {
            btn.disabled = false;
            btn.classList.remove('asiento-ocupado');
            btn.innerText = `Asiento ${data.asiento}`;
        }
    });

    // También limpiamos visualmente el lugar del rival en la mesa
    const numeroPos = obtenerPosicionVisual(data.asiento);
    const contenedorEnMesa = document.getElementById(`pos-visual-${numeroPos}`);
    
    if (contenedorEnMesa) {
        contenedorEnMesa.classList.remove('rival-activo');

        // En lugar de innerHTML = '', solo borramos las etiquetas de nombre y fichas del rival
        const nombreEtiqueta = contenedorEnMesa.querySelector('.nombre-rival-etiqueta');
        if (nombreEtiqueta) nombreEtiqueta.remove();
        
        const fichasRivales = contenedorEnMesa.querySelectorAll('.ficha-rival');
        fichasRivales.forEach(f => f.remove());
        
        console.log(`Visual: Se limpió la identidad del asiento ${data.asiento}, pero el tablero permanece.`);
        
    }
});


// --- C. SOLICITAR ACTUALIZACIÓN AL ENTRAR ---
socket.on('connect', () => {
    if (asientoSeleccionado) {
        socket.emit('solicitar_lista_jugadores');
    }
});



/* ==========================================================================
    CONTROL DE LA PARTIDA 
   ========================================================================== */

socket.on('mostrar_boton_inicio', () => {
    const btn = document.getElementById('btn-iniciar');
    const centro = document.getElementById('tablero-central');
    
    // REGLA DE ORO: Solo mostramos el botón si el centro está VACÍO
    // Si ya hay una mula ahí (tiene hijos/children), el botón se queda escondido.
    if (btn && centro && centro.children.length === 0) {
        btn.classList.add('visible');
        btn.style.display = 'block'; 
        console.log("Visual: Eres anfitrión y la mesa está limpia. Botón mostrado.");
    } else {
        console.log("Visual: Partida en curso detectada. El botón de inicio se mantiene oculto.");
    }
});


// Usamos una función para el clic
document.getElementById('btn-iniciar').onclick = () => { 
    socket.emit('iniciar_partida'); 
};

socket.on('partida_iniciada', () => { 
    const btn = document.getElementById('btn-iniciar');
    if (btn) {
        btn.classList.remove('visible');
        console.log("Partida en marcha. Botón retirado.");
    }
});



/* ==========================================================================
    RECEPCIÓN DE FICHAS 
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
        div.onclick = () => establecerFichaSeleccionada(ficha.lado1, ficha.lado2, div);

        contenedor.appendChild(div);
    });
});

/* ==========================================================================
    RESALTAR FICHA
   ========================================================================== */
   
function resaltarFichaEnInterfaz(elemento) {
    // 1. Quitamos el brillo a todas las fichas de mi mano
    document.querySelectorAll('.ficha-domino').forEach(f => {
        f.classList.remove('ficha-seleccionada');
    });

    // 2. Se lo ponemos solo a la que tocamos
    if (elemento) {
        elemento.classList.add('ficha-seleccionada');
    }
}

/* ==========================================================================
    ACTUALIZAR MANO RIVALES
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

/* ==========================================================================
    CONTROL DE TURNOS Y MENSAJES
   ========================================================================== */

socket.on('turno_actual', (data) => {
    // 1. Ponemos el anuncio en la consola para saber que llegó
    console.log("Anuncio de turno:", data.mensaje);

    if (data.valor_mula !== null) {
        renderizarMulaInicial(data.valor_mula);
    }

    // 2. Buscamos o creamos un letrero en la pantalla para avisar a todos
    let letreroTurno = document.getElementById('anuncio-turno');
    
    if (!letreroTurno) {
        letreroTurno = document.createElement('div');
        letreroTurno.id = 'anuncio-turno';
        letreroTurno.className = 'alerta-turno'; // Luego le damos estilo en CSS
        document.body.appendChild(letreroTurno);
    }

    letreroTurno.innerText = data.mensaje;

    // 3. Si el turno es MÍO, resaltamos mi zona de fichas
    if (String(data.asiento) === String(asientoSeleccionado)) {
        document.getElementById('mi-mano').classList.add('mi-turno-activo');
        alert("¡Es tu turno! Tienes la mula de " + data.valor_mula + " para abrir la estación.");
    } else {
        document.getElementById('mi-mano').classList.remove('mi-turno-activo');
    }
});

// MULA MAYOR INICIA PARTIDA


function renderizarMulaInicial(valor) {
    // 1. Antes que nada, si existe el botón de inicio, lo borramos físicamente
    const btn = document.getElementById('btn-iniciar');
    if (btn) {
        btn.remove(); // Lo eliminamos por completo del documento
    }
    const centro = document.getElementById('tablero-central');
    
    // Solo ponemos la mula si el centro está vacío
    if (centro.children.length > 0) {
        console.log("Visual: La estación ya tiene su mula, no hace falta limpiar.");
        return; 
    }

    // Creamos el elemento de la ficha
    const fichaDiv = document.createElement('div');
    fichaDiv.className = 'ficha-domino mula-central'; 
    
    // Le ponemos los números (como es mula, ambos lados son iguales)
    fichaDiv.innerHTML = `
        <div class="numero numero-${valor}">${valor}</div>
        <div class="divisor"></div>
        <div class="numero numero-${valor}">${valor}</div>
    `;

    // La metemos al centro de la estación
    centro.appendChild(fichaDiv);
    console.log("Visual: Mula de " + valor + " colocada en la estación.");
}


socket.on('anuncio_global', (data) => {
    const btn = document.getElementById('btn-iniciar');
    if (btn) btn.style.display = 'none';

    // 1. Colocamos la mula físicamente en la mesa
    renderizarMulaInicial(data.valor_mula);

    // 2. Creamos el elemento del letrero
    const banner = document.createElement('div');
    banner.className = 'banner-inicio-partida'; // La "clase" es la que manda
    banner.innerHTML = `<h3>🌟 ${data.mensaje} 🌟</h3>`;
    
    // Lo pegamos al body para que no empuje la mesa
    document.body.appendChild(banner);

    // 3. Animación de salida y limpieza
    setTimeout(() => { 
        banner.classList.add('desvanecer'); // Solo añadimos una clase de CSS
        setTimeout(() => banner.remove(), 1000); 
    }, 7000); 
});


// Entrada y salida de jugadores 
// Cambio del anfitrion ausente

socket.on('jugador_ausente', (data) => {
    const numeroPos = obtenerPosicionVisual(data.asiento);
    const contenedor = document.getElementById(`pos-visual-${numeroPos}`);
    
    if (contenedor) {
        // En lugar de borrar, le ponemos una apariencia de "fantasma"
        contenedor.style.opacity = "0.5"; 
        const etiqueta = contenedor.querySelector('.nombre-rival-etiqueta');
        if (etiqueta) {
            etiqueta.innerText += " (AUSENTE)";
        }
        console.log(`Visual: El jugador del asiento ${data.asiento} está ausente, fichas preservadas.`);
    }
});

// 1. Para cambiar el nombre en la etiqueta
socket.on('jugador_salio_y_dejo_fichas', (data) => {
    const numeroPos = obtenerPosicionVisual(data.asiento);
    const etiqueta = document.querySelector(`#pos-visual-${numeroPos} .nombre-rival-etiqueta`);
    if (etiqueta) {
        etiqueta.innerText = data.nuevo_nombre;
        etiqueta.style.color = "#ffcc00"; // Un color llamativo para que alguien se anime a entrar
    }
});

// 2. Para recibir la "corona" de anfitrión
socket.on('eres_nuevo_anfitrion', () => {
    console.log("¡Ahora tú tienes el mando de la mesa!");
    // Aquí podrías mostrar de nuevo el botón de inicio si la partida no ha empezado
    const btn = document.getElementById('btn-iniciar');
    if (btn && document.getElementById('tablero-central').children.length === 0) {
        btn.style.display = 'block';
        btn.classList.add('visible');
    }
});

socket.on('error_jugada', (data) => {
    alert(data.mensaje); // O un aviso flotante más elegante como los que ya tenemos
});