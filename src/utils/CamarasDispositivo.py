from windows_capture_devices import get_capture_devices


def conseguir_camaras_dispositivo() -> dict[str, int]:
    """
    Devuelve un diccionario con las camaras disponibles y su identificador en OpenCV

    :return: un diccionario con las cámaras disponibles y su identificador en OpenCV
    """
    camaras = dict()
    device_list = get_capture_devices()
    for i in range(len(device_list)):
        camaras[device_list[i]] = i
    return camaras
