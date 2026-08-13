from memoria import Memoria 
from cpu import CPU 
memoria = Memoria()
cpu = CPU(memoria)

while cpu.on:
    a = 0
    b = 0
    c = 0
    d = 0
    print("\n ======================================")
    print("\n ==================MENU================\n" \
    "1. Suma (input ADD)\n"
    "2. Resta (input SUB)\n"
    "3. Multiplicacion (input MUL)\n"
    "4. Division (input DIV)\n"
    "5. Detener el programa (input HALT)\n")
    cantidad = int(input("Ingrese la cantidad de operaciones que desea hacer simultaneamente (maximo 2 por ahora): "))
    if cantidad == 1:
        operacion = input("Escoge la operacion que deseas hacer: ")
        if operacion.upper() != "HALT":
            a = float(input("Escoge el numero que deseas operar: "))
            b = float(input("Escoge el otro numero: "))
        memoria.guardar((operacion.upper(), a, b))
        cpu.ciclo()
    else: 
        operacion_1 = input("Escoge la primera operacion que deseas hacer: ")
        operacion_2 = input("Escoge la segunda operacion que deseas hacer: ")
        if operacion_1.upper() != "HALT" or operacion_2.upper() != "HALT":
            a = float(input("Ingrese el numero que desea operar: "))
            b = float(input("Ingrese el segundo numero que desea operar: "))
            c = float(input("Ingresa el primer numero para la segunda operacion: "))
            d = float(input("Ingresa el segundo numero para la segunda operacion "))
        instruccion1 = (operacion_1.upper(), a, b)
        instruccion2 = (operacion_2.upper(), c, d)

        memoria.guardar(instruccion1)
        memoria.guardar(instruccion2)

        resultado1, resultado2 = cpu.ejecutar_dos(
            instruccion1,
            instruccion2
        )

        print("\nRESULTADOS")
        print("Modulo 1:", resultado1)
        print("Modulo 2:", resultado2)
        cpu.ciclo()
        if cpu.on:
            cpu.ciclo()
