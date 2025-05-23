import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from fpdf import FPDF
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="📁 Document Tracker", layout="wide")

# تحميل البيانات
try:
    df = pd.read_csv("documents.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "File Name", "Doc Ref", "Document Title", "Status", "Discipline",
        "File Type", "Rev Date", "Delivery Date", "Project", "Originator", "Project Stage"
    ])

status_options = ["A - Approved", "B - Approved with Comments", "C - Revise and Resubmit", "D - Rejected"]
discipline_options = ["Architecture", "Civil", "Electrical", "Mechanical", "Surveying"]

st.title("📁 Document Tracker")

# ➕ إضافة مستند
with st.form("add_doc"):
    st.subheader("➕ Add New Document")
    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("File Name")
        doc_ref = st.text_input("Doc Ref")
        title = st.text_input("Document Title")
        status = st.selectbox("Status", [""] + status_options)
        discipline = st.selectbox("Discipline", discipline_options)
        file_type = st.text_input("File Type")
    with col2:
        rev_date = st.date_input("Rev Date", value=datetime.date.today())
        delivery_date = st.date_input("Delivery Date", value=datetime.date.today())
        project = st.text_input("Project")
        originator = st.text_input("Originator")
        stage = st.text_input("Project Stage")
    submitted = st.form_submit_button("💾 Save")

    if submitted:
        if not all([file_name, doc_ref, title, discipline, file_type, project, originator, stage]):
            st.warning("❗ Please fill in all required fields before saving.")
        else:
            new_row = {
                "File Name": file_name, "Doc Ref": doc_ref, "Document Title": title,
                "Status": status, "Discipline": discipline, "File Type": file_type,
                "Rev Date": rev_date, "Delivery Date": delivery_date,
                "Project": project, "Originator": originator, "Project Stage": stage
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv("documents.csv", index=False)
            st.success("✅ Document added!")
            st.rerun()

# 🗂️ جدول قابل للتعديل (AgGrid)
st.subheader("🗂️ All Documents (Editable)")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)
gb.configure_column("Status", cellEditor='agSelectCellEditor', cellEditorParams={'values': status_options})
gb.configure_column("Discipline", cellEditor='agSelectCellEditor', cellEditorParams={'values': discipline_options})
gb.configure_selection('single')
gb.configure_grid_options(domLayout='autoHeight')

grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False
)

# 💾 حفظ التعديلات
if st.button("💾 Save All Changes"):
    updated_df = grid_response['data']
    updated_df.to_csv("documents.csv", index=False)
    st.success("✅ All changes saved!")

# ⬇️ التصدير PDF و CSV
st.subheader("⬇️ Export Data")
col_pdf, col_csv = st.columns(2)

# PDF
with col_pdf:
    if st.button("📄 Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="All Documents", ln=True, align="C")
        for i, row in df.iterrows():
            line = f"{row['File Name']} | {row['Doc Ref']} | {row['Document Title']} | {row['Status']}"
            pdf.cell(200, 8, txt=line, ln=True)
        buffer = BytesIO()
        pdf.output(buffer)
        st.download_button("⬇️ Download PDF", data=buffer.getvalue(), file_name="documents.pdf")

# CSV
with col_csv:
    st.download_button("⬇️ Download CSV", data=df.to_csv(index=False), file_name="documents.csv", mime="text/csv")
