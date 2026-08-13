from alu import ALU
from alu2 import ALU2
import time
import threading

class CPU:
    def __init__(self, memoria, benchmark=False):
        self.memoria = memoria 
        self.pc = 0
        self.ir = None
        self.ac = 0
        self.mar = None 
        self.mbr = None 

        self.memoria_datos = {}

        self.benchmark = benchmark
        self.alu = ALU()
        self.alu2 = ALU2()

        self.on = True 
        self.operaciones1 = {
            "ADD": self.alu.sumar,
            "SUB": self.alu.restar,
            "MUL": self.alu.multiplicar,
            "DIV": self.alu.dividir,
        }
        self.operaciones2 = {
            "ADD": self.alu2.sumar,
            "SUB": self.alu2.restar,
            "MUL": self.alu2.multiplicar,
            "DIV": self.alu2.dividir,
            }
    def fetch(self):
        self.mar = self.pc

        if self.mar >= len(self.memoria.memoria):
            print("MAR fuera de rango, no hay mas instrucciones en la memoria")
            self.ir = None
            self.on = False
            return 
        self.mbr = self.memoria.leer(self.pc)
        self.ir = self.mbr

        print("FETCH")
        print("PC: ", self.pc)
        print("MAR: ", self.mar)
        print("MBR: ", self.mbr)
        print("IR: ", self.ir)
        time.sleep(1)
    def decodificar(self):
        operacion = self.ir[0]

        print("Decodificar")
        print("Operacion", operacion)
        time.sleep(1)

        return operacion
    def ejecutar(self, operacion):
        operacion = self.ir[0]
        print("EJECUTARRR")

        if operacion == "HALT":
            self.on = False
            return
        funcion = self.operaciones1.get(operacion)
        if funcion is None: 
            print(f"Operacion no encontrada: {operacion}")
            return 
        a, b = self.ir[1], self.ir[2]
        time.sleep(1)

        if operacion == "DIV" and b == 0:
            print("Error, division entre 0")
            return 
        self.ac = funcion(a, b)
        print(f"AC: {self.ac}")
        time.sleep(1)

    def ejecutar_modulo(self, instruccion, modulo):
        print("EJECUTAR")
        operacion = instruccion[0]

        if operacion == "HALT":
            return None

        if modulo == 1:
            funcion = self.operaciones1.get(operacion)
        else:
            funcion = self.operaciones2.get(operacion)

        if funcion is None:
            print(f"Operacion no encontrada: {operacion}")
            return None

        a, b = instruccion[1], instruccion[2]

        if operacion == "DIV" and b == 0:
            print("Error, division entre 0")
            return None
        if operacion == "LOAD":
            direccion = int(self.ir[1])
            valor = self.memoria_datos.get(direccion, 0)
            self.ac = valor 
            print(f"LOAD -> AC = memoria_datos[{direccion}] = {valor}")
            return
        
        if operacion == "STORE":
            direccion = int(self.ir[1])
            self.memoria_datos[direccion] = self.ac
            print(f"STORE -> memoria_datos[{direccion}] = AC ({self.ac})")
            return
        
        resultado = funcion(a, b)

        print(f"ALU {modulo}: {a} {operacion} {b} = {resultado}")

        return resultado
    
    def ejecutar_dos(self, instruccion1, instruccion2):

        resultado1 = [None]
        resultado2 = [None]

        hilo1 = threading.Thread(
            target=lambda: resultado1.__setitem__(
                0, self.ejecutar_modulo(instruccion1, 1)
            )
        )

        hilo2 = threading.Thread(
            target=lambda: resultado2.__setitem__(
                0, self.ejecutar_modulo(instruccion2, 2)
            )
        )

        hilo1.start()
        hilo2.start()

        hilo1.join()
        hilo2.join()

        return resultado1[0], resultado2[0]

    def ciclo(self):
        self.fetch()
        if not self.on or self.ir is None:
            return
        operacion = self.decodificar()
        self.ejecutar(operacion)
        if self.on:
            self.pc += 1
    def ejecutar_programa(self):
        print("=== EJECUTANDO ===")
        self.pc = 0
        self.on = True 
        instrucciones = 0

        while self.on and self.pc < len(self.memoria.memoria):
            self.ciclo()
            instrucciones += 1

        print("=== PROGRAMA FINALIZADO "
            f"({instrucciones} instrucciones ejecutadas y AC final {self.ac}) ===")
        return instrucciones