import streamlit as st
from PIL import Image
from upi_screenshot_parser import handle_upi_screenshots

def render_upload_tabs():
    tab1, tab2, tab3 = st.tabs(["🏦 Bank Statement", "📱 UPI App Statement", "🖼️ UPI Screenshot"])

    with tab1:
        st.header("📄 Upload Bank Statement")
        st.info("Coming soon: Upload your bank statement PDFs or CSVs and parse them.")

        uploaded_file = st.file_uploader("Upload bank statement", type=["pdf", "csv"], key="bank")
        if uploaded_file:
            st.success("✅ File uploaded successfully!")

    with tab2:
        st.header("📱 Upload UPI App Statement")
        st.info("Coming soon: Upload UPI app statements for processing.")

        uploaded_file = st.file_uploader("Upload UPI app statement", type=["pdf", "csv"], key="upi")
        if uploaded_file:
            st.success("✅ File uploaded successfully!")

    with tab3:
            handle_upi_screenshots()