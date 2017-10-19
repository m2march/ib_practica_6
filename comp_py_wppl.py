#-*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import io
import pandas as pd
import json

with open('ejercicio.wppl.json', 'r') as f:
    wppl = json.load(f)

with open('ejercicio.py.json', 'r') as f:
    py = json.load(f)

assert set(wppl.keys()) == set(py.keys())

df = pd.DataFrame.from_records([py, wppl], index=['py', 'wppl'])
df = df.T
df['Diff'] = df['wppl'] - df['py'] 

with io.open('comp.txt', 'w', encoding='utf8') as f:
    print(u'Probabilidad de las enfermedades dados los síntomas', file=f)
    df_enfermedades = df.loc[['tb_dado_sintomas', 'cancer_dado_sintomas']]
    print(df_enfermedades.to_string(), file=f)

    print(u'\nProbabilidad de los síntomas dado tb', file=f)
    df_sintomas_tb = df.loc[['sintomas_dado_tb', 'fiebre_dado_tb',
                             'tos_dado_tb', 'difResp_dado_tb']]
    print(df_sintomas_tb.to_string(), file=f)

    print(u'\nProbabilidad de los síntomas dado cancer', file=f)
    df_sintomas_cancer = df.loc[['sintomas_dado_cancer', 'fiebre_dado_cancer', 
                                 'tos_dado_cancer', 'difResp_dado_cancer']]
    print(df_sintomas_cancer.to_string(), file=f)

    print(u'\nProbabilidad prior de síntomas y enfermedad', file=f)
    df_prior = df.loc[['tb_prior', 'cancer_prior', 'sintomas_prior',
                       'fiebre_prior', 'tos_prior', 'difResp_prior']]
    print(df_prior.to_string(), file=f)
