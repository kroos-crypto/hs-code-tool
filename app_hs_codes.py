import streamlit as st
import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from hs_code_classifier import classify_hs_code, get_notes
import io

st.set_page_config(page_title="HS Code Filler", layout="wide")
st.title("HS Code Auto-Filler")
st.markdown("Excel hochladen – HS Codes werden automatisch eingetragen")

uploaded_file = st.file_uploader("Excel Datei hier hochladen", type=['xlsx', 'xls'])

if uploaded_file:
    st.success("Datei hochgeladen!")
    df = pd.read_excel(uploaded_file, sheet_name='Data sheet')
    unique = df.drop_duplicates(subset=['Style number']).copy()
    st.info(str(len(unique)) + " verschiedene Produkttypen gefunden")

    results = []
    for idx, row in unique.iterrows():
        code = classify_hs_code(row)
        count = len(df[df['Style number'] == row['Style number']])
        results.append({
            'Produkt': row['Style/Display name'],
            'Kategorie': row['Boozt Product Category'],
            'Geschlecht': row.get('Gender (F = Female, M = Male, U = Unisex)', ''),
            'HS Code': code,
            'Varianten': count,
            'Beschreibung': get_notes(code)
        })

    st.subheader("Automatische Klassifizierung")
    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    hs_mapping = dict(zip(unique['Style number'], [classify_hs_code(r) for _, r in unique.iterrows()]))

    if st.button("HS Codes eintragen und Excel downloaden", use_container_width=True):
        input_buffer = io.BytesIO(uploaded_file.getvalue())
        wb = load_workbook(input_buffer)
        ws = wb['Data sheet']

        col_idx = None
        style_col_idx = None
        for cell in ws[1]:
            if cell.value == 'Customs code/Tariff Code (Sweden)':
                col_idx = cell.column
            if cell.value == 'Style number':
                style_col_idx = cell.column

        if col_idx and style_col_idx:
            for row_idx in range(2, ws.max_row + 1):
                style_val = ws.cell(row=row_idx, column=style_col_idx).value
                if style_val in hs_mapping:
                    ws.cell(row=row_idx, column=col_idx, value=hs_mapping[style_val])

        output_buffer = io.BytesIO()
        wb.save(output_buffer)
        output_buffer.seek(0)

        st.success("Fertig!")
        st.download_button(
            label="Excel herunterladen",
            data=output_buffer.getvalue(),
            file_name=Path(uploaded_file.name).stem + "_with_hs_codes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("Bitte lade deine Excel-Datei hoch")
