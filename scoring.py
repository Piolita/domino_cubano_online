# scoring.py Juez de cuentas

def calcular_puntos_mano(mano):
    """
    Suma el valor total de las fichas que un jugador tiene en la mano.
    Cada ficha es un diccionario como {'lado1': 12, 'lado2': 5}
    """
    total = 0
    for ficha in mano:
        total += ficha['lado1'] + ficha['lado2']
    return total

def obtener_ganador_ronda(jugadores_con_puntos):
    """
    Recibe un diccionario {nombre: puntos} y devuelve al que tiene menos.
    """
    if not jugadores_con_puntos:
        return None
    
    # El ganador de la ronda es quien acumuló MENOS puntos
    ganador = min(jugadores_con_puntos, key=jugadores_con_puntos.get)
    return ganador, jugadores_con_puntos[ganador]