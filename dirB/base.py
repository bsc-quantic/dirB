import pandas as pd
import os
import h5py
import uuid
import json
import pathlib
from datetime import datetime
from typing import Dict, List, Tuple

from dirB.utils import esperarDesbloqueoDeHDF5


class zsan_DirB:
    """
    Clase para el tratamiento de ficheros DIR-B, implementados sobre HDF5. La estructura de estos ficheros es sencilla:
        
        /CASO
            JSON_IN
        /SOLUCIONES
            1
                JSON_OUT_1
            2
                JSON_OUT_2
            ...

            N
                JSON_OUT_N

    La '/' representa la raíz del fichero. El campo CASO contiene un conjunto de metadatos y un fichero JSON con los parámetros generales que definin el caso.

    Cada solución se guarda por defecto con un número, que, de la misma manera, contiene un conjunto de metadatos y un fichero JSON con los valores resultantes. Todos estos valores son no estructurados. En otras palabras, pueden tener un nombre y un tipo arbitrario, definidos por el usuario en función de sus propias necesidades. La cantidad de valores de salida también es arbitraria.
    """

    def __init__(self):
        self._nombreDeFichero: str = None
        self._fullPath: str = None
        self._directorio: str = None

        self._dicAtrCaso: Dict = None
        self._dicAtrSoluciones: Dict = None
        
        self._dataFrameAtributosCaso = None
        self._dataFrameAtributosSoluciones = None

        self._listaSoluciones: List = None
        self._numeroSoluciones: int = None
    
    def __repr__(self):
        """ Resumen del DIR-B  mostrando el atributo de la clase dataFrameAtributos. Se llama con print(unDIR-B)
        """
        cadena = '\n ===>  Descripción DIR-B ' + self.nombreDeFichero
        cadena += '\n'

        if self.dicAtrCaso: 
            cadena += '\n **** Atributos del CASO incluido en el DIR-B  ****** '
            cadena += '\n'
            aux = self.dataFrameAtributosCaso.to_string()
            cadena += aux
        else:
            cadena += '\n **** En el CASO no han sido cargados atributos  ****** \n'
        cadena += '\n'
        
        
        if self.numeroSoluciones == 0:
            cadena += '\n **** Aún no se han cargado soluciones en el DIR-B ****** '
            cadena += ' \n'          
        else:
            if self.dicAtrSoluciones:      
                cadena += '\n **** Atributos de soluciones incluidas en el DIR-B ****** '
                cadena += ' \n'
                cadena += ' \n'      
                cadena += str(self.dataFrameAtributosSoluciones)
                cadena += ' \n'
            else:
                cadena += '\n **** NO hay ATRIBUTOS cargados en las SOLUCIONES el DIR-B  ****** \n'
        cadena += '\n'         
        return cadena
    
    @property
    def nombreDeFichero(self):
        return self._nombreDeFichero
    
    @property
    def fullPath(self):
        return self._fullPath
    
    @property
    def directorio(self):
        return self._directorio
    
    @property
    def dicAtrCaso(self):
        return self._dicAtrCaso
    
    @property
    def dicAtrSoluciones(self):
        return self._dicAtrSoluciones
    
    @property
    def dataFrameAtributosCaso(self):
        return self._dataFrameAtributosCaso

    @property
    def dataFrameAtributosSoluciones(self):
        return self._dataFrameAtributosSoluciones

    @property
    def listaSoluciones(self):
        return self._listaSoluciones
    
    @property
    def numeroSoluciones(self):
        return self._numeroSoluciones

    @nombreDeFichero.setter
    def nombreDeFichero(self, new_nombreDeFichero: str):
        self._nombreDeFichero = new_nombreDeFichero

    @fullPath.setter
    def fullPath(self, new_fullPath: str):
        self._fullPath = new_fullPath

    @directorio.setter
    def directorio(self, new_directorio: str):
        self._directorio = new_directorio

    @dicAtrCaso.setter
    def dicAtrCaso(self, new_dicAtrCaso: str):
        self._dicAtrCaso = new_dicAtrCaso
    
    @dicAtrSoluciones.setter
    def dicAtrSoluciones(self, new_dicAtrSoluciones: str):
        self._dicAtrSoluciones = new_dicAtrSoluciones
    
    @dataFrameAtributosCaso.setter
    def dataFrameAtributosCaso(self, new_dataFrameAtributosCaso: str):
        self._dataFrameAtributosCaso = new_dataFrameAtributosCaso

    @dataFrameAtributosSoluciones.setter
    def dataFrameAtributosSoluciones(self, new_dataFrameAtributosSoluciones: str):
        self._dataFrameAtributosSoluciones = new_dataFrameAtributosSoluciones

    @listaSoluciones.setter
    def listaSoluciones(self, new_listaSoluciones: str):
        self._listaSoluciones = new_listaSoluciones

    @numeroSoluciones.setter
    def numeroSoluciones(self, new_numeroSoluciones: str):
        self._numeroSoluciones = new_numeroSoluciones

    def creaNuevoCaso(self, diccionarioDeParamsInput: Dict, diccionarioDeMetadatos: Dict = None, 
                      directorio: str = os.getcwd(), 
                      nombreDeFichero: str = str(datetime.now().strftime("%Y-%m-%dT%H.%M.%S")) + '_' + str(uuid.uuid4()) + '.hdf5'):
        """Crea un nuevo caso teniendo en cuenta el dataset principal y los metadatos proporcionados.

        :param Dict diccionarioDeParamsInput: dataset principal en formato JSON. Contiene los parámetros de entrada del caso.
        :param Dict diccionarioDeMetadatos: diccionario con los metadatos del caso.
        :param str directorio: directorio donde se creará el caso.
        :param str nombreDeFichero: nombre del fichero HDF5 que se utilizará.
        """

        if pathlib.Path(nombreDeFichero).suffix != ".hdf5":
            raise ValueError("El fichero " +  nombreDeFichero + " no tiene extensión HDF5.")
        
        fullPath = os.path.join(directorio, nombreDeFichero)
        with h5py.File(fullPath, 'w') as f:
            caso = f.create_group('CASO')
            
            caso.create_dataset('JSON_IN',
                                data=json.dumps(diccionarioDeParamsInput, ensure_ascii=False), 
                                dtype=h5py.string_dtype(encoding='utf-8'))

            if diccionarioDeMetadatos:
                for key, value in diccionarioDeMetadatos.items():
                    caso.attrs[key] = value
                    
        esperarDesbloqueoDeHDF5(fullPath)

        self._actualizaMiembros(nombreDeFichero, fullPath, directorio)
    
    def cargaCaso(self, nombreDeFichero: str, directorio: str = os.getcwd()):
        """Carga un caso identificado por su nombre de fichero.
        
        :param str nombreDeFichero: nombre del fichero con el caso a cargar (identificador).
        :param str directorio: directorio desde donde se cargará el caso.

        """
        fullPath = os.path.join(directorio, nombreDeFichero)

        if not(os.path.exists(fullPath)):
            raise ValueError('El fichero ' + fullPath + ' no existe.')
        
        self._actualizaMiembros(nombreDeFichero, fullPath, directorio)
    
    def _actualizaMiembros(self, nombreDeFichero: str, fullPath: str, directorio: str = os.getcwd()):
        self.nombreDeFichero = nombreDeFichero        
        self.fullPath = fullPath
        self.directorio = directorio
        
        self._actualizaMiembrosDerivados()

    def _actualizaMiembrosDerivados(self):
        self.dicAtrCaso, self.dicAtrSoluciones = self._getDiccionariosDeAtributos(self.fullPath)

        self.dataFrameAtributosCaso = self._getDataFrameResumenAtributosCaso(self.dicAtrCaso)
        self.dataFrameAtributosSoluciones = self._getDataFrameResumenAtributosSoluciones(self.dicAtrSoluciones)        
        
        self.listaSoluciones = list(self.dicAtrSoluciones.keys())
        self.numeroSoluciones = len(self.listaSoluciones)

    def _getDiccionariosDeAtributos(self, nombreDelFichero: str) -> Tuple[Dict, Dict]:
        """Lee estructura de un fichero dirB y consigue los diccionarios de metadatos del caso y de las SOLUCIONES.

        :param str nombreDelFichero: fichero a leer.
        """

        with h5py.File(nombreDelFichero, 'r') as f:
            dicAtrCaso = {}
            dicAtrCaso = {key: value for key, value in f['/CASO'].attrs.items() }

            # Podría ser que no existieran SOLUCIONES por se un DIR-B recién creado.
            try: 
                listaDeSoluciones = list(f['/SOLUCIONES'])
            except:
                listaDeSoluciones = []
                
            dicAtrSoluciones = {}    
            for numSolucion in listaDeSoluciones:
                cadenaPathSolEnCurso = '/SOLUCIONES/' + numSolucion
                dicAtrSoluciones[numSolucion] = { key: value for key, value in f[cadenaPathSolEnCurso].attrs.items() }
              
        esperarDesbloqueoDeHDF5(nombreDelFichero)
        
        return dicAtrCaso, dicAtrSoluciones
    
    def _getDataFrameResumenAtributosCaso(self, diccionarioAttrs: Dict) -> pd.Series:
        """Devuelve un dataframe (objecto pandas.Series) con atributos del Caso.

        :param Dict diccionarioAttrs: diccionario a partir del cual se genera el dataframe de salida
        """

        if len(diccionarioAttrs) != 0:
          return pd.Series(diccionarioAttrs)
        else:
          return pd.Series(dtype=int)  # Esencialmente una serie vacia

    def _getDataFrameResumenAtributosSoluciones(self, dicAtrSoluciones: Dict):
        """Devuelve un dataframe resumen de todos los atributos de todas las soluciones (ver comentarios) a partir de diccionario atributos soluciones
        """

        if not(dicAtrSoluciones):
            return pd.DataFrame()  # Un dataFrame vacio
            
        aux = [(caso, dicAtributosAux) for caso, dicAtributosAux in dicAtrSoluciones.items()]
        listaDeClaves = ['SOLUCION  '+str(e[0]) for e in aux]
        listaDeDiccionarios = [e[1] for e in aux]

        return pd.DataFrame.from_records(listaDeDiccionarios, index=listaDeClaves)
    
    def guardaNuevaSolucion(self, diccionarioConEl_JSON_OUT: Dict, diccionarioAtributos: Dict = None):
        """Guarda una nueva solución en el dirB.

        :param Dict diccionarioConEl_JSON_OUT: dataset principal en formato JSON. Contiene los parámetros de entrada del caso.
        :param Dict diccionarioAtributos: diccionario con los metadatos del caso.
        """

        with h5py.File(self.fullPath, 'a') as f:
            if self.numeroSoluciones == 0:
                f.create_group('/SOLUCIONES')   

            cadena = '/SOLUCIONES/' + str(self.numeroSoluciones + 1)
            f.create_group(cadena)

            f[cadena].create_dataset('JSON_OUT', 
                                     data=json.dumps(diccionarioConEl_JSON_OUT, ensure_ascii=False),
                                     dtype=h5py.string_dtype(encoding='utf-8'))

            if diccionarioAtributos:
                for key, value in diccionarioAtributos.items():
                    f[cadena].attrs[key] = value
               
        esperarDesbloqueoDeHDF5(self.fullPath)
        
        self._actualizaMiembrosDerivados()

    def guardaNuevasSoluciones(self, listaDeSoluciones: List[Dict], listaDeAtributosDeSoluciones: List[Dict]):
        """Guarda las nuevas soluciones pasadas por parámetro en el actual dirB.

        :param List[Dict] listaDeSoluciones: lista con los diccionarios que representan las soluciones a guardar.
        :param List[Dict] listaDeAtributosDeSoluciones: lista de los atributos de las soluciones a guardar.
        """

        if len(listaDeSoluciones) != len(listaDeAtributosDeSoluciones):
            raise ValueError("Las listas no tienen el mismo tamaño!")

        with h5py.File(self.fullPath, 'a') as f:
            if self.numeroSoluciones == 0:
                f.create_group('/SOLUCIONES')

            idSolucion: int = self.numeroSoluciones + 1
            for index, solucion in enumerate(listaDeSoluciones):
                pathDeSolucion: str = '/SOLUCIONES/' + str(idSolucion)
                f.create_group(pathDeSolucion)

                f[pathDeSolucion].create_dataset("JSON_OUT",
                                                 data=json.dumps(solucion, ensure_ascii=False),
                                                 dtype=h5py.string_dtype(encoding='utf-8'))
            
                atributosDeSolucion = listaDeAtributosDeSoluciones[index]
                if atributosDeSolucion:
                    for key, value in atributosDeSolucion.items():
                        f[pathDeSolucion].attrs[key] = value

                idSolucion += 1

    def recuperaCasoComoDiccionario(self):
        """Recupera el caso como diccionario (built-in dictionary en Python).
        """

        with h5py.File(self.fullPath, 'r') as f:
            salida = json.loads(f['/CASO/JSON_IN'][()].decode("utf-8"))
           
        esperarDesbloqueoDeHDF5(self.fullPath)
        return salida      
      
    def recuperaSolucionComoDiccionario(self, numeroDeSolucion: int) -> Dict:
        """Recupera un numero de solucion como diccionario Python (built-in Dict).

        :param int numeroDeSolucion: identificador de la solución a recuperar.
        :returns Dict:
        """
        
        numeroDeSolucion = str(numeroDeSolucion)
        if not numeroDeSolucion in self.listaSoluciones:
            raise ValueError('No existe número de caso ', numeroDeSolucion)
        
        with h5py.File(self.fullPath, 'r') as f:
            cadena = '/SOLUCIONES/' + numeroDeSolucion + '/JSON_OUT'

            salida = json.loads(f[cadena][()].decode("utf-8"))
         
        esperarDesbloqueoDeHDF5(self.fullPath) 

        return salida

    def representaAtributosDelCaso(self):
        """Muestra metadatos del caso.
        """

        cadena = '\n ===>  Descripción DIR-B ' + self.nombreDeFichero
        cadena += '\n'
        if self.dicAtrCaso: 
            cadena += '\n **** Atributos del CASO incluido en el DIR-B  ****** '
            cadena += '\n'
            cadena += self.dataFrameAtributosCaso.to_string()
        else:
            cadena += '\n **** En el CASO no han sido cargados atributos  ****** \n'
            
        cadena += '\n'

        print(cadena)

    def representaAtributosDeTodasLasSoluciones(self):
        """Muestra los metadatos de todas las soluciones.
        """
      
        if len(self.dicAtrSoluciones) == 0:
            print('\n Aún no hay soluciones cargadas')
        else:
            for solucion, dicAtri in self.dicAtrSoluciones.items():
                print('SOLUCION ', solucion)

                if not dicAtri:
                    print('   **** SIN ATRIBUTOS ****' )
                else:
                    for atributo, valor in dicAtri.items():
                        print('   ', atributo, ' ===> ', valor)
                
    def listaSolucionesQueTienenDeterminadoAtributo(self, campo: int | str) -> List:
        """Devuelve todas las soluciones que tengan el campo proporcionado entre sus metadatos.

        :param int | str campo: nombre del atributo del que se quieren conseguir los valores.
        """

        lista = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for atributo, valor in dicAtri.items():
                if atributo == campo:
                    lista.append((str(solucion), 'SOLUCION ' + str(solucion), "Valor = " + str(valor)))

        return lista
    
    def listaSolucionesQue_NO_TienenDeterminadoAtributo(self, campo: int | str) -> List:
        """Devuelve todas las soluciones que NO tengan el campo proporcionado entre sus metadatos.

        :param int | str campo: nombre del atributo del que NO se quieren conseguir los valores.
        """

        lista = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            if campo not in dicAtri.keys():
                lista.append(solucion)

        return lista    
    
    def atributosDeUnaSolucion(self, unNumeroDeSolucion: int | str) -> Dict:
        """Devuelve todos los metadatos para la solución indicada.

        :param int | str unNumeroDeSolucion: identificador de la solución  a considerar.
        """

        unNumeroDeSolucion = str(unNumeroDeSolucion)

        return self.dicAtrSoluciones.get(unNumeroDeSolucion)
        
    def siUnaSolucionTieneUnAtributo(self, unNumeroDeSolucion: int | str, campo: int | str) -> bool:
        """Devuelve si la solución indicada contiene el campo proporcionado entre sus metadatos.

        :param int | str unNumeroDeSolucion: identificador de la solución a considerar.
        :param int | str campo: nombre del atributo a considerar
        """

        return campo in self.dicAtrSoluciones[str(unNumeroDeSolucion)].keys()
    
    def solucionesQueTienenUnValorEntreSusAtributos(self, valor: int | str) -> List:
        """De entre todas las soluciones, devuelve una lista de los campos que contienen el valor indicado.
            
        :param int | str valor: valor a buscar entre los metadatos de todas sus soluciones.
        """
        
        salida = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for attribute, value in dicAtri.items():
                if valor == value:
                    salida.append((str(solucion), 'SOLUCION ' + str(solucion), "Atributo = " + str(attribute)))

        return salida
    
    def solucionesQueTieneUnAtributoEnUnaListaPosiblesValores(self, campo: str | int, listaDeValores: List[str]) -> List:
        """De entre todas las soluciones, devuelve las soluciones que contengan el campo especificado entre sus metadatos y cuyo valor esté entre la lista de valores.
            
        :param str | int campo: nombre del campo a buscar en los metadatos de las soluciones.
        :param List[str]: listaDeValores: lista de valores posibles que puede tener el campo.
        """

        salida = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for atributo, valor in dicAtri.items():
                if atributo == campo and valor in listaDeValores:
                    salida.append((str(solucion), 'SOLUCION ' + str(solucion), "Valor = " + str(valor)))

        return salida 