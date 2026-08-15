import streamlit as st
import PyPDF2

# --- APP SETUP & THEME ---
st.set_page_config(page_title="PDF Reader App", page_icon="📄", layout="centered")

# Black and Yellow Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    h1, h2, h3, p, span, label, div {
        color: #FFD700 !important; 
    }
    .stButton>button {
        background-color: #FFD700;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #CCAC00;
        color: #000000 !important;
    }
    .text-box {
        background-color: #1A1A00;
        padding: 20px;
        border: 1px solid #FFD700;
        border-radius: 8px;
        color: #FFFFFF !important;
        white-space: pre-wrap;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 PDF Reader App")
st.write("Upload your PDF document below to extract and read its text instantly!")

st.write("---")
uploaded_file = st.file_uploader("📁 Upload your PDF file here", type="pdf")

if uploaded_file is not None:
    with st.spinner('Reading PDF file... Please wait! ⏳'):
        try:
            # Extracting text from PDF using PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text += f"\n--- Page {i+1} ---\n" + extracted + "\n"
            
            st.success("PDF successfully read!")
            st.subheader("📖 Extracted PDF Content:")
            
            # Displaying extracted text in a clean box
            st.markdown(f'<div class="text-box">{text}</div>', unsafe_allow_html=True)
            
        except Exception as e:
        
            st.error(f"An error occurred while reading the PDF: {e}")
else:
    st.info("Please upload a PDF file to begin.")
