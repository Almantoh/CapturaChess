from customtkinter import CTkButton


class CTkButtonImagen(CTkButton):
    """
    Clase que edita el botón base de customtkinter para permitir tener varias imagenes segun el si tiene el puntero
    arriba o no
    """
    def __init__(self, root, imagen_inactivo, imagen_activo, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        # ----- VAR LOCALES ------
        self.imagen_inactivo = imagen_inactivo
        self.imagen_activo = imagen_activo

        # Por defecto se activa la imagen de incactivo
        self.configure(image=self.imagen_inactivo)

        # Asociamos los eventos dle raton a funciones para cambiar la imágen
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)

    def enter(self, event):
        self.configure(image=self.imagen_activo)

    def leave(self, event):
        self.configure(image=self.imagen_inactivo)
