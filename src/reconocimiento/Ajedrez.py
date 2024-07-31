import io

import cairosvg
import chess
import chess.svg as svg
import customtkinter as ctk
from PIL import Image
from ultralytics.engine.results import Results

from ChessMio import BoardMio


def de_Resultado_to_FEN(resultados: list[Results], confianza: float = 0.5) -> str:
    """
    Dado un resultado lo pasa a FEN (Forsyth–Edwards Notation). \n\nGuía: https://www.chess.com/terms/fen-chess

    :param resultados: Una lista de prediccion de la red neuronal
    :param confianza: La confianza de la prediccion minima para que se acepte
    :return: Un string con la notacion
    """
    # Declaracion de variables de conteo y el string vacio con el resultado
    FEN: str = ""
    i_blancos: int = 0
    i_contador_casilla_linea: int = 0

    for r in resultados:
        print(f"- {r.names[r.probs.top1]} -> {r.probs.top1conf}")
        # Aumentamos el contador de casilla de la linea simbolizando que avanzamos de casilla
        i_contador_casilla_linea += 1

        # Obtenemos el id de la prediccion
        ids: int = r.probs.top1

        # Si no pertenece a la clase, es blanco o no cumple el estandar de coonfianza, se considera casilla en blanco
        if r.names[ids] == "blanco" or r.probs.top1conf < confianza:
            i_blancos += 1
        else:
            # Aqui se considera que es una ficha válida

            # Si el numero de blancos no es 0, lo añadimos al string de FEN y lo ponemos a 0
            FEN, i_blancos = comprobar_blancos(FEN, i_blancos)

            # Filtra las piezas para saber la inicial que corrsponde
            match r.names[ids][:-2]:  # Quita los 2 últimos carácteres. Ej. Dama_1 -> Dama
                case "Torre":
                    resultado = "r"
                case "Caballo":
                    resultado = "n"
                case "Alfil":
                    resultado = "b"
                case "Dama":
                    resultado = "q"
                case "Rey":
                    resultado = "k"
                case "Peon":
                    resultado = "p"
                case _:
                    resultado = "fallo"

            # Si no ha fallado comprueba el color. El 1 se considera blanco y debe ser mayúscyla, mientras que el 0 es
            # negro y se queda en minúscula
            if resultado != "fallo":
                if r.names[ids][-1] == "1":  # Extrae el último carácter. Ej. Dama_1 -> 1
                    resultado = resultado.upper()
                FEN += resultado
            else:  # Sería un fallo por lo que lo dariamos como blanco
                i_blancos += 1
                print("FALLO en una de las casillas")
        # Si hemos llegado a la 8 casilla (es decir, recorrido una línea) volvemos a escribir las casillas blancas que
        # tengamos y cerramos la linea con una "/".
        if i_contador_casilla_linea >= 8:
            FEN, i_blancos = comprobar_blancos(FEN, i_blancos)
            FEN += "/"
            i_contador_casilla_linea = 0
    return FEN[:-1]  # El último carácter es una "/" y sobra


def comprobar_blancos(FEN, i_blancos) -> (str, int):
    """
    Si el numero de blancos no es 0, lo añadimos al string de FEN y lo ponemos a 0

    :param FEN: Notacion FEN
    :param i_blancos: el numero de blancos
    :return: La notaacion y el numero de blancos actalizado
    """
    if i_blancos != 0:
        FEN += str(i_blancos)
        i_blancos = 0
    return FEN, i_blancos


def crear_ajedrez(FEN: str = "8/8/8/8/8/8/8/8") -> BoardMio:
    """
    Crea un ajedrez de mi clase
    :param FEN: Notacion FEN
    :return: El ajedrez creado segun la notación o None si no esta bien
    """
    ajedrez: BoardMio = BoardMio(FEN)
    return ajedrez


def ajedrez_to_SGV(ajedrez: BoardMio) -> str:
    """
    Devuelve el código SVG para mostrar el tablero
    :param ajedrez: Un tablero
    :return: El código SVG
    """
    res: str = svg.board(ajedrez)
    return res


def tablero_to_ctkImage(ajedrez: BoardMio, ancho: int, alto: int):
    res: str = ajedrez_to_SGV(ajedrez)

    # Conseguimos los bytes en para png
    image_data: bytes = cairosvg.svg2png(res, output_width=ancho, output_height=alto)

    # Creamos la imagen compatible con CustomTkinker
    image: Image = Image.open(io.BytesIO(image_data))
    img = ctk.CTkImage(image, image, size=(ancho, alto))
    return img


def escribr_svg(codigo: str, nombre_fichero: str = "resultado.svg"):
    """
    Escribe el fichero SVG
    :param codigo: El código SVG
    :param nombre_fichero: El nombre del fichero donde lo quieras escribir
    """
    with open(nombre_fichero, "w") as fichero:
        fichero.write(codigo)


def enrroque(chess1: BoardMio, chess2: BoardMio) -> (str, str, str, bool) or (None, None, None, None):
    """
    Comprueba si ha habido enrroque entre los 2 tableros
    :param chess1: Pirmer tablero
    :param chess2: Segundo tablero
    :return: Una tula con el resultado. ("Origen del Rey", "Destino del rey", "O-O | O-O-O", Color)
    """

    # Recorremos los colores de las fichas
    colores: (bool, bool) = (chess.WHITE, chess.BLACK)  # True -> Blanco | False -> Negro
    for color in colores:

        # Almacenamos las posiciones del rey y las nuevas de las torres de este detemrinado color
        posicion_rey = chess1.king(color)
        posicion_rey_nueva = chess2.king(color)
        posiciones_torres_nueva = list(chess2.pieces(chess.ROOK, color))

        # Depende de la disposicion del tablero los calculos pueden varíar, por eso comprobamos 2 veces la posición del
        # rey. El rey y las torres deben acabar en una posición específica del tablero, si no no es enrroque.
        res = None
        if posicion_rey == chess.E8:
            if posicion_rey_nueva == posicion_rey + 2 and (posicion_rey + 1) in posiciones_torres_nueva:
                res = "O-O"
            elif posicion_rey_nueva == posicion_rey - 2 and (posicion_rey - 1) in posiciones_torres_nueva:
                res = "O-O-O"
        elif posicion_rey == chess.E1:  # Tablero del revés
            if posicion_rey_nueva == posicion_rey - 2 and (posicion_rey - 1) in posiciones_torres_nueva:
                res = "O-O-O"
            elif posicion_rey_nueva == posicion_rey + 2 and (posicion_rey + 1) in posiciones_torres_nueva:
                res = "O-O"

        # Si ha habido enrroque devuelve la posicion del rey
        if res is not None:
            return chess.square_name(posicion_rey), chess.square_name(posicion_rey_nueva), res, color
    # Si sale del bucle, devuelve None
    return None, None, None, None


def letra_a_pieza(letra: str) -> str:
    """
    Pasa de letra a nombre de pieza
    :param letra: La letra a procesar
    :return: El nombre y color de la ficha en string
    """
    match letra:
        case "b":
            res = "Alfil negro"
        case "B":
            res = "Alfil blanco"
        case "r":
            res = "Torre negra"
        case "R":
            res = "Torre blanca"
        case "n":
            res = "Caballo negro"
        case "N":
            res = "Caballo blanco"
        case "q":
            res = "Dama negra"
        case "Q":
            res = "Dama blanca"
        case "k":
            res = "Rey negro"
        case "K":
            res = "Rey blanco"
        case "p":
            res = "Peón negro"
        case "P":
            res = "Peón blanco"
        case _:
            res = "Cagaste"
    return res


def ver_el_movimiento_tablero(chess1: BoardMio, chess2: BoardMio) -> (
        (str, str, chess.Piece, str) or (int, str, None, None)):
    """
    Dados 2 tableros, deduce el movimiento LEGAL que ha habido entre los 2. No comprueba el turno del jugador.
    Simplemente se asegura que el movimiento que se haya realizado esta de acuerdo a la normativa del juego y si es
    válido para ser registrado en la BDD. Si ocurre algun problema devuelve una tupla cuyo primer elemento es el
    código de error (int), siendo su segundo su respectivo mensaje de error, indicando el problema

    Requisitos:\n
    - El tablero tiene que estar bien colocado:
       > La cámara tiene que estar grabando desde el lado del enrroque corto\n
       > Las blancas tienen que estar a la izquierda de la cámara
    *(Tambien vale la viceversa)

    :param chess1: Ajedrez previo al movimiento
    :param chess2: Ajedrez posterior al movimiento
    :return: Una tupla simbolizando ("Casilla de origen", "Casilla de destino", Pieza, "O-O | O-O-O | None")
    """

    # **************************************************************
    # *               COMPROBACIONES INICIALES                     *
    # **************************************************************

    # Si es el mismo ajedrez, es que no ha habido ningun movimiento
    if chess1 == chess2:
        return -2, "Tablero es igual al anterior", None, None

    # Comprobar el numero de piezas
    piezas1 = chess1.piece_map()
    piezas2 = chess2.piece_map()

    # Piezas que estan en distinta posicion respecto a la original
    posicion_original = {chess.square_name(k): piezas1[k].symbol() for k in piezas1.keys() - piezas2.keys()}

    # Piezas que estan en distinta posicion respecto a este movimiento
    posicion_final = {chess.square_name(k): piezas2[k].symbol() for k in piezas2.keys() - piezas1.keys()}

    print(posicion_final)

    # print(f"Piezas antes -> {posicion_original}\nPiezas ahora -> {posicion_final}")

    # Si hay menos piezas en el nuevo, sin contando con la posibilidad de que haaya capturado, da fallo
    legal: bool = False
    if len(piezas1) > len(piezas2):  # + 1
        temp = None

        # Tenemos que mirar los 2 colores
        for i in range(2):
            # Obtenemos las posibles capturas en esa posición
            capturas = list(chess1.generate_legal_captures())

            # Obtenemos las fichas que echamos en falta
            temp = {x: posicion_original[x] for x in posicion_original if x not in posicion_final}

            # Vemos si ha habido caputra
            for captura in capturas:
                pieza_inicial = temp.get(chess.square_name(captura.from_square))
                if pieza_inicial is not None:
                    pieza_inicial = chess.Piece.from_symbol(pieza_inicial)
                    pieza_final = chess2.piece_at(captura.to_square)

                    if pieza_final is not None and pieza_final == pieza_inicial:
                        legal = True
                        break
            if not legal:
                chess1.turn = not chess1.turn
            else:
                break

        if not legal:
            # Si no ha encontrado ninguna captura, es que es movimiento ilegal
            mensaje = ""
            for i in temp:
                mensaje += f"\t- {letra_a_pieza(temp.get(i))} en {i.upper()}\n"
            return -3, f"Hay menos piezas que antes en el tablero. Faltan:\n{mensaje}", None, None

    # Si hay mas piezas en el nuevo tablero da fallo
    if len(piezas1) < len(piezas2):
        # Obtenemos las fichas que sobran
        temp = {x: posicion_final[x] for x in posicion_final if x not in posicion_original}
        mensaje = ""
        for i in temp:
            mensaje += f"\t- {letra_a_pieza(temp.get(i))} en {i.upper()}\n"
        return -4, f"Hay mas piezas que antes en el tablero. Hay:\n{mensaje}", None, None

    # Si se ha realizado mas de un movimiento y no han intervenido un rey y una torre (enrroque) da fallo
    if len(posicion_final) > 1 and (
            not set(posicion_original.values()).issubset(("K", "R")) and
            not set(posicion_original.values()).issubset(("r", "k"))
    ):
        mensaje = ""
        for posicion_previa, pieza_previa in posicion_original.items():

            # Encontramos la posición final de la pieza
            for casilla_final, pieza_final in posicion_final.items():

                # Si es la misma pieza y su posicion no es la misma que la final le damos
                if pieza_previa == pieza_final and posicion_previa != casilla_final:
                    mensaje += (f"\t- {letra_a_pieza(pieza_previa)} movida de {posicion_previa.upper()} a "
                                f"{casilla_final.upper()}\n")
                    break

        #  mensaje = f" - Posicion Previa: {str(posicion_original)}\n - Posicion Final: {str(posicion_final)}"
        return -5, f"Se ha hecho un movimiento de mas. Movimientos registrados:\n\n{mensaje}", None, None

    # **************************************************************
    # *                       MOVIMIENTO                           *
    # **************************************************************
    # FIN DE LAS COMPROBACIONES INICIALES. A partir de aquí ya no hay mas returns

    # Definimos las variables globales a retornar
    origen_mov = None
    destino_mov = ""
    pieza = None
    tipo_enrroque = None

    # Recorremos ambos colores
    for i in range(2):
        # Recorremos las jugadas legales posibles
        for move in chess1.legal_moves:
            chess1.push(move)

            # Si tras realizar la jugada ambos tableros son iguales, ya la tenemos
            if chess1.board_fen() == chess2.board_fen():
                # Sacamos la pieza que se ha movido
                pieza = chess1.piece_at(move.to_square)

                # Sacamos la pieza que había antes
                chess1.pop()
                pieza_antes_de_que_llegase = chess1.piece_at(move.to_square)
                pieza_antes_de_mover = chess1.piece_at(move.from_square)

                # Sacar string de las cordenadas
                origen_mov = chess.square_name(move.from_square)

                # Comprobar si hay captura
                destino_mov = chess.square_name(move.to_square) if pieza_antes_de_que_llegase is None else (
                        "x" + chess.square_name(move.to_square)
                )

                # Comprueba que sea un peon y en dependencia del color calcula si se puede comer al paso en la
                # siguiente jugada. Te apuesto lo que quieras, querido lector, a que no sabias ni que existia esto.
                if (
                        pieza.piece_type == chess.PAWN and
                        pieza.color == chess.BLACK and
                        ((move.from_square - 16) == move.to_square)
                ):
                    chess2.casilla_comer_al_paso = move.from_square - 8
                elif (
                        pieza.piece_type == chess.PAWN and
                        pieza.color == chess.WHITE and
                        ((move.from_square + 16) == move.to_square)
                ):
                    chess2.casilla_comer_al_paso = move.from_square + 8
                else:
                    chess2.casilla_comer_al_paso = None

                # Controlar las coronaciones/promociones
                if (pieza_antes_de_mover.piece_type == chess.PAWN and
                        pieza.piece_type in (chess.QUEEN, chess.ROOK, chess.KNIGHT, chess.BISHOP)):
                    destino_mov += f"={pieza.symbol()}"

                # Comprobar jaque
                destino_mov = comprobar_jaque(chess2, destino_mov)

                break
            else:
                chess1.pop()
        chess1.turn = not chess1.turn

    if origen_mov is None:
        # Enroque
        origen_mov, destino_mov, tipo_enrroque, color = enrroque(chess1, chess2)
        if color is not None:
            # Comprueba la pieza que ha movido en funcion del color
            pieza = "K" if color == chess.WHITE else "k"
            pieza = chess.Piece.from_symbol(pieza)
        elif chess1.casilla_comer_al_paso is not None and chess2.piece_at(chess1.casilla_comer_al_paso) is not None:
            # Comer al paso
            # Mira que en el tablero anterior se pueda comer al paso y que en el actual hay una ficha donde antes se
            # podía comer al paso
            # + ----------------------------
            # Obtiene la pieza que esta ahí, donde estaba antes y la asigna a la variable que corresponda
            pieza = chess2.piece_at(chess1.casilla_comer_al_paso)
            origen_mov = list(posicion_original.keys())[1]
            destino_mov = "x" + chess.square_name(chess1.casilla_comer_al_paso)

            # Comprobar jaque
            destino_mov = comprobar_jaque(chess2, destino_mov)
        else:
            # Si ha llegado aquí, es un movimiento ilegal
            mensaje = f" - Posicion Previa: {str(posicion_original)}\n - Posicion Final: {str(posicion_final)}"
            origen_mov = -1
            destino_mov = f"Es un movimiento ilegal:\n{mensaje}"

    return origen_mov, destino_mov, pieza, tipo_enrroque


def comprobar_jaque(chess2, destino_mov):
    for i in range(2):
        if chess2.is_check():
            destino_mov += "+"
            break
        chess2.turn = not chess2.turn
    return destino_mov


# 0-0-0
# -> R2K3R/PPP1QPPP/2N1P2N/3P1B1B/3p4/2n1p3/ppp2ppp/r1bkqbnr
# -> R3RK2/PPP1QPPP/2N1P2N/3P1B1B/3p4/2n1p3/ppp2ppp/r1bkqbnr
# O-O
# -> "R2KQBNR/PPP1PPPP/2N5/3P1B2/3p4/2n1p3/ppp2ppp/r1bkqbnr"
# -> "1KR1QBNR/PPP1PPPP/2N5/3P1B2/3p4/2n1p3/ppp2ppp/r1bkqbnr"
# O-O-O - Del reves
# -> "bbrknrqn/ppp2ppp/4p3/3p4/3P4/7N/PPPQPPPP/R3KBNR"
# -> "bbrknrqn/ppp2ppp/4p3/3p4/3P4/7N/PPPQPPPP/2KR1BNR"
# O-O - Del reves
# -> "bbrknrqn/ppp2ppp/4p3/3p4/2B1P3/3P1N2/PPP2PPP/RNBQK2R"
# -> "bbrknrqn/ppp2ppp/4p3/3p4/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1"
# Peon E4
# -> "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
# -> "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"


if __name__ == "__main__":
    ajedrez1 = crear_ajedrez("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    ajedrez2 = crear_ajedrez("rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R")
    ajedrez3 = crear_ajedrez("rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R")
    ajedrez4 = crear_ajedrez("rnbqkbnr/ppp2ppp/8/3Pp3/8/5N2/PPPP1PPP/RNBQKB1R")

    # print(f"{ajedrez1}\n")
    # print(f"{ajedrez2}\n")
    # print(f"{ajedrez3}\n")

    origen, destino, piez, pieza_coronada = ver_el_movimiento_tablero(ajedrez1, ajedrez2)
    print(origen, destino, piez, pieza_coronada)

    # origen, destino, piez, pieza_coronada = ver_el_movimiento_tablero_bueno(ajedrez2, ajedrez3)
    # print(origen, destino, piez, pieza_coronada)

    # origen, destino, piez, pieza_coronada = ver_el_movimiento_tablero_bueno(ajedrez3, ajedrez4)
    # print(origen, destino, piez, pieza_coronada)
