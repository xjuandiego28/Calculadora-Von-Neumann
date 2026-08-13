class Memoria:
    def __init__(self):
        self.memoria = []

    def guardar(self, instruccion):
        self.memoria.append(instruccion)

    def leer(self, direccion):
        return self.memoria[direccion]

    def cargar_programa(self, instrucciones):
        self.reiniciar()
        for instruccion in instrucciones:
            self.guardar(instruccion)

    def mostrar(self):
        for i, instrucccion in enumerate(self.memoria):
            print(i, instrucccion)
    def reiniciar(self):
        self.memoria.clear()