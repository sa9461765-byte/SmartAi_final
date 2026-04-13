import streamlit as st
import google.generativeai as genai
import pdfplumber
from docx import Document
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors 
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# إعداد الـ API (المفتاح الجديد الشغال)
API_KEY = "AIzaSyDso4OPFXij1guGTSX6gN2zwSaXDix-c1o"
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

def fix_text(t):
    return get_display(reshape(t))

# واجهة المستخدم (التصميم الملكي)
st.set_page_config(page_title="المنصة الملكية AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #fdfdfd; }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 20px; }
    .quran { background: #fffcf0; border-right: 12px solid #059669; padding: 25px; border-radius: 15px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 التحكم")
    b_color = st.color_picker("لون الإطار", "#1e3a8a")
    st.success("الذكاء الخارق مفعل ✅")

t1, t2, t3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات المطور", "📖 واحة القرآن"])

# --- التلخيص ---
with t1:
    st.markdown('<div class="card"><h2>🎯 مركز التلخيص وتنسيق الملفات</h2></div>', unsafe_allow_html=True)
    up_files = st.file_uploader("ارفع (صور، PDF، Word)", accept_multiple_files=True)
    if up_files and st.button("🚀 ولّد الملخص الإمبراطوري"):
        with st.spinner("⚡ جاري استخراج العظمة..."):
            contents = ["لخص باحترافية، لغة عربية رصينة، جداول، أسئلة. قلد القالب لو وجد."]
            for f in up_files:
                if f.type.startswith('image/'): contents.append(Image.open(f))
                elif f.type == "application/pdf":
                    with pdfplumber.open(f) as pdf:
                        contents.append(" ".join([p.extract_text() for p in pdf.pages if p.extract_text()]))
                else: contents.append(f.read().decode(errors='ignore'))
            res = model.generate_content(contents).text
            st.markdown(f'<div class="card" style="border-right: 10px solid {b_color};">{res}</div>', unsafe_allow_html=True)

# --- الشات (الصور والملفات) ---
with t2:
    if "messages" not in st.session_state: st.session_state.messages = []
    chat_up = st.file_uploader("ارفع ملف/صورة للشات", accept_multiple_files=True, key="chat")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("تكلم معي.. أنا أفهم كل شيء"):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            payload = [p]
            if chat_up:
                for cf in chat_up:
                    if cf.type.startswith('image/'): payload.append(Image.open(cf))
                    else: payload.append(f"مرفق: {cf.name}")
            r = model.generate_content(payload).text
            st.markdown(r)
            st.session_state.messages.append({"role": "assistant", "content": r})

# --- القرآن ---
with t3:
    st.markdown('<div class="card"><h2>📖 التفسير الملم والرزين</h2></div>', unsafe_allow_html=True)
    q = st.text_input("أدخل الآية أو السورة:")
    if q:
        with st.spinner("جاري استحضار علوم القرآن..."):
            res = model.generate_content(f"فسر الآتي بأسلوب رزين ملم بكافة التفاسير: {q}").text
            st.markdown(f'<div class="quran">{res}</div>', unsafe_allow_html=True)
