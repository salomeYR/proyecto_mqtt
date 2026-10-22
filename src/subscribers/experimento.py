import time
import psutil
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# =====================================================================
# 1. FUNCIÓN DE ANÁLISIS
# =====================================================================
def analizar_ventana(datos_ventana):
    """
    Calcula RMS, Valor Pico y Desviación Estándar de una ventana de datos.
    Se ejecuta de forma idéntica tanto en modo secuencial como paralelo.
    """
    arr = np.array(datos_ventana)
    
    # Simulación de carga computacional repetida para hacer significativa la prueba
    # (Repite los cálculos matemáticos sobre la matriz para simular un pipeline real de análisis)
    for _ in range(500):
        rms = np.sqrt(np.mean(arr ** 2))
        pico = np.max(np.abs(arr))
        std_dev = np.std(arr)
        
    return {
        "rms": round(float(rms), 6),
        "pico": round(float(pico), 6),
        "std_dev": round(float(std_dev), 6)
    }

# =====================================================================
# 2. GENERADOR DE DATOS DE SINTESIS (10 Ventanas por corrida)
# =====================================================================
def generar_ventanas_corrida(run_id, num_ventanas=10, muestras_por_ventana=10000):
    """
    Genera 10 ventanas de datos sintéticos de vibración identificadas por run_id.
    """
    ventanas = []
    np.random.seed(run_id) # Semilla fija por corrida para asegurar reproducibilidad
    for i in range(num_ventanas):
        t = np.linspace(0, 1, muestras_por_ventana, endpoint=False)
        ruido = np.random.normal(0, 0.1, muestras_por_ventana)
        senos = np.sin(2 * np.pi * 5 * t) + ruido
        ventanas.append(senos.tolist())
    return ventanas

# =====================================================================
# 3. MODO SECUENCIAL
# =====================================================================
def ejecutar_modo_secuencial(ventanas):
    tiempos_ventanas = []
    resultados = []
    
    for ventana in ventanas:
        t_inicio = time.perf_counter()
        res = analizar_ventana(ventana)
        t_fin = time.perf_counter()
        
        tiempos_ventanas.append(t_fin - t_inicio)
        resultados.append(res)
        
    return resultados, tiempos_ventanas

# =====================================================================
# 4. MODO PARALELO
# =====================================================================
def ejecutar_modo_paralelo(ventanas, num_workers=4):
    tiempos_ventanas = []
    
    # Medimos el tiempo individual enviando los trabajos al pool de procesos
    t_inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        resultados = list(executor.map(analizar_ventana, ventanas))
    t_fin = time.perf_counter()
    
    tiempo_total = t_fin - t_inicio
    # Tiempo estimado promedio asignado por ventana en paralelo
    tiempos_ventanas = [tiempo_total / len(ventanas)] * len(ventanas)
    
    return resultados, tiempos_ventanas, tiempo_total

# =====================================================================
# 5. BLOQUE PRINCIPAL (5 Corridas Secuenciales vs 5 Paralelas)
# =====================================================================
if __name__ == "__main__":
    NUM_CORRIDAS = 5
    NUM_VENTANAS = 10
    WORKERS = 4  # Número de núcleos / trabajadores paralelos
    
    print("=" * 70)
    print(" INICIANDO EXPERIMENTO COMPUTACIONAL (5 CORRIDAS SECUENCIALES VS PARALELAS)")
    print("=" * 70)
    
    # -----------------------------------------------------------------
    # EJECUCIÓN SECUENCIAL
    # -----------------------------------------------------------------
    print("\n [1/2] Ejecutando 5 Corridas en Modo SECUENCIAL...")
    tiempos_secuenciales_totales = []
    resultados_secuenciales_all = []
    
    psutil.cpu_percent(interval=None) # Resetear medidor de CPU
    t_sec_inicio_bloque = time.perf_counter()
    
    for run_id in range(1, NUM_CORRIDAS + 1):
        ventanas = generar_ventanas_corrida(run_id, num_ventanas=NUM_VENTANAS)
        res, tiempos_v = ejecutar_modo_secuencial(ventanas)
        
        duracion_corrida = sum(tiempos_v)
        tiempos_secuenciales_totales.append(duracion_corrida)
        resultados_secuenciales_all.append(res)
        print(f"   - Corrida {run_id} completada en {duracion_corrida:.4f} s")
        
    t_sec_fin_bloque = time.perf_counter()
    cpu_promedio_sec = psutil.cpu_percent(interval=None)
    
    # -----------------------------------------------------------------
    # EJECUCIÓN PARALELA
    # -----------------------------------------------------------------
    print("\n [2/2] Ejecutando 5 Corridas en Modo PARALELO (ProcessPoolExecutor)...")
    tiempos_paralelos_totales = []
    resultados_paralelos_all = []
    
    psutil.cpu_percent(interval=None) # Resetear medidor de CPU
    t_par_inicio_bloque = time.perf_counter()
    
    for run_id in range(1, NUM_CORRIDAS + 1):
        ventanas = generar_ventanas_corrida(run_id, num_ventanas=NUM_VENTANAS)
        res, tiempos_v, t_total = ejecutar_modo_paralelo(ventanas, num_workers=WORKERS)
        
        tiempos_paralelos_totales.append(t_total)
        resultados_paralelos_all.append(res)
        print(f"   - Corrida {run_id} completada en {t_total:.4f} s")
        
    t_par_fin_bloque = time.perf_counter()
    cpu_promedio_par = psutil.cpu_percent(interval=None)
    
    # =====================================================================
    # 6. VERIFICACIÓN Y RESULTADOS FINALES
    # =====================================================================
    print("\n" + "=" * 70)
    print(" VERIFICACIÓN DE RESULTADOS ANALÍTICOS")
    print("=" * 70)
    
    # Comprobar si los valores matemáticos calculados son idénticos en ambos modos
    coinciden = True
    for r in range(NUM_CORRIDAS):
        for v in range(NUM_VENTANAS):
            if resultados_secuenciales_all[r][v] != resultados_paralelos_all[r][v]:
                coinciden = False
                break
                
    if coinciden:
        print(" [CORRECTO] Los resultados analíticos (RMS, Pico, Std) coinciden EXACTAMENTE en ambos modos.")
    else:
        print(" [ERROR] Se detectaron diferencias en los cálculos analíticos.")

    # Mediana de los tiempos
    mediana_sec = np.median(tiempos_secuenciales_totales)
    mediana_par = np.median(tiempos_paralelos_totales)
    speedup = mediana_sec / mediana_par if mediana_par > 0 else 0

    print("\n" + "=" * 70)
    print(" RESUMEN DE RENDIMIENTO Y COMPARATIVA")
    print("=" * 70)
    print(f" Modo Secuencial - Mediana de Tiempo: {mediana_sec:.4f} s | CPU Promedio Bloque: {cpu_promedio_sec}%")
    print(f" Modo Paralelo   - Mediana de Tiempo: {mediana_par:.4f} s | CPU Promedio Bloque: {cpu_promedio_par}%")
    print(f" Aceleración (Speedup): {speedup:.2f}x más rápido en paralelo.")
    print("-" * 70)
    
    # Decisión
    print(" DECISIÓN Y CONCLUSIÓN:")
    if speedup > 1.2:
        print(" -> Conviene utilizar el MODO PARALELO.")
        print("    Razón: El costo de creación de procesos es superado ampliamente por la ganancia al distribuir el procesamiento matemático en múltiples núcleos de la CPU.")
    else:
        print(" -> Conviene utilizar el MODO SECUENCIAL.")
        print("    Razón: El volumen de datos no es lo suficientemente grande para compensar la sobrecarga (overhead) que genera la creación de procesos en Windows.")