import streamlit as st
import pandas as pd
import subprocess
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from components.metrics import render_metrics
from components.charts import render_charts
from components.contact_table import render_contact_table
import config

st.set_page_config(
    page_title="Outreach AI Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom Styles
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .block-container { padding-top: 2rem; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# State Management
if 'scheduler_proc' not in st.session_state:
    st.session_state.scheduler_proc = None

# Helper Functions
def load_data():
    """Load application log using the robust logger module."""
    from modules.logger import ApplicationLogger
    log_file = PROJECT_ROOT / "logs" / "application_log.csv"
    logger = ApplicationLogger(log_file)
    return logger.load_log()

def run_cli_command(args, wait=True):
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py")] + args
    if wait:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_ROOT)
        if "send" in args or "followup" in args:
            proc.stdin.write("yes\n")
            proc.stdin.flush()
        out, _ = proc.communicate()
        return out
    else:
        # For non-waiting commands like scheduler
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_ROOT)
        return proc

# Sidebar
with st.sidebar:
    st.title("🤖 Outreach AI")
    st.markdown("Automated Career Growth")
    st.divider()
    
    view = st.radio("Navigation", ["Dashboard", "Automation", "Templates", "Settings"])
    
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.rerun()

# --- Dashboard View ---
if view == "Dashboard":
    st.title("📊 Campaign Overview")
    df = load_data()
    
    if df.empty:
        st.warning("Welcome! Start by initializing your contacts in the Settings tab.")
    else:
        render_metrics(df)
        st.divider()
        render_charts(df)
        st.divider()
        render_contact_table(df)

# --- Automation View ---
elif view == "Automation":
    st.title("⚡ Automation Control Center")
    
    a1, a2 = st.columns(2)
    
    with a1:
        st.subheader("Scheduler Control")
        if st.session_state.scheduler_proc is None:
            st.info("Automation Scheduler is currently: **STOPPED**")
            if st.button("▶️ Start Scheduler", type="primary"):
                st.session_state.scheduler_proc = run_cli_command(["scheduler"], wait=False)
                st.success("Scheduler started in background.")
                time.sleep(1)
                st.rerun()
        else:
            st.success("Automation Scheduler is currently: **RUNNING**")
            if st.button("⏹️ Stop Scheduler", type="secondary"):
                st.session_state.scheduler_proc.terminate()
                st.session_state.scheduler_proc = None
                st.warning("Scheduler stopped.")
                time.sleep(1)
                st.rerun()

    with a2:
        st.subheader("Manual Triggers")
        limit = st.number_input("Batch Limit", min_value=1, max_value=50, value=5)
        m1, m2 = st.columns(2)
        if m1.button("Send Initial Batch"):
            with st.spinner("Processing Stage 1..."):
                out = run_cli_command(["send", "--limit", str(limit)])
                st.code(out)
        if m2.button("Trigger Follow-ups"):
            with st.spinner("Processing Stage 2..."):
                out = run_cli_command(["followup", "--limit", str(limit)])
                st.code(out)

    st.divider()
    st.subheader("📝 Activity Log (Last 50)")
    df = load_data()
    if not df.empty:
        log_df = df.sort_values(by='timestamp', ascending=False).head(50)
        st.dataframe(log_df[['timestamp', 'name', 'company', 'status', 'message']], use_container_width=True)

# --- Templates View ---
elif view == "Templates":
    st.title("✉️ Message Templates")
    
    t1, t2 = st.tabs(["Initial Outreach", "Follow-up Message"])
    
    with t1:
        path = PROJECT_ROOT / "templates" / "email_template.txt"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = st.text_area("Edit Stage 1 Template", value=content, height=400)
            if st.button("Save outreach.txt"):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                st.success("Saved!")
                
    with t2:
        path = PROJECT_ROOT / "templates" / "followup_template.txt"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = st.text_area("Edit Stage 2 Template", value=content, height=400)
            if st.button("Save followup.txt"):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                st.success("Saved!")

# --- Settings View ---
elif view == "Settings":
    st.title("⚙️ System Settings")
    
    s1, s2 = st.columns(2)
    
    with s1:
        st.subheader("Data Import")
        uploaded = st.file_uploader("Upload Recruitment List", type=['csv', 'xlsx', 'pdf'])
        if uploaded:
            save_path = PROJECT_ROOT / "data" / uploaded.name
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
            if st.button("Initialize Campaign"):
                out = run_cli_command(["init", "--input", str(save_path)])
                st.success("Initialized!")
                st.code(out)
                
    with s2:
        st.subheader("Campaign Health")
        rate_limiter = run_cli_command(["status"], wait=True)
        st.code(rate_limiter)
        
    st.divider()
    st.subheader("Environment Configuration")
    if os.path.exists(PROJECT_ROOT / ".env"):
        with open(PROJECT_ROOT / ".env", 'r') as f:
            st.text(f.read())
    else:
        st.error(".env file missing!")
