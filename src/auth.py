
import os
import hmac
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


def admin_login():
    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"],
        #MainMenu,
        footer {
            visibility: hidden;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 10% 10%,
                    #172c59 0%,
                    transparent 35%
                ),
                linear-gradient(135deg, #071225, #0b1730);
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
            color: #e2e8f0;
            font-weight: 600;
        }

        div[data-testid="stTextInput"] input {
            box-sizing: border-box;
            width: 100%;
            min-width: 0;
            background: #111f38;
            color: #f8fafc;
            border: 1px solid #344b70;
            border-radius: 10px;
            min-height: 46px;
            padding-right: 3rem;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #60a5fa;
            box-shadow: 0 0 0 1px #60a5fa;
        }

        /* Hide the Enter-to-submit hint near the password eye */
        [data-testid="InputInstructions"] {
            display: none !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 48px;
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 700;
            background: linear-gradient(90deg, #4f67f5, #269be8);
            transition: filter 0.2s ease;
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

    left, right = st.columns([0.9, 1.1], gap="large")

    with left:
        st.markdown(
            """
            <div style="padding-top: 48px;">
                <div style="font-size: 3rem;">📊</div>
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

                <p style="color:#7f95b8; font-size:0.85rem;
                          margin-top:28px;">
                    Smarter Analytics &nbsp; • &nbsp;
                    Faster Insights &nbsp; • &nbsp;
                    Better Decisions
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-heading">🔐<br>Admin Login</div>
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

            valid_username = (
                hmac.compare_digest(username, admin_username)
                if admin_username else False
            )
            valid_password = (
                hmac.compare_digest(password, admin_password)
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
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.get("authenticated", False)



def admin_logout():
    st.markdown(
        """
        <style>
        /* Hide the built-in Deploy button */
        [data-testid="stAppDeployButton"] {
            display: none !important;
        }

        /* Style the top-right toolbar area */
        div[data-testid="stButton"]:has(
            button[kind="secondary"][aria-label="Logout"]
        ) {
            position: fixed;
            top: 12px;
            right: 58px;
            z-index: 999999;
            width: auto;
        }

        div[data-testid="stButton"]:has(
            button[kind="secondary"][aria-label="Logout"]
        ) button {
            background: #172640;
            color: #f8fafc;
            border: 1px solid #3b5276;
            border-radius: 9px;
            padding: 5px 16px;
            font-weight: 600;
        }

        div[data-testid="stButton"]:has(
            button[kind="secondary"][aria-label="Logout"]
        ) button:hover {
            background: #243b5e;
            border-color: #60a5fa;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Logout",
        key="admin_logout_topbar",
        type="secondary",
        help="Log out of the admin dashboard",
    ):
        st.session_state["authenticated"] = False
        st.rerun()
