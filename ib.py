#-*- coding: utf-8 -*-
"""
Modelo de inferencia exacta para redes bayesiana con eventos binarios.

Este módulo contiene clases para calcular probabilidades exactas en una red
bayesiana con eventos binarios. El módulo posee una clase principal que
representa cada nodo en la red y contiene la lógica para calcular
probabilidades. Esta clase es BinaryEvent. La clase tiene ciertas restricciones
sobre las redes que puede modelar (ver su documentación).
   
En el módulo también se encuentra definida la clase JointProbability que modela
una variable aleatoria que es conjunción de varios BinaryEvents. Esta clase
también tiene ciertas restricciones respecto a qué puede modelar (ver
documentación).
"""
from __future__ import print_function, division, unicode_literals
import itertools
from decimal import Decimal

class BinaryEvent:
    """
    Esta clase modela un evento binario en una red bayesiana.

    Definimos un evento binario como una variable aleatoria con dos posibles 
    resultados: 
        * éxito (positivo, 1)
        * fracaso (negativo, 0)

    La probabilidad de éxito estará condicionada por la influencia de otros
    eventos cuando estos son positivos, sumado a la probabilidad intrínseca de
    que el evento suceda independiente de las otras influencias.

    Llamamos a las influencias: alpha_1, alpha_2, ..., alpha_n
    Llamamos a la probabilidad independiente de las influencias: gamma

    Si X es un evento binario con influencias alpha_1, ..., alpha_n y
    probabilidad independiente gamma, decimos entonces que 

        P(X = 1 | alpha_1 = 0, ..., alpha_n = 0) = gamma

    Por otra parte, para calcular la probabilidad de éxito bajo el éxito de
    alguna de los eventos que lo influyen es necesario utilizar la lógida de
    noisy-or.

    La clase permite calcular la probablidad de éxito o fracaso de un evento
    binario condicionado al éxito o fracaso de eventos de los que depende
    directamente. 

    Se asume que el grafo de dependencias entre eventos binarios no tiene
    ciclos y además no tiene conexiones "horizontales". Esto es, si X <- (A, B)
    (X depende de A y B) entonces no pasa que A <- B o B <- A.
    """
    
    def __init__(self, deps={}, gamma=0, name=None):
        """
        Crea un evento binario.

        Args:
            gamma: probabilidad de éxito si no suceden ninguna de las
                influencias en deps
            deps: diccionario de BinaryEvent -> [0, 1] que describe la
                influencia de cada evento.
        """
        self.gamma = Decimal(gamma)
        self.deps = dict([(k, Decimal(v)) for k, v in deps.items()])
        self.deps_keys = self.deps.keys()
        self.name = name

    def _p_neg_fw_full(self, full_config):
        """
        Calcula la probabilidad de X = 0 dada las dependencias.
        
        Este método implementa la lógica de noisy-or.

        Args:
            full_config: conjunto de dependencias que sabemos que se cumplen.
                Las dependencias que no aparecen en el conjunto se asume que
                no se cumplen.

        Ej:
            Si mi clase es la variable X y es influenciada por las variables A,
            B y C:

            X._p_neg_fw_full({A, C}) == P(X = 0 | A = 1, B = 0, C = 1)
        """
        ret = Decimal('1') - self.gamma
        for ev, influence in self.deps.items():
            if ev in full_config:
                ret *= Decimal('1') - influence

        return ret

    def _p_pos_fw_full(self, full_config):
        """
        Calcula la probabilidad de X = 1 dada las dependencias.

        Args:
            full_config: conjunto de dependencias que sabemos que se cumplen.
                Las dependencias que no aparecen en el conjunto se asume que
                no se cumplen.
        
        Ej:
            Si mi clase es la variable X y es influenciada por las variables A,
            B y C:

            X._p_pos_fw_full({A, C}) == P(X = 1 | A = 1, B = 0, C = 1)
        """
        ret = Decimal('1') - self._p_neg_fw_full(full_config)
        return ret

    def _p_pos_fw(self, full_config, deps_settings):
        """
        Calcula la probabilidad de X = 1 dado un caso de marginalización.

        El método asiste a uno de los pasos de marginalización, por ejemplo en:
            
            P(X = 1 | A = 1) = P(X=1, B=0, C=0 | A = 1) +
                               P(X=1, B=0, C=1 | A = 1) + ... 

        Sirve para calcular:

            P(X=1, B=0, C=1 | A = 1) = P(X=1 | A=1, B=0, C=0) * P(B=0) * P(C=1)

        Donde (B=0, C=1) está descripto por full_config y A=1 esta descripto
        por deps_settings.

        Args:
            full_config : Conjunto de eventos que describe un caso de la
                marginalización. El conjunto contiene las dependencias que
                asumimos sucedieron. La diferencia con self.deps son las que no
                sucedieron. El conjunto no debe contradecir deps_settings
            deps_settings: Diccionario de BinaryEvent -> bool describe que 
                información se conoce ya se asumía independientemente de la 
                marginalización.
        
        Ej:
            Si mi clase es la variable X y es influenciada por las variables A,
            B y C.

            (1) X._p_pos_fw({A, B}, {A: true, C: false}) ==
            (2) P(X=1, B=1 | A=1, C=0) == 
            (3) P(X=1 | A=1, B=1, C=0) * P(B=1)

            Se infiere que se calcula P(X=1, B=1) (B aparece como probabilidad
            conjunta) ya que B no fue descripto por deps_settings, que son las
            condiciones asumidas desde el principio. Luego, es necesario
            multiplicar la probabilidad condicional por la probabilidad del
            evento (como en eq 3).
        
        Ej2:
            (1) X._p_pos_fw({A}, {C: false}) ==
            (2) P(X=1, B=0, A=1 | C=0) == 
            (3) P(X=1 | A=1, B=1, C=0) * P(B=0) * P(A=1)

            Se infiere que se calcula P(X=1, B=0, A=1) ya que ni A ni B fueron
            descriptos por deps_settings, que son las condiciones asumidas
            desde el principio. Luego, es necesario multiplicar la probabilidad
            condicional por la probabilidad del evento (como en eq 3).

            Además, buscamos B=0 ya que B no aparece en la descripción completa
            full_config (a diferencia de A que si aparece).

        Ej3:
            X._p_pos_fw({A}, {A: false}) no es una llamada admitida para la
            función ya que full_config = {A} nos dice que queremos A=1 y
            deps_settings = {A: false} nos dice que sabemos A=0.
        """
        ret = self._p_pos_fw_full(full_config)
        for k in self.deps_keys:
            if k not in deps_settings.keys():
                if k in full_config:
                    ret *= k._prob_pos()
                else:
                    ret *= k._prob_neg()
        return ret

    def _prob_pos(self, deps_settings={}):
        """Decimal version of prob_pos. Ver prob_pos"""
        all_configs = [c
                       for k in range(len(self.deps_keys) + 1)
                       for c in itertools.combinations(self.deps_keys, k)]

        compatible_configs = [c
                              for c in all_configs
                              if self._is_compatible(c, deps_settings)]

        return sum([self._p_pos_fw(c, deps_settings) 
                    for c in compatible_configs])

    def _prob_neg(self, deps_settings={}):
        """Decimal version of prob_neg. Ver prob_neg"""
        return Decimal('1') - self._prob_pos(deps_settings)


    def prob_pos(self, deps_settings={}):
        """
        Calcula la probabilidad de X = 1 dada las dependencias.

        Asumiendo X evento binario con dependencias A, B, C; este método
        permite calcular P(X = 1 | A = 1). Para ello marginaliza sobre X las
        variables restantes: B y C. Tenemos entonces:

            P(X = 1 | A = 1) = P(X=1, B=0, C=0 | A = 1) +
                               P(X=1, B=0, C=1 | A = 1) + ... 

        Luego usamos la definición de probabilidad marginal para pasar las
        dependencias:

            P(X = 1 | A = 1) = P(X=1 | B=0, C=0, A=1) * P(B=0, C=0) +
                               P(X=1 | B=0, C=1, A=1) * P(B=0, C=1) + ... 

        En particular, como B y C son independientes:
            
            P(X = 1 | A = 1) = P(X=1 | B=0, C=0, A=1) * P(B=0) * P(C=0) +
                               P(X=1 | B=0, C=1, A=1) * P(B=0) * P(C=1) + ... 

        Args:
            deps_settings: diccionario BinaryEvent -> bool que codifica que
                condiciones imponemos sobre las dependencias. El diccionario
                puede no describir todas las dependencias de 'self'

        Ej:
            X.prob_pos({A: false, B: true}} == P(X = 1 | A = 0, B = 1)
                P(X = 1, C = 0 | A = 0, B = 1) +
                P(X = 1, C = 1 | A = 0, B = 1) ==
                P(X = 1 | C = 0, A = 0, B = 1) * P(C=0) +
                P(X = 1 | C = 1, A = 0, B = 1) * P(C=1)

            X.prob_pos({A: true}) == P(X = 1 | A = 1)

            Ver desarrollo al principio de la documentación.
        """
        return float(self._prob_pos(deps_settings))

    def prob_neg(self, deps_settings={}):
        "1 - prob_pos"
        return float(self._prob_neg(deps_settings))
        
    def _is_compatible(self, full_config, partial_config):
        """
        Define si la configuracion completa es compatible con la parcial

        Args:
            full_config: conjunto de dependencias que se sabe que se cumplen.
                Las dependencias de 'self' que no estén en este conjunto se
                asume que no se cumplen.
            partial_config: diccionario BinaryEvent -> bool que define, para
                algunas dependencias, cuales se deben cumplir y cuales no.

        Ej:
            Si X depende de A, B y C

            X._is_compatible({A, B}, {}) == true
            X._is_compatible({A, B}, {A: true}) == true
            X._is_compatible({B}, {A: true}) == false
            X._is_compatible({B}, {A: true, B: true}) == false
            X._is_compatible({B}, {B: true}) == true
            X._is_compatible({B}, {B: false}) == false
        """
        ret = all([(ev in full_config) == happens
                   for ev, happens in partial_config.items()
                   if ev in self.deps_keys])
        return ret

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.name is not None:
            return 'Bi({})'.format(self.name)
        else:
            return super().__repr__()

class JointProbability(BinaryEvent):
    """
    Esta clase modela una probabilidad conjunta de varios eventos binarios.

    Los eventos binarios no deberían ser directamente dependientes entre si.

    Un JointProbability también es un evento binario. Las funciones tienen la
    mísma semántica que en la otra clase.
    
    Si Y es la probabilidad conjunta de A y B (Y = JointProbability(A, B)),
    no debe pasar que A dependa directamente de B ni viceversa. Visto de otra
    forma, en el DAG no hay flechas de A a B o viceversa.
    """

    def __init__(self, *args):
        """
        Constructor de la probabilidad conjunta.

        Args:
            *args: Lista de eventos binarios. Los eventos binarios no deben ser
                   directamente dependientes entre si.
        """
        self.events = args
        self.deps_keys = set([k 
                              for x in args
                              for k in x.deps_keys])

    def _p_pos_fw_full(self, full_config):
        ret = Decimal('1')
        for x in self.events:
            ret *= x._p_pos_fw_full(full_config)
        return ret

    def _p_neg_fw_full(self, full_config):
        return Decimal('1') - self._p_pos_fw_full(full_config)
    
    def __repr__(self):
        if self.name is not None:
            return 'Joint({})'.format(', '.join([str(x) for x in self.events]))
        else:
            return super().__repr__()
