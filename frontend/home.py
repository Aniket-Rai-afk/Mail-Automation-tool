import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import os
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

# Import existing dashboard components
from dashboard import load_data, run_cli_command
from components.metrics import render_metrics
from components.charts import render_charts
from components.contact_table import render_contact_table
import config

st.set_page_config(
    page_title="Job Outreach AI | High-Scale Job Search",
    page_icon="🚀",
    layout="wide"
)

# --- Custom Styling for SaaS Feel ---
st.markdown("""
<style>
    /* Main Background and Container */
    .main { background-color: #ffffff; }
    
    /* Hero Section */
    .hero-container {
        padding: 100px 0;
        text-align: center;
        background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%);
        border-radius: 0 0 50px 50px;
        margin-bottom: 50px;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        color: #64748b;
        max-width: 800px;
        margin: 0 auto 40px auto;
    }
    
    /* Feature Cards */
    .feature-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 15px;
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 10px;
    }
    .feature-desc {
        color: #64748b;
        font-size: 0.95rem;
    }
    
    /* Step Cards */
    .step-card {
        padding: 20px;
        border-left: 4px solid #3b82f6;
        background-color: #f8fafc;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- Navigation Sidebar ---
with st.sidebar:
    st.title("🤖 Outreach Manager")
    nav = st.radio("Navigation", ["Home", "Dashboard", "Automation", "Templates", "Campaign Setup"])
    
    st.divider()
    status_df = load_data()
    if not status_df.empty:
        # Guidance Logic
        pending = len(status_df[status_df['status'] == 'pending'])
        sent = len(status_df[status_df['status'] == 'sent'])
        followups = len(status_df[status_df['status'] == 'followup_sent'])
        
        st.subheader("🎯 Current Task")
        if pending > 0:
            st.info(f"**Step 2: Start Outreach**\nYou have {pending} pending contacts ready to engage.")
        elif sent > 0 or followups > 0:
            st.success("**Step 3: Monitor & Automate**\nYour campaign is active. Keep the Scheduler running!")
        else:
            st.warning("**Step 1: Setup Campaign**\nImport your recruiter contact list to begin.")
        
        st.divider()
        st.metric("Total Contacts", len(status_df))
        replies = len(status_df[status_df['status'] == 'replied'])
        st.metric("Total Replies", replies, delta=f"{replies} new" if replies > 0 else 0)

# --- HOME PAGE ---
if nav == "Home":
    # 1. Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Automated Job Outreach Platform</h1>
        <p class="hero-subtitle">
            A smart automation engine for your job search. We handle the scale, you handle the interviews.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        ### 🚀 Simple 3-Step Success
        1. **Campaign Setup**: Upload your recruiter list (CSV/PDF/XLSX).
        2. **Templates**: Personalize your outreach and follow-up messages.
        3. **Automation**: Start the **Scheduler** to put your outreach on 24/7 autopilot.
        """)
        if st.button("Get Started Now", type="primary", use_container_width=True):
            st.info("👈 Use the sidebar to go to **Campaign Setup**.")

    st.markdown("---")
    
    # 2. Features Section
    st.subheader("🛠️ Why use this tool?")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">24/7 Scheduler</div>
            <div class="feature-desc">The Scheduler automatically syncs replies, sends follow-ups, and manages batches every 30 minutes.</div>
        </div>
        """, unsafe_allow_html=True)

    with f_col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Micro-Personalization</div>
            <div class="feature-desc">Dynamically generates a unique line for every company to ensure your emails feel human and unique.</div>
        </div>
        """, unsafe_allow_html=True)

    with f_col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Anti-Spam Shield</div>
            <div class="feature-desc">Rotates through multiple sender accounts and randomizes delays to keep your accounts safe.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Campaign Visual Section
    st.subheader("💡 The Campaign Lifecycle")
    st.image("https://mermaid.ink/img/pako:eNptkEELwjAMRv_KCOfSbe7idS8iDvSizLWG2-rSFmSU_Xc3U8d8XEI-8uVNIDtO2CiafG12E6YAnZ0SiaVf6HhBlyxL18mG92QvL3XjB-Pj8AnYis8P9SId79-wH8G7F_83nCHvGz4vG8G7l2BfP_X0m6uE1Ggh-8v_WjWh0VogeyT_vGrSNo3yD1UuYfE", use_container_width=True)

# --- ROUTING TO DASHBOARD CONTENT ---
elif nav == "Dashboard":
    st.title("📊 Campaign Analytics")
    df = load_data()
    if df.empty:
        st.warning("No data found. First, go to **Campaign Setup** to import contacts.")
    else:
        render_metrics(df)
        st.divider()
        render_charts(df)
        st.divider()
        render_contact_table(df)

elif nav == "Automation":
    st.title("⚡ Automation Control Center")
    
    # Detailed Explanation of Scheduler
    with st.expander("❓ What does the Scheduler do?", expanded=True):
        st.markdown("""
        The **Automated Scheduler** is the brain of your outreach. When running:
        *   **📩 Syncs Responses**: Checks your inbox and marks contacts as 'Replied' so automation stops for them.
        *   **🚀 Sends Outreach**: Engages 'Pending' contacts in safe, randomized batches.
        *   **🔁 Handles Follow-ups**: Detects contacts sent 7 days ago and sends a Stage 2 follow-up.
        *   **🧹 Clean Up**: After 14 days of no response, marks contacts as 'Finished' to keep your pipeline clean.
        
        **Use Case:** Start it at the beginning of your day and let it handle 100% of your job search engagement!
        """)

    a_col1, a_col2 = st.columns(2)
    with a_col1:
        st.subheader("Scheduler Control")
        if st.session_state.get('scheduler_proc') is None:
            st.warning("Status: **OFFLINE**")
            if st.button("▶️ ACTIVATE SCHEDULER", type="primary", use_container_width=True):
                st.session_state.scheduler_proc = run_cli_command(["scheduler"], wait=False)
                st.success("Scheduler is now managing your campaign.")
                time.sleep(1)
                st.rerun()
        else:
            st.success("Status: **ACTIVE & MONITORING**")
            if st.button("⏹️ DEACTIVATE SCHEDULER", use_container_width=True):
                st.session_state.scheduler_proc.terminate()
                st.session_state.scheduler_proc = None
                st.warning("Automated tasks paused.")
                time.sleep(1)
                st.rerun()

    with a_col2:
        st.subheader("Manual Control")
        limit = st.number_input("Batch Limit", 1, 50, 5)
        m1, m2 = st.columns(2)
        if m1.button("Send Outreach Now", use_container_width=True):
            with st.spinner("Processing Stage 1..."):
                st.code(run_cli_command(["send", "--limit", str(limit)]))
        if m2.button("Send Follow-ups Now", use_container_width=True):
            with st.spinner("Processing Stage 2..."):
                st.code(run_cli_command(["followup", "--limit", str(limit)]))

    st.divider()
    df = load_data()
    if not df.empty:
        st.subheader("🕒 Recent Activity History")
        st.dataframe(df.sort_values(by='timestamp', ascending=False).head(20), use_container_width=True)

elif nav == "Templates":
    st.title("📝 Message Customization")
    st.info("Personalize these templates to match your professional tone. Use `{name}` and `{company}` as placeholders.")
    
    t1, t2 = st.tabs(["[Stage 1] Primary Outreach", "[Stage 2] 7-Day Follow-up"])
    with t1:
        path = PROJECT_ROOT / "templates" / "email_template.txt"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            new = st.text_area("Initial Email Content", value=content, height=450)
            if st.button("Save outreach.txt", type="primary"):
                with open(path, 'w', encoding='utf-8') as f: f.write(new)
                st.success("Primary template updated!")
    with t2:
        path = PROJECT_ROOT / "templates" / "followup_template.txt"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            new = st.text_area("Follow-up Email Content", value=content, height=450)
            if st.button("Save followup.txt", type="primary"):
                with open(path, 'w', encoding='utf-8') as f: f.write(new)
                st.success("Follow-up template updated!")

elif nav == "Campaign Setup":
    st.title("⚙️ Campaign Setup")
    
    # Guide for this specific step
    st.success("""
    **Getting Started?** 
    1. Upload your file below.
    2. Click 'Run Setup Check' to verify your Gmail credentials.
    3. Click 'Initialize Campaign' to load the contacts!
    """)
    
    u1, u2 = st.columns([2, 1])
    with u1:
        uploaded = st.file_uploader("Upload recruiter list (PDF, CSV, XLSX)", type=['pdf', 'csv', 'xlsx'])
        if uploaded:
            save_path = PROJECT_ROOT / "data" / uploaded.name
            with open(save_path, "wb") as f: f.write(uploaded.getbuffer())
            if st.button("Initialize Campaign Data", type="primary", use_container_width=True):
                out = run_cli_command(["init", "--input", str(save_path)])
                st.success("✅ Contacts Loaded Successfully!")
                st.balloons()
                st.markdown("""
                ### 🎯 Your next move:
                The contacts are now in your system. Go to the **Automation** tab and click **▶️ ACTIVATE SCHEDULER** 
                to start reaching out to them automatically.
                """)
                st.code(out)
    
    with u2:
        st.subheader("System Health")
        if st.button("Verify System Setup", use_container_width=True):
            st.code(run_cli_command(["setup"]))
        
    st.divider()
    st.subheader("System Status Summary")
    st.code(run_cli_command(["status"]))
