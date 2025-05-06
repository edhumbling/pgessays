#!/usr/bin/env python3
"""
Simple script to fix the date for the "What to Do" essay using CSV module.
"""

import os
import csv

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
TEMP_CSV = os.path.join(ESSAYS_DIR, "essays_temp.csv")

def main():
    """Main function to fix the date."""
    print("Fixing date for 'What to Do' essay...")
    
    # Read the essays.csv file
    if not os.path.exists(ESSAYS_CSV):
        print(f"Error: {ESSAYS_CSV} does not exist")
        return
    
    # Read the CSV file
    rows = []
    with open(ESSAYS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
    
    # Find the "What to Do" essay and update the date
    found = False
    for i, row in enumerate(rows):
        if i > 0 and len(row) >= 3 and row[1] == 'What to Do':
            print(f"Found 'What to Do' essay with date: {row[2]}")
            row[2] = 'March 2025'
            found = True
            break
    
    if not found:
        print("Error: 'What to Do' essay not found in the database")
        return
    
    # Write the updated CSV file
    with open(TEMP_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    
    # Replace the original file
    os.replace(TEMP_CSV, ESSAYS_CSV)
    
    print("Date updated to 'March 2025'")

if __name__ == "__main__":
    main()
