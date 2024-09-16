import streamlit as st
import webbrowser
from openai import OpenAI
import PyPDF2
from io import BytesIO
import google.generativeai as genai
from docx import Document
from gtts import gTTS
from PIL import Image

# Function to convert text to speech using gTTS
def text_to_speech_gtts(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)  # Move cursor to the beginning of BytesIO
    return audio_fp

# Def for Chat
# Configure the API key
genai.configure(api_key="AIzaSyBqm_dXuNWqT_DmZtuLKUtRREG2xwX7Jjg")  # Replace with your actual API key

# Define the generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192
}

# Safety settings to allow risky output
safe = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Create the GenerativeModel instance with adjusted safety settings
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safe
)

def get_answer_from_model(chat_session, question):
    chat_session.history.append({
        "role": "user",
        "parts": [question]
    })
    response = chat_session.send_message(question)
    return response.text

# Function to translate the answer to the desired language
def translate_answer(answer, target_language):
    translation_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"Translate to {target_language}: {answer}",
                ],
            }
        ]
    )
    response = translation_session.send_message(answer)
    return response.text

def initialize_chat_with_document_text(extracted_text):
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"Document content for context: {extracted_text}",
                ],
            }
        ]
    )
    return chat_session


# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from a Word document
def extract_text_from_word(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Set page config with customized colors
st.set_page_config(page_title="NyAI", page_icon="⚖️", layout="wide")

# Custom CSS for styling
custom_css = """
<style>
/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #fff2ef;
    color: black;
}
[data-testid="stSidebar"] * {
    color: black !important;
}
.sidebar .sidebar-content .element-container {
    background-color: #6f5d4f;
    border-radius: 8px;
    padding: 5px;
    margin: 5px 0;
}
.sidebar .sidebar-content .element-container:hover {
    background-color: #564a3d;
}

/* Screen background and font colors */
body {
    color: black;
    background-color: white;
}

/* Box styling for "Related Judgements" */
.box {
    border: 1px solid #6f5d4f;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #fff2ef;
}

/* Submit button styling */
.stButton > button {
    background-color: #6f5d4f;
    color: white;
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
}
.stButton > button:hover {
    background-color: #564a3d;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Sidebar navigation with styled buttons
st.sidebar.title("NyAI ✨")
options = ["Search", "Compare", "Find", "Ask"]
selected_option = st.sidebar.radio("", options, format_func=lambda x: f"  {x}")

# Adding the "Exit" button to the sidebar
if st.sidebar.button("Exit"):
    st.stop()  # Stops the script if the user clicks "Exit"

# Initialize session state variables if they don't exist
if 'type_of_litigation' not in st.session_state:
    st.session_state['type_of_litigation'] = ''
if 'court' not in st.session_state:
    st.session_state['court'] = ''
if 'jurisdiction' not in st.session_state:
    st.session_state['jurisdiction'] = ''
if 'nature_of_case' not in st.session_state:
    st.session_state['nature_of_case'] = ''
if 'respondents' not in st.session_state:
    st.session_state['respondents'] = ''
if 'digitize_option' not in st.session_state:
    st.session_state['digitize_option'] = False

# Main interface for "Search"
if selected_option == "Search":
    st.title("HI JYOTI, HOW CAN I ASSIST YOU?")
    
    # Search bar with an emoji icon and search on Enter press
    search_query = st.text_input("Search 🔍", placeholder="Enter your search here...")
    if search_query:
        query = f"in:site indiankanoon.org {search_query}"
        webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")

    st.markdown("**OR**")
    
    # Create two columns for form fields
    col1, col2 = st.columns(2)
    
    with col1:
        # Dropdown for Type of Litigation
        st.session_state['type_of_litigation'] = st.selectbox("Type of Litigation", ["Select", "Civil", "Criminal"])
        
        # Dropdown for Court
        st.session_state['court'] = st.selectbox("Court", ["Select", "Supreme Court", "High Court", "District Court", "Trial Court"])
        
        # Textbox for Jurisdiction, disabled if Supreme Court is selected
        jurisdiction_disabled = st.session_state['court'] == "Supreme Court"
        st.session_state['jurisdiction'] = st.text_input("Intended Jurisdiction", disabled=jurisdiction_disabled)
        
    with col2:
        # Conditional dropdown for Nature of the Case
        if st.session_state['type_of_litigation'] == "Civil":
            st.session_state['nature_of_case'] = st.selectbox("Nature of the Case", ["Select", "Insurance", "Divorce", "Family Dispute", "Inheritance", "Wages", "Land"])
        elif st.session_state['type_of_litigation'] == "Criminal":
            st.session_state['nature_of_case'] = st.selectbox("Nature of the Case", ["Select", "Defamation"])
        else:
            st.session_state['nature_of_case'] = st.selectbox("Nature of the Case", ["Select"])

        # Show the "DIGITIZE" option if "Land" is selected
        if st.session_state['nature_of_case'] == "Land":
            st.session_state['digitize_option'] = True
        else:
            st.session_state['digitize_option'] = False
        
        # Conditional dropdown for Respondents based on Nature of the Case
        if st.session_state['nature_of_case'] == "Insurance":
            st.session_state['respondents'] = st.selectbox("Respondents", ["Select", "Max Insurance", "Bajaj Insurance", "New India Insurance", "Other"])
        elif st.session_state['nature_of_case'] == "Defamation":
            st.session_state['respondents'] = st.selectbox("Respondents", ["Select", "Competitor", "News Media", "Private Person"])
        else:
            st.session_state['respondents'] = st.selectbox("Respondents", ["Select"])
        
    # Submit button positioned centrally and styled
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Submit"):
            st.success("Search/Details Submitted!")
            st.write(f"Type of Litigation: {st.session_state['type_of_litigation']}")
            st.write(f"Nature of the Case: {st.session_state['nature_of_case']}")
            st.write(f"Court: {st.session_state['court']}")
            st.write(f"Intended Jurisdiction: {st.session_state['jurisdiction']}")
            st.write(f"Respondents: {st.session_state['respondents']}")

if 'show_digitize' not in st.session_state:
    st.session_state['show_digitize'] = True

# Sidebar checkbox to show or hide the "DIGITIZE" section
show_digitize = st.sidebar.checkbox("NyAI Translate", value=st.session_state['show_digitize'])
st.session_state['show_digitize'] = show_digitize

# Show the "DIGITIZE" option if "Land" is selected and checkbox is checked
if st.session_state['digitize_option'] and st.session_state['show_digitize']:
    st.sidebar.header("DIGITIZE")
    
    uploaded_image = st.sidebar.file_uploader("Upload an image (PNG/JPEG/JPG)", type=["png", "jpeg", "jpg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.markdown("""
            **Column Headers:**

            - Serial Number (کالم نمبر)
            - Name and Details (نام مالک و احوال)
            - Owner's Name and Relationship (نام مالک کے نام اور رشتہ)
            - Property and Condition (حالت و موجودہ حال)

            **Row Details:**

            - Serial No: 1 (نمبر: 1)
            - Owner's Name: [Name not clearly visible]
            - Relationship: First Wife (اول زوجہ)
            - Details: Land of the first wife, measuring 8 bighas and 2 biswas, currently in the possession of [Name not clearly visible], property at [Location not clearly visible]

            **Stamp/Signature:**

            - True Copy Attested
            - Nafees Tersildar
            - General Record Room, Jammu
            """)


# Main "Compare" Section
if selected_option == "Compare":
    st.title("Compare")

    # Sliders for Time and Expenditure
    time_value = st.slider("Time (in years)", 0.0, 7.0, 2.61)
    expenditure_value = st.slider("Expenditure (₹ in Lakhs)", 0.0, 10.0, 6.755)

    # Columns for "Similar Cases resolved by ADR" and "Related Judgements"
    col1, col2 = st.columns(2)

    with col1:
        st.header("Similar Cases Resolved by ADR")
        
        # First button for a similar case
        if st.button("Mumbai Mediation Centre - Rajesh Kumar - Daily Times - News Media - Settled"):
            st.write("""
            **Case ID**: D7A9P3  
            **Location**: Mumbai  
            **Mediation Centre**: Mumbai Mediation Centre  
            **Parties Involved**: Rajesh Kumar vs Daily Times (News Media)  
            **Sessions**: 3  
            **Duration**: 45 days  
            **Settlement**: ₹5,00,000  
            **Status**: Settled
            """)

        # Second button for another similar case
        if st.button("Delhi High Court Mediation - Anjali Verma - Kunal Bhardwaj - Private Person - Settled"):
            st.write("""
            **Case ID**: D4B8X1  
            **Location**: Delhi  
            **Mediation Centre**: Delhi High Court Mediation  
            **Parties Involved**: Anjali Verma vs Kunal Bhardwaj (Private Person)  
            **Sessions**: 5  
            **Duration**: 60 days  
            **Settlement**: Apology and ₹2,00,000  
            **Status**: Settled
            """)

    with col2:
        st.header("Related Judgements")
        # Boxed text for "Related Judgements"

        st.write("Click on Find to Chat with the below case(s)")


        if st.button("Gautam Gambhir vs Punjab Kesari & Ors - Judgement: 17 May, 2023 - Status: Adjourned, Pending"):
            st.write("""
        
            """)

        # # Button to navigate to the "Find" section
        # if st.button("Chat with Case"):
        #     st.session_state.selected_option = "Find"

language_codes = {
    'english': 'en',
    'hindi': 'hi',
    'kannada': 'kn',
    'tamil': 'ta',
    'malayalam': 'ml',
    'telugu': 'te',
    'gujarati': 'gu',
    'bangla': 'bn',
    'assamese': 'as',
    'khasi': 'kha',  # Note: Khasi is not supported by gTTS
    'bhojpuri': 'bho',  # Note: Bhojpuri is not supported by gTTS
    'tulu': 'tcy'  # Note: Tulu is not supported by gTTS
}


if selected_option == "Find":
    st.title("Find Cases")
    col1, col2 = st.columns(2)
   
    with col1:
        st.header("Judgement Assist")
        
        # PDF upload
        uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
        if uploaded_file is not None:
            st.success("PDF uploaded successfully!")

        # Search bar
        search_query = st.text_input("Search 🔍", placeholder="Enter your search here...")
        if search_query:
            query = f"https://notebooklm.google.com/notebook/8663e50a-386e-4dcd-8bae-d2ba9c4cd3ad?pli=1"
            webbrowser.open_new_tab(query)
    
    with col2:
        st.header("Courtroom Exchange")

        uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                document_text = extract_text_from_pdf(BytesIO(uploaded_file.read()))
            elif uploaded_file.name.endswith('.docx'):
                document_text = extract_text_from_word(BytesIO(uploaded_file.read()))
            else:
                st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                document_text = ""

            if document_text:
                st.success("Document uploaded and text extracted successfully. You can now ask questions.")
                chat_session = initialize_chat_with_document_text(document_text)

                user_input = st.text_input("Enter your question:", "")
                if user_input:
                    answer = get_answer_from_model(chat_session, "(Don't make any text bold):" + user_input)
                    
                    target_language = st.selectbox(
                        "Translate answer to:",
                        options=['English', 'Hindi', 'Kannada', 'Tamil', 'Malayalam', 'Telugu', 'Gujarati', 'Bangla', 'Assamese', 'Khasi', 'Bhojpuri', 'Tulu']
                    )
                    
                    if target_language != 'english':  # Assuming 'english' is the default
                        translated_answer = translate_answer(answer, target_language)
                        st.write(f"Response in {target_language}: {translated_answer}")
                        if st.button("Read Response Aloud"):
                            lang_code = language_codes.get(target_language, 'en')  # Default to 'en' if language not found
                            audio_fp = text_to_speech_gtts(translated_answer, lang=lang_code)
                            st.audio(audio_fp, format='audio/mp3')
                    else:
                        st.write(f"Response: {answer}")
                        if st.button("Read Response Aloud"):
                            audio_fp = text_to_speech_gtts(answer)
                            st.audio(audio_fp, format='audio/mp3')
#### Main "Ask" Section

# Initialize chat session
def initialize_chat():
    chat_session = model.start_chat(history=[])
    return chat_session 

if selected_option == "Ask":
    st.title("Ask NyAI")
    
    if 'chat_session' not in st.session_state:
        st.session_state['chat_session'] = initialize_chat()

    col1, col2, col3 = st.columns(3)
    if col1.button("Draft email to registry for Listing", key="prompt_1"):
        st.session_state['user_input'] = "Draft email to registry for listing the case"
    
    if col2.button("Vakalatnama (Power of Attorney)", key="prompt_2"):
        st.session_state['user_input'] = "Vakalatnama"

    if col3.button("Summons to Defendant(s)", key="prompt_3"):
        st.session_state['user_input'] = "Summons to Defendant(s)"

    user_input = st.text_input("Type your question:", value=st.session_state.get('user_input', ''))
    user_input = "Opening Message - How can I help you? (Don't print: If the question is about animals/maths, reply - I am not aware. You must answer all other questions assuming a qualified lawyer is asking you (DONT MAKE TEXT BOLD))"+user_input
     
    if user_input:
        answer = get_answer_from_model(st.session_state['chat_session'], user_input)
        st.write(f"NyAI: {answer}")
        if st.button("Read Response Aloud"):
            audio_fp = text_to_speech_gtts(answer)
            st.audio(audio_fp, format='audio/mp3')

st.markdown("<h6 style='text-align: center;'>NyAI can make mistakes. Click here to know more.</h6>", unsafe_allow_html=True)
