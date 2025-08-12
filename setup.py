#!/usr/bin/env python3
"""
Setup script for Recipe Genie bot
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return True
    
    print("📝 Creating .env file from template...")
    
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created successfully!")
        print("📋 Please edit .env file with your actual values:")
        print("   - BOT_TOKEN: Your Telegram bot token")
        print("   - LLM_MODEL: Your LMStudio model name")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'telegram',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    return True

def validate_config():
    """Validate the configuration."""
    print("🔧 Validating configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    llm_endpoint = os.getenv('LLM_ENDPOINT')
    llm_model = os.getenv('LLM_MODEL')
    
    issues = []
    
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        issues.append("BOT_TOKEN not set or using default value")
    
    if not llm_model or llm_model == 'your_model_name_here':
        issues.append("LLM_MODEL not set or using default value")
    
    if not llm_endpoint:
        issues.append("LLM_ENDPOINT not set")
    
    if issues:
        print("⚠️  Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n📝 Please edit your .env file to fix these issues.")
        return False
    else:
        print("✅ Configuration looks good!")
        return True

def main():
    """Main setup function."""
    print("🍳 Recipe Genie Bot Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Setup failed: Dependencies not installed")
        return
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed: Could not create .env file")
        return
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual values")
    print("2. Get a Telegram bot token from @BotFather")
    print("3. Set up LMStudio and note your model name")
    print("4. Test LLM integration: python test_llm_integration.py")
    print("5. Run the bot: python recipe_genie_bot_enhanced.py")
    
    print("\n🔗 Useful links:")
    print("- Telegram BotFather: https://t.me/botfather")
    print("- LMStudio: https://lmstudio.ai/")
    print("- Recipe Genie Documentation: README.md")
    
    print("\n✅ Setup completed!")

if __name__ == "__main__":
    main()