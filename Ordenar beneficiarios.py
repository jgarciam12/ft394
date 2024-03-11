# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 16:32:18 2022

@author: jcgarciam
"""

import pandas as pd

path_int = r'D:\DATOS\Users\jcgarciam\OneDrive - AXA Colpatria Seguros\Documentos\Informes\Reservas ARL\Formato 394\Input'

Benerficiarios_Reales = pd.read_excel(path_int + '\Beneficiario reales.xlsx', header = 3)

#%%


lista = ['Parent.','Tipo de identif.','No. de identif.','Sexo','Fecha de Nacimiento','Nombre','Estudios','Estado']



for i in range(1,6):
    for j in len(Benerficiarios_Reales):
        if Benerficiarios_Reales['Parent.'+str(i)][j].isin(['Cónyugue','Conyugue']) == True:
            for k in lista:
                Benerficiarios_Reales[k+'1.1'] = Benerficiarios_Reales['Parent.'+str(i)][j]
                
c = 0

for j in len(Benerficiarios_Reales):
    fechas = []
    for i in range(1,5):        
        if Benerficiarios_Reales['Parent.'+str(i)][j] == 'Hijo':
            fechas[]