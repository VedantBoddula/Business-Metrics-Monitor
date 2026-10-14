from pathlib import Path
import io
import sqlite3
import pandas as pd
import streamlit as st

from src.column_mapping import auto_map_columns
from src.email_alert import send_email_alert
from src.auth import admin_login, admin_logout

from src.preprocessing import (
    create_daily_data,
    create_region_data,
    create_product_data,
    create_category_data,
)

from src.anomaly_detector import (
    detect_overall_sales_drops,
    detect_overall_sales_spikes,
    detect_category_sales_spikes,
    detect_product_sales_spikes,
    detect_profit_margin_drops,
    detect_regional_sales_drops,
)

# Page configuration
st.set_page_config(
    page_title="Business Metrics Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Authentication gate
if not admin_login():
    st.stop()

admin_logout()

# ---------------------------------------------------------------------------
# Executive Design System & Styling
# Token alignment with src/auth.py:
#   ink:    #0E1A2B (Deep corporate navy)
#   canvas: #F8FAFC (Modern slate off-white)
#   paper:  #FFFFFF (Crisp container cards)
#   line:   #E2E8F0 (Subtle structural borders)
#   accent: #1F5FD6 (Primary interaction blue)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #0E1A2B;
    --ink-dark: #08111D;
    --ink-soft: #9FB0C8;
    --canvas: #F8FAFC;
    --paper: #FFFFFF;
    --line: #E2E8F0;
    --line-subtle: #EDF2F7;
    --text: #0F172A;
    --text-muted: #64748B;
    --accent: #1F5FD6;
    --accent-hover: #174BB0;
    --accent-soft: #EFF6FF;
    --critical: #EF4444;
    --critical-soft: #FEF2F2;
    --critical-border: #FCA5A5;
    --high: #F97316;
    --high-soft: #FFF7ED;
    --high-border: #FDBA74;
    --moderate: #F59E0B;
    --moderate-soft: #FFFBEB;
    --moderate-border: #FCD34D;
    --success: #10B981;
}

/* Page canvas & typography */
html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: var(--canvas) !important;
    color: #0F172A !important;
}

.block-container {
    max-width: 1400px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2.25rem !important;
    padding-right: 2.25rem !important;
}

/* Base text color guarantees */
.main .block-container p,
.main .block-container span,
.main .block-container label,
.main .block-container div[data-testid="stMarkdownContainer"] p {
    color: #0F172A !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #0E1A2B !important;
    font-weight: 700 !important;
}

.stCaption, .stCaption p, [data-testid="stCaptionContainer"] p {
    color: #64748B !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0E1A2B !important;
    border-right: 1px solid #1E2D42 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 1.25rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
    color: #CBD5E1 !important;
}

[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] .stCaption p {
    color: #94A3B8 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #1E2D42 !important;
    margin: 1.25rem 0 !important;
}

/* Sidebar navigation - Sleek pill navigation */
[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 4px !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 7px 10px !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
}

/* Hide the clunky radio circle */
[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
    color: #94A3B8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
    padding-left: 4px !important;
    transition: color 0.15s ease !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.06) !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
    background: #1F5FD6 !important;
    box-shadow: 0 1px 3px rgba(31, 95, 214, 0.3) !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Sidebar Dataset Card */
.sidebar-dataset-card {
    background: #16263D;
    border: 1px solid #2B3E5C;
    border-radius: 9px;
    padding: 10px 12px;
    margin-top: 8px;
    margin-bottom: 12px;
}

.dataset-badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    gap: 8px;
}

.dataset-badge-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #38BDF8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.dataset-pill {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid rgba(16, 185, 129, 0.35);
    white-space: nowrap;
}

.dataset-file-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #F8FAFC;
    word-break: break-all;
    line-height: 1.35;
    margin-bottom: 4px;
}

.dataset-meta {
    font-size: 0.72rem;
    color: #94A3B8;
}

/* Sidebar File Uploader Container */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] label p {
    color: #CBD5E1 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

/* Dropzone Area */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] section {
    background: #16263D !important;
    border: 1px dashed #2E4468 !important;
    border-radius: 8px !important;
    padding: 12px 10px !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] section:hover {
    border-color: #3B82F6 !important;
    background: #192D4A !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] section [data-testid="stMarkdownContainer"] p {
    color: #CBD5E1 !important;
    font-size: 0.8rem !important;
    line-height: 1.3 !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] section small {
    color: #94A3B8 !important;
    font-size: 0.7rem !important;
}

/* "Browse files" button ONLY inside dropzone */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] section button {
    background-color: #1F5FD6 !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 6px !important;
    padding: 5px 14px !important;
    margin-top: 6px !important;
    width: auto !important;
    min-height: 32px !important;
    height: 32px !important;
    box-shadow: 0 1px 3px rgba(31, 95, 214, 0.3) !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] section button:hover {
    background-color: #2563EB !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] section button p,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] section button span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}

/* Uploaded File Item Container */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] div[data-testid="stFileUploader"] li {
    background: #16263D !important;
    border: 1px solid #2B3E5C !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    margin-top: 8px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 8px !important;
    list-style: none !important;
}

/* Uploaded file text (filename & size) - Force high contrast white */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul *,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] *,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span {
    color: #FFFFFF !important;
    font-size: 0.78rem !important;
}

/* Uploaded file icon */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] svg,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul svg {
    color: #38BDF8 !important;
    fill: #38BDF8 !important;
    min-width: 16px !important;
}

/* Delete 'X' button in file uploader */
[data-testid="stSidebar"] div[data-testid="stFileUploader"] button[data-testid="stFileUploaderDeleteFile"],
[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul button {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 6px !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 26px !important;
    height: 26px !important;
    min-height: 26px !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button:hover,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul button:hover {
    background: rgba(239, 68, 68, 0.25) !important;
    border-color: #EF4444 !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button svg,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul button svg {
    color: #E2E8F0 !important;
    fill: #E2E8F0 !important;
    width: 12px !important;
    height: 12px !important;
}

[data-testid="stSidebar"] div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button:hover svg,
[data-testid="stSidebar"] div[data-testid="stFileUploader"] ul button:hover svg {
    color: #EF4444 !important;
    fill: #EF4444 !important;
}

/* Executive Metric Cards */
div[data-testid="stMetric"] {
    background-color: var(--paper) !important;
    padding: 1.1rem 1.3rem !important;
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
    box-shadow: 0 1px 3px rgba(14, 26, 43, 0.04), 0 2px 6px -1px rgba(14, 26, 43, 0.02) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px -2px rgba(14, 26, 43, 0.06) !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label * {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 2px !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
    color: #0E1A2B !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricDelta"],
div[data-testid="stMetric"] [data-testid="stMetricDelta"] * {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

/* Primary and Secondary Buttons */
.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background-color: var(--ink) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--ink) !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    padding: 0.48rem 1.15rem !important;
    font-size: 0.88rem !important;
    min-height: 38px !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(14, 26, 43, 0.06) !important;
}

.stButton > button *, div[data-testid="stFormSubmitButton"] > button * {
    color: #FFFFFF !important;
}

.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 3px 8px rgba(31, 95, 214, 0.22) !important;
    transform: translateY(-1px);
}

.stButton > button:hover *, div[data-testid="stFormSubmitButton"] > button:hover * {
    color: #FFFFFF !important;
}

/* Sign out button top bar */
.st-key-logout_bar button p,
.st-key-logout_bar button span {
    color: #F4F7FB !important;
}

/* Clean, proportionate expanders */
div[data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    margin: 0.5rem 0 !important;
    padding: 0 !important;
}

div[data-testid="stExpander"] details {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(14, 26, 43, 0.03) !important;
    overflow: hidden !important;
    transition: border-color 0.15s ease !important;
}

div[data-testid="stExpander"] details:hover {
    border-color: #CBD5E1 !important;
}

div[data-testid="stExpander"] details summary {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #1E293B !important;
    padding: 0.55rem 0.85rem !important;
    min-height: auto !important;
    line-height: 1.4 !important;
    cursor: pointer !important;
}

div[data-testid="stExpander"] details summary:hover {
    background-color: #F8FAFC !important;
    color: #1F5FD6 !important;
}

div[data-testid="stExpander"] details summary svg {
    width: 0.95rem !important;
    height: 0.95rem !important;
    color: #64748B !important;
}

div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border-top: 1px solid #F1F5F9 !important;
    padding: 0.85rem 1rem !important;
    background: #FFFFFF !important;
}

div[data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
    color: #1E293B !important;
}

/* Alert callout containers */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin: 0.65rem 0 !important;
}

/* Selectboxes & Dropdowns */
div[data-baseweb="select"] {
    border-radius: 8px !important;
}

div[data-baseweb="select"] > div {
    background-color: var(--paper) !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    min-height: 42px !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(31, 95, 214, 0.15) !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] p,
div[data-baseweb="select"] input {
    color: #0F172A !important;
    font-size: 0.92rem !important;
}

/* Dropdown popover list */
div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px rgba(14, 26, 43, 0.12) !important;
}

ul[role="listbox"] li, div[data-baseweb="menu"] li, [role="option"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

ul[role="listbox"] li:hover, [role="option"]:hover,
ul[role="listbox"] li[aria-selected="true"], [role="option"][aria-selected="true"] {
    background-color: #EFF6FF !important;
    color: #1F5FD6 !important;
}

/* Dataframe containers */
div[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
    background-color: var(--paper) !important;
    box-shadow: 0 1px 3px rgba(14, 26, 43, 0.04) !important;
    overflow: hidden !important;
}

/* Custom Header Banner */
.app-header {
    background: linear-gradient(135deg, #0E1A2B 0%, #16263D 100%);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.75rem;
    color: #FFFFFF;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px -2px rgba(14, 26, 43, 0.15);
    border: 1px solid #1E2D42;
}

.app-header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    background: rgba(31, 95, 214, 0.25);
    border: 1px solid rgba(59, 130, 246, 0.4);
    font-size: 0.72rem;
    font-weight: 600;
    color: #93C5FD;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.app-header-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 6px 0;
    line-height: 1.2;
}

.app-header-subtitle {
    color: #9FB0C8;
    font-size: 0.92rem;
    margin: 0;
    max-width: 680px;
    line-height: 1.5;
}

.header-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34D399;
    font-size: 0.82rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-dot-pulse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: status-pulse 2s infinite;
}

@keyframes status-pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Section Title Modules */
.section-title-wrap {
    margin-bottom: 1.25rem;
}

.section-tag {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent);
    margin-bottom: 3px;
}

.section-heading {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
}

.section-caption {
    font-size: 0.88rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* Sidebar Elements */
.sidebar-brand-box {
    padding: 0.5rem 0 1.25rem 0;
    border-bottom: 1px solid #1E2D42;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 12px;
}

.sidebar-logo-icon {
    width: 32px;
    height: 32px;
    background: #1F5FD6;
    border-radius: 8px;
    display: grid;
    place-items: center;
}

.sidebar-brand-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}

.sidebar-brand-subtitle {
    font-size: 0.72rem;
    color: #9FB0C8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.sidebar-system-card {
    background: #16263D;
    border: 1px solid #2B3E5C;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 1.75rem;
}

.system-card-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #9FB0C8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.system-status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    padding: 4px 0;
    color: #CBD5E1;
    white-space: nowrap;
}

.system-status-val {
    font-weight: 600;
    color: #F8FAFC;
    text-align: right;
}

/* Email Alert Dispatch Box */
.email-dispatch-card {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0;
    box-shadow: 0 1px 3px rgba(14, 26, 43, 0.05);
}
</style>
""", unsafe_allow_html=True)

# Top Branded Executive Header
st.markdown("""
<div class="app-header">
    <div class="header-left">
        <div class="app-header-badge">Enterprise Intelligence Platform</div>
        <div class="app-header-title">Business Metrics Anomaly Monitor</div>
        <div class="app-header-subtitle">Continuous metric tracking, statistical anomaly detection, and automated incident alerts across commercial operations.</div>
    </div>
    <div class="header-status-pill">
        <div class="status-dot-pulse"></div>
        <span>Detection Engine Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar & Navigation
# ---------------------------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-brand-box">
    <div class="sidebar-logo-icon">
        <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
            <path d="M1.5 11 5 7l3 2.5L14 3" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <div>
        <div class="sidebar-brand-title">MetricsRadar</div>
        <div class="sidebar-brand-subtitle">Anomaly Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("##### Navigation")
page = st.sidebar.radio(
    "Navigation Menu",
    [
        "Overview",
        "Sales Analytics",
        "Anomaly Detection",
        "Business Impact",
        "Alert History",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("##### 📁 Data Source")

card_placeholder = st.sidebar.empty()

uploaded_file = st.sidebar.file_uploader(
    "Upload custom dataset",
    type=["csv", "xlsx", "xls"],
    help="Upload a CSV or Excel transaction dataset.",
)

is_custom = uploaded_file is not None
active_name = uploaded_file.name if is_custom else "ecommerce_business_monitoring_dataset.xlsx"
active_tag = "Custom" if is_custom else "Default"
active_meta = "Uploaded Dataset In Use" if is_custom else "13,464 records • 8 columns"

card_placeholder.markdown(f"""
<div class="sidebar-dataset-card">
    <div class="dataset-badge-row">
        <span class="dataset-badge-title">Active Source</span>
        <span class="dataset-pill">{active_tag}</span>
    </div>
    <div class="dataset-file-name" title="{active_name}">
        {active_name}
    </div>
    <div class="dataset-meta">{active_meta}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-system-card">
    <div class="system-card-title">System Health</div>
    <div class="system-status-row"><span>Detectors</span><span class="system-status-val">6 Active</span></div>
    <div class="system-status-row"><span>Database</span><span class="system-status-val">Connected</span></div>
    <div class="system-status-row"><span>Status</span><span class="system-status-val">Operational</span></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Loading & Ingestion Pipeline
# ---------------------------------------------------------------------------
DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "ecommerce_business_monitoring_dataset.xlsx"
)


@st.cache_data
def load_transactions(path):
    return pd.read_excel(path, sheet_name="Transactions")


@st.cache_data
def load_uploaded_transactions(file_bytes, filename):
    file_obj = io.BytesIO(file_bytes)
    if filename.lower().endswith(".csv"):
        return pd.read_csv(file_obj)
    return pd.read_excel(file_obj, sheet_name="Transactions")


try:
    if uploaded_file is not None:
        raw_df = load_uploaded_transactions(
            uploaded_file.getvalue(),
            uploaded_file.name,
        )
        st.sidebar.success("Custom dataset loaded successfully")
    else:
        raw_df = load_transactions(DATA_PATH)

    # Map alternative column names to standard internal schema
    df = auto_map_columns(raw_df)

    required_columns = [
        "Order_ID",
        "Date",
        "Product_Name",
        "Category",
        "Region",
        "Quantity",
        "Sales",
        "Profit",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(
            "Dataset is missing required columns: "
            + ", ".join(missing_columns)
        )
        st.stop()

    # Convert columns to appropriate data types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["Sales", "Profit", "Quantity"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove rows with missing critical values
    df = df.dropna(
        subset=[
            "Order_ID",
            "Date",
            "Sales",
            "Profit",
            "Quantity",
        ]
    ).copy()

    if df.empty:
        st.error(
            "No valid transaction records found. "
            "Please check your dataset."
        )
        st.stop()

except Exception as error:
    st.error(f"Could not load transaction data: {error}")
    st.stop()


# ---------------------------------------------------------------------------
# Page: Overview
# ---------------------------------------------------------------------------
if page == "Overview":
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Executive Summary</div>
        <h2 class="section-heading">Business Performance Overview</h2>
        <div class="section-caption">Core commercial metrics, transaction volumes, and aggregated sales trajectories.</div>
    </div>
    """, unsafe_allow_html=True)

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()
    total_units = df["Quantity"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"₹{total_sales:,.0f}")
    col2.metric("Total Profit", f"₹{total_profit:,.0f}")
    col3.metric("Total Orders", f"{total_orders:,}")
    col4.metric("Units Sold", f"{total_units:,.0f}")

    st.markdown("---")

    daily_sales = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )

    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Temporal Trajectory</div>
        <h3 class="section-heading">Daily Sales Trend</h3>
        <div class="section-caption">Aggregated daily revenue generation across all operations over time.</div>
    </div>
    """, unsafe_allow_html=True)

    st.line_chart(
        daily_sales.set_index("Date")["Sales"],
        x_label="Date",
        y_label="Sales (₹)",
    )

    left, right = st.columns(2)

    with left:
        st.markdown("""
        <div class="section-title-wrap">
            <div class="section-tag">Sector Breakdown</div>
            <h3 class="section-heading">Sales by Category</h3>
        </div>
        """, unsafe_allow_html=True)
        category_sales = (
            df.groupby("Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(category_sales, horizontal=True)

    with right:
        st.markdown("""
        <div class="section-title-wrap">
            <div class="section-tag">Territory Breakdown</div>
            <h3 class="section-heading">Sales by Region</h3>
        </div>
        """, unsafe_allow_html=True)
        region_sales = (
            df.groupby("Region")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(region_sales)


# ---------------------------------------------------------------------------
# Page: Sales Analytics
# ---------------------------------------------------------------------------
elif page == "Sales Analytics":
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Segment Analytics</div>
        <h2 class="section-heading">Sales & Margin Analytics</h2>
        <div class="section-caption">Filter by commercial category to investigate localized sales and profit performance.</div>
    </div>
    """, unsafe_allow_html=True)

    categories = ["All"] + sorted(
        df["Category"].dropna().unique().tolist()
    )
    selected_category = st.selectbox("Select Category", categories)

    filtered_df = df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Category"] == selected_category
        ]

    daily = (
        filtered_df.groupby("Date", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum"),
        )
        .sort_values("Date")
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Segment Sales", f"₹{filtered_df['Sales'].sum():,.0f}")
    metric2.metric("Segment Profit", f"₹{filtered_df['Profit'].sum():,.0f}")
    metric3.metric("Units Sold", f"{filtered_df['Quantity'].sum():,.0f}")

    st.markdown("---")

    st.markdown("##### Sales Over Time")
    st.line_chart(daily.set_index("Date")["Sales"])

    st.markdown("##### Profit Over Time")
    st.line_chart(daily.set_index("Date")["Profit"])

    with st.expander("📄 View filtered transaction data"):
        st.dataframe(filtered_df, use_container_width=True)


# ---------------------------------------------------------------------------
# Page: Anomaly Detection
# ---------------------------------------------------------------------------
elif page == "Anomaly Detection":
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Algorithmic Monitoring</div>
        <h2 class="section-heading">Anomaly Detection Command Center</h2>
        <div class="section-caption">Statistical anomaly detection across revenue drops, category spikes, product surges, margin drops, and regional activity.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Executing anomaly detection algorithms..."):
        daily_data = create_daily_data(df)
        region_daily = create_region_data(df)
        product_daily = create_product_data(df)
        category_daily = create_category_data(df)

        _, sales_drops = detect_overall_sales_drops(daily_data)
        _, sales_spikes = detect_overall_sales_spikes(daily_data)
        _, category_spikes = detect_category_sales_spikes(category_daily)
        _, product_spikes = detect_product_sales_spikes(product_daily)
        _, margin_drops = detect_profit_margin_drops(category_daily)
        _, regional_drops = detect_regional_sales_drops(region_daily)

    events = []

    def add_events(data, anomaly_type, scope_column=None):
        for _, event in data.iterrows():
            row = {
                "Anomaly Type": anomaly_type,
                "Start Date": pd.to_datetime(event["Start_Date"]),
                "End Date": pd.to_datetime(event["End_Date"]),
                "Duration (days)": int(event["Duration"]),
                "Scope": (
                    str(event[scope_column])
                    if scope_column and scope_column in event.index
                    else "Overall Business"
                ),
            }

            if "Avg_Sales_Change" in event.index:
                row["Sales Change (%)"] = round(
                    event["Avg_Sales_Change"], 1
                )

            if "Avg_Quantity_Change" in event.index:
                row["Quantity Change (%)"] = round(
                    event["Avg_Quantity_Change"], 1
                )

            if "Avg_Margin_Drop_pp" in event.index:
                row["Margin Drop (pp)"] = round(
                    event["Avg_Margin_Drop_pp"], 1
                )

            events.append(row)

    add_events(sales_drops, "Overall Sales Drop")
    add_events(sales_spikes, "Overall Sales Spike")
    add_events(category_spikes, "Category Sales Spike", "Category")
    add_events(product_spikes, "Product Sales Spike", "Product_Name")
    add_events(margin_drops, "Profit Margin Drop", "Category")
    add_events(regional_drops, "Regional Sales Drop", "Region")

    # Assign severity using transparent, configurable rules
    def assign_severity(row):
        anomaly_type = row["Anomaly Type"]
        sales_change = row.get("Sales Change (%)")
        margin_drop = row.get("Margin Drop (pp)")

        if anomaly_type in [
            "Overall Sales Drop",
            "Regional Sales Drop",
        ] and pd.notna(sales_change):
            if sales_change <= -40:
                return "Critical"
            elif sales_change <= -30:
                return "High"
            return "Moderate"

        if anomaly_type == "Profit Margin Drop" and pd.notna(margin_drop):
            if margin_drop <= -15:
                return "Critical"
            elif margin_drop <= -8:
                return "High"
            return "Moderate"

        if pd.notna(sales_change):
            magnitude = abs(sales_change)
            if magnitude >= 200:
                return "Critical"
            elif magnitude >= 100:
                return "High"

        return "Moderate"

    if not events:
        st.success("No anomalies were detected with the current rules.")
    else:
        results = pd.DataFrame(events)
        results["Severity"] = results.apply(assign_severity, axis=1)
        results = results.sort_values("Start Date", ascending=False)

        critical_count = (results["Severity"] == "Critical").sum()
        high_count = (results["Severity"] == "High").sum()
        moderate_count = (results["Severity"] == "Moderate").sum()

        # Stakeholder Incident Alert Dispatcher
        st.markdown("""
        <div class="email-dispatch-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="font-weight:700; font-size:1.05rem; color:#0E1A2B; display:flex; align-items:center; gap:8px;">
                        <span>📧</span> Executive Incident Dispatcher
                    </div>
                    <div style="font-size:0.86rem; color:#64748B; margin-top:2px;">
                        Dispatch an automated anomaly summary report to registered stakeholders via email.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📧 Send Email Alert"):
            email_body = (
                "Business Metrics Anomaly Report\n\n"
                "Hello,\n\n"
                "Business monitoring has detected unusual activity.\n\n"
                f"Total anomalies: {len(results)}\n"
                f"Critical: {critical_count}\n"
                f"High: {high_count}\n"
                f"Moderate: {moderate_count}\n\n"
                "Please visit the dashboard for detailed insights. "
                "For extended monitoring or further analysis, feel free to contact us.\n\n"
                "Regards,\n"
                "Business Metrics Monitor Team"
            )

            html_body = f"""
            <html>
            <body style="margin:0;padding:24px;background:#f1f5f9;
            font-family:Arial,sans-serif;color:#1e293b;">
            <div style="max-width:560px;margin:auto;background:#ffffff;
            border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">

                <div style="background:#172640;color:white;padding:24px;">
                <h2 style="margin:0;">Business Metrics Anomaly Report</h2>
                <p style="color:#cbd5e1;margin-bottom:0;">
                    Automated Business Monitoring Alert
                </p>
                </div>

                <div style="padding:24px;">
                <p>Hello,</p>
                <p>Unusual business activity has been detected by the monitoring system.</p>

                <h3>Anomaly Summary</h3>

                <table style="width:100%;border-collapse:collapse;">
                    <tr>
                    <td style="padding:12px;border-bottom:1px solid #e2e8f0;">
                        Total Anomalies
                    </td>
                    <td style="padding:12px;text-align:right;">
                        <b>{len(results)}</b>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:12px;color:#dc2626;">Critical</td>
                    <td style="padding:12px;text-align:right;"><b>{critical_count}</b></td>
                    </tr>
                    <tr>
                    <td style="padding:12px;color:#d97706;">High</td>
                    <td style="padding:12px;text-align:right;"><b>{high_count}</b></td>
                    </tr>
                    <tr>
                    <td style="padding:12px;color:#a16207;">Moderate</td>
                    <td style="padding:12px;text-align:right;"><b>{moderate_count}</b></td>
                    </tr>
                </table>

                <p style="margin-top:24px;line-height:1.6;">
                    Please visit the dashboard for detailed insights.
                    For extended monitoring or further analysis, feel free to contact us.
                </p>

                <p style="line-height:1.6;">
                    Regards,<br><b>Business Metrics Monitor Team</b>
                </p>
                </div>
            </div>
            </body>
            </html>
            """

            email_sent = send_email_alert(
                subject="Business Metrics Anomaly Report",
                body=email_body,
                html_body=html_body,
            )

            if email_sent:
                st.success("Email sent successfully!")
            else:
                st.error(
                    "Email could not be sent. "
                    "Check your .env configuration and terminal."
                )

        # Overview metric cards
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Detected Events", len(results))
        with col2:
            st.metric(
                "Distinct Anomaly Types",
                results["Anomaly Type"].nunique(),
            )

        # Severity triage cards
        st.markdown("##### Severity Triage Breakdown")
        col_c, col_h, col_m = st.columns(3)

        with col_c:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #FECACA; border-left:4px solid #EF4444; border-radius:10px; padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.78rem; font-weight:700; color:#DC2626; text-transform:uppercase; letter-spacing:0.05em;">Critical Severity</span>
                    <span style="background:#FEF2F2; color:#DC2626; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #FCA5A5;">Immediate</span>
                </div>
                <div style="font-size:2rem; font-weight:700; color:#0E1A2B; margin-top:6px;">{critical_count}</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:2px;">Events requiring urgent investigation</div>
            </div>
            """, unsafe_allow_html=True)

        with col_h:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #FED7AA; border-left:4px solid #F97316; border-radius:10px; padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.78rem; font-weight:700; color:#EA580C; text-transform:uppercase; letter-spacing:0.05em;">High Severity</span>
                    <span style="background:#FFF7ED; color:#EA580C; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #FDBA74;">Elevated</span>
                </div>
                <div style="font-size:2rem; font-weight:700; color:#0E1A2B; margin-top:6px;">{high_count}</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:2px;">Substantial baseline departures</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #FDE68A; border-left:4px solid #F59E0B; border-radius:10px; padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.78rem; font-weight:700; color:#D97706; text-transform:uppercase; letter-spacing:0.05em;">Moderate Severity</span>
                    <span style="background:#FFFBEB; color:#D97706; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #FCD34D;">Standard</span>
                </div>
                <div style="font-size:2rem; font-weight:700; color:#0E1A2B; margin-top:6px;">{moderate_count}</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:2px;">Moderate deviations detected</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Interactive filter bar
        anomaly_types = ["All"] + sorted(
            results["Anomaly Type"].unique().tolist()
        )
        severity_options = ["All", "Critical", "High", "Moderate"]

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            selected_anomaly = st.selectbox(
                "Filter by anomaly type",
                anomaly_types,
            )
        with filter_col2:
            selected_severity = st.selectbox(
                "Filter by severity",
                severity_options,
            )

        filtered_results = results.copy()

        if selected_severity != "All":
            filtered_results = filtered_results[
                filtered_results["Severity"] == selected_severity
            ]

        if selected_anomaly != "All":
            filtered_results = filtered_results[
                filtered_results["Anomaly Type"] == selected_anomaly
            ]

        st.caption(f"Showing {len(filtered_results)} of {len(results)} detected event(s)")

        st.dataframe(
            filtered_results,
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------------------------
        # Anomaly Investigation Studio
        # -------------------------------------------------------------------
        st.markdown("---")
        st.markdown("""
        <div class="section-title-wrap">
            <div class="section-tag">Root Cause Analysis</div>
            <h3 class="section-heading">🔎 Anomaly Investigation Studio</h3>
            <div class="section-caption">Select any detected incident to compare metrics against historical 4-week baselines and inspect root drivers.</div>
        </div>
        """, unsafe_allow_html=True)

        if filtered_results.empty:
            st.info("No events match the selected filters for investigation.")
        else:
            investigation_data = filtered_results.reset_index(drop=True)

            selected_index = st.selectbox(
                "Choose an incident to investigate",
                options=investigation_data.index.tolist(),
                format_func=lambda i: (
                    f"{investigation_data.loc[i, 'Anomaly Type']} | "
                    f"{investigation_data.loc[i, 'Scope']} | "
                    f"{investigation_data.loc[i, 'Start Date']:%Y-%m-%d} to "
                    f"{investigation_data.loc[i, 'End Date']:%Y-%m-%d} "
                    f"[{investigation_data.loc[i, 'Severity'].upper()}]"
                ),
                key="investigation_event",
            )

            event = investigation_data.loc[selected_index]

            anomaly_type = event["Anomaly Type"]
            scope = event["Scope"]
            severity = event["Severity"]
            start_date = event["Start Date"]
            end_date = event["End Date"]

            # Severity banner feedback
            if severity == "Critical":
                st.error(f"🚨 **CRITICAL SEVERITY INCIDENT** — Immediate operational review recommended.")
            elif severity == "High":
                st.warning(f"⚠️ **HIGH SEVERITY INCIDENT** — Substantial baseline variation detected across monitored timeframe.")
            else:
                st.info(f"ℹ️ **MODERATE SEVERITY INCIDENT** — Baseline fluctuation within standard variance monitoring limits.")

            detail1, detail2, detail3 = st.columns(3)
            detail1.metric("Anomaly Type", anomaly_type)
            detail2.metric("Duration", f"{event['Duration (days)']} days")
            detail3.metric("Timeframe", f"{start_date:%d %b %Y} – {end_date:%d %b %Y}")

            # Select the correct data and baseline for this event
            if anomaly_type in [
                "Overall Sales Drop",
                "Overall Sales Spike",
            ]:
                detail_data = daily_data[
                    (daily_data["Date"] >= start_date)
                    & (daily_data["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Sales_4week_Avg"
                metric_label = "Sales"
                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            elif anomaly_type == "Regional Sales Drop":
                detail_data = region_daily[
                    (region_daily["Region"] == scope)
                    & (region_daily["Date"] >= start_date)
                    & (region_daily["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Same_Day_4week_Avg"
                metric_label = "Sales"
                quantity_column = None
                quantity_baseline = None

            elif anomaly_type == "Product Sales Spike":
                detail_data = product_daily[
                    (product_daily["Product_Name"] == scope)
                    & (product_daily["Date"] >= start_date)
                    & (product_daily["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Same_Day_4week_Avg"
                metric_label = "Sales"
                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            else:
                # Category sales spike or profit margin drop
                detail_data = category_daily[
                    (category_daily["Category"] == scope)
                    & (category_daily["Date"] >= start_date)
                    & (category_daily["Date"] <= end_date)
                ].copy()

                if anomaly_type == "Profit Margin Drop":
                    metric_column = "Profit_Margin_pct"
                    baseline_column = "Profit_Margin_4week_Avg"
                    metric_label = "Profit Margin (%)"
                else:
                    metric_column = "Sales"
                    baseline_column = "Same_Day_4week_Avg"
                    metric_label = "Sales"

                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            if detail_data.empty:
                st.warning("No matching daily records were found for this event.")
            else:
                if metric_column == "Profit_Margin_pct":
                    actual_value = detail_data[metric_column].mean()
                    baseline_value = detail_data[baseline_column].mean()
                    value_format = "{:.2f}%"
                else:
                    actual_value = detail_data[metric_column].sum()
                    baseline_value = detail_data[baseline_column].sum()
                    value_format = "₹{:,.0f}" if metric_column == "Sales" else "{:,.0f}"

                if pd.notna(baseline_value) and baseline_value != 0:
                    change_pct = (
                        (actual_value - baseline_value)
                        / abs(baseline_value)
                    ) * 100
                else:
                    change_pct = None

                st.markdown("##### Actual Performance vs Historical Baseline")

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric(
                    f"Actual {metric_label}",
                    value_format.format(actual_value),
                )

                metric2.metric(
                    f"Baseline {metric_label}",
                    value_format.format(baseline_value)
                    if pd.notna(baseline_value)
                    else "Unavailable",
                )

                metric3.metric(
                    "Change vs Baseline",
                    f"{change_pct:+.1f}%"
                    if change_pct is not None
                    else "Unavailable",
                    delta=f"{change_pct:+.1f}%" if change_pct is not None else None,
                )

                # Plot actual values against historical baseline
                chart_columns = [metric_column, baseline_column]

                chart_data = detail_data[
                    ["Date"] + chart_columns
                ].copy()

                chart_data = chart_data.sort_values("Date")
                chart_data = chart_data.set_index("Date")

                chart_data = chart_data.rename(columns={
                    metric_column: f"Actual {metric_label}",
                    baseline_column: f"Historical Baseline ({metric_label})",
                })

                st.line_chart(
                    chart_data,
                    x_label="Date",
                    y_label=metric_label,
                )

                # Supporting business metrics
                if "Profit" in detail_data.columns:
                    total_profit = detail_data["Profit"].sum()
                    st.metric("Total Profit During Event", f"₹{total_profit:,.2f}")

                if (
                    quantity_column
                    and quantity_column in detail_data.columns
                    and quantity_baseline in detail_data.columns
                ):
                    actual_quantity = detail_data[quantity_column].sum()
                    baseline_quantity = detail_data[quantity_baseline].sum()

                    q1, q2 = st.columns(2)
                    q1.metric("Units Sold During Event", f"{actual_quantity:,.0f}")
                    q2.metric(
                        "Expected Baseline Units",
                        f"{baseline_quantity:,.1f}",
                    )

                # Break down overall business events by product and region
                if anomaly_type in [
                    "Overall Sales Drop",
                    "Overall Sales Spike",
                ]:
                    event_transactions = df[
                        (df["Date"] >= start_date)
                        & (df["Date"] <= end_date)
                    ]

                    left, right = st.columns(2)

                    with left:
                        st.markdown("##### Top Contributing Products")
                        product_breakdown = (
                            event_transactions.groupby("Product_Name")["Sales"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(5)
                        )
                        st.bar_chart(product_breakdown, horizontal=True)

                    with right:
                        st.markdown("##### Regional Distribution")
                        region_breakdown = (
                            event_transactions.groupby("Region")["Sales"]
                            .sum()
                            .sort_values(ascending=False)
                        )
                        st.bar_chart(region_breakdown)

                # Daily records expander
                with st.expander("📄 View daily investigation data records"):
                    st.dataframe(
                        detail_data,
                        use_container_width=True,
                        hide_index=True,
                    )

                st.info(
                    "💡 **Context Note**: The historical baseline serves as an observational comparison "
                    "reference derived from moving averages, not a guaranteed forecast. Review broader "
                    "business seasonality and marketing events before initiating corrective actions."
                )

        with st.expander("ℹ️ How does algorithmic anomaly detection work?"):
            st.markdown("""
            The monitor computes rolling multi-week statistical metrics across transaction records, categories, and territories:
            - **Overall Sales Drops & Spikes**: Flags multi-day deviations comparing total sales to 4-week trailing averages.
            - **Category Surges & Margin Drops**: Isolates product segment fluctuations and profit margin compressions.
            - **Product Spikes & Regional Drops**: Pinpoints micro-level changes impacting specific SKUs or geographical hubs.
            
            Detected events are flagged for investigation to help teams react proactively to supply, pricing, or demand shifts.
            """)


# ---------------------------------------------------------------------------
# Page: Business Impact
# ---------------------------------------------------------------------------
elif page == "Business Impact":
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Commercial Valuation</div>
        <h2 class="section-heading">💼 Business Impact Analysis</h2>
        <div class="section-caption">Quantify revenue generation, profitability margins, and geographic concentrations across operations.</div>
    </div>
    """, unsafe_allow_html=True)

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Revenue", f"₹{total_sales:,.0f}")

    with col2:
        st.metric("Total Profit", f"₹{total_profit:,.0f}")

    with col3:
        st.metric("Total Orders", f"{total_orders:,}")

    st.markdown("---")

    col_cat, col_reg = st.columns(2)

    with col_cat:
        st.markdown("##### Revenue & Profit by Category")
        category_impact = (
            df.groupby("Category", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
            .sort_values("Revenue", ascending=False)
        )
        st.bar_chart(
            category_impact.set_index("Category")[["Revenue", "Profit"]]
        )

    with col_reg:
        st.markdown("##### Revenue & Profit by Region")
        region_impact = (
            df.groupby("Region", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
            .sort_values("Revenue", ascending=False)
        )
        st.bar_chart(
            region_impact.set_index("Region")[["Revenue", "Profit"]]
        )

    st.markdown("##### Category Performance Matrix")
    st.dataframe(
        category_impact,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# Page: Alert History
# ---------------------------------------------------------------------------
elif page == "Alert History":
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-tag">Audit & Compliance</div>
        <h2 class="section-heading">📜 Alert & Incident History</h2>
        <div class="section-caption">Historical audit trail of all automated alerts and incident notifications logged to SQLite.</div>
    </div>
    """, unsafe_allow_html=True)

    DB_PATH = Path(__file__).parent / "alert_history.db"

    if not DB_PATH.exists():
        st.info("ℹ️ No alert history database found yet. Run the monitoring pipeline first.")
    else:
        try:
            with sqlite3.connect(DB_PATH) as connection:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table'",
                    connection,
                )["name"].tolist()

                if not tables:
                    st.info("The alert history database has no tables yet.")
                else:
                    history = pd.read_sql_query(
                        f'SELECT * FROM "{tables[0]}"',
                        connection,
                    )

                    if history.empty:
                        st.info("No alerts recorded yet.")
                    else:
                        history.columns = [
                            column.replace("_", " ").title()
                            for column in history.columns
                        ]

                        st.metric("Total Recorded Alerts", len(history))

                        if "Alert Type" in history.columns:
                            alert_types = ["All"] + sorted(
                                history["Alert Type"].dropna().unique().tolist()
                            )
                            selected_type = st.selectbox(
                                "Filter by alert type",
                                alert_types,
                            )

                            if selected_type != "All":
                                history = history[
                                    history["Alert Type"] == selected_type
                                ]

                        st.caption(f"Showing {len(history)} recorded alert(s)")

                        for _, alert in history.iloc[::-1].iterrows():
                            alert_type = alert.get("Alert Type", "Alert")
                            start_date = str(alert.get("Start Date", "N/A"))[:10]
                            end_date = str(alert.get("End Date", "N/A"))[:10]
                            status = alert.get("Status", "Unknown")
                            summary = str(alert.get("Summary", "No summary available"))

                            with st.expander(
                                f"🔔 {alert_type} | {start_date} to {end_date} [{status.upper()}]"
                            ):
                                meta_col1, meta_col2 = st.columns(2)
                                meta_col1.markdown(f"**Status:** `{status}`")
                                meta_col2.markdown(f"**Alert ID:** `{alert.get('Id', 'N/A')}`")

                                st.markdown("**Incident Summary**")
                                st.markdown(f"""
                                <div style="background:#F1F5F9; border-left:3px solid #1F5FD6; padding:12px 16px; border-radius:6px; font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#1E293B; white-space:pre-wrap;">{summary.replace('\\n', '\n')}</div>
                                """, unsafe_allow_html=True)

        except Exception as error:
            st.error(f"Could not read alert history: {error}")
