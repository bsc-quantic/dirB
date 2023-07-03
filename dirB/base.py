import pandas as pd
import os
import h5py
import uuid
import json
import pathlib
from datetime import date, datetime
from typing import Dict, List, Tuple

from dirB.utils import esperarDesbloqueoDeHDF5


class zsan_DirB:
    """
    Una clase para tratamiento de DIR-B. En el fichero donde esta definida la clase existe documentación y ejemplos sencillos
    Internamente, se guarda como un objeto hdf5 muy sencillo. Estructura:
       / ==> fichero exntension hdf5 con un nombre: ID unico  
       /CASO ==> es un grupo para albergar la info del caso.  
             - JSON_IN: el dataset (nomenclatura hdf5) que contendrá la info JSON ==> a todos efectos: diccionarioPython del escenario.
             - diccionarioAtributos: en aras de generalización y dado que los atributos pueden crecer y depender del problema particular,
                         internamente se manejan como un diccionario que están asociados al grupo "JSON_IN"

    El creador está pensado para ser utilizada en dos contextos:
      a) Creación: en la cual, se persige crear el fichero a partir de info que el programa usuario de la clase esté utilizando
                   En este uso: se invoca a __init__ con "diccionarioDel_JSON y diccionario de atributos" y se crea un objeto DIR-G
                   (se escribe en fichero hdf5 con nombre "ID", conteniendo el JSON (internamente como dataframe) y asignando valores de los
                   atributos)
                       casoEjemplo_01 = zsan_DirB(ID=None, pathDirectorio=None, diccionarioConEl_JSON, diccionarioAtributos)
                    # pathDirectorio si None = directorio en Curso
      b) Carga desde fichero: en la cual con llamar con un ID (el path de un fichero hdf5 ya creado) # tb puede incluirse pathDirectorio
                   ejemplo de llamada para este caso:
                       casoEjemplo_02 = zsanClaseCaso(directorio=None, ID='nombreDelficheroSINEXTENSION_HDF5', diccionarioConEl_JSON_IN=None, diccionarioAtributos=None)

      ¿pq de este comportamiento?
         A) No hay polimorfismo en __init__ de python
         B) Versión punto CERO de este código                   
     
    Parameters
    __________
    
    ID: string
        un string que el un uID del escenario. Uso para trabajar con DIR-B ya creados
    directorio: string
        el path path donde queremos que el fichero que se genere/desde el que se lea (si None=directorio actual)
    diccionarioConEl_JSON_IN: unJSON tal como sería generando en un programa standard Python ¡¡un diccionario!!. Info precisa para
        "resolver el caso" con posterioridad
    diccionarioAtributos: dict
        un diccionario que contiene la info con la que queremos catalogar el caso.
 
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

    def creaNuevoCaso(self, diccionarioConEl_JSON_IN: Dict, diccionarioAtributos: Dict = None, 
                      directorio: str = os.getcwd(), 
                      nombreDeFichero: str = str(datetime.now().strftime("%Y-%m-%dT%H.%M.%S")) + '_' + str(uuid.uuid4()) + '.hdf5'):
        """Crea un nuevo caso teniendo en cuenta el dataset principal y los metadatos

        :param Dict diccionarioConEl_JSON_IN: dataset principal en formato JSON. Contiene los parámetros de entrada del caso.
        :param Dict diccionarioAtributos: diccionario con los metadatos del caso.
        :param str directorio: directorio donde se creará el caso.
        :param str nombreDeFichero: nombre del fichero HDF5 que se utilizará.
        """

        if pathlib.Path(nombreDeFichero).suffix != ".hdf5":
            raise ValueError("El fichero " +  nombreDeFichero + " no tiene extensión HDF5.")
        
        fullPath = os.path.join(directorio, nombreDeFichero)
        with h5py.File(fullPath, 'w') as f:
            caso = f.create_group('CASO')
            
            dataType = h5py.string_dtype(encoding='utf-8')
            info = json.dumps(diccionarioConEl_JSON_IN, ensure_ascii=False)
            caso.create_dataset('JSON_IN', data=info, dtype=dataType)

            if diccionarioAtributos:
                for key, value in diccionarioAtributos.items():
                    caso.attrs[key] = value
                    
        esperarDesbloqueoDeHDF5(fullPath,segundosDeSleep=0.1)

        self._actualizaMiembros(nombreDeFichero, fullPath, directorio)
    
    def cargaCaso(self, nombreDeFichero: str, directorio: str = os.getcwd()):
        """Carga un caso identificado con idCaso
        
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
        """Lee estructura de un fichero DIR-B y consigue los diccionarios de atributos del CASO y de las SOLUCIONES.

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
              dicAtrSoluciones[numSolucion] = {key: value for key, value in f[cadenaPathSolEnCurso].attrs.items() }
              
        esperarDesbloqueoDeHDF5(nombreDelFichero)
        
        return dicAtrCaso, dicAtrSoluciones
    
    def _getDataFrameResumenAtributosCaso(self, diccionarioAttrs: Dict) -> pd.Series:
        """Devuelve un dataframe (objecto pandas.Series) con atributos del Caso.

        : param Dict diccionarioAttrs: diccionario a partir del cual se genera el dataframe de salida
        """

        if len(diccionarioAttrs) != 0:
          return pd.Series(diccionarioAttrs)
        else:
          return pd.Series(dtype=int)  # Esencialmente una serie vacia

    def _getDataFrameResumenAtributosSoluciones(self, dicAtrSoluciones: Dict):
        """Devuelve un dataframe resumen de todos los atributos de todas las soluciones (ver comentarios) a partir de diccionario atributos soluciones
        """
        # Podrian no existir el diccinario de Atributos de soluciones, por no existir aún soluciones en le fichero o
        # pq ninguna de las solcuiones incluidas, incluyan metadatos
        if not(dicAtrSoluciones):
            return pd.DataFrame()  # Un dataFrame vacio
            
        aux = [(caso, dicAtributosAux) for caso, dicAtributosAux in dicAtrSoluciones.items()]
        listaDeClaves = ['SOLUCION  '+str(e[0]) for e in aux]
        listaDeDiccionarios = [e[1] for e in aux]                
        return pd.DataFrame.from_records(listaDeDiccionarios, index=listaDeClaves)
    
    def guardaNuevaSolucion(self, diccionarioConEl_JSON_OUT: Dict, diccionarioAtributos: Dict = None):
        """Guarda una nueva solución en el DIR-B.

        :param Dict diccionarioConEl_JSON_OUT: dataset principal en formato JSON. Contiene los parámetros de entrada del caso.
        :param Dict diccionarioAtributos: diccionario con los metadatos del caso.
        """

        with h5py.File(self.fullPath, 'a') as f:
            if self.numeroSoluciones == 0:
                f.create_group('/SOLUCIONES')                    
            cadena = '/SOLUCIONES/' + str(self.numeroSoluciones + 1)
            f.create_group(cadena)        
            dataType = h5py.string_dtype(encoding='utf-8')
            info = json.dumps(diccionarioConEl_JSON_OUT, ensure_ascii=False)
            f[cadena].create_dataset('JSON_OUT', data=info, dtype=dataType)                       
            # Los atributos se guardan "valor a valor", en caso de haber sido pasados
            if diccionarioAtributos:
                for key, value in diccionarioAtributos.items():
                   f[cadena].attrs[key] = value
               
        esperarDesbloqueoDeHDF5(self.fullPath)
        
        self._actualizaMiembrosDerivados()

    def guardaNuevasSoluciones(self, listaDeSoluciones: List[Dict], listaDeAtributosDeSoluciones: List[Dict]):
        """ Guarda las nuevas soluciones pasadas por parámetro en el actual dirB.

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
        """ Recupera el caso como diccionario === NO COMO JSON. Dicicionario objeto natural PYTHON
        """

        with h5py.File(self.fullPath, 'r') as f:
            aux1 = f['/CASO/JSON_IN'][()]
            aux2 = aux1.decode("utf-8")
            salida = json.loads(aux2)
           
        esperarDesbloqueoDeHDF5(self.fullPath)  # Criterio de finalización de proceso: se puede bloquear fichero
        return salida      
      
    def recuperaSolucionComoDiccionario(self, numeroDeSolucion: int):
        """ Recupera un numero de solucion como diccionario Python (built-in Dict)

        :param int numeroDeSolucion: identificador de la solución a recuperar
        """
        
        numeroDeSolucion = str(numeroDeSolucion)
        if not numeroDeSolucion in self.listaSoluciones:
            raise ValueError('No existe número de caso ', numeroDeSolucion)
        
        with h5py.File(self.fullPath, 'r') as f:
            cadena = '/SOLUCIONES/' + numeroDeSolucion + '/JSON_OUT'
            aux1 = f[cadena][()]
            aux2 = aux1.decode("utf-8")
            salida = json.loads(aux2)
         
        esperarDesbloqueoDeHDF5(self.fullPath)  # Criterio de finalización de proceso: se puede bloquear fichero 
        return salida
    
    def representaAtributosDeTodasLasSoluciones(self):
        """ Muestra atributos de todos las SOLUCIONES forma bonita. Recordar que print(a) muestra todo detalle
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

    def representaAtributosDelCaso(self):
        """ Muestra atributos del caso en forma bonita.  Recordar que print(a) muestra todo detalle
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
        print(cadena)
                
    def listaSolucionesQueTienenDeterminadoAtributo(self, literalDeUnAtributo: int | str):
        """ Admite el literal de un atributo y muestra las soluciones que tienen dicho atributo

        :param int | str literalDeUnAtributo: nombre del atributo del que se quieren conseguir los valores
        """

        lista = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for atributo, valor in dicAtri.items():
                if atributo == literalDeUnAtributo:
                    lista.append((solucion, 'SOLUCION '+str(solucion), valor))
        return lista
    
    
    def listaSolucionesQue_NO_TienenDeterminadoAtributo(self, literalDeUnAtributo: int | str):
        """ Admite el literal de un atributo y muestra las soluciones que NO tienen dicho atributo

        :param int | str literalDeUnAtributo: nombre del atributo del que NO se quieren conseguir los valores

        TODO fusionar esta función con la anterior con un booleano
        """

        lista = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            if literalDeUnAtributo not in dicAtri.keys():
                lista.append(solucion)
        return lista    
    
    def atributosDeUnaSolucion(self, unNumeroDeSolucion: int | str):
        """ Autoexplicado. Devuelve diccionario si el numero de solución existe

        :param int | str unNumeroDeSolucion: identificador de la solución  a considerar
        """

        unNumeroDeSolucion = str(unNumeroDeSolucion)
        salida = self.dicAtrSoluciones.get(unNumeroDeSolucion)
        return salida
        
    def siUnaSolucionTieneUnAtributo(self, unNumeroDeSolucion: int | str, literalDeUnAtributo: int | str):
        """ Autoexplicado

        :param int | str unNumeroDeSolucion: identificador de la solución a considerar
        :param int | str literalDeUnAtributo: nombre del atributo a considerar
        """
        unNumeroDeSolucion = str(unNumeroDeSolucion)  # Por si acaso...
        print(self.dicAtrSoluciones[unNumeroDeSolucion].keys())
        loTiene = literalDeUnAtributo in self.dicAtrSoluciones[unNumeroDeSolucion].keys()
        return loTiene
      
    
    def solucionesQueTienenUnValorEntreSusAtributos(self, unLiteral):
        """ Mejor con ejemeplo: unID.solucionesQueTienenUnValorEntreSusAtributos('RC01334') devuelve lista de tuplas (solucion, nombreAtributoQueTieneEseLiteral)

            :param int | str unLiteral: ----
        """
        salida = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for atributo, valor in dicAtri.items():
                if valor == unLiteral:
                    salida.append((solucion, 'SOLUCION '+str(solucion),  atributo))
        return salida
    
    
    def solucionesQueTieneUnAtributoEnUnaListaPosiblesValores(self, unLiteralAtributo, listaValores):
        """ Lo que le nombre dice devuelve lista de tuplas (solucion,  valordelAtributo)
            :param unLiteralAtributo: ----
            :param listaValores: ----
        """

        salida = []
        for solucion, dicAtri in self.dicAtrSoluciones.items():
            for atributo, valor in dicAtri.items():
                if atributo == unLiteralAtributo and  valor in listaValores:
                    salida.append((solucion, 'SOLUCION '+str(solucion),  valor))
        return salida 
