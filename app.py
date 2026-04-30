import streamlit as st
import numpy as np
import pickle
import os
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CardioAI — Heart Risk Analyzer",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Cormorant+Garamond:wght@500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
[data-testid="stSidebarNav"]{display:none!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stHeader"]{display:none!important}
html,body,.stApp{background:#030C1A!important;color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important}
.stApp::before{content:'';position:fixed;width:700px;height:700px;top:-200px;left:-200px;background:radial-gradient(ellipse,rgba(0,98,204,.15) 0%,transparent 70%);border-radius:50%;z-index:0;animation:drift1 18s ease-in-out infinite;pointer-events:none}
.stApp::after{content:'';position:fixed;width:500px;height:500px;bottom:-100px;right:-100px;background:radial-gradient(ellipse,rgba(0,194,255,.08) 0%,transparent 70%);border-radius:50%;z-index:0;animation:drift2 22s ease-in-out infinite;pointer-events:none}
@keyframes drift1{0%,100%{transform:translate(0,0)}50%{transform:translate(80px,60px)}}
@keyframes drift2{0%,100%{transform:translate(0,0)}50%{transform:translate(-60px,40px)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.block-container{padding-top:0!important;padding-bottom:3rem!important;max-width:1280px!important;position:relative;z-index:1}
section[data-testid="stSidebar"]{background:rgba(6,20,40,.97)!important;border-right:1px solid rgba(255,255,255,.08)!important;backdrop-filter:blur(24px)}
section[data-testid="stSidebar"]>div{padding:0!important}
section[data-testid="stSidebar"] .stButton>button{width:100%!important;background:transparent!important;border:1px solid transparent!important;border-radius:10px!important;color:#7FA8C8!important;font-family:'DM Sans',sans-serif!important;font-size:13.5px!important;font-weight:400!important;text-align:left!important;padding:10px 16px!important;margin-bottom:4px!important;transition:all .2s!important}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(0,194,255,.12)!important;border-color:rgba(0,194,255,.25)!important;color:#00C2FF!important;transform:translateX(4px)!important}
h1,h2,h3,h4,p,label,.stMarkdown{color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important}
.stSlider>div>div>div{background:#00C2FF!important}
.stSlider>label{color:#7FA8C8!important;font-size:13px!important}
.stNumberInput input{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:8px!important;color:#E2EFF9!important;font-family:'JetBrains Mono',monospace!important;font-size:14px!important}
.stNumberInput input:focus{border-color:rgba(0,194,255,.5)!important;box-shadow:0 0 0 3px rgba(0,194,255,.08)!important}
.stNumberInput label,.stSelectbox label{color:#7FA8C8!important;font-size:13px!important}
.stSelectbox>div>div{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:8px!important;color:#E2EFF9!important}
div.stButton>button{background:linear-gradient(135deg,#0087C8,#00C2FF)!important;border:none!important;border-radius:10px!important;color:white!important;font-family:'DM Sans',sans-serif!important;font-size:15px!important;font-weight:500!important;padding:12px 36px!important;box-shadow:0 4px 24px rgba(0,194,255,.3)!important;transition:all .25s!important}
div.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 36px rgba(0,194,255,.45)!important}
[data-testid="stMetric"]{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:12px!important;padding:16px 20px!important}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:28px!important}
[data-testid="stMetricLabel"]{color:#4A6A88!important;font-size:11px!important;text-transform:uppercase!important;letter-spacing:.08em!important}
div[data-testid="stAlert"]{border-radius:10px!important;border-left-width:3px!important}
.stCaption,small{color:#4A6A88!important;font-size:12px!important}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION
# ─────────────────────────────────────────────
if "logged_in"      not in st.session_state: st.session_state.logged_in      = False
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = False

if not st.session_state.logged_in:
    st.switch_page("pages/login.py")

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root",
        password="Kishlay@0610", database="heart_app"
    )

conn   = get_db()
cursor = conn.cursor()

# ─────────────────────────────────────────────
#  MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    search_dirs = [
        BASE_DIR,
        os.getcwd(),
        os.path.join(BASE_DIR, "models"),
    ]

    model_path  = None
    scaler_path = None

    for d in search_dirs:
        mp = os.path.join(d, "heart_disease.pkl")
        sp = os.path.join(d, "scalar.pkl")
        if os.path.exists(mp) and os.path.exists(sp):
            model_path  = mp
            scaler_path = sp
            break

    if model_path is None or scaler_path is None:
        st.error(
            "❌ **Model files not found!**\n\n"
            "Please copy `heart_disease.pkl` and `scalar.pkl` into the same "
            "folder as `app.py` and restart the app.",
            icon="🚨"
        )
        st.stop()

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    return model, scaler

model, scaler = load_model()

# ─────────────────────────────────────────────
#  SMTP CONFIG
# ─────────────────────────────────────────────
SMTP_EMAIL    = "tactickeet@gmail.com"
SMTP_PASSWORD = "tvrqisveumxavgyg"

# ─────────────────────────────────────────────
#  EMAIL REPORT
# ─────────────────────────────────────────────
def send_risk_email(to_email, name, risk, risk_label,
                    age, sex_label, trestbps, chol, thalach, fbs, exang, oldpeak):

    if risk > 70:
        color, emoji = "#FF3B5C", "🔴"
        advice = "Your risk level is HIGH. Please consult a cardiologist at the earliest."
    elif risk > 40:
        color, emoji = "#FFB830", "🟡"
        advice = "Your risk level is MODERATE. Focus on lifestyle changes and monitor regularly."
    else:
        color, emoji = "#00C47A", "🟢"
        advice = "Your risk level is LOW. Keep maintaining your healthy habits!"

    html = f"""
    <div style="font-family:Arial,sans-serif;background:#030C1A;padding:40px 0;">
      <div style="max-width:560px;margin:0 auto;background:#0B1E38;
                  border-radius:20px;overflow:hidden;border:1px solid rgba(255,255,255,.08);">

        <div style="padding:32px 36px;border-bottom:1px solid rgba(255,255,255,.06);text-align:center;
                    background:linear-gradient(135deg,#061428,#0B1E38);">
          <div style="font-size:28px;margin-bottom:6px;">🫀</div>
          <h1 style="font-size:22px;font-weight:600;color:#E2EFF9;margin:0;">CardioAI</h1>
          <p style="font-size:12px;color:#4A6A88;margin:6px 0 0;">Your Heart Risk Analysis Report</p>
        </div>

        <div style="padding:32px 36px;">
          <p style="font-size:15px;color:#E2EFF9;margin:0 0 24px;">
            Hi <strong>{name}</strong>,<br><br>
            Your cardiovascular risk analysis is complete. Here are your results:
          </p>

          <div style="background:#061428;border:1px solid {color}40;border-radius:16px;
                      padding:28px;text-align:center;margin-bottom:24px;">
            <p style="font-size:11px;color:#4A6A88;text-transform:uppercase;
                      letter-spacing:.12em;margin:0 0 10px;">Overall Risk Score</p>
            <div style="font-size:52px;font-weight:700;color:{color};
                        font-family:'Courier New',monospace;line-height:1;">{risk}%</div>
            <div style="display:inline-block;margin-top:12px;padding:6px 20px;
                        border-radius:999px;background:{color}20;border:1px solid {color}40;
                        font-size:14px;font-weight:600;color:{color};">
              {emoji} {risk_label}
            </div>
          </div>

          <div style="background:#061428;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
            <p style="font-size:13px;font-weight:600;color:#E2EFF9;margin:0 0 10px;">
              Your Biomarkers
            </p>
            <table style="width:100%;border-collapse:collapse;font-size:13px;color:#7FA8C8;">
              <tr><td style="padding:6px 0;">Age</td>
                  <td style="text-align:right;color:#E2EFF9;font-family:'Courier New',monospace;">{age} yrs</td></tr>
              <tr><td style="padding:6px 0;">Sex</td>
                  <td style="text-align:right;color:#E2EFF9;">{sex_label}</td></tr>
              <tr><td style="padding:6px 0;">Blood Pressure</td>
                  <td style="text-align:right;color:#E2EFF9;font-family:'Courier New',monospace;">{trestbps} mmHg</td></tr>
              <tr><td style="padding:6px 0;">Cholesterol</td>
                  <td style="text-align:right;color:#E2EFF9;font-family:'Courier New',monospace;">{chol} mg/dL</td></tr>
              <tr><td style="padding:6px 0;">Max Heart Rate</td>
                  <td style="text-align:right;color:#E2EFF9;font-family:'Courier New',monospace;">{thalach} bpm</td></tr>
              <tr><td style="padding:6px 0;">Fasting Blood Sugar &gt;120</td>
                  <td style="text-align:right;color:#E2EFF9;">{'Yes' if fbs else 'No'}</td></tr>
              <tr><td style="padding:6px 0;">Exercise Angina</td>
                  <td style="text-align:right;color:#E2EFF9;">{'Yes' if exang else 'No'}</td></tr>
              <tr><td style="padding:6px 0;">ST Depression</td>
                  <td style="text-align:right;color:#E2EFF9;font-family:'Courier New',monospace;">{oldpeak:.1f} mm</td></tr>
            </table>
          </div>

          <div style="background:{color}08;border:1px solid {color}20;
                      border-radius:12px;padding:16px 20px;margin-bottom:20px;">
            <p style="font-size:13px;color:#E2EFF9;margin:0 0 8px;font-weight:600;">
              AI Advice
            </p>
            <p style="font-size:13px;color:#7FA8C8;margin:0;line-height:1.7;">{advice}</p>
          </div>

          <div style="background:#061428;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
            <p style="font-size:13px;font-weight:600;color:#E2EFF9;margin:0 0 10px;">
              Key Recommendations
            </p>
            <ul style="margin:0;padding-left:18px;color:#7FA8C8;font-size:13px;line-height:2;">
              <li>Maintain a heart-healthy Mediterranean diet</li>
              <li>Exercise at least 150 min/week (moderate intensity)</li>
              <li>Monitor blood pressure and cholesterol regularly</li>
              <li>Manage stress through mindfulness or yoga</li>
              <li>Avoid smoking and limit alcohol consumption</li>
            </ul>
          </div>

          <div style="background:rgba(255,184,48,.06);border:1px solid rgba(255,184,48,.15);
                      border-radius:10px;padding:12px 16px;">
            <p style="font-size:11px;color:#7FA8C8;margin:0;line-height:1.7;">
              ⚠ <strong style="color:#FFB830;">Medical Disclaimer:</strong>
              This report is for educational purposes only and does not constitute
              medical advice or diagnosis. Always consult a qualified healthcare professional.
            </p>
          </div>
        </div>

        <div style="padding:16px 36px;border-top:1px solid rgba(255,255,255,.06);text-align:center;">
          <p style="font-size:11px;color:#4A6A88;margin:0;">
            CardioAI · Built by Kishlay · Not a substitute for medical advice
          </p>
        </div>
      </div>
    </div>
    """

    msg            = MIMEMultipart("alternative")
    msg["Subject"] = f"🫀 CardioAI — Your Heart Risk Report: {risk}% ({risk_label})"
    msg["From"]    = SMTP_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    server.quit()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    st.markdown(
        "<div style='padding:28px 20px 20px;"
        "border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:16px'>"
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>"
        "<div style='width:32px;height:32px;"
        "background:linear-gradient(135deg,#FF3B5C,#FF7B93);"
        "border-radius:8px;display:flex;align-items:center;justify-content:center'>"
        "<svg width='16' height='14' viewBox='0 0 24 22' fill='none'>"
        "<path d='M12 21.593c-.5-.377-10-7.9-10-13.093a6 6 0 0 1 10-4.472"
        "A6 6 0 0 1 22 8.5c0 5.193-9.5 12.716-10 13.093z' fill='white'/>"
        "</svg></div>"
        "<span style='font-family:\"Cormorant Garamond\",serif;"
        "font-size:20px;font-weight:600;color:#E2EFF9'>CardioAI</span>"
        "</div>"
        "<p style='font-size:11px;color:#4A6A88;margin:0;padding-left:42px'>"
        "AI Health Intelligence System</p>"
        "</div>",
        unsafe_allow_html=True
    )

    if st.button("🏠  Dashboard"):
        st.switch_page("app.py")

    st.markdown(
        "<div style='padding:0 12px;margin-top:16px;margin-bottom:8px'>"
        "<p style='font-size:10px;color:#4A6A88;font-weight:500;"
        "letter-spacing:.12em;text-transform:uppercase;margin:0;padding-left:4px'>"
        "Account</p></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<style>section[data-testid='stSidebar'] .logout-btn>button,"
        "section[data-testid='stSidebar'] div:nth-child(6) .stButton>button"
        "{color:#FF3B5C!important;border-color:rgba(255,59,92,.25)!important;"
        "background:rgba(255,59,92,.06)!important}"
        "section[data-testid='stSidebar'] div:nth-child(6) .stButton>button:hover"
        "{background:rgba(255,59,92,.14)!important;color:#FF3B5C!important;"
        "border-color:rgba(255,59,92,.45)!important}</style>",
        unsafe_allow_html=True
    )
    if st.button("🚪  Logout"):
        st.session_state.logged_in = False
        st.switch_page("pages/login.py")

    st.markdown(
        "<style>section[data-testid='stSidebar'] div:nth-child(7) .stButton>button"
        "{color:#FF3B5C!important;border:1px solid rgba(255,59,92,.3)!important;"
        "background:rgba(255,59,92,.08)!important}"
        "section[data-testid='stSidebar'] div:nth-child(7) .stButton>button:hover"
        "{background:rgba(255,59,92,.18)!important;"
        "border-color:rgba(255,59,92,.5)!important}</style>",
        unsafe_allow_html=True
    )
    if st.button("🗑️  Delete Account"):
        st.session_state.confirm_delete = True

    if st.session_state.confirm_delete:
        st.markdown(
            "<div style='margin:10px 0;padding:14px 16px;border-radius:12px;"
            "background:rgba(255,59,92,.08);border:1px solid rgba(255,59,92,.25)'>"
            "<p style='font-size:12px;color:#FF3B5C;font-weight:500;margin:0 0 4px'>"
            "⚠ Confirm Delete</p>"
            "<p style='font-size:11px;color:#7FA8C8;margin:0;line-height:1.6'>"
            "This will permanently remove your account and all saved predictions."
            "</p></div>",
            unsafe_allow_html=True
        )
        dc1, dc2 = st.columns(2, gap="small")
        with dc1:
            if st.button("Yes, Delete"):
                try:
                    uid = st.session_state.user_id
                    cursor.execute("DELETE FROM predictions WHERE user_id=%s", (uid,))
                    cursor.execute("DELETE FROM users WHERE id=%s", (uid,))
                    conn.commit()
                    st.session_state.logged_in      = False
                    st.session_state.confirm_delete = False
                    st.success("Account deleted.")
                    import time; time.sleep(1)
                    st.switch_page("pages/login.py")
                except Exception as e:
                    st.error(f"Error: {e}")
        with dc2:
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

    st.markdown(
        "<div style='padding:20px 20px 0;"
        "border-top:1px solid rgba(255,255,255,.06);margin-top:24px'>"
        "<div style='display:flex;align-items:center;gap:6px;margin-bottom:4px'>"
        "<div style='width:6px;height:6px;border-radius:50%;"
        "background:#00E09A;animation:pulse 2s infinite'></div>"
        "<span style='font-size:11px;color:#4A6A88'>Model Active</span>"
        "</div>"
        "<p style='font-size:10px;color:#4A6A88;margin:0'>CardioAI v2.4 · 18 biomarkers</p>"
        "</div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────
st.markdown("""
<style>
.header-btn-row [data-testid="column"]:nth-child(3) .stButton>button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 8px !important;
    color: #7FA8C8 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    box-shadow: none !important;
    width: 100% !important;
}
.header-btn-row [data-testid="column"]:nth-child(3) .stButton>button:hover {
    border-color: rgba(255,59,92,.4) !important;
    color: #FF3B5C !important;
    background: rgba(255,59,92,.07) !important;
    transform: none !important;
    box-shadow: none !important;
}
.header-btn-row [data-testid="column"]:nth-child(2) .stButton>button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 8px !important;
    color: #7FA8C8 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    box-shadow: none !important;
    width: 100% !important;
}
.header-btn-row [data-testid="column"]:nth-child(2) .stButton>button:hover {
    border-color: rgba(255,59,92,.4) !important;
    color: #FF3B5C !important;
    background: rgba(255,59,92,.07) !important;
    transform: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-btn-row'>", unsafe_allow_html=True)
hdr_left, hdr_spacer, hdr_b1, hdr_b2 = st.columns([4, 2, 1, 1])

with hdr_left:
    st.markdown(
        "<div style='padding:32px 0 8px'>"
        "<h1 style='font-family:\"Cormorant Garamond\",serif;"
        "font-size:clamp(32px,4vw,50px);font-weight:600;line-height:1.1;"
        "color:#E2EFF9;margin:0 0 10px'>"
        "Heart Risk <span style='background:linear-gradient(135deg,#00C2FF,#00E09A);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text'>Analyzer</span>"
        "</h1>"
        "<p style='font-size:14px;color:#7FA8C8;font-weight:300;margin:0;"
        "max-width:520px;line-height:1.6'>"
        "Complete your health profile across three sections. "
        "Our AI model processes 18 biomarkers to generate your personalized cardiovascular risk score."
        "</p></div>",
        unsafe_allow_html=True
    )

with hdr_b1:
    st.markdown("<div style='padding-top:36px'>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.switch_page("pages/login.py")
    st.markdown("</div>", unsafe_allow_html=True)

with hdr_b2:
    st.markdown("<div style='padding-top:36px'>", unsafe_allow_html=True)
    if st.button("🗑️ Delete Account"):
        st.session_state.confirm_delete = True
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.confirm_delete:
    st.markdown(
        "<div style='background:rgba(255,59,92,.07);border:1px solid rgba(255,59,92,.25);"
        "border-radius:14px;padding:18px 24px;margin-bottom:20px;"
        "display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px'>"
        "<div>"
        "<p style='font-size:14px;font-weight:500;color:#FF3B5C;margin:0 0 4px'>⚠ Delete Account?</p>"
        "<p style='font-size:12px;color:#7FA8C8;margin:0'>"
        "This will permanently remove your account and all saved predictions.</p>"
        "</div></div>",
        unsafe_allow_html=True
    )
    conf1, conf2, conf_rest = st.columns([1, 1, 6])
    with conf1:
        if st.button("✅ Yes, Delete"):
            try:
                uid = st.session_state.user_id
                cursor.execute("DELETE FROM predictions WHERE user_id=%s", (uid,))
                cursor.execute("DELETE FROM users WHERE id=%s", (uid,))
                conn.commit()
                st.session_state.logged_in      = False
                st.session_state.confirm_delete = False
                st.success("Account deleted.")
                import time; time.sleep(1)
                st.switch_page("pages/login.py")
            except Exception as e:
                st.error(f"Error: {e}")
    with conf2:
        if st.button("❌ Cancel"):
            st.session_state.confirm_delete = False
            st.rerun()

st.markdown(
    "<div style='height:1px;background:rgba(255,255,255,.06);margin-bottom:32px'></div>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def section_header(icon, title, subtitle, bg="rgba(0,194,255,.10)"):
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:12px;margin-bottom:24px;"
        f"padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.06)'>"
        f"<div style='width:40px;height:40px;border-radius:10px;background:{bg};"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:18px;flex-shrink:0'>{icon}</div>"
        f"<div>"
        f"<div style='font-size:16px;font-weight:500;color:#E2EFF9'>{title}</div>"
        f"<div style='font-size:12px;color:#4A6A88;margin-top:2px'>{subtitle}</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

def field_label(text):
    st.markdown(
        f"<p style='font-size:12px;font-weight:500;color:#7FA8C8;"
        f"letter-spacing:.05em;text-transform:uppercase;margin:0 0 4px'>{text}</p>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
#  FORM
# ─────────────────────────────────────────────
CARD = ("background:rgba(10,22,45,.85);border:1px solid rgba(255,255,255,.07);"
        "border-radius:20px;padding:28px;backdrop-filter:blur(16px);"
        "box-shadow:0 16px 48px rgba(0,0,0,.4);height:100%")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(f"<div style='{CARD}'>", unsafe_allow_html=True)
    section_header("👤", "Personal Profile", "Demographic information")
    field_label("Age")
    age = st.slider("Age", 20, 100, 50, label_visibility="collapsed")
    st.markdown(
        f"<div style='text-align:right;margin-top:-8px;margin-bottom:16px'>"
        f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:18px;"
        f"font-weight:500;color:#00C2FF'>{age}</span>"
        f"<span style='font-size:11px;color:#4A6A88'> years old</span></div>",
        unsafe_allow_html=True
    )
    field_label("Biological Sex")
    sex_label = st.selectbox("Sex", ["Female", "Male"], label_visibility="collapsed")
    sex = 0 if sex_label == "Female" else 1
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='{CARD}'>", unsafe_allow_html=True)
    section_header("🫀", "Medical History",
                   "Clinical measurements & diagnoses", bg="rgba(255,59,92,.10)")
    cp_map = {"Typical Angina": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Asymptomatic": 3}
    field_label("Chest Pain Type")
    cp = cp_map[st.selectbox("Chest Pain", list(cp_map.keys()), label_visibility="collapsed")]
    ca_col, cb_col = st.columns(2)
    with ca_col:
        field_label("Blood Pressure")
        trestbps = st.number_input("BP", 80, 200, 120, label_visibility="collapsed")
        st.caption("mmHg systolic")
    with cb_col:
        field_label("Cholesterol")
        chol = st.number_input("Chol", 100, 600, 200, label_visibility="collapsed")
        st.caption("mg/dL total")

    # ── UPDATED: Major Vessels with descriptive labels ──
    ca_map = {
        "0 — All vessels clear (No blockage)":     0,
        "1 — One vessel blocked (Mild risk)":      1,
        "2 — Two vessels blocked (Moderate risk)": 2,
        "3 — Three vessels blocked (High risk)":   3,
        "4 — All vessels blocked (Severe risk)":   4,
    }
    field_label("Major Vessels (Fluoroscopy)")
    ca = ca_map[st.selectbox("Major Vessels", list(ca_map.keys()), label_visibility="collapsed")]

    thal_map = {"Normal (1)": 1, "Fixed Defect (2)": 2, "Reversible Defect (3)": 3}
    field_label("Thalassemia")
    thal = thal_map[st.selectbox("Thalassemia", list(thal_map.keys()), label_visibility="collapsed")]
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div style='{CARD}'>", unsafe_allow_html=True)
    section_header("🏃", "Lifestyle Factors",
                   "Activity & daily habits", bg="rgba(0,224,154,.10)")
    field_label("Fasting Blood Sugar > 120 mg/dL")
    fbs = 1 if st.selectbox("FBS", ["No", "Yes"], label_visibility="collapsed") == "Yes" else 0
    field_label("Max Heart Rate Achieved")
    thalach = st.number_input("Heart Rate", 60, 250, 150, label_visibility="collapsed")
    st.caption("bpm during stress test")
    field_label("Exercise-Induced Angina")
    exang = 1 if st.selectbox("Exercise Angina", ["No", "Yes"], label_visibility="collapsed") == "Yes" else 0
    field_label("ST Depression (Oldpeak)")
    oldpeak = st.slider("Oldpeak", 0.0, 6.0, 1.0, step=0.1, label_visibility="collapsed")
    st.markdown(
        f"<div style='text-align:right;margin-top:-8px;margin-bottom:12px'>"
        f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:16px;"
        f"font-weight:500;color:#00E09A'>{oldpeak:.1f}</span>"
        f"<span style='font-size:11px;color:#4A6A88'> mm</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ANALYZE BUTTON
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1.5, 2, 1.5])
with btn_col:
    analyze = st.button("🧠  Analyze My Heart Risk", use_container_width=True)

# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
if analyze:
    input_data = np.array([[age, sex, cp, trestbps, chol, fbs, 0,
                             thalach, exang, oldpeak, 1, ca, thal]])
    scaled     = scaler.transform(input_data)
    prob       = model.predict_proba(scaled)
    risk       = round(prob[0][1] * 100, 2)

    if risk > 70:
        rc, rb, rbr, rl = "#FF3B5C", "rgba(255,59,92,.08)", "rgba(255,59,92,.25)", "High Risk"
    elif risk > 40:
        rc, rb, rbr, rl = "#FFB830", "rgba(255,184,48,.08)", "rgba(255,184,48,.25)", "Moderate Risk"
    else:
        rc, rb, rbr, rl = "#00E09A", "rgba(0,224,154,.08)", "rgba(0,224,154,.25)", "Low Risk"

    try:
        cursor.execute("INSERT INTO predictions(user_id,risk) VALUES(%s,%s)",
                       (st.session_state.user_id, risk))
        conn.commit()
    except Exception:
        pass

    user_name, user_email = "User", None
    try:
        cursor.execute("SELECT name, email FROM users WHERE id=%s",
                       (st.session_state.user_id,))
        row = cursor.fetchone()
        if row:
            user_name, user_email = row
    except Exception:
        pass

    if user_email:
        try:
            send_risk_email(user_email, user_name, risk, rl,
                            age, sex_label, trestbps, chol,
                            thalach, fbs, exang, oldpeak)
            st.toast(f"📧 Report sent to {user_email}", icon="✅")
        except Exception as e:
            st.toast(f"Email could not be sent: {e}", icon="⚠️")

    st.markdown(
        "<div style='text-align:center;padding:32px 0 24px'>"
        "<div style='font-family:\"Cormorant Garamond\",serif;font-size:32px;"
        "font-weight:600;color:#E2EFF9'>Your Cardiac Risk Report</div>"
        "</div>",
        unsafe_allow_html=True
    )

    r1, r2 = st.columns([1, 2], gap="large")

    with r1:
        deg = int(risk * 3.6)
        st.markdown(
            f"<div style='background:rgba(10,22,45,.9);border:1px solid {rbr};"
            f"border-radius:20px;padding:32px;text-align:center;box-shadow:0 0 40px {rb}'>"
            f"<p style='font-size:11px;font-weight:500;color:#4A6A88;"
            f"letter-spacing:.12em;text-transform:uppercase;margin-bottom:20px'>Overall Risk Score</p>"
            f"<div style='width:160px;height:160px;border-radius:50%;margin:0 auto 20px;"
            f"background:conic-gradient({rc} {deg}deg,rgba(255,255,255,.05) 0deg);"
            f"display:flex;align-items:center;justify-content:center'>"
            f"<div style='width:128px;height:128px;border-radius:50%;background:#0B1E38;"
            f"display:flex;flex-direction:column;align-items:center;justify-content:center'>"
            f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:38px;"
            f"font-weight:500;color:{rc};line-height:1'>{risk}</span>"
            f"<span style='font-size:11px;color:#4A6A88'>/ 100</span>"
            f"</div></div>"
            f"<div style='display:inline-flex;align-items:center;gap:8px;padding:8px 20px;"
            f"border-radius:999px;background:{rb};border:1px solid {rbr};"
            f"font-size:14px;font-weight:500;color:{rc}'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{rc};"
            f"display:inline-block;animation:pulse 2s infinite'></span>{rl}"
            f"</div></div>",
            unsafe_allow_html=True
        )

    with r2:
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Age", f"{age} yrs")
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Blood Pressure", f"{trestbps} mmHg",
                      delta="⚠ Elevated" if trestbps >= 130 else "✓ Normal",
                      delta_color="inverse" if trestbps >= 130 else "normal")
        with m2:
            st.metric("Cholesterol", f"{chol} mg/dL",
                      delta="⚠ High" if chol > 240 else "✓ Ok",
                      delta_color="inverse" if chol > 240 else "normal")
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Max Heart Rate", f"{thalach} bpm")

        st.markdown(
            f"<div style='background:rgba(10,22,45,.7);border:1px solid rgba(255,255,255,.07);"
            f"border-radius:14px;padding:20px;margin-top:16px'>"
            f"<div style='display:flex;justify-content:space-between;margin-bottom:8px'>"
            f"<span style='font-size:12px;color:#7FA8C8'>Risk Meter</span>"
            f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:12px;color:{rc}'>{risk}%</span>"
            f"</div>"
            f"<div style='height:8px;border-radius:4px;background:rgba(255,255,255,.06);overflow:hidden'>"
            f"<div style='height:100%;width:{risk}%;border-radius:4px;"
            f"background:linear-gradient(90deg,#00E09A,#FFB830,#FF3B5C)'></div>"
            f"</div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:6px'>"
            f"<span style='font-size:10px;color:#00E09A'>Low (0–40)</span>"
            f"<span style='font-size:10px;color:#FFB830'>Moderate (40–70)</span>"
            f"<span style='font-size:10px;color:#FF3B5C'>High (70+)</span>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    def insight_card(icon, title, value, unit, status_text, color, tag):
        fw = (min(int(float(str(value)) / (200 if unit == 'mmHg' else 400) * 100), 100)
              if unit in ('mmHg', 'mg/dL') else (70 if value == "Positive" else 20))
        st.markdown(
            f"<div style='background:rgba(10,22,45,.85);border-left:3px solid {color};"
            f"border-top:1px solid rgba(255,255,255,.06);"
            f"border-right:1px solid rgba(255,255,255,.06);"
            f"border-bottom:1px solid rgba(255,255,255,.06);"
            f"border-radius:14px;padding:20px'>"
            f"<div style='display:flex;justify-content:space-between;"
            f"align-items:flex-start;margin-bottom:10px'>"
            f"<div style='font-size:14px;font-weight:500;color:#E2EFF9'>{icon} {title}</div>"
            f"<span style='font-size:10px;font-weight:500;color:{color};padding:3px 10px;"
            f"border-radius:999px;background:{color}20;border:1px solid {color}40'>{tag}</span>"
            f"</div>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:26px;"
            f"font-weight:500;color:{color};margin-bottom:8px'>{value}"
            f"<span style='font-size:12px;color:#4A6A88'> {unit}</span></div>"
            f"<p style='font-size:12px;color:#7FA8C8;margin:0;line-height:1.6'>{status_text}</p>"
            f"<div style='margin-top:10px;height:3px;border-radius:2px;background:rgba(255,255,255,.06)'>"
            f"<div style='width:{fw}%;height:100%;border-radius:2px;background:{color}'></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    i1, i2, i3 = st.columns(3, gap="large")
    with i1:
        bc = "#FF3B5C" if trestbps >= 130 else "#00E09A"
        insight_card("🫀", "Blood Pressure", trestbps, "mmHg",
                     "Pre-hypertension — above optimal" if trestbps >= 130 else "Within normal range",
                     bc, "HIGH" if trestbps >= 130 else "NORMAL")
    with i2:
        cc = "#FF3B5C" if chol > 240 else ("#FFB830" if chol > 200 else "#00E09A")
        insight_card("💉", "Cholesterol", chol, "mg/dL",
                     "High — consult physician" if chol > 240 else ("Borderline" if chol > 200 else "Healthy range"),
                     cc, "HIGH" if chol > 240 else ("BORDERLINE" if chol > 200 else "HEALTHY"))
    with i3:
        ec = "#FF3B5C" if exang else "#00E09A"
        insight_card("🏃", "Exercise Angina",
                     "Positive" if exang else "Negative", "",
                     "Exercise-induced angina present — cardiac indicator." if exang
                     else "No exercise-induced angina — favorable sign.",
                     ec, "POSITIVE" if exang else "NEGATIVE")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div style='background:rgba(10,22,45,.85);border:1px solid rgba(255,255,255,.07);"
        "border-radius:20px;padding:28px'>"
        "<div style='font-size:16px;font-weight:500;color:#E2EFF9;margin-bottom:6px'>"
        "💡 Personalized Action Plan</div>"
        "<div style='font-size:12px;color:#4A6A88;margin-bottom:24px'>"
        "Recommendations ranked by impact</div>",
        unsafe_allow_html=True
    )

    recs = []
    if trestbps >= 130:
        recs.append(("🔴", "Address First", "#FF3B5C", "rgba(255,59,92,.1)",
                     "Manage Blood Pressure",
                     "Target systolic below 130 mmHg. Reduce sodium to &lt;2,300 mg/day and consider physician consultation."))
    if chol > 240:
        recs.append(("🔴", "Address First", "#FF3B5C", "rgba(255,59,92,.1)",
                     "Reduce Cholesterol",
                     "LDL-lowering interventions recommended. Adopt a Mediterranean diet and discuss statin therapy with your doctor."))
    if exang:
        recs.append(("🔴", "Address First", "#FF3B5C", "rgba(255,59,92,.1)",
                     "Cardiac Evaluation",
                     "Exercise-induced angina warrants prompt cardiologist evaluation. Avoid strenuous activity until cleared."))
    if fbs:
        recs.append(("🟡", "Within 30 Days", "#FFB830", "rgba(255,184,48,.1)",
                     "Manage Blood Sugar",
                     "Fasting glucose &gt;120 indicates pre-diabetes risk. Reduce refined carbs and monitor HbA1c levels."))
    if oldpeak > 2.0:
        recs.append(("🟡", "Within 30 Days", "#FFB830", "rgba(255,184,48,.1)",
                     "Review ST Changes",
                     f"ST depression of {oldpeak:.1f}mm may indicate ischemia. Request a stress ECG and echocardiogram."))
    recs.append(("🟢", "Lifestyle", "#00E09A", "rgba(0,224,154,.1)",
                 "Increase Physical Activity",
                 "Aim for 150 min/week of moderate cardio. Even 30 min/day reduces cardiac risk by up to 35%."))
    recs.append(("🟢", "Lifestyle", "#00E09A", "rgba(0,224,154,.1)",
                 "Adopt Heart-Healthy Diet",
                 "Mediterranean diet: olive oil, fish, legumes, whole grains. Proven to reduce cardiovascular events by 30%."))

    for i in range(0, len(recs), 3):
        batch = recs[i:i+3]
        rcols = st.columns(len(batch), gap="medium")
        for col, r in zip(rcols, batch):
            with col:
                st.markdown(
                    f"<div style='background:rgba(255,255,255,.02);"
                    f"border:1px solid rgba(255,255,255,.07);"
                    f"border-radius:14px;padding:18px;height:100%'>"
                    f"<div style='display:inline-flex;align-items:center;gap:5px;padding:3px 10px;"
                    f"border-radius:999px;background:{r[3]};border:1px solid {r[2]}30;"
                    f"font-size:10px;font-weight:500;color:{r[2]};margin-bottom:12px'>"
                    f"{r[0]} {r[1]}</div>"
                    f"<div style='font-size:14px;font-weight:500;color:#E2EFF9;margin-bottom:8px'>{r[4]}</div>"
                    f"<p style='font-size:12px;color:#7FA8C8;margin:0;line-height:1.65'>{r[5]}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

    if user_email:
        st.markdown(
            f"<div style='text-align:center;margin-top:16px;padding:12px 24px;"
            f"border-radius:12px;background:rgba(0,194,255,.05);"
            f"border:1px solid rgba(0,194,255,.15);max-width:600px;"
            f"margin-left:auto;margin-right:auto'>"
            f"<p style='font-size:12px;color:#7FA8C8;margin:0'>"
            f"📧 Full report sent to "
            f"<strong style='color:#00C2FF'>{user_email}</strong>"
            f"</p></div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<div style='text-align:center;margin-top:14px;padding:14px 24px;"
        "border-radius:12px;background:rgba(255,184,48,.05);"
        "border:1px solid rgba(255,184,48,.12);max-width:700px;"
        "margin-left:auto;margin-right:auto'>"
        "<p style='font-size:12px;color:#4A6A88;margin:0;line-height:1.7'>"
        "⚠ <strong style='color:#FFB830'>Medical Disclaimer:</strong> "
        "CardioAI is for educational purposes only — not medical diagnosis or advice. "
        "Always consult a qualified healthcare professional."
        "</p></div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    "<div style='margin-top:48px;padding:20px 0;"
    "border-top:1px solid rgba(255,255,255,.06);"
    "display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>"
    "<span style='font-size:13px;font-weight:500;color:#E2EFF9'>CardioAI"
    "<span style='font-size:12px;color:#4A6A88;font-weight:400'> · Built by Kishlay</span></span>"
    "<p style='font-size:11px;color:#4A6A88;margin:0'>"
    "Not a substitute for professional medical advice</p>"
    "</div>",
    unsafe_allow_html=True
)


