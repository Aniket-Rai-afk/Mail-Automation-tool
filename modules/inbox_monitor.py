"""
Inbox Monitor Module
Monitors inbox for bounced emails and replies via IMAP.
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta


class InboxMonitor:
    """Monitors inbox for bounces and replies."""
    
    def __init__(self, email_address, password, imap_server, imap_port=993, bounce_keywords=None):
        """
        Initialize inbox monitor.
        
        Args:
            email_address (str): Email account to monitor
            password (str): Email password
            imap_server (str): IMAP server address
            imap_port (int): IMAP port (default 993 for SSL)
            bounce_keywords (list): Keywords to detect bounce emails
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.bounce_keywords = bounce_keywords or [
            'Delivery Status Notification',
            'Undelivered Mail Returned to Sender',
            'Mail Delivery Subsystem',
            'Delivery Failure',
            'Mail Delivery Failed',
            'returned to sender',
            'undeliverable'
        ]
    
    def connect(self):
        """Connect to IMAP server."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            return mail
        except Exception as e:
            print(f"Error connecting to IMAP: {str(e)}")
            return None
    
    def _decode_subject(self, subject):
        """Decode email subject."""
        try:
            decoded_parts = decode_header(subject)
            subject_str = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    subject_str += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    subject_str += str(part)
            return subject_str
        except:
            return str(subject)
    
    def _extract_email_address(self, email_str):
        """Extract email address from 'Name <email@domain.com>' format."""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email_str)
        return match.group(0).lower() if match else email_str.lower()
    
    def check_for_bounces(self, contact_emails, days_back=7):
        """
        Check inbox for bounced emails.
        
        Args:
            contact_emails (list): List of email addresses we sent to
            days_back (int): How many days back to check
            
        Returns:
            list: Email addresses that bounced
        """
        bounced_emails = []
        
        mail = self.connect()
        if not mail:
            return bounced_emails
        
        try:
            # Select inbox
            mail.select('INBOX')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Search for emails since date
            status, messages = mail.search(None, f'SINCE {since_date}')
            
            if status != 'OK':
                print("No messages found")
                return bounced_emails
            
            message_ids = messages[0].split()
            
            print(f"Checking {len(message_ids)} recent emails for bounces...")
            
            for msg_id in message_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Get subject
                    subject = self._decode_subject(msg.get('Subject', ''))
                    
                    # Check if it's a bounce
                    is_bounce = any(keyword.lower() in subject.lower() 
                                   for keyword in self.bounce_keywords)
                    
                    if is_bounce:
                        # Try to extract the original recipient
                        # Check body for email addresses
                        body = self._get_email_body(msg)
                        
                        # Find email addresses in body
                        found_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', body)
                        
                        for found_email in found_emails:
                            found_email_lower = found_email.lower()
                            if found_email_lower in [e.lower() for e in contact_emails]:
                                if found_email_lower not in [e.lower() for e in bounced_emails]:
                                    bounced_emails.append(found_email_lower)
                                    print(f"  Bounce detected: {found_email_lower}")
                
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
        
        except Exception as e:
            print(f"Error checking for bounces: {str(e)}")
        
        return bounced_emails
    
    def check_for_replies(self, contact_emails, days_back=7):
        """
        Check inbox for replies from contacts.
        
        Args:
            contact_emails (list): List of email addresses we sent to
            days_back (int): How many days back to check
            
        Returns:
            list: Email addresses that replied
        """
        replied_emails = []
        
        mail = self.connect()
        if not mail:
            return replied_emails
        
        try:
            # Select inbox
            mail.select('INBOX')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Search for emails since date
            status, messages = mail.search(None, f'SINCE {since_date}')
            
            if status != 'OK':
                print("No messages found")
                return replied_emails
            
            message_ids = messages[0].split()
            
            print(f"Checking {len(message_ids)} recent emails for replies...")
            
            for msg_id in message_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Get sender
                    from_email = self._extract_email_address(msg.get('From', ''))
                    
                    # Check if sender is in our contact list
                    if from_email in [e.lower() for e in contact_emails]:
                        # Make sure it's not a bounce
                        subject = self._decode_subject(msg.get('Subject', ''))
                        is_bounce = any(keyword.lower() in subject.lower() 
                                       for keyword in self.bounce_keywords)
                        
                        if not is_bounce and from_email not in [e.lower() for e in replied_emails]:
                            replied_emails.append(from_email)
                            print(f"  Reply detected from: {from_email}")
                
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
        
        except Exception as e:
            print(f"Error checking for replies: {str(e)}")
        
        return replied_emails
    
    def _get_email_body(self, msg):
        """Extract email body text."""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body


if __name__ == "__main__":
    # This module requires configuration from config.py
    print("Inbox Monitor Module - Use via main.py")
