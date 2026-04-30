import streamlit as st
from database.db_connect import get_db

st.set_page_config(
    page_title="Sign In · CardioAI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("<style>[data-testid='stSidebarNav']{display:none!important}[data-testid='stDecoration']{display:none!important}[data-testid='stHeader']{display:none!important}header{visibility:hidden!important}#MainMenu{display:none!important}footer{display:none!important}.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important}section.main>div{padding-top:0!important}</style>", unsafe_allow_html=True)

st.markdown("<style>html,body,.stApp{background:#030C1A!important;color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important;min-height:100vh}</style>", unsafe_allow_html=True)

st.markdown("<style>.stApp::before{content:'';position:fixed;width:700px;height:700px;top:-200px;left:-200px;background:radial-gradient(ellipse,rgba(0,98,204,.15) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d1 18s ease-in-out infinite;pointer-events:none}.stApp::after{content:'';position:fixed;width:500px;height:500px;bottom:-100px;right:-100px;background:radial-gradient(ellipse,rgba(0,194,255,.08) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d2 22s ease-in-out infinite;pointer-events:none}@keyframes d1{0%,100%{transform:translate(0,0)}50%{transform:translate(80px,60px)}}@keyframes d2{0%,100%{transform:translate(0,0)}50%{transform:translate(-60px,40px)}}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}</style>", unsafe_allow_html=True)

st.markdown("<style>.stTextInput input{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;color:#E2EFF9!important;font-size:14px!important;padding:12px 16px!important;transition:all .2s!important}.stTextInput input:focus{border-color:rgba(0,194,255,.5)!important;background:rgba(0,194,255,.04)!important;box-shadow:0 0 0 3px rgba(0,194,255,.08)!important}.stTextInput input::placeholder{color:#4A6A88!important}.stTextInput label{color:#7FA8C8!important;font-size:12px!important;font-weight:500!important;letter-spacing:.05em!important;text-transform:uppercase!important;margin-bottom:4px!important}</style>", unsafe_allow_html=True)

st.markdown("<style>div.stButton>button{background:linear-gradient(135deg,#0087C8,#00C2FF)!important;border:none!important;border-radius:10px!important;color:white!important;font-size:15px!important;font-weight:500!important;padding:13px 24px!important;width:100%!important;box-shadow:0 4px 24px rgba(0,194,255,.25)!important;transition:all .25s!important}div.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 36px rgba(0,194,255,.45)!important}div[data-testid='stAlert']{border-radius:10px!important;border-left-width:3px!important;font-size:13px!important}[data-testid='column']{position:relative;z-index:1}</style>", unsafe_allow_html=True)

# ── Forgot password link style — bilkul link jaisa dikhega ──
st.markdown("""
<style>
.fp-link div.stButton > button {
    background: transparent !important;
    border: none !important;
    color: #00C2FF !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 0 !important;
    box-shadow: none !important;
    width: auto !important;
    text-decoration: underline !important;
    float: right !important;
    margin-top: -8px !important;
    margin-bottom: 20px !important;
}
.fp-link div.stButton > button:hover {
    transform: none !important;
    color: #00E0FF !important;
    box-shadow: none !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ── Database ──
conn   = get_db()
cursor = conn.cursor()

# ── Layout ──
_, center, _ = st.columns([1, 1.1, 1])

with center:

    st.markdown(
        "<div style='text-align:center;padding:52px 0 36px'>"
        "<div style='display:inline-flex;align-items:center;gap:12px;margin-bottom:8px'>"
        "<div style='width:44px;height:44px;background:linear-gradient(135deg,#1a0a10,#2d0f1a);"
        "border:1px solid rgba(255,59,92,.3);border-radius:12px;"
        "display:flex;align-items:center;justify-content:center'>"
        "<svg width='22' height='20' viewBox='0 0 24 22' fill='none' xmlns='http://www.w3.org/2000/svg'>"
        "<path d='M12 21.593c-.5-.377-10-7.9-10-13.093a6 6 0 0 1 10-4.472A6 6 0 0 1 22 8.5c0 5.193-9.5 12.716-10 13.093z' fill='url(#hg)'/>"
        "<defs><linearGradient id='hg' x1='2' y1='2' x2='22' y2='22' gradientUnits='userSpaceOnUse'>"
        "<stop offset='0%' stop-color='#FF3B5C'/><stop offset='100%' stop-color='#FF7B93'/>"
        "</linearGradient></defs>"
        "</svg></div>"
        "<span style='font-family:Georgia,serif;font-size:26px;font-weight:600;"
        "color:#E2EFF9;letter-spacing:-.3px'>CardioAI</span>"
        "</div>"
        "<p style='font-size:12px;color:#4A6A88;margin:0'>AI Health Intelligence System</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:rgba(10,22,45,.92);border:1px solid rgba(255,255,255,.08);"
        "border-radius:24px;padding:40px 40px 32px;backdrop-filter:blur(32px);"
        "box-shadow:0 24px 80px rgba(0,0,0,.6),0 0 60px rgba(0,194,255,.04)'>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='text-align:center;margin-bottom:32px'>"
        "<h2 style='font-family:Georgia,serif;font-size:30px;"
        "font-weight:600;color:#E2EFF9;margin:0 0 8px'>Welcome Back</h2>"
        "<p style='font-size:13px;color:#7FA8C8;margin:0;font-weight:300'>"
        "Sign in to your CardioAI account</p>"
        "</div>",
        unsafe_allow_html=True
    )

    email    = st.text_input("Email Address", placeholder="you@example.com")
    password = st.text_input("Password",      placeholder="••••••••", type="password")

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    if st.button("Sign In to CardioAI"):
        if not email or not password:
            st.warning("⚠ Please enter your email and password.")
        else:
            with st.spinner("Verifying credentials..."):
                cursor.execute(
                    "SELECT id FROM users WHERE email=%s AND password=%s",
                    (email, password)
                )
                user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id   = user[0]
                st.success("✅ Login successful! Redirecting...")
                import time; time.sleep(0.8)
                st.switch_page("app.py")
            else:
                st.error("❌ Invalid email or password.")

    st.markdown(
        "<div style='height:1px;background:rgba(255,255,255,.06);margin:24px 0 20px'></div>",
        unsafe_allow_html=True
    )

    b1, b2 = st.columns(2, gap="small")
    with b1:
        if st.button("Forgot Password"):
            st.switch_page("pages/forgot_password.py")
    with b2:
        if st.button("Create Account"):
            st.switch_page("pages/signup.py")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;padding:20px 0 48px'>"
        "<p style='font-size:11px;color:#2A4A68;margin:0;line-height:1.7'>"
        "CardioAI is for educational purposes only — not medical advice.<br>"
        "Your data is encrypted and never shared."
        "</p></div>",
        unsafe_allow_html=True
    )
