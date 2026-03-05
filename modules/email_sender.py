"""
Email Sender Module
Sends personalized emails with anti-spam protections:
- Template-based emails
- Resume attachment
- Subject randomization
- Resume filename randomization
- Account rotation
"""

import smtplib
import random
from pathlib import Path
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


class EmailSender:
    """Handles email sending with template support and anti-spam features."""
    
    def __init__(self, accounts, smtp_server, smtp_port, template_path, resume_path, subject_templates):
        """
        Initialize email sender.
        
        Args:
            accounts (list): List of email account dicts with 'address' and 'password'
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
            template_path (str): Path to email template file
            resume_path (str): Path to resume PDF
            subject_templates (list): List of subject line templates
        """
        self.accounts = accounts
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.template_path = template_path
        self.resume_path = resume_path
        self.subject_templates = subject_templates
        
        # Validate
        self.resume_path = Path(resume_path)
        self.template_path = Path(template_path)
        
        if not self.accounts:
            raise ValueError("No email accounts configured")
        if not self.resume_path.exists():
            raise FileNotFoundError(f"Resume not found: {self.resume_path}")
        if not self.template_path.exists():
            raise FileNotFoundError(f"Email template not found: {self.template_path}")
    
    def _load_template(self):
        """Load email template from file."""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _personalize_content(self, template, name, company, personalized_line=""):
        """Replace placeholders in template with actual values."""
        content = template.replace('{name}', name)
        content = content.replace('{company}', company)
        content = content.replace('{personalized_line}', personalized_line)
        return content
    
    def _generate_personalized_line(self, company):
        """Generate a micro-personalized invitation line for the company."""
        templates = [
            "I recently came across {company} and was particularly interested in the work your team is doing.",
            "I noticed that {company} operates in an environment where strong cybersecurity practices are essential.",
            "I came across {company} while researching organizations focused on technology and security.",
            "I was exploring companies working in innovative tech environments and {company} stood out to me.",
            "I noticed the work happening at {company} and wanted to reach out regarding potential opportunities."
        ]
        return random.choice(templates).format(company=company)

    def _get_random_subject(self, company):
        """Get a random subject line from templates."""
        template = random.choice(self.subject_templates)
        return template.format(company=company)
    
    def _get_randomized_resume_path(self):
        """Create a copy of resume with randomized filename."""
        # Generate random number
        random_num = random.randint(1000, 9999)
        
        # Get base name and extension using pathlib
        base_name = self.resume_path.stem
        ext = self.resume_path.suffix
        
        # Create new filename
        new_filename = f"{base_name}_{random_num}{ext}"
        new_path = self.resume_path.parent / new_filename
        
        # Copy file
        shutil.copy2(self.resume_path, new_path)
        
        return new_path, new_filename
    
    def send_email(self, to_email, name, company, account_index=0):
        """
        Send a personalized email with resume attachment.
        
        Args:
            to_email (str): Recipient email address
            name (str): Recipient name
            company (str): Company name
            account_index (int): Index of sender account to use
            
        Returns:
            dict: Result with 'success' boolean and 'message' string
        """
        try:
            # Get sender account
            if account_index >= len(self.accounts):
                account_index = 0
            
            sender_account = self.accounts[account_index]
            sender_email = sender_account['address']
            sender_password = sender_account['password']
            
            print(f"\nSending email to: {name} ({to_email})")
            print(f"Using sender account: {sender_email}")
            
            # Load and personalize template
            template = self._load_template()
            
            # Generate personalized line
            personalized_line = self._generate_personalized_line(company)
            
            # Extract subject from template (first line after "Subject:")
            lines = template.split('\n')
            subject_line = None
            body_start = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('Subject:'):
                    subject_line = line.replace('Subject:', '').strip()
                    body_start = i + 1
                    break
            
            if not subject_line:
                # Use random subject if not in template
                subject = self._get_random_subject(company)
            else:
                # Personalize subject from template
                subject = self._personalize_content(subject_line, name, company, personalized_line)
            
            # Get body (everything after subject line)
            body_template = '\n'.join(lines[body_start:])
            body = self._personalize_content(body_template, name, company, personalized_line)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach resume with randomized filename
            randomized_resume_path, randomized_filename = self._get_randomized_resume_path()
            
            try:
                with open(randomized_resume_path, 'rb') as f:
                    resume_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    resume_attachment.add_header('Content-Disposition', 'attachment', 
                                                filename=randomized_filename)
                    msg.attach(resume_attachment)
                
                print(f"Attached resume as: {randomized_filename}")
            finally:
                # Clean up randomized copy
                if randomized_resume_path.exists():
                    randomized_resume_path.unlink()
            
            # Connect to SMTP server and send
            if self.smtp_port == 465:
                # SSL connection
                server_class = smtplib.SMTP_SSL
            else:
                # STARTTLS connection
                server_class = smtplib.SMTP
            
            with server_class(self.smtp_server, self.smtp_port) as server:
                if self.smtp_port != 465:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"[OK] Email sent successfully!")
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'sender': sender_email,
                'subject': subject
            }
        
        except smtplib.SMTPAuthenticationError:
            error_msg = f"Authentication failed for {sender_email}. Check credentials."
            print(f"[ERROR] {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'auth'
            }
        
        except smtplib.SMTPException as e:
            error_msg = str(e)
            if "Too many messages" in error_msg or "Rate limit exceeded" in error_msg or "421" in error_msg:
                print(f"[WARN] Rate limit hit on {sender_email}: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'error_type': 'rate_limit'
                }
            print(f"[ERROR] SMTP Error: {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'smtp'
            }
        
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'other'
            }


if __name__ == "__main__":
    # This module requires configuration from config.py
    print("Email Sender Module - Use via main.py")
