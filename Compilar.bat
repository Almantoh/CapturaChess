poetry run pyinstaller -D -w ^
-p "src/reconocimiento;src/interfaz;src/IA;src/baseDeDatos;" ^
--name "CapturaChess" ^
--add-data "src/_internal/resultados:./resultados" ^
--add-data "src/_internal/icons:./icons"  ^
--add-data "src/_internal/fuentes:./fuentes"  ^
--add-data "D:/PoetryCache/virtualenvs/04-lagloriosa-mAynO3wB-py3.12/Lib/site-packages/ultralytics/cfg/default.yaml:./ultralytics/cfg" ^
--icon "src/_internal/icons/icon.png" ^
src\main.py
