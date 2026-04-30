import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from database.db_connect import get_db

st.set_page_config(
    page_title="Reset Password · CardioAI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS in separate small blocks (prevents render-as-text bug) ──
st.markdown("<style>[data-testid='stSidebarNav']{display:none!important}[data-testid='stDecoration']{display:none!important}[data-testid='stHeader']{display:none!important}header{visibility:hidden!important}#MainMenu{display:none!important}footer{display:none!important}.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important}section.main>div{padding-top:0!important}</style>", unsafe_allow_html=True)

st.markdown("<style>html,body,.stApp{background:#030C1A!important;color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important;min-height:100vh}</style>", unsafe_allow_html=True)

st.markdown("<style>.stApp::before{content:'';position:fixed;width:700px;height:700px;top:-200px;left:-200px;background:radial-gradient(ellipse,rgba(0,98,204,.15) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d1 18s ease-in-out infinite;pointer-events:none}.stApp::after{content:'';position:fixed;width:500px;height:500px;bottom:-100px;right:-100px;background:radial-gradient(ellipse,rgba(0,194,255,.08) 0%,transparent 70%);border-radius:50%;z-index:0;animation:d2 22s ease-in-out infinite;pointer-events:none}@keyframes d1{0%,100%{transform:translate(0,0)}50%{transform:translate(80px,60px)}}@keyframes d2{0%,100%{transform:translate(0,0)}50%{transform:translate(-60px,40px)}}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}</style>", unsafe_allow_html=True)

st.markdown("<style>.stTextInput input{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;color:#E2EFF9!important;font-family:'DM Sans',sans-serif!important;font-size:14px!important;padding:12px 16px!important;transition:all .2s!important}.stTextInput input:focus{border-color:rgba(0,194,255,.5)!important;background:rgba(0,194,255,.04)!important;box-shadow:0 0 0 3px rgba(0,194,255,.08)!important}.stTextInput input::placeholder{color:#4A6A88!important}.stTextInput label{color:#7FA8C8!important;font-size:12px!important;font-weight:500!important;letter-spacing:.05em!important;text-transform:uppercase!important;margin-bottom:4px!important}</style>", unsafe_allow_html=True)

st.markdown("<style>div.stButton>button{background:linear-gradient(135deg,#0087C8,#00C2FF)!important;border:none!important;border-radius:10px!important;color:white!important;font-family:'DM Sans',sans-serif!important;font-size:15px!important;font-weight:500!important;padding:13px 24px!important;width:100%!important;box-shadow:0 4px 24px rgba(0,194,255,.25)!important;transition:all .25s!important}div.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 36px rgba(0,194,255,.45)!important}div[data-testid='stAlert']{border-radius:10px!important;border-left-width:3px!important;font-size:13px!important}[data-testid='column']{position:relative;z-index:1}</style>", unsafe_allow_html=True)

# ── Database & Session ──
conn   = get_db()
cursor = conn.cursor()

if "reset_otp"    not in st.session_state: st.session_state.reset_otp    = None
if "otp_sent"     not in st.session_state: st.session_state.otp_sent     = False
if "reset_email"  not in st.session_state: st.session_state.reset_email  = ""

# ── SVG Logo ──
LOGO = (
    "<div style='text-align:center;padding:52px 0 36px'>"
    "<div style='display:inline-flex;align-items:center;gap:12px;margin-bottom:8px'>"
    "<div style='width:44px;height:44px;"
    "background:linear-gradient(135deg,#1a0a10,#2d0f1a);"
    "border:1px solid rgba(255,59,92,.3);border-radius:12px;"
    "display:flex;align-items:center;justify-content:center'>"
    "<svg width='22' height='20' viewBox='0 0 24 22' fill='none'>"
    "<path d='M12 21.593c-.5-.377-10-7.9-10-13.093a6 6 0 0 1 10-4.472A6 6 0 0 1 22 8.5"
    "c0 5.193-9.5 12.716-10 13.093z' fill='url(#fg)'/>"
    "<defs><linearGradient id='fg' x1='2' y1='2' x2='22' y2='22' gradientUnits='userSpaceOnUse'>"
    "<stop offset='0%' stop-color='#FF3B5C'/>"
    "<stop offset='100%' stop-color='#FF7B93'/>"
    "</linearGradient></defs>"
    "</svg></div>"
    "<span style='font-family:Georgia,serif;font-size:26px;font-weight:600;"
    "color:#E2EFF9;letter-spacing:-.3px'>CardioAI</span>"
    "</div>"
    "<p style='font-size:12px;color:#4A6A88;margin:0'>AI Health Intelligence System</p>"
    "</div>"
)

# ── Glass card wrapper ──
CARD_OPEN = (
    "<div style='background:rgba(10,22,45,.92);"
    "border:1px solid rgba(255,255,255,.08);"
    "border-radius:24px;padding:40px 40px 32px;"
    "backdrop-filter:blur(32px);"
    "box-shadow:0 24px 80px rgba(0,0,0,.6),0 0 60px rgba(0,194,255,.04)'>"
)

# ── Layout ──
_, center, _ = st.columns([1, 1.1, 1])

with center:

    st.markdown(LOGO, unsafe_allow_html=True)
    st.markdown(CARD_OPEN, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  STEP 1 — Enter Email
    # ══════════════════════════════════════════
    if not st.session_state.otp_sent:

        # Step indicator
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:center;"
            "gap:8px;margin-bottom:28px'>"
            "<div style='display:flex;align-items:center;gap:6px'>"
            "<div style='width:24px;height:24px;border-radius:50%;"
            "background:linear-gradient(135deg,#0087C8,#00C2FF);"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:11px;font-weight:500;color:white'>1</div>"
            "<span style='font-size:12px;color:#00C2FF;font-weight:500'>Email</span>"
            "</div>"
            "<div style='width:40px;height:1px;background:rgba(255,255,255,.1)'></div>"
            "<div style='display:flex;align-items:center;gap:6px'>"
            "<div style='width:24px;height:24px;border-radius:50%;"
            "background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:11px;color:#4A6A88'>2</div>"
            "<span style='font-size:12px;color:#4A6A88'>Verify & Reset</span>"
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='text-align:center;margin-bottom:28px'>"
            "<h2 style='font-family:Georgia,serif;font-size:28px;"
            "font-weight:600;color:#E2EFF9;margin:0 0 8px'>Reset Password</h2>"
            "<p style='font-size:13px;color:#7FA8C8;margin:0;font-weight:300'>"
            "Enter your registered email to receive a verification code</p>"
            "</div>",
            unsafe_allow_html=True
        )

        email = st.text_input("Email Address", placeholder="you@example.com")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Send Verification Code"):
            if not email:
                st.warning("⚠ Please enter your email address.")
            else:
                cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
                if not cursor.fetchone():
                    st.error("❌ No account found with this email.")
                else:
                    otp = random.randint(100000, 999999)
                    st.session_state.reset_otp   = otp
                    st.session_state.otp_sent    = True
                    st.session_state.reset_email = email

                    msg = MIMEText(
                        f"Your CardioAI password reset code is:\n\n  {otp}\n\n"
                        f"Valid for 10 minutes.\n\n— The CardioAI Team"
                    )
                    msg["Subject"] = "CardioAI — Password Reset Code"

                    try:
                        with st.spinner("Sending code..."):
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.starttls()
                            server.login("tactickeet@gmail.com", "tvrqisveumxavgyg")
                            server.sendmail("tactickeet@gmail.com", email, msg.as_string())
                            server.quit()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not send email: {e}")

    # ══════════════════════════════════════════
    #  STEP 2 — OTP + New Password
    # ══════════════════════════════════════════
    else:
        masked = st.session_state.reset_email

        # Step indicator — step 2 active
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:center;"
            "gap:8px;margin-bottom:24px'>"
            "<div style='display:flex;align-items:center;gap:6px'>"
            "<div style='width:24px;height:24px;border-radius:50%;"
            "background:rgba(0,224,154,.15);border:1px solid rgba(0,224,154,.3);"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:10px;color:#00E09A'>✓</div>"
            "<span style='font-size:12px;color:#00E09A'>Email</span>"
            "</div>"
            "<div style='width:40px;height:1px;background:rgba(0,224,154,.3)'></div>"
            "<div style='display:flex;align-items:center;gap:6px'>"
            "<div style='width:24px;height:24px;border-radius:50%;"
            "background:linear-gradient(135deg,#0087C8,#00C2FF);"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:11px;font-weight:500;color:white'>2</div>"
            "<span style='font-size:12px;color:#00C2FF;font-weight:500'>Verify & Reset</span>"
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='text-align:center;margin-bottom:20px'>"
            "<h2 style='font-family:Georgia,serif;font-size:28px;"
            "font-weight:600;color:#E2EFF9;margin:0 0 8px'>Check Your Inbox</h2>"
            f"<p style='font-size:13px;color:#7FA8C8;margin:0;font-weight:300'>"
            f"Code sent to <span style='color:#00C2FF;font-family:monospace'>{masked}</span></p>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='background:rgba(0,194,255,.06);border:1px solid rgba(0,194,255,.18);"
            "border-radius:12px;padding:12px 16px;margin-bottom:20px'>"
            "<p style='font-size:12px;color:#7FA8C8;margin:0;line-height:1.7'>"
            "💡 Check your spam folder. Code is valid for "
            "<strong style='color:#E2EFF9'>10 minutes</strong>.</p>"
            "</div>",
            unsafe_allow_html=True
        )

        otp_input    = st.text_input("6-Digit Code",       placeholder="Enter OTP",          max_chars=6)
        new_password = st.text_input("New Password",       placeholder="Min. 8 characters",  type="password")
        confirm_pass = st.text_input("Confirm Password",   placeholder="Repeat password",     type="password")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Reset My Password"):
            if not otp_input or not new_password or not confirm_pass:
                st.warning("⚠ Please fill in all fields.")
            elif not otp_input.isdigit():
                st.error("❌ OTP must contain digits only.")
            elif len(new_password) < 8:
                st.warning("⚠ Password must be at least 8 characters.")
            elif new_password != confirm_pass:
                st.error("❌ Passwords do not match.")
            elif int(otp_input) != st.session_state.reset_otp:
                st.error("❌ Incorrect code. Please check your email.")
            else:
                try:
                    cursor.execute(
                        "UPDATE users SET password=%s WHERE email=%s",
                        (new_password, st.session_state.reset_email)
                    )
                    conn.commit()
                    st.session_state.reset_otp   = None
                    st.session_state.otp_sent    = False
                    st.session_state.reset_email = ""
                    st.success("✅ Password reset successfully! Redirecting...")
                    st.balloons()
                    import time; time.sleep(1.5)
                    st.switch_page("pages/login.py")
                except Exception as e:
                    st.error(f"Reset failed: {e}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        rc1, rc2 = st.columns(2, gap="small")
        with rc1:
            if st.button("Resend Code"):
                st.session_state.otp_sent = False
                st.rerun()
        with rc2:
            if st.button("Back to Login"):
                st.session_state.otp_sent    = False
                st.session_state.reset_otp   = None
                st.session_state.reset_email = ""
                st.switch_page("pages/login.py")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        "<div style='text-align:center;padding:20px 0 48px'>"
        "<p style='font-size:11px;color:#2A4A68;margin:0;line-height:1.7'>"
        "CardioAI is for educational purposes only — not medical advice.<br>"
        "Your data is encrypted and never shared."
        "</p></div>",
        unsafe_allow_html=True
    )
