# El Árbitro y el Matemático
# logic_domino.py

# Generación del Set: Crear las 91 fichas del 0 al 12.

# La Sopa (Barajeo): Revolver las fichas de forma aleatoria.

# Reparto Legal: Entregar la cantidad correcta de fichas según el número de personas sentadas.

# Validación de Jugadas (Próximamente): Decir "Sí" o "No" cuando alguien intente poner una ficha. Por ejemplo, si hay un 5 en la mesa, solo permite un 5.

# Estado de la Mesa: Saber qué números están en los extremos (punta izquierda y punta derecha).



import random

class JuegoDominio:

    # Crear las 91 fichas del 0 al 12.
    def __init__(self):
        self.fichas = self._crear_set_doble_12()
        self.pozo = []
        self.tablero = []  # Para guardar las fichas jugadas en orden
        self.extremo_izquierdo = None
        self.extremo_derecho = None

    def _crear_set_doble_12(self):
        set_fichas = []
        contador_id = 0
        for i in range(13):
            for j in range(i, 13):
                set_fichas.append({
                    'id': contador_id,
                    'lado1': i, 
                    'lado2': j,
                    'es_mula': (i == j)
                })
                contador_id += 1
        return set_fichas
    
    # La Sopa 
    def barajar(self):
        random.shuffle(self.fichas)
        self.pozo = self.fichas[:]
        self.tablero = [] 

    # Reparto Legal
    def repartir(self, lista_asientos):
        num_jugadores = len(lista_asientos)

        # Regla de reparto para Doble 12 (91 fichas totales)
        if 2 <= num_jugadores <= 4:
            fichas_por_persona = 15
        elif 5 <= num_jugadores <= 6:
            fichas_por_persona = 12
        elif 7 <= num_jugadores <= 8:
            fichas_por_persona = 11
        else:
            fichas_por_persona = 10
        
        manos = {}
        for asiento in lista_asientos:
            mano_jugador = []
            for _ in range(fichas_por_persona):
                if self.pozo:
                    mano_jugador.append(self.pozo.pop())
            manos[asiento] = mano_jugador
        
        return manos
    

    def encontrar_mula_inicio(self, manos):
        """
        Busca la mula más alta disponible en las manos repartidas,
        empezando desde el 12-12 hacia abajo.
        """
        for valor_mula in range(12, -1, -1): # Del 12 al 0
            for asiento, fichas in manos.items():
                for ficha in fichas:
                    if ficha['lado1'] == valor_mula and ficha['lado2'] == valor_mula:
                        return asiento, valor_mula
        return None, None
    
    