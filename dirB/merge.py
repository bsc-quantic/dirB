import os

from typing import List

from dirB.base import zsan_DirB
from dirB.utils import esperarDesbloqueoDeHDF5

def mergeListaDeHDF5(listaDeFicheros: List[str], ficheroDeSalida: str):
    """Fusiona todos los ficheros de la lista en un único fichero con nombre 'ficheroDeSalida'

    :param List[str] listaDeFicheros: lista de nombres de ficheros a ser combinados
    :param str ficheroDeSalida: nombre del fichero resultante
    """
    
    print("NOT IMPLEMENTED YET")
    
    return None

def mergeDeDosDirB(el_ID_deUnDirB, el_ID_deOtroDirB, ID_NuevoDirB, directorio: str = os.getcwd()):
    """Fusiona las soluciones de dos DIRB. Se asume que ambos tienen el mismo CASO 
    
        Se asume que ambos tienen el mismo CASO y atributos de caso
        Se crea un nuevo DirB, con el nombre pasado en ID_NuevoDirB
        La llamada "natural" (ver documentación de la calse zsan_DirB) a este metodo sería:
           == (se usa "cadena": para no sobre-cargar
        nuevo = zsan_DirB('01_01_2020_cadena_VERSION01', '01_01_2020_cadena_VERSION01, '01_01_2020_cadena')
        si directorio = None ==> Directorio actual
        NOTA: Si hay que fusionar más de dos dir-b se puede llamar recursivo, a la espera de crear un metodo
              especifico que reciba una lista de dir-b's a fusiones

        :param str el_ID_deUnDirB: identificador del caso #1 a combinar
        :param str el_ID_deOtroDirB: identificador del caso #2 a combinar
        :param str ID_NuevoDirB: identificador del caso resultante (combinado)
        :param str: directorio: directorio donde se esperan encontrar los casos
    """

    fichero1 = el_ID_deUnDirB + '.hdf5'
    fichero2 = el_ID_deOtroDirB + '.hdf5'    
    ficheroSalida = ID_NuevoDirB + '.hdf5'
    fullPath1 = os.path.join(directorio, fichero1)
    fullPath2 = os.path.join(directorio, fichero2)  
    fullPathSalida = os.path.join(directorio, ficheroSalida)     

    if not(os.path.exists(fullPath1)):
        cadena = 'El fichero ' + fullPath1 + ' no existe '
        raise ValueError(cadena)
    if not(os.path.exists(fullPath2)):
        cadena = 'El fichero ' + fullPath2 + ' no existe '
        raise ValueError(cadena)   
    if (os.path.exists(fullPathSalida)):
        cadena = 'El fichero ' + fullPathSalida + ' YA EXISTE == REVISAR  '
        raise ValueError(cadena)           

    # Por no liarnos....
    #  copiamos el primero de los ficheros y el cambiamos el nombre
    #  volcamos las soluciones de la segund solución en el nuevo fichero
    # shutil.copyfile(fullPath1, fullPathSalida)
    os.rename(fullPath1, fullPathSalida)
    
    esperarDesbloqueoDeHDF5(fullPathSalida)  # Criterio de finalización de proceso: se puede bloquear fichero

    dirB1 = zsan_DirB();    dirB1.cargaCaso(ID_NuevoDirB)
    dirB2 = zsan_DirB();    dirB2.cargaCaso(el_ID_deOtroDirB)

    # Añadimos las soluciones del segundo al fichero de salida
    for numDeSolucion in dirB2.listaSoluciones:
        dirB1.guardaNuevaSolucion(dirB2.recuperaCasoComoDiccionario(), dirB2.atributosDeUnaSolucion(numDeSolucion))
                
    esperarDesbloqueoDeHDF5(fullPathSalida)
    
    return dirB1