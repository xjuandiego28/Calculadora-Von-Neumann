from cpu import CPU
from memoria import Memoria


OPCIONES_OPERACION = {
    "1": "ADD",
    "2": "SUB",
    "3": "MUL",
    "4": "DIV",
    "5": "HALT",
}

DESCRIPCIONES_OPERACION = {
    "ADD": "Suma",
    "SUB": "Resta",
    "MUL": "Multiplicación",
    "DIV": "División",
    "HALT": "Detener la CPU",
}


def mostrar_menu_operaciones():
    print("\nOperaciones disponibles:")
    for opcion, codigo in OPCIONES_OPERACION.items():
        print(f"  {opcion}. {DESCRIPCIONES_OPERACION[codigo]} ({codigo})")


def leer_entero(mensaje, opciones_validas=None):
    while True:
        valor = input(mensaje).strip()
        if opciones_validas and valor not in opciones_validas:
            print(f"Entrada inválida. Opciones válidas: {', '.join(opciones_validas)}.")
            continue
        try:
            return int(valor)
        except ValueError:
            print("Entrada inválida. Debes escribir un número entero.")


def leer_numero(mensaje):
    while True:
        valor = input(mensaje).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print("Entrada inválida. Debes escribir un número. Ejemplo: 12.5")


def leer_operacion(numero_operacion):
    mostrar_menu_operaciones()
    while True:
        entrada = input(f"Selecciona la operación {numero_operacion} por número o código: ").strip().upper()
        operacion = OPCIONES_OPERACION.get(entrada, entrada)
        if operacion in OPCIONES_OPERACION.values():
            return operacion
        print("Operación no reconocida. Usa ADD, SUB, MUL, DIV, HALT o una opción del menú.")


def leer_instruccion(numero_operacion):
    operacion = leer_operacion(numero_operacion)
    if operacion == "HALT":
        return ("HALT", 0.0, 0.0)

    print(f"\nOperandos para {DESCRIPCIONES_OPERACION[operacion]} ({operacion})")
    a = leer_numero("  Ingresa el primer operando (A): ")
    while True:
        b = leer_numero("  Ingresa el segundo operando (B): ")
        if operacion == "DIV" and b == 0:
            print("No se puede dividir entre cero. Ingresa otro valor para B.")
            continue
        return (operacion, a, b)


def leer_cantidad_operaciones():
    print("\n¿Cuántas instrucciones deseas ejecutar ahora?")
    print("  1. Una instrucción con una unidad aritmético-lógica")
    print("  2. Dos instrucciones aritméticas en paralelo con dos unidades aritmético-lógicas")
    return leer_entero("Selecciona 1 o 2: ", opciones_validas=("1", "2"))


def guardar_instruccion(memoria, cpu, instruccion):
    direccion = memoria.guardar(instruccion)
    print(f"\nLa instrucción se guardó en memoria[{direccion}]: {cpu.formatear_instruccion(instruccion)}.")
    return direccion


def ejecutar_una_instruccion(memoria, cpu):
    instruccion = leer_instruccion(1)
    guardar_instruccion(memoria, cpu, instruccion)
    cpu.ciclo()


def ejecutar_dos_instrucciones(memoria, cpu):
    print("\nModo paralelo: se usarán dos unidades aritmético-lógicas.")
    print("Nota: en este modo solo tienen sentido ADD, SUB, MUL, DIV y HALT.")

    instruccion1 = leer_instruccion(1)
    instruccion2 = leer_instruccion(2)
    guardar_instruccion(memoria, cpu, instruccion1)
    guardar_instruccion(memoria, cpu, instruccion2)

    print("\n[PREPARACIÓN DEL PROCESAMIENTO PARALELO]")
    print(f"El contador de programa apunta a la primera instrucción del par: {cpu.contador_programa}.")
    print(f"La unidad aritmético-lógica 1 tomará memoria[{cpu.contador_programa}].")
    print(f"La unidad aritmético-lógica 2 tomará memoria[{cpu.contador_programa + 1}].")

    resultado1, resultado2 = cpu.ejecutar_dos(instruccion1, instruccion2)

    print("\nRESULTADOS DEL PROCESAMIENTO PARALELO")
    print(f"  Resultado de la unidad aritmético-lógica 1: {resultado1}")
    print(f"  Resultado de la unidad aritmético-lógica 2: {resultado2}")


def crear_calculadora(benchmark=False, benchmark_retardo=0.0):
    """Crea una CPU con memoria lista para ejecutar o medir."""
    memoria = Memoria()
    cpu = CPU(memoria, benchmark=benchmark, benchmark_retardo=benchmark_retardo)
    return memoria, cpu


def ejecutar_secuencia(instrucciones, usar_dos_ual=False, benchmark=False, benchmark_retardo=0.0):
    """
    Ejecuta exactamente la misma secuencia de dos instrucciones.

    Con una UAL se ejecutan en dos ciclos secuenciales. Con dos UAL se
    ejecutan simultáneamente mediante CPU.ejecutar_dos().
    """
    if len(instrucciones) != 2:
        raise ValueError("La prueba de rendimiento requiere exactamente dos instrucciones.")

    memoria, cpu = crear_calculadora(
        benchmark=benchmark,
        benchmark_retardo=benchmark_retardo,
    )
    memoria.cargar_programa(instrucciones)

    if usar_dos_ual:
        return cpu.ejecutar_dos(*instrucciones, mostrar_pasos=False)

    resultados = []
    for _ in instrucciones:
        resultados.append(cpu.ciclo_sin_interfaz())

    return tuple(resultados)


def main():
    memoria, cpu = crear_calculadora()

    print("\n" + "=" * 68)
    print("CALCULADORA VON NEUMANN - VERSIÓN EN CONSOLA")
    print("=" * 68)
    print("Este simulador muestra el ciclo: búsqueda -> decodificación -> ejecución.")
    print("Puede ejecutar una instrucción o dos instrucciones aritméticas en paralelo.")
    while cpu.on:
        cantidad = leer_cantidad_operaciones()
        if cantidad == 1:
            ejecutar_una_instruccion(memoria, cpu)
        else:
            ejecutar_dos_instrucciones(memoria, cpu)

    print("\nLa CPU quedó detenida. Fin de la simulación.")


if __name__ == "__main__":
    main()
