import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import sys
from streamlit.web import cli as stcli

# --- APP SETUP & THEME ---
st.set_page_config(page_title="AI PDF Quiz App", page_icon="🟡", layout="centered")

# Black and Yellow Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    h1, h2, h3, p, span, label, div {
        color: #FFD700 !important; 
    }
    .stRadio label {
        color: #FFFFFF !important; 
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
    .explanation-box {
        background-color: #1A1A00;
        padding: 15px;
        border-left: 4px solid #FFD700;
        border-radius: 5px;
        margin-top: 10px;
        color: #FFFFFF !important;
    }
    .stTextInput>div>div>input {
        background-color: #1A1A00;
        color: #FFFFFF;
        border: 1px solid #FFD700;
    }
    .stFileUploader label {
        font-size: 1.2rem !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🟡 AI PDF Quiz App")
st.write("Upload your PDF document below. The AI will read it and generate a quiz in Sinhala!")

# --- API KEY INPUT ---
api_key = st.text_input("Enter your Gemini API Key here:", type="password")

# --- AI PDF PARSER ---
@st.cache_data
def parse_pdf_with_ai(file_bytes, api_key):
    try:
        # Extracting text from PDF
        reader = PyPDF2.PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        # Configuring Gemini AI
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # AI Prompt
        prompt = f"""
        You are a helpful assistant. Extract the multiple choice questions, options, correct answers (usually indicated by underlines or marks), and explanations from the following text.
        
        IMPORTANT: You MUST translate and write ALL output (questions, options, correct answer, and explanations) in the Sinhala Language (සිංහල අකුරෙන්).
        
        Return the result STRICTLY as a valid JSON array of objects. Do not include markdown blocks like ```json.
        Structure each object exactly like this:
        [
            {{
                "question": "Sinhala question text here",
                "options": ["Option A in Sinhala", "Option B in Sinhala", "Option C in Sinhala"],
                "answer": "Correct option text in Sinhala exactly as in the options array",
                "explanation": "Detailed explanation in Sinhala here"
            }}
        ]
        
        Text to analyze:
        {text}
        """
        
        response = model.generate_content(prompt)
        
        # Converting API response to JSON
        result_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(result_text)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- APP LOGIC ---
if api_key:
    # PDF Upload Feature
    st.subheader("📁 Upload your PDF Marking Scheme")
    uploaded_file = st.file_uploader("", type="pdf")

    if uploaded_file is not None:
        with st.spinner('AI is generating your Sinhala quiz... Please wait! ⏳'):
            questions = parse_pdf_with_ai(uploaded_file, api_key)
            
        if questions:
            st.write("---")
            user_answers = {}

            # Quiz Form
            with st.form(key='quiz_form'):
                for i, q in enumerate(questions):
                    st.subheader(f"Q{i+1}: {q.get('question', 'ප්‍රශ්නය')}")
                    options = q.get('options', [])
                    user_answers[i] = st.radio("Select your answer:", options, key=f"q_{i}", index=None)
                    st.write("")
                    
                submit_button = st.form_submit_button(label='Submit Responses')

            # --- SCORING & EXPLANATIONS ---
            if submit_button:
                score = 0
                for i, q in enumerate(questions):
                    if user_answers[i] == q.get('answer'):
                        score += 1
                        
                st.header(f"🏆 Your Score: {score} / {len(questions)}")
                st.write("---")
                
                st.subheader("📝 Answers & Explanations")
                for i, q in enumerate(questions):
                    st.write(f"**Q{i+1}: {q.get('question', '')}**")
                    
                    correct_answer = q.get('answer', '')
                    if user_answers[i] == correct_answer:
                        st.success(f"Your Answer: {user_answers[i]} (Correct ✅)")
                    else:
                        st.error(f"Your Answer: {str(user_answers[i])} (Incorrect ❌)")
                        st.info(f"Correct Answer: {correct_answer}")
                        
                    explanation = q.get('explanation', 'No explanation provided.')
                    st.markdown(f'<div class="explanation-box"><b>Explanation:</b><br>{explanation}</div>', unsafe_allow_html=True)
                    st.write("---")
else:
    st.warning("Please enter your Gemini API Key in the box above to use the app.")


