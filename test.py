"""Benchmark de una UAL vs. dos UAL para dos instrucciones independientes."""

import statistics
import time

from main import ejecutar_secuencia


# Un pequeño retardo representa el tiempo de un ciclo de la UAL en el modelo.
# Con 0.0 se mide únicamente el costo computacional/overhead de Python.
RETARDO_CICLO = 0.01
REPETICIONES = 30
CALENTAMIENTO = 5

# Dos instrucciones independientes: ninguna necesita el resultado de la otra.
SECUENCIA = (
    ("ADD", 20.0, 30.0),
    ("MUL", 7.0, 8.0),
)


def medir(usar_dos_ual):
    """Devuelve las mediciones de tiempo de una configuración."""
    for _ in range(CALENTAMIENTO):
        ejecutar_secuencia(
            SECUENCIA,
            usar_dos_ual=usar_dos_ual,
            benchmark=True,
            benchmark_retardo=RETARDO_CICLO,
        )

    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        resultados = ejecutar_secuencia(
            SECUENCIA,
            usar_dos_ual=usar_dos_ual,
            benchmark=True,
            benchmark_retardo=RETARDO_CICLO,
        )
        tiempos.append(time.perf_counter() - inicio)

    return tiempos, resultados


def main():
    tiempos_secuencial, resultados_secuencial = medir(usar_dos_ual=False)
    tiempos_paralelo, resultados_paralelo = medir(usar_dos_ual=True)

    tiempo_secuencial = statistics.median(tiempos_secuencial)
    tiempo_paralelo = statistics.median(tiempos_paralelo)

    ahorro = (tiempo_secuencial - tiempo_paralelo) / tiempo_secuencial * 100
    speedup = tiempo_secuencial / tiempo_paralelo

    # La comparación solo es válida si ambas configuraciones producen lo mismo.
    if resultados_secuencial != resultados_paralelo:
        raise AssertionError(
            "Los resultados de la ejecución secuencial y paralela no coinciden."
        )

    print("=" * 70)
    print("BENCHMARK: 1 UAL vs. 2 UAL")
    print("=" * 70)
    print(f"Secuencia: {SECUENCIA[0]} -> {SECUENCIA[1]}")
    print(f"Retardo simulado por ciclo: {RETARDO_CICLO * 1000:.2f} ms")
    print(f"Repeticiones: {REPETICIONES}")
    print()
    print(f"1 UAL (secuencial): {tiempo_secuencial * 1000:.3f} ms")
    print(f"2 UAL (paralelo):   {tiempo_paralelo * 1000:.3f} ms")
    print()
    print(f"Reducción de tiempo: {ahorro:.2f}%")
    print(f"Speedup:             {speedup:.2f}x")
    print("Speedup ideal para dos operaciones iguales: 2.00x")
    print("Reducción ideal: 50.00%")
    print()
    print(f"Resultado 1: {resultados_paralelo[0]}")
    print(f"Resultado 2: {resultados_paralelo[1]}")
    print("=" * 70)


if __name__ == "__main__":
    main()
