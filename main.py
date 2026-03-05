"""
Main Script for Job Mail Automation System
Orchestrates the entire workflow:
1. Parse input files
2. Send personalized emails
3. Apply anti-spam protections
4. Monitor inbox for bounces and replies
5. Update status logs
"""

import sys
import os
import argparse
from pathlib import Path
from modules.input_parser import parse_input_file, load_contacts
from modules.email_sender import EmailSender
from modules.inbox_monitor import InboxMonitor
from modules.rate_limiter import RateLimiter
from modules.logger import ApplicationLogger
from datetime import datetime
import config


def validate_email(email):
    """Simple email validation regex."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None


def check_environment():
    """Verify that environment is correctly configured."""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️ Environment not configured. Please copy .env.example to .env and fill your email credentials.")
        return False
    
    # Check both formats
    emails = os.getenv('SENDER_EMAILS')
    if not emails:
        # Fallback to single account
        email = os.getenv('EMAIL_ADDRESS') or os.getenv('EMAIL_ADDRESS_1')
        password = os.getenv('EMAIL_PASSWORD') or os.getenv('EMAIL_PASSWORD_1')
    else:
        email = emails
        password = os.getenv('SENDER_PASSWORDS')
    
    if not email or not password:
        print("⚠️ Environment not configured. Please fill SENDER_EMAILS and SENDER_PASSWORDS in .env.")
        return False
    
    return True


def run_setup():
    """Run first-time setup validation."""
    print("\n" + "="*60)
    print("RUNNING SYSTEM SETUP")
    print("="*60)
    
    # 1. Verify dependencies
    print("\n1. Verifying dependencies...")
    try:
        import pandas
        import dotenv
        import pdfplumber
        import openpyxl
        import xlrd
        print("   [OK] Dependencies verified.")
    except ImportError as e:
        print(f"   [ERROR] Missing dependency: {e.name}")
        print("     Please run: pip install -r requirements.txt")
        return
    
    # 2. Check .env file
    print("\n2. Checking .env file...")
    if check_environment():
        print(f"   [OK] .env file is configured ({len(config.EMAIL_ACCOUNTS)} accounts found).")
    else:
        return
        
    # 3. Check resume/Aniket_Rai_Resume.pdf exists
    print("\n3. Checking resume...")
    if config.RESUME_PATH.exists():
        print(f"   [OK] Resume found at: {config.RESUME_PATH}")
    else:
        print(f"   [ERROR] Resume NOT found at: {config.RESUME_PATH}")
        print("     Please place Aniket_Rai_Resume.pdf in the resume/ directory.")
    
    # 4. Check templates
    print("\n4. Checking templates...")
    if config.EMAIL_TEMPLATE.exists():
        print(f"   [OK] Email template found: {config.EMAIL_TEMPLATE}")
    else:
        print(f"   [ERROR] Email template NOT found.")

    if config.FOLLOWUP_TEMPLATE.exists():
        print(f"   [OK] Follow-up template found: {config.FOLLOWUP_TEMPLATE}")
    else:
        print(f"   [!] Follow-up template NOT found.")
        
    # 5. Logs
    print("\n5. Checking application log...")
    logger = ApplicationLogger(config.APPLICATION_LOG)
    if config.APPLICATION_LOG.exists():
        print(f"   [OK] Application log exists.")
    else:
        print(f"   [OK] Created application log.")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)


def send_batch(contacts, template_path, limit, status_after, stage=None):
    """Common logic for sending a batch of emails with progress output."""
    import time
    logger = ApplicationLogger(config.APPLICATION_LOG)
    rate_limiter = RateLimiter(
        max_daily=config.MAX_EMAILS_PER_DAY,
        min_delay=config.MIN_DELAY_SECONDS,
        max_delay=config.MAX_DELAY_SECONDS
    )
    
    status = rate_limiter.get_status()
    if not status['can_send']:
        print(f"\n[ERROR] Daily email limit reached ({config.MAX_EMAILS_PER_DAY})")
        return 0
    
    # Initialize email sender
    try:
        sender = EmailSender(
            accounts=config.EMAIL_ACCOUNTS,
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            template_path=template_path,
            resume_path=config.RESUME_PATH,
            subject_templates=config.SUBJECT_TEMPLATES
        )
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return 0
    
    total_to_send = min(len(contacts), limit, status['emails_remaining'])
    batch = contacts.head(total_to_send)
    
    if total_to_send == 0:
        print("\nNo contacts to process in this batch.")
        return 0

    print(f"\nPreparing to send {total_to_send} emails (Stage {stage if stage else 'Unknown'})...")
    
    # Confirm (Only if not in scheduler mode - we check sys.argv)
    if 'scheduler' not in sys.argv:
        response = input(f"Proceed? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            return 0
    
    sent_count = 0
    current_idx = 0
    
    for idx, row in batch.iterrows():
        current_idx += 1
        
        # 1. Validate Email
        if not validate_email(row['email']):
            print(f"[{current_idx}/{total_to_send}] [ERROR] Invalid email: {row['email']}")
            logger.update_status(row['email'], config.STATUS_INVALID, message="Invalid format")
            continue

        # 2. Check Daily Limit
        if not rate_limiter.can_send_email():
            print(f"\n[{current_idx}/{total_to_send}] [ERROR] Daily limit reached.")
            break
            
        # 3. Apply Delay
        if sent_count > 0:
            rate_limiter.apply_delay()
            
        # 4. Account Rotation
        account_idx = rate_limiter.get_next_account_index(len(config.EMAIL_ACCOUNTS))
        sender_email = config.EMAIL_ACCOUNTS[account_idx]['address']
        
        # 5. Send
        result = sender.send_email(row['email'], row['name'], row['company'], account_idx)
        
        if result['success']:
            logger.update_status(
                row['email'], 
                status_after, 
                sender_account=sender_email, 
                message=f"Stage {stage} Sent", 
                stage=stage
            )
            rate_limiter.record_email_sent()
            sent_count += 1
            print(f"[{current_idx}/{total_to_send}] SENT: {row['email']} via {sender_email}")
        else:
            if result.get('error_type') == 'rate_limit':
                print(f"[WARN] Throttled on {sender_email}. Pausing {config.THROTTLE_PAUSE_MINUTES}m...")
                time.sleep(config.THROTTLE_PAUSE_MINUTES * 60)
                continue
            elif result.get('error_type') == 'auth':
                print(f"[ERROR] Auth failure: {sender_email}")
                continue
            else:
                print(f"[ERROR] Error: {result['message']}")
                logger.update_status(row['email'], config.STATUS_INVALID, sender_account=sender_email, message=result['message'])

    return sent_count


def send_emails(limit=5, test_n=None):
    """Stage 1 outreach."""
    logger = ApplicationLogger(config.APPLICATION_LOG)
    pending = logger.get_pending_contacts()
    
    if pending.empty:
        if 'scheduler' not in sys.argv:
            print("\nNo pending contacts.")
        return 0
        
    actual_limit = test_n if test_n else limit
    return send_batch(pending, config.EMAIL_TEMPLATE, actual_limit, config.STATUS_SENT, stage=1)


def send_followups(limit=5):
    """Stage 2 follow-ups (after 7 days)."""
    logger = ApplicationLogger(config.APPLICATION_LOG)
    needing_followup = logger.get_followup_eligible_contacts(days_ago=7)
    
    if needing_followup.empty:
        if 'scheduler' not in sys.argv:
            print(f"\nNo contacts eligible for 7-day follow-up.")
        return 0
        
    print(f"Found {len(needing_followup)} contacts eligible for Stage 2.")
    return send_batch(needing_followup, config.FOLLOWUP_TEMPLATE, limit, config.STATUS_FOLLOWUP_SENT, stage=2)


def update_no_response():
    """Stage 3: Move to no_response after 14 days total (7 days after follow-up)."""
    logger = ApplicationLogger(config.APPLICATION_LOG)
    eligible = logger.get_no_response_eligible_contacts(days_ago=7)
    
    if not eligible.empty:
        emails = eligible['email'].tolist()
        logger.bulk_update_status(emails, config.STATUS_NO_RESPONSE, message="No response after 14 days")
        print(f"Moved {len(emails)} contacts to 'no_response' status.")
        return len(emails)
    return 0


def monitor_inbox():
    """Monitor for replies to stop automation."""
    if not check_environment():
        return

    logger = ApplicationLogger(config.APPLICATION_LOG)
    log_df = logger.load_log()
    
    # We care about anyone who was sent something and didn't reply yet
    active_mask = log_df['status'].isin([config.STATUS_SENT, config.STATUS_FOLLOWUP_SENT])
    active_emails = log_df[active_mask]['email'].tolist()
    
    if not active_emails:
        return
    
    all_bounces = []
    all_replies = []
    
    for account in config.EMAIL_ACCOUNTS:
        try:
            monitor = InboxMonitor(
                email_address=account['address'],
                password=account['password'],
                imap_server=config.IMAP_SERVER,
                bounce_keywords=config.BOUNCE_KEYWORDS
            )
            
            bounces = monitor.check_for_bounces(active_emails, days_back=14)
            all_bounces.extend(bounces)
            
            replies = monitor.check_for_replies(active_emails, days_back=14)
            all_replies.extend(replies)
        except Exception as e:
            print(f" [ERROR] Inbox Error ({account['address']}): {e}")
    
    if all_bounces:
        logger.bulk_update_status(list(set(all_bounces)), config.STATUS_BOUNCE, message="Bounce detected")
    
    if all_replies:
        logger.bulk_update_status(list(set(all_replies)), config.STATUS_REPLIED, message="Reply received")


def run_scheduler():
    """Run automated campaign lifecycle."""
    import time
    print("\n" + "="*60)
    print("CAMPAIGN SCHEDULER STARTED")
    print("="*60)
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running automation cycle...")
            
            # 1. Sync Replies/Bounces
            monitor_inbox()
            
            # 2. Stage 3: Clean up no-responses
            update_no_response()
            
            # 3. Stage 2: Follow-ups
            send_followups(limit=10)
            
            # 4. Stage 1: Initial outreach
            send_emails(limit=10)
            
            print(f"\nCycle complete. Sleeping for 30 minutes...")
            time.sleep(30 * 60)
            
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


def initialize_from_file(input_file):
    """Parse input file and initialize contact database."""
    print("\n" + "="*60)
    print("INITIALIZING FROM INPUT FILE")
    print("="*60)
    
    from modules.input_parser import parse_input_file
    import config
    
    # Parse input file
    contacts_df = parse_input_file(input_file, config.CONTACTS_CSV)
    
    # Initialize logger
    logger = ApplicationLogger(config.APPLICATION_LOG)
    logger.initialize_contacts(contacts_df)
    
    print("\n[OK] Initialization complete!")
    print(f"  Contacts database updated: {config.APPLICATION_LOG}")


def show_status():
    """Show current status."""
    print("\n" + "="*60)
    print("CAMPAIGN STATUS")
    print("="*60)
    
    rate_limiter = RateLimiter()
    limit_status = rate_limiter.get_status()
    
    print(f"\nDaily Progress: {limit_status['emails_sent_today']}/{limit_status['max_daily']}")
    
    logger = ApplicationLogger(config.APPLICATION_LOG)
    counts = logger.get_status_counts()
    
    print("\nOutreach Breakdown:")
    for s, c in counts.items():
        print(f"  {s:15}: {c}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Automated Outreach Lifecycle')
    
    parser.add_argument('action', choices=['setup', 'init', 'send', 'followup', 'monitor', 'status', 'scheduler'])
    parser.add_argument('--input', help='Input file for init')
    parser.add_argument('--limit', type=int, default=5, help='Limit per run')
    parser.add_argument('--test', type=int, help='Test N contacts')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        run_setup()
    elif not check_environment():
        sys.exit(1)
    elif args.action == 'init':
        if not args.input:
            print("ERROR: --input required")
            sys.exit(1)
        initialize_from_file(args.input)
    elif args.action == 'send':
        send_emails(limit=args.limit, test_n=args.test)
    elif args.action == 'followup':
        send_followups(limit=args.limit)
    elif args.action == 'monitor':
        monitor_inbox()
    elif args.action == 'status':
        show_status()
    elif args.action == 'scheduler':
        run_scheduler()


if __name__ == "__main__":
    main()
