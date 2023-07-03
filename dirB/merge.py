import os
import shutil
from typing import List, Dict

from dirB.base import zsan_DirB
from dirB.utils import esperarDesbloqueoDeHDF5

def _atributosDeCasosIguales(nombreDelCasoBase: str, listaDeFicherosConSoluciones: List[str]) -> bool:
    
    return True

def mergeListaDeSoluciones(nombreDelCasoBase: str, listaDeFicherosConSoluciones: List[str], nombreDeFichero_salida: str, directorio: str = os.getcwd()):
    """Añade la lista de soluciones al caso base proporcionado, dejando el fichero HDF5 resultante en el 'nombreDeFichero_salida'.

    :param str nombreDelCasoBase: nombre del caso base al que añadir la soluciones
    :param List[str] listaDeFicherosConSoluciones: lista de nombres de ficheros que contienen las soluciones a ser añadidas la caso base
    :param str nombreDefichero_salida: nombre del fichero resultante
    :param str directorio: directorio donde se esperan encontrar los casos
    """
    
    # Initial checks
    fullPathSalida = os.path.join(directorio, nombreDeFichero_salida)
    if os.path.exists(fullPathSalida): raise ValueError('El fichero ' + fullPathSalida + ' YA EXISTE == REVISAR  ')

    for fichero in listaDeFicherosConSoluciones:
        fullPath = os.path.join(directorio, fichero)
        if not os.path.exists(fullPath): raise ValueError('El fichero ' + fullPath + ' no existe ')

    if not _atributosDeCasosIguales(nombreDelCasoBase, listaDeFicherosConSoluciones):
        user_input = input('Los atributos de caso de los ficheros proporcionados no coinciden. Continuar con el merge? (Y/n)')
        if user_input.lower() == "n": exit(0)

    # Prepare resulting file
    shutil.copy(nombreDelCasoBase, fullPathSalida)

    # Get all the dicts from the list of solution files and add them all in the resulting file
    listaDeSoluciones: List[Dict] = []
    listaDeAtributosDeSoluciones: List[Dict] = []

    dirB_salida = zsan_DirB();    dirB_salida.cargaCaso(nombreDeFichero_salida, directorio)
    for nombreDeFichero in listaDeFicherosConSoluciones:
        dirB_aux = zsan_DirB();    dirB_aux.cargaCaso(nombreDeFichero, directorio)

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