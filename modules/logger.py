"""
Logger Module
Maintains application log with email status tracking.
"""

import pandas as pd
import os
from datetime import datetime


class ApplicationLogger:
    """Manages application status log."""
    
    def __init__(self, log_file='logs/application_log.csv'):
        self.log_file = log_file
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file if it doesn't exist."""
        from pathlib import Path
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not log_path.exists():
            # Create empty log with headers per production requirements
            df = pd.DataFrame(columns=[
                'timestamp', 'name', 'email', 'company', 
                'sender_account', 'status', 'first_email_date', 
                'followup_date', 'last_activity', 'message'
            ])
            df.to_csv(log_path, index=False)
    
    def load_log(self):
        """Load the application log."""
        df = pd.read_csv(self.log_file)
        # Ensure all required columns exist for backward compatibility
        required_cols = [
            'timestamp', 'name', 'email', 'company', 
            'sender_account', 'status', 'first_email_date', 
            'followup_date', 'last_activity', 'message'
        ]
        for col in required_cols:
            if col not in df.columns:
                if col == 'status':
                    df[col] = 'pending'
                else:
                    df[col] = ''
        return df
    
    def save_log(self, df):
        """Save the application log."""
        df.to_csv(self.log_file, index=False)
    
    def initialize_contacts(self, contacts_df):
        """Initialize log with contacts from DataFrame."""
        log_df = self.load_log()
        
        # Add new contacts not already in log
        new_entries = []
        for _, row in contacts_df.iterrows():
            if row['email'] not in log_df['email'].values:
                new_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'name': row['name'],
                    'email': row['email'],
                    'company': row['company'],
                    'sender_account': '',
                    'status': 'pending',
                    'first_email_date': '',
                    'followup_date': '',
                    'last_activity': datetime.now().isoformat(),
                    'message': 'Imported'
                }
                new_entries.append(new_entry)
        
        if new_entries:
            log_df = pd.concat([log_df, pd.DataFrame(new_entries)], ignore_index=True)
            self.save_log(log_df)
            print(f"Added {len(new_entries)} new contacts to log")
    
    def update_status(self, email, status, sender_account=None, message=None, stage=None):
        """Update status for a specific email."""
        log_df = self.load_log()
        
        mask = log_df['email'] == email
        if mask.any():
            log_df.loc[mask, 'status'] = status
            log_df.loc[mask, 'timestamp'] = datetime.now().isoformat()
            log_df.loc[mask, 'last_activity'] = datetime.now().isoformat()
            
            if stage == 1:
                log_df.loc[mask, 'first_email_date'] = datetime.now().isoformat()
            elif stage == 2:
                log_df.loc[mask, 'followup_date'] = datetime.now().isoformat()
            
            if sender_account:
                log_df.loc[mask, 'sender_account'] = sender_account
            
            if message:
                log_df.loc[mask, 'message'] = message
                
            self.save_log(log_df)
            return True
        else:
            print(f"Warning: Email {email} not found in log")
            return False
    
    def get_pending_contacts(self):
        """Get contacts with pending status."""
        log_df = self.load_log()
        return log_df[log_df['status'] == 'pending']
    
    def get_followup_eligible_contacts(self, days_ago=7):
        """Get contacts sent X days ago with no reply."""
        log_df = self.load_log()
        from datetime import datetime, timedelta
        
        # Filtrre: status is 'sent'
        sent_mask = log_df['status'] == 'sent'
        candidates = log_df[sent_mask].copy()
        
        if candidates.empty:
            return candidates
            
        candidates['first_dt'] = pd.to_datetime(candidates['first_email_date'])
        threshold = datetime.now() - timedelta(days=days_ago)
        
        followup_mask = candidates['first_dt'] <= threshold
        return candidates[followup_mask]

    def get_no_response_eligible_contacts(self, days_ago=7):
        """Get contacts followed up X days ago with no reply."""
        log_df = self.load_log()
        from datetime import datetime, timedelta
        
        # Filtre: status is 'followup_sent'
        followup_mask = log_df['status'] == 'followup_sent'
        candidates = log_df[followup_mask].copy()
        
        if candidates.empty:
            return candidates
            
        candidates['followup_dt'] = pd.to_datetime(candidates['followup_date'])
        threshold = datetime.now() - timedelta(days=days_ago)
        
        no_response_mask = candidates['followup_dt'] <= threshold
        return candidates[no_response_mask]
    
    def get_status_counts(self):
        """Get count of contacts by status."""
        log_df = self.load_log()
        counts = log_df['status'].value_counts().to_dict()
        return counts
    
    def bulk_update_status(self, email_list, status, message=None):
        """Update status for multiple emails at once."""
        log_df = self.load_log()
        
        mask = log_df['email'].isin(email_list)
        log_df.loc[mask, 'status'] = status
        log_df.loc[mask, 'timestamp'] = datetime.now().isoformat()
        log_df.loc[mask, 'last_activity'] = datetime.now().isoformat()
        
        if message:
            log_df.loc[mask, 'message'] = message
            
        self.save_log(log_df)
        print(f"Updated status to '{status}' for {mask.sum()} contacts")
    
    def export_report(self, output_file='logs/status_report.csv'):
        """Export a status report."""
        log_df = self.load_log()
        
        # Add summary
        summary = self.get_status_counts()
        
        print("\n=== Application Status Report ===")
        print(f"Total contacts: {len(log_df)}")
        for status, count in summary.items():
            print(f"  {status}: {count}")
        
        log_df.to_csv(output_file, index=False)
        print(f"\nReport saved to {output_file}")


if __name__ == "__main__":
    # Test logger
    logger = ApplicationLogger()
    
    # Test data
    test_contacts = pd.DataFrame({
        'name': ['Test User'],
        'email': ['test@example.com'],
        'company': ['Test Company']
    })
    
    logger.initialize_contacts(test_contacts)
    print("\nStatus counts:", logger.get_status_counts())
