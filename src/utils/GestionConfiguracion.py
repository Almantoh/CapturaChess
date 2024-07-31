import configparser as cfg
import os
import re
import sys


# Comprobamos si se esta ejecutando desde un ejecutable
ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."

# Ruta por defecto donde se va a almacenar la configuración
FICHERO_CONFIGURACION: str = os.path.join(ruta, "_internal/config.ini")

# Creamos el objeto de ConfigParser de manera global
config: cfg.ConfigParser = cfg.ConfigParser()


def cargar_configuracion(fichero: str = FICHERO_CONFIGURACION) -> (str, str, int, bool, int, int):
    """
    Devuelve la configuracion de la sección "IA" en el fichero de cofiugración

    :param fichero: El fichero de configuracion
    :return: Una tupla con la configuracion
    """
    # Read the configuration file
    config_str: list[str] = config.read(fichero)

    if len(config_str) != 0:
        imagen_escalada = config.getfloat('IA', 'frame_escalada')
        resize = config.getfloat('IA', 'resize_ficha')
        distancia_pixeles = config.getint('IA', 'Clusters')
        pasos_intermedios = config.getboolean('IA', 'pasos_intermedios')
        lower = config.getint('IA', 'lower')
        upper = config.getint('IA', 'upper')
        modo_imagen_fichas = config.get('IA', 'modo_imagen_fichas')
    else:
        imagen_escalada = None
        resize = None
        distancia_pixeles = None
        pasos_intermedios = None
        lower = None
        upper = None
        modo_imagen_fichas = None

    return imagen_escalada, resize, distancia_pixeles, pasos_intermedios, lower, upper, modo_imagen_fichas


def obtener_parametro(seccion: str, opcion: str, fichero: str = FICHERO_CONFIGURACION) -> str | float | int | bool:
    """
    Devuelve el valor de la seccion y clave en el fichero de cofiugración que le indiques.
    Si buscas la en la seccion de CÁMARAS y no encuentra, devuelve un 0.

    :param seccion: La seccion [] en la que se encuentra
    :param opcion: La opcion que quiere cosneguir
    :param fichero: El fichero de configuracion
    :return: El paramentro requerido
    """
    # Leemos el contenido del fichero de configuración
    config.read(fichero)

    # Comprobamos si tiene dicha seccion y valor
    if config.has_section(seccion):
        if config.has_option(seccion, opcion):

            # Obtenemos el resultado y lo evaluamos para saber que tipo de dato devolver
            ress: str = config.get(seccion, opcion).lower()
            if ress.isdigit():
                ress: int = int(ress)
            elif re.match(r'^-?\d+\.\d+$', ress):  # Comprueba con una expresion regular si puede ser float
                # La 'r' hace que ignore todos los elementos de escape. Por ejemplo el '/n' no seria salto de línea.
                ress: float = float(ress)
            elif ress == "true":
                ress: bool = True
            elif ress == "false":
                ress: bool = False
        elif opcion == "CAMARA":
            ress: int = 0
        else:
            raise Exception(f"La opcion {opcion} no existe en la seccion {seccion} de la configuración")
    elif seccion == "CAMARA":
        ress: int = 0
    else:
        raise Exception(f"La seccion {seccion} no existe en la configuración")

    return ress


def guardar_Configuracion_IA(distancia_pixeles: int, imagen_escalada: float, pasos_intermedios: str, resize: float,
                             lower: int, upper: int, grabacion_fichas: str, fichero: str = FICHERO_CONFIGURACION):
    """
    :param grabacion_fichas: El tipo de postprocesado a realizar sobre las imágenes resultantes de las fichas
    :param upper: El Upper de Canny
    :param lower: El Lower de Canny
    :param distancia_pixeles: La distancia de px entre cada interseccion
    :param imagen_escalada: El tamaño del frame a mostrar
    :param pasos_intermedios: Si queremos que muestre los pasos intermedios
    :param resize: El tamaño de escalado de las fichas extraidas del tablero
    :param fichero: El fichero de configuracion
    """
    # Leemos el contenido del fichero de configuración
    config.read(fichero)

    # Comprobamos que tenga la seccion de IA
    if not config.has_section("IA"):
        config.add_section("IA")

    # Guardamos la infrmación
    config.set('IA', "frame_escalada", str(imagen_escalada))
    config.set('IA', "resize_ficha", str(resize))
    config.set('IA', "Clusters", str(distancia_pixeles))
    config.set('IA', "pasos_intermedios", pasos_intermedios)
    config.set('IA', "lower", str(lower))
    config.set('IA', "upper", str(upper))
    config.set('IA', "modo_imagen_fichas", grabacion_fichas)

    with open(fichero, 'w') as con:
        config.write(con)


def guardar_camara(identificador_openCV_camara: int = 0, fichero: str = FICHERO_CONFIGURACION):
    """
    Guardamos el identificador de la cámara de OpenCV en el fichero

    :param identificador_openCV_camara: el identificador de OpenCV
    :param fichero: El fichero de configuración
    """
    # Leemos la configuración
    config.read(fichero)
    # Si el archivo de confgración no contiene la seccion de CAMARA se le añade
    if not config.has_section("CAMARA"):
        config.add_section("CAMARA")
    # Añadimos la camara que el usuario haya elegido
    config.set('CAMARA', "camara", str(identificador_openCV_camara))
    with open(fichero, 'w') as con:
        config.write(con)


def crear_configuracion(fichero: str = FICHERO_CONFIGURACION):
    """
    Crea el fichero de configuración con los valores por defecto de cada seccion del fichero si no tiene
    la sección creada

    :param fichero: El fichero de configuración
    """
    # Leemos la configuración
    config.read(fichero)

    # Revisa si tiene la seccion ya creada. Si no la crea y le da el valor por defecto
    if not config.has_section("IA"):
        config.add_section("IA")

        config.set('IA', "frame_escalada", "0.6")
        config.set('IA', "resize_ficha", "2")
        config.set('IA', "Clusters", "80")
        config.set('IA', "pasos_intermedios", "false")
        config.set('IA', "lower", "40")
        config.set('IA', "upper", "150")
        config.set('IA', "modo_imagen_fichas", "Brillo + Contraste")

    if not config.has_section("CAMARA"):
        config.add_section("CAMARA")

        config.set('CAMARA', "camara", "0")

    with open(fichero, 'w') as con:
        config.write(con)
