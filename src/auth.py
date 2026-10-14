import os
import hmac
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


def admin_login() -> bool:
    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"],
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        #MainMenu,
        footer {
            display: none !important;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 10% 10%,
                    #172c59 0%,
                    transparent 35%
                ),
                linear-gradient(135deg, #071225, #0b1730) !important;
            color: #f1f5f9;
        }

        .block-container {
            width: 100%;
            max-width: 1200px;
            padding: 2.5rem 2rem 3rem;
        }

        .brand-title {
            font-size: clamp(1.7rem, 3vw, 2.45rem);
            font-weight: 800;
            line-height: 1.2;
            color: #f8fafc;
            margin-bottom: 12px;
            overflow-wrap: anywhere;
        }

        .brand-gradient {
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-subtitle {
            color: #a9bad4;
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 2rem;
        }

        .feature {
            padding: 14px;
            margin: 12px 0;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.035);
            color: #dbeafe;
            overflow-wrap: anywhere;
        }

        .login-card {
            box-sizing: border-box;
            width: 100%;
            min-width: 0;
            border: 1px solid #253c62;
            border-radius: 18px;
            padding: 28px 24px;
            background: rgba(16, 32, 59, 0.85);
            box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(8px);
        }

        .login-heading {
            font-size: clamp(1.6rem, 3vw, 2rem);
            font-weight: 750;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 6px;
        }

        .login-subtitle {
            color: #9fb2cf;
            text-align: center;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 24px;
        }

        div[data-testid="stTextInput"] {
            width: 100%;
            min-width: 0;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stTextInput"] label {
            color: #e2e8f0 !important;
            font-weight: 600;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            background: #111f38 !important;
            border: 1px solid #344b70 !important;
            border-radius: 10px !important;
            min-height: 46px !important;
            transition: border-color 0.15s ease;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #60a5fa !important;
            box-shadow: 0 0 0 1px #60a5fa !important;
        }

        div[data-testid="stTextInput"] input {
            background: transparent !important;
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
            font-size: 0.95rem !important;
            border: none !important;
        }

        /* Password visibility eye toggle icon */
        div[data-testid="stTextInput"] button {
            background: transparent !important;
            border: none !important;
            color: #94A3B8 !important;
            cursor: pointer !important;
            padding: 0 8px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"] button:hover {
            color: #60A5FA !important;
        }

        div[data-testid="stTextInput"] button * {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
            font-size: 20px !important;
            font-style: normal !important;
            letter-spacing: normal !important;
            line-height: 1 !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: 'liga' 1 !important;
            font-feature-settings: 'liga' 1 !important;
            -webkit-font-smoothing: antialiased !important;
        }

        /* Hide the Enter-to-submit hint near the password eye */
        [data-testid="InputInstructions"] {
            display: none !important;
        }

        /* Submit Button */
        div[data-testid="stFormSubmitButton"] {
            width: 100% !important;
            margin-top: 0.75rem !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            width: 100% !important;
            min-height: 46px !important;
            border: none !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 0.98rem !important;
            background: linear-gradient(90deg, #4f67f5, #269be8) !important;
            transition: filter 0.2s ease;
            box-shadow: 0 2px 8px rgba(38, 155, 232, 0.3) !important;
        }

        div[data-testid="stFormSubmitButton"] button p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            filter: brightness(1.12);
        }

        .secure-note {
            text-align: center;
            color: #8da2c2;
            font-size: 0.82rem;
            line-height: 1.5;
            padding-top: 16px;
            margin-top: 18px;
            border-top: 1px solid #253854;
            overflow-wrap: anywhere;
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 1.5rem 1rem 2rem;
            }

            .brand-subtitle {
                margin-bottom: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.markdown(
            """
            <div style="padding-top: 36px;">
                <div style="font-size: 3rem; margin-bottom: 8px;">📊</div>
                <div class="brand-title">
                    Business Metrics<br>
                    <span class="brand-gradient">Anomaly Monitor</span>
                </div>
                <div class="brand-subtitle">
                    Detect anomalies. Make better decisions.
                </div>

                <div class="feature">
                    📈 &nbsp; <b>Monitor Business Metrics</b><br>
                    <span style="color:#9fb2cf">
                    Track important business indicators.
                    </span>
                </div>

                <div class="feature">
                    🛡️ &nbsp; <b>Detect Anomalies</b><br>
                    <span style="color:#9fb2cf">
                    Identify unusual patterns and outliers.
                    </span>
                </div>

                <div class="feature">
                    ✉️ &nbsp; <b>Email Alerts</b><br>
                    <span style="color:#9fb2cf">
                    Send reports when you need them.
                    </span>
                </div>

                <p style="color:#7f95b8; font-size:0.85rem; margin-top:28px;">
                    Smarter Analytics &nbsp; • &nbsp;
                    Faster Insights &nbsp; • &nbsp;
                    Better Decisions
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center; font-size:2.5rem; margin-bottom:4px;">🔐</div>
            <div class="login-heading">Admin Login</div>
            <div class="login-subtitle">
                Sign in to access your monitoring dashboard
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("admin_login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )
            submitted = st.form_submit_button("Sign in →")

        if submitted:
            admin_username = os.getenv("ADMIN_USERNAME", "")
            admin_password = os.getenv("ADMIN_PASSWORD", "")

            if not admin_username or not admin_password:
                st.warning(
                    "Admin credentials are not set. Add ADMIN_USERNAME "
                    "and ADMIN_PASSWORD to your .env file."
                )
            else:
                valid_username = (
                    hmac.compare_digest(
                        username.encode("utf-8"),
                        admin_username.encode("utf-8"),
                    )
                    if admin_username else False
                )
                valid_password = (
                    hmac.compare_digest(
                        password.encode("utf-8"),
                        admin_password.encode("utf-8"),
                    )
                    if admin_password else False
                )

                if valid_username and valid_password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown(
            """
            <div class="secure-note">
                🛡️ &nbsp; Authorized admin access only
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.get("authenticated", False)


LOGOUT_CSS = """
<style>
[data-testid="stAppDeployButton"] { display: none !important; }

.st-key-logout_bar {
    position: fixed;
    top: 10px;
    right: 155px;
    z-index: 999999;
    width: auto;
}
.st-key-logout_bar button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 12px !important;
    box-shadow: 0 1px 2px rgba(14, 26, 43, 0.04) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
}
.st-key-logout_bar button p,
.st-key-logout_bar button span,
.st-key-logout_bar button * {
    color: #0E1A2B !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}
.st-key-logout_bar button:hover {
    background: #FEF2F2 !important;
    border-color: #FCA5A5 !important;
}
.st-key-logout_bar button:hover p,
.st-key-logout_bar button:hover span,
.st-key-logout_bar button:hover * {
    color: #DC2626 !important;
}
.st-key-logout_bar button:focus-visible {
    outline: 2px solid rgba(220, 38, 38, .35) !important;
    outline-offset: 1px !important;
}
</style>
"""


def admin_logout() -> None:
    st.markdown(LOGOUT_CSS, unsafe_allow_html=True)

    with st.container(key="logout_bar"):
        if st.button(
            "Sign out",
            key="admin_logout_topbar",
            type="secondary",
            help="Sign out of the admin dashboard",
        ):
            st.session_state["authenticated"] = False
            st.rerun()