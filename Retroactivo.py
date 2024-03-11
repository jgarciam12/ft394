# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 15:11:24 2022

@author: jcgarciam
"""

import xlsxwriter
import pandas as pd
import numpy as np

## Esta función busca calcular el retroactivo del formato 394
## FIN RETROACTIVO


def Retroactivo(df, fecha, path_int):
    dfmesadas = pd.read_excel(path_int + '\Tabla de homologacion.xlsx', header = 0, usecols = ['mes numérico','Mesadas antes de agosto 2012','Mesadas a pagar 1','Mesadas a pagar 2','Mesada'])

    df.loc[(30 - df['Fecha_Calculo'].dt.day) < 0,'dias'] = 0 
    df.loc[(df['dias'].isnull() == True),'dias'] = (30 - df['Fecha_Calculo'].dt.day)

    ## CALCULO DE MESES
    dfmesadas1 = dfmesadas.loc[:,['mes numérico','Mesadas a pagar 1','Mesadas a pagar 2']]
    dfmesadas2 = dfmesadas.loc[dfmesadas['mes numérico'] == fecha.month,'Mesada'].item()
    dfmesadas3 = dfmesadas.loc[dfmesadas['mes numérico'] == fecha.month,'Mesadas antes de agosto 2012'].item()

    df = df.merge(dfmesadas1, left_on = df['Fecha_Calculo'].dt.month, right_on = 'mes numérico', how = 'left', validate = 'many_to_one')
    df['Mesada'] = dfmesadas2
    df['Mesadas antes de agosto 2012'] = dfmesadas3
    df.loc[df['Fecha_Calculo'].dt.year == fecha.year,'meses'] =  (df['Mesada'] - df['Fecha_Calculo'].dt.month)
    df.loc[(df['meses'].isnull() == True) & (df['28-Número de Mesadas'] == 14),'meses'] = df['Mesadas a pagar 1']
    df.loc[(df['meses'].isnull() == True),'meses'] = df['Mesadas a pagar 2']    
    
    ## VALORES DÍAS
    df['valores_dias'] = (df['dias'] * (df['27-Mesada']/30)).astype('float')
    ## VALORES MESES
    df['valores_meses'] = (df['meses'] * df['27-Mesada']).astype('float')
    ## VALORES AÑOS ANTERIORES
    df.loc[(df['Fecha_Calculo'].dt.year != fecha.year) & (df['Fecha_Calculo'].dt.year >= 1994),'años'] = (fecha.year - 1) - df['Fecha_Calculo'].dt.year
    df.loc[(df['Fecha_Calculo'].dt.year != fecha.year) & (df['Fecha_Calculo'].dt.year < 1994),'años'] = fecha.year - 1994

    df['valores_años'] = (df['años'].fillna(0.0).astype(int) * df['28-Número de Mesadas'] * df['27-Mesada']).astype('float')


    ## VALORES AÑO ACTUAL
    df.loc[df['Fecha_Calculo'].dt.year == fecha.year,'multiplo'] = 0
    df.loc[(df['Fecha_Calculo'].dt.year != fecha.year) & (df['28-Número de Mesadas'] == 14),'multiplo'] = df['Mesadas antes de agosto 2012'] 
    df.loc[(df['Fecha_Calculo'].dt.year != fecha.year) & (df['28-Número de Mesadas'] != 14),'multiplo'] = df['Mesada']
    df['valores_final'] = (df['multiplo'].fillna(0.0).astype(int) * df['27-Mesada']).astype('float')


    ## RETROACTIVO
    df['Retroactivo'] = df['valores_dias'] + df['valores_meses'] + df['valores_años'] + df['valores_final']
    
    condictions = [(df['Retroactivo'] < 0),
                   ((df['% comité judicial'].isnull() == True) & (df['Retroactivo'] >= 0)),
                   ((df['% comité judicial'].isnull() == False) & (df['Retroactivo'] >= 0))]
    
    choices = [0, df['Retroactivo'], df['Retroactivo'] * df['% comité judicial']]
    
    df['Retroactivo_def'] = np.select(condictions, choices)
    
    df = df.fillna(0.0).astype({'Retroactivo_def':'float'})

    return df['Retroactivo_def']