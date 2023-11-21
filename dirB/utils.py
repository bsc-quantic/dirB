import time
import h5py

def esperarDesbloqueoDeHDF5(pathDelFichero: str, numIntentosMaximo: int = 120, segundosDeSleep: int = 0.1):
    """Medida de sanidad en moficación de HDF5: Verificar que HDF5 está desbloqueado.

    :param str pathDelFichero: path completo del fichero HDF5 a esperar
    :param int numIntentosMaximo: número máximo de intentos a la hora de probar si el fichero sigue bloqueado
    :param int segundosDeSleep: tiempo en segundos entre intentos.
    """

    numeroDeIntentos = 0
    desbloqueado = False
    
    while not(desbloqueado):
        numeroDeIntentos = numeroDeIntentos + 1

        try:
            f = h5py.File(pathDelFichero, "r")           
            f.close()
            time.sleep(segundosDeSleep)
            desbloqueado=True

        except:
            time.sleep(segundosDeSleep)
            if numeroDeIntentos >= numIntentosMaximo:
                cadena = 'Problemas al crear el fichero de salida ' + pathDelFichero + ' revisar'
                raise  ValueError(cadena)