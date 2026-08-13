class Memoria:
    def __init__(self):
        self.memoria = []

    def guardar(self, instruccion):
        # Guardar como lista: [operacion, dato1, dato2, resultado]
        instr_con_resultado = list(instruccion) + [None]
        self.memoria.append(instr_con_resultado)
        return len(self.memoria) - 1

    def leer(self, direccion):
        # Devolver solo operación, dato1, dato2 (sin el resultado)
        instr = self.memoria[direccion]
        return tuple(instr[:3])

    def actualizar_resultado(self, direccion, resultado):
        """Actualiza el resultado de una instrucción en memoria."""
        if 0 <= direccion < len(self.memoria):
            self.memoria[direccion][3] = resultado

    def obtener_resultado(self, direccion):
        """Obtiene el resultado de una instrucción."""
        if 0 <= direccion < len(self.memoria):
            return self.memoria[direccion][3]
        return None

    def cargar_programa(self, instrucciones):
        self.reiniciar()
        for instruccion in instrucciones:
            self.guardar(instruccion)

    def mostrar(self):
        for i, instruccion in enumerate(self.memoria):
            print(i, instruccion)

    def reiniciar(self):
        self.memoria.clear()
