import threading
import time

from alu import UnidadAritmeticoLogica


class CPU:
    OPERACIONES_ARITMETICAS = ("ADD", "SUB", "MUL", "DIV")
    OPERACIONES_MEMORIA = ("LOAD", "STORE")
    OPERACIONES_VALIDAS = OPERACIONES_ARITMETICAS + OPERACIONES_MEMORIA + ("HALT",)

    SIMBOLOS = {
        "ADD": "+",
        "SUB": "-",
        "MUL": "*",
        "DIV": "/",
    }

    NOMBRES_OPERACIONES = {
        "ADD": "Suma",
        "SUB": "Resta",
        "MUL": "Multiplicación",
        "DIV": "División",
        "LOAD": "Carga desde la memoria de datos",
        "STORE": "Almacenamiento en memoria de datos",
        "HALT": "Detención del programa",
    }

    def __init__(self, memoria, benchmark=False, retardo=1):
        self.memoria = memoria
        self.contador_programa = 0
        self.registro_instruccion = None
        self.acumulador = 0
        self.registro_direccion_memoria = None
        self.registro_datos_memoria = None
        self.memoria_datos = {}

        self.benchmark = benchmark
        self.retardo = 0 if benchmark else retardo
        self.unidad_aritmetico_logica_1 = UnidadAritmeticoLogica()
        self.unidad_aritmetico_logica_2 = UnidadAritmeticoLogica()
        self.unidades_aritmetico_logicas = [
            self.unidad_aritmetico_logica_1,
            self.unidad_aritmetico_logica_2,
        ]

        self.on = True
        self.operaciones_unidad_1 = self._crear_tabla_operaciones(self.unidad_aritmetico_logica_1)
        self.operaciones_unidad_2 = self._crear_tabla_operaciones(self.unidad_aritmetico_logica_2)
        self.tablas_operaciones = [self.operaciones_unidad_1, self.operaciones_unidad_2]

    def _crear_tabla_operaciones(self, unidad_aritmetico_logica):
        return {
            "ADD": unidad_aritmetico_logica.sumar,
            "SUB": unidad_aritmetico_logica.restar,
            "MUL": unidad_aritmetico_logica.multiplicar,
            "DIV": unidad_aritmetico_logica.dividir,
        }

    def pausar(self):
        if self.retardo > 0:
            time.sleep(self.retardo)

    def informar(self, mensaje):
        print(mensaje)
        self.pausar()

    def formatear_instruccion(self, instruccion):
        operacion, a, b = instruccion
        if operacion == "HALT":
            return "HALT"
        if operacion in self.OPERACIONES_MEMORIA:
            return f"{operacion} dirección={int(a)}"
        return f"{operacion} {a:g}, {b:g}"

    def validar_instruccion(self, instruccion):
        if len(instruccion) != 3:
            raise ValueError("La instrucción debe tener operación, primer parámetro y segundo parámetro.")

        operacion, a, b = instruccion
        if operacion not in self.OPERACIONES_VALIDAS:
            raise ValueError(f"Operación no reconocida: {operacion}.")
        if operacion == "DIV" and b == 0:
            raise ValueError("No se puede dividir entre cero.")
        if operacion in self.OPERACIONES_MEMORIA and int(a) < 0:
            raise ValueError("La dirección de memoria no puede ser negativa.")

    def buscar_instruccion(self):
        self.informar("\n[BÚSQUEDA DE INSTRUCCIÓN]")
        self.informar(
            "El contador de programa contiene la dirección de la siguiente "
            f"instrucción: {self.contador_programa}."
        )
        self.registro_direccion_memoria = self.contador_programa
        self.informar(
            "El valor del contador de programa se copia al registro de dirección "
            f"de memoria: {self.registro_direccion_memoria}."
        )

        if self.registro_direccion_memoria >= len(self.memoria.memoria):
            self.registro_instruccion = None
            self.on = False
            self.informar(
                "El registro de dirección de memoria está fuera de rango: "
                "no hay más instrucciones en memoria."
            )
            return None

        self.registro_datos_memoria = self.memoria.leer(self.registro_direccion_memoria)
        self.informar(
            f"La memoria entrega memoria[{self.registro_direccion_memoria}] = "
            f"{self.formatear_instruccion(self.registro_datos_memoria)}; ese valor queda en "
            "el registro de datos de memoria."
        )
        self.registro_instruccion = self.registro_datos_memoria
        self.informar(
            "El contenido del registro de datos de memoria se copia al registro "
            f"de instrucción: {self.formatear_instruccion(self.registro_instruccion)}."
        )
        return self.registro_instruccion

    def decodificar(self):
        if self.registro_instruccion is None:
            return None

        operacion = self.registro_instruccion[0]
        descripcion = self.NOMBRES_OPERACIONES.get(operacion, "Operación desconocida")
        self.informar("\n[DECODIFICACIÓN]")
        self.informar(f"La unidad de control lee el operador '{operacion}', que representa: {descripcion}.")
        return operacion

    def ejecutar(self, operacion=None, modulo=1):
        if self.registro_instruccion is None:
            return None

        return self.ejecutar_modulo(
            self.registro_instruccion,
            modulo=modulo,
            actualizar_acumulador=True,
            mostrar_pasos=True,
        )

    def ejecutar_modulo(self, instruccion, modulo=1, actualizar_acumulador=False, mostrar_pasos=True):
        self.validar_instruccion(instruccion)
        operacion, a, b = instruccion
        nombre_modulo = f"unidad aritmético-lógica {modulo}"

        if mostrar_pasos:
            self.informar(f"\n[EJECUCIÓN EN {nombre_modulo.upper()}]")

        if operacion == "HALT":
            self.on = False
            if mostrar_pasos:
                self.informar("La instrucción HALT apaga la CPU. No se ejecutan más instrucciones.")
            return None

        if operacion == "LOAD":
            direccion = int(a)
            valor = self.memoria_datos.get(direccion, 0)
            if actualizar_acumulador:
                self.acumulador = valor
            if mostrar_pasos:
                self.informar(f"Se lee memoria_datos[{direccion}] = {valor:g}.")
                self.informar(f"El valor leído se copia al acumulador: {self.acumulador:g}.")
            return valor

        if operacion == "STORE":
            direccion = int(a)
            self.memoria_datos[direccion] = self.acumulador
            if mostrar_pasos:
                self.informar(
                    "Se copia el acumulador hacia memoria de datos: "
                    f"memoria_datos[{direccion}] = {self.acumulador:g}."
                )
            return self.acumulador

        tabla = self.tablas_operaciones[modulo - 1]
        funcion = tabla[operacion]
        simbolo = self.SIMBOLOS[operacion]

        if mostrar_pasos:
            self.informar(
                "Los operandos salen del registro de instrucción hacia la "
                f"{nombre_modulo}: A = {a:g}, B = {b:g}."
            )
            self.informar(f"La {nombre_modulo} reemplaza el operador: {a:g} {simbolo} {b:g}.")

        resultado = funcion(a, b)

        if actualizar_acumulador:
            self.acumulador = resultado

        if mostrar_pasos:
            self.informar(f"La {nombre_modulo} calcula el resultado: {resultado:g}.")
            if actualizar_acumulador:
                self.informar(f"El resultado se guarda en el acumulador: {self.acumulador:g}.")

        return resultado

    def avanzar_contador_programa(self, cantidad=1):
        anterior = self.contador_programa
        self.contador_programa += cantidad
        self.informar(
            "El contador de programa avanza: "
            f"{anterior} -> {self.contador_programa}."
        )

    def ciclo(self):
        self.buscar_instruccion()
        if not self.on or self.registro_instruccion is None:
            return None

        operacion = self.decodificar()
        resultado = self.ejecutar(operacion)
        if self.on:
            self.avanzar_contador_programa()
        return resultado

    def ejecutar_dos(self, instruccion1, instruccion2, mostrar_pasos=True):
        resultados = [None, None]
        instrucciones = [instruccion1, instruccion2]

        for instruccion in instrucciones:
            self.validar_instruccion(instruccion)

        if mostrar_pasos:
            self.informar("\n[BÚSQUEDA PARALELA DE DOS INSTRUCCIONES]")
            self.informar(
                "El contador de programa apunta a la primera instrucción del par: "
                f"{self.contador_programa}."
            )
            for desplazamiento, instruccion in enumerate(instrucciones):
                direccion = self.contador_programa + desplazamiento
                self.registro_direccion_memoria = direccion
                self.registro_datos_memoria = instruccion
                self.informar(
                    "El registro de dirección de memoria toma el valor "
                    f"{direccion}; se lee memoria[{direccion}] para el módulo {desplazamiento + 1}."
                )
                self.informar(
                    "El registro de datos de memoria recibe "
                    f"{self.formatear_instruccion(instruccion)} y lo entrega a la "
                    f"unidad aritmético-lógica {desplazamiento + 1}."
                )
            self.registro_instruccion = instrucciones[0]
            self.informar("El registro de instrucción conserva la primera instrucción del par como referencia de control.")

        def ejecutar_en_modulo(indice):
            modulo = indice + 1
            instruccion = instrucciones[indice]
            if mostrar_pasos:
                self.informar(
                    f"\n[MÓDULO {modulo}] Inicia procesamiento en paralelo de "
                    f"{self.formatear_instruccion(instruccion)}."
                )
            resultados[indice] = self.ejecutar_modulo(
                instruccion,
                modulo=modulo,
                actualizar_acumulador=(modulo == 1),
                mostrar_pasos=mostrar_pasos,
            )

        hilos = [threading.Thread(target=ejecutar_en_modulo, args=(i,)) for i in range(2)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        if self.on:
            self.avanzar_contador_programa(2)
        return tuple(resultados)

    def ejecutar_programa(self):
        print("=== EJECUCIÓN DEL PROGRAMA ===")
        self.contador_programa = 0
        self.on = True
        instrucciones_ejecutadas = 0

        while self.on and self.contador_programa < len(self.memoria.memoria):
            self.ciclo()
            instrucciones_ejecutadas += 1

        print(
            "=== PROGRAMA FINALIZADO "
            f"({instrucciones_ejecutadas} instrucciones ejecutadas; acumulador final = {self.acumulador:g}) ==="
        )
        return instrucciones_ejecutadas
