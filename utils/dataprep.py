# Package per l'importazione e la preparazione dei dati
# AB_10/05/2024
#
#
# -----------------------------------------------------

import pandas as pd
import streamlit as st 
from io import BytesIO

def upload(messaggio):
    path = st.sidebar.file_uploader(messaggio)
    if not path:
        st.stop()
    df = pd.read_excel(path)
    return df,path

def upload_multiplo(messaggio):
        path_list = st.sidebar.file_uploader(messaggio,accept_multiple_files=True)
        if not path_list:
              st.stop()
        df_list = []
        for path in path_list:
                df = pd.read_excel(path)
                df_list.append(df)
        return df_list

def rimuovi_motore(df):
        indice_motore = 0
        df['rimuovi'] = None
        for i in range (len (df)):
                if df.loc[i,'Numero componenti'].startswith('0029'):
                        indice_motore = i
                        livello = '..2'
                        df['rimuovi'].iloc[i]='x'
                        for j in range(indice_motore+1,len(df)):
                                liv_check = df['Liv. esplosione'].iloc[j]
                                if liv_check != livello:
                                        df['rimuovi'].iloc[j]='x'
                                else:
                                      break
        df = df[df.rimuovi !='x']
        df = df.drop(columns='rimuovi')
        return df

def piattaforme(df_input):
    df_input = df_input.rename(columns={'Numero componenti':'Articolo'})
    codici_piattaforma = ['P','S','T']
    #codici_piattaforma = ['P','S','T','Z']
    #df = list(set(list(df_input[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in df_input.Articolo.astype(str)]].Articolo)))
    df = df_input[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in df_input.Articolo.astype(str)]]
    return df

def test(df, dic):
        riferimento = pd.DataFrame({'first4':dic.keys(), 'count_rif':dic.values()})
        df['first4'] = [articolo[:4] for articolo in df.Articolo]
        df_car = df[['first4','Articolo']].groupby(by='first4',as_index=False).count() #car sta per cardinalità
        df_car = df_car.rename(columns={'Articolo':'val_bom'})
        df_distinct = df[['first4','Articolo']].groupby(by='first4',as_index=False).nunique()
        st.write(df_distinct)
        st.write(df)
        df_distinct = df_distinct.rename(columns={'Articolo':'distinti'})
        riferimento = riferimento.merge(df_car, how='outer',left_on = 'first4',right_on = 'first4')
        riferimento = riferimento.merge(df_distinct, how='outer',left_on = 'first4',right_on = 'first4')
        # test 1 - confronto con dizionario standard
        riferimento['test'] = None
        for i in range(len(riferimento)):
                if riferimento['count_rif'].iloc[i] == riferimento.val_bom.iloc[i]:
                       riferimento['test'].iloc[i] = 'OK'
                else:
                       riferimento['test'].iloc[i] = 'NOK'
                
        return riferimento

def sap_raw (df):
        if df.columns[21]=='Descr. Gruppo Tecnico.1':
             df = df.rename(columns={'Descr. Gruppo Tecnico.1':'Descr. Gruppo Appartenenza'})
        
        #df = df.rename(columns={'Qtà comp.(UMB)':'Qtà comp. (UMC)'})

        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        df = df[['Liv.','Materiale','Qtà comp. (UMC)','MerceSfusa (BOM)','Ril.Tecn.','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Ril.Prod.','Ril.Ric.','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Materiale':'Articolo','Qtà comp. (UMC)':'Qty'},inplace=True)
        df['Liv.']=df['Liv.'].astype(int)
        #df = df[df['MerceSfusa (BOM)']=='No']
        return df

def sap_raw_test (df): #andava bene con il layout utilizzato per  lo sviluppo
        if df.columns[21]=='Descr. Gruppo Tecnico.1':
             df = df.rename(columns={'Descr. Gruppo Tecnico.1':'Descr. Gruppo Appartenenza'})
        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        df = df[['Liv.','Materiale','Qtà comp. (UMC)','MerceSfusa (BOM)','Ril.Tecn.','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Ril.Prod.','Ril.Ric.','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Materiale':'Articolo','Qtà comp. (UMC)':'Qty'},inplace=True)
        df['Liv.']=df['Liv.'].astype(int)
        #df = df[df['MerceSfusa (BOM)']=='No']
        return df

def plm_raw (df):
        if df.columns[21]=='Descr. Gruppo Tecnico.1':
             df = df.rename(columns={'Descr. Gruppo Tecnico.1':'Descr. Gruppo Appartenenza'})
        
        df = df.rename(columns={'Qtà comp. (UMB)':'Qtà comp. (UMC)'})

        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        #df['Liv.']=df['Liv.'].astype(int)-1
        df = df[['Liv.','Numero componenti','Qtà comp. (UMC)','Merce sfusa','Ril. progettazione','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Rilevante produzione','Cd.parte di ricambio','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Numero componenti':'Articolo','Qtà comp. (UMC)':'Qty','Merce sfusa':'MerceSfusa (BOM)','Ril. progettazione':'Ril.Tecn.','Rilevante produzione':'Ril.Prod.','Cd.parte di ricambio':'Ril.Ric.'},
                inplace=True)
        #df = df.fillna(0) eliminato 28/12
        df['Liv.']= df['Liv.'].astype(int)
        df['MerceSfusa (BOM)']=df['MerceSfusa (BOM)'].apply(lambda x: 'Sì' if x == 'X' else 'No' )        
        df['Ril.Tecn.']=df['Ril.Tecn.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Prod.']=df['Ril.Prod.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Ric.']=df['Ril.Ric.'].apply(lambda x: True if x  =='X' else False)      
        #df = df[df['MerceSfusa (BOM)']=='No']

        return df

def plm_raw_test (df): #andava bene con il layout utilizzato per  lo sviluppo
        if df.columns[21]=='Descr. Gruppo Tecnico.1':
             df = df.rename(columns={'Descr. Gruppo Tecnico.1':'Descr. Gruppo Appartenenza'})
        


        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        #df['Liv.']=df['Liv.'].astype(int)-1
        df = df[['Liv.','Numero componenti','Qtà comp. (UMC)','Merce sfusa','Ril. progettazione','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Rilevante produzione','Cd.parte di ricambio','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Numero componenti':'Articolo','Qtà comp. (UMC)':'Qty','Merce sfusa':'MerceSfusa (BOM)','Ril. progettazione':'Ril.Tecn.','Rilevante produzione':'Ril.Prod.','Cd.parte di ricambio':'Ril.Ric.'},
                inplace=True)
        #df = df.fillna(0) eliminato 28/12
        df['Liv.']= df['Liv.'].astype(int)
        df['MerceSfusa (BOM)']=df['MerceSfusa (BOM)'].apply(lambda x: 'Sì' if x == 'X' else 'No' )        
        df['Ril.Tecn.']=df['Ril.Tecn.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Prod.']=df['Ril.Prod.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Ric.']=df['Ril.Ric.'].apply(lambda x: True if x  =='X' else False)      
        #df = df[df['MerceSfusa (BOM)']=='No']

        return df

def piattaforme_plm(PLM_raw):
    codici_piattaforma = ['P','S','T','Z']   
    df = list(set(list(PLM_raw[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in PLM_raw.Articolo.astype(str)]].Articolo)))
    return df

def scarica_excel(df, filename):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )


'''

Script per la creazione dei dizionari standard
- viene prima eliminato il motore dalle distinte
- vengono estratte le piattaforme
- vengono estratti i primi 4digit del codice
- vengono contate

for i in range(len(df_list)):
    no_mot = dp.rimuovi_motore(df_list[i])
    df_test = dp.piattaforme(no_mot)
    out = dp.test(df_test)
    out = out.rename(columns={'Articolo':f'Articolo_{i}'})
    if i==0:
        tot = out
    else:
        tot = tot.merge(out, how='left',left_on='first4',right_on='first4')

st.write(tot)
# creazione dizionari

valori = list(tot.Articolo_0)
chiavi = list(tot.index)
dizionario = dict(zip(chiavi,valori))
st.write(dizionario)
'''