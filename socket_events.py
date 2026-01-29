# socket_events.py Servidor Telefonista, capitan de meseros
# : encargado de la comunicación, Su lema es: "Yo me encargo de que todos se enteren de lo que está pasando".,
# Le pregunta a logic_domino.py: "Oye, según tus reglas, ¿qué fichas le tocan a este jugador?". .
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
anfitrion_sid = None
sesiones_jugadores = {}

# --- E V E N T O S    D E L   S E R V I D O R


# ==========================================================================
#   SECCIÓN DE ADMINISTRACIÓN (Poderes del Anfitrión)
# ==========================================================================

def es_anfitrion(sid):
    return sid == anfitrion_sid

# Aquí añadiremos las funciones de expulsión y reinicio más adelante

# ==========================================================================
#   SECCIÓN DE REGISTRO
# ==========================================================================

def register_handlers(socketio):

    @socketio.on('connect')
    def handle_connect():
        for asiento, info in jugadores_en_mesa.items():
            emit('jugador_sentado', {
                'nombre': info['nombre'], 
                'asiento': asiento
            })


    @socketio.on('unirse_juego')
    def handle_unirse(data):
        global anfitrion_sid
        nombre = data.get('nombre')
        asiento = data.get('asiento')
        sid_actual = request.sid

        # Si el asiento existe pero el dueño es "DISPONIBLE", 
        # permitimos que el nuevo jugador tome el control.
        if asiento in jugadores_en_mesa and jugadores_en_mesa[asiento]['nombre'] == "DISPONIBLE":
            print(f"DEBUG: {nombre} está tomando el lugar disponible en el asiento {asiento}")
            jugadores_en_mesa[asiento]['nombre'] = nombre
            jugadores_en_mesa[asiento]['sid'] = sid_actual
            
            # Si era el jefe, le devolvemos el botón
            if sesiones_jugadores.get(nombre) == anfitrion_sid:
                anfitrion_sid = sid_actual
        
        else:
            # 2. ¿Es un jugador nuevo o un sustituto?
            print(f"DEBUG: Nuevo registro en asiento {asiento}: {nombre}")
            jugadores_en_mesa[asiento] = {'nombre': nombre, 'sid': sid_actual}
            sesiones_jugadores[nombre] = sid_actual
            
            # Si la mesa estaba vacía, este es el primer jefe
            if anfitrion_sid is None:
                anfitrion_sid = sid_actual

        # 3. Avisamos a todos que el asiento está ocupado
        emit('jugador_sentado', {'nombre': nombre, 'asiento': asiento}, broadcast=True)

        # 4. EL PAQUETE DE RESCATE (Para que no vea la pantalla vacía)
        # Si ese asiento ya tiene fichas repartidas, se las mandamos de una vez
        if 'mano' in jugadores_en_mesa[asiento]:
            emit('recibir_fichas', {'mano': jugadores_en_mesa[asiento]['mano']}, room=sid_actual)
            
            # Le avisamos que la partida ya inició para que esconda el botón de inicio
            emit('partida_iniciada', room=sid_actual)
            
            # Le mandamos la mula que está en el centro (si existe)
            if hasattr(juego, 'mula_inicial'):
                emit('anuncio_global', {
                    'mensaje': "Te has unido a la partida en curso",
                    'valor_mula': juego.mula_inicial
                }, room=sid_actual)

        # 5. Si no han empezado y hay 2 o más, mostramos el botón al anfitrión
        if len(jugadores_en_mesa) >= 2 and not hasattr(juego, 'mula_inicial'):
            emit('mostrar_boton_inicio', room=anfitrion_sid)
            

        # --- B. LÓGICA PARA JUGADOR NUEVO  ---
        # PRIMERO: Registramos al jugador en el sistema
        jugadores_en_mesa[asiento] = {'nombre': nombre, 'sid': sid_actual}
        sesiones_jugadores[nombre] = sid_actual

        # SEGUNDO: Si es el primero, es el jefe
        if anfitrion_sid is None:
            anfitrion_sid = sid_actual
            print(f"DEBUG: {nombre} es el anfitrión.")

        # TERCERO: Avisamos a todos de la nueva entrada
        emit('jugador_sentado', {'nombre': nombre, 'asiento': asiento}, broadcast=True)

        # CUARTO: Si hay mesa lista, mostramos botón al jefe
        if len(jugadores_en_mesa) >= 2:
            emit('mostrar_boton_inicio', room=anfitrion_sid)


        
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
        # Seguridad: Solo el anfitrión 
        if request.sid != anfitrion_sid:
            print("Intento de inicio no autorizado.")
            return
        juego.barajar()
        
        # Obtenemos la lista de asientos ocupados actualmente
        asientos_reales = list(jugadores_en_mesa.keys())
        
        #  Usamos la lógica de repartir que acepta la lista de asientos
        manos = juego.repartir(asientos_reales) 
        
        #  Reparto de fichas individual 
        for asiento in asientos_reales:
            info = jugadores_en_mesa[asiento]
            mano_jugador = manos[asiento]
            info['mano'] = mano_jugador 
            
            # Enviamos las fichas directo a la habitación del jugador (sid)
            emit('recibir_fichas', {'mano': mano_jugador}, room=info['sid'])
        
        # 4. Anuncio General
        emit('partida_iniciada', broadcast=True)

        # 5. Actualizar fichas ocultas para los rivales
        for asiento in asientos_reales:
            emit('actualizar_manos_rivales', {
                'asiento': asiento,
                'cantidad': len(jugadores_en_mesa[asiento]['mano'])
            }, broadcast=True)

        # 6. IDENTIFICAR EL TURNO INICIAL 
        asiento_inicial, valor_mula = juego.encontrar_mula_inicio(manos)

        if asiento_inicial:
            # (Esto hará que la mula desaparezca de la mano del que la tenía)
            for asiento, fichas in manos.items():
                sid_jugador = jugadores_en_mesa[asiento]['sid']
                emit('recibir_fichas', {'mano': fichas}, room=sid_jugador)

            #  EL ANUNCIO BONITO: Un mensaje para todos los jugadores
            nombre_valiente = jugadores_en_mesa[asiento_inicial]['nombre']
            mensaje_global = f"¡Atención! {nombre_valiente} abre la estación con la mula de {valor_mula}."
            
            # Enviamos a todos (broadcast)
            emit('anuncio_global', {
                'mensaje': mensaje_global,
                'valor_mula': valor_mula,
                'asiento_inicial': asiento_inicial
            }, broadcast=True)
                
            
            
    @socketio.on('jugar_ficha')
    def handle_jugar(data):
        # data trae: {'lado1': 6, 'lado2': 4, 'lado_mesa': 'izq'}
        ficha = (data['lado1'], data['lado2'])
        lado_mesa = 0 if data['lado_mesa'] == 'izq' else 1
        
        if juego.es_jugada_valida(ficha, lado_mesa):
            # Si es válida, el Chef actualiza las puntas
            # (Aquí pondremos luego la lógica de girar la ficha si es necesario)
            print(f"JUGADA LEGAL: {ficha}")
            emit('ficha_colocada_en_mesa', data, broadcast=True)
        else:
            # Si es ilegal, le avisamos solo al que se equivocó
            print(f"¡JUGADA ILEGAL! {ficha} no entra en la punta {juego.puntas[lado_mesa]}")
            emit('error_jugada', {'mensaje': "Esa ficha no entra ahí, pícara."}, room=request.sid)


    @socketio.on('disconnect')
    def handle_disconnect():
        global anfitrion_sid
        sid_que_se_fue = request.sid
        asiento_a_liberar = None
        nombre_jugador = ""

        # Buscamos quién se fue
        for asiento, info in jugadores_en_mesa.items():
            if info['sid'] == sid_que_se_fue:
                asiento_a_liberar = asiento
                nombre_jugador = info['nombre']
                break

        if asiento_a_liberar:
            print(f"DEBUG: {nombre_jugador} ha dejado la mesa.")
            
            # 1. CAMBIO DE NOMBRE: El asiento ahora está "DISPONIBLE"
            # Mantenemos las fichas ('mano'), pero cambiamos el nombre para que otro entre
            jugadores_en_mesa[asiento_a_liberar]['nombre'] = "DISPONIBLE"
            jugadores_en_mesa[asiento_a_liberar]['sid'] = None  # Nadie lo controla ahora
            
            # Avisamos a todos los comedores que el asiento cambió de dueño
            emit('jugador_salio_y_dejo_fichas', {
                'asiento': asiento_a_liberar,
                'nuevo_nombre': "DISPONIBLE"
            }, broadcast=True)

            # 2. TRASPASO DE PODER: Si el que se fue era el jefe...
            if sid_que_se_fue == anfitrion_sid:
                anfitrion_sid = None # Quitamos el mando al que se fue
                # Buscamos a alguien más que esté conectado (que tenga un SID válido)
                for asiento_id, datos in jugadores_en_mesa.items():
                    if datos['sid'] is not None:
                        anfitrion_sid = datos['sid']
                        print(f"DEBUG: El mando pasa a {datos['nombre']}")
                        emit('eres_nuevo_anfitrion', room=anfitrion_sid)
                        break