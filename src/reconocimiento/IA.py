import os
import random
import string
import sys
import cv2 as cv

from ultralytics import YOLO
from ultralytics.engine.results import Results


def generar_dataset(resultados_img: list, resultados: list[Results], ubicacion: str, clases_a_excluir: list[str],
                    prob_min: float = 0.8):
    """
    Genera una carpeta en la ubicación proporcionada con la clasificación en carpetas de las clases de las imágenes
    proporcionadas.

    :param resultados_img: Una lista con las imágenes recortadas en formato de array de Numpy
    :param resultados: Una lista de Resultados de la clasificacion de imágenes realzada por la red neuronal
    :param ubicacion: Carpeta a guardar la clasificacion de las imágenes
    :param clases_a_excluir: Una lista de strings conteniendo las clases que quieres excluir de clasificar
    :param prob_min: Probabilidad minima para que el resultado sea correcto si no mandarlo a la carpeta "zz_residuio"
    """
    # Pasamos resultados a lista de Python
    resultados = list(resultados)

    # Obtenemos las clases del primer resultado
    clases = resultados[0].names.values()

    # Creamos la estructura de carpetas si no existe
    if not os.path.exists(ubicacion):
        os.makedirs(ubicacion, exist_ok=True)
        for clase in clases:
            if clase not in clases_a_excluir:
                os.makedirs(f"{ubicacion}/{clase}", exist_ok=True)
        os.makedirs(f"{ubicacion}/zz_residuio")

    # Recorremos las imágenes
    for i in range(len(resultados_img)):
        # Obtenemos la clase de la prediccion y nos aseguramos que no este en las clases a excluir
        clase: str = resultados[i].names[resultados[i].probs.top1]
        if clase not in clases_a_excluir:
            # Obtenemos la confiablilidad de que el resultado sea veridico
            conf: int = resultados[i].probs.top1conf

            # Comprueba que la confiablilidad este por encima de la minima para en funcion de la misma, asignar
            # la ubicación de almacenamiento
            directorio_a_explorar = f'{ubicacion}/{clase}' if float(conf) > prob_min else (
                f"{ubicacion}/zz_residuio"
            )

            # Conseguimos el máximo número de dicho directorio
            numero_siguiente = siguiente_numer(directorio_a_explorar)

            # Escribe la imagen con el siguiente formato: "imagen{8charAletorios}{xxxx[maxNumero]}.jpeg"
            cv.imwrite(
                f'{directorio_a_explorar}/imagen{"".join(random.choices(string.ascii_letters, k=8))}'
                f'{numero_siguiente:04}.jpeg',
                resultados_img[i]
            )


def siguiente_numer(directorio_a_explorar: str) -> int:
    """
    Devuelve el siguiente mayor al maximo de directorio que le indiques
    :param directorio_a_explorar: El directorio del que quieres sacar el fichero con mayor numero en su nombre
    :return: El numero
    """
    lista_ficheros: list[str] = os.listdir(directorio_a_explorar)

    # Por defecto el máximo es 1
    numero_siguiente: int = 1
    if len(lista_ficheros) > 0:

        # Queremos los 4 numeros entre el 15 y el 18 que es la parte numerica y a el resultado le añadimos 1
        max_num = lista_ficheros[-1][15:18]
        numero_siguiente = int(max_num) + 1
    return numero_siguiente


def resultados_IA(resultados_img: list) -> list[Results]:
    """
    Dada una lista de imagenes devuelve una lista con las predicciones realizadas por la IA

    :param resultados_img: Una lista o una imágen con imagenes de fichas de ajedrez
    :return: Una lista con las predicciones
    """

    # Al fin y al cabo, la IA SE FIJA EN PATRONES. No importa mucho el tamaño de la imágen
    # recortadas = list()
    # for img in resultados_img:
    #     im_recortada = cv2.resize(img, (640, 450))
    #     recortadas.append(im_recortada)'''

    # Cargamos el modelo entrenado
    ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else ".."
    model = YOLO(f'{ruta}/_internal/resultados/2_fichasAjedrez_small/weights/best.pt')

    # Obtenemos el resultado
    resultados: list[Results] = model.predict(
        resultados_img,
        stream=True,  # Ahorra espacio en memoria y la agiliza cargando mas tareas en RAM
        verbose=False  # No muestra los logs referentes al rendimiento
    )
    return resultados
