
// static/js/domino_ui.js

/**
 * Crea el elemento visual de una ficha para el tablero
 * @param {Array} ficha - Ejemplo: [6, 6]
 * @returns {HTMLElement} - El div de la ficha configurado
 */


// static/js/domino_ui.js

function crearFichaParaTablero(ficha, debeInvertirse) {
    const fichaDiv = document.createElement('div');
    fichaDiv.className = 'ficha-tablero';
    
    // 1. Decidir orientación
    if (ficha[0] === ficha[1]) {
        fichaDiv.classList.add('ficha-vertical'); // Doble (T)
    } else {
        fichaDiv.classList.add('ficha-horizontal'); // Normal (Acostada)
    }

    // 2. Determinar qué valores dibujar
    const valor1 = debeInvertirse ? ficha[1] : ficha[0];
    const valor2 = debeInvertirse ? ficha[0] : ficha[1];

    // --- AQUÍ ESTABA EL ERROR: Cambiamos a crearCaraFicha ---
    fichaDiv.appendChild(crearCaraFicha(valor1));
    fichaDiv.appendChild(crearCaraFicha(valor2));
    
    return fichaDiv;
}

function crearCaraFicha(valor) {
    const contenedor = document.createElement('div');
    contenedor.className = 'cara-puntos';
    const posiciones = {
        0: [], 1: [5], 2: [1, 9], 3: [1, 5, 9], 4: [1, 3, 7, 9],
        5: [1, 3, 5, 7, 9], 6: [1, 3, 4, 6, 7, 9], 7: [1, 3, 4, 5, 6, 7, 9],
        8: [1, 3, 4, 6, 7, 9, 2, 8], 9: [1, 2, 3, 4, 5, 6, 7, 8, 9]
    };
    const puntosActivos = posiciones[valor] || [];
    for (let i = 1; i <= 9; i++) {
        const celda = document.createElement('div');
        if (puntosActivos.includes(i)) {
            const punto = document.createElement('div');
            punto.className = 'punto-negro';
            celda.appendChild(punto);
        }
        contenedor.appendChild(celda);
    }
    return contenedor;
}