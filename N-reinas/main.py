import random
import time

def checar_ataques(t):
    ataques = 0
    sz = len(t)
    for i in range(sz):
        for j in range(i + 1, sz):
            if t[i] == t[j] or abs(t[i] - t[j]) == abs(i - j):
                ataques += 1
    return ataques

def saca_vecinos(t):
    vecinos = []
    n = len(t)
    for c in range(n):
        actual_f = t[c]
        for f in range(n):
            if f != actual_f:
                v = list(t)
                v[c] = f
                vecinos.append((v, (c, f)))
    return vecinos

def resolver_tabu(max_it=1000, tam_t=7):
    actual = [random.randint(0, 7) for _ in range(8)]
    mejor = list(actual)
    tabu = []
    movs = 0
    
    t_ini = time.time()
    
    for _ in range(max_it):
        if checar_ataques(actual) == 0:
            break
            
        lista_vec = saca_vecinos(actual)
        best_v = None
        best_mov = None
        min_atq = float('inf')
        
        for v, mov in lista_vec:
            atq_v = checar_ataques(v)
            if mov not in tabu:
                if atq_v < min_atq:
                    min_atq = atq_v
                    best_v = v
                    best_mov = mov
                    
        if best_v is None:
            best_v, best_mov = lista_vec[0]
            
        actual = best_v
        movs += 1
        
        tabu.append(best_mov)
        if len(tabu) > tam_t:
            tabu.pop(0)
            
        if checar_ataques(actual) < checar_ataques(mejor):
            mejor = list(actual)
            
    t_fin = time.time()
    return mejor, checar_ataques(mejor), movs, (t_fin - t_ini)

if __name__ == "__main__":
    print("Corriendo busqueda tabu para 8 reinas...")
    sol, conf, movs, tiempo = resolver_tabu()
    
    print("\nResultados:")
    print("Solucion:", sol)
    print("Conflictos:", conf)
    print("Movimientos:", movs)
    print(f"Tiempo: {tiempo:.6f} s")
    
    print("\nTablero:")
    for r in range(8):
        linea = ""
        for c in range(8):
            if sol[c] == r:
                linea += " Q "
            else:
                linea += " . "
        print(linea)
