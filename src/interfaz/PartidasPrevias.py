import os
import sys

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.utils.GestionDAO import Conexion
from dateutil import parser
from PIL import Image
from Elementos.Boton import CTkButtonImagen
from ventana_partida import VentanaPartida
import locale

locale.setlocale(locale.LC_TIME, "")


class PartidasPrevias(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, fg_color="gray15")
        # ------------ + VAR LOCALES + ------------
        self.popup = None
        self.con = Conexion()

        # Cargamos los iconos
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."

        img = Image.open(f"{ruta}/_internal/icons/trash-bin.png")
        self.imagen_basura_cerrada = ctk.CTkImage(img, img, size=(30, 30))

        img = Image.open(f"{ruta}/_internal/icons/trash-bin_open.png")
        self.imagen_basura_abierta = ctk.CTkImage(img, img, size=(30, 30))

    def actualizar_registros(self):
        # De la BDD recuperamos las partidas
        partidas = self.con.recuperar_partidas()

        for registro in partidas:
            # Texto a mostrar en el registro
            fecha = parser.parse(registro[2])
            texto = f"{registro[1]}\t\t\t{fecha.strftime("%d de %B %Y, %H:%M")}"

            # Fondo que usará el Frame
            fondo_frame = "#283618"
            frame = ctk.CTkFrame(
                self,
                height=60,
                fg_color=fondo_frame,
                border_width=5,
            )

            # ------------ + GRID + ------------
            frame.grid_columnconfigure(0, weight=6, uniform="frame")
            frame.grid_columnconfigure(1, weight=1, uniform="frame")

            # ------------ + WIDGETS + ------------
            boton = ctk.CTkButton(
                frame,
                text=texto,
                font=("Montserrat", 18),
                command=lambda m=registro[0]: self.btn_partida(m),
                height=20,
                fg_color="#588157",
                hover_color="#3a5a40",
                corner_radius=0
            )
            btn_borrado = CTkButtonImagen(
                frame,
                imagen_inactivo=self.imagen_basura_cerrada,
                imagen_activo=self.imagen_basura_abierta,
                text="",
                command=lambda m=registro[0]: self.borrar_partida(m),
                height=30,
                fg_color="transparent",
                image=self.imagen_basura_cerrada,
                hover_color=fondo_frame,
            )

            # ------------ + COLOCACION + ------------
            boton.grid(column=0, row=0, sticky="nsew")
            btn_borrado.grid(column=1, row=0, sticky="nsew")

            frame.pack(fill="both", expand=True, pady=10)

    def btn_partida(self, idd):
        res = self.con.recuperar_movimientos(idd)
        if len(res) != 0:
            self.popup = VentanaPartida(res)
        else:
            box = CTkMessagebox(title="Información", message="Esta partida no tiene ningún movimiento registrado",
                                icon="info", option_1="Vale", width=600)
            box.grid_columnconfigure(1, weight=4)

    def borrar_partida(self, idd):
        self.con.cargarse_partidas(idd)
        self.vaciarse()
        self.actualizar_registros()

    def vaciarse(self):
        for child in self.winfo_children():
            child.destroy()
