# dirB

A generic tool working over HDF5 files to share experiments data, both input and output, in a standardized way.

JSON dictionaries are the default objects used within the HDF5 files in order to collect input parameters and resulting data.

## Features

The main features available in dirB are:
- Create new cases with input parameters and metadata (`dirB.base.creaNuevoCaso(inputParamsDict, metadataDict)`)
- Load already existing cases from HDF5 files (`dirB.base.cargaCaso(hdf5FileName)`)
- Merge several files containing solutions (`dirB.merge.mergeListaDeSoluciones(baseCase, listOfFilesWithSolutions, outputFile)`)

Features to be implemented:
- Retrieval of solutions fulfilling a certain criteria, in order to process all them together

## Examples

To create a new case from scratch:
```
from dirB.base import zsan_DirB
from datetime import date, datetime
import time
import shutil

diccionarioCasoBase = { 'x': 12,
                        'y': 7}
diccionarioAtributosCasoBase = {
                        'Autor': 'RC01334',
                        'Dia':  str(date.today()),
                        'Escenario': 'Acido',
                        'Numero Caso': 23
                        }

casoBase = zsan_DirB()
casoBase.creaNuevoCaso(diccionarioCasoBase, diccionarioAtributosCasoBase, nombreDeFichero = "casoBase.hdf5")
```

For new partners looking to run this case within their own environments, the first step is to copy the file. Then, run the model with the considered solvers and save them into regular Python dictionaries, which should be added to the new file:
```
shutil.copy("casoBase.hdf5", "casoConSolucion_01.hdf5")
time.sleep(2)

# Assume these are the 2 resulting dictionaries
diccionarioSolucionCaso_1 = {'ex1': 'xxx',
                             'ex2': 'yyy',
                             'ex3': 'zzz'}
diccionarioAtributosSolucionCaso_1 = {
                            'Autor': 'BSC0123',
                            'Dia':  str(datetime.now()),
                            'Escenario': 'Amargo',
                            }

solucion_1 = zsan_DirB()
solucion_1.cargaCaso("casoConSolucion_01.hdf5")
solucion_1.guardaNuevaSolucion(diccionarioSolucionCaso_1, diccionarioAtributosSolucionCaso_1)
```

For every new experiment, the same process should be followed.

Finally, when all the runs have been finished, they should be added up into the same file. As an example, consider we've got a total of 3 runs and that we want to merge them all into our base case file. An additional parameter should be provided to specify the resulting file name, as the base case one will never be overwritten by this method.
```
from dirB.merge import mergeListaDeSoluciones

casoBase = 'casoBase.hdf5'
listaDeCasos = ['casoConSolucion_01.hdf5', 'casoConSolucion_02.hdf5', 'casoConSolucion_03.hdf5']
id_salida = "salida.hdf5"

mergedList = mergeListaDeSoluciones(casoBase, listaDeCasos, id_salida)
```

Complete example notebooks have been added to this repository.

## Documentation

To generate the documentation, you should install sphinx and the proper theme plugin, and then run the make command for the HTML creation:

```
pip install sphinx sphinx_rtd_theme

cd docs
make html
```

With the following command we'll get a clean documentation env to regenerate the whole documentation in case we need to:

```
make clean html
make html
```