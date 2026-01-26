
# app.py (El Director de Orquesta)
# Es el puente. Su único trabajo es escuchar lo que dicen los jugadores 
# y preguntarle al árbitro (logic_domino.py) qué hacer.

# Gestión de Conexiones: Saber quién entra y quién sale de la mesa.

# Comunicación (SocketIO): Recibir los emit del JavaScript y enviar las respuestas a todos.

# Persistencia Temporal: Guardar el diccionario de jugadores_en_mesa para saber qué mano tiene cada sid.


# --- I M P O R T A C I O N E S
from flask import Flask, render_template
from flask_socketio import SocketIO
from socket_events import register_handlers
from config import Config


#  --- C O N F I G U R A C I O N  I N I C I A L

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

register_handlers(socketio)

@app.route('/')
def index():
    # Esta ruta servirá para que tus primos entren a la mesa
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)


