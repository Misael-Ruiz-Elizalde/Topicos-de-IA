import random
import math

class InstanciaCuliacan:
    def __init__(self):
        # CEDIS ubicado en la salida norte y 8 sucursales representativas en Culiacán
        self.nombres_nodos = [
            "CEDIS Culiacán", "Sucursal Tres Ríos", "Sucursal Centro", 
            "Sucursal Isla Musala", "Sucursal Las Quintas", "Sucursal Humaya", 
            "Sucursal Zapata", "Sucursal Alameda", "Sucursal Sanalona"
        ]
        # Coordenadas geográficas simuladas proyectadas en plano cartesiano (latitud, longitud)
        self.coordenadas = [
            (24.8500, -107.3900), (24.8150, -107.4000), (24.8100, -107.3880),
            (24.8050, -107.3750), (24.8200, -107.3700), (24.8350, -107.4100),
            (24.7900, -107.3950), (24.8250, -107.3800), (24.8000, -107.3500)
        ]
        # Demandas en kilogramos de comestibles
        self.demandas = [0, 250, 300, 180, 220, 310, 270, 190, 240]
        self.capacidad_vehiculo = 1000
        self.n = len(self.demandas)
        self.matriz_distancias = self.calcular_matriz()

    def calcular_matriz(self):
        matriz = [[0.0]*self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    x1, y1 = self.coordenadas[i]
                    x2, y2 = self.coordenadas[j]
                    matriz[i][j] = math.sqrt((x1 - x2)**2 + (y1 - y2)**2) * 111.0
        return matriz

class SolucionadorTabu:
    def __init__(self, instancia, max_iter=300, tabu_tenure=10):
        self.inst = instancia
        self.max_iter = max_iter
        self.tabu_tenure = tabu_tenure

    def evaluar_ruta(self, ruta):
        costo_total = 0.0
        carga_actual = 0
        rutas_completas = []
        ruta_actual = []

        for nodo in ruta:
            carga_actual += self.inst.demandas[nodo]
            if carga_actual > self.inst.capacidad_vehiculo:
                ruta_actual.insert(0, 0)
                ruta_actual.append(0)
                rutas_completas.append(ruta_actual)
                carga_actual = self.inst.demandas[nodo]
                ruta_actual = [nodo]
            else:
                ruta_actual.append(nodo)
        
        if ruta_actual:
            ruta_actual.insert(0, 0)
            ruta_actual.append(0)
            rutas_completas.append(ruta_actual)

        for r in rutas_completas:
            for i in range(len(r) - 1):
                costo_total += self.inst.matriz_distancias[r[i]][r[i+1]]
        
        return costo_total, rutas_completas

    def resolver(self):
        clientes = list(range(1, self.inst.n))
        random.seed(42)
        random.shuffle(clientes)
        
        mejor_solucion = list(clientes)
        mejor_costo, _ = self.evaluar_ruta(mejor_solucion)
        
        solucion_actual = list(mejor_solucion)
        costo_actual = mejor_costo
        lista_tabu = {}

        for it in range(self.max_iter):
            mejor_vecino = None
            mejor_costo_vecino = float('inf')
            movimiento_realizado = None

            for i in range(len(clientes)):
                for j in range(i + 1, len(clientes)):
                    vecino = list(solucion_actual)
                    vecino[i], vecino[j] = vecino[j], vecino[i]
                    
                    costo_v, _ = self.evaluar_ruta(vecino)
                    movimiento = (vecino[i], vecino[j])
                    es_tabu = movimiento in lista_tabu and lista_tabu[movimiento] > it

                    if (es_tabu and costo_v < mejor_costo) or (not es_tabu and costo_v < mejor_costo_vecino):
                        mejor_vecino = vecino
                        mejor_costo_vecino = costo_v
                        movimiento_realizado = movimiento

            if mejor_vecino is None:
                break

            solucion_actual = mejor_vecino
            costo_actual = mejor_costo_vecino
            
            if movimiento_realizado:
                lista_tabu[movimiento_realizado] = it + self.tabu_tenure

            if costo_actual < mejor_costo:
                mejor_solucion = list(solucion_actual)
                mejor_costo = costo_actual

        _, rutas_optimizadas = self.evaluar_ruta(mejor_solucion)
        return mejor_costo, rutas_optimizadas

if __name__ == "__main__":
    instancia = InstanciaCuliacan()
    solver = SolucionadorTabu(instancia, max_iter=200, tabu_tenure=8)
    costo_optimo, rutas = solver.resolver()
    
    print("==================================================")
    print("=== RESULTADOS DE OPTIMIZACIÓN TABÚ (CULIACÁN) ===")
    print("==================================================")
    print(f"Distancia Total Mínima Encontrada: {costo_optimo:.2f} km\n")
    print("Rutas de Distribución Asignadas por Vehículo:")
    for idx, r in enumerate(rutas):
        nombres = [instancia.nombres_nodos[n] for n in r]
        print(f"  [Vehículo {idx+1}] {' -> '.join(nombres)}")
    print("==================================================")
