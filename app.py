# app.py

import random
import flask
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'domino_secreto_veracruz'

# Configuración estable de SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- DEFINICIÓN DE FUNCIONES 

def crear_mazo_cubano():
    mazo = []
    # Dominó de 55 fichas (del 0 al 9)
    for i in range(10):
        for j in range(i, 10):
            mazo.append([i, j])
    random.shuffle(mazo)
    return mazo

# --- ESTADO GLOBAL DEL JUEGO 

mazo_maestro = crear_mazo_cubano() 
jugadores = []
fichas_en_mesa = []
extremos = []
turno_actual = 0

# --- RUTAS DE NAVEGACIÓN 

@app.route('/')
def index():
    return render_template('index.html')


# --- C O N E X I O N
@socketio.on('connect')
def handle_connect():
    global mazo_maestro, jugadores, turno_actual
    sid = flask.request.sid
    
    if sid not in jugadores:
        if len(jugadores) < 4:
            jugadores.append(sid)
            num_jugador = jugadores.index(sid)
            
            # Repartimos 10 fichas del mazo único
            mis_fichas = []
            for _ in range(10):
                if mazo_maestro:
                    mis_fichas.append(mazo_maestro.pop(0))
            
            print(f"--- JUGADOR {num_jugador} CONECTADO ---")
            print(f"Fichas entregadas: {mis_fichas}")
            print(f"Quedan {len(mazo_maestro)} fichas en el mazo total.")
            
            emit('bienvenida', {'num_jugador': num_jugador})
            emit('recibir_fichas', {'fichas': mis_fichas})
        else:
            # Si ya hay 4, entra como espectador
            emit('bienvenida', {'num_jugador': 'espectador'})
    
    # Informamos a todos quién tiene el turno actual
    emit('cambio_turno', {'turno': turno_actual}, broadcast=True)


# ----- J U G A R   F I C H A
@socketio.on('jugar_ficha')
def ficha_jugada(data):
    global extremos, fichas_en_mesa, turno_actual, jugadores
    
    sid_que_cliqueo = flask.request.sid
    
    # --- BLOQUE 1: IDENTIFICACIÓN ---
    try:
        indice_jugador = jugadores.index(sid_que_cliqueo)
    except ValueError:
        return 

    # --- BLOQUE 2: SEGURIDAD (TURNO) ---
    if indice_jugador != turno_actual:
        emit('error_jugada', {
            'mensaje': f'¡No es tu turno! Le toca al Jugador {turno_actual}', 
            'ficha': data['ficha']
        })
        return

    # --- BLOQUE 3: LÓGICA DE CONEXIÓN Y ORIENTACIÓN ---
    ficha = data['ficha']      
    jugada_valida = False
    invertir = False          
    indice_punta = -1

    # 1. SI LA MESA ESTÁ VACÍA
    if not fichas_en_mesa:
        fichas_en_mesa.append(ficha)
        if ficha[0] == ficha[1]:
            # Es mula: abre 4 caminos (arriba, abajo, izq, der)
            extremos = [ficha[0], ficha[0], ficha[0], ficha[0]]
        else:
            # Normal: solo 2 caminos
            extremos = [ficha[0], ficha[1]]
        jugada_valida = True
        indice_punta = 0
    
    # 2. SI YA HAY FICHAS: BUSCAMOS EN TODAS LAS PUNTAS DISPONIBLES
    else:
        for i, valor_punta in enumerate(extremos):
            if ficha[0] == valor_punta:
                extremos[i] = ficha[1] # La punta se actualiza con el otro extremo de la ficha
                invertir = True if i == 0 else False
                indice_punta = i
                jugada_valida = True
                break
            elif ficha[1] == valor_punta:
                extremos[i] = ficha[0] # Se invierte y la punta se actualiza con el primer valor
                invertir = False if i == 0 else True
                indice_punta = i
                jugada_valida = True
                break

        # REGLA ESPECIAL: Si la ficha jugada es una MULA, añade 2 brazos nuevos
        if jugada_valida and ficha[0] == ficha[1]:
            extremos.append(ficha[0])
            extremos.append(ficha[0])

    # 3. RESPUESTA AL CLIENTE (CORREGIDA)
    if jugada_valida:
        p_indice = indice_punta if 'indice_punta' in locals() else 0
        
        # Usamos la variable lado_visual que SÍ calculamos
        lado_visual = 'izq' if p_indice == 0 else 'der'
        
        emit('actualizar_tablero', {
            'ficha': ficha, 
            'invertir': invertir,
            'puntas_activas': extremos,
            'indice_punta': p_indice,
            'lado': lado_visual  # <-- CAMBIO AQUÍ: antes decía 'der'
        }, broadcast=True)
        
        fichas_en_mesa.append(ficha) # Importante: mover esto aquí para no duplicar
        turno_actual = (turno_actual + 1) % len(jugadores)
        emit('cambio_turno', {'turno': turno_actual}, broadcast=True)


        
# ------ P A S A R   T U R N O
@socketio.on('pasar_turno')
def pasar_turno():
    global turno_actual, jugadores
    sid_que_cliqueo = flask.request.sid
    
    if jugadores[turno_actual] == sid_que_cliqueo:
        turno_actual = (turno_actual + 1) % len(jugadores)
        print(f"El jugador {jugadores.index(sid_que_cliqueo)} pasó.")
        emit('cambio_turno', {'turno': turno_actual}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5005)


