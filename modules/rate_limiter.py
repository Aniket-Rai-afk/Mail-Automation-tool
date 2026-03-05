"""
Rate Limiter Module
Implements anti-spam protections including:
- Random delays between emails
- Daily send limits
- Account rotation
"""

import time
import random
import json
import os
from datetime import datetime, timedelta


class RateLimiter:
    """Manages email sending rate to prevent spam detection."""
    
    def __init__(self, max_daily=80, min_delay=45, max_delay=120, state_file=None):
        from pathlib import Path
        import config
        self.max_daily = max_daily
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.state_file = state_file or config.DAILY_STATS_FILE
        self.state = self._load_state()
    
    def _load_state(self):
        """Load rate limiter state from file."""
        import os
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Convert date strings back to datetime
                    if 'date' in state:
                        state['date'] = datetime.fromisoformat(state['date']).date()
                    return state
            except:
                pass
        
        # Default state per requirements
        return {
            'date': datetime.now().date(),
            'emails_sent_today': 0,
            'current_account_index': 0,
            'last_send_time': None
        }
    
    def _save_state(self):
        """Save rate limiter state to file."""
        import os
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        state_copy = self.state.copy()
        if hasattr(state_copy['date'], 'isoformat'):
            state_copy['date'] = state_copy['date'].isoformat()
        
        with open(self.state_file, 'w') as f:
            json.dump(state_copy, f, indent=2)
    
    def _reset_daily_counter(self):
        """Reset daily counter if a new day has started."""
        today = datetime.now().date()
        last_reset = self.state.get('date')
        
        if isinstance(last_reset, str):
            last_reset = datetime.fromisoformat(last_reset).date()
        
        if today > last_reset:
            print(f"New day detected ({today}). Resetting daily email counter.")
            self.state['emails_sent_today'] = 0
            self.state['date'] = today
            self._save_state()
    
    def can_send_email(self):
        """Check if we can send another email today."""
        self._reset_daily_counter()
        return self.state['emails_sent_today'] < self.max_daily
    
    def get_emails_remaining(self):
        """Get number of emails remaining for today."""
        self._reset_daily_counter()
        return self.max_daily - self.state['emails_sent_today']
    
    def apply_delay(self):
        """Apply random delay before sending next email."""
        delay = random.randint(self.min_delay, self.max_delay)
        print(f"Applying random delay: {delay} seconds")
        
        # Show countdown
        for remaining in range(delay, 0, -5):
            print(f"  Waiting... {remaining} seconds remaining", end='\r')
            time.sleep(min(5, remaining))
        
        print("\n")
    
    def record_email_sent(self):
        """Record that an email was sent."""
        self.state['emails_sent_today'] += 1
        self.state['last_send_time'] = datetime.now().isoformat()
        self._save_state()
    
    def get_next_account_index(self, total_accounts):
        """Get next account index for rotation."""
        if total_accounts == 0:
            return 0
        
        current = self.state['current_account_index']
        next_index = (current + 1) % total_accounts
        self.state['current_account_index'] = next_index
        self._save_state()
        
        return next_index
    
    def get_status(self):
        """Get current rate limiter status."""
        self._reset_daily_counter()
        
        return {
            'date': str(self.state['date']),
            'emails_sent_today': self.state['emails_sent_today'],
            'max_daily': self.max_daily,
            'emails_remaining': self.get_emails_remaining(),
            'can_send': self.can_send_email()
        }


if __name__ == "__main__":
    # Test rate limiter
    limiter = RateLimiter()
    status = limiter.get_status()
    print("Rate Limiter Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
