import os
import sys

import customtkinter as ctk


class VentanaImagen(ctk.CTkToplevel):
    def __init__(self, imagen: ctk.CTkImage, titulo: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        anchura, altura = imagen.cget("size")

        self.title(titulo)
        self.minsize(anchura, altura)
        self.geometry(f"{anchura}x{altura}")

        # self.attributes('-topmost', True)

        # Icono
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
        self.iconbitmap(f'{ruta}/_internal/icons/icon.ico')

        # ------------ + VAR LOCALES + ------------
        self.label = ctk.CTkLabel(self, text="", image=imagen)
        self.label.pack()

    def actualizarImagen(self, imagen: ctk.CTkImage):
        self.label.configure(image=imagen)
