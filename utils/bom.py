# Package per le operazioni sulle BOM
# AB_10/05/2024
#
# -------------------------------------------------

import pandas as pd 
import streamlit as  st

def rimuovi_motore(df):
    df['elimina'] = False
    for i in range(len(df)):
        codice = str(df.Articolo.iloc[i])
        if codice[0:4]=='0029':
            df.elimina.iloc[i]=True
            livello = df['Liv.'].iloc[i]
            riga = i
            for j in range(riga+1, len(df)):
                liv_check = df['Liv.'].iloc[j]
                if liv_check > livello:
                    df.elimina.iloc[j]=True
                else:
                    break    
    df = df[df.elimina == False]
    df = df.reset_index(drop=True)
    df = df.drop(columns=['elimina'])
    return df

def estrai_piattaforme(df):
    '''
    Funzione con doppio return
    --------------------------
    [0] = piattaforme \n
    [1] = no_piattaforme
    '''
    codici_piattaforma = ['P','S','T']
    df['piattaforma']=False
    df['Piattaforma']=None
    df['Desc_piattaforma']=None
    for i in range(len(df)):
        art = str(df.Articolo.iloc[i])[3:4]
        if any([digit in art for digit in codici_piattaforma]):
            df['piattaforma'].iloc[i]=True
            piattaforma = df.Articolo.iloc[i]
            desc_piatt = df['Testo breve oggetto'].iloc[i]
            df['Piattaforma'].iloc[i]=piattaforma
            df['Desc_piattaforma'].iloc[i]=desc_piatt

            liv = df['Liv.'].iloc[i]
            if i != len(df):
                for j in range(i+1, (len(df))):
                    liv_check = df['Liv.'].iloc[j]
                    if liv_check > liv:
                        df.piattaforma.iloc[j] = True
                        df['Piattaforma'].iloc[j]=piattaforma
                        df['Desc_piattaforma'].iloc[j]=desc_piatt
                    else:
                        break
    piattaforme = df[df.piattaforma == True].reset_index(drop=True)
    no_piatt = df[df.piattaforma == False].reset_index(drop=True)

    return piattaforme, no_piatt
    
def livello1(df):
    '''
    NOTA
    ---
    Da applicare dopo aver tolto il motore
    '''
    livelli1 = ['M','V','X']
    df['L1']=None
    for i in range(len(df)):
        art = str(df.Articolo.iloc[i])[0:1]
        if any([digit in art for digit in livelli1]):
            df.L1.iloc[i] = art
            if i != len(df):
                for j in range(i+1, len(df)):
                    check = str(df.Articolo.iloc[j])[0:1]
                    if all([digit not in check for digit in livelli1]):
                        df.L1.iloc[j] = art
                    else:
                        break

    return df

def elabora_motore(df):
    '''
    Doppio output:
    ---
    [0] = df \n
    [1] = warning (lista)
    Elimina righe gruppi tecnici
    Riduce di 1 il livello
    Ripeete info GT a livelli >1
    '''

    df = df[df['Liv.'] != 1]
    df['Liv.'] = df['Liv.']-1

    for i in range(len(df)):
        gt = str(df['Gruppo Tecnico'].iloc[i])
        if gt == 'nan':
            if df['Liv.'].iloc[i] > df['Liv.'].iloc[i-1]:
                gt_new = df['Gruppo Tecnico'].iloc[i-1]
                dgt_new = df['Descr. Gruppo Tecnico'].iloc[i-1]
                livello = df['Liv.'].iloc[i-1]
                for j in range(i, len(df)):
                    if (str(df['Gruppo Tecnico'].iloc[j])=='nan') and (df['Liv.'].iloc[j]>livello):
                        df['Gruppo Tecnico'].iloc[j] = gt_new
                        df['Descr. Gruppo Tecnico'].iloc[j] =  dgt_new
                    else:
                        break
    return df

def add_padre(df):
    # la funzione prende in ingresso un albero (df) di distinta e accanto a ogni codice scrive il nome di suo padre
    df['Padre']=None
    for i in range(len(df)):
        livello = df['Liv.'].iloc[i]
        if livello == 1:
            df['Padre'].iloc[i]='Motore'
        elif livello == df['Liv.'].iloc[i-1]+1:
            df['Padre'].iloc[i]=df['Articolo'].iloc[i-1]
        else:
            for j in range(1,i):
                liv_check = df['Liv.'].iloc[i-j]
                if liv_check == livello:
                    df['Padre'].iloc[i]=df['Padre'].iloc[i-j] 
                    break
    return df
            
def key(df,col1,col2,col3,col4):
    #df['key']=df[col1].astype(str)+df[col2].astype(str)+df[col3].astype(str)+df[col4].astype(str)
    df['key']=[(df[col1].astype(str).iloc[i],df[col2].astype(str).iloc[i],df[col3].astype(str).iloc[i],df[col4].astype(str).iloc[i]) for i in range(len(df))]
    return df

def key3(df,col1,col2,col3):
    #df['key']=df[col1].astype(str)+df[col2].astype(str)+df[col3].astype(str)+df[col4].astype(str)
    df['key']=[(df[col1].astype(str).iloc[i],df[col2].astype(str).iloc[i],df[col3].astype(str).iloc[i]) for i in range(len(df))]
    return df

def rimuovi_sfusa(df):
    for i in range(len(df)):
        sfusa_check = df['MerceSfusa (BOM)'].iloc[i]
        if sfusa_check=='Sì':
            livello = df['Liv.'].iloc[i]
            for j in range(i,len(df)):
                if df['Liv.'].iloc[j]>livello:
                    df['MerceSfusa (BOM)'].iloc[j]='Sì'
                else:
                    break
    return df

def count_chiavi(df,key,count,articolo,cols=[]):
    df = df[cols].copy()
    df = df.groupby('Articolo',as_index=False).key.nunique()
    df = df.rename(columns={'key':count, 'Articolo':articolo})
    return df




