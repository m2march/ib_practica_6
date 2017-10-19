#-*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import ib
import json

# Enfermedades

## Condiciones ambientales
Frio = ib.BinaryEvent(gamma=0.2, name='Frio')
Hosp = ib.BinaryEvent(gamma=0.01, name='Hosp')
Fuma = ib.BinaryEvent(gamma=0.3, name='Fuma')

## Enfermedades
Gripe = ib.BinaryEvent({Frio: 0.1, Hosp: 0.2}, gamma=0.2, name='Gripe')
TB = ib.BinaryEvent({Hosp: 0.01}, gamma=0.005, name='TB')
Canc = ib.BinaryEvent({Fuma: 0.05}, gamma=0.01, name='Canc')

## Síntomas
Tos = ib.BinaryEvent({Gripe: 0.5, TB: 0.7, Canc: 0.3}, name='Tos')
Fiebre = ib.BinaryEvent({Gripe: 0.3, TB: 0.2}, name='Fiebre')
DifResp = ib.BinaryEvent({TB: 0.5, Canc: 0.4}, name='Dif. Resp')

Sintomas = ib.JointProbability(Tos, Fiebre, DifResp)

# Ejercicios

## Calcular P(TB | Tos, Fiebre, Dif. Resp)
# 

# P(TB | Tos, Fiebre, Dif. Resp) =  [variable: prob_tb_dado_sintomas]
#       P(Tos, Fiebre, Dif. Resp | TB) * 
#       P(TB) /
#       P(Tos, Fiebre, Dif. Resp)

# P(Tos, Fiebre, Dif. Resp | TB) =  [variable: prob_sintomas_dado_tb]
#       sum_{Canc=c} sum_{Gripe=g}  [Marginalizo en Cancer y Gripe]
#           P(Tos | c, g, TB) * 
#           P(Fiebre | c, g, TB) * 
#           P(Dif. Resp | c, g, TB) * 
#           P(c, g)

# P(Tos, Fiebre, Dif. Resp) =  [variable: prob_sintomas]
#       sum_{Canc=c} sum_{Gripe=g} sum_{TB=tb}  [Marginalizo en todas las
#                                                enfermedades]
#           P(Tos | c, g, tb) * 
#           P(Fiebre | c, g, tb) * 
#           P(Dif. Resp | c, g, tb) *
#           P(c, g, tb) 

prob_sintomas_dado_tb = Sintomas.prob_pos({TB: True})

prob_sintomas = Sintomas.prob_pos()

prob_tb_dado_sintomas = (prob_sintomas_dado_tb * TB.prob_pos() / prob_sintomas)

## Calcular P(Canc | Tos, Fiebre, Dif. Resp)

# P(Canc | Tos, Fiebre, Dif. Resp) =  [variable: prob_canc_dado_sintomas]
#       P(Tos, Fiebre, Dif. Resp | Canc) * 
#       P(Canc) /
#       P(Tos, Fiebre, Dif. Resp)

# P(Tos, Fiebre, Dif. Resp | TB) =  [variable: prob_sinotmas_dado_canc]
#       sum_{Canc=c} sum_{TB=tb}  [Marginalizo en TB y Gripe]
#           P(Tos | Canc, g, tb) * 
#           P(Fiebre | Canc, g, tb) * 
#           P(Dif. Resp | Canc, g, tB) * 
#           P(tb, g)

prob_sintomas_dado_canc = Sintomas.prob_pos({Canc: True})

prob_canc_dado_sintomas = (prob_sintomas_dado_canc * Canc.prob_pos() / 
                           prob_sintomas)

if __name__ == '__main__':
    print(json.dumps(
    {
        'tos_prior': Tos.prob_pos(),
        'fiebre_prior': Fiebre.prob_pos(),
        'difResp_prior': DifResp.prob_pos(),
        'sintomas_prior': prob_sintomas,
        
        'tos_dado_tb': Tos.prob_pos({TB: True}),
        'fiebre_dado_tb': Fiebre.prob_pos({TB: True}),
        'difResp_dado_tb': DifResp.prob_pos({TB: True}),
        'sintomas_dado_tb': prob_sintomas_dado_tb,    

        'tb_dado_sintomas': prob_tb_dado_sintomas,
        
        'tos_dado_cancer': Tos.prob_pos({Canc: True}),
        'fiebre_dado_cancer': Fiebre.prob_pos(),
        'difResp_dado_cancer': DifResp.prob_pos({Canc: True}),
        'sintomas_dado_cancer': prob_sintomas_dado_canc,

        'cancer_dado_sintomas': prob_canc_dado_sintomas,

        'tb_prior': TB.prob_pos(),
        'cancer_prior': Canc.prob_pos()
    }, indent=4))
