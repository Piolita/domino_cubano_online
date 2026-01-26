# socket_events.py Telefonista: 
# recibir llamadas y pasar mensajes

# Filtro de Entrada: Recibir los datos crudos del usuario (como el clic en la ficha).

# Gestión de Salas: Si después quieres que haya "Mesa 1", "Mesa 2", 
# ella se encarga de que los mensajes lleguen a la mesa correcta.

# Traducción de Acciones: Cuando alguien juega, ella le pregunta a la lógica:
#  "¿Se puede?". Si la lógica dice que sí, ella le avisa a todos con un emit.

# Manejo de Desconexiones: Si a Litza se le va el internet, 
# la Telefonista detecta que se colgó la llamada y avisa a la mesa: "Litza se ha ido".
from flask import request
from flask_socketio import emit
from logic_domino import JuegoDominio


# Creamos una instancia única del juego
juego = JuegoDominio()
jugadores_en_mesa = {}


# --- E V E N T O S    D E L  S E R V I D O R

def register_handlers(socketio):

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


    @socketio.on('jugar_ficha')
    def handle_jugar(data):
        # Aquí la Telefonista le preguntará al Árbitro en el futuro
        print(f"Ficha recibida en servidor: {data['lado1']}-{data['lado2']}")
        emit('ficha_colocada_en_mesa', data, broadcast=True)
