import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CARGA DE DATOS DESDE LOS ARCHIVOS EXCEL
# ==========================================
print("Cargando datos y matrices desde Excel...")
df_nodes = pd.read_excel('datos_distribucion_tiendas.xlsx')
dist_matrix = pd.read_excel('matriz_distancias.xlsx').values
fuel_matrix = pd.read_excel('matriz_costos_combustible.xlsx').values
n_nodes = dist_matrix.shape[0]

demands = df_nodes['Capacidad_Venta'].values 
VEHICLE_CAPACITY = 60000  # Capacidad máxima por vehículo

# ==========================================
# 2. FUNCIONES DE EVALUACIÓN Y CVRP
# ==========================================
def evaluar_ruta_cvrp_costo(ruta, matriz_costos, demandas, cap_max):
    costo_total = 0
    carga_actual = 0
    nodo_actual = 0  
    for next_nodo in ruta:
        carga_actual += demandas[next_nodo]
        if carga_actual > cap_max:
            costo_total += matriz_costos[nodo_actual, 0] + matriz_costos[0, next_nodo]
            carga_actual = demandas[next_nodo]
        else:
            costo_total += matriz_costos[nodo_actual, next_nodo]
        nodo_actual = next_nodo
    costo_total += matriz_costos[nodo_actual, 0]
    return costo_total

def evaluar_ruta_cvrp_distancia(ruta, matriz_distancias, demandas, cap_max):
    dist_total = 0
    carga_actual = 0
    nodo_actual = 0
    for next_nodo in ruta:
        carga_actual += demandas[next_nodo]
        if carga_actual > cap_max:
            dist_total += matriz_distancias[nodo_actual, 0] + matriz_distancias[0, next_nodo]
            carga_actual = demandas[next_nodo]
        else:
            dist_total += matriz_distancias[nodo_actual, next_nodo]
        nodo_actual = next_nodo
    dist_total += matriz_distancias[nodo_actual, 0]
    return dist_total

# ==========================================
# 3. ALGORITMO DE BÚSQUEDA TABÚ (CVRP)
# ==========================================
def busqueda_tabu_cvrp(matriz_costos, matriz_distancias, demandas, cap_max, max_iter=200, tenure=10):
    np.random.seed(42)
    current_route = [0] + list(np.random.permutation(range(1, n_nodes)))
    current_cost = evaluar_ruta_cvrp_costo(current_route, matriz_costos, demandas, cap_max)
    
    best_route = current_route.copy()
    best_cost = current_cost
    
    cost_history = [current_cost]
    tabu_list = {}
    
    print("Ejecutando Búsqueda Tabú con Restricción de Capacidad (CVRP)...")
    for iteration in range(max_iter):
        best_neighborhood_cost = float('inf')
        best_move = None
        best_neighbor_route = None
        
        sample_swaps = set()
        while len(sample_swaps) < min(200, (n_nodes-1)*(n_nodes-2)//2):
            i, j = np.random.randint(1, n_nodes, size=2)
            if i != j:
                if i > j: i, j = j, i
                sample_swaps.add((i, j))
                
        for (i, j) in sample_swaps:
            neighbor = current_route.copy()
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            cost = evaluar_ruta_cvrp_costo(neighbor, matriz_costos, demandas, cap_max)
            
            is_tabu = (i, j) in tabu_list and tabu_list[(i, j)] > iteration
            if is_tabu and cost < best_cost:
                is_tabu = False  
                
            if not is_tabu:
                if cost < best_neighborhood_cost:
                    best_neighborhood_cost = cost
                    best_move = (i, j)
                    best_neighbor_route = neighbor
                    
        if best_neighbor_route is not None:
            current_route = best_neighbor_route
            current_cost = best_neighborhood_cost
            tabu_list[best_move] = iteration + tenure
            
            if current_cost < best_cost:
                best_route = current_route.copy()
                best_cost = current_cost
        else:
            break
            
        cost_history.append(best_cost)
        
    best_dist = evaluar_ruta_cvrp_distancia(best_route, matriz_distancias, demandas, cap_max)
    return best_route, best_cost, best_dist, cost_history

best_route, best_cost, best_dist, cost_history = busqueda_tabu_cvrp(fuel_matrix, dist_matrix, demands, VEHICLE_CAPACITY)

# ==========================================
# 4. ASIGNACIÓN Y LIMPIEZA DE FORMATO
# ==========================================
# Convertir explícitamente a enteros nativos de Python para evitar la notación np.int64
tiendas_en_ruta = [int(n) for n in best_route if n >= 10]

asignacion_centros = {}
chunk_size = len(tiendas_en_ruta) // 10
for c_idx in range(1, 11):
    start = (c_idx - 1) * chunk_size
    end = start + chunk_size if c_idx < 10 else len(tiendas_en_ruta)
    asignacion_centros[c_idx] = sorted(tiendas_en_ruta[start:end])

# ==========================================
# 5. SALIDA LIMPIA EN TERMINAL
# ==========================================
print("\nASIGNACIÓN DE TIENDAS")
print("-" * 38)
for c_id, tiendas in asignacion_centros.items():
    print(f"Centro {c_id}: {len(tiendas)} tiendas -> {tiendas}")
print("-" * 38)
print(f"Costo Óptimo Total de Combustible: ${best_cost:.2f} USD")
print(f"Distancia Total Recorrida: {best_dist:.2f} km\n")

# ==========================================
# 6. GENERACIÓN AUTOMÁTICA DE GRÁFICAS
# ==========================================
sns.set_theme(style="whitegrid")

# Gráfica 1: Convergencia
plt.figure(figsize=(10, 5))
plt.plot(cost_history, color='#27ae60', linewidth=2, marker='o', markersize=3, markevery=5)
plt.title('Evolución del Costo con CVRP (Búsqueda Tabú)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Iteración', fontsize=12)
plt.ylabel('Costo de Combustible (USD)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('tabu_cvrp_cost_evolution.png', dpi=300)
plt.close()
print("Gráfica guardada: tabu_cvrp_cost_evolution.png")

# Gráfica 2: Mapa Geoespacial
plt.figure(figsize=(10, 8))
dcs = df_nodes[df_nodes['Tipo'] == 'Centro de Distribución']
stores = df_nodes[df_nodes['Tipo'] == 'Tienda']

plt.scatter(dcs['Longitud_WGS84'], dcs['Latitud_WGS84'], color='red', s=120, marker='^', label='Centros de Distribución', zorder=5)
plt.scatter(stores['Longitud_WGS84'], stores['Latitud_WGS84'], color='blue', s=30, alpha=0.7, label='Sucursales / Tiendas', zorder=4)

sample_route = best_route[:30]
route_lats = df_nodes.loc[sample_route, 'Latitud_WGS84'].values
route_lons = df_nodes.loc[sample_route, 'Longitud_WGS84'].values
route_lats = np.append(route_lats, route_lats[0])
route_lons = np.append(route_lons, route_lons[0])

plt.plot(route_lons, route_lats, color='purple', linestyle='-', linewidth=1.5, alpha=0.8, label='Trayectoria Óptima CVRP', zorder=3)

plt.title('Mapa Geoespacial y Rutas CVRP (Culiacán, Sin.)', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Longitud (WGS84)', fontsize=11)
plt.ylabel('Latitud (WGS84)', fontsize=11)
plt.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('tabu_cvrp_spatial_routes.png', dpi=300)
plt.close()
print("Gráfica guardada: tabu_cvrp_spatial_routes.png")
