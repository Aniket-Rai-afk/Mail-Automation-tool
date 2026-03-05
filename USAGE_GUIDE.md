# Complete Usage Guide

## Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
cd job-mail-automation
pip install -r requirements.txt --break-system-packages
```

### Step 2: Configure Email Account

```bash
cp .env.example .env
nano .env  # Or use any text editor
```

Add your Gmail credentials:
```env
EMAIL_ADDRESS_1=yourname@gmail.com
EMAIL_PASSWORD_1=your-16-char-app-password
```

**Getting Gmail App Password:**
1. Visit: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Click "App passwords"
4. Generate password for "Mail"
5. Copy the 16-character code

### Step 3: Add Your Resume

```bash
cp /path/to/your/resume.pdf resume/resume.pdf
```

### Step 4: Initialize Contacts

```bash
python main.py init --input your_contacts.pdf
```

### Step 5: Send Emails

Test with 3 contacts first:
```bash
python main.py send --test 3
```

Then send to all:
```bash
python main.py send
```

---

## Detailed Workflow

### Day 1: Setup and First Batch

```bash
# 1. Parse your HR contact list
python main.py init --input CompanyWise_HR_contact.pdf

# 2. Check what was parsed
python main.py status

# Output will show:
# Rate Limiter:
#   Emails sent today: 0/80
#   Emails remaining: 80
# 
# Application Status:
#   pending: 1781

# 3. Test with small batch
python main.py send --test 5

# 4. Review results
python main.py status

# 5. Send more (or continue to daily limit)
python main.py send
```

### Day 2: Monitor and Continue

```bash
# 1. Check for bounces and replies
python main.py monitor

# This will update statuses automatically:
# - Bounced emails → status: bounce
# - Received replies → status: replied

# 2. View updated statistics
python main.py status

# Output might show:
# Application Status:
#   pending: 1701
#   sent: 75
#   bounce: 3
#   replied: 2

# 3. Send next batch
python main.py send
```

### Ongoing: Daily Routine

```bash
# Every day:
python main.py monitor    # Check inbox
python main.py send       # Send to remaining contacts
python main.py status     # Review progress
```

---

## Command Reference

### `python main.py init --input FILE`

**Purpose**: Parse contact file and create database

**Arguments**:
- `--input FILE`: Path to PDF/CSV/XLSX/XLS file

**Example**:
```bash
python main.py init --input contacts.pdf
python main.py init --input contacts.xlsx
```

**Output**:
- Creates `data/contacts.csv`
- Creates `logs/application_log.csv`
- Shows number of contacts extracted

---

### `python main.py send`

**Purpose**: Send emails to pending contacts

**Options**:
- `--test N`: Send only to first N contacts (testing)

**Examples**:
```bash
# Send to all pending contacts
python main.py send

# Test with 10 contacts
python main.py send --test 10
```

**Behavior**:
- Checks daily limit (stops at 80/day)
- Applies random 45-120 second delays
- Rotates between sender accounts
- Updates status log
- Shows confirmation prompt before sending

**What it does**:
1. Loads pending contacts
2. Checks if daily limit allows sending
3. Asks for confirmation
4. For each contact:
   - Waits random delay (45-120s)
   - Selects next sender account
   - Personalizes email template
   - Attaches resume with random filename
   - Sends email
   - Updates status to 'sent'

---

### `python main.py monitor`

**Purpose**: Check inbox for bounces and replies

**No arguments needed**

**Example**:
```bash
python main.py monitor
```

**Behavior**:
- Connects to all configured email accounts
- Checks last 7 days of emails
- Detects bounced emails
- Detects replies from HR contacts
- Updates status log automatically

**Detection Logic**:
- **Bounces**: Emails with subjects like "Delivery Status Notification", "Undelivered Mail"
- **Replies**: Emails FROM addresses in your contact list

---

### `python main.py status`

**Purpose**: Show campaign statistics

**No arguments needed**

**Example**:
```bash
python main.py status
```

**Output**:
```
Rate Limiter:
  Emails sent today: 45/80
  Emails remaining: 35
  Last reset: 2024-03-05

Application Status:
  pending: 1650
  sent: 120
  bounce: 8
  replied: 3

Ready to send: 1650 emails
```

---

## Tips and Best Practices

### Starting Out

1. **Test First**: Always use `--test 5` or `--test 10` before full run
2. **Check Spam**: Send a test to yourself, check if it lands in spam
3. **Personalize Template**: More personal = less spam
4. **Warm Up Account**: If new email account, send 10-20/day for first week

### During Campaign

1. **Monitor Daily**: Run `monitor` every 24 hours
2. **Don't Rush**: Spread emails over days/weeks
3. **Watch Bounce Rate**: >5% bounces? Your list might have bad emails
4. **Response Rate**: Track replies, adjust template if low

### Troubleshooting

**"Authentication failed"**
- Using App Password? (not regular password)
- 2-Step Verification enabled?
- Correct email in .env file?

**"Daily limit reached"**
- Wait until tomorrow
- Or add more sender accounts

**High bounce rate**
- Your contact list might have outdated emails
- Filter and clean your input file

**Emails going to spam**
- Reduce sending rate (send 40/day instead of 80)
- Personalize template more
- Use multiple sender accounts
- Check your domain reputation

---

## File Structure Reference

```
job-mail-automation/
├── data/
│   └── contacts.csv              # Generated from input file
│
├── logs/
│   ├── application_log.csv       # Status tracking (pending/sent/bounce/replied)
│   └── rate_limiter_state.json   # Daily counter and account rotation state
│
├── resume/
│   └── resume.pdf                # YOUR resume (you add this)
│
├── templates/
│   └── email_template.txt        # Email template (customize this)
│
├── modules/                      # Code modules (don't modify)
│
├── main.py                       # Main script
├── config.py                     # Configuration
├── .env                          # YOUR credentials (don't commit)
└── README.md                     # Documentation
```

---

## Configuration Options

Edit `config.py` to adjust:

```python
# Daily send limit
MAX_EMAILS_PER_DAY = 80

# Delay range (seconds)
MIN_DELAY_SECONDS = 45
MAX_DELAY_SECONDS = 120

# Subject templates (add more!)
SUBJECT_TEMPLATES = [
    "Opportunity Inquiry at {company}",
    "Checking opportunities at {company}",
    "Quick question regarding roles at {company}",
    # Add your variations here
]
```

---

## Advanced: Multiple Sender Accounts

Using 3 accounts significantly reduces spam risk:

**.env file:**
```env
EMAIL_ADDRESS_1=account1@gmail.com
EMAIL_PASSWORD_1=app-password-1

EMAIL_ADDRESS_2=account2@gmail.com
EMAIL_PASSWORD_2=app-password-2

EMAIL_ADDRESS_3=account3@gmail.com
EMAIL_PASSWORD_3=app-password-3
```

**Benefits**:
- Each account sends ~27 emails/day (instead of 80)
- Better deliverability
- If one account gets limited, others continue
- More natural sending pattern

---

## Monitoring Results

### Interpreting Status Counts

```
pending: 1650   # Not yet contacted
sent: 120       # Successfully sent
bounce: 8       # Invalid emails (6.6% bounce rate - acceptable)
replied: 3      # Got responses (2.5% response rate)
```

**Bounce Rate**: 8/120 = 6.6%
- <5%: Excellent
- 5-10%: Acceptable
- >10%: List quality issue

**Response Rate**: 3/120 = 2.5%
- 1-3%: Normal for cold outreach
- 3-5%: Good
- >5%: Excellent

---

## Safety Checklist

Before running for real:

- [ ] Using App Password (not regular password)
- [ ] Tested with `--test 5` first
- [ ] Sent test email to yourself
- [ ] Checked test email not in spam
- [ ] Resume PDF in resume/ folder
- [ ] Personalized email template
- [ ] Have 2+ sender accounts (recommended)

---

## Getting Help

**Check these in order:**

1. Error message in terminal
2. This guide
3. README.md
4. `logs/application_log.csv` for status details

**Common solutions:**
- Clear error? Follow the message
- "Authentication failed"? Check App Password setup
- Emails not sending? Run with `--test 1` and watch output
- Status not updating? Check `logs/application_log.csv` permissions

---

## Example: Complete First Run

```bash
# Setup (one time)
cd job-mail-automation
pip install -r requirements.txt --break-system-packages
cp .env.example .env
nano .env  # Add your credentials
cp ~/my_resume.pdf resume/resume.pdf

# Initialize
python main.py init --input ~/Downloads/HR_contacts.pdf
# Output: Extracted 1781 contacts

# Test
python main.py send --test 3
# Sends 3 emails, watch for errors

# Check results
python main.py status
# Shows: sent: 3, pending: 1778

# Send daily batch
python main.py send
# Sends up to 80 emails

# Next day: monitor and continue
python main.py monitor
python main.py send
```

You now have a complete, production-ready job outreach automation system!
