# 📧 Automated Job Outreach Platform

A powerful, automated job outreach engine designed to help candidates connect with recruiters at scale. This tool automates the entire outreach lifecycle, from initial touchpoints to smart follow-ups, with built-in anti-spam protections and a modern Streamlit-based control center.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.30%2B-FF4B4B.svg)

## 🚀 Core Features

- **Automated 3-Stage Campaign**:
  - **Stage 1**: Professional initial outreach.
  - **Stage 2**: Automated follow-up after 7 days (if no response).
  - **Stage 3**: Automated campaign completion after 14 days.
- **Smart Micro-Personalization**: Dynamically generates unique introductory lines for every company to ensure your emails feel human and personal.
- **Anti-Spam Shield**:
  - **Account Rotation**: Support for multiple sender Gmail accounts.
  - **Randomized Delays**: Mimics human behavior with variable delays between sends.
  - **Rate Limiting**: Daily sending caps to protect your accounts from being flagged.
- **Reply & Bounce Detection**: Automatically monitors your inbox via IMAP to stop outreach the moment a recruiter replies or a bounce is detected.
- **Interactive Dashboard**:
  - **Campaign Analytics**: Track total sends, replies, and active statuses visually.
  - **Contact Management**: Filter and search through your contact list with real-time status updates.
  - **Live Automation Control**: Start/Stop the background scheduler or trigger manual batches.
- **Support for Multi-Format Import**: Built-in parsers for PDF, CSV, and XLSX recruiter lists.

---

## 🏗️ Project Structure

```text
Mail-Automation-tool/
├── frontend/             # Streamlit UI Components
│   ├── home.py           # Main Entry Point (Landing Page)
│   ├── dashboard.py      # Analytics & Control Hub
│   └── components/       # Modular UI blocks
├── modules/              # Core Logic
│   ├── email_sender.py   # Multi-account SMTP engine
│   ├── logger.py         # 3-Stage status tracking
│   ├── rate_limiter.py   # Anti-spam timing logic
│   └── input_parser.py   # PDF/CSV/XLSX readers
├── templates/            # Email content files
├── resume/               # Your Resume PDF
├── data/                 # Contact lists
├── main.py               # CLI Engine
├── config.py             # System Configurations
└── requirements.txt      # Dependencies
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.9 or higher.
- A Gmail account with **App Passwords** enabled (Standard Gmail passwords will not work).

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/Aniket-Rai-afk/Mail-Automation-tool.git
cd Mail-Automation-tool

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Open `.env` and fill in your Gmail accounts and credentials:
```env
SENDER_EMAILS=user1@gmail.com,user2@gmail.com
SENDER_PASSWORDS=your_app_pass_1,your_app_pass_2
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
IMAP_SERVER=imap.gmail.com
```

### 4. Running the Platform
Launch the modern dashboard:
```powershell
streamlit run frontend/home.py
```

---

## 💡 Usage Workflow

1. **Campaign Setup**: Go to the sidebar and select **Campaign Setup**. Upload your recruiter list (PDF/CSV/XLSX) and click **Initialize**.
2. **Setup Check**: Click **Verify System Setup** to ensure your credentials and templates are ready.
3. **Customize Templates**: Use the **Templates** tab to edit your message. Do not remove placeholders like `{name}`, `{company}`, or `{personalized_line}`.
4. **Launch Automation**: Go to the **Automation** tab and click **▶️ ACTIVATE SCHEDULER**. The system will now manage your entire job search in the background!

---

## ⚠️ Safety Warning
This tool is for professional outreach. Please respect daily Gmail limits (recommended < 50-100 emails/day total) and ensure your templates remain highly professional.

## 📄 License
Distributed under the MIT License. See `LICENSE` (to be added) for more information.

---
**Created with ❤️ by [Aniket Rai](https://aniket-rai-portfolio.netlify.app/)**
