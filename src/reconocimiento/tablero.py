import datetime
import os
import string
from collections import defaultdict

import cv2 as cv
import numpy as np
import scipy.cluster as cluster
import scipy.spatial as spatial
from CTkMessagebox import CTkMessagebox

from Ajedrez import crear_ajedrez, de_Resultado_to_FEN, ver_el_movimiento_tablero
from IA import resultados_IA, generar_dataset
from src.utils.GestionConfiguracion import obtener_parametro
from src.utils.GestionDAO import Conexion

# Variables Globlaes
cluser_int_previo = None  # Sirve para por si no lo encuentra, utilizaremos el viejo
ajedrez_viejo = None  # Almacena el tablero anterior, para saber el movimiento realizado

MENSAJE_TABLERO_NO_ENCONTRADO = (
    "No se ha podido encontrar el tablero. Aquí algunos consejos:\n\n"
    "\t1. Asegúrate de que no haya objetos en el fondo que puedan entorpecer el reconocimiento\n"
    "\t2. Intenta que el fondo sea lo más liso posible, sin irregularidades\n"
    "\t3. Trata de que la cámara se situé lo más cerca posible del tablero\n"
    "\t4. Vigila los reflejos o las sombras; pueden dificultar el reconocimiento de la imagen.\n"
    "\t5. Siempre trata de usar luz natural."
)


def set_ajedrez_viejo(value):
    global ajedrez_viejo
    ajedrez_viejo = value


def ordenar_array(intersecciones: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Recibe un array de intersecciones en forma de tupla (x,y) con 81 intersecciones y lo devuelve ordenado segun el
    orden en el tablero.
    :param intersecciones: las intersecciones a ordenar
    :return: las intersecciones ordenadas
    """
    # Divide el array ordenado en grupos de nueve con similitudes en 'y'
    grupos = np.array_split(np.array(intersecciones), 9)

    # Recorre cada fila y la añade al array organizandola por coordenadas en 'x'
    coordenadas_ordenadas: list[tuple[int, int]] = []
    for grupo in grupos:
        coordenadas_ordenadas.extend(sorted(grupo, key=lambda tupla: tupla[0]))

    return coordenadas_ordenadas


def dividir_imagen(img: np.array, intersecciones: list[tuple[int, int]],
                   margen_subida: int = 0,
                   margen_izquierdo: int = 0,
                   margen_derecho: int = 0,
                   margen_inferior: int = 0):
    """
    Dada una imagen y una lista de 81 intersecciones, te devuelve una lista de imágenes recortadas segun las
    intersecciones
    :param img: La imagen a dividir
    :param intersecciones: Las intersecciones que se usaran en el proceso de vision
    :param margen_subida: px de margen superior que se admiten al recortar
    :param margen_izquierdo: px de margen izquierdo que se admiten al recortar
    :param margen_derecho: px de margen derecho que se admiten al recortar
    :param margen_inferior: px de margen inferior que se admiten al recortar
    :return: Lista de imagenes recortadas segun las intersecciones
    """
    imagenes: list[np.array] = []

    # Si estamos en un determinada interseccion, su interseccion cuadrada esta a 9 puntos de la interseccion
    n_interecciones_futuro: int = 9

    n_intersecciones: int = len(intersecciones)
    j: int = 1

    # Quitamos el futuro para que no recorra la úlima fila ya que no pueden formar rectángulos con su flila inferior
    for i in range(n_intersecciones - n_interecciones_futuro):

        # Si esta acabando de recorrer una fila, no queremos que calcule el rectángulo ya que lo haría con el inicio de
        # la siguiente
        if i != (n_interecciones_futuro - 1) * j + (j - 1):  # i = 8, 17, 26, 35, 45, 54, 63, 72, 81
            x1, y1 = intersecciones[i]
            x2, y2 = intersecciones[i + 1]

            x3, y3 = intersecciones[i + n_interecciones_futuro]
            # x4, y4 = intersecciones[i + 1 + n_interecciones_futuro] # No hace falta. La altura lo marca ya 'y3'

            y1 -= margen_subida
            x1 -= margen_izquierdo
            x2 += margen_derecho
            y3 += margen_inferior

            y1 = max(y1, 0)
            y3 = max(y3, 0)
            x1 = max(x1, 0)
            x2 = max(x2, 0)

            imagen_recortada = img[y1:y3, x1:x2]
            imagenes.append(imagen_recortada)
        else:
            j += 1
    return imagenes


def cluster_points(points: np.ndarray, distancia_puntos: int = 85):
    """
    Dado un array de intersecciones, filtra las intersecciones que esten mas cerca que la distrancia que se le indique
    con el objetivo de quitar intersecciones demasiado juntas.

    Basada en la función del bueno de https://github.com/andrewleeunderwood
    :param points: Un array de numpy con las intersecciones en formato (x,y)
    :param distancia_puntos: Un integer con la distancia
    :return: Una lista con las intersecciones que cumplan las condiciones
    """
    # print(f"Points ->  Numero: {len(points)}. Dimensiones: {len(points[0])}.\n {str(points)}")

    # Devuelve una array UNIDIMENSIONAL con los cálculos de la distancia entre las intersecciones entre ellas. Para cada
    # intersección calcula su distancia con cada una de las otras intersecciones, excepto ella misma por eso -1.
    #
    #          N * (N−1)
    # n_res = -----------
    #              2
    #
    #     N es el numero de puntos
    # El orden del nuevo narray es el de primero comparar el primer punto con los demas (menos el mismo), luego el 2º...
    #
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html
    dists: np.ndarray = spatial.distance.pdist(points)

    # print(f"dist -> {len(dists)}. Dimensiones: {1}.\n {str(dists)}")

    # Devuelve tuplas de 4 con las distancias calculadas previamente indicando las distancias entre los puntos de una
    # manera gerárquica. Ordenados de menor a mayor
    # 1. Punto 1º mas cercano
    # 2. Punto 2º mas cercano
    # 3. Distancia minima entre los puntos que intervienen en la comparacion
    # 4. Intersecciones que intervienenen
    # Por su naturaleza devuelve el mismo numer de distancias - 1
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.single.html
    single_linkage: np.ndarray = cluster.hierarchy.single(dists)

    # print(f"single_linkage -> {len(single_linkage)}. Dimensiones: {len(single_linkage[0])}.\n {str(single_linkage)}")

    # Agrupa los puntos basados en la distnacia minima que se le pasa.
    # Devuelve una lista asignando cada punto a un clúster distino. Un clúster es una agrupación de intersecciones
    # cercanas que cumplan con el criterio que se le asgina. Por ejemplo, [37, 37, 47,  ...] indican que los 2 primeras
    # intersecciones de 'single_linkage', pertenecen al cluster 37 y que el 3º elemento al cluster 47
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html
    flat_clusters = cluster.hierarchy.fcluster(single_linkage, distancia_puntos, 'distance')

    # print(f"flat_clusters -> {len(flat_clusters)}. Dimensiones: {1}.\n {str(flat_clusters)}")

    # Diccionario cuya clave va a ser el numero de la agrupacion y cuyo valor una lista de intersecciones Hay que usar
    # este tipo de diccionario, ya que es el que permite en el futuro hacer la pijoteria de actualizar la lista
    # obteniendola con la clave, ya que por defecto para cada key, crea una lista vacia como value.
    # Viene bien para agrupar los clusters con sus respectivas intersecciones
    cluster_dict: defaultdict = defaultdict(list)

    # Rellenamos la lista de intersecciones
    for i in range(len(flat_clusters)):
        # Con i = 2
        # Al cluster que haya en la posicion "2" (22) le asignamos el punto en la posicion 2 (832, 953).
        # Al cluster que haya en la posicion "3" (24) le asignamos el punto en la posicion 3 (1232, 462).
        cluster_dict[flat_clusters[i]].append(points[i])

    # Obtenemos los centros de cada agrupacion
    clusters: list[(float, float)] = []
    # print(f"Diccionario de cluster agrupados: f{str(cluster_dict)}")
    for clusterr in cluster_dict.values():
        # Pasa la agrupacion de clusters a array de numpy en 2D
        array_numpy = np.array(clusterr)

        res1 = array_numpy[:, 0]  # Pilla la 1ª columna (x)
        res2 = np.mean(res1)  # Calcula la media de x

        res11 = array_numpy[:, 1]  # Pilla la 2ª columna (y)
        res22 = np.mean(res11)  # Calcula la media de y

        clusters.append((res2, res22))

    # Ordena la lista por 'y' (para agrupar en filas) y luego por 'x' (para agrupar en columnas)
    return sorted(list(clusters), key=lambda g: [g[1], g[0]])


def encontrar_interseccion_Inf(linea_h: tuple, linea_v: tuple):
    """
    Tira la linea al infinito a ver en que coordenada se van a chochar
    :param linea_h: Una tupa de 4 elementos simbolizando una recta. (x1,y1,x2,y2)
    :param linea_v: Una tupa de 4 elementos simbolizando una recta. (x1,y1,x2,y2)
    :return: (-1, -1) Si no hay interseccion en ningun momento (son paralelas), o las coordenadas de la
    interseccion en formato (x,y)
    """

    x1_h, y1_h, x2_h, y2_h = linea_h
    x1_v, y1_v, x2_v, y2_v = linea_v

    #  Primero calculamos la pendiente
    #       △y           y2 - y1
    #  m = ----  => m = ---------
    #       △x           x2 - x1
    #

    # Si son paralelas es infinito
    m_h = (y2_h - y1_h) / (x2_h - x1_h) if x2_h != x1_h else float('inf')
    m_v = (y2_v - y1_v) / (x2_v - x1_v) if x2_v != x1_v else float('inf')

    # ECUACION GENERAL DE LA RECTA
    # y = mx + b
    #
    # PENDIENTE
    #       y2 - y1
    #  m = ---------
    #       x2 - x1
    #
    # ORDENADA DE ORIGEN
    #  b = y - m * x
    #
    # Para encontrar la interseccion hay que igualar para sacar la coordenada buscada. En este caso x
    # m1 * x + b1 = m2 * x + b2
    #
    # m1 * x - m2 = x * b2 - b1
    #
    # m1 * x - m2 * x = b2 - b1
    #
    # ( m1 - m2 ) * x = b2 - b1
    #
    #       b2 - b1              (y2 - m2 * x2) - (y1 - m1 * x1)
    # x = ------------  =>  x = -------------------------------
    #       m1 - m2                         m1 - m2
    #
    # Con la coordenada x ya podemos sustituir arrbia

    if m_h == m_v:
        x_interseccion = -1
        y_interseccion = -1
    elif m_h == float('inf'):  # Es una linea recta, por lo tanto su coordenada x no cambia
        x_interseccion = x1_h
        y_interseccion = m_v * (x1_h - x1_v) + y1_v
    elif m_v == float('inf'):  # Es una linea recta, por lo tanto su coordenada x no cambia
        x_interseccion = x1_v
        y_interseccion = m_h * (x1_v - x1_h) + y1_h
    else:
        x_interseccion = ((y1_v - m_v * x1_v) - (y1_h - m_h * x1_h)) / (m_h - m_v)
        y_interseccion = m_h * (x_interseccion - x1_h) + y1_h

    return x_interseccion, y_interseccion


def ajustar_gamma(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Ajusta el gamma de la imagen que se le pasa. De
    https://rockyshikoku.medium.com/opencv-is-a-great-way-to-enhance-underexposed-overexposed-too-dark-and-too-bright-images-f79c57441a8a

    :param image: La imagen a cambiar
    :param gamma: El gamma deseado
    :return:  La imagen actualizada
    """
    # build a lookup table mapping the pixel values [0, 255] to their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv.LUT(image, table)


def aumentar_contraste(imagen: np.ndarray, contraste=4.3, brillo=-300):
    """
    Adjusta el brillo de la imagen junto con su contraste, devolviendo la imágen ya modificada

    :param imagen: La imagen a cambiar
    :param contraste: El nuevo contraste
    :param brillo: El nuevo brillo
    :return: La imagen actualizada
    """
    imagen = cv.addWeighted(imagen, contraste, np.zeros(imagen.shape, imagen.dtype), 0, brillo)
    return imagen


def procesar_imagenes_recortadas(imagenes: list[np.ndarray], resize: float = 2, ubicacion_imagenes: str = None) -> \
        list[np.ndarray]:
    """
    Recibe una lista de imagenes del tablero y lo devuelve con las imágenes preparadas para ser procesadas por
    ultralytics
    :param resize: El resize que se la va a aplicar a las imagenes resultantes
    :param imagenes: La lista de imagenes del tablero a procesar
    :param ubicacion_imagenes: Si queremos se guarden en una carpeta, podemos indicarle la ruta
    :return: La lista ordenada
    """
    imagenes_para_IA = []
    fila: int = 0
    linea: int = 1

    for imagen_sacada in imagenes:
        #   if imagenes[i].shape[0] != 0 or imagenes[i].shape[1] != 0:
        # imagen_sacada = imagenes[i]

        # Procesa la imágen y la añade al array a devolver
        # INTER_NEAREST, INTER_LINEAR, INTER_AREA, INTER_CUBIC & INTER_LANCZ0S4
        imagen_sacada = cv.resize(imagen_sacada, None, fx=resize, fy=resize, interpolation=cv.INTER_CUBIC)  # 2, 2
        imagenes_para_IA.append(imagen_sacada)

        # print(f"Imagen {i} -> {imagen_sacada.shape[0]} x {imagen_sacada.shape[1]}")
        if ubicacion_imagenes is not None:
            if linea == 9:
                fila += 1
                linea = 1

            if not os.path.exists(ubicacion_imagenes):
                os.makedirs(ubicacion_imagenes)
            cv.imwrite(f'{ubicacion_imagenes}/imagen_{list(string.ascii_uppercase)[fila]}{linea}.jpeg', imagen_sacada)

            linea += 1

    return imagenes_para_IA


def tratar_resultado(resultados: list, ventana_tablero):
    """
    Recibidos los resultados los procesa para mostrarlos al usuario y almacenarlos en la BDD
    :param resultados: Una lista de predicciones de la red neuronal
    :param ventana_tablero: La ventana en la que va a mostrar el resultado
    """
    global ajedrez_viejo

    FEN = de_Resultado_to_FEN(resultados, 0.3)
    print("Fen : " + FEN)
    ajedrez = crear_ajedrez(FEN)

    # Se lo mostramos al usuario
    if ventana_tablero is not None:
        ventana_tablero.visualizar(ajedrez)

    # Escribimos el resultado en SVG
    # svg: str = ajedrez_to_SGV(ajedrez)
    # escribr_svg(svg)

    # Si hay moviento
    if ajedrez_viejo is not None:
        origen, destino, pieza, tipo_enrroque = ver_el_movimiento_tablero(ajedrez_viejo, ajedrez)
        if pieza is None:  # Es error y se le muestra a usuario
            print("* ----------------------------------------------------------------------------- *")
            print(f"ERROR {origen}: {destino}")
            mensaje = (f"{destino}\n\nLa jugada no ha sido registrada por lo tanto, una vez enmendado el fallo vuelve "
                       f"a intentar registrarla.")
            box = CTkMessagebox(title=f"Error {origen}", message=mensaje, icon="cancel", option_1="Vale", width=1500)
            box.grid_columnconfigure(1, weight=5)
        else:
            ajedrez_viejo = ajedrez  # Actualizamos el ajedrez viejo
            if tipo_enrroque is not None:
                print(f"Enrroque desde {origen} a {destino} de {pieza} haciendolo de tipo {tipo_enrroque}")
            else:
                print(f"{pieza} movida de {origen} a {destino}")

            #  Almacenamos el movimiento en la BDD
            if ventana_tablero is not None:
                idd = ventana_tablero.id_bdd

                if tipo_enrroque is not None:
                    destino = tipo_enrroque

                insertar_movimiento(pieza.symbol(), destino, None, FEN, idd)

    elif ventana_tablero is not None:
        # Si no hay ajedrez viejo, asigna el actual al viejo. No hay movimiento
        confirmacion: CTkMessagebox = CTkMessagebox(
            title="Confirmación",
            message="¿Esta correcto el tablero?",
            icon="question",
            option_1="No",
            option_2="Si"
        )
        if confirmacion.get() == "Si":
            ajedrez_viejo = ajedrez


def insertar_movimiento(pieza, destino, fecha, FEN, ultimo_id):
    """
    Inserta un movimiento en la BDD
    :param pieza: la pieza
    :param destino: Casilla de destino
    :param fecha: Hora de movimieno
    :param FEN: Estado actual del tablero
    :param ultimo_id: Id de la partida a la que pertenece el movimiento
    """
    con = Conexion()
    if fecha is None:
        fecha = str(datetime.datetime.now())

    con.insertar_movimientos([(pieza, destino, fecha, FEN, ultimo_id)])


def sacar_tablero(camara: cv.VideoCapture | None,
                  frame: np.ndarray,
                  ventana_tablero,
                  entrenar: bool = False,
                  sacar_imagenes_intermedias: bool = True,
                  utilizar_cluster_viejo: bool = False):
    global cluser_int_previo
    numero_interaciones: int = 30
    tablero_encontrado: bool = False

    # Imagenes para ver el proceso
    imagen2: np.ndarray = frame.copy()
    imagen3: np.ndarray = frame.copy()
    imagen_final: np.ndarray = frame.copy()
    blur_gausanno: np.ndarray = np.array([])
    clusters_int: list[tuple[int, int]] = []

    i: int = 0
    while not tablero_encontrado and (camara is not None or i != 1) and i < numero_interaciones:
        i += 1
        if i != 1:
            frame = camara.read()[1]

            # Clonamos la imagen para si futuro uso
            imagen2: np.ndarray = frame.copy()
            imagen3: np.ndarray = frame.copy()
            imagen_final: np.ndarray = frame.copy()

        # Antes de pasarlo a moncromático, subimos un poco el contraste de la imágen para que los detalles de las
        # se difuninen mas aun.
        # cv.imwrite("doc/00_original.jpeg", frame)

        frame: np.ndarray = aumentar_contraste(frame, contraste=2, brillo=-120)  # 2, -120

        # cv.imwrite("doc/01_contraste.jpeg", frame)

        # Los algoridmos futuros que usaremos requieren que la imágen este en escala de grises, ya que asi facilitaremos
        # en gran medida el preprocesamiento de la imágen
        # Pasamos el frame a escala de grises
        frame: np.ndarray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # ES BGR ya que numpy es especial y no usa RGB

        # cv.imwrite("doc/01_gris.jpeg", frame)
        # frame: np.ndarray = cv.threshold(frame, 100, 255, cv.THRESH_TRUNC)[1]

        # De los distinos tipos de Blur que exiten el Gaussian es el que mejor resultado ofrece ya que da unas lineas
        # mas suaves en comparacion al normal
        # frame: np.ndarray = cv.blur(frame, (11, 11))
        # frame: np.ndarray = cv.bilateralFilter(frame, 9, 75, 1000)

        # El 'Kernel Size' tiene que ser impar (9,9)
        # El 'sigma' ayuda a distorsionar un poco la imágen, quitando aun mas ruido
        frame = cv.GaussianBlur(frame, (11, 11), sigmaX=100, sigmaY=100,
                                borderType=cv.BORDER_CONSTANT)  # Este es que viene por defecto

        # Copiamos el frame para mostrar despues el resultado despues del preprocesado
        blur_gausanno: np.ndarray = frame.copy()
        # cv.imwrite("doc/02_blur.jpeg", frame)
        # Devuelve la media del array de pixeles de numpy
        # v: float = np.median(frame)

        # print(f"Media de pixeles: {v}")

        # Indica lo estricto que es el Canny
        # variable = 0.33  # Cuanto mas alto mas extricto

        # t_lower = int(max(0, (1.0 - variable) * v))  # Lower Threshold
        # t_upper = int(min(255, (1.0 + variable) * v))  # Upper threshold

        # Aplicamos el filtro Canny para filtrar las lineas.
        # Lower -> Manteniendo los demás valores constantes, cuando disminuimos este valor, los bordes que están rotos
        #          tienden a unirse. Si lo incrementamos, los bordes continuos tienden a romperse
        # Upper -> con los otros valores fijos, si lo incrementamos, pocos son los bordes detectados, por otro lado, si
        #          lo disminuimos vamos a detectar más bordes
        # https://www.linkedin.com/pulse/detecci%C3%B3n-de-bordes-objetos-con-canny-edge-detection-v%C3%A9lez-rom%C3%A1n/

        # TODO: Toca lo de los bordes fuertes
        frame: np.ndarray = cv.Canny(
            frame,
            obtener_parametro('IA', 'lower'),
            obtener_parametro('IA', 'upper')
        )  # Lower, upper -> 100, 150

        # cv.imwrite("doc/03_canny.jpeg", frame)

        # Detecta las lineas probabilisticamente
        lines = cv.HoughLinesP(
            frame,  # Frame con lo edege
            1,  # Exactitud del calculo del pixel en la coordenada Polar
            np.pi / 180,  # Exactitud del calculo de los radianes
            130,  # Mínimo de votos validos para considerarlo linea
            minLineLength=350,  # Minima longitud para considerarlo linea en px
            maxLineGap=600  # Espacio entre lines para unirlas en una unica linea en px
        )

        # Comprueba que al menos ha sacaado alguna linea
        if lines is not None:
            lineas_horizontales = []
            lineas_verticales = []

            # TODO: BORRAR
            # imagen4: np.ndarray = imagen2.copy()

            for points in lines:
                x1, y1, x2, y2 = points[0]  # Esto es una linea.

                # Tangente - Calculamos la pendiente entre 2 puntos.
                # arctan2 calcula el ángulo en radianes de cada linea entre el punto dado y el eje 0, 0
                # [ * 180.0 / np.pi ] lo pasa a grados
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)

                # print(F"Angulo -> {angle}")

                # Filtrar las lineas diagonales. Si hay algunacon alguna pendiente muy acusada, nos la cargamos.
                # Tambien de paso, agiliza el proceso, ya que son menos lineas con las que interactuar.
                if angle < 10 or angle > 80:  # 8, 85
                    # Difenrecia entre las coordenadas 'x' e 'y'
                    dx = abs(x2 - x1)
                    dy = abs(y2 - y1)

                    # cv.line(imagen4, (x1, y1), (x2, y2), (0, 0, 255), 5)

                    # Determina si la linea es horizontal o vertical
                    if dx > dy:  # Horizontal
                        cv.line(imagen2, (x1, y1), (x2, y2), (0, 255, 0), 5)
                        lineas_horizontales.append((x1, y1, x2, y2))
                    else:  # Vertical
                        cv.line(imagen2, (x1, y1), (x2, y2), (255, 0, 0), 5)
                        lineas_verticales.append((x1, y1, x2, y2))
                else:
                    print(f"Linea con {int(angle)}º, al carré")

            # cv.imwrite("doc/04_HoughLinesP.jpeg", imagen4)
            # cv.imwrite("doc/05_HoughLinesP_clasificado.jpeg", imagen2)

            # Tenemos ya las lineas buenas, clasificadas en horizontales y verticales
            intersecciones = []

            # Al dividir las lineas entre verticales y hroizontales, nos ahorramos unas cuantas operaciones ya que no
            # se buscan intersecciones entre dos horizontales o dos verticales
            for linea_h in lineas_horizontales:
                for linea_v in lineas_verticales:
                    inters_x, inters_y = encontrar_interseccion_Inf(linea_h, linea_v)
                    # imagen3.shape[0] -> Altura
                    # imagen3.shape[1] -> Anchura
                    if inters_x != -1 and inters_y != -1:
                        if (inters_x > 20 and inters_x + 20 < imagen3.shape[1] and
                                inters_y > 20 and inters_y + 20 < imagen3.shape[0]):
                            interseccion: tuple[int, int] = int(inters_x), int(inters_y)
                            intersecciones.append(interseccion)

            # A partir de aqui, ya tenemos todas las interescciones de las lineas y las dibujamos en la imágen
            if len(intersecciones) != 0:
                for x, y in intersecciones:
                    cv.circle(imagen2, (x, y), 8, (0, 0, 255), -1)

            # cv.imwrite("doc/06_intersecciones.jpeg", imagen2)

            # *********************************************************************************************
            # Filtramos por las intersecciones

            intersecciones_numpy: np.ndarray = np.array(intersecciones)
            if intersecciones_numpy.ndim >= 2:  # El array tiene que ser de 2 dimensiones
                clusters = cluster_points(intersecciones_numpy, distancia_puntos=obtener_parametro('IA', 'clusters'))
                print(f"Clusters {len(clusters)}")

                if i == numero_interaciones:
                    clusters_int = [(int(coordx), int(coordy)) for (coordx, coordy) in clusters]
                    for x, y in clusters_int:
                        cv.circle(imagen3, (x, y), 8, (0, 255, 255), -1)
                        cv.putText(imagen3, f'{x}, {y}', (x + 10, y + 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Un tablero tiene 81 intersecciones; hace el bucle hasta que pilla 81
                if len(clusters) == 81:
                    clusters_int = [(int(coordx), int(coordy)) for (coordx, coordy) in clusters]
                    for x, y in clusters_int:
                        cv.circle(imagen3, (x, y), 8, (0, 255, 255), -1)
                        cv.putText(imagen3, f'{x}, {y}', (x + 10, y + 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # cv.imwrite("doc/07_clusters.jpeg", imagen3)
                    # El tablero de ajedrez debe tener 81 intersecciones
                    tablero_encontrado = True  # Si tiene 81 da True si no False

    # ********************************************************************************************************

    # Si no tenemos las 81 intersecciones y tenemos interescciones de antes, le lanzamos la pregunta al usuario
    if len(clusters_int) != 81 and (not tablero_encontrado and cluser_int_previo is not None):
        confirmacion: CTkMessagebox = CTkMessagebox(
            title="Tablero no encontrado",
            message=f"{MENSAJE_TABLERO_NO_ENCONTRADO}\n¿Quieres reutilizar los que generó anteriormente para este "
                    f"movimiento?",
            icon="question",
            option_1="No",
            option_2="Si",
            width=1200
        )
        confirmacion.grid_columnconfigure(1, weight=10)
        utilizar_cluster_viejo = confirmacion.get() == "Si"

    # Reulizamos los clusterprevios si asi el usuario lo dispone
    if len(clusters_int) == 81 or (utilizar_cluster_viejo and not tablero_encontrado and cluser_int_previo is not None):
        if utilizar_cluster_viejo and not tablero_encontrado:
            clusters_int = cluser_int_previo
            print("He reutilizado los CLUSTERS antiguos")
        else:
            clusters_int = ordenar_array(clusters_int)
            if utilizar_cluster_viejo:
                # Guardamos por si acaso una copia
                cluser_int_previo = clusters_int.copy()

        # Bajamos el contrase para que se pueda apreciar mejor los relieves de las piezas
        # Full luz natural (Base) -> 0.6, 50
        # Con luz nautral + artificial -> 0.5, 80
        # Full luz artificial -> No va. Recomendable Gamma

        if obtener_parametro('IA', 'modo_imagen_fichas').lower() == "brillo + contraste":
            imagen_final: np.ndarray = aumentar_contraste(imagen_final, contraste=0.5, brillo=80)
        else:
            # Ayuda con la luz artificial en gran medida
            imagen_final: np.ndarray = ajustar_gamma(imagen_final, gamma=2)

        # cv.imwrite("doc/08_iamgen_reconocer_piezas.jpeg", imagen_final)

        # Dividimos las imagenes un 64 iguales
        imagenes: list[np.ndarray] = dividir_imagen(imagen_final, clusters_int, 20, 20, 5, 10)
        print(f"Imagenes Recortadas -> {len(imagenes)}")

        imagenes = procesar_imagenes_recortadas(imagenes, obtener_parametro('IA', 'resize_ficha'))

        # ******************************************************************************************************
        # IA Rockea
        resultados: list = resultados_IA(imagenes)

        # Diferenciamos entre si estabamos entrenando o no
        if entrenar:
            generar_dataset(imagenes, resultados, "./datasetGloriosa3", [], 0.3)
        else:
            tratar_resultado(resultados, ventana_tablero)
    elif ventana_tablero is not None and cluser_int_previo is None:
        box: CTkMessagebox = CTkMessagebox(title="Tablero no encontrado", message=MENSAJE_TABLERO_NO_ENCONTRADO,
                                           icon="warning", option_1="Vale", width=1500)
        box.grid_columnconfigure(1, weight=10)
    else:
        print('''
        + -------------------------------------------------------------- +
        |          No se ha logrado encontrar un tablero válido :(       |
        + -------------------------------------------------------------- +''')

    escalada = obtener_parametro('IA', 'frame_escalada')
    if obtener_parametro('IA', 'pasos_intermedios') and ventana_tablero is not None:

        blur_gausanno = cv.resize(blur_gausanno, None, fx=escalada - 0.1, fy=escalada - 0.1)
        frame = cv.resize(frame, None, fx=escalada - 0.1, fy=escalada - 0.1)
        imagen2 = cv.resize(imagen2, None, fx=escalada - 0.1, fy=escalada - 0.1)
        imagen_final = cv.resize(imagen_final, None, fx=escalada - 0.1, fy=escalada - 0.1)
        imagen3 = cv.resize(imagen3, None, fx=escalada, fy=escalada)

        ventana_tablero.mostrar_ventanas([
            ('Canny', frame),
            ('Original', imagen2),
            ('Imagen Final', imagen_final),
            ('Blur Gausanno', blur_gausanno),
            ('Clusters', imagen3)
        ])

    elif sacar_imagenes_intermedias:
        imagen3 = cv.resize(imagen3, None, fx=escalada, fy=escalada)
        cv.imshow('Custlers', imagen3)

        if not entrenar or True:
            if blur_gausanno.shape[0] != 0 and blur_gausanno.shape[1] != 0:
                blur_gausanno = cv.resize(blur_gausanno, None, fx=escalada, fy=escalada)
                cv.imshow('Blur Gausanno', blur_gausanno)

            frame = cv.resize(frame, None, fx=escalada, fy=escalada)
            imagen2 = cv.resize(imagen2, None, fx=escalada, fy=escalada)
            # frame2 = cv.resize(frame2, None, fx=0.6, fy=0.6)
            imagen_final = cv.resize(imagen_final, None, fx=escalada, fy=escalada)

            cv.imshow('Canny', frame)
            cv.imshow('Original', imagen2)
            # cv.imshow('Blur', frame2)
            cv.imshow('Imagen Final', imagen_final)


def main(cam: cv.VideoCapture, ventana_tablero):
    # Leemos la configuración
    imagen_escalada: float = obtener_parametro('IA', 'frame_escalada', "../_internal/config.ini")

    quedarse: bool = True
    while quedarse:
        frame2 = cam.read()[1]

        frame_chiquito = frame2.copy()
        frame_chiquito = cv.resize(frame_chiquito, None, fx=imagen_escalada, fy=imagen_escalada)  # 0.6

        print(frame_chiquito)

        cv.imshow("Pulsa 'Espacio' para indicar movimiento / 'q' para salir", frame_chiquito)

        k = cv.waitKey(2)

        if k == ord('q'):
            # Presionaste 'q'
            print("Has presionado 'q'. Hasta lugo...")
            quedarse = False
        elif k == ord(' ') or k == 13:  # Espacio o el 13 es el unicde de Intro
            # Presionaste 'Espacio' o 'Enter'
            sacar_tablero(cam, frame2, ventana_tablero, False, True, False)

    cam.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main(cv.VideoCapture(1), None)
