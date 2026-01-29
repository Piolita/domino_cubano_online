# El Árbitro y el Matemático, Libro de recetas reglas.
# logic_domino.py

# Generación del Set: Crear las 91 fichas del 0 al 12
# No sabe de internet, botones, ni quien esta sentado, solo el manual,  
# Sabe cuántas fichas tiene un dominó cubano ($55$ fichas).
# Sabe cómo barajar para que sea justo.Sabe quién tiene la mula más alta para empezar.
# La Sopa (Barajeo): Revuelve las fichas de forma aleatoria.
# Reparto Legal: Entregar la cantidad correcta de fichas según el número de personas sentadas.
# Validación de Jugadas (Próximamente): Decir "Sí" o "No" cuando alguien intente poner una ficha. 
# Por ejemplo, si hay un 5 en la mesa, solo permite un 5.
# Estado de la Mesa: Saber qué números están en los extremos (punta izquierda y punta derecha).



import random

class JuegoDominio:

    # Crear las 91 fichas del 0 al 12.
    def __init__(self):
        self.fichas = self._crear_set_doble_12()
        self.pozo = []
        self.tablero = []  # Para guardar las fichas jugadas en orden
        self.puntas = [None, None]

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
        for valor_mula in range(12, -1, -1):
            for asiento, fichas in manos.items():
                for i, ficha in enumerate(fichas):
                    if ficha['lado1'] == valor_mula and ficha['lado2'] == valor_mula:
                        # 1. Quitamos la ficha de la mano del jugador
                        fichas.pop(i) 
                        
                        # 2. Guardamos en la memoria qué mula inició
                        self.mula_inicial = valor_mula
                        
                        # 3. ¡IMPORTANTE! Establecemos las primeras puntas
                        # Como es la primera ficha, ambos lados son iguales
                        self.puntas = [valor_mula, valor_mula]
                        
                        # 4. Metemos la mula al registro del tablero
                        self.tablero = [(valor_mula, valor_mula)]
                        
                        return asiento, valor_mula
        return None, None
    

    def es_jugada_valida(self, ficha, lado):
        # ficha es una tupla (6, 4)
        # lado es 'izq' o 'der' (0 o 1)
        punta_a_conectar = self.puntas[lado]
        
        # Si la ficha tiene el número de la punta, es válida
        return ficha[0] == punta_a_conectar or ficha[1] == punta_a_conectar