import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from database.db_connect import get_db

st.set_page_config(
    page_title="Create Account · CardioAI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──
st.markdown("<style>[data-testid='stSidebarNav']{display:none!important}[data-testid='stDecoration']{display:none!important}[data-testid='stHeader']{display:none!important}header{visibility:hidden!important}#MainMenu{display:none!important}footer{display:none!important}.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important}section.main>div{padding-top:0!important}</style>", unsafe_allow_html=True)

st.markdown("<style>html,body,.stApp{background:#030C1A!important;color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important;min-height:100vh}</style>", unsafe_allow_html=True)

st.markdown("<style>.stApp::before{content:'';position:fixed;width:700px;height:700px;top:-200px;left:-200px;background:radial-gradient(ellipse,rgba(0,98,204,.15) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d1 18s ease-in-out infinite;pointer-events:none}.stApp::after{content:'';position:fixed;width:500px;height:500px;bottom:-100px;right:-100px;background:radial-gradient(ellipse,rgba(0,194,255,.08) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d2 22s ease-in-out infinite;pointer-events:none}@keyframes d1{0%,100%{transform:translate(0,0)}50%{transform:translate(80px,60px)}}@keyframes d2{0%,100%{transform:translate(0,0)}50%{transform:translate(-60px,40px)}}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}</style>", unsafe_allow_html=True)

st.markdown("<style>.stTextInput input{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;color:#E2EFF9!important;font-size:14px!important;padding:12px 16px!important;transition:all .2s!important}.stTextInput input:focus{border-color:rgba(0,194,255,.5)!important;background:rgba(0,194,255,.04)!important;box-shadow:0 0 0 3px rgba(0,194,255,.08)!important}.stTextInput input::placeholder{color:#4A6A88!important}.stTextInput label{color:#7FA8C8!important;font-size:12px!important;font-weight:500!important;letter-spacing:.05em!important;text-transform:uppercase!important;margin-bottom:4px!important}</style>", unsafe_allow_html=True)

st.markdown("<style>div.stButton>button{background:linear-gradient(135deg,#0087C8,#00C2FF)!important;border:none!important;border-radius:10px!important;color:white!important;font-size:15px!important;font-weight:500!important;padding:13px 24px!important;width:100%!important;box-shadow:0 4px 24px rgba(0,194,255,.25)!important;transition:all .25s!important}div.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 36px rgba(0,194,255,.45)!important}div[data-testid='stAlert']{border-radius:10px!important;border-left-width:3px!important;font-size:13px!important}[data-testid='column']{position:relative;z-index:1}</style>", unsafe_allow_html=True)

# ── Database & Session Init ──
conn   = get_db()
cursor = conn.cursor()

if "otp"       not in st.session_state: st.session_state.otp       = None
if "otp_sent"  not in st.session_state: st.session_state.otp_sent  = False
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# ── Pehle se logged in ho toh seedha app pe bhejo ──
if st.session_state.logged_in:
    st.switch_page("app.py")


def render_logo():
    st.markdown(
        "<div style='text-align:center;padding:52px 0 36px'>"
        "<div style='display:inline-flex;align-items:center;gap:12px;margin-bottom:8px'>"
        "<div style='width:44px;height:44px;background:linear-gradient(135deg,#1a0a10,#2d0f1a);"
        "border:1px solid rgba(255,59,92,.3);border-radius:12px;"
        "display:flex;align-items:center;justify-content:center'>"
        "<svg width='22' height='20' viewBox='0 0 24 22' fill='none' xmlns='http://www.w3.org/2000/svg'>"
        "<path d='M12 21.593c-.5-.377-10-7.9-10-13.093a6 6 0 0 1 10-4.472A6 6 0 0 1 22 8.5c0 5.193-9.5 12.716-10 13.093z' fill='url(#hg2)'/>"
        "<defs><linearGradient id='hg2' x1='2' y1='2' x2='22' y2='22' gradientUnits='userSpaceOnUse'>"
        "<stop offset='0%' stop-color='#FF3B5C'/><stop offset='100%' stop-color='#FF7B93'/>"
        "</linearGradient></defs></svg></div>"
        "<span style='font-family:Georgia,serif;font-size:26px;font-weight:600;"
        "color:#E2EFF9;letter-spacing:-.3px'>CardioAI</span>"
        "</div>"
        "<p style='font-size:12px;color:#4A6A88;margin:0'>AI Health Intelligence System</p>"
        "</div>",
        unsafe_allow_html=True
    )


_, center, _ = st.columns([1, 1.1, 1])

with center:

    render_logo()

    st.markdown(
        "<div style='background:rgba(10,22,45,.92);border:1px solid rgba(255,255,255,.08);"
        "border-radius:24px;padding:40px 40px 32px;backdrop-filter:blur(32px);"
        "box-shadow:0 24px 80px rgba(0,0,0,.6),0 0 60px rgba(0,194,255,.04)'>",
        unsafe_allow_html=True
    )

    # ══ STEP 1 — Details Fill ══
    if not st.session_state.otp_sent:

        st.markdown(
            "<div style='text-align:center;margin-bottom:32px'>"
            "<h2 style='font-family:Georgia,serif;font-size:30px;"
            "font-weight:600;color:#E2EFF9;margin:0 0 8px'>Create Your Account</h2>"
            "<p style='font-size:13px;color:#7FA8C8;margin:0;font-weight:300'>"
            "Join CardioAI and take charge of your heart health</p>"
            "</div>",
            unsafe_allow_html=True
        )

        nc1, nc2 = st.columns(2, gap="small")
        with nc1:
            first_name = st.text_input("First Name", placeholder="John")
        with nc2:
            last_name  = st.text_input("Last Name",  placeholder="Doe")

        email    = st.text_input("Email Address",    placeholder="you@example.com")
        password = st.text_input("Password",         placeholder="Min. 8 characters", type="password")
        confirm  = st.text_input("Confirm Password", placeholder="Repeat your password", type="password")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Send Verification OTP"):
            name = f"{first_name.strip()} {last_name.strip()}".strip()
            if not first_name or not last_name or not email or not password or not confirm:
                st.warning("⚠ Please fill in all fields.")
            elif len(password) < 8:
                st.warning("⚠ Password must be at least 8 characters.")
            elif password != confirm:
                st.error("❌ Passwords do not match.")
            else:
                cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
                if cursor.fetchone():
                    st.error("❌ This email is already registered. Please sign in.")
                else:
                    otp = random.randint(100000, 999999)
                    st.session_state.otp       = otp
                    st.session_state.otp_sent  = True
                    st.session_state.reg_name  = name
                    st.session_state.reg_email = email
                    st.session_state.reg_pass  = password

                    msg = MIMEText(
                        f"Hi {name},\n\n"
                        f"Your CardioAI verification code is:\n\n  {otp}\n\n"
                        f"This code expires in 10 minutes.\n\n— The CardioAI Team"
                    )
                    msg["Subject"] = "CardioAI — Verify Your Email"

                    try:
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls()
                        server.login("tactickeet@gmail.com", "tvrqisveumxavgyg")
                        server.sendmail("tactickeet@gmail.com", email, msg.as_string())
                        server.quit()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Email could not be sent: {e}")

    # ══ STEP 2 — OTP Verify ══
    else:
        masked = st.session_state.get("reg_email", "your email")

        st.markdown(
            "<div style='text-align:center;margin-bottom:28px'>"
            "<div style='width:56px;height:56px;border-radius:16px;"
            "background:rgba(0,194,255,.10);border:1px solid rgba(0,194,255,.2);"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:26px;margin:0 auto 16px'>📬</div>"
            "<h2 style='font-family:Georgia,serif;font-size:28px;"
            "font-weight:600;color:#E2EFF9;margin:0 0 8px'>Check Your Inbox</h2>"
            f"<p style='font-size:13px;color:#7FA8C8;margin:0;font-weight:300'>"
            f"We sent a 6-digit code to<br>"
            f"<span style='color:#00C2FF;font-family:monospace'>{masked}</span></p>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='background:rgba(0,194,255,.06);border:1px solid rgba(0,194,255,.18);"
            "border-radius:12px;padding:14px 18px;margin-bottom:20px'>"
            "<p style='font-size:12px;color:#7FA8C8;margin:0;line-height:1.7'>"
            "💡 Didn't receive it? Check your spam folder. "
            "Code is valid for <strong style='color:#E2EFF9'>10 minutes</strong>.</p>"
            "</div>",
            unsafe_allow_html=True
        )

        user_otp = st.text_input("6-Digit OTP", placeholder="Enter OTP", max_chars=6)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Verify & Create Account"):
            if not user_otp:
                st.warning("⚠ Please enter the OTP.")
            elif not user_otp.isdigit():
                st.error("❌ OTP must be digits only.")
            elif int(user_otp) != st.session_state.otp:
                st.error("❌ Incorrect OTP. Please check your email.")
            else:
                try:
                    # ── DB mein user insert ──
                    cursor.execute(
                        "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
                        (st.session_state.reg_name,
                         st.session_state.reg_email,
                         st.session_state.reg_pass)
                    )
                    conn.commit()

                    # ── AUTO-LOGIN: naya user fetch karke session set karo ──
                    cursor.execute(
                        "SELECT id, name, email FROM users WHERE email=%s",
                        (st.session_state.reg_email,)
                    )
                    new_user = cursor.fetchone()
                    if new_user:
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = new_user[0]
                        st.session_state.user_name  = new_user[1]
                        st.session_state.user_email = new_user[2]

                    # ── Signup state cleanup ──
                    st.session_state.otp      = None
                    st.session_state.otp_sent = False
                    st.session_state.pop("reg_name",  None)
                    st.session_state.pop("reg_email", None)
                    st.session_state.pop("reg_pass",  None)

                    st.success("🎉 Account created! Taking you in...")
                    st.balloons()
                    import time; time.sleep(1.5)
                    st.switch_page("app.py")   # ✅ FIXED — root ka app.py

                except Exception as e:
                    st.error(f"Registration failed: {e}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Resend OTP"):
            st.session_state.otp_sent = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;padding:20px 0 48px'>"
        "<p style='font-size:11px;color:#2A4A68;margin:0;line-height:1.7'>"
        "By creating an account you agree to our Terms &amp; Privacy Policy.<br>"
        "CardioAI is for educational purposes only — not medical advice."
        "</p></div>",
        unsafe_allow_html=True
    )

    if st.button("Back to Login"):
        st.switch_page("pages/login.py")
