# Package per la stampa a video con layout
# AB_10/05/2024
#
# ----------------------------------------

import pandas as pd
import streamlit as st 
from io import BytesIO
import xlsxwriter


def stampa(df,intestazione,layout, layout_scelto, colore_divider='red'):
    st.subheader(intestazione, divider=colore_divider)
    st.dataframe(
        df[layout[layout_scelto]['cols']], 
        height=layout[layout_scelto]['h'], 
        width=layout[layout_scelto]['w']
                 )

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