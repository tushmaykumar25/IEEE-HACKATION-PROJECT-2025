import streamlit as st
import nltk
import pdfplumber
import os
import requests
from openai import OpenAI  

# Download NLTK data
nltk.download('punkt', quiet=True)

# --- Gemini API Key ---
GEMINI_API_KEY = "AIzaSyBc3OaQIHxfYtlEARfDi6ywuhYap9TX_nw"
client = OpenAI(api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

# --- Dyslexia-friendly font setup ---
FONT_URL = "https://github.com/antijingoist/opendyslexic/raw/master/OPEN%20DYSLEXIC/OpenDyslexic-Regular.otf"
FONT_FILE = "OpenDyslexic-Regular.otf"

if not os.path.exists(FONT_FILE):
    with st.spinner("Downloading dyslexia-friendly font..."):
        r = requests.get(FONT_URL)
        with open(FONT_FILE, "wb") as f:
            f.write(r.content)

# --- CSS Styling ---
st.markdown(f"""
<style>
@font-face {{
  font-family: 'OpenDyslexic';
  src: url('{FONT_FILE}') format('opentype');
}}
body {{
  background: #fbfbf7;
}}
.open-dys {{
  font-family: 'OpenDyslexic', Arial, sans-serif;
  font-size: 18px;
  line-height: 1.6;
}}
.highlight {{
  font-weight: bold;
  color: #000000;
}}
.stButton>button {{
  padding: 10px 16px;
  font-size: 16px;
  border-radius: 8px;
}}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🧠 ReadEase – AI Simplified Reader with Focus Mode")

# --- File Upload ---
uploaded = st.file_uploader("📄 Upload PDF (optional)", type=["pdf"])
if uploaded:
    with pdfplumber.open(uploaded) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages[:5]]
    original = "\n\n".join(pages)
    st.success("✅ PDF loaded successfully!")
else:
    original = ""

# --- Text Area ---
original = st.text_area("✏️ Paste or type text here:", value=original, height=200)

# --- AI Simplify Function ---
def simplify_text(text):
    system_msg = (
        "You are ReadEase, an assistant that rewrites text for dyslexic readers. "
        "Use short, simple sentences (under 12 words). "
        "Include a one-line summary labeled 'Summary:'."
    )
    try:
        resp = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=700
        )
        if resp and resp.choices and resp.choices[0].message:
            return resp.choices[0].message.content.strip()
        return "⚠️ No response from Gemini API."
    except Exception as e:
        return f"Error simplifying text: {e}"

# --- Simplify Button ---
simplified = ""
if st.button("✨ Simplify Text"):
    if not original.strip():
        st.warning("Please enter or upload text first.")
    else:
        with st.spinner("Simplifying text..."):
            simplified = simplify_text(original)

# --- Show Simplified Text ---
if simplified:
    st.markdown("### 🪶 Simplified Text:")
    st.markdown(f"<div class='open-dys'>{simplified}</div>", unsafe_allow_html=True)

    # --- Focus Reading Mode ---
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(simplified)

    if 'current_sentence' not in st.session_state:
        st.session_state['current_sentence'] = 0

    st.markdown("### 👁️ Focus Reading Mode:")
    highlighted_text = ""
    for i, sent in enumerate(sentences):
        if i == st.session_state['current_sentence']:
            highlighted_text += f"<div class='open-dys highlight'>{sent}</div><br>"
        else:
            highlighted_text += f"<div class='open-dys'>{sent}</div><br>"

    st.markdown(highlighted_text, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("⬅ Previous"):
        if st.session_state['current_sentence'] > 0:
            st.session_state['current_sentence'] -= 1
            st.experimental_rerun()
    if col2.button("Next ➡"):
        if st.session_state['current_sentence'] < len(sentences) - 1:
            st.session_state['current_sentence'] += 1
            st.experimental_rerun()

st.markdown("---")
st.caption("Made with ❤️ for IEEE 'Tech for All' Accessibility Challenge | Theme: AI for Humanity 🌍")
