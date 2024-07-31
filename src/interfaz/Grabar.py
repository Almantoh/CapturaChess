import configparser
import datetime
import os
import sys
import tkinter as tk

import customtkinter as ctk
import cv2 as cv
from CTkMessagebox import CTkMessagebox
from PIL import Image

from Elementos.Boton import CTkButtonImagen
from src.utils.CamarasDispositivo import conseguir_camaras_dispositivo
from src.utils.GestionConfiguracion import obtener_parametro, guardar_camara
from src.utils.GestionDAO import Conexion
from ventana_tablero import VenanaTablero


class Grabar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, fg_color="gray15")

        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
        img = Image.open(f"{ruta}/_internal/icons/ask.png")
        img_clara = ctk.CTkImage(img, img, size=(50, 50))

        img = Image.open(f"{ruta}/_internal/icons/ask_oscuro.png")
        img_oscuro = ctk.CTkImage(img, img, size=(50, 50))

        # ------------ + VAR LOCALES + ------------

        self.ventana_tablero = None
        self.camara = None

        self.confuracion = configparser.ConfigParser()

        self.radio_var = tk.IntVar(value=0)

        # ------------ + PROPIEDADES + ------------

        ventana_tablero = property(self.get_ventana_tablero, self.set_ventana_tablero)

        # ------------ + GRID + ------------

        self.grid_columnconfigure(0, weight=5, uniform="grabar")
        self.grid_columnconfigure(1, weight=10, uniform="grabar")
        self.grid_columnconfigure(2, weight=20, uniform="grabar")
        self.grid_columnconfigure(3, weight=5, uniform="grabar")

        self.grid_rowconfigure(0, weight=10, uniform="grabar")
        self.grid_rowconfigure(1, weight=5, uniform="grabar")
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=5, uniform="grabar")
        self.grid_rowconfigure(4, weight=10, uniform="grabar")
        self.grid_rowconfigure(5, weight=10, uniform="grabar")
        self.grid_rowconfigure(6, weight=3, uniform="grabar")
        self.grid_rowconfigure(7, weight=5, uniform="grabar")
        self.grid_rowconfigure(8, weight=3, uniform="grabar")

        # ------------ + WIDGETS + ------------

        self.btn_info = CTkButtonImagen(
            self,
            text="",
            command=self.mostrar_informacion,
            image=img_clara,
            imagen_inactivo=img_clara,
            imagen_activo=img_oscuro,
            fg_color="transparent",
            hover_color="grey15"
        )

        self.camaras_dispositivo = conseguir_camaras_dispositivo()

        self.rbt_Camara = ctk.CTkRadioButton(self, text="Camara IP", variable=self.radio_var, value=1,
                                             command=self.radiobutton_event, )
        self.rbt_USBCamaras = ctk.CTkRadioButton(self, text="Camara USB", variable=self.radio_var, value=0,
                                                 command=self.radiobutton_event)

        self.urlCamara = ctk.CTkEntry(self, placeholder_text="http://192.168.0.1:8000/video", state=ctk.DISABLED)
        self.USBcamaras = ctk.CTkOptionMenu(self, values=list(self.camaras_dispositivo.keys()),
                                            dynamic_resizing=False, command=self.guardar_camara)

        self.lbl_test = ctk.CTkLabel(self, text="")
        self.test = ctk.CTkButton(self, text="Test", font=("Montserrat", 16), command=self.btn_test)

        self.lbl_nombrePartida = ctk.CTkLabel(self, text="Nombre de la partida")
        self.nombrePartida = ctk.CTkEntry(self, placeholder_text="Nombre de la partida")

        self.iniciar = ctk.CTkButton(self, text="Iniciar", font=("Montserrat", 16), command=self.boton_iniciar,
                                     width=400, height=50)

        # ------------ + COLOCACION + ------------

        self.btn_info.grid(row=0, column=3, sticky="ne", padx=15, pady=10)

        self.rbt_Camara.grid(row=1, column=1, sticky="new")
        self.rbt_USBCamaras.grid(row=3, column=1, sticky="new")

        self.urlCamara.grid(row=1, column=2, sticky="new")
        self.USBcamaras.grid(row=3, column=2, sticky="new")

        self.lbl_test.grid(row=4, column=2, sticky="nsew")
        self.test.grid(row=4, column=2, sticky="n")

        self.lbl_nombrePartida.grid(row=5, column=1, sticky="new")
        self.nombrePartida.grid(row=5, column=2, sticky="new")
        self.iniciar.grid(row=7, column=0, columnspan=4)

        # ------------ + CONFIGURACION + ------------

        # Comprobamos que tenga alguna camara USB disponible en el equipo
        if len(self.camaras_dispositivo) != 0:

            # Cogemos la camara guardada en preferencias
            camara = obtener_parametro("CAMARA", "camara")

            # Buscamos a ver cual dispositivo se correponde con esa camara. Si no es ninguno se pone a 0
            result = [nombre for nombre, numero in self.camaras_dispositivo.items() if numero == camara]

            if len(result) == 0:
                self.USBcamaras.set(list(self.camaras_dispositivo.keys())[0])
            else:
                self.USBcamaras.set(str(result[0]))
        else:
            self.rbt_USBCamaras.configure(state=ctk.DISABLED)
            self.radio_var.set(1)
            self.radiobutton_event()

    def mostrar_informacion(self):
        # Mostrar mensajes de información
        box = CTkMessagebox(
            title="Guía Rapida Grabación",
            message="\n  1. Mantén la cámara lo más cercana posible al tablero\n"
                    "  2. La cámara debe de tener una vista cenital del tablero\n"
                    "  3. Se debe tratar de que esté lo más recta posible recta respecto al tablero; sin que las líneas "
                    "formen diagonales\n"
                    "  4. Ten el tablero en un área limpia, con buena iluminación natural para evitar interferencias.\n\n"
                    "  Si falla en el detectar el tablero prueba a mover ligeramente la cámara.\n"
                    "  Si falla en el detectar la ficha prueba a moverla y/o rotarla un poco.\n\n"
                    "  Para registrar la posición inicial del tablero pulsa 'espacio' y se te pedirá la confirmación.",
                icon="info", option_1="Sigue...", width=1500)

        box.grid_columnconfigure(1, weight=4)

        if box.get() == "Sigue...":
            # Mensaje infromativo
            box = CTkMessagebox(
                title="Importante",
                message="Asegúrate de que las fichas blancas se encuentren en la parte inferior y que la posición "
                        "original de los reyes esté en el lado derecho de la ventana de 'Camara'.",
                icon="info", option_1="Entiendo", width=1000)
            box.grid_columnconfigure(1, weight=4)

    def guardar_camara(self, choice):
        guardar_camara(self.camaras_dispositivo.get(choice))

    def radiobutton_event(self):
        if self.radio_var.get() == 1:
            self.urlCamara.configure(state=ctk.NORMAL)
            self.USBcamaras.configure(state=ctk.DISABLED)
        else:
            self.urlCamara.configure(state=ctk.DISABLED)
            self.USBcamaras.configure(state=ctk.NORMAL)

    def btn_test(self, mensajeria: bool = True):
        # En dependencia de los radio button, elige una camara
        if self.radio_var.get() == 0:
            cam = self.USBcamaras.get()
            cam = self.camaras_dispositivo.get(cam)
        else:
            cam = self.urlCamara.get()

        # Si no es un numero (que ha elegido una URL) y es string vacio salta error
        if not str(cam).isnumeric() and cam == "":
            CTkMessagebox(title="Información", message="La URL de la cámara no puede ser nula.",
                          icon="cancel", option_1="Vale")
        else:
            try:
                self.camara: cv.VideoCapture = cv.VideoCapture(cam)
            except Exception as e:
                print(str(e))

            # Informar al usuario sobre el resultado de la cámara
            if self.camara is not None and self.camara.isOpened():
                if self.camara.read()[0] and mensajeria:
                    CTkMessagebox(title="Información", message="La cámara funciona correctamente.",
                                  icon="check", option_1="Bien")
                elif mensajeria:
                    CTkMessagebox(title="Información", message="Se ha podido acceder a la cámara pero no se pudo "
                                                               "obtener su grabación",
                                  icon="cancel", option_1="Vale")
            else:
                CTkMessagebox(title="Información", message="No se pudo acceder a la cámara.",
                              icon="cancel", option_1="Vale")

    def boton_iniciar(self):
        # Comprueba que no este ya iniciada una partida
        if self.ventana_tablero is None or not self.ventana_tablero.winfo_exists():

            # Pone la camara a None por si ya estaba iniciada y la recarga
            if self.camara is not None and self.camara.isOpened():
                self.camara.release()

            self.camara = None
            self.btn_test(False)

            if self.camara is not None and self.camara.isOpened():
                # Le da nombre a la partida
                nombre = self.nombrePartida.get()
                if nombre == "":
                    nombre = "Vacio"

                # Inserta la partida
                conexion = Conexion()
                idd = conexion.insertar_partidas((nombre, str(datetime.datetime.now())))

                # Muestra al usuario la ventana del tablero
                self.ventana_tablero: VenanaTablero = VenanaTablero(self.camara, idd)
        else:
            self.ventana_tablero.focus()

    def get_ventana_tablero(self) -> VenanaTablero:
        return self.ventana_tablero

    def set_ventana_tablero(self, value: VenanaTablero):
        self.ventana_tablero = value
