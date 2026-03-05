"""
Excel Parser Module
Extracts HR contact information from Excel files (XLSX, XLS).
"""

import pandas as pd
import re


def extract_contacts_from_excel(excel_path):
    """
    Extract contact information from an Excel file.
    
    Args:
        excel_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: DataFrame with columns: name, email, company
    """
    try:
        # Read Excel file (tries both xlsx and xls)
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
        except:
            df = pd.read_excel(excel_path, engine='xlrd')
        
        # Normalize column names (lowercase, strip spaces)
        df.columns = df.columns.str.lower().str.strip()
        
        # Find relevant columns
        name_col = _find_column(df.columns, ['name', 'contact_name', 'person', 'full_name'])
        email_col = _find_column(df.columns, ['email', 'email_address', 'e-mail', 'mail'])
        company_col = _find_column(df.columns, ['company', 'organization', 'org', 'firm', 'business'])
        
        if not email_col:
            raise ValueError("Could not find email column in Excel file")
        
        # Create result DataFrame
        result = pd.DataFrame()
        result['email'] = df[email_col]
        result['name'] = df[name_col] if name_col else df[email_col].str.split('@').str[0]
        result['company'] = df[company_col] if company_col else 'Unknown Company'
        
        # Clean and validate
        result = _clean_contacts(result)
        
        return result
    
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        raise


def _find_column(columns, possible_names):
    """Find a column by matching possible names."""
    for col in columns:
        for name in possible_names:
            if name in col:
                return col
    return None


def _clean_contacts(df):
    """Clean and validate contact data."""
    # Remove duplicates
    df = df.drop_duplicates(subset=['email'])
    
    # Remove empty values
    df = df.dropna(subset=['email'])
    
    # Clean strings
    df['name'] = df['name'].astype(str).str.strip()
    df['email'] = df['email'].astype(str).str.strip().str.lower()
    df['company'] = df['company'].astype(str).str.strip()
    
    # Validate emails
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    df = df[df['email'].str.match(email_pattern, na=False)]
    
    return df


if __name__ == "__main__":
    # Test the parser
    import sys
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        df = extract_contacts_from_excel(excel_path)
        print(f"Extracted {len(df)} contacts")
        print(df.head())
