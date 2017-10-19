# Inferencia bayesiana - Práctica Entregable: Inferencia exacta

**Martin A. Miguel (LU: 181/09)**

En actual directorio contiene la implementación de los cálculos de inferencia
exacta para el entregable de la clase 6.

El código fue implementado para _Python 3_ pero es compatible con _Python 2.7_.

## Contenido del entregable

Por una parte se utilizó python para calcular las probabilidades exactas
requeridas en el ejercicio. Esto se realizó mediante los siguientes archivos:

* `ib.py`: Módulo donde se encuentran las clases `BinaryEvent` y
  `JointProbabilty` que sirven para describir los DAGs y realizar ciertas
  cuentas sobre ellos. En particular, `BinaryEvent` describe un nodo del DAG y
  permite calcular su probabilidad de éxito con o sin restricciones sobre
  variables que lo influencian directamente. `JointProbability` crea una nueva
  variable aleatoria que consiste de la conjunción de sus variables parámetros.
  Asume que sus variables son condicionalmente independientes entre si.

* `ib_test.py`: Tests sobre la implementación de `ib.py` utilizando el ejemplo
  de la clase 4 de la alarma, el ladrón y el terremoto. Se ejecuta utilizando
  [pytest](https://docs.pytest.org/en/latest/)

* `ejercicio.py`: en este script se calculan las probabilidades necesarias para
  responder las preguntas del enunciado. El script utiliza lo desarrollado en
  `ib.py`. El archivo escribe en formato json las probabilidades finales del
  enunciado así como las probabilidades intermedias que fue necesario calcular.

* `ejercicio.wppl`: este script describe el modelo en el lenguaje webppl. Al
  igual que `ejercicio.py`, al correrlo imprime en formato json las
  probabilidades finales del enunciado así como las intermedias.

* `comp_py_wppl.py`: este script espera dos archivos (`ejercicio.wppl.json` y
  `ejercicio.py.json`) con los json resultado de los dos scripts anteriores
  anteriores e imprime una tabla que muestra los resultados para cada modelo y
  la diferencia entre los resultados.

* `Makefile`: este archivo contiene las recetas para producir los archivos
  resultados `ejercicio.wppl.json`, `ejercicio.py.json` y `comp.txt`. El último
  es la tabla resultado de `comp_py_wppl.py`. Las recetas se ejecutan
  utilizando el comando `$> make`.

## ¿Cómo leer el entregable?

Se puede empezar leyendo `ib.py` para entender la implementación genérica del
cálculo de probabilidades exactas. `ib.py` fue documentado extensamente, por lo
que puede ser algo largo de leer pero debería ser sencillo. 

Luego se puede leer `ib_test.py` para entender cómo se utiliza el módulo. Ahí
se encuentra el modelo de la clase 4 de terremotos y alarmas.

Finalmente, en `comp.txt` están los resultados de calcular las probabilidades
para el modelo con python y con wppl. Para ver el detalle de cómo calculamos
las probabilidads en python (la implementación del modelo), referirse a
`ejercicio.py`. En este último archivo está detallado cómo se aplicó la regla
de bayes y las marginalizaciones en el cálculo de las probabilidades.
