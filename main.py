import customtkinter as ctk
import tkinter as tk
import json
import os
from pathlib import Path

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ESTADO_FILE = "estado_materias.json"

class Estado:
    NO_CURSADA = "No cursada"
    REGULAR = "Regular"
    CURSANDO = "Cursando"
    APROBADA = "Aprobada"

    @staticmethod
    def color(estado):
        return {
            Estado.NO_CURSADA: "#cccccc",
            Estado.REGULAR: "#ffd966",
            Estado.CURSANDO: "#87CEEB",
            Estado.APROBADA: "#a4cba4"
        }[estado]

class Materia:
    def __init__(self, codigo, nombre, nivel, corr_reg=None, corr_apr=None):
        self.codigo = codigo
        self.nombre = nombre
        self.nivel = nivel
        self.correlativas_regular = corr_reg or []
        self.correlativas_aprobadas = corr_apr or []
        self.estado = Estado.NO_CURSADA
        self.boton = None
        self.disponible = False

    def actualizar_color(self):
        if self.boton:
            self.boton.configure(fg_color=Estado.color(self.estado), text_color="black")
            if self.disponible:
                self.boton.configure(border_width=3, border_color="#1E90FF")
            else:
                self.boton.configure(border_width=0)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Malla Universitaria")
        self.after(100, lambda: self.state("zoomed"))

        self.universidades = {
            "UTN": {
                "Facultad Regional Cordoba": {
                    "Ingeniería en Sistemas": self.crear_materias_sistemas(),
                    "Ingeniería Electrónica": self.crear_materias_electronica()
                },
            },
            "UNC": {
                "Facultad de Psicología": {
                    "Licenciatura en Psicologia": self.crear_materias_psicologia(),
                    "Profesorado en Psicologia": self.crear_materias_profesorado_psicologia()
                },
            },
        }

        self.frame_superior = ctk.CTkFrame(self)
        self.frame_superior.pack(side="top", fill="x", padx=10, pady=10)

        self.universidad_var = tk.StringVar()
        self.universidad_menu = ctk.CTkOptionMenu(
            self.frame_superior,
            values=list(self.universidades.keys()),
            variable=self.universidad_var,
            command=self.universidad_seleccionada
        )
        self.universidad_menu.pack(side="left", padx=10)
        self.universidad_var.set("")  # NO seleccion inicial

        self.facultad_var = tk.StringVar()
        self.facultad_menu = ctk.CTkOptionMenu(
            self.frame_superior,
            values=[],
            variable=self.facultad_var,
            command=self.facultad_seleccionada
        )
        self.facultad_menu.pack(side="left", padx=10)
        self.facultad_var.set("")  # NO seleccion inicial

        self.carrera_var = tk.StringVar()
        self.carrera_menu = ctk.CTkOptionMenu(
            self.frame_superior,
            values=[],
            variable=self.carrera_var,
            command=self.carrera_seleccionada
        )
        self.carrera_menu.pack(side="left", padx=10)
        self.carrera_var.set("")  # NO seleccion inicial

        self.frame_materias = ctk.CTkFrame(self)
        self.frame_materias.pack(side="top", fill="both", expand=True, padx=10, pady=(0,10))

        self.tabs_niveles = None

        self.cargar_estados()

        # NO llamar a universidad_seleccionada ni setear valores iniciales para que arranque vacío

    def universidad_seleccionada(self, universidad):
        if not universidad:
            self.facultad_menu.configure(values=[])
            self.facultad_var.set("")
            self.carrera_menu.configure(values=[])
            self.carrera_var.set("")
            self.limpiar_materias()
            return

        facultades = list(self.universidades[universidad].keys())
        self.facultad_menu.configure(values=facultades)
        self.facultad_var.set("")
        self.carrera_menu.configure(values=[])
        self.carrera_var.set("")
        self.limpiar_materias()

    def facultad_seleccionada(self, facultad):
        universidad = self.universidad_var.get()
        if not facultad or not universidad:
            self.carrera_menu.configure(values=[])
            self.carrera_var.set("")
            self.limpiar_materias()
            return

        carreras = list(self.universidades[universidad][facultad].keys())
        self.carrera_menu.configure(values=carreras)
        self.carrera_var.set("")
        self.limpiar_materias()

    def carrera_seleccionada(self, carrera):
        if not carrera:
            self.limpiar_materias()
            return

        universidad = self.universidad_var.get()
        facultad = self.facultad_var.get()
        if not universidad or not facultad:
            self.limpiar_materias()
            return

        self.limpiar_materias()

        materias = self.universidades[universidad][facultad][carrera]
        self.tabs_niveles = ctk.CTkTabview(self.frame_materias)
        self.tabs_niveles.pack(expand=True, fill="both")

        niveles = {}
        for m in materias:
            niveles.setdefault(m.nivel, []).append(m)

        for nivel in sorted(niveles):
            tab = self.tabs_niveles.add(f"Nivel {nivel}")
            frame = ctk.CTkFrame(tab)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            for m in niveles[nivel]:
                btn = ctk.CTkButton(frame, text=m.nombre, width=360, height=40,
                                    fg_color=Estado.color(m.estado), text_color="black",
                                    command=lambda mat=m: self.abrir_popup_estado(mat))
                btn.pack(pady=5)
                m.boton = btn

        self.actualizar_disponibilidad_actual()

    def limpiar_materias(self):
        for widget in self.frame_materias.winfo_children():
            widget.destroy()
        self.tabs_niveles = None

    def actualizar_disponibilidad_actual(self):
        universidad = self.universidad_var.get()
        facultad = self.facultad_var.get()
        carrera = self.carrera_var.get()
        if not (universidad and facultad and carrera):
            return
        materias = self.universidades[universidad][facultad][carrera]
        cod_a_materia = {m.codigo: m for m in materias}
        for m in materias:
            if not m.correlativas_regular and not m.correlativas_aprobadas:
                m.disponible = True
            else:
                aprobadas_ok = all(
                    cod_a_materia[cod].estado == Estado.APROBADA
                    for cod in m.correlativas_aprobadas
                )
                regular_ok = all(
                    cod_a_materia[cod].estado in [Estado.REGULAR, Estado.APROBADA]
                    for cod in m.correlativas_regular
                )
                m.disponible = aprobadas_ok and regular_ok
            m.actualizar_color()

    def abrir_popup_estado(self, materia):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Cambiar estado - {materia.nombre}")
        popup.geometry("300x180")
        popup.grab_set()

        label = ctk.CTkLabel(popup, text="Seleccione el estado:")
        label.pack(pady=10)

        estado_var = tk.StringVar(value=materia.estado)
        estados_posibles = [Estado.NO_CURSADA, Estado.REGULAR, Estado.CURSANDO, Estado.APROBADA]
        option_menu = ctk.CTkOptionMenu(popup, values=estados_posibles, variable=estado_var)
        option_menu.pack(pady=5)

        def confirmar():
            materia.estado = estado_var.get()
            materia.actualizar_color()
            self.actualizar_disponibilidad_actual()
            self.guardar_estados()
            popup.destroy()

        btn_confirmar = ctk.CTkButton(popup, text="Confirmar", command=confirmar)
        btn_confirmar.pack(pady=10)

    def guardar_estados(self):
        data = {}
        for universidad, facultades in self.universidades.items():
            data_uni = {}
            for facultad, carreras in facultades.items():
                data_facultad = {}
                for carrera, materias in carreras.items():
                    data_carrera = {str(m.codigo): m.estado for m in materias}
                    data_facultad[carrera] = data_carrera
                data_uni[facultad] = data_facultad
            data[universidad] = data_uni

        with open(ESTADO_FILE, "w") as f:
            json.dump(data, f)

    def cargar_estados(self):
        if os.path.exists(ESTADO_FILE):
            try:
                with open(ESTADO_FILE, "r") as f:
                    data = json.load(f)
                for universidad, facultades in data.items():
                    if universidad in self.universidades:
                        for facultad, carreras in facultades.items():
                            if facultad in self.universidades[universidad]:
                                for carrera, estados_carrera in carreras.items():
                                    if carrera in self.universidades[universidad][facultad]:
                                        materias = self.universidades[universidad][facultad][carrera]
                                        for m in materias:
                                            if str(m.codigo) in estados_carrera:
                                                m.estado = estados_carrera[str(m.codigo)]
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def crear_materias_psicologia(self):
        return [
            Materia(1, "Biologia", 1),
        ]

    def crear_materias_profesorado_psicologia(self):
        return [
            Materia(1, "Biologia", 1),
        ]

    def crear_materias_sistemas(self):
        return [
            Materia(1, "Análisis Matemático 1", 1),
            Materia(2, "Álgebra y Geometría Analítica", 1),
            Materia(3, "Física 1", 1),
            Materia(4, "Inglés 1", 1),
            Materia(5, "Lógica y Estructuras Discretas", 1),
            Materia(6, "Algoritmos y Estructuras de Datos", 1),
            Materia(7, "Arquitectura de Computadoras", 1),
            Materia(8, "Sistemas y Procesos de Negocio", 1),
            Materia(11, "Ingeniería y Sociedad", 1),
            Materia(9, "Análisis Matemático 2", 2, [1, 2]),
            Materia(10, "Física 2", 2, [1, 3]),
            Materia(12, "Inglés 2", 2, [4]),
            Materia(13, "Sintaxis y Semántica de los Lenguajes", 2, [5, 6]),
            Materia(14, "Paradigmas de Programación", 2, [5, 6]),
            Materia(15, "Sistemas Operativos", 2, [7]),
            Materia(16, "Análisis de Sistemas de Información", 2, [6, 8]),
            Materia(17, "Probabilidad y Estadísticas", 2, [1, 2]),
            Materia(18, "Economía", 3, [], [1, 2]),
            Materia(19, "Bases de Datos", 3, [13, 16], [5, 6]),
            Materia(20, "Desarrollo de Software", 3, [14, 16], [5, 6]),
            Materia(21, "Comunicación de Datos", 3, [], [3, 7]),
            Materia(22, "Análisis Numérico", 3, [9], [1, 2]),
            Materia(23, "Diseño de Sistemas de Información", 3, [14, 16], [4, 6, 8]),
            Materia(99, "Seminario Integrador (Analista)", 3, [16], [6, 8, 13, 14]),
            Materia(24, "Legislación", 4, [11]),
            Materia(25, "Ingeniería y Calidad de Software", 4, [19, 20, 23], [13, 14]),
            Materia(26, "Redes de Datos", 4, [15, 21]),
            Materia(27, "Investigación Operativa", 4, [17, 22]),
            Materia(28, "Simulación", 4, [17], [9]),
            Materia(29, "Tecnologías para la Automatización", 4, [10, 22], [9]),
            Materia(30, "Administración de Sistemas de Información", 4, [18, 23], [16]),
            Materia(31, "Inteligencia Artificial", 5, [28], [17, 22]),
            Materia(32, "Ciencia de Datos", 5, [28], [17, 19]),
            Materia(33, "Sistemas de Gestión", 5, [18, 27], [23]),
            Materia(34, "Gestión Gerencial", 5, [24, 30], [18]),
            Materia(35, "Seguridad en los Sistemas de Información", 5, [26, 30], [20, 21]),
            Materia(36, "Proyecto Final", 5, [25, 26, 30], [12, 20, 23]),
        ]

    def crear_materias_electronica(self):
        return [
            Materia(101, "Matemática Electrónica I", 1),
            Materia(102, "Física Electrónica", 1),
            Materia(103, "Programación Básica", 1),
            Materia(104, "Circuitos I", 2, [101, 102]),
            Materia(105, "Electrónica Digital", 2, [103]),
            Materia(106, "Instrumentación", 3, [104]),
            Materia(107, "Microcontroladores", 4, [105]),
            Materia(108, "Proyecto Electrónica", 5, [106, 107])
        ]

class AppMejorada(App):
    """Interfaz con persistencia segura y explicación de correlatividades."""

    VERSION_DATOS = 2

    def __init__(self):
        self.archivo_estado = self.ruta_estado()
        super().__init__()
        self.title("Gestor de Correlatividades")
        self.minsize(900, 600)

        self.resumen_var = tk.StringVar(value="Elegí una universidad, facultad y carrera para ver tu avance.")
        self.resumen = ctk.CTkLabel(
            self.frame_superior,
            textvariable=self.resumen_var,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.resumen.pack(side="left", padx=(16, 10), fill="x", expand=True)

    @staticmethod
    def ruta_estado():
        """Guarda el progreso junto al perfil de Windows, sin depender del directorio de inicio."""
        base = os.environ.get("LOCALAPPDATA")
        if base:
            carpeta = Path(base) / "GestorCorrelatividades"
        else:
            carpeta = Path.home() / ".gestor_correlatividades"
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta / "estado_materias.json"

    def carrera_seleccionada(self, carrera):
        super().carrera_seleccionada(carrera)
        if carrera:
            self.actualizar_disponibilidad_actual()

    def actualizar_disponibilidad_actual(self):
        universidad = self.universidad_var.get()
        facultad = self.facultad_var.get()
        carrera = self.carrera_var.get()
        if not (universidad and facultad and carrera):
            return

        materias = self.universidades[universidad][facultad][carrera]
        por_codigo = {materia.codigo: materia for materia in materias}
        for materia in materias:
            faltantes = self.correlativas_faltantes(materia, por_codigo)
            materia.disponible = not faltantes
            materia.actualizar_color()

        if hasattr(self, "resumen_var"):
            aprobadas = sum(m.estado == Estado.APROBADA for m in materias)
            disponibles = sum(m.disponible and m.estado != Estado.APROBADA for m in materias)
            self.resumen_var.set(
                f"{carrera}  |  {aprobadas}/{len(materias)} aprobadas  |  {disponibles} disponibles"
            )

    @staticmethod
    def correlativas_faltantes(materia, por_codigo):
        faltantes = []
        for codigo in materia.correlativas_regular:
            correlativa = por_codigo.get(codigo)
            if correlativa is None:
                faltantes.append(f"Regularizar la correlativa {codigo}")
            elif correlativa.estado not in (Estado.REGULAR, Estado.APROBADA):
                faltantes.append(f"Regularizar: {correlativa.nombre}")
        for codigo in materia.correlativas_aprobadas:
            correlativa = por_codigo.get(codigo)
            if correlativa is None:
                faltantes.append(f"Aprobar la correlativa {codigo}")
            elif correlativa.estado != Estado.APROBADA:
                faltantes.append(f"Aprobar: {correlativa.nombre}")
        return faltantes

    def abrir_popup_estado(self, materia):
        universidad = self.universidad_var.get()
        facultad = self.facultad_var.get()
        carrera = self.carrera_var.get()
        materias = self.universidades[universidad][facultad][carrera]
        faltantes = self.correlativas_faltantes(materia, {m.codigo: m for m in materias})

        popup = ctk.CTkToplevel(self)
        popup.title(f"Estado de {materia.nombre}")
        popup.geometry("480x310")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text=materia.nombre,
            wraplength=420,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(padx=20, pady=(20, 8))

        mensaje = "Disponible para cursar." if not faltantes else "Para habilitarla falta:\n• " + "\n• ".join(faltantes)
        ctk.CTkLabel(popup, text=mensaje, justify="left", wraplength=420).pack(padx=20, pady=8, anchor="w")

        estado_var = tk.StringVar(value=materia.estado)
        ctk.CTkOptionMenu(
            popup,
            values=[Estado.NO_CURSADA, Estado.CURSANDO, Estado.REGULAR, Estado.APROBADA],
            variable=estado_var,
        ).pack(pady=10)

        def confirmar():
            materia.estado = estado_var.get()
            self.actualizar_disponibilidad_actual()
            self.guardar_estados()
            popup.destroy()

        ctk.CTkButton(popup, text="Guardar estado", command=confirmar).pack(pady=(4, 18))

    def guardar_estados(self):
        carreras = {}
        for universidad, facultades in self.universidades.items():
            for facultad, oferta in facultades.items():
                for carrera, materias in oferta.items():
                    clave = " | ".join((universidad, facultad, carrera))
                    carreras[clave] = {str(m.codigo): m.estado for m in materias}

        contenido = {"version": self.VERSION_DATOS, "carreras": carreras}
        temporal = self.archivo_estado.with_suffix(".tmp")
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, ensure_ascii=False, indent=2)
        temporal.replace(self.archivo_estado)

    def cargar_estados(self):
        # Conserva el formato anterior si el usuario ya tenía progreso guardado.
        origen = self.archivo_estado
        legado = Path.cwd() / ESTADO_FILE
        if not origen.exists() and legado.exists():
            origen = legado
        if not origen.exists():
            return

        try:
            with origen.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError):
            return

        if "carreras" in datos:
            for universidad, facultades in self.universidades.items():
                for facultad, oferta in facultades.items():
                    for carrera, materias in oferta.items():
                        clave = " | ".join((universidad, facultad, carrera))
                        self.aplicar_estados(materias, datos["carreras"].get(clave, {}))
            return

        for universidad, facultades in datos.items():
            for facultad, carreras in facultades.items():
                for carrera, estados in carreras.items():
                    materias = self.universidades.get(universidad, {}).get(facultad, {}).get(carrera)
                    if materias:
                        self.aplicar_estados(materias, estados)

    @staticmethod
    def aplicar_estados(materias, estados):
        estados_validos = {Estado.NO_CURSADA, Estado.CURSANDO, Estado.REGULAR, Estado.APROBADA}
        for materia in materias:
            estado = estados.get(str(materia.codigo))
            if estado in estados_validos:
                materia.estado = estado

if __name__ == "__main__":
    app = AppMejorada()
    app.mainloop()
