#!/usr/bin/env python3
"""
Setup script for CymbalBot - Internal Knowledge Assistant
This script helps initialize the project with proper configuration.
"""

import os
import sys
import json
import shutil
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🏢 CymbalBot - Internal Knowledge Assistant Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories."""
    directories = [
        "test_results",
        "config",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_env_file():
    """Set up .env file from template."""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_template.exists():
        shutil.copy(env_template, env_file)
        print("✅ Created .env from template")
        print("⚠️  Please update .env with your actual values")
    else:
        # Create basic .env file
        env_content = """# GCP Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
GOOGLE_CLOUD_REGION=us-central1

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_NAME=gemini-2.5-flash
VERTEX_STAGING_BUCKET=gs://your-bucket-name

# RAG API Configuration
RAG_BASE_URL=http://your-rag-api-url:8000
RAG_KTOP=10
RAG_THRESHOLD=0.6
RAG_ALLOWED_TAGS=hr,tech,infra,product,policy,onboarding,benefits,it,security,finance,legal
RAG_DEFAULT_TAG=policy
API_AUTH_TOKEN=your-api-token
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please update .env with your actual values")

def setup_config_file():
    """Set up config file from template."""
    config_file = Path("config/agent_engine.json")
    config_template = Path("config/agent_engine.json.template")
    
    if config_file.exists():
        print("✅ config/agent_engine.json already exists")
        return
    
    if config_template.exists():
        shutil.copy(config_template, config_file)
        print("✅ Created config/agent_engine.json from template")
        print("⚠️  Please update config/agent_engine.json with your actual values")
    else:
        print("❌ Config template not found")

def check_credentials():
    """Check if service account credentials exist."""
    creds_file = Path("service-account-key.json")
    if creds_file.exists():
        print("✅ Service account credentials found")
    else:
        print("⚠️  Service account credentials not found")
        print("   Please download your service account key from Google Cloud Console")
        print("   and save it as 'service-account-key.json' in the project root")

def check_conda():
    """Check if conda is available."""
    try:
        import subprocess
        result = subprocess.run(["conda", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Conda found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Conda not found")
            return False
    except FileNotFoundError:
        print("❌ Conda not found")
        return False

def create_conda_environment():
    """Create conda environment named cymbal-agent."""
    print("\n🐍 Creating conda environment...")
    
    if not check_conda():
        print("⚠️  Conda not available, skipping environment creation")
        print("   Please install Anaconda or Miniconda and run setup again")
        return False
    
    try:
        import subprocess
        
        # Check if environment already exists
        result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
        if "cymbal-agent" in result.stdout:
            print("✅ Conda environment 'cymbal-agent' already exists")
            return True
        
        # Create new environment
        print("Creating conda environment 'cymbal-agent'...")
        result = subprocess.run([
            "conda", "create", "-n", "cymbal-agent", 
            "python=3.11", "-y"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conda environment 'cymbal-agent' created successfully")
            return True
        else:
            print("❌ Failed to create conda environment:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error creating conda environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        import subprocess
        
        # Try to use conda environment if available
        if check_conda():
            print("Installing dependencies in conda environment 'cymbal-agent'...")
            result = subprocess.run([
                "conda", "run", "-n", "cymbal-agent", 
                "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
        else:
            print("Installing dependencies in current environment...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("1. 🐍 Activate Conda Environment:")
    print("   conda activate cymbal-agent")
    print()
    print("2. 📋 Update Configuration Files:")
    print("   • Edit .env with your actual GCP project details")
    print("   • Edit config/agent_engine.json with your agent details")
    print("   • Add your service-account-key.json file")
    print()
    print("3. 🧪 Test Local Agent:")
    print("   python scripts/test_local_agent.py")
    print()
    print("4. 🚀 Deploy Agent:")
    print("   python deploy.py")
    print()
    print("5. 🧪 Test Deployed Agent:")
    print("   python scripts/test_deployed_agent.py")
    print()
    print("6. 💬 Use CLI Interface:")
    print("   python agent_cli.py")
    print()
    print("📚 For more information, see README.md")

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Setup configuration files
    print("\n⚙️  Setting up configuration...")
    setup_env_file()
    setup_config_file()
    
    # Check credentials
    print("\n🔑 Checking credentials...")
    check_credentials()
    
    # Create conda environment
    create_conda_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
