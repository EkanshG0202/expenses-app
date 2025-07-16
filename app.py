import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Budget Tracker", layout="centered")

st.title("💸 Smart Budget Tracker")

st.markdown("Upload your monthly expenses and get useful insights.")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file of your expenses", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # Show raw data
        st.subheader("📄 Raw Expense Data")
        st.dataframe(df)

        # Basic summary
        st.subheader("📊 Expense Summary")
        if 'Amount' in df.columns and 'Category' in df.columns:
            category_summary = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            st.bar_chart(category_summary)

            # Pie chart
            fig, ax = plt.subplots()
            category_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
            ax.set_ylabel('')
            st.pyplot(fig)

        else:
            st.error("The uploaded CSV must have 'Amount' and 'Category' columns.")

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("Please upload a CSV file to get started.")

st.markdown("---")
st.caption("Made with ❤️ using Streamlit")
