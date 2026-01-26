import os

class Config:
    # Clave para que los mensajes de Socket sean seguros
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dominov_2026_veracruz_super_secreta'
    
    # Ajustes del Juego
    FICHAS_POR_JUGADOR_4 = 15
    FICHAS_POR_JUGADOR_5 = 12
    DOBLE_MAXIMO = 12  # Por si luego quieres jugar de doble 9
    
    # Servidor
    DEBUG = True
    PORT = 5000