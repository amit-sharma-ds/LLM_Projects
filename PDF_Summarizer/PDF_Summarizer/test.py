import streamlit as st
from utils import summarizer

def main():
    st.set_page_config(page_title="PDF Summarizer", layout="centered")

    st.title("📄 PDF Summarizer")
    st.write("Upload a PDF and get a quick summary instantly.")

    st.divider()

    pdf = st.file_uploader("Upload your PDF", type=["pdf"])

    if st.button("Generate Summary"):
        if pdf is not None:
            with st.spinner("⏳ Processing..."):
                result = summarizer(pdf)

            st.success("✅ Summary Generated")
            st.subheader("Summary:")
            st.write(result)

        else:
            st.warning("⚠️ Please upload a PDF first.")

if __name__ == "__main__":
    main()