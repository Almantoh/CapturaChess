import customtkinter as ctk
import configparser

from CTkMessagebox import CTkMessagebox
from src.utils.GestionConfiguracion import cargar_configuracion, guardar_Configuracion_IA


class Configuracion(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, fg_color="gray15")

        # Cargamos los tamaños disponibles para el escalado de los frames y de las casillas
        tamannos = ["100%", "90%", "80%", "70%", "60%", "50%", "40%", "30%", "20%"]
        tamannos2 = ["x1.0", "x1.5", "x2.0", "x2.5", "x3.0", "x3.5", "x4.0"]

        # ------------ + VAR LOCALES + ------------
        self.imagen_escalada_var = ctk.StringVar(self, value=tamannos[0])
        self.resize_var = ctk.StringVar(value=tamannos2[0])
        self.distancia_pixeles_var = ctk.StringVar(value="80")
        self.int_UpperCanny = ctk.StringVar(value="190")
        self.int_lowCanny = ctk.StringVar(value="50")

        self.config = configparser.ConfigParser()

        # ------------ + GRID + ------------
        self.grid_columnconfigure(0, weight=1, uniform="configuracion")
        self.grid_columnconfigure(1, weight=44, uniform="configuracion")
        self.grid_columnconfigure(2, weight=10, uniform="configuracion")
        self.grid_columnconfigure(3, weight=5, uniform="configuracion")

        self.grid_rowconfigure(0, weight=1, uniform="configuracion")  # Margen Superior
        self.grid_rowconfigure(1, weight=1, uniform="configuracion")
        self.grid_rowconfigure(2, weight=3, uniform="configuracion")
        self.grid_rowconfigure(3, weight=1, uniform="configuracion")
        self.grid_rowconfigure(4, weight=3, uniform="configuracion")
        self.grid_rowconfigure(5, weight=1, uniform="configuracion")
        self.grid_rowconfigure(6, weight=4, uniform="configuracion")
        self.grid_rowconfigure(7, weight=1, uniform="configuracion")
        self.grid_rowconfigure(8, weight=2, uniform="configuracion")
        self.grid_rowconfigure(9, weight=1, uniform="configuracion")
        self.grid_rowconfigure(10, weight=6, uniform="configuracion")
        self.grid_rowconfigure(11, weight=1, uniform="configuracion")  #
        self.grid_rowconfigure(12, weight=3, uniform="configuracion")  # Margen inferior
        self.grid_rowconfigure(13, weight=2, uniform="configuracion")  # Botón
        self.grid_rowconfigure(14, weight=1, uniform="configuracion")  # Margen inferior

        # ------------ + WIDGETS + ------------
        self.lbl_escaladas = ctk.CTkLabel(self, text="Escalado del frame a mostrar", font=(None, 14))
        self.escaladas = ctk.CTkOptionMenu(
            self, values=tamannos,
            dynamic_resizing=False,
            variable=self.imagen_escalada_var
        )
        self.lbl_infoescaladas = ctk.CTkLabel(
            self,
            text='Cuando inicias una partida, aparece una ventana con la imagen que capta de la cámara. Por defecto se '
                 'muestra a la resolución que graba la cámara, en la mayoría de los casos es conveniente ajustar a que '
                 'porcentaje lo quieres rescaldar para que no se vea muy grande',
            font=("Arial", 10),
            text_color="gray",
            wraplength=520
        )

        self.lbl_resize = ctk.CTkLabel(self, text="Tamaño de las imágenes de las fichas", font=(None, 14))
        self.resize = ctk.CTkOptionMenu(self, values=tamannos2, dynamic_resizing=False, variable=self.resize_var)
        self.lbl_infoResize = ctk.CTkLabel(
            self,
            text='Cuando la cámara no graba con suficiente resolución o el ajedrez se encuentra a una gran distancia '
                 'del objetivo, los detalles de las piezas no se pueden apreciar bien y puede desencadenar en fallos. '
                 'en la detección de las mismas. Mediante algoritmos de OpenCV puedes rescaldar la imagen para aumentar'
                 ' la resolución y facilitar el reconocimiento. A su vez, si escalas demasiado, puede llevarte a malos '
                 'resultados y ser contraproducente',
            font=("Arial", 10),
            text_color="gray",
            wraplength=520
        )

        self.lbl_distanciaPixeles = ctk.CTkLabel(self, text="Espacio mínimo entre casillas", font=(None, 14))
        self.distanciaPixeles = ctk.CTkEntry(
            self,
            placeholder_text="80",
            width=50,
            textvariable=self.distancia_pixeles_var
        )
        self.px = ctk.CTkLabel(self, text="px")
        self.lbl_infodistanciaPixelese = ctk.CTkLabel(
            self,
            text='La aplicación espera una distancia mínima en px entre cada casilla del tablero de ajedrez. '
                 'Ajustándolo demasiado bajo puede causar que los falsos positivos crezcan. A su vez aumentándolo '
                 'demasiado, puede causar que ya no detecte tableros al no cumplir ninguna intersección con la '
                 'distancia mínima.\n\nCon la resolución de su dispositivo en mano, juegue con este valor hasta que '
                 'consiga el resultado que espera.\nPor defecto es 80.',
            font=("Arial", 10),
            text_color="gray",
            wraplength=520,
        )

        self.lbl_mostrar_pasos = ctk.CTkLabel(self, text="Mostrar pasos intermedios", font=(None, 14))
        self.mostrar_pasos = ctk.CTkSwitch(self, text="", switch_width=44, switch_height=22)
        self.lbl_infomostrar_pasos = ctk.CTkLabel(
            self,
            text='Después de cada detección de tablero, muestra los pasos intermedios y procedimientos que el algoritmo'
                 ' ha llevado a cabo para reconocer el tablero',
            font=("Arial", 10),
            text_color="gray",
            wraplength=520
        )

        self.lbl_lowCanny = ctk.CTkLabel(self, text="Lower y Upper del Canny", font=(None, 14))
        self.lower = ctk.CTkEntry(
            self,
            placeholder_text="50",
            width=50,
            textvariable=self.int_lowCanny
        )
        self.upper = ctk.CTkEntry(
            self,
            placeholder_text="150",
            width=50,
            textvariable=self.int_UpperCanny
        )
        self.lbl_infoCanny = ctk.CTkLabel(
            self,
            text="Ajusta los valores que va a recibir la función Canny, encargada de encontrar las líneas del tablero "
                 "mediante los contrastes entre las casillas.\nEl 'Upper' (el segundo) es el encargado de filtrar los "
                 "puntos con gran contraste. Cuando más alto, más exigente va a ser para encontrar la línea.\nEl "
                 "'Lower' (el primero) es el encargado de unir los diferentes puntos. Cuanto más bajo, más líneas "
                 "conexas van a aparecer, mientras que cuanto más alto sea menos cohesionadas estarán las líneas.\n\n"
                 "Juega con estos valores con conciencia. Por norma general, si no se encuentra el tablero hay que "
                 "saber si es por exceso de ruido en la imagen (donde habría que aumentar los números) o porque no "
                 "detecta bien las intersecciones del tablero (donde habría de disminuir los valores)",
            font=("Arial", 10),
            text_color="gray",
            wraplength=520,
        )

        self.lbl_reconocer_piezas = ctk.CTkLabel(self, text="Uso de Gamma o Brillo para reconocer las piezas",
                                                 font=(None, 14))
        self.reconocer_piezas = ctk.CTkOptionMenu(self, values=["Brillo + Contraste", "Gamma"], dynamic_resizing=False)
        self.lbl_infoReconocer_piezas = ctk.CTkLabel(
            self,
            text="Aunque el brillo y Contraste suele funcionar correctamente en la mayoría de ocasiones, a veces "
                 "cuando hay demasiada luz artificial conviene usar Gamma.",
            font=("Arial", 10),
            text_color="gray",
            wraplength=520,
        )

        self.iniciar = ctk.CTkButton(self, text="Guardar Configuración", font=("Montserrat", 16),
                                     command=self.btn_salvar, width=400, height=50)

        # ------------ + COLOCAR + ------------
        self.lbl_escaladas.grid(row=1, column=1, sticky="sew")
        self.escaladas.grid(row=1, column=2, sticky="new", rowspan=2, pady=10)
        self.lbl_infoescaladas.grid(row=2, column=1, sticky="new")

        self.lbl_resize.grid(row=3, column=1, sticky="sew")
        self.resize.grid(row=3, column=2, sticky="new", rowspan=2)
        self.lbl_infoResize.grid(row=4, column=1, sticky="new")

        self.lbl_distanciaPixeles.grid(row=5, column=1, sticky="new")
        self.distanciaPixeles.grid(row=5, column=2, sticky="n", rowspan=2)
        self.px.grid(row=5, column=2, sticky="ne", rowspan=2)
        self.lbl_infodistanciaPixelese.grid(row=6, column=1, sticky="new")

        self.lbl_mostrar_pasos.grid(row=7, column=1, sticky="new")
        self.mostrar_pasos.grid(row=7, column=2, sticky="new", padx=30)
        self.lbl_infomostrar_pasos.grid(row=8, column=1, sticky="new")

        self.lbl_lowCanny.grid(row=9, column=1, sticky="new")
        self.lower.grid(row=9, column=2, sticky="nw")
        self.upper.grid(row=9, column=2, sticky="ne")
        self.lbl_infoCanny.grid(row=10, column=1, sticky="new")

        self.lbl_reconocer_piezas.grid(row=11, column=1, sticky="new")
        self.reconocer_piezas.grid(row=11, column=2, sticky="new")
        self.lbl_infoReconocer_piezas.grid(row=12, column=1, sticky="new")

        self.iniciar.grid(row=13, column=0, columnspan=5)

        # Cargamos la configuración preiva
        self.cargar_configuracion(cargar_configuracion())

    def cargar_configuracion(self, res):
        # Rellenamos los espacios, de una manera que el usuario pueda verlo bien
        imagen_escalada, resize, distancia_pixeles, pasos_intermedios, lower, upper, modo_imagen_fichas = res

        self.imagen_escalada_var.set(f"{int(imagen_escalada * 100)}%")
        self.resize_var.set(f"x{resize}")
        self.distancia_pixeles_var.set(distancia_pixeles)
        self.int_lowCanny.set(str(lower))
        self.int_UpperCanny.set(str(upper))
        self.reconocer_piezas.set(modo_imagen_fichas)
        if pasos_intermedios:
            self.mostrar_pasos.select()
        else:
            self.mostrar_pasos.deselect()

    def btn_salvar(self):
        distancia_pixeles = self.distanciaPixeles.get()
        upper_canny: str = self.int_UpperCanny.get()
        lower_canny: str = self.int_lowCanny.get()

        bien: bool = True

        # Si la distancia en pixeles no cumple los requisitos, se muestra error y no guarda
        if not distancia_pixeles.isnumeric():
            CTkMessagebox(title="ERROR", message="El espacio mínimo entre casillas debe ser un número entero",
                          icon="cancel", option_1="Vale")
            bien = False
        if not upper_canny.isnumeric():
            CTkMessagebox(title="ERROR", message="El Upper debe debe ser un número entero",
                          icon="cancel", option_1="Vale")
            bien = False
        if not lower_canny.isnumeric():
            CTkMessagebox(title="ERROR", message="El Lower debe ser un número entero",
                          icon="cancel", option_1="Vale")
            bien = False

        if bien:
            # Obtenemos los datos procesados
            imagen_escalada = float(self.escaladas.get()[:-1]) / 100
            resize = float(self.resize.get()[1:])
            upper_canny: int = int(upper_canny)
            lower_canny: int = int(lower_canny)
            grabacion_fichas: str = self.reconocer_piezas.get()
            pasos_intermedios = "true" if self.mostrar_pasos.get() == 1 else "false"

            # Guardamos los datos en el fichero de configuración
            guardar_Configuracion_IA(distancia_pixeles, imagen_escalada, pasos_intermedios, resize, lower_canny,
                                     upper_canny, grabacion_fichas)
            CTkMessagebox(title="Información", message="Configuración guardada con éxito", icon="check",
                          option_1="Vale")
