import os
import sys

import customtkinter as ctk
from PIL import Image

from Confiugracion import Configuracion
from Grabar import Grabar
from PartidasPrevias import PartidasPrevias
from src.utils.GestionConfiguracion import crear_configuracion
from src.utils.GestionDAO import Conexion


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1100x700")
        self.title("CapturaChess")
        self.minsize(1000, 400)

        # Icono
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."

        # Cargamos la fuente del logo
        ctk.FontManager.load_font(f'{ruta}/_internal/fuentes/Blackcastlemf.ttf')

        self.iconbitmap(f'{ruta}/_internal/icons/icon.ico')

        # La imagen pija
        img = Image.open(f"{ruta}/_internal/icons/pijada.png")
        img_pija = ctk.CTkImage(img, img, size=(260, 38))
        img = img.rotate(180)
        img_pija_inversa = ctk.CTkImage(img, img, size=(260, 38))

        # Interfaz de la ventana
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        # ------------ + GRID + ------------

        self.grid_columnconfigure(0, weight=26, uniform="main")
        self.grid_columnconfigure(1, weight=1, uniform="main")
        self.grid_columnconfigure(2, weight=80, uniform="main")
        self.grid_columnconfigure(3, weight=1, uniform="main")

        self.grid_rowconfigure(0, weight=1, uniform="main")
        self.grid_rowconfigure(1, weight=70, uniform="main")
        self.grid_rowconfigure(2, weight=1, uniform="main")

        # **********************************************
        # *                  MARGEN                    *
        # **********************************************

        self.margen = ctk.CTkFrame(self, fg_color="gray20")
        self.margen.grid(row=0, column=0, sticky="nsew", rowspan=3)

        # ------------ + GRID + ------------
        self.margen.grid_columnconfigure(0, weight=1, uniform="main")
        self.margen.grid_columnconfigure(1, weight=8, uniform="main")
        self.margen.grid_columnconfigure(2, weight=1, uniform="main")

        self.margen.grid_rowconfigure(0, weight=5, uniform="main")
        self.margen.grid_rowconfigure(1, weight=4, uniform="main")
        self.margen.grid_rowconfigure(2, weight=7, uniform="main")
        self.margen.grid_rowconfigure(3, weight=3, uniform="main")
        self.margen.grid_rowconfigure(4, weight=1, uniform="main")
        self.margen.grid_rowconfigure(5, weight=3, uniform="main")
        self.margen.grid_rowconfigure(6, weight=1, uniform="main")
        self.margen.grid_rowconfigure(7, weight=3, uniform="main")
        self.margen.grid_rowconfigure(8, weight=10, uniform="main")
        self.margen.grid_rowconfigure(9, weight=3, uniform="main")
        self.margen.grid_rowconfigure(10, weight=4, uniform="main")

        # ------------ + WIDGETS + ------------

        self.imagen_inversa = ctk.CTkLabel(self.margen, text="", image=img_pija_inversa)
        self.titulo = ctk.CTkLabel(self.margen, text="CapturaChess", font=("Blackcastlemf", 50))
        self.imagen = ctk.CTkLabel(self.margen, text="", image=img_pija)
        self.btn_grabar = ctk.CTkButton(
            self.margen,
            text="Grabar",
            font=("Montserrat", 16),
            command=lambda: self.button_click_cambiar_pestanna(self.btn_grabar),
            fg_color="#14375e"
        )
        self.btn_configuracion = ctk.CTkButton(
            self.margen,
            text="Configuración",
            font=("Montserrat", 16),
            command=lambda: self.button_click_cambiar_pestanna(self.btn_configuracion)
        )
        self.btn_partidasPrevias = ctk.CTkButton(
            self.margen, text="Partidas Previas",
            font=("Montserrat", 16),
            command=lambda: self.button_click_cambiar_pestanna(self.btn_partidasPrevias)
        )

        # Lista de botones
        self.botones = (self.btn_grabar, self.btn_configuracion, self.btn_partidasPrevias)

        self.salir = ctk.CTkButton(
            self.margen,
            text="Salir",
            font=("Montserrat", 16),
            command=self.button_click_salir
        )

        # ------------ + COLOCAR + ------------

        self.imagen_inversa.grid(row=0, column=0, sticky="sew", columnspan=3)
        self.titulo.grid(row=1, column=0, sticky="nsew", columnspan=3)
        self.imagen.grid(row=2, column=0, sticky="new", columnspan=3)
        self.btn_grabar.grid(row=3, column=1, sticky="nsew")
        self.btn_configuracion.grid(row=5, column=1, sticky="nsew")
        self.btn_partidasPrevias.grid(row=7, column=1, sticky="nsew")
        self.salir.grid(row=9, column=1, sticky="nsew")

        # *******************************
        # *        CONFIGURACION        *
        # *******************************
        crear_configuracion()

        # *******************************
        # *          PANELES            *
        # *******************************

        # Creamos los paneles de las demás ventanas
        self.PP_configuracion = Configuracion(self)
        self.PP_grabar = Grabar(self)
        self.PP_partidas_previas = PartidasPrevias(self)

        # Seleccionamos el panel que se muestra por defecto y lo mostramos
        self.panel = self.PP_grabar
        self.panel.grid(row=1, column=2, sticky="nsew")

    def button_click_salir(self):
        self.salir_de_la_app()

    def al_cerrar(self):
        self.salir_de_la_app()

    def salir_de_la_app(self):
        # Cerramos la conexión
        Conexion().cerrar_conexion()

        # Si por algun casual el hilo de OpenCV sigue funcionando, le damos la señal de que termine
        if self.PP_grabar.ventana_tablero is not None:
            self.PP_grabar.ventana_tablero.quedarse = False

        # Se destruye la ventana
        self.destroy()

    def button_click_cambiar_pestanna(self, boton: ctk.CTkButton):
        # El boton que representa la pestaña actual se pone con un azul mas oscuro y el resto regresa a su estado base
        for btn in self.botones:
            if btn is boton:
                btn.configure(fg_color="#14375e")
            else:
                btn.configure(fg_color="#1f538d")

        # Ocultamos todos los componentes del panel principal
        self.panel.grid_forget()

        # En funcion del botón elegido, se asigna un nuevo panel
        match boton:
            case self.btn_grabar:
                self.panel = self.PP_grabar
            case self.btn_configuracion:
                self.panel = self.PP_configuracion
            case self.btn_partidasPrevias:
                # Recargamos los datos de las partidas antes de mostrarlas
                self.PP_partidas_previas.vaciarse()
                self.PP_partidas_previas.actualizar_registros()

                self.panel = self.PP_partidas_previas

        # Ponemos el nuevo panel de nuevo
        self.panel.grid(row=1, column=2, sticky="nsew")
