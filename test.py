"""Benchmark de rendimiento de una UAL vs. dos UAL."""

import statistics
import time

import matplotlib.pyplot as plt

from main import ejecutar_secuencia


RETARDO_CICLO = 0.01
REPETICIONES = 30
CALENTAMIENTO = 5
MAX_OPERACIONES = 20


# Operaciones independientes. Ninguna necesita el resultado de otra.
OPERACIONES_BASE = (
    ("ADD", 20.0, 30.0),
    ("MUL", 7.0, 8.0),
    ("SUB", 100.0, 25.0),
    ("DIV", 144.0, 12.0),
)


def construir_secuencia(cantidad):
    """Construye una secuencia de 'cantidad' operaciones independientes."""
    if cantidad < 2 or cantidad % 2 != 0:
        raise ValueError("La cantidad de operaciones debe ser par y mayor o igual a 2.")

    return tuple(OPERACIONES_BASE[i % len(OPERACIONES_BASE)] for i in range(cantidad))


def medir(secuencia, usar_dos_ual):
    """Mide una configuración y devuelve tiempos y resultados."""
    for _ in range(CALENTAMIENTO):
        ejecutar_secuencia(
            secuencia,
            usar_dos_ual=usar_dos_ual,
            benchmark=True,
            benchmark_retardo=RETARDO_CICLO,
        )

    tiempos = []
    resultados = None

    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        resultados = ejecutar_secuencia(
            secuencia,
            usar_dos_ual=usar_dos_ual,
            benchmark=True,
            benchmark_retardo=RETARDO_CICLO,
        )
        tiempos.append(time.perf_counter() - inicio)

    return statistics.median(tiempos), resultados


def ejecutar_benchmark():
    """Ejecuta todas las pruebas y devuelve los datos para los gráficos."""
    datos = {
        "operaciones": [],
        "tiempo_1_ual": [],
        "tiempo_2_ual": [],
        "mejora": [],
        "speedup": [],
    }

    for cantidad in range(2, MAX_OPERACIONES + 1, 2):
        secuencia = construir_secuencia(cantidad)

        tiempo_1, resultados_1 = medir(secuencia, usar_dos_ual=False)
        tiempo_2, resultados_2 = medir(secuencia, usar_dos_ual=True)

        if resultados_1 != resultados_2:
            raise AssertionError(
                f"Los resultados no coinciden para {cantidad} operaciones."
            )

        mejora = (tiempo_1 - tiempo_2) / tiempo_1 * 100
        speedup = tiempo_1 / tiempo_2

        datos["operaciones"].append(cantidad)
        datos["tiempo_1_ual"].append(tiempo_1 * 1000)
        datos["tiempo_2_ual"].append(tiempo_2 * 1000)
        datos["mejora"].append(mejora)
        datos["speedup"].append(speedup)

    return datos


def mostrar_resultados(datos):
    print("=" * 78)
    print("BENCHMARK: 1 UAL vs. 2 UAL")
    print("=" * 78)
    print(f"Retardo simulado por ciclo: {RETARDO_CICLO * 1000:.2f} ms")
    print(f"Repeticiones por prueba:    {REPETICIONES}")
    print()
    print(
        f"{'Operaciones':>12} | {'1 UAL (ms)':>12} | {'2 UAL (ms)':>12} | "
        f"{'Mejora':>10} | {'Speedup':>9}"
    )
    print("-" * 78)

    for i, cantidad in enumerate(datos["operaciones"]):
        print(
            f"{cantidad:>12} | "
            f"{datos['tiempo_1_ual'][i]:>12.3f} | "
            f"{datos['tiempo_2_ual'][i]:>12.3f} | "
            f"{datos['mejora'][i]:>9.2f}% | "
            f"{datos['speedup'][i]:>8.2f}x"
        )

    print("-" * 78)
    print("Referencia teórica: 50% de reducción y 2.00x de speedup.")
    print("=" * 78)


def graficar_tiempos(datos):
    """Genera el gráfico de tiempo de ejecución."""
    plt.figure(figsize=(9, 5))
    plt.plot(
        datos["operaciones"],
        datos["tiempo_1_ual"],
        marker="o",
        label="1 UAL - secuencial",
    )
    plt.plot(
        datos["operaciones"],
        datos["tiempo_2_ual"],
        marker="o",
        label="2 UAL - paralelo",
    )
    plt.xlabel("Número de operaciones")
    plt.ylabel("Tiempo de ejecución (ms)")
    plt.title("Tiempo de ejecución según el número de operaciones")
    plt.xticks(datos["operaciones"])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def graficar_mejora(datos):
    """Genera el gráfico de reducción porcentual del tiempo."""
    plt.figure(figsize=(9, 5))
    plt.plot(
        datos["operaciones"],
        datos["mejora"],
        marker="o",
        label="Mejora observada",
    )
    plt.axhline(
        50,
        linestyle="--",
        label="Máximo teórico: 50%",
    )
    plt.xlabel("Número de operaciones")
    plt.ylabel("Reducción del tiempo (%)")
    plt.title("Mejora de rendimiento con dos UAL")
    plt.xticks(datos["operaciones"])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    datos = ejecutar_benchmark()
    mostrar_resultados(datos)
    graficar_tiempos(datos)
    graficar_mejora(datos)


if __name__ == "__main__":
    main()
