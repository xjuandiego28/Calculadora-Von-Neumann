class Memoria:
    def __init__(self):
        self.memoria = []

    def guardar(self, instruccion):
        self.memoria.append(instruccion)
        return len(self.memoria) - 1

    def leer(self, direccion):
        return self.memoria[direccion]

    def cargar_programa(self, instrucciones):
        self.reiniciar()
        for instruccion in instrucciones:
            self.guardar(instruccion)

    def mostrar(self):
        for i, instruccion in enumerate(self.memoria):
            print(i, instruccion)

    def reiniciar(self):
        self.memoria.clear()
