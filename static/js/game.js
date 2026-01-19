// game.js - VERSIÓN AUDITADA Y LIMPIA

var socket = io({
    transports: ['polling', 'websocket']
});

var miNumeroDeJugador = null;

socket.on('connect', function() {
    console.log("¡Conectado al servidor de dominó!");
});

// 1. BIENVENIDA
socket.on('bienvenida', function(data) {
    miNumeroDeJugador = data.num_jugador;
    console.log("Soy el Jugador número: " + miNumeroDeJugador);
    
    var spanMiNum = document.getElementById('mi-num');
    if(spanMiNum) {
        spanMiNum.innerText = miNumeroDeJugador;
    }

    // Dibujar fichas ocultas para rivales
    const rivales = ['fichas-j1', 'fichas-j2', 'fichas-j3'];
    rivales.forEach(idContenedor => {
        const contenedor = document.getElementById(idContenedor);
        if (contenedor) {
            contenedor.innerHTML = ""; 
            for (let i = 0; i < 10; i++) {
                const fichaOculta = document.createElement('div');
                fichaOculta.className = 'ficha-oculta';
                contenedor.appendChild(fichaOculta);
            }
        }
    });
});

// 2. CAMBIO DE TURNO
socket.on('cambio_turno', function(data) {
    // Apagar luces de todos
    document.querySelectorAll('.asiento').forEach(asiento => {
        asiento.classList.remove('asiento-activo', 'activo');
    });

    // Encender luz del actual
    var asientoActual = document.getElementById('asiento-' + data.turno);
    if (asientoActual) {
        asientoActual.classList.add('asiento-activo');
    }

    var mensajeEstado = document.getElementById('mensaje-estado');
    var btnPaso = document.getElementById('btn-paso');
    
    if (mensajeEstado) {
        if (data.turno === miNumeroDeJugador) {
            mensajeEstado.innerHTML = "⭐ <span style='color: #FFD700;'>¡ES TU TURNO!</span> ⭐";
        } else {
            mensajeEstado.innerText = "Esperando al Jugador " + data.turno + "...";
        }
    }

    if (btnPaso) {
        btnPaso.style.display = (data.turno === miNumeroDeJugador) ? "inline-block" : "none";
        btnPaso.onclick = function() { socket.emit('pasar_turno'); };
    }
});

// 3. RECIBIR FICHAS (Tu código original con protección)
socket.on('recibir_fichas', function(data) {
    console.log("Fichas recibidas:", data.fichas);
    var contenedor = document.getElementById('mis-fichas');
    
    if (contenedor) {
        contenedor.innerHTML = ""; 
        data.fichas.forEach(function(ficha) {
            var divFicha = document.createElement('div');
            divFicha.className = 'ficha';
            divFicha.appendChild(crearCaraFicha(ficha[0]));
            divFicha.appendChild(crearCaraFicha(ficha[1]));

            divFicha.onclick = function() {
                this.style.opacity = "0.3"; 
                this.style.pointerEvents = "none"; 
                jugarFicha(ficha, this); 
            };
            contenedor.appendChild(divFicha);
        });
    }
});

function jugarFicha(ficha, elementoFicha) {
    socket.emit('jugar_ficha', {ficha: ficha});
    elementoFicha.id = "ficha-intentando-" + ficha[0] + "-" + ficha[1];
}

// 4. ACTUALIZAR TABLERO
socket.on('actualizar_tablero', function(data) {
    var idBusqueda = "ficha-intentando-" + data.ficha[0] + "-" + data.ficha[1];
    var miFichaEnMano = document.getElementById(idBusqueda);
    
    if (miFichaEnMano) miFichaEnMano.remove();

    var mesa = document.getElementById('mesa'); // Cambiado a 'mesa' que es tu ID real
    if (mesa) {
        var nuevaFicha = crearFichaParaTablero(data.ficha, data.invertir);
        if (data.indice_punta === 0) {
            mesa.prepend(nuevaFicha);
        } else {
            mesa.appendChild(nuevaFicha);
        }
    }
});

socket.on('error_jugada', function(data) {
    alert(data.mensaje);
    var fichaError = document.getElementById("ficha-intentando-" + data.ficha[0] + "-" + data.ficha[1]);
    if (fichaError) {
        fichaError.style.opacity = "1"; 
        fichaError.style.pointerEvents = "auto"; 
        fichaError.id = ""; 
    }
});

