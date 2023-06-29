import os

from typing import List, Dict

from dirB.base import zsan_DirB
from dirB.utils import esperarDesbloqueoDeHDF5


def mergeListaDeHDF5(nombresDeFichero: List[str], nombreDeFichero_salida: str, directorio: str = os.getcwd()):
    """Fusiona todos los ficheros de la lista en un único fichero con nombre 'ficheroDeSalida'

    :param List[str] nombresDeFichero: lista de nombres de ficheros a ser combinados
    :param str nombreDefichero_salida: nombre del fichero resultante
    :param str directorio: directorio donde se esperan encontrar los casos
    """
    
    fullPathSalida = os.path.join(directorio, nombreDeFichero_salida)
    if os.path.exists(fullPathSalida): raise ValueError('El fichero ' + fullPathSalida + ' YA EXISTE == REVISAR  ')

    for fichero in nombresDeFichero:
        fullPath = os.path.join(directorio, fichero)
        if not os.path.exists(fullPath): raise ValueError('El fichero ' + fullPath + ' no existe ')

    os.rename(nombresDeFichero[0], fullPathSalida)
    esperarDesbloqueoDeHDF5(fullPathSalida, segundosDeSleep=0.1)

    listaDeSoluciones: List[Dict] = []
    listaDeAtributosDeSoluciones: List[Dict] = []

    dirB_salida = zsan_DirB();    dirB_salida.cargaCaso(nombreDeFichero_salida)
    for nombreDeFichero in nombresDeFichero[1:]:
        dirB_aux = zsan_DirB();    dirB_aux.cargaCaso(nombreDeFichero)

        for numDeSolucion in dirB_aux.listaSoluciones:
            solucion = dirB_aux.recuperaSolucionComoDiccionario(numDeSolucion)
            atributosDeSolucion = dirB_aux.atributosDeUnaSolucion(numDeSolucion)

            listaDeSoluciones.append(solucion)
            listaDeAtributosDeSoluciones.append(atributosDeSolucion)

    dirB_salida.guardaNuevasSoluciones(listaDeSoluciones, listaDeAtributosDeSoluciones)
    esperarDesbloqueoDeHDF5(fullPathSalida)

    return dirB_salida

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

    if not os.path.exists(fullPath1): raise ValueError('El fichero ' + fullPath1 + ' no existe ')
    if not os.path.exists(fullPath2): raise ValueError('El fichero ' + fullPath2 + ' no existe ')
    if os.path.exists(fullPathSalida): raise ValueError('El fichero ' + fullPathSalida + ' YA EXISTE == REVISAR  ')

    os.rename(fullPath1, fullPathSalida)
    esperarDesbloqueoDeHDF5(fullPathSalida)

    dirB1 = zsan_DirB();    dirB1.cargaCaso(nombreDeFichero_salida)
    dirB2 = zsan_DirB();    dirB2.cargaCaso(nombreDeFichero2)

    for numDeSolucion in dirB2.listaSoluciones:
        dirB1.guardaNuevaSolucion(dirB2.recuperaSolucionComoDiccionario(numDeSolucion), dirB2.atributosDeUnaSolucion(numDeSolucion))
    esperarDesbloqueoDeHDF5(fullPathSalida)
    
    return dirB1