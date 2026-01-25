# app.py 
# Director de orquesta


# --- I M P O R T A C I O N E S
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logic_domino import JuegoDominio
from scoring import calcular_puntos_mano


#  --- C O N F I G U R A C I O N  I N I C I A L

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dominov_2026_veracruz'
socketio = SocketIO(app)

# Creamos una instancia única del juego
juego = JuegoDominio()
jugadores_en_mesa = {}

@app.route('/')
def index():
    # Esta ruta servirá para que tus primos entren a la mesa
    return render_template('index.html')


# --- E V E N T O S    D E L  S E R V I D O R
@socketio.on('connect')
def handle_connect():
    # Enviamos a quien se acaba de conectar la lista de quién ya está sentado
    for asiento, info in jugadores_en_mesa.items():
        emit('jugador_sentado', {
            'nombre': info['nombre'], 
            'asiento': asiento
        })

@socketio.on('unirse_juego')
def handle_unirse(data):
    nombre = data.get('nombre')
    asiento = data.get('asiento')

    jugadores_en_mesa[asiento] = {'nombre': nombre, 'sid': request.sid}
   
    print(f"DEBUG: Jugadores actuales: {len(jugadores_en_mesa)}")

    # Avisamos a todos los demás quién se sentó
    emit('jugador_sentado', {'nombre': nombre, 'asiento': asiento}, broadcast=True)

    # Si hay al menos 2 personas, mostramos el botón de iniciar a todos
    if len(jugadores_en_mesa) >= 2:
        print("DEBUG: ¡Mesa lista! Enviando botón de inicio.")
        emit('mostrar_boton_inicio', broadcast=True)


@socketio.on('solicitar_lista_jugadores')
def handle_lista():
    # Enviamos solo a quien lo pidió (request.sid) la lista de todos
    for asiento, info in jugadores_en_mesa.items():
        emit('jugador_sentado', {
            'nombre': info['nombre'], 
            'asiento': asiento
        })


@socketio.on('iniciar_partida')
def handle_iniciar():
    juego.barajar()
    
    # 1. Obtenemos la lista de asientos ocupados actualmente
    asientos_reales = list(jugadores_en_mesa.keys())
    
    # 2. Usamos la nueva lógica de repartir que acepta la lista de asientos

    manos = juego.repartir(asientos_reales) 
    
    # 3. Reparto de fichas individual (Susurro)
    for asiento in asientos_reales:
        info = jugadores_en_mesa[asiento]
        mano_jugador = manos[asiento]
        info['mano'] = mano_jugador 
        
        # Enviamos las fichas directo a la habitación del jugador (sid)
        emit('recibir_fichas', {'mano': mano_jugador}, room=info['sid'])
    
    # 4. Anuncio General: ¡Esto mata el botón rojo!
    emit('partida_iniciada', broadcast=True)

    # 5. Actualizar visual de fichas ocultas para los rivales
    for asiento in asientos_reales:
        emit('actualizar_manos_rivales', {
            'asiento': asiento,
            'cantidad': len(jugadores_en_mesa[asiento]['mano'])
        }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)


