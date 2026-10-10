import random
import time

def evaluar_tablero(tablero):
    """Calcula el número de pares de reinas que se atacan entre sí (conflictos)."""
    conflictos = 0
    n = len(tablero)
    for i in range(n):
        for j in range(i + 1, n):
            # Misma fila
            if tablero[i] == tablero[j]:
                conflictos += 1
            # Misma diagonal
            elif abs(tablero[i] - tablero[j]) == abs(i - j):
                conflictos += 1
    return conflictos

def obtener_vecinos(tablero):
    """Genera todos los vecinos posibles moviendo una reina a otra fila en su columna."""
    vecinos = []
    n = len(tablero)
    for col in range(n):
        fila_original = tablero[col]
        for fila in range(n):
            if fila != fila_original:
                vecino = list(tablero)
                vecino[col] = fila
                # Guardamos el movimiento como (columna, nueva_fila)
                vecinos.append((vecino, (col, fila)))
    return vecinos

def busqueda_tabu_8_reinas(max_iteraciones=1000, tam_tabu=7):
    # 1. Estado inicial aleatorio (regla 1)
    estado_actual = [random.randint(0, 7) for _ in range(8)]
    mejor_estado = list(estado_actual)
    
    lista_tabu = []  # Almacenará movimientos recientes
    movimientos = 0
    
    tiempo_inicio = time.time()
    
    for _ in range(max_iteraciones):
        conflictos_actuales = evaluar_tablero(estado_actual)
        
        # Si encontramos la solución perfecta (0 conflictos), terminamos
        if conflictos_actuales == 0:
            break
            
        vecinos_movimientos = obtener_vecinos(estado_actual)
        mejor_vecino = None
        mejor_movimiento = None
        min_conflictos = float('inf')
        
        # Buscar el mejor vecino que no esté en la lista tabú
        for vecino, movimiento in vecinos_movimientos:
            conflictos_vecino = evaluar_tablero(vecino)
            
            # Criterio: que mejore o sea el mejor disponible y no esté prohibido (tabú)
            if movimiento not in lista_tabu oracion_aspiracion_simulada: # (o simplemente verificar tabú)
                if conflictos_vecino < min_conflictos:
                    min_conflictos = conflictos_vecino
                    mejor_vecino = vecino
                    mejor_movimiento = movimiento
                    
        # Si todos los mejores vecinos están en tabú, tomamos el primero por flexibilidad
        if mejor_vecino is None:
            mejor_vecino, mejor_movimiento = vecinos_movimientos[0]
            
        # Actualizar estado actual
        estado_actual = mejor_vecino
        movimientos += 1
        
        # Actualizar lista tabú (FIFO)
        lista_tabu.append(mejor_movimiento)
        if len(lista_tabu) > tam_tabu:
            lista_tabu.pop(0)
            
        # Guardar el mejor histórico
        if evaluar_tablero(estado_actual) < evaluar_tablero(mejor_estado):
            mejor_estado = list(estado_actual)
            
    tiempo_fin = time.time()
    tiempo_total = tiempo_fin - tiempo_inicio
    
    return mejor_estado, evaluar_tablero(mejor_estado), movimientos, tiempo_total

# --- Ejecución de prueba ---
if __name__ == "__main__":
    print("Ejecutando Búsqueda Tabú para el problema de las 8 Reinas...")
    solucion, conflictos, movimientos, tiempo = busqueda_tabu_8_reinas()
    
    print("\n--- RESULTADOS ---")
    print(f"Estado solución (Columnas 0-7, Valores Filas 0-7): {solucion}")
    print(f"Conflictos restantes: {conflictos}")
    print(f"Cantidad de movimientos realizados: {movimientos}")
    print(f"Tiempo de ejecución: {tiempo:.6f} segundos")
    
    # Representación visual sencilla del tablero
    print("\nTablero visual (Q = Reina, . = Espacio vacío):")
    for r in range(8):
        fila_str = ""
        for c in range(8):
            if solucion[c] == r:
                fila_str += " Q "
            else:
                fila_str += " . "
        print(fila_str)
