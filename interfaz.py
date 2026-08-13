import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from memoria import Memoria
from cpu import CPU

# ---------------------------------------------------------------------------
# Paleta y constantes visuales
# ---------------------------------------------------------------------------
BG = "#0f172a"          # fondo general (azul muy oscuro)
PANEL_BG = "#1e293b"     # paneles
BOX_BG = "#1e293b"       # cajas del diagrama (inactivas)
BOX_BORDER = "#475569"
BOX_BORDER_ACTIVE = "#f97316"
TEXT_LIGHT = "#e2e8f0"
TEXT_MUTED = "#94a3b8"
ACCENT_1 = "#38bdf8"     # celeste: módulo 1
ACCENT_2 = "#a78bfa"     # violeta: módulo 2
OK_COLOR = "#22c55e"
ERR_COLOR = "#ef4444"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BOX_TITLE = ("Segoe UI", 10, "bold")
FONT_BOX_VALUE = ("Consolas", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_LOG = ("Consolas", 9)

OPERACIONES_ARITMETICAS = ["ADD", "SUB", "MUL", "DIV"]
OPERACIONES_DUAL = OPERACIONES_ARITMETICAS + ["HALT"]
OPERACIONES_SINGLE = OPERACIONES_ARITMETICAS + ["LOAD", "STORE"] + ["HALT"]


class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador CPU — Arquitectura de Von Neumann")
        self.root.configure(bg=BG)
        self.root.geometry("1180x720")
        self.root.minsize(1040, 640)

        self.memoria = Memoria()
        self.cpu = CPU(self.memoria)

        # estado de animación / control manual
        self.animando = False
        self.modo_manual = tk.BooleanVar(value=False)
        self.manual_paso_actual = None   # None -> 'FETCH' -> 'DECODE' -> 'EXECUTE' -> None
        self.instr_pendiente = None
        self.velocidad = tk.IntVar(value=2)  # 1 lento, 2 normal, 3 rápido

        self._construir_layout()
        self._dibujar_diagrama()
        self._log("Sistema listo. Configura una operación y presiona Ejecutar.", "info")

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir_layout(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=PANEL_BG)
        style.configure("TLabel", background=PANEL_BG, foreground=TEXT_LIGHT, font=FONT_NORMAL)
        style.configure("Title.TLabel", background=BG, foreground=TEXT_LIGHT, font=FONT_TITLE)
        style.configure("Sub.TLabel", background=BG, foreground=TEXT_MUTED, font=FONT_NORMAL)
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TRadiobutton", background=PANEL_BG, foreground=TEXT_LIGHT, font=FONT_NORMAL)
        style.configure("TCheckbutton", background=PANEL_BG, foreground=TEXT_LIGHT, font=FONT_NORMAL)
        style.configure("TCombobox", padding=4)
        style.configure("Treeview", background="#0b1220", fieldbackground="#0b1220",
                         foreground=TEXT_LIGHT, rowheight=24, font=FONT_LOG)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#334155")])

        # Encabezado
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=16, pady=(12, 4))
        ttk.Label(header, text="Simulador de CPU — Arquitectura de Von Neumann", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Fetch → Decode → Execute, con visualización del flujo de datos entre Memoria, ALU y Registros",
                  style="Sub.TLabel").pack(anchor="w")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # --------- Columna izquierda: diagrama + memoria ---------
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(0, weight=3)
        left.rowconfigure(1, weight=2)
        left.columnconfigure(0, weight=1)

        diag_frame = tk.Frame(left, bg=PANEL_BG, highlightbackground=BOX_BORDER, highlightthickness=1)
        diag_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.canvas = tk.Canvas(diag_frame, bg="#0b1220", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<Configure>", lambda e: self._dibujar_diagrama())

        mem_frame = tk.Frame(left, bg=PANEL_BG, highlightbackground=BOX_BORDER, highlightthickness=1)
        mem_frame.grid(row=1, column=0, sticky="nsew")
        ttk.Label(mem_frame, text="Memoria (instrucciones almacenadas)", font=FONT_BOX_TITLE,
                  background=PANEL_BG, foreground=TEXT_LIGHT).pack(anchor="w", padx=8, pady=(6, 0))
        cols = ("dir", "op", "a", "b")
        self.tree = ttk.Treeview(mem_frame, columns=cols, show="headings", height=6)
        for c, wd, t in zip(cols, (50, 90, 90, 90), ("Dir.", "Operación", "A", "B")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=wd, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.tag_configure("activa", background="#7c2d12", foreground="#fed7aa")

        # --------- Columna derecha: controles + log ---------
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ctrl = tk.Frame(right, bg=PANEL_BG, highlightbackground=BOX_BORDER, highlightthickness=1)
        ctrl.pack(fill="x", pady=(0, 8))
        self._construir_controles(ctrl)

        log_frame = tk.Frame(right, bg=PANEL_BG, highlightbackground=BOX_BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True)
        ttk.Label(log_frame, text="Registro de ejecución", font=FONT_BOX_TITLE,
                  background=PANEL_BG, foreground=TEXT_LIGHT).pack(anchor="w", padx=8, pady=(6, 0))
        log_container = tk.Frame(log_frame, bg=PANEL_BG)
        log_container.pack(fill="both", expand=True, padx=8, pady=8)
        scroll = ttk.Scrollbar(log_container)
        scroll.pack(side="right", fill="y")
        self.log_text = tk.Text(log_container, bg="#0b1220", fg=TEXT_LIGHT, font=FONT_LOG,
                                 wrap="word", yscrollcommand=scroll.set, state="disabled",
                                 borderwidth=0, highlightthickness=0)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.log_text.yview)
        self.log_text.tag_configure("info", foreground=TEXT_MUTED)
        self.log_text.tag_configure("ok", foreground=OK_COLOR)
        self.log_text.tag_configure("err", foreground=ERR_COLOR)
        self.log_text.tag_configure("m1", foreground=ACCENT_1)
        self.log_text.tag_configure("m2", foreground=ACCENT_2)

    def _construir_controles(self, parent):
        pad = {"padx": 8, "pady": 4}
        ttk.Label(parent, text="Panel de control", font=FONT_BOX_TITLE,
                  background=PANEL_BG, foreground=TEXT_LIGHT).grid(row=0, column=0, columnspan=4, sticky="w", **pad)

        ttk.Label(parent, text="Operaciones simultáneas:").grid(row=1, column=0, sticky="w", **pad)
        self.cantidad_var = tk.IntVar(value=1)
        ttk.Radiobutton(parent, text="1", variable=self.cantidad_var, value=1,
                         command=self._actualizar_visibilidad).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(parent, text="2 (paralelo)", variable=self.cantidad_var, value=2,
                         command=self._actualizar_visibilidad).grid(row=1, column=2, sticky="w")

        # Operación 1
        ttk.Label(parent, text="Operación 1:").grid(row=2, column=0, sticky="w", **pad)
        self.op1 = ttk.Combobox(parent, values=OPERACIONES_SINGLE, state="readonly", width=8)
        self.op1.set("ADD")
        self.op1.grid(row=2, column=1, sticky="w")
        self.op1.bind("<<ComboboxSelected>>", lambda e: self._toggle_operandos())
        self.lbl_a1 = ttk.Label(parent, text="A:")
        self.lbl_a1.grid(row=2, column=2, sticky="e")
        self.a1 = ttk.Entry(parent, width=8)
        self.a1.insert(0, "10")
        self.a1.grid(row=2, column=3, sticky="w")
        self.lbl_b1 = ttk.Label(parent, text="B:")
        self.lbl_b1.grid(row=3, column=2, sticky="e")
        self.b1 = ttk.Entry(parent, width=8)
        self.b1.insert(0, "5")
        self.b1.grid(row=3, column=3, sticky="w")

        # Operación 2 (solo visible en modo paralelo) — sin LOAD/STORE: el
        # camino paralelo de dos ALUs no pasa por AC ni memoria de datos.
        self.lbl_op2 = ttk.Label(parent, text="Operación 2:")
        self.lbl_op2.grid(row=4, column=0, sticky="w", **pad)
        self.op2 = ttk.Combobox(parent, values=OPERACIONES_DUAL, state="readonly", width=8)
        self.op2.set("MUL")
        self.op2.grid(row=4, column=1, sticky="w")
        self.lbl_a2 = ttk.Label(parent, text="C:")
        self.lbl_a2.grid(row=4, column=2, sticky="e")
        self.a2 = ttk.Entry(parent, width=8)
        self.a2.insert(0, "4")
        self.a2.grid(row=4, column=3, sticky="w")
        self.lbl_b2 = ttk.Label(parent, text="D:")
        self.lbl_b2.grid(row=5, column=2, sticky="e")
        self.b2 = ttk.Entry(parent, width=8)
        self.b2.insert(0, "3")
        self.b2.grid(row=5, column=3, sticky="w")

        # Velocidad
        ttk.Label(parent, text="Velocidad animación:").grid(row=6, column=0, sticky="w", **pad)
        vel_frame = tk.Frame(parent, bg=PANEL_BG)
        vel_frame.grid(row=6, column=1, columnspan=3, sticky="w")
        for val, txt in ((1, "Lenta"), (2, "Normal"), (3, "Rápida")):
            ttk.Radiobutton(vel_frame, text=txt, variable=self.velocidad, value=val).pack(side="left", padx=2)

        # Modo manual
        self.chk_manual = ttk.Checkbutton(parent, text="Modo paso a paso manual (solo con 1 operación)",
                                           variable=self.modo_manual, command=self._actualizar_visibilidad)
        self.chk_manual.grid(row=7, column=0, columnspan=4, sticky="w", **pad)

        # Botones
        btn_frame = tk.Frame(parent, bg=PANEL_BG)
        btn_frame.grid(row=8, column=0, columnspan=4, sticky="ew", padx=8, pady=(8, 10))
        btn_frame.columnconfigure((0, 1, 2), weight=1)
        self.btn_ejecutar = ttk.Button(btn_frame, text="▶ Ejecutar", command=self._on_ejecutar)
        self.btn_ejecutar.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_paso = ttk.Button(btn_frame, text="Siguiente paso", command=self._on_paso_manual, state="disabled")
        self.btn_paso.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_reset = ttk.Button(btn_frame, text="⟲ Reiniciar", command=self._on_reset)
        self.btn_reset.grid(row=0, column=2, sticky="ew", padx=2)

        self._actualizar_visibilidad()

    def _actualizar_visibilidad(self):
        dual = self.cantidad_var.get() == 2
        widgets2 = (self.lbl_op2, self.op2, self.lbl_a2, self.a2, self.lbl_b2, self.b2)
        for w in widgets2:
            if dual:
                w.grid()
            else:
                w.grid_remove()

        # LOAD/STORE solo tienen sentido en modo de una operación: el camino
        # paralelo (ejecutar_dos) trabaja directo con las ALUs, sin pasar
        # por AC ni por la memoria de datos.
        if dual:
            self.op1.config(values=OPERACIONES_DUAL)
            if self.op1.get() not in OPERACIONES_DUAL:
                self.op1.set("ADD")
        else:
            self.op1.config(values=OPERACIONES_SINGLE)

        # el modo manual solo aplica a una sola operación
        if dual:
            self.modo_manual.set(False)
            self.chk_manual.state(["disabled"])
        else:
            self.chk_manual.state(["!disabled"])
        self._toggle_operandos()

    def _toggle_operandos(self):
        op = self.op1.get()
        if op == "HALT":
            self.a1.config(state="disabled")
            self.b1.config(state="disabled")
            self.lbl_a1.config(text="A:")
            self.lbl_b1.config(text="B:")
        elif op in ("LOAD", "STORE"):
            # Solo necesitan una dirección de memoria de datos.
            self.a1.config(state="normal")
            self.b1.delete(0, tk.END)
            self.b1.config(state="disabled")
            self.lbl_a1.config(text="Dirección:")
            self.lbl_b1.config(text="")
        else:
            self.a1.config(state="normal")
            self.b1.config(state="normal")
            self.lbl_a1.config(text="A:")
            self.lbl_b1.config(text="B:")

    # ------------------------------------------------------------------
    # Diagrama de arquitectura (canvas)
    # ------------------------------------------------------------------
    def _dibujar_diagrama(self):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 640)
        h = max(self.canvas.winfo_height(), 420)

        self.coords = {}

        mem = (20, h * 0.30, 130, h * 0.50)
        datos = (20, h * 0.66, 130, h * 0.86)
        mar = (w * 0.20, h * 0.06, w * 0.315, h * 0.22)
        mbr = (w * 0.20, h * 0.28, w * 0.315, h * 0.44)
        pc = (w * 0.36, h * 0.06, w * 0.50, h * 0.22)
        ir = (w * 0.36, h * 0.28, w * 0.50, h * 0.44)
        alu1 = (w * 0.66, h * 0.06, w * 0.86, h * 0.28)
        alu2 = (w * 0.66, h * 0.62, w * 0.86, h * 0.84)
        ac1 = (w * 0.36, h * 0.50, w * 0.50, h * 0.64)
        ac2 = (w * 0.36, h * 0.68, w * 0.50, h * 0.82)

        self.coords["mem"] = self._caja(mem, "MEMORIA (programa)", "")
        self.coords["datos"] = self._caja(datos, "MEMORIA DE DATOS", "vacío")
        self.coords["mar"] = self._caja(mar, "MAR (dirección)", "—")
        self.coords["mbr"] = self._caja(mbr, "MBR (dato leído)", "—")
        self.coords["pc"] = self._caja(pc, "PC (Contador)", "0")
        self.coords["ir"] = self._caja(ir, "IR (Instrucción)", "—")
        self.coords["alu1"] = self._caja(alu1, "ALU 1", "—", color=ACCENT_1)
        self.coords["alu2"] = self._caja(alu2, "ALU 2", "—", color=ACCENT_2)
        self.coords["ac1"] = self._caja(ac1, "RESULTADO 1 (AC)", "—", color=ACCENT_1)
        self.coords["ac2"] = self._caja(ac2, "RESULTADO 2", "—", color=ACCENT_2)

        # Bus de fetch: Memoria -> MAR -> MBR -> IR (en vez de un salto directo)
        self._linea_guia(mem, mar)
        self._linea_guia(mar, mbr)
        self._linea_guia(mbr, ir)
        self._linea_guia(pc, mar)
        # Bus de datos: AC <-> Memoria de datos (LOAD / STORE)
        self._linea_guia(ac1, datos)
        # Bus hacia las ALUs
        self._linea_guia(ir, alu1)
        self._linea_guia(ir, alu2)
        self._linea_guia(alu1, ac1)
        self._linea_guia(alu2, ac2)

        # MAR/MBR son registros de la CPU (su "ventana" hacia la memoria),
        # así que quedan dentro del recuadro de CPU; mem y datos quedan
        # afuera, como la memoria principal en una arquitectura Von Neumann real.
        cpu_box = (w * 0.17, h * 0.02, w * 0.92, h * 0.90)
        self.canvas.create_rectangle(*cpu_box, outline=BOX_BORDER, dash=(4, 3))
        self.canvas.create_text(cpu_box[0] + 10, cpu_box[1] + 10, text="CPU", anchor="nw",
                                 fill=TEXT_MUTED, font=FONT_BOX_TITLE)

    def _mid(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def _edge(self, box, side):
        x1, y1, x2, y2 = box
        cy = (y1 + y2) / 2
        cx = (x1 + x2) / 2
        return {"right": (x2, cy), "left": (x1, cy), "top": (cx, y1), "bottom": (cx, y2)}[side]

    def _linea_guia(self, box_a, box_b):
        pa = self._mid(box_a)
        pb = self._mid(box_b)
        self.canvas.create_line(*pa, *pb, fill="#1f2a3d", width=2)

    def _caja(self, box, titulo, valor, color=None):
        rect = self.canvas.create_rectangle(*box, fill=BOX_BG, outline=BOX_BORDER, width=2)
        x1, y1, x2, y2 = box
        self.canvas.create_text((x1 + x2) / 2, y1 + 14, text=titulo, fill=TEXT_MUTED, font=FONT_BOX_TITLE)
        value_id = self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 + 8, text=valor,
                                            fill=color or TEXT_LIGHT, font=FONT_BOX_VALUE)
        return {"box": box, "rect": rect, "value": value_id}

    def _set_valor(self, clave, texto):
        self.canvas.itemconfig(self.coords[clave]["value"], text=texto)

    def _actualizar_datos_display(self):
        if self.cpu.memoria_datos:
            texto = ", ".join(f"{k}:{v:g}" for k, v in sorted(self.cpu.memoria_datos.items()))
        else:
            texto = "vacío"
        self._set_valor("datos", texto)

    def _resaltar(self, clave, activo=True, color=None):
        info = self.coords[clave]
        if activo:
            self.canvas.itemconfig(info["rect"], outline=color or BOX_BORDER_ACTIVE, width=3)
        else:
            self.canvas.itemconfig(info["rect"], outline=BOX_BORDER, width=2)

    # ------------------------------------------------------------------
    # Animación de flujo de datos (paquete viajando entre cajas)
    # ------------------------------------------------------------------
    def _delay_base(self):
        return {1: 650, 2: 350, 3: 160}[self.velocidad.get()]

    def _animar_flujo(self, clave_origen, clave_destino, color, on_done=None):
        box_o = self.coords[clave_origen]["box"]
        box_d = self.coords[clave_destino]["box"]
        if box_o[0] < box_d[0]:
            p1 = self._edge(box_o, "right")
            p2 = self._edge(box_d, "left")
        else:
            p1 = self._edge(box_o, "left")
            p2 = self._edge(box_d, "right")

        r = 6
        dot = self.canvas.create_oval(p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r, fill=color, outline="")
        pasos = 18
        dx = (p2[0] - p1[0]) / pasos
        dy = (p2[1] - p1[1]) / pasos
        delay = max(8, self._delay_base() // pasos)

        def paso(i=0):
            if i >= pasos:
                self.canvas.delete(dot)
                if on_done:
                    on_done()
                return
            self.canvas.move(dot, dx, dy)
            self.root.after(delay, lambda: paso(i + 1))

        paso()

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------
    def _log(self, mensaje, tag="info"):
        self.log_text.config(state="normal")
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{hora}] {mensaje}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ------------------------------------------------------------------
    # Validación y construcción de instrucciones
    # ------------------------------------------------------------------
    def _leer_instruccion(self, combo_op, entry_a, entry_b):
        op = combo_op.get().upper().strip()
        if not op:
            raise ValueError("Selecciona una operación.")
        if op == "HALT":
            return (op, 0.0, 0.0)
        if op in ("LOAD", "STORE"):
            try:
                direccion = int(entry_a.get())
            except ValueError:
                raise ValueError("La dirección debe ser un número entero.")
            return (op, direccion, 0.0)
        try:
            a = float(entry_a.get())
            b = float(entry_b.get())
        except ValueError:
            raise ValueError("Los operandos deben ser números.")
        if op == "DIV" and b == 0:
            raise ValueError("No se puede dividir entre 0.")
        return (op, a, b)

    def _refrescar_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, instr in enumerate(self.memoria.memoria):
            self.tree.insert("", "end", iid=str(i), values=(i, instr[0], instr[1], instr[2]))

    def _marcar_fila_activa(self, direccion):
        for iid in self.tree.get_children():
            self.tree.item(iid, tags=())
        if str(direccion) in self.tree.get_children():
            self.tree.item(str(direccion), tags=("activa",))
            self.tree.see(str(direccion))

    # ------------------------------------------------------------------
    # Botones principales
    # ------------------------------------------------------------------
    def _bloquear_controles(self, bloquear=True):
        estado = "disabled" if bloquear else "normal"
        self.btn_ejecutar.config(state=estado)
        self.btn_reset.config(state=estado)

    def _on_reset(self):
        if self.animando:
            return
        self.memoria.reiniciar()
        self.cpu.pc = 0
        self.cpu.ac = 0
        self.cpu.on = True
        self.cpu.mar = None
        self.cpu.mbr = None
        self.cpu.memoria_datos.clear()
        self.manual_paso_actual = None
        self.instr_pendiente = None
        self.btn_paso.config(text="Siguiente paso", state="disabled")
        self.btn_ejecutar.config(state="normal")
        self._refrescar_tree()
        self._set_valor("pc", "0")
        self._set_valor("mar", "—")
        self._set_valor("mbr", "—")
        self._set_valor("ir", "—")
        self._set_valor("alu1", "—")
        self._set_valor("alu2", "—")
        self._set_valor("ac1", "—")
        self._set_valor("ac2", "—")
        self._actualizar_datos_display()
        for k in ("mem", "datos", "mar", "mbr", "pc", "ir", "alu1", "alu2", "ac1", "ac2"):
            self._resaltar(k, False)
        self._log("Simulador reiniciado.", "ok")

    def _on_ejecutar(self):
        if self.animando:
            return
        if not self.cpu.on:
            messagebox.showinfo("CPU detenida", "La CPU está detenida. Presiona Reiniciar para continuar.")
            return

        dual = self.cantidad_var.get() == 2
        try:
            instr1 = self._leer_instruccion(self.op1, self.a1, self.b1)
            instr2 = self._leer_instruccion(self.op2, self.a2, self.b2) if dual else None
        except ValueError as e:
            messagebox.showerror("Entrada inválida", str(e))
            return

        if dual:
            self.memoria.guardar(instr1)
            self.memoria.guardar(instr2)
            self._refrescar_tree()
            self._ejecutar_dual(instr1, instr2)
        else:
            self.memoria.guardar(instr1)
            self._refrescar_tree()
            if self.modo_manual.get():
                self._preparar_manual(instr1)
            else:
                self._ejecutar_single_auto(instr1)

    # ------------------------------------------------------------------
    # Ejecución con UNA operación — modo automático
    # ------------------------------------------------------------------
    def _ejecutar_single_auto(self, instr):
        self._bloquear_controles(True)
        self.animando = True
        direccion = self.cpu.pc

        def fase_fetch_a_mar():
            self._resaltar("mem", True)
            self._resaltar("pc", True)
            self._marcar_fila_activa(direccion)
            self._log(f"FETCH → PC={direccion} se copia al MAR", "info")
            self._animar_flujo("mem", "mar", TEXT_LIGHT, on_done=fase_fetch_a_mbr)

        def fase_fetch_a_mbr():
            self._set_valor("mar", str(direccion))
            self._resaltar("mar", True)
            self._log(f"MAR = {direccion} → se lee memoria[{direccion}]", "info")
            self.root.after(self._delay_base() // 3,
                            lambda: self._animar_flujo("mar", "mbr", TEXT_LIGHT, on_done=fase_fetch_a_ir))

        def fase_fetch_a_ir():
            texto_instr = f"{instr[0]} {instr[1]:g} {instr[2]:g}" if instr[0] != "HALT" else "HALT"
            self._set_valor("mbr", texto_instr)
            self._resaltar("mem", False)
            self._resaltar("mar", False)
            self._resaltar("mbr", True)
            self._log(f"MBR ← dato leído de memoria: {instr}", "info")
            self.root.after(self._delay_base() // 3,
                            lambda: self._animar_flujo("mbr", "ir", TEXT_LIGHT, on_done=fase_fetch_fin))

        def fase_fetch_fin():
            self._resaltar("mbr", False)
            self._resaltar("ir", True)
            self._set_valor("ir", f"{instr[0]} {instr[1]:g} {instr[2]:g}" if instr[0] != "HALT" else "HALT")
            self._log("IR ← MBR: instrucción lista para decodificar", "info")
            self.root.after(self._delay_base() // 2, fase_decode)

        def fase_decode():
            self._set_valor("pc", str(direccion))
            op = instr[0]
            self._log(f"DECODE → operación detectada: {op}", "info")
            if op == "HALT":
                self.cpu.on = False
                self._log("HALT → la CPU se detiene.", "err")
                self._resaltar("ir", False)
                self._resaltar("pc", False)
                self._finalizar_ejecucion()
                return
            self.root.after(self._delay_base() // 2, fase_execute_router)

        def fase_execute_router():
            op = instr[0]
            if op == "LOAD":
                fase_load()
            elif op == "STORE":
                fase_store()
            else:
                fase_execute()

        def fase_load():
            self._resaltar("ir", False)
            self._resaltar("datos", True)
            direccion_datos = int(instr[1])
            self._log(f"LOAD → leyendo memoria_datos[{direccion_datos}]", "m1")

            def hacia_ac():
                valor = self.cpu.memoria_datos.get(direccion_datos, 0)
                self.cpu.ac = valor
                self._resaltar("datos", False)
                self._resaltar("ac1", True)
                self._set_valor("ac1", f"{valor:g}")
                self._log(f"LOAD → AC = memoria_datos[{direccion_datos}] = {valor:g}", "ok")
                self.cpu.pc += 1
                self._finalizar_ejecucion()

            self.root.after(self._delay_base() // 3,
                            lambda: self._animar_flujo("datos", "ac1", ACCENT_1, on_done=hacia_ac))

        def fase_store():
            self._resaltar("ir", False)
            self._resaltar("ac1", True)
            direccion_datos = int(instr[1])
            self._log(f"STORE → guardando AC en memoria_datos[{direccion_datos}]", "m1")

            def hacia_datos():
                self.cpu.memoria_datos[direccion_datos] = self.cpu.ac
                self._resaltar("ac1", False)
                self._resaltar("datos", True)
                self._actualizar_datos_display()
                self._log(f"STORE → memoria_datos[{direccion_datos}] = AC ({self.cpu.ac:g})", "ok")
                self.cpu.pc += 1
                self._finalizar_ejecucion()

            self.root.after(self._delay_base() // 3,
                            lambda: self._animar_flujo("ac1", "datos", ACCENT_1, on_done=hacia_datos))

        def fase_execute():
            self._resaltar("ir", False)
            self._resaltar("alu1", True)
            self._log("EXECUTE → enviando operandos a ALU 1", "m1")
            self._animar_flujo("ir", "alu1", ACCENT_1, on_done=fase_execute_calcular)

        def fase_execute_calcular():
            op, a, b = instr
            funcion = self.cpu.operaciones1.get(op)
            resultado = funcion(a, b)
            self.cpu.ac = resultado
            self._set_valor("alu1", f"{a:g} {op} {b:g}")
            self._log(f"ALU 1: {a:g} {op} {b:g} = {resultado:g}", "m1")
            self.root.after(self._delay_base() // 3, lambda: self._animar_flujo(
                "alu1", "ac1", ACCENT_1, on_done=lambda: fase_final(resultado)))

        def fase_final(resultado):
            self._resaltar("alu1", False)
            self._resaltar("ac1", True)
            self._set_valor("ac1", f"{resultado:g}")
            self._log(f"AC actualizado con el resultado: {resultado:g}", "ok")
            self.cpu.pc += 1
            self._finalizar_ejecucion()

        fase_fetch_a_mar()

    def _finalizar_ejecucion(self):
        self.animando = False
        self._bloquear_controles(False)

    # ------------------------------------------------------------------
    # Ejecución con UNA operación — modo manual paso a paso
    # ------------------------------------------------------------------
    def _preparar_manual(self, instr):
        self.instr_pendiente = instr
        self.manual_paso_actual = "FETCH"
        self.btn_ejecutar.config(state="disabled")
        self.btn_paso.config(text="1) FETCH", state="normal")
        self._marcar_fila_activa(self.cpu.pc)
        self._log("Instrucción cargada en memoria. Modo manual activo: presiona 'Siguiente paso'.", "info")

    def _on_paso_manual(self):
        if self.animando or self.instr_pendiente is None:
            return
        self.animando = True
        self.btn_paso.config(state="disabled")
        instr = self.instr_pendiente
        direccion = self.cpu.pc

        if self.manual_paso_actual == "FETCH":
            self._resaltar("mem", True)
            self._log(f"FETCH  → leyendo dirección {direccion}: {instr}", "info")

            def fin():
                self._resaltar("mem", False)
                self._resaltar("ir", True)
                self._set_valor("ir", f"{instr[0]} {instr[1]:g} {instr[2]:g}" if instr[0] != "HALT" else "HALT")
                self._set_valor("pc", str(direccion))
                self.manual_paso_actual = "DECODE"
                self.btn_paso.config(text="2) DECODE", state="normal")
                self.animando = False

            self._animar_flujo("mem", "ir", TEXT_LIGHT, on_done=fin)

        elif self.manual_paso_actual == "DECODE":
            self._resaltar("pc", True)
            op = instr[0]
            self._log(f"DECODE → operación detectada: {op}", "info")
            self.root.after(self._delay_base() // 2, lambda: self._decode_manual_fin(instr))

        elif self.manual_paso_actual == "EXECUTE":
            self._resaltar("ir", False)
            self._resaltar("alu1", True)
            self._log("EXECUTE → enviando operandos a ALU 1", "m1")

            def calcular():
                op, a, b = instr
                funcion = self.cpu.operaciones1.get(op)
                resultado = funcion(a, b)
                self.cpu.ac = resultado
                self._set_valor("alu1", f"{a:g} {op} {b:g}")
                self._log(f"ALU 1: {a:g} {op} {b:g} = {resultado:g}", "m1")

                def hacia_ac():
                    self._resaltar("alu1", False)
                    self._resaltar("ac1", True)
                    self._set_valor("ac1", f"{resultado:g}")
                    self._log(f"AC actualizado con el resultado: {resultado:g}", "ok")
                    self.cpu.pc += 1
                    self._resaltar("pc", False)
                    self.manual_paso_actual = None
                    self.instr_pendiente = None
                    self.btn_paso.config(text="Siguiente paso", state="disabled")
                    self.btn_ejecutar.config(state="normal")
                    self.animando = False

                self.root.after(self._delay_base() // 3, lambda: self._animar_flujo("alu1", "ac1", ACCENT_1, on_done=hacia_ac))

            self._animar_flujo("ir", "alu1", ACCENT_1, on_done=calcular)

    def _decode_manual_fin(self, instr):
        op = instr[0]
        if op == "HALT":
            self.cpu.on = False
            self._log("HALT → la CPU se detiene.", "err")
            self._resaltar("ir", False)
            self._resaltar("pc", False)
            self.manual_paso_actual = None
            self.instr_pendiente = None
            self.btn_paso.config(text="Siguiente paso", state="disabled")
            self.btn_ejecutar.config(state="normal")
            self.animando = False
            return
        self.manual_paso_actual = "EXECUTE"
        self.btn_paso.config(text="3) EXECUTE", state="normal")
        self.animando = False

    # ------------------------------------------------------------------
    # Ejecución con DOS operaciones en paralelo (ALU1 + ALU2)
    # ------------------------------------------------------------------
    def _ejecutar_dual(self, instr1, instr2):
        self._bloquear_controles(True)
        self.animando = True
        estado = {"m1": False, "m2": False}

        def hacer_listo(clave):
            estado[clave] = True
            if estado["m1"] and estado["m2"]:
                self._resaltar("mem", False)
                self._resaltar("ir", False)
                self.cpu.pc += 2
                self._log("Ambas operaciones completadas en paralelo.", "ok")
                self._finalizar_ejecucion()

        def modulo_run(instr, clave_alu, clave_ac, ops_dict, tag, color, nombre, clave_estado):
            self._log(f"[{nombre}] FETCH → {instr}", tag)
            self._resaltar("mem", True)

            def tras_fetch():
                self._resaltar("ir", True)
                self._set_valor("ir", f"{instr[0]} (multi)")
                op = instr[0]
                self._log(f"[{nombre}] DECODE → operación: {op}", tag)
                if op == "HALT":
                    self._log(f"[{nombre}] HALT recibido.", "err")
                    hacer_listo(clave_estado)
                    return
                self._resaltar(clave_alu, True)
                self._log(f"[{nombre}] EXECUTE → enviando operandos a {nombre}", tag)

                def calcular():
                    a, b = instr[1], instr[2]
                    funcion = ops_dict.get(op)
                    if op == "DIV" and b == 0:
                        self._log(f"[{nombre}] Error: división entre 0.", "err")
                        hacer_listo(clave_estado)
                        return
                    resultado = funcion(a, b)
                    self._set_valor(clave_alu, f"{a:g} {op} {b:g}")
                    self._log(f"[{nombre}]: {a:g} {op} {b:g} = {resultado:g}", tag)

                    def hacia_ac():
                        self._resaltar(clave_alu, False)
                        self._resaltar(clave_ac, True)
                        self._set_valor(clave_ac, f"{resultado:g}")
                        self._log(f"[{nombre}] resultado guardado: {resultado:g}", "ok")
                        hacer_listo(clave_estado)

                    self.root.after(self._delay_base() // 3,
                                    lambda: self._animar_flujo(clave_alu, clave_ac, color, on_done=hacia_ac))

                self._animar_flujo("ir", clave_alu, color, on_done=calcular)

            self._animar_flujo("mem", "ir", color, on_done=tras_fetch)

        # Se lanzan casi simultáneamente para simular paralelismo real de dos ALUs
        self.root.after(0, lambda: modulo_run(instr1, "alu1", "ac1", self.cpu.operaciones1, "m1", ACCENT_1, "ALU 1", "m1"))
        self.root.after(60, lambda: modulo_run(instr2, "alu2", "ac2", self.cpu.operaciones2, "m2", ACCENT_2, "ALU 2", "m2"))


def main():
    root = tk.Tk()
    SimuladorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()