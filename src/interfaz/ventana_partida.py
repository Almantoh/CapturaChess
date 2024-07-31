import os
import sys

import customtkinter as ctk
from PIL import Image
from dateutil import parser

from Ajedrez import crear_ajedrez, tablero_to_ctkImage
from ventana_imagen import VentanaImagen


class VentanaPartida(ctk.CTkToplevel):
    def __init__(self, res, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes('-topmost', True)
        
        # Cargamos los iconos
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."

        img = Image.open(f"{ruta}/_internal/icons/chess.png")
        imagen_tablero = ctk.CTkImage(img, img, size=(30, 30))

        self.title("Resultados")
        self.minsize(500, 500)
        # self.attributes('-topmost', True)

        # Icono
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
        self.iconbitmap(f'{ruta}/_internal/icons/icon.ico')

        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        # ------------ + GRID + ------------
        self.frame.grid_columnconfigure(0, weight=2, uniform="ven_partida")
        self.frame.grid_columnconfigure(1, weight=3, uniform="ven_partida")
        self.frame.grid_columnconfigure(2, weight=3, uniform="ven_partida")
        self.frame.grid_columnconfigure(3, weight=3, uniform="ven_partida")
        self.frame.grid_columnconfigure(4, weight=2, uniform="ven_partida")

        # ------------ + WIDGETS (CABECERAS) + ------------
        elemento = ctk.CTkLabel(self.frame, text="ID", height=40, font=('Arial', 14), bg_color="grey16")
        elemento.grid(row=0, column=0, sticky='ew', pady=2, padx=1)

        elemento = ctk.CTkLabel(self.frame, text="Ficha", height=40, font=('Arial', 14), bg_color="grey16")
        elemento.grid(row=0, column=1, sticky='ew', pady=2, padx=1)

        elemento = ctk.CTkLabel(self.frame, text="Movimiento", height=40, font=('Arial', 14), bg_color="grey16")
        elemento.grid(row=0, column=2, sticky='ew', pady=2, padx=1)

        elemento = ctk.CTkLabel(self.frame, text="Hora", height=40, font=('Arial', 14), bg_color="grey16")
        elemento.grid(row=0, column=3, sticky='ew', pady=2, padx=1)

        elemento = ctk.CTkLabel(self.frame, text="Tablero", height=40, font=('Arial', 14), bg_color="grey16")
        elemento.grid(row=0, column=4, sticky='ew', pady=2, padx=1)

        # Rellenar la tabla
        for i in range(len(res)):

            # Escribir el nº de jugada
            elemento = ctk.CTkLabel(self.frame, text=str(i+1), height=40, font=('Arial', 14), bg_color="grey25")
            elemento.grid(row=i + 1, column=0, sticky='ew', pady=1, padx=1)

            for j in range(1, len(res[i])):  # El FEN no queremos que lo muestre. Tampoco el ID
                texto = res[i][j]
                if j == 3:
                    fecha = parser.parse(res[i][j])
                    texto = fecha.strftime("%I:%M:%S")

                if j == 4:
                    elemento = ctk.CTkButton(
                        self.frame, 
                        text="", 
                        height=40,
                        fg_color="transparent",
                        image=imagen_tablero,
                        hover_color="grey10",
                        command=lambda m=res[i][j]: self.mostrarTablero(m)
                    )
                else:
                    elemento = ctk.CTkLabel(self.frame, text=texto, height=40, font=('Arial', 14), bg_color="grey25")

                elemento.grid(row=i + 1, column=j, sticky='ew', pady=1, padx=1)

    def mostrarTablero(self, m: str):
        tablero = crear_ajedrez(m)

        img = tablero_to_ctkImage(tablero, 600, 600)

        VentanaImagen(img, "Tablero")
