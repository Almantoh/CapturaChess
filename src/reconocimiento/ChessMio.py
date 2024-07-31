from chess import Board
import chess


class BoardMio(Board):
    def __init__(self, fen: str = chess.STARTING_FEN):
        """
        Subclase que hereda de Board para incluirle la casilla disponible en esa jugada para comer al paso
        :param fen: El tablero en formato FEN
        """
        super().__init__(fen)

        # Variable local
        self._casilla_comer_al_paso = None

    def get_casilla_comer_al_paso(self) -> int:
        return self._casilla_comer_al_paso

    def set_casilla_comer_al_paso(self, value: int):
        self._casilla_comer_al_paso = value

    casilla_comer_al_paso = property(get_casilla_comer_al_paso, set_casilla_comer_al_paso)
