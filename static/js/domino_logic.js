


// Variables 
let miAsiento = null;
let miNombre = "";
let fichaSeleccionada = null; // Guardará el objeto ficha {lado1, lado2}

function establecerFichaSeleccionada(l1, l2, elemento) {
    // Guardamos los datos técnicos
    fichaSeleccionada = {
        lado1: parseInt(l1),
        lado2: parseInt(l2),
        id: elemento.id
    };
    
    // Le pedimos a la UI que brille
    resaltarFichaEnInterfaz(elemento);
    
    console.log("Lógica: Tenemos lista la ficha " + l1 + "-" + l2);
}

function obtenerFichaSeleccionada() {
    return fichaSeleccionada;
}

function limpiarSeleccion() {
    fichaSeleccionada = null;
}

