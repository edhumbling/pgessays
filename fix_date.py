#!/usr/bin/env python3
"""
Simple script to fix the date for the "What to Do" essay.
"""

import os
import pandas as pd

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")

def main():
    """Main function to fix the date."""
    print("Fixing date for 'What to Do' essay...")
    
    # Read the essays.csv file
    if not os.path.exists(ESSAYS_CSV):
        print(f"Error: {ESSAYS_CSV} does not exist")
        return
    
    df = pd.read_csv(ESSAYS_CSV)
    
    # Find the "What to Do" essay
    mask = df['Title'] == 'What to Do'
    if not any(mask):
        print("Error: 'What to Do' essay not found in the database")
        return
    
    # Get the current date
    current_date = df.loc[mask, 'Date'].iloc[0]
    print(f"Current date: {current_date}")
    
    # Update the date
    df.loc[mask, 'Date'] = 'March 2025'
    
    # Save the updated DataFrame to CSV
    df.to_csv(ESSAYS_CSV, index=False)
    
    print("Date updated to 'March 2025'")

if __name__ == "__main__":
    main()
