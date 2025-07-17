import streamlit as st
from PIL import Image
import easyocr
import re

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Regex patterns
date_pattern = re.compile(r"\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b", re.IGNORECASE)
amount_pattern = re.compile(r"[₹]?\s?([+-]?[,\d]+\.\d{2}|\d+)", re.IGNORECASE)

def parse_upi_ocr_text(raw_text_lines):
    parsed = []
    current_date = None

    for i, line in enumerate(raw_text_lines):
        text = line.strip()

        # Step 1: Detect and store date
        if date_pattern.match(text):
            current_date = text
            continue

        # Step 2: If this line has an amount, and previous line is merchant
        amount_match = amount_pattern.match(text.replace(",", ""))
        if amount_match:
            try:
                amount = float(amount_match.group(1).replace(",", ""))
                merchant = raw_text_lines[i-1].strip() if i > 0 else "Unknown"

                parsed.append({
                    "date": current_date or "Unknown",
                    "merchant": merchant,
                    "amount": amount
                })
            except:
                continue

    return parsed

def handle_upi_screenshots():
    st.header("🖼️ Upload UPI Payment Screenshots")

    uploaded_files = st.file_uploader(
        "Upload screenshot",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        help="Limit 200MB per file • PNG, JPG, JPEG"
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded.")
        for file in uploaded_files:
            image = Image.open(file)
            st.image(image, caption=file.name, width=300)

            # OCR
            with st.spinner("Extracting text..."):
                ocr_result = reader.readtext(image, detail=0)
                st.subheader("📄 Extracted Text")
                st.code("\n".join(ocr_result))

                parsed_data = parse_upi_ocr_text(ocr_result)
                st.subheader("📊 Parsed Transactions")
                st.json(parsed_data)
