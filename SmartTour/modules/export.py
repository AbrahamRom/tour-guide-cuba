import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

    # st.button("Compartir por correo")
    # st.button("Compartir en redes sociales")

def render(state):
    st.header("📤 Exportar / Compartir")

    itinerary = state.get("itinerary", [])

    # Exportar a Excel
    if st.button("Descargar itinerario (Excel)"):
        df = pd.DataFrame(itinerary)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Itinerario')
        st.download_button(
            label="Descargar archivo Excel",
            data=output.getvalue(),
            file_name="itinerario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Exportar a PDF (muy básico)
    if st.button("Descargar itinerario (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Itinerario", ln=True, align='C')
        for item in itinerary:
            pdf.cell(200, 10, txt=str(item), ln=True)
        pdf_output = BytesIO(pdf.output(dest='S').encode('latin1'))
        st.download_button(
            label="Descargar archivo PDF",
            data=pdf_output,
            file_name="itinerario.pdf",
            mime="application/pdf"
        )

    # Compartir por correo y redes sociales: normalmente mostrarías instrucciones o un enlace, ya que Streamlit no puede enviar correos directamente sin backend.
    st.info("Para compartir por correo o redes sociales, descarga el archivo y adjúntalo en tu plataforma preferida.")
