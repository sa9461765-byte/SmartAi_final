import streamlit as st
import google.generativeai as genai
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# ==========================================
# 1. إعدادات الذكاء الاصطناعي (API Key)
# ==========================================
API_KEY = "AIzaSyDso4OPFXij1guGTSX6gN2zwSaXDix-c1o"
genai.configure(api_key=API_KEY)

@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-1.5-flash")

model = load_model()

# ==========================================
# 2. وظائف المعالجة الاحترافية
# ==========================================
def fix_arabic(text):
    try:
        if not text: return ""
        return get_display(reshape(text))
    except:
        return text

def extract_audio_text(file):
    try:
        audio = AudioSegment.from_file(file)
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
        return r.recognize_google(audio_data, language="ar-SA")
    except Exception as e:
        return f"⚠️ خطأ في معالجة الصوت: {str(e)}"

def extract_content(file):
    try:
        if file.type.startswith("image/"):
            img = Image.open(file)
            return pytesseract.image_to_string(img, lang="ara+eng")
        elif file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                return "\n".join([p.extract_text() or "" for p in pdf.pages])
        elif file.type in ["audio/mpeg", "audio/wav", "audio/mp3"]:
            return extract_audio_text(file)
        else:
            return file.read().decode(errors="ignore")
    except Exception as e:
        return f"⚠️ تعذر قراءة {file.name}: {str(e)}"

# ==========================================
# 3. تصميم واجهة المستخدم VIP
# ==========================================
st.set_page_config(page_title="Royal AI Platform", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Cairo', sans-serif;
        text-align: right;
    }
    .stApp { background-color: #f8fafc; }
    .card {
        padding: 25px;
        background: white;
        border-radius: 20px;
        border-right: 10px solid #1e3a8a;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- التبويبات ---
tabs = st.tabs(["📑 التلخيص الذكي", "💬 الشات المطور", "📖 واحة القرآن"])

# 1. تبويب التلخيص
with tabs[0]:
    st.header("🎯 معالج الوسائط الشامل")
    files = st.file_uploader("ارفع (صور OCR، ملفات PDF، تسجيلات صوتية)", accept_multiple_files=True)
    if files and st.button("🚀 ابدأ التلخيص الملكي"):
        with st.spinner("⚡ جاري تحويل الملفات لنصوص وتلخيصها..."):
            full_text = ""
            for f in files:
                full_text += f"\n--- {f.name} ---\n" + extract_content(f)
            
            p = f"قم بتلخيص هذا المحتوى باحترافية، استخدم جداول ونقاط واضحة: \n{full_text}"
            res = model.generate_content(p)
            st.markdown(f'<div class="card">{res.text}</div>', unsafe_allow_html=True)

# 2. تبويب الشات
with tabs[1]:
    if "history" not in st.session_state: st.session_state.history = []
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if user_q := st.chat_input("اسأل أي شيء..."):
        st.session_state.history.append({"role": "user", "content": user_q})
        with st.chat_message("user"): st.markdown(user_q)
        with st.chat_message("assistant"):
            ans = model.generate_content(user_q).text
            st.markdown(ans)
            st.session_state.history.append({"role": "assistant", "content": ans})

# 3. تبويب القرآن
with tabs[2]:
    st.header("📖 التفسير الملم")
    q_verse = st.text_input("أدخل الآية أو اسم السورة:")
    if q_verse:
        with st.spinner("جاري استحضار التفاسير..."):
            res_q = model.generate_content(f"فسر الآتي بأسلوب رزين ملم بكافة التفاسير: {q_verse}").text
            st.markdown(f'<div class="card" style="border-right-color: #059669;">{res_q}</div>', unsafe_allow_html=True)
