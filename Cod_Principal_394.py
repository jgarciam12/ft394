# -*- coding: utf-8 -*-

"""
Created on Thu Oct 13 10:28:00 2022

@author: jcgarciam
"""

'''
El siguiente codigo busca caclcular el formato 394 en el cual se calcula el retroactivo de las pensiones
de los sobrevivientes y discapacitada y estimar sus posibles beneficiarios. Esto se hace para la base
reserva avisados la cual trae la informacion de las personas a las que se les debe calcular la pension.
Ademas, existe un historico el cual se le debe actualizar el retroaactivo y al que se le debe concatenar
los nuevos registros
'''


import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import Retroactivo

Tiempo_Total = datetime.now()

path_int = r'D:\DATOS\Users\jcgarciam\OneDrive - AXA Colpatria Seguros\Documentos\Informes\Reservas ARL\Formato 394\Input'
path_out = r'D:\DATOS\Users\jcgarciam\OneDrive - AXA Colpatria Seguros\Documentos\Informes\Reservas ARL\Formato 394\Output'


#%%

lista = os.listdir(path_int)

fecha =  input('Ingrese la fecha de corte dd/mm/aaaa: ')
fecha2 = fecha
fecha = datetime.strptime(fecha, '%d/%m/%Y')
print('\n La fecha de corte para este cierre es: ', fecha)


previous_month = fecha - timedelta(days=fecha.day)
'''
Dentro de la base historica del formato 394 existe una columna que trae el valor de la mesada de la pension.
Este valor se debe actualizar cada enero ya que el ipc y el salarion minimo cambian. Cuando llega comienzo
de año se dede multplicar el valor de la mesada por (uno mas el ipc el cual viene dado en decimales y 
representa un porcentaje). Este valor va a ser la nueva mesada, pero si el valor calculado es menor que 
el salario minimo del nuevo año este valor de la mesada se debe ajustar al minimo
'''

### ACTUALIZACION DEL IPC Y EL SMMLV ###

Digitados = pd.read_excel(path_int + '\Digitados.xlsx', header = 0)
respuesta = 'Si'
while (respuesta.title() == 'Si') & (fecha.month == 1):
    print('\n Estamos en el mes de Enero y debe actualizarse el IPC y el SMMLV')
    print('El SMMLV actual es: $', '{:,.0f}'.format(Digitados['SMMLV'][0]))
    print('Y el IPC actual es: ', Digitados['IPC DEL AÑO'][0])
    respuesta2 = input('Desea modificarlo? (Si/No): ')
    
    if respuesta2.upper() == 'SI':
        smmlv = int(input('\nIngrese el nuevo SMMLV: (Ejemplo: 1000000): '))
        ipc = float(input('Ingrese el nuevo IPC en valor decimal: (Ejemplo: 0.0562): '))
        Digitados['SMMLV'][0] = smmlv
        Digitados['IPC DEL AÑO'][0] = ipc
        print('\n El nuevo SMMLV es: $', '{:,.0f}'.format(Digitados['SMMLV'][0]))
        print('El nuevo IPC es: ', Digitados['IPC DEL AÑO'][0])
        respuesta3 = input('Es correcto? (Si/No): ')
        if respuesta3.upper() == 'SI':
            print('Guardando actualizaciones')                     
            Digitados.to_excel(path_int + '\Digitados.xlsx', index = False)
            print('Actualizaciones guardadas')
            respuesta = 'No'   
        else:
            respuesta = 'Si'
    else:
        respuesta = 'No' 
#%%

### ACTUALIZACION DE LA MESADA

def ConvertirMes(mes):
    m = {
        '01': "Enero",
        '02': "Febrero",
        '03': "Marzo",
        '04': "Abril",
        '05': "Mayo",
        '06': "Junio",
        '07': "Julio",
        '08': "Agosto",
        '09': "Septiembre",
        '10': "Octubre",
        '11': "Noviembre",
        '12': "Diciembre"
        }
    return str(m[mes])

### La reserva historica es el formato 394
print('\n Cargando el Formato 394 de',ConvertirMes(previous_month.strftime('%m')), str(previous_month.strftime('%Y')))
Reserva_Historica = pd.read_excel(path_out + '\Formato 394 de ' + ConvertirMes(previous_month.strftime('%m')) + ' ' + str(previous_month.strftime('%Y')) + '.xlsx', header = 0)
print('\n Formato 394 de',ConvertirMes(previous_month.strftime('%m')), str(previous_month.strftime('%Y')), 'cargado')


Reserva_Historica['27-Mesada'] = Reserva_Historica['27-Mesada'].astype(float)

#funcion para actualizar la mesada
def NuevaMesada(df):
    ipc = float(Digitados['IPC DEL AÑO'][0])
    smmlv = float(Digitados['SMMLV'][0])
    a = df['27-Mesada']
    b = a * (ipc + 1) 
    
    if b < smmlv:
        c = smmlv
    else:
        c = b
    return c
    
### Si el mes actual es enero se actualiza la mesada en funcion del nuevo SMMLV e IPC
if fecha.month == 1:
    print('\n Estamos en el mes de Enero \n')
    pregunta = input('Desea actualizar la mesada para este año en base al IPC y al nuevo SMMLV? (Si/No): ')
    if pregunta.upper() == 'SI':
        print('\n Actualizando la Mesada para este nuevo año \n')
        Reserva_Historica['27-Mesada'] = Reserva_Historica.apply(NuevaMesada, axis = 1)
        print('Mesada Actualizada para este año')
    else:
        print('\n Se deja la misma Mesada que se tenía')
    
#%%

print('\n Cargando fuentes auxiliares')
xls = pd.ExcelFile(path_int + '\Insumos.xlsx')
sheets = xls.sheet_names
Data = {}
for sheet in sheets:
    print(sheet)
    Data[sheet] = xls.parse(sheet)
            
xls.close()

print('\n Fuentes cargadas')
#%%    

## La base de Calculo beneficiarios estimados es creada precisamente para estimar los beneficiarios
## y edades del pensionado mientras se consigue la informacion real
Calculo_Ben_Estimados = Data['Calculo Ben. Estimados']
#Reserva = Data['Reserva']
#Comite_Judicial = Data['Comite Judicial']
Se_amortiza = Data['Se amortiza']

## Esta base se usa para actualizar los datos de los beneficiarios estimados a los reales para los siniestros
## Esta base se debe actualizar mensualente

print('\n Cargando la base Beneficiarios reales')
Benerficiarios_Reales = pd.read_excel(path_int + '\Beneficiario reales.xlsx', header = 3)
print('\n Beneficiarios reales cargados')



columnas = ['Afiliación','No. Siniestro','Fecha de Accidente','Tipo','IBL AT','Mesada Pensional','No Mesadas',
            'Grado de invalidez inicial','FECHA DE DICTAMEN','Fecha de aviso','Porcentaje comité judicial','Tipo de Identificación',
            'Sexo','Nombre  Afiliado ','Edad / Fecha Nacimiento','Fecha de muerte','FECHA DE LA ULTIMA IT',
            'Identificacion Trabajador ','% PCL']
### la base de reserva avisados es nuestra fuente principal para este proyecto, ya que son los nuevos registros
### a los que se les va a calcular el retroactivo y estimar los beneficiarios



print('\n Cargando base de Reserva avisados')
Reserva_Avisados = pd.read_excel(path_int + '\Reserva avisados ' + ConvertirMes(fecha.strftime('%m')).lower() + ' ' + str(fecha.strftime('%Y')) + '.xlsx', header = 0, usecols = columnas, sheet_name = 'Nuevos')
print('Reserva avisados cargada')

### La siguiente base tiene los siniestros que se van a liberar, es decir a los que ya no van a ser parte
### del formato 394. Esta base la van actualizar mensualemnete

print('\n Cargando base de Objetados')
Objetados = pd.read_excel(path_int + '\Reserva avisados ' + ConvertirMes(fecha.strftime('%m')) + ' ' + str(fecha.strftime('%Y')) + '.xlsx', header = 0, usecols = ['No. Siniestro'], sheet_name = 'Objetados')
print('\n Base de Objetados cargada')

print('\n Cargando base de liberaciones')
Liberaciones = pd.read_excel(path_int + '\Reserva avisados ' + ConvertirMes(fecha.strftime('%m')) + ' ' + str(fecha.strftime('%Y')) + '.xlsx', header = 0, usecols = ['Siniestro'], sheet_name = 'Otros liberados')
print('\n base de liberaciones cargada')

print('\n Cargando base de liberaciones Matematica')
Matematica = pd.read_excel(path_int + '\Reserva avisados ' + ConvertirMes(fecha.strftime('%m')) + ' ' + str(fecha.strftime('%Y')) + '.xlsx', header = 0, usecols = ['Siniestro'], sheet_name = 'Matemática')
print('\n base de liberaciones Matematica cargada')

print('\n Cargando base de historico de liberaciones')
Liberaciones_hist = pd.read_excel(path_out + '\Historico de Liberaciones.xlsx', header = 0)
print('\n Historico de liberaciones cargada')



#%%


Calculo_Ben_Estimados['46-Fecha de Nacimiento'] = int(fecha2[-4::])-Calculo_Ben_Estimados['Edad Beneficiario 1']
Calculo_Ben_Estimados['54-Fecha de Nacimiento'] = int(fecha2[-4::])-Calculo_Ben_Estimados['Edad Beneficiario 2']

Calculo_Ben_Estimados['46-Fecha de Nacimiento'] = str(fecha.strftime('%d')) + '/' + str(fecha.strftime('%m')) + '/' + Calculo_Ben_Estimados['46-Fecha de Nacimiento'].astype(str)
Calculo_Ben_Estimados['54-Fecha de Nacimiento'] = str(fecha.strftime('%d')) + '/' + str(fecha.strftime('%m')) + '/' + Calculo_Ben_Estimados['54-Fecha de Nacimiento'].astype(str)


Calculo_Ben_Estimados['46-Fecha de Nacimiento'] = np.where(Calculo_Ben_Estimados['46-Fecha de Nacimiento'].str[0:5] == '29/04', '28/04' + '/' + Calculo_Ben_Estimados['46-Fecha de Nacimiento'].str[-4::],Calculo_Ben_Estimados['46-Fecha de Nacimiento'])
Calculo_Ben_Estimados['54-Fecha de Nacimiento'] = np.where(Calculo_Ben_Estimados['54-Fecha de Nacimiento'].str[0:5] == '29/04', '28/04' + '/' + Calculo_Ben_Estimados['54-Fecha de Nacimiento'].str[-4::],Calculo_Ben_Estimados['54-Fecha de Nacimiento'])

Calculo_Ben_Estimados['46-Fecha de Nacimiento'] = pd.to_datetime(Calculo_Ben_Estimados['46-Fecha de Nacimiento'], format = '%d/%m/%Y') 
Calculo_Ben_Estimados['54-Fecha de Nacimiento'] = pd.to_datetime(Calculo_Ben_Estimados['54-Fecha de Nacimiento'], format = '%d/%m/%Y') 

Calculo_Ben_Estimados.loc[Calculo_Ben_Estimados['Importancia 2 - Parentesco'].astype(str) == '0', '54-Fecha de Nacimiento'] = np.nan 


#%%

condictions = [((Calculo_Ben_Estimados['Género Afiliado'].str.title() == 'Hombre') | (Calculo_Ben_Estimados['Género Afiliado'] == 1)),
               ((Calculo_Ben_Estimados['Género Afiliado'].str.title() == 'Mujer') | (Calculo_Ben_Estimados['Género Afiliado'] == 2))]

choices = [1,2]

Calculo_Ben_Estimados['Género Afiliado'] = np.select(condictions, choices)




#%%

lista = ['09-Vigencia inicial','11-Fecha de siniestro','20-Fecha de Nacimiento','31-Fecha última modificación',
         '46-Fecha de Nacimiento','54-Fecha de Nacimiento','62-Fecha de Nacimiento','71-Fecha Inicial Renta Diferida',
         '83-Fecha del Aviso del Siniestro','Fecha siniestro','Fecha_Calculo']

for i in lista:
    print(i)
    Reserva_Historica[i] = pd.to_datetime(Reserva_Historica[i], format = '%d/%m/%Y')
    
#%%

## Se renombran los campos de la Reserva Avisado en base a los que deben quedar en el formato 394
columnas = {'No. Siniestro':'10-No. de siniestro','Fecha de Accidente':'11-Fecha de siniestro',
            'Tipo':'12-Origen de la pensión','IBL AT':'26-Ingreso base de liquidación',
            'Mesada Pensional':'27-Mesada','No Mesadas':'28-Número de Mesadas',
            'Grado de invalidez inicial':'30-Grado de invalidez inicial','FECHA DE DICTAMEN':'31-Fecha última modificación',
            'Fecha de aviso':'83-Fecha del Aviso del Siniestro','Porcentaje comité judicial':'% comité judicial',
            'Tipo de Identificación':'17-Tipo de identif.','Sexo':'19-Sexo','Fecha nacimiento':'20-Fecha de Nacimiento',
            'Nombre  Afiliado ':'21-Nombre','Afiliación':'08-No. de poliza','Identificacion Trabajador ':'18-No. de identif.',
            'Edad / Fecha Nacimiento':'20-Fecha de Nacimiento','% PCL':'32-Grado de invalidez actual'}

Reserva_Avisados = Reserva_Avisados.rename(columns = columnas)

## esta funcion se crea ya que algunas veces hay campos que python los sobreentiende en formato float
## y deben quedar en formato string y sin el .0 que aparece al final de los tipo float
def CambioFormato(df, a = 'a'):
    df[a] = df[a].astype(str)
    df[a] = np.where(df[a].str[-2::] == '.0', df[a].str[0:-2], df[a])
    return df[a]

Reserva_Avisados['10-No. de siniestro'] = CambioFormato(Reserva_Avisados, a = '10-No. de siniestro')
Reserva_Historica['10-No. de siniestro'] = CambioFormato(Reserva_Historica, a = '10-No. de siniestro')

Reserva_Avisados.loc[Reserva_Avisados['17-Tipo de identif.'].astype(str).str.upper() == 'CC','17-Tipo de identif.'] = 1


Reserva_Avisados = Reserva_Avisados[Reserva_Avisados['10-No. de siniestro'].isin(Reserva_Historica['10-No. de siniestro']) == False]

#Campos vacíos que se crean para formato 394 pero no se diligencian
Reserva_Avisados[['14-Tiempo de  Diferimiento','15-Tiempo de  Temporalidad','22-Estudios','24-No. Hijos',
                 '25-No. hijos invalidos','33-Invalidez-Vejez-Jubilación','34-Sobrevivencia','35-Auxilio funerario',
                 '36-Otra','37-Gastos','38-Total','39-Fondo de ahorro','40-Fondo rendim. ahorro',
                 '41-Cálculo partic. utilidad','43-Tipo de identif.','44-No. de identif.','47-Nombre',
                 '48-Estudios','51-Tipo de identif.','52-No. de identif.','55-Nombre','56-Estudios','58-Parent. 04',
                 '59-Tipo de identif.','60-No. de identif.','61-Sexo','62-Fecha de Nacimiento','63-Nombre',
                 '64-Estudios','65-Estado','66-Número de Radicación de la Nota Técnica','67-Interés Técnico Prima',
                 '68-Tasa de Crecimiento Prima','69-Gastos Prima','70-Prima Única','71-Fecha Inicial Renta Diferida',
                 '72-Valor Mesada o Beneficio Periódico Diferido','73-Valor Auxilio Funerario','74-Reserva Gastos',
                 '75-Utilidad Reconocida','76-Observaciones','77-VRRV89(0)','78-VRRV08(0)','79-PAR(0)',
                 '80-%  Amort. Mensual Adicional (PARMA)','81-% Amort. en Exceso del PARMA','82-% Amort. Acumulado',
                 '84-Total Reserva Estados Financieros']] = np.nan


condiction = [(Reserva_Avisados['12-Origen de la pensión'].str.upper() == 'I'),
              (Reserva_Avisados['12-Origen de la pensión'].str.upper() == 'S')]

choices = [1,2]

Reserva_Avisados['12-Origen de la pensión'] = np.select(condiction,choices)


Reserva_Avisados['19-Sexo'] = Reserva_Avisados['19-Sexo'].astype(str)
Reserva_Avisados['19-Sexo'] = Reserva_Avisados['19-Sexo'].str.upper()

condiction = [((Reserva_Avisados['19-Sexo'].str.upper() == 'M') | (Reserva_Avisados['19-Sexo'] == '1')),
              ((Reserva_Avisados['19-Sexo'].str.upper() == 'F') | (Reserva_Avisados['19-Sexo'] == '2'))]

choices = [1,2]

Reserva_Avisados['19-Sexo'] = np.select(condiction,choices)



condiction = [(Reserva_Avisados['12-Origen de la pensión'] == 1),
              (Reserva_Avisados['12-Origen de la pensión'] == 2)]

choices = [2,3]

Reserva_Avisados['23-Estado'] = np.select(condiction,choices)


Reserva_Avisados['20-Fecha de Nacimiento'] = pd.to_datetime(Reserva_Avisados['20-Fecha de Nacimiento'], format = '%Y-%m-%d')

### Se calcula la edad de los pensionados
Reserva_Avisados['Edad'] = fecha.year - Reserva_Avisados['20-Fecha de Nacimiento'].dt.year



condictions = [ (fecha.month < Reserva_Avisados['20-Fecha de Nacimiento'].dt.month),
               (fecha.month == Reserva_Avisados['20-Fecha de Nacimiento'].dt.month) & (pd.to_datetime(fecha, format = '%d/%m/%Y').day < Reserva_Avisados['20-Fecha de Nacimiento'].dt.day)]

choices = [(Reserva_Avisados['Edad'] - 1), (Reserva_Avisados['Edad'] - 1)]

Reserva_Avisados['Edad'] = np.select(condictions, choices)




Reserva_Avisados['Edad'] = np.where(Reserva_Avisados['Edad'] == 0, pd.to_datetime(fecha, format = '%d/%m/%Y').year - Reserva_Avisados['20-Fecha de Nacimiento'].dt.year, Reserva_Avisados['Edad'])


### Con la edad del pensionado se le asigna un grupo para asi mismo estimarle los beneficiarios
condictions = [((Reserva_Avisados['Edad'] >= 0) & (Reserva_Avisados['Edad'] < 25) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 25) & (Reserva_Avisados['Edad'] < 30) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 30) & (Reserva_Avisados['Edad'] < 35) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 35) & (Reserva_Avisados['Edad'] < 40) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 40) & (Reserva_Avisados['Edad'] < 45) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 45) & (Reserva_Avisados['Edad'] < 50) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 50) & (Reserva_Avisados['Edad'] < 55) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 55) & (Reserva_Avisados['Edad'] < 60) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 60) & (Reserva_Avisados['19-Sexo'] == 1)),
               ((Reserva_Avisados['Edad'] >= 0) & (Reserva_Avisados['Edad'] < 23) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 23) & (Reserva_Avisados['Edad'] < 28) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 28) & (Reserva_Avisados['Edad'] < 33) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 33) & (Reserva_Avisados['Edad'] < 36) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 36) & (Reserva_Avisados['Edad'] < 43) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 43) & (Reserva_Avisados['Edad'] < 48) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 48) & (Reserva_Avisados['Edad'] < 53) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 53) & (Reserva_Avisados['Edad'] < 58) & (Reserva_Avisados['19-Sexo'] == 2)),
               ((Reserva_Avisados['Edad'] >= 58) & (Reserva_Avisados['19-Sexo'] == 2))]


choices = [0, 25, 30, 35, 40, 45, 50, 55, 60, 0, 23, 28, 33, 36, 43, 48, 53, 58]

Reserva_Avisados['Categoría Edad Afiliado'] = np.select(condictions, choices)



Reserva_Avisados2 = Reserva_Avisados.merge(Calculo_Ben_Estimados, how = 'left',  left_on = ['Categoría Edad Afiliado','19-Sexo'], right_on = ['Categoría Edad Afiliado','Género Afiliado'])




#%%



#### si el tipo de pension es S la fecha calculo es igual a la fecha de muerte, pero si el tipo es I entonces
#### se compara la fecha de ocurrencia o accidente con la FECHA DE LA ULTIMA IT de la ultima incapacidad y se toma la maxima
def maxima_fecha(df):
    a = df['11-Fecha de siniestro']
    b = df['FECHA DE LA ULTIMA IT']
    c = df['Fecha de muerte']
    if df['12-Origen de la pensión'] == 2:
        d = c
    else:
        d = max(a,b)
    return d
    

Reserva_Avisados2['Fecha_Calculo'] = Reserva_Avisados2.apply(maxima_fecha, axis = 1)

#%%
Reserva_Avisados2['01-Ramo'] = Digitados['01-Ramo'][0]
Reserva_Avisados2['02-Unidad'] = Digitados['02-Unidad'][0]
Reserva_Avisados2['03-Equivalencia'] = Digitados['03-Equivalencia'][0]
Reserva_Avisados2['04-Tasa de crecim.'] = Digitados['04-Tasa de crecim.'][0]
Reserva_Avisados2['05-Tipo de crecim.'] = Digitados['05-Tipo de crecim.'][0]
Reserva_Avisados2['06-Interés Técnico'] = Digitados['06-Interés Técnico'][0]
Reserva_Avisados2['07-Rentabil. Esperada'] = Digitados['07-Rentabil. Esperada'][0]
Reserva_Avisados2['13-Clase de pensión'] =  Digitados['13-Clase de pensión'][0]
Reserva_Avisados2['16-Parent. 01'] = Digitados['16-Parent. 01'][0]
Reserva_Avisados2['09-Vigencia inicial'] = (fecha - timedelta(fecha.day) + timedelta(days = 1)).date()
Reserva_Avisados2['Fecha siniestro'] = Reserva_Avisados2['11-Fecha de siniestro']
Reserva_Avisados2['85-Tipo beneficiarios'] = Digitados['85-Tipo beneficiarios'][0]
Reserva_Avisados2['86-Constituida a sep/10'] = Digitados['86-Constituida a sep/10'][0]

#%%
Reserva_Avisados2['87-Se amortiza'] = np.where(Reserva_Avisados2['10-No. de siniestro'].isin(Se_amortiza['SNTRO'].astype(str)) == True, 'Si', 'No')
 
condictions = [(Reserva_Avisados2['Importancia 1 - Parentesco'] == 'Madre'),
               (Reserva_Avisados2['Importancia 1 - Parentesco'] == 'Padre'),
               (Reserva_Avisados2['Importancia 1 - Parentesco'] == 'Cónyuge'),
               ((Reserva_Avisados2['Importancia 1 - Parentesco'].str.title() == 'Hijo') & (Reserva_Avisados2['Importancia 1 - Estado'].str.title().isin(['Válido','Valido']) == True)),
               ((Reserva_Avisados2['Importancia 1 - Parentesco'].str.title() == 'Hijo') & (Reserva_Avisados2['Importancia 1 - Estado'].str.title().isin(['Inválido','Invalido']) == True)),
               (Reserva_Avisados2['Importancia 1 - Parentesco'] == '0')]

choices = [6,5,4,3,2,0]
#%%
Reserva_Avisados2['42-Parent. 02'] = np.select(condictions, choices)

condictions = [(Reserva_Avisados2['Importancia 2 - Parentesco'] == 'Madre'),
               (Reserva_Avisados2['Importancia 2 - Parentesco'] == 'Padre'),
               (Reserva_Avisados2['Importancia 2 - Parentesco'] == 'Cónyuge'),
               ((Reserva_Avisados2['Importancia 2 - Parentesco'].str.title() == 'Hijo') & (Reserva_Avisados2['Importancia 2 - Estado'].str.title().isin(['Válido','Valido']) == True)),
               ((Reserva_Avisados2['Importancia 2 - Parentesco'].str.title() == 'Hijo') & (Reserva_Avisados2['Importancia 2 - Estado'].str.title().isin(['Inválido','Invalido']) == True)),
               (Reserva_Avisados2['Importancia 2 - Parentesco'] == '0')]

choices = [6,5,4,3,2,0]

Reserva_Avisados2['50-Parent. 03'] = np.select(condictions, choices)

condictions = [(Reserva_Avisados2['Importancia 1 - Género'] == 'M'),
               (Reserva_Avisados2['Importancia 1 - Género'] == 'F')]

choices = [1,2]

Reserva_Avisados2['45-Sexo'] = np.select(condictions, choices)

Reserva_Avisados2['53-Sexo'] = np.where((Reserva_Avisados2['Importancia 2 - Género'] == 'F'), 2, np.nan)

Reserva_Avisados2['49-Estado'] = np.where(Reserva_Avisados2['Importancia 1 - Estado'] == 'Válido', 1, np.nan)

Reserva_Avisados2['57-Estado'] = np.where(Reserva_Avisados2['Importancia 2 - Estado'] == 'Válido', 1, np.nan)


#%%

Reserva_Avisados2['% reconocido'] = 1 - Reserva_Avisados2['% comité judicial']
Reserva_Avisados2['Nuevos'] = 'Si'

## Despues de calcularle los campos que se necesitan para la reserva avisados se concatena con el historico
Reserva_Historica_Nueva = pd.concat([Reserva_Historica,Reserva_Avisados2]).reset_index(drop = True)

### Ahora se calcula el retroactivo el cual actualiza la informacion de los anteriores y se la calcula a los
### siniestros nuevos

Reserva_Historica_Nueva['29-Retroactivo'] = Retroactivo.Retroactivo(Reserva_Historica_Nueva, fecha, path_int)


#%%
Reserva_Historica_Nueva['10-No. de siniestro'] = CambioFormato(Reserva_Historica_Nueva, a = '10-No. de siniestro')

Objetados['No. Siniestro'] = CambioFormato(Objetados, a = 'No. Siniestro')
Liberaciones['Siniestro'] = CambioFormato(Liberaciones, a = 'Siniestro')
Matematica['Siniestro'] = CambioFormato(Matematica, a = 'Siniestro')

### Se extraen las liberaciones de los siniestros
Reserva_Historica_Nueva3 = Reserva_Historica_Nueva[Reserva_Historica_Nueva['10-No. de siniestro'].isin(Objetados['No. Siniestro']) == False]
Reserva_Historica_Nueva3 = Reserva_Historica_Nueva3[Reserva_Historica_Nueva3['10-No. de siniestro'].isin(Liberaciones['Siniestro']) == False]
Reserva_Historica_Nueva3 = Reserva_Historica_Nueva3[Reserva_Historica_Nueva3['10-No. de siniestro'].isin(Matematica['Siniestro']) == False]


#%%
### Se cruza la base con la tabla beneficiarios reales y se actualizan los datos
Benerficiarios_Reales['No. Siniestro'] = CambioFormato(Benerficiarios_Reales, a = 'No. Siniestro')
Reserva_Historica_Nueva2 = Reserva_Historica_Nueva3.merge(Benerficiarios_Reales, how = 'left', left_on = '10-No. de siniestro', right_on = 'No. Siniestro')

#%%

Reserva_Historica_Nueva2['42-Parent. 02'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Parent.1'],Reserva_Historica_Nueva2['42-Parent. 02'] )
Reserva_Historica_Nueva2['43-Tipo de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Tipo de identif.1'], Reserva_Historica_Nueva2['43-Tipo de identif.'] )
Reserva_Historica_Nueva2['44-No. de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['No. de identif.1'],Reserva_Historica_Nueva2['44-No. de identif.'] )
Reserva_Historica_Nueva2['45-Sexo'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Sexo1'],Reserva_Historica_Nueva2['45-Sexo'] )
Reserva_Historica_Nueva2.loc[Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, '46-Fecha de Nacimiento'] = Reserva_Historica_Nueva2['Fecha de Nacimiento1']
Reserva_Historica_Nueva2['47-Nombre'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Nombre1'],Reserva_Historica_Nueva2['47-Nombre'] )
Reserva_Historica_Nueva2['48-Estudios'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estudios1'],Reserva_Historica_Nueva2['48-Estudios'] )
Reserva_Historica_Nueva2['49-Estado'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estado1'],Reserva_Historica_Nueva2['49-Estado'] )

condictions = [(Reserva_Historica_Nueva2['49-Estado'].astype(str).str.upper().isin(['VÁLIDO','VALIDO','1','1.0']) == True),
               (Reserva_Historica_Nueva2['49-Estado'].astype(str).str.upper().isin(['INVÁLIDO','INVALIDO','2','2.0']) == True),
               (Reserva_Historica_Nueva2['49-Estado'].astype(str).str.upper().isin(['MUERTO','3','3.0']) == True)]

choices = [1,2,3]

Reserva_Historica_Nueva2['49-Estado'] = np.select(condictions, choices)

condictions = [(Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).str.title().isin(['Madre','6','6.0']) == True),
               (Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).str.title().isin(['Padre','5','5.0']) == True),
               (Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).str.title().isin(['Cónyuge','Conyuge','4','4.0']) == True),
               ((Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).isin(['3','3.0']) == True) | ((Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['49-Estado'] == 1))),
               ((Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).isin(['2','2.0']) == True) | ((Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['49-Estado'] == 2))),
               (Reserva_Historica_Nueva2['42-Parent. 02'].astype(str).isin(['0','0.0']) == True)]

choices = [6,5,4,3,2,0]

Reserva_Historica_Nueva2['42-Parent. 02 2'] = np.select(condictions, choices)

 
Reserva_Historica_Nueva2['50-Parent. 03'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Parent.2'],Reserva_Historica_Nueva2['50-Parent. 03'] )
Reserva_Historica_Nueva2['51-Tipo de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Tipo de identif.2'],Reserva_Historica_Nueva2['51-Tipo de identif.'] )
Reserva_Historica_Nueva2['52-No. de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['No. de identif.2'],Reserva_Historica_Nueva2['52-No. de identif.'] )
Reserva_Historica_Nueva2['53-Sexo'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Sexo2'],Reserva_Historica_Nueva2['53-Sexo'] )
Reserva_Historica_Nueva2.loc[Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False,'54-Fecha de Nacimiento'] = Reserva_Historica_Nueva2['Fecha de Nacimiento2']
Reserva_Historica_Nueva2['55-Nombre'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Nombre2'],Reserva_Historica_Nueva2['55-Nombre'] )
Reserva_Historica_Nueva2['56-Estudios'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estudios2'],Reserva_Historica_Nueva2['56-Estudios'] )
Reserva_Historica_Nueva2['57-Estado'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estado2'],Reserva_Historica_Nueva2['57-Estado'] )

condictions = [(Reserva_Historica_Nueva2['57-Estado'].astype(str).str.upper().isin(['VÁLIDO','VALIDO','1','1.0']) == True),
               (Reserva_Historica_Nueva2['57-Estado'].astype(str).str.upper().isin(['INVÁLIDO','INVALIDO','2','2.0']) == True),
               (Reserva_Historica_Nueva2['57-Estado'].astype(str).str.upper().isin(['MUERTO','3','3.0']) == True)]

choices = [1,2,3]

Reserva_Historica_Nueva2['57-Estado'] = np.select(condictions, choices)

condictions = [(Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).str.title().isin(['Madre','6','6.0']) == True),
               (Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).str.title().isin(['Padre','5','5.0']) == True),
               (Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).str.title().isin(['Cónyuge','Conyuge','4','4.0']) == True),
               ((Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).isin(['3','3.0']) == True) | ((Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['57-Estado'] == 1))),
               ((Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).isin(['2','2.0']) == True) | ((Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['57-Estado'] == 2))),
               (Reserva_Historica_Nueva2['50-Parent. 03'].astype(str).isin(['0','0.0']) == True)]

choices = [6,5,4,3,2,0]

Reserva_Historica_Nueva2['50-Parent. 03 2'] = np.select(condictions, choices)


Reserva_Historica_Nueva2['58-Parent. 04'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Parent.3'],Reserva_Historica_Nueva2['58-Parent. 04'] )
Reserva_Historica_Nueva2['59-Tipo de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Tipo de identif.3'],Reserva_Historica_Nueva2['59-Tipo de identif.'] )
Reserva_Historica_Nueva2['60-No. de identif.'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['No. de identif.3'],Reserva_Historica_Nueva2['60-No. de identif.'] )
Reserva_Historica_Nueva2['61-Sexo'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Sexo3'],Reserva_Historica_Nueva2['61-Sexo'] )
Reserva_Historica_Nueva2['62-Fecha de Nacimiento'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Fecha de Nacimiento3'],Reserva_Historica_Nueva2['62-Fecha de Nacimiento'] )
Reserva_Historica_Nueva2['63-Nombre'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Nombre3'],Reserva_Historica_Nueva2['63-Nombre'] )
Reserva_Historica_Nueva2['64-Estudios'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estudios3'],Reserva_Historica_Nueva2['64-Estudios'] )
Reserva_Historica_Nueva2['65-Estado'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, Reserva_Historica_Nueva2['Estado3'],Reserva_Historica_Nueva2['65-Estado'])

condictions = [(Reserva_Historica_Nueva2['65-Estado'].astype(str).str.upper().isin(['VÁLIDO','VALIDO','1','1.0']) == True),
               (Reserva_Historica_Nueva2['65-Estado'].astype(str).str.upper().isin(['INVÁLIDO','INVALIDO','2','2.0']) == True),
               (Reserva_Historica_Nueva2['65-Estado'].astype(str).str.upper().isin(['MUERTO','3','3.0']) == True)]

choices = [1,2,3]

Reserva_Historica_Nueva2['65-Estado'] = np.select(condictions, choices)

condictions = [(Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).str.title().isin(['Madre','6','6.0']) == True),
               (Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).str.title().isin(['Padre','5','5.0']) == True),
               (Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).str.title().isin(['Cónyuge','Conyuge','4','4.0']) == True),
               ((Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).isin(['3','3.0']) == True) | ((Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['65-Estado'] == 1))),
               ((Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).isin(['2','2.0']) == True) | ((Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).str.title() == 'Hijo') & (Reserva_Historica_Nueva2['65-Estado'] == 2))),
               (Reserva_Historica_Nueva2['58-Parent. 04'].astype(str).isin(['0','0.0']) == True)]

choices = [6,5,4,3,2,0]

Reserva_Historica_Nueva2['58-Parent. 04'] = np.select(condictions, choices)
#%%
Reserva_Historica_Nueva2['Hijo1 numerico valido'] = np.where(Reserva_Historica_Nueva2['42-Parent. 02'].astype(int) == 3, 1, 0)
Reserva_Historica_Nueva2['Hijo2 numerico valido'] = np.where(Reserva_Historica_Nueva2['50-Parent. 03'].astype(int) == 3, 1, 0)
Reserva_Historica_Nueva2['Hijo3 numerico valido'] = np.where(Reserva_Historica_Nueva2['58-Parent. 04'].astype(int) == 3, 1, 0)

Reserva_Historica_Nueva2['24-No. Hijos'] = Reserva_Historica_Nueva2['Hijo1 numerico valido'] + Reserva_Historica_Nueva2['Hijo2 numerico valido'] + Reserva_Historica_Nueva2['Hijo3 numerico valido']

Reserva_Historica_Nueva2['Hijo1 numerico invalido'] = np.where(Reserva_Historica_Nueva2['42-Parent. 02'].astype(int) == 2, 1, 0)
Reserva_Historica_Nueva2['Hijo2 numerico invalido'] = np.where(Reserva_Historica_Nueva2['50-Parent. 03'].astype(int) == 2, 1, 0)
Reserva_Historica_Nueva2['Hijo3 numerico invalido'] = np.where(Reserva_Historica_Nueva2['58-Parent. 04'].astype(int) == 2, 1, 0)

Reserva_Historica_Nueva2['25-No. hijos invalidos'] = Reserva_Historica_Nueva2['Hijo1 numerico invalido'] + Reserva_Historica_Nueva2['Hijo2 numerico invalido'] + Reserva_Historica_Nueva2['Hijo3 numerico invalido']

Reserva_Historica_Nueva2['85-Tipo beneficiarios'] = np.where(Reserva_Historica_Nueva2['No. Siniestro'].isnull() == False, 'Beneficiarios Reales',Reserva_Historica_Nueva2['85-Tipo beneficiarios'] )

#%%

Reserva_Historica_Nueva2 = Reserva_Historica_Nueva2[['01-Ramo','02-Unidad','03-Equivalencia','04-Tasa de crecim.',
       '05-Tipo de crecim.','06-Interés Técnico','07-Rentabil. Esperada','08-No. de poliza','09-Vigencia inicial',
       '10-No. de siniestro','11-Fecha de siniestro','12-Origen de la pensión','13-Clase de pensión',
       '14-Tiempo de  Diferimiento','15-Tiempo de  Temporalidad','16-Parent. 01','17-Tipo de identif.',
       '18-No. de identif.','19-Sexo','20-Fecha de Nacimiento','21-Nombre','22-Estudios','23-Estado','24-No. Hijos',
       '25-No. hijos invalidos','26-Ingreso base de liquidación','27-Mesada','28-Número de Mesadas','29-Retroactivo',
       '30-Grado de invalidez inicial','31-Fecha última modificación','32-Grado de invalidez actual',
       '33-Invalidez-Vejez-Jubilación','34-Sobrevivencia','35-Auxilio funerario','36-Otra','37-Gastos',
       '38-Total','39-Fondo de ahorro','40-Fondo rendim. ahorro','41-Cálculo partic. utilidad','42-Parent. 02',
       '43-Tipo de identif.','44-No. de identif.','45-Sexo','46-Fecha de Nacimiento','47-Nombre','48-Estudios',
       '49-Estado','50-Parent. 03','51-Tipo de identif.','52-No. de identif.','53-Sexo','54-Fecha de Nacimiento',
       '55-Nombre','56-Estudios','57-Estado','58-Parent. 04','59-Tipo de identif.','60-No. de identif.','61-Sexo', 
       '62-Fecha de Nacimiento','63-Nombre','64-Estudios','65-Estado','66-Número de Radicación de la Nota Técnica',
       '67-Interés Técnico Prima','68-Tasa de Crecimiento Prima','69-Gastos Prima','70-Prima Única',
       '71-Fecha Inicial Renta Diferida','72-Valor Mesada o Beneficio Periódico Diferido','73-Valor Auxilio Funerario',
       '74-Reserva Gastos','75-Utilidad Reconocida','76-Observaciones','77-VRRV89(0)','78-VRRV08(0)','79-PAR(0)',
       '80-%  Amort. Mensual Adicional (PARMA)','81-% Amort. en Exceso del PARMA','82-% Amort. Acumulado',
       '83-Fecha del Aviso del Siniestro','84-Total Reserva Estados Financieros','85-Tipo beneficiarios',
       '86-Constituida a sep/10','87-Se amortiza','Fecha siniestro','% comité judicial','Fecha_Calculo','Nuevos']]

Reserva_Historica_Nueva2['18-No. de identif.'] = Reserva_Historica_Nueva2['18-No. de identif.'].astype(str)
Reserva_Historica_Nueva2['27-Mesada'] = Reserva_Historica_Nueva2['27-Mesada'].astype(int)
Reserva_Historica_Nueva2['29-Retroactivo'] = Reserva_Historica_Nueva2['29-Retroactivo'].astype(int)
Reserva_Historica_Nueva2['73-Valor Auxilio Funerario'] = Reserva_Historica_Nueva2['73-Valor Auxilio Funerario'].fillna(0).astype(int)
#%%
lista = ['09-Vigencia inicial','11-Fecha de siniestro','20-Fecha de Nacimiento','31-Fecha última modificación',
         '46-Fecha de Nacimiento','54-Fecha de Nacimiento','62-Fecha de Nacimiento','83-Fecha del Aviso del Siniestro',
         'Fecha siniestro','Fecha_Calculo']

for i in lista:
    print(i)
    Reserva_Historica_Nueva2[i] = pd.to_datetime(Reserva_Historica_Nueva2[i], format = '%Y-%m-%d')
    Reserva_Historica_Nueva2[i] = Reserva_Historica_Nueva2[i].dt.strftime('%d/%m/%Y')

#%%

Liberaciones['Fecha'] = fecha
Liberaciones = Liberaciones.rename(columns = {'Siniestro':'No. Siniestro'})
Matematica = Matematica.rename(columns = {'Siniestro':'No. Siniestro'})

Objetados['Fecha'] = fecha
Matematica['Fecha'] = fecha


Liberaciones_hist = pd.concat([Liberaciones_hist, Liberaciones, Objetados]).reset_index(drop = True)
Liberaciones_hist = Liberaciones_hist.drop_duplicates('No. Siniestro', keep = 'last')

print('\n La cantidad de siniestros que habían al comienzo eran ',str(Reserva_Historica.shape[0]),' registros')
print('La cantidad de siniestros nuevos son ',str(Reserva_Avisados.shape[0]),' registros')
print('La cantidad de siniestros al final para la reserva con liberados son ',str(Reserva_Historica_Nueva2.shape[0]),' registros')


print('\n Guardando archivo Formato 394 de',ConvertirMes(fecha.strftime('%m')),str(fecha.strftime('%Y')))
Reserva_Historica_Nueva2.to_excel(path_out + '\Formato 394 de ' + ConvertirMes(fecha.strftime('%m')) + ' ' + str(fecha.strftime('%Y')) + '.xlsx', index = False)
print('Formato 394 de',ConvertirMes(fecha.strftime('%m')), str(fecha.strftime('%Y')),'guardado')

print('\n Guardando historico de liberaciones')
Liberaciones_hist.to_excel(path_out + '\Historico de Liberaciones.xlsx', index = False)
print('Historico de liberaciones guardado')

print('\n Proceso finalizado')

print("Tiempo del Proceso: " , datetime.now()-Tiempo_Total)

















