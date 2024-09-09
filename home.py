import pandas as pd
import streamlit as st
from utils import bom 
from utils import dataprep as dp
from utils import print as pt

st.set_page_config(layout="wide")
sx,cx,dx = st.columns([3,5,1])
with sx:
    st.title("Analisi distinte")
with dx:
    st.image('https://github.com/alebelluco/delta_24/blob/main/Ducati_red_logo.png?raw=True')


# Guida

if st.sidebar.toggle('Help'):

    st.subheader('Istruzioni',divider='grey')
    with st.expander('Caricamento dati'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/Caricamento_dati.png?raw=True', width=1000)

    st.subheader('Interpretazione risultati', divider='grey')
    with st.expander('1_Controllo piattaforme mancanti o in più rispetto allo standard'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/1.png?raw=True',output_format='PNG', width=1500)

    with st.expander('2_Overview test'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/2.png?raw=True', width=1500)

    with st.expander('3_Test cardinalità'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/cardinalita.png?raw=True', width=1500)

    with st.expander('4_Test duplicati'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/3.png?raw=True', width=1500)

    with st.expander('5_Test quantità'):
        st.image('https://github.com/alebelluco/delta_24/blob/main/Istruzioni/4.png?raw=True', width=1500)


    st.stop()



# Importazione multipla file
df_list = dp.upload_multiplo('Caricare i file da analizzare')
#st.write(df_list[1])

#--------------------------------------------------------------------------------------------------
# Test:
# 1) La BOM deve contenere i codici piattaforma nella cardinalità indicata nel dizionario standard.
# 2) All'interno dei codici piattaforma con cardinalità >1 non devono esserci codici duplicati.
#--------------------------------------------------------------------------------------------------

# dizionario standard: contiene la cardinalità di ogni chiave first4

dic_rs = {
  "340P": 1,
  "342P": 1,
  "360S": 1,
  "370P": 1,
  "470S": 1,
  "480P": 3,
  "492S": 1,
  "494S": 1,
  "499P": 1,
  "500P": 1,
  "561S": 1,
  "585P": 1,
  "586P": 1,
  "627P": 1,
  "630P": 1,
  "819P": 1
}

dic_s = {
    "340P":1,   
    "342P":1,
    "360S":1,
    "370P":1,
    "460P":2,
    "470S":1,
    "480P":7,
    "494P":1,
    "499P":1,
    "500P":1,
    "561S":1,
    "585P":1,
    "586P":1,
    "627P":1,
    "630P":1,
    "936S":1
}

dic_rally = {
  "340P": 1,
  "342P": 1,
  "360S": 1,
  "370P": 1,
  "460P": 2,
  "470S": 1,
  "480P": 3,
  "480S": 2,
  "494S": 1,
  "499P": 1,
  "500P": 1,
  "561S": 1,
  "585P": 1,
  "586P": 1,
  "627P": 1,
  "630P": 1
}

dic_pp = {
  "340P": 1,
  "342P": 1,
  "360S": 1,
  "370P": 1,
  "460P": 2,
  "470S": 1,
  "480P": 3,
  "492S": 1,
  "494S": 1,
  "499P": 1,
  "500P": 1,
  "561S": 1,
  "585P": 1,
  "586P": 1,
  "627P": 1,
  "630P": 1,
  "819P": 1,
  "936S": 1
}

dic_base = {
  "340P": 1,
  "342P": 1,
  "360S": 1,
  "370P": 1,
  "460P": 2,
  "470S": 1,
  "480P": 7,
  "494P": 1,
  "499P": 1,
  "500P": 1,
  "561S": 1,
  "585P": 1,
  "586P": 1,
  "627P": 1,
  "630P": 1,
  "936S": 1
}

# dizionario di abbinamento modello - dizionari standard

dic_modelli = {
    'S ': ('S',dic_s),
    'ST': ('S',dic_s),
    'SP': ('S',dic_s),
    'ST': ('S',dic_s),
    'SI': ('S',dic_s),
    'RS': ('RS',dic_rs),
    'RI': ('Rally',dic_rally),
    'RT': ('Rally',dic_rally),
    'PP': ('Pikes Peak',dic_pp),
    ' 2': ('Base',dic_base)
}

# Note
# - Aggiungere controllo sulle quantità | le quantità (escludendo il motore) sono sempre 1 --> il test guarda cosa c'è con qty != 1
# - La STI ha una piattaforma in più. forse dipende dallo standard nazione e non dal modello | 827SH401AA STGR STAFFA SUPP. LAT. CATADIOTTRO USA|
# - Nel report far uscire le piattaforme in più (o in meno)


# SKU di test
# 480P, cardinalit standard 7 --> duplicati 2 valori all'interno mantenendo 7 come cardinalità
# 340P (stgr forcella) rimosso dalla distinta
# aggiunto codice piattaforma a caso (121P)

# Routine di test -----------------------------------------

# qui vanno creati:
# - un dataframe delle SKU riassuntivo 
# - un dataframe delle eccezioni globale
# Questi dataframe vanno poi passati come input al metodo "test"

df_eccezioni = pd.DataFrame(columns=['SKU','Modello','first4','Articolo','Testo breve oggetto','Alert'])
df_globale = pd.DataFrame(columns=['SKU','Modello','first4','test_cardinalità','test_duplicati','test_quantità'])

for i in range(len(df_list)):
    no_mot = dp.rimuovi_motore(df_list[i])
    desc_moto = no_mot['Testo breve oggetto'].iloc[0]
    modello = desc_moto[4:6]
    dic = dic_modelli[modello][1]
    fam = dic_modelli[modello][0]
    cod_moto = no_mot['Numero componenti'].iloc[0]
    df_test = dp.piattaforme(no_mot)
    out = dp.test(df_test, dic, df_eccezioni,cod_moto, fam)[0]
    out['SKU'] = cod_moto
    out['Modello'] = fam
    df_globale = pd.concat([df_globale,out])
    #st.write(cod_moto, desc_moto, fam)
    #st.write(out)
    ecc = dp.test(df_test, dic, df_eccezioni,cod_moto, fam)[1]
    df_eccezioni = pd.concat([df_eccezioni,ecc])

#700008

def highlight(df):
    if (df['test_cardinalità']=='NOK') | (df['test_duplicati']=='NOK') | (df['test_quantità']=='NOK') :
        return ['background-color: #F04F2D']*len(df)
    else:
        return ['background-color: #0E1116']*len(df)


df_globale['count_rif'] = df_globale['count_rif'].astype(int)
df_globale['val_bom'] = df_globale['val_bom'].astype(int)
df_globale['distinti'] = df_globale['distinti'].astype(int)

df_globale = df_globale.reset_index(drop=True)
df_eccezioni = df_eccezioni.drop_duplicates()
df_eccezioni = df_eccezioni.reset_index(drop=True)

st.subheader('Tabella riassuntiva SKU', divider='red')
st.dataframe(df_globale.style.apply(highlight, axis=1))
dp.scarica_excel(df_globale, 'report_globale.xlsx')
st.subheader('Alert report', divider='red')
st.write(df_eccezioni)
dp.scarica_excel(df_eccezioni, 'alert_report.xlsx')






