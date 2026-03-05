"""
PDF Parser Module
Extracts HR contact information from PDF files using pdfplumber.
"""

import pdfplumber
import pandas as pd
import re


def extract_contacts_from_pdf(pdf_path):
    """
    Extract contact information from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        pd.DataFrame: DataFrame with columns: name, email, company
    """
    contacts = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                
                if not text:
                    print(f"Warning: No text found on page {page_num}")
                    continue
                
                # Try to extract tables first
                tables = page.extract_tables()
                
                if tables:
                    # Process tables
                    for table in tables:
                        contacts.extend(_parse_table(table))
                else:
                    # Parse text line by line
                    contacts.extend(_parse_text(text))
    
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        raise
    
    # Create DataFrame
    df = pd.DataFrame(contacts)
    
    # Clean and validate
    if not df.empty:
        df = _clean_contacts(df)
    
    return df


def _parse_table(table):
    """Parse contact information from a table structure."""
    contacts = []
    
    # Skip header row
    for row in table[1:]:
        if not row or len(row) < 3:
            continue
        
        # Try to extract email from the row
        email = None
        name = None
        company = None
        
        for cell in row:
            if cell and '@' in str(cell):
                email = _extract_email(str(cell))
                if email:
                    break
        
        if not email:
            continue
        
        # Get name (usually first non-empty column or second column)
        for cell in row:
            if cell and cell.strip() and '@' not in str(cell) and not str(cell).isdigit():
                name = str(cell).strip()
                break
        
        # Get company (usually last meaningful column)
        for cell in reversed(row):
            if cell and cell.strip() and '@' not in str(cell) and cell != name:
                company = str(cell).strip()
                break
        
        if email and name and company:
            contacts.append({
                'name': name,
                'email': email,
                'company': company
            })
    
    return contacts


def _parse_text(text):
    """Parse contact information from plain text."""
    contacts = []
    lines = text.split('\n')
    
    for line in lines:
        if not line or not '@' in line:
            continue
        
        # Extract email
        email = _extract_email(line)
        if not email:
            continue
        
        # Try to extract name and company from the line
        # Pattern: Name | email | title | company
        parts = [p.strip() for p in line.split('|')]
        
        name = None
        company = None
        
        if len(parts) >= 3:
            # Find the part with email
            email_idx = -1
            for i, part in enumerate(parts):
                if email in part:
                    email_idx = i
                    break
            
            if email_idx > 0:
                name = parts[email_idx - 1]
            
            if email_idx >= 0 and email_idx < len(parts) - 1:
                company = parts[-1]  # Last part is usually company
        else:
            # Try to extract from space-separated values
            words = line.split()
            name_words = []
            company_words = []
            
            for word in words:
                if '@' in word:
                    break
                if not word.isdigit():
                    name_words.append(word)
            
            # Get company (words after email)
            capture_company = False
            for word in words:
                if capture_company and not word.isdigit():
                    company_words.append(word)
                if email in word:
                    capture_company = True
            
            name = ' '.join(name_words[:3]) if name_words else None
            company = ' '.join(company_words[:5]) if company_words else None
        
        if email and name and company:
            contacts.append({
                'name': name,
                'email': email,
                'company': company
            })
    
    return contacts


def _extract_email(text):
    """Extract email address from text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def _clean_contacts(df):
    """Clean and validate contact data."""
    # Remove duplicates
    df = df.drop_duplicates(subset=['email'])
    
    # Remove empty values
    df = df.dropna(subset=['name', 'email', 'company'])
    
    # Clean strings
    df['name'] = df['name'].str.strip()
    df['email'] = df['email'].str.strip().str.lower()
    df['company'] = df['company'].str.strip()
    
    # Validate emails
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    df = df[df['email'].str.match(email_pattern, na=False)]
    
    return df


if __name__ == "__main__":
    # Test the parser
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        df = extract_contacts_from_pdf(pdf_path)
        print(f"Extracted {len(df)} contacts")
        print(df.head())
