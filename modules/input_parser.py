"""
Input Parser Module
Detects file type and routes to appropriate parser.
Converts all formats to standardized CSV.
"""

import os
import pandas as pd
from modules.pdf_parser import extract_contacts_from_pdf
from modules.csv_parser import extract_contacts_from_csv
from modules.excel_parser import extract_contacts_from_excel


def parse_input_file(input_path, output_csv='data/contacts.csv'):
    """
    Parse input file and convert to standardized CSV format.
    
    Args:
        input_path (str): Path to input file (PDF, CSV, XLSX, XLS)
        output_csv (str): Path to output CSV file
        
    Returns:
        pd.DataFrame: Parsed contacts
    """
    # Detect file type
    file_ext = os.path.splitext(input_path)[1].lower()
    
    print(f"Detected file type: {file_ext}")
    
    # Route to appropriate parser
    if file_ext == '.pdf':
        print("Parsing PDF file...")
        df = extract_contacts_from_pdf(input_path)
    elif file_ext == '.csv':
        print("Parsing CSV file...")
        df = extract_contacts_from_csv(input_path)
    elif file_ext in ['.xlsx', '.xls']:
        print("Parsing Excel file...")
        df = extract_contacts_from_excel(input_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}. Supported: PDF, CSV, XLSX, XLS")
    
    if df.empty:
        print("Warning: No contacts extracted from file")
        return df
    
    print(f"Extracted {len(df)} contacts")
    
    # Ensure required columns exist
    required_cols = ['name', 'email', 'company']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Contacts saved to {output_csv}")
    
    return df


def load_contacts(csv_path='data/contacts.csv'):
    """
    Load contacts from CSV file.
    
    Args:
        csv_path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Contact data
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Contacts file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} contacts from {csv_path}")
    
    return df


if __name__ == "__main__":
    # Test the parser
    import sys
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        df = parse_input_file(input_path)
        print("\nFirst 5 contacts:")
        print(df.head())
