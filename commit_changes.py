#!/usr/bin/env python3
"""
Script to commit changes to the repository.
"""

import os
import sys
import subprocess

def run_command(command):
    """Run a shell command and print the output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(f"Output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    
    return process.returncode

def main():
    """Main function to commit changes."""
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize git repository if it doesn't exist
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        run_command('git init')
    
    # Configure git user if not already configured
    run_command('git config user.name "Emmanuel D. Humbling"')
    run_command('git config user.email "edhumbling@gmail.com"')
    
    # Check git status
    print("Checking git status...")
    run_command('git status')
    
    # Add all files
    print("Adding files to git...")
    run_command('git add .')
    
    # Commit changes
    print("Committing changes...")
    run_command('git commit -m "Add reading metrics with Supabase integration and glass effect progress bar"')
    
    # Check if remote exists
    print("Checking if remote exists...")
    remote_exists = run_command('git remote -v') == 0
    
    if remote_exists:
        # Push changes
        print("Pushing changes...")
        run_command('git push')
    else:
        print("No remote repository configured. Skipping push.")
    
    print("Done!")

if __name__ == "__main__":
    main()
