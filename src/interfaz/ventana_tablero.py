import os
import sys

import customtkinter as ctk
import numpy as np

from PIL import Image

from Ajedrez import tablero_to_ctkImage
from ChessMio import BoardMio
from src.utils.GestionConfiguracion import obtener_parametro
from tablero import sacar_tablero, set_ajedrez_viejo
import threading
import cv2 as cv
from CTkMessagebox import CTkMessagebox

from ventana_imagen import VentanaImagen


class VenanaTablero(ctk.CTkToplevel):
    def __init__(self, camara, id_bdd: int, anchura: int = 700, altura: int = 700, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Tablero - Pulsa espacio para indicar movimiento")
        # self.attributes('-topmost', True)

        # Icono
        ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
        self.iconbitmap(f'{ruta}/_internal/icons/icon.ico')

        self.minsize(anchura - 50, altura - 50)

        # ------------ + VAR LOCALES + ------------

        self.camara: cv.VideoCapture = camara
        self.anchura: int = anchura
        self.altura: int = altura
        self.id_bdd: int = id_bdd
        self.tablero = None
        self.ventanas_mostrar: dict[str, VentanaImagen] = dict()
        self.quedarse: bool = True
        self.mostrar_intermedios: bool = False

        # ------------ + EVENTOS + ------------

        self.event_add("<<movimiento>>", "<ButtonRelease-2>", "<space>")
        self.bind("<<movimiento>>", self.evento_teclado)
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        self.geometry(f"{self.anchura}x{self.altura}")

        # ------------ + MOSTRAR CÁMARA + ------------
        self.mostrar_intermedios: bool = obtener_parametro('IA', 'pasos_intermedios')

        # Hilo para mostrar lo que saca la cámara encargada de OpenCV
        t1 = threading.Thread(target=self.mostrar_camara, args=(camara, obtener_parametro('IA', 'frame_escalada')))
        t1.start()

        # ------------ + WIDGETS + ------------
        # El label donde se mostrará el tablero
        self.label = ctk.CTkLabel(self, text="")
        self.label.pack()

        # Visualizamos el tablero
        self.visualizar()

    def mostrar_ventanas(self, imagenes: list[str, np.ndarray]):
        # Recorremos cada imagen y la mostramos si no existe. Si existe actualizamos la imágen
        for titulo, imagen in imagenes:
            ventana = self.ventanas_mostrar.get(titulo)
            if ventana is None:
                ventana = VentanaImagen(self.openCV_a_Tkinker(imagen), titulo)
                self.ventanas_mostrar.update({titulo: ventana})
            elif ventana.winfo_exists():
                ventana.actualizarImagen(self.openCV_a_Tkinker(imagen))

    def evento_teclado(self, event):
        if self.camara is not None and self.camara.isOpened():
            self.reconocer_tablero()

    def reconocer_tablero(self):
        # Cogemos un frame
        frame2 = self.camara.read()[1]

        # Sacamos el tablero
        sacar_tablero(self.camara, frame2, self, False, False, True)

    def visualizar(self, tablero: BoardMio = BoardMio("8/8/8/8/8/8/8/8")):
        """
        Dado un tablero, muestra en el label la imágen del mismo

        :param tablero: El tablero
        """
        self.tablero = tablero

        # Creamos la imagen compatible con CustomTkinker
        img = tablero_to_ctkImage(tablero, self.anchura, self.altura)

        # Asignamos la imágen
        self.label.configure(image=img)

    def al_cerrar(self):
        self.quedarse = False
        for ventana in self.ventanas_mostrar.values():
            ventana.destroy()

        set_ajedrez_viejo(None)
        self.ventanas_mostrar = dict()

        self.destroy()

    def mostrar_camara(self, cam: cv.VideoCapture, escalada_frame):
        self.quedarse = True
        # Se queda ahí esperando a que le llegue la señal de morirse
        while self.quedarse:
            res, frame = cam.read()
            if res:
                frame = cv.resize(frame, None, fx=escalada_frame, fy=escalada_frame)  # 0.6
                cv.imshow("Camara", frame)
            cv.waitKey(5)

        cam.release()
        cv.destroyAllWindows()

    def openCV_a_Tkinker(self, frame: np.ndarray, alto: int = -1, ancho: int = -1):

        # Obtenemos el alto y el ancho de la imágen
        if alto == -1:
            alto = frame.shape[1]
        if ancho == -1:
            ancho = frame.shape[0]

        # Lo pasamos a imagen de customTkinker
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ctk.CTkImage(frame, frame, size=(alto, ancho))

        return frame

    # GET y SET
    def get_id_bdd(self) -> int:
        return self.id_bdd

    def set_id_bdd(self, value: int):
        self.id_bdd = value

    def get_quedarse(self) -> bool:
        return self.quedarse

    def set_quedarse(self, value: bool):
        self.quedarse = value

    def get_ventanas_mostrar(self) -> dict[str, VentanaImagen]:
        return self.ventanas_mostrar

    def set_ventanas_mostrar(self, value: dict[str, VentanaImagen]):
        self.ventanas_mostrar = value
