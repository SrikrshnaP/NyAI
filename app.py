import streamlit as st
import webbrowser
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

/* Make the sidebar title larger */
.sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4 {
    font-size: 600px;  /* Adjust size as needed */
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

/* Exit button styling to make text white */
.stButton > button {
    color: white !important;  /* Ensure Exit button text is white */
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
            st.session_state['nature_of_case'] = st.selectbox("Nature of the Case", ["Select", "Insurance", "Divorce", "Land"])
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

    # Call Gemini API to get synthetic data for time
    if st.session_state['type_of_litigation'] == "Criminal" and st.session_state['court'] == "High Court" and st.session_state['nature_of_case'] == "Defamation":
        chat_session = model.start_chat(history=[])
        synthetic_time_query = "How long (in years) will it take for a Criminal Defamation Litigation in the Delhi High Court? Print only one number, no text."
        time_value = get_answer_from_model(chat_session, synthetic_time_query)
        time_value = float(time_value)  # Assuming the model returns a valid number

        st.write(f"Estimated Time (in years): {time_value}")
    else:
        # Fallback to slider if conditions are not met
        time_value = st.slider("Time (in years)", 0.0, 7.0, 2.5)

    print(time_value)

    # Call Gemini API to get synthetic data for expenditure
    if st.session_state['type_of_litigation'] == "Criminal" and st.session_state['court'] == "High Court" and st.session_state['nature_of_case'] == "Defamation":
        synthetic_expenditure_query = "How many lakhs (in rupees) will it take for a Criminal Defamation Litigation in the Delhi High Court? Print only one number between 1-10."
        expenditure_value = get_answer_from_model(chat_session, synthetic_expenditure_query)
        expenditure_value = float(expenditure_value)  # Assuming the model returns a valid number

        st.write(f"Estimated Expenditure (₹ in Lakhs): {expenditure_value}")
    else:
        # Fallback to slider if conditions are not met
        expenditure_value = st.slider("Expenditure (₹ in Lakhs)", 0.0, 10.0, 6.755)

    # Create two rows for "Similar Cases resolved by ADR" and "Related Judgements"

    # First Row: Similar Cases Resolved by ADR
    st.header("Similar Cases Resolved by ADR")
    adr_columns = st.columns(4)

    adr_cases = [
        {
            "title": "Mumbai Mediation Centre - Rajesh Kumar vs Daily Times",
            "case_id": "D7A9P3",
            "location": "Mumbai",
            "mediation_centre": "Mumbai Mediation Centre",
            "parties": "Rajesh Kumar vs Daily Times (News Media)",
            "sessions": 3,
            "duration": "45 days",
            "settlement": "₹5,00,000",
            "status": "Settled"
        },
        {
            "title": "Delhi High Court Mediation - Anjali Verma vs Kunal Bhardwaj",
            "case_id": "D4B8X1",
            "location": "Delhi",
            "mediation_centre": "Delhi High Court Mediation",
            "parties": "Anjali Verma vs Kunal Bhardwaj (Private Person)",
            "sessions": 5,
            "duration": "60 days",
            "settlement": "Apology and ₹2,00,000",
            "status": "Settled"
        },
        {
            "title": "Bangalore Mediation Centre - Aditi vs Sunil",
            "case_id": "D5C3K8",
            "location": "Bangalore",
            "mediation_centre": "Bangalore Mediation Centre",
            "parties": "Aditi vs Sunil (Private Person)",
            "sessions": 4,
            "duration": "30 days",
            "settlement": "₹3,00,000",
            "status": "Settled"
        },
        {
            "title": "Chennai Mediation Centre - Ravi vs Priya",
            "case_id": "D8F1A2",
            "location": "Chennai",
            "mediation_centre": "Chennai Mediation Centre",
            "parties": "Ravi vs Priya (Private Person)",
            "sessions": 2,
            "duration": "15 days",
            "settlement": "₹1,00,000",
            "status": "Settled"
        },
    ]

    for idx, column in enumerate(adr_columns):
        with column:
            with st.expander(adr_cases[idx]["title"]):
                st.write(f""" 
                **Case ID**: {adr_cases[idx]['case_id']}  
                **Location**: {adr_cases[idx]['location']}  
                **Mediation Centre**: {adr_cases[idx]['mediation_centre']}  
                **Parties Involved**: {adr_cases[idx]['parties']}  
                **Sessions**: {adr_cases[idx]['sessions']}  
                **Duration**: {adr_cases[idx]['duration']}  
                **Settlement**: {adr_cases[idx]['settlement']}  
                **Status**: {adr_cases[idx]['status']}
                """)

    # Second Row: Related Judgements
    st.header("Related Judgements")
    judgment_columns = st.columns(4)

    judgment_cases = [
        {
            "title": "How to Use eSCR",
            "link": "https://www.youtube.com/watch?v=2OwmXTJ6Wl0",
            "details": "You can learn how to use eSCR by watching this tutorial."
        },
        {
            "title": "Gautam Gambhir vs Punjab Kesari",
            "details": """**Judgment Date**: Adjourned  
                        **Details**: Gautam Gambhir filed a defamation suit against the newspaper Punjab Kesari for allegedly publishing defamatory content against him. The publication had allegedly made statements affecting Gambhir's reputation, leading to the legal action."""
        },
        {
            "title": "Subramanian Swamy vs Union of India",
            "details": """**Judgment Date**: May 13, 2016  
                        **Status**: The court upheld the constitutionality of criminal defamation under Sections 499 and 500 of the Indian Penal Code, stating it is not a violation of free speech."""
        },
        {
            "title": "R. Rajagopal vs State of Tamil Nadu",
            "details": """**Judgment Date**: October 7, 1994  
                        **Status**: The court ruled that the right to privacy cannot prevent the publication of true statements about a public official, especially if based on public records."""
        },
    ]

    for idx, column in enumerate(judgment_columns):
        with column:
            with st.expander(judgment_cases[idx]["title"], expanded=(idx==0)):
                if idx == 0:
                    st.markdown(f"<div style='background-color: brown; padding: 10px; border-radius: 5px;'><h5 style='color: white;'>{judgment_cases[idx]['title']}</h5></div>", unsafe_allow_html=True)
                    st.write(judgment_cases[idx]["details"])
                    st.markdown(f"<a href='{judgment_cases[idx]['link']}' style='background-color: white; color: brown; padding: 10px; border-radius: 5px; text-decoration: none;' target='_blank'>Watch Here</a>", unsafe_allow_html=True)
                else:
                    st.write(judgment_cases[idx]["details"])



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
    
    # First Row: Precedents
    st.header("Precedents")
    
    st.markdown("""
    <div style="background-color: saddlebrown; padding: 10px; border-radius: 5px; color: white;">
        <strong>With NyAI Assist</strong>
    </div>
    """, unsafe_allow_html=True)

    # Expander for Gautam Gambhir vs Punjab Kesari
    with st.expander("Gautam Gambhir vs Punjab Kesari", expanded=False):

        if st.button("Open Link"):
            js = "window.open('https://notebooklm.google.com/notebook/8663e50a-386e-4dcd-8bae-d2ba9c4cd3ad?pli=1', '_blank')"
            st.components.v1.html(f"<script>{js}</script>")

    # Light green box for ratio of the first case
    st.markdown("""
    <div style="background-color: tan; padding: 10px; border-radius: 5px;">
        <strong>Ratio: 4:1</strong>
    </div>
    """, unsafe_allow_html=True)

    # Expander for Kaushal Kishor vs State of Uttar Pradesh & Ors (first instance)
    with st.expander("Kaushal Kishor vs State of Uttar Pradesh & Ors", expanded=False):
        st.write("""
        **Judgment Date**: 3rd January, 2023  
        **Reference Answered**  
        Majority Judgement – Justice V Ramasubramanian for Justices A Nazeer, B R Gavai, A S Bopanna  
        Concurring Judgement – Justice B V Nagarathna  
        **Question Formulated**: 1. Whether the Court can impose restrictions on the right to freedom of speech and expression beyond the present restrictions provided under Article 19(2) of the Constitution?  
        **Court’s Opinion**: The Court held that the grounds lined up in Article 19(2) of the Constitution for restricting the right to free speech, under the guise of invoking other Fundamental Rights is taking a competing climb against each other, additional restrictions not found in Article 19(2) cannot be imposed on the exercise of right conferred by Article 19(1)(a) of the Constitution.
        """)

    # Light green box for ratio of the second case
    st.markdown("""
    <div style="background-color: tan; padding: 10px; border-radius: 5px;">
        <strong>Unanimous. Referred to Larger Bench</strong>
    </div>
    """, unsafe_allow_html=True)

    # Expander for Kaushal Kishor vs State of Uttar Pradesh & Ors (second instance)
    with st.expander("Kaushal Kishor vs State of Uttar Pradesh & Ors", expanded=False):
        
        
        st.write("""
        **Judgment Date**: 23rd November 2022  
        **Ratio**: Unanimous Verdict  
        **Judgment**: Justice V Ramasubramanian  
        Concurring Judgement – Justice B V Nagarathna (Concurring)  
        **Question Formulated**: Can a fundamental right under Article 19, i.e., the freedom of speech and expression, or Article 21, i.e., the right to life and personal liberty, be enforced against anyone other than the ‘State’ or its instrumentalities?  
        **Court’s Opinion**: “A fundamental right under Article 19/21 can be enforced even against persons other than the State or its instrumentalities.”
        """)

    # Second Row: Existing Functionality from the Original Second Column
    st.header("Courtroom Exchange")

    # PDF upload for Courtroom Exchange
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
