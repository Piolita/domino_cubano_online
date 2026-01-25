# El Árbitro y el Matemático
# logic_domino.py



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
        # Añadimos un ID único para que el JS no se confunda
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
    
    # La Sopa (Barajeo)
    def barajar(self):
        random.shuffle(self.fichas)
        self.pozo = self.fichas[:]
        self.tablero = [] # Limpiamos mesa al barajar

    # Reparto Legal
    def repartir(self, lista_asientos):
        """
        Ahora recibe la lista de asientos reales (ej: [1, 2, 5])
        para entregar las fichas a los IDs correctos.
        """
        num_jugadores = len(lista_asientos)
        fichas_por_persona = 12 if num_jugadores >= 5 else 15
        
        manos = {}
        for asiento in lista_asientos:
            mano_jugador = []
            for _ in range(fichas_por_persona):
                if self.pozo:
                    mano_jugador.append(self.pozo.pop())
            manos[asiento] = mano_jugador
        
        return manos