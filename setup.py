#!/usr/bin/env python3
"""
Westpac Scholars Analysis Project Setup Script
This script helps set up the project environment and initial configuration.
"""

import os
import sys
import subprocess
import platform
import argparse

def check_python_version():
    """Check if the Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"Python version {current_version[0]}.{current_version[1]} is compatible.")
    return True

def create_virtual_environment():
    """Create a Python virtual environment."""
    if os.path.exists("venv"):
        print("Virtual environment already exists.")
        return True
    
    try:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies from requirements.txt."""
    pip_cmd = "venv/bin/pip" if platform.system() != "Windows" else r"venv\Scripts\pip.exe"
    
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found.")
        return False
    
    try:
        print("Installing Python dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("Python dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        return False

def setup_frontend():
    """Set up the frontend React application."""
    if not os.path.exists("frontend"):
        print("Error: frontend directory not found.")
        return False
    
    try:
        print("Setting up frontend...")
        os.chdir("frontend")
        
        # Check if Node.js is installed
        try:
            subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Node.js is not installed. Please install Node.js before proceeding.")
            return False
        
        # Install dependencies
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        os.chdir("..")
        print("Frontend setup completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up frontend: {e}")
        os.chdir("..")
        return False

def create_data_directories():
    """Create necessary data directories."""
    directories = ["data", "scholar_photos", "frontend/public/data", "frontend/public/scholar_photos"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return True

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup Westpac Scholars Analysis Project")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip frontend setup")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")
    args = parser.parse_args()
    
    print("=" * 50)
    print("Westpac Scholars Analysis Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not args.skip_venv:
        if not create_virtual_environment():
            return 1
        
        # Install Python dependencies
        if not install_python_dependencies():
            return 1
    else:
        print("Skipping virtual environment creation.")
    
    # Create data directories
    if not create_data_directories():
        return 1
    
    # Setup frontend
    if not args.skip_frontend:
        if not setup_frontend():
            return 1
    else:
        print("Skipping frontend setup.")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    
    # Print next steps
    print("\nNext steps:")
    if not args.skip_venv:
        if platform.system() != "Windows":
            print("1. Activate the virtual environment: source venv/bin/activate")
        else:
            print(r"1. Activate the virtual environment: venv\Scripts\activate")
    
    print("2. Run the data collection script: python collect_westpac_data.py")
    print("3. Start the frontend: cd frontend && npm start")
    print("\nAlternatively, run everything with the shell script: ./run_westpac_analysis.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 