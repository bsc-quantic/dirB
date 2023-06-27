import os

from typing import List

from dirB.base import zsan_DirB
from dirB.utils import esperarDesbloqueoDeHDF5

def _checkPathExists(pathToCheck: str, errorMessage: str):
    if not(os.path.exists(pathToCheck)):
        raise ValueError(errorMessage)

def mergeListaDeHDF5(nombresDeFichero: List[str], nombreDefichero_salida: str, directorio: str = os.getcwd()):
    """Fusiona todos los ficheros de la lista en un único fichero con nombre 'ficheroDeSalida'

    :param List[str] nombresDeFichero: lista de nombres de ficheros a ser combinados
    :param str nombreDefichero_salida: nombre del fichero resultante
    :param str directorio: directorio donde se esperan encontrar los casos
    """

    
    return None

def mergeDeDosDirB(nombreDeFichero1: str, nombreDeFichero2: str, nombreDeFichero_salida: str, directorio: str = os.getcwd()):
    """ Fusiona las soluciones de dos dirB. Se asume que ambos tienen el mismo Caso.
        Los datos de los ficheros 'nombreDeFichero1' y 'nombreDeFichero2' se combinarán en un solo fichero de salida 'nombreDeFichero_salida'.

        :param str nombreDeFichero1: nombre del fichero a combinar #1 (identificador del caso #1)
        :param str nombreDeFichero2: nombre del fichero a combinar #1 (identificador del caso #1)
        :param str nombreDeFichero_salida: nombre del fichero de salida
        :param str directorio: directorio donde se esperan encontrar los casos
    """

    fullPath1 = os.path.join(directorio, nombreDeFichero1)
    fullPath2 = os.path.join(directorio, nombreDeFichero2)  
    fullPathSalida = os.path.join(directorio, nombreDeFichero_salida)     

    _checkPathExists(fullPath1, 'El fichero ' + fullPath1 + ' no existe ')
    _checkPathExists(fullPath2, 'El fichero ' + fullPath2 + ' no existe ')
    _checkPathExists(fullPathSalida, 'El fichero ' + fullPathSalida + ' YA EXISTE == REVISAR  ')         

    os.rename(fullPath1, fullPathSalida)
    esperarDesbloqueoDeHDF5(fullPathSalida)

    dirB1 = zsan_DirB();    dirB1.cargaCaso(nombreDeFichero_salida)
    dirB2 = zsan_DirB();    dirB2.cargaCaso(nombreDeFichero2)

    for numDeSolucion in dirB2.listaSoluciones:
        dirB1.guardaNuevaSolucion(dirB2.recuperaSolucionComoDiccionario(numDeSolucion), dirB2.atributosDeUnaSolucion(numDeSolucion))
    esperarDesbloqueoDeHDF5(fullPathSalida)
    
    return dirB1