import os
import sqlite3 as sql
import datetime
import sys
from typing import Tuple


class Conexion:
    """
    Clase dedicada a gestionar la base de Datos usando el patrón de diseño Singleton
    """

    # Ruta hacia la base de datos
    UBICACION_DEFECTO_BDD: str = "_internal/ajedrez.sqlite3"

    _instancia = None

    def __new__(cls, base_de_datos: str = UBICACION_DEFECTO_BDD):
        if not cls._instancia:
            cls._instancia = super(Conexion, cls).__new__(cls)

            ruta: str = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
            base_de_datos = os.path.join(ruta, base_de_datos)

            cls._instancia.con = sql.connect(base_de_datos)
            cls._instancia.con.execute("PRAGMA foreign_keys = ON")

            # Usando la instancia que tenemos creandose,
            # comprobamos que las tablas existen en la base de datos a traves de la tabla master
            cur1 = cls._instancia.con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='partida'")
            if cur1.fetchone() is None:
                cls.crear_tabla_partidas(cls._instancia)

            cur1 = cls._instancia.con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movimiento'")
            if cur1.fetchone() is None:
                cls.crear_tabla_movimientos(cls._instancia)

            cur1.close()

        return cls._instancia

    def mirar_conexion(self) -> bool:
        """
        Comprueba el estado de la conexión con la BDD
        :return: True si se mantiene activa y False si no se mantiene activa
        """
        try:
            self._instancia.con.cursor()
            return True
        except sql.Error:
            return False

    def cerrar_conexion(self):
        """
        Cierra la conexion con la BDD
        """
        self._instancia.con.close()

    def crear_tabla_partidas(self):
        """
        Crea las tablas de partidas en la base de datos si no existe
        """
        cur: sql.Cursor = self._instancia.con.cursor()
        ejecucion: str = f'''
            CREATE TABLE IF NOT EXISTS partida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                fecha DATE NOT NULL
            );'''

        try:
            cur.execute(ejecucion)
            self._instancia.con.commit()
        except sql.Error as e:
            print(e)

        cur.close()

    def crear_tabla_movimientos(self):
        """
        Crea las tabla de movimiento en la base de datos si no existe, junto con su clave foranea
        """
        cur: sql.Cursor = self._instancia.con.cursor()
        ejecucion: str = f'''
            CREATE TABLE IF NOT EXISTS movimiento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pieza TEXT NOT NULL,
                cordenada TEXT NOT NULL,
                fecha DATE NOT NULL, 
                FEN TEXT, 
                partida_id INTEGER,
                
                CONSTRAINT fk_movimeinto_partida FOREIGN KEY (partida_id) REFERENCES partida(id) ON DELETE CASCADE ON UPDATE CASCADE
            );'''

        try:
            cur.execute(ejecucion)
            self._instancia.con.commit()
        except sql.Error as e:
            print(e)

        cur.close()

    def insertar_partidas(self, datos: Tuple[str, str]) -> int:
        """
        Inserta una partida en la BDD y devuelve el nuevo ID insertado
        :param datos: 1. El Nombre de la partida | 2. La fecha de la partida
        :return: El nuevo ID insertado
        """
        cur: sql.Cursor = self._instancia.con.cursor()

        cur.execute("INSERT INTO partida(nombre, fecha) VALUES (?,?)", datos)
        newID: int = cur.lastrowid

        self._instancia.con.commit()
        cur.close()
        # print(f"Nuevo id {newID}")
        return newID

    def insertar_movimientos(self, datos: list[(str, str, str, str, int)]):
        """
        Inserta un movimiento o varios en la base de datos

        :param datos: 1.Pieza | 2.Coordenada | 3.Fecha | 4.Color | 5.Enrroque | 6.Partida (int)
        """
        cur: sql.Cursor = self._instancia.con.cursor()

        try:
            cur.executemany(
                "INSERT INTO movimiento(pieza, cordenada, fecha, FEN, partida_id) VALUES (?,?,?,?,?)",
                datos
            )
            self._instancia.con.commit()
        except sql.Error as e:
            print(e)
            self._instancia.con.rollback()

        cur.close()

    def recuperar_partidas(self) -> list:
        """
        Devuelve una lista con todas las partidas
        :return: Una lista con todas las partidas
        """
        cur: sql.Cursor = self._instancia.con.execute("SELECT id, nombre, fecha FROM partida ORDER BY fecha DESC")
        res: list = cur.fetchall()
        cur.close()
        return res

    def recuperar_id_utlima_partida(self) -> int:
        """
        Devuelve el ID de la ultima partida
        :return: El ID de la última partida
        """
        cur: sql.Cursor = self._instancia.con.execute("SELECT id FROM partida ORDER BY fecha DESC LIMIT 1")
        res = cur.fetchone()
        cur.close()
        return res[0]

    def cargarse_partidas(self, id_partida: int):
        """
        Borra la partida que le indiques
        :param id_partida: El ID de la partida a borrar
        """
        cur: sql.Cursor = self._instancia.con.cursor()

        try:
            cur.execute("DELETE FROM partida WHERE id = ?", [id_partida])
            self._instancia.con.commit()
        except sql.Error as e:
            print(e)
            self._instancia.con.rollback()

        cur.close()

    def recuperar_movimientos(self, id_partida: int) -> list:
        """
        Obtiene los movimientos de la partida con el ID que le indiques
        :param id_partida: El id de la partida a ver los movimientos
        :return: Una lista con todos los movimientos
        """
        cur: sql.Cursor = self._instancia.con.execute(
            '''
            SELECT id, pieza, cordenada, fecha, FEN
            FROM movimiento 
            WHERE partida_id = ? ORDER BY fecha''',
            [id_partida]
        )
        res: list = cur.fetchall()
        cur.close()
        return res

    def cargarse_movimientos(self, id_movimiento: int):
        """
        Borra el movimiento que le indiques

        :param id_movimiento: El ID del movimiento a borrar
        """
        cur: sql.Cursor = self._instancia.con.cursor()
        try:
            cur.execute("DELETE FROM movimientos WHERE id = ?", [id_movimiento])
            self._instancia.con.commit()
        except sql.Error as e:
            print(e)
            self._instancia.con.rollback()

        cur.close()

    def __insertar_datos_ejemplo(self):
        """
        Inserta algunos datos de ejemplo
        """
        self.insertar_partidas(("Juancha vs Manolo", str(datetime.datetime(2021, 2, 2))))

        # print(str(datetime.datetime(2023, 6, 1)))

        self.insertar_partidas(("Jose vs Manolo", str(datetime.datetime(2023, 6, 1))))

        # ("Juancha vs Manolo", str(datetime.datetime(2021, 2, 2))),
        # ("Ramon vs Manolo", str(datetime.datetime(2022, 5, 1))),
        # ("Manuel vs Kasparov", str(datetime.datetime.now()))

        self.insertar_movimientos(
            [
                ("Peon", 1, "E4", str(datetime.datetime.now()), 3),
                ("Peon", 0, "E5", str(datetime.datetime.now()), 3),
                ("Caballo", 1, "F3", str(datetime.datetime.now()), 3),
                ("Peon", 0, "D6", str(datetime.datetime.now()), 3),
                ("Alfil", 1, "C4", str(datetime.datetime.now()), 3),
                ("Caballo", 0, "F6", str(datetime.datetime.now()), 3),
            ]
        )


if __name__ == '__main__':
    con = Conexion()
    con.insertar_partidas(("Prueba", str(datetime.datetime.now())))
