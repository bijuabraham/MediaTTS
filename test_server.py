import requests
import time
import sys
import os

def check_lm_studio():
    """Check if LM Studio API is running"""
    try:
        response = requests.get("http://127.0.0.1:1234/v1/models")
        if response.status_code == 200:
            print("✅ LM Studio API is running")
            return True
        else:
            print("❌ LM Studio API returned unexpected status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ LM Studio API is not running at http://127.0.0.1:1234")
        print("   Please start LM Studio and load the Orpheus model")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    all_installed = True
    
    # Check core dependencies
    dependencies = [
        ('flask', 'Flask web framework'),
        ('flask_cors', 'Flask CORS extension'),
        ('numpy', 'NumPy for numerical operations'),
        ('torch', 'PyTorch for ML operations'),
        ('sounddevice', 'Sound device for audio playback'),
        ('snac', 'SNAC for audio processing')
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name}) is installed")
        except ImportError:
            print(f"❌ Missing dependency: {module_name} ({description})")
            all_installed = False
    
    if not all_installed:
        print("\n   Some dependencies are missing. Run: pip install -r requirements.txt")
        print("   Note: The server may still work if you're not using all features.")
    
    return True  # Return True to continue with other checks

def main():
    """Run tests to verify the setup is correct"""
    print("\n=== Orpheus TTS Web Client Test ===\n")
    
    # Check dependencies (continue regardless of result)
    check_dependencies()
    
    # Check if LM Studio is running
    lm_studio_running = check_lm_studio()
    
    print("\n=== Summary ===")
    if lm_studio_running:
        print("✅ LM Studio is running and ready")
        print("\nYou can run the server with:")
        print("   python server.py")
        print("\nThen open your browser to: http://localhost:5000")
        return True
    else:
        print("❌ LM Studio is not running or not properly configured")
        print("\nPlease start LM Studio and load the Orpheus model before running:")
        print("   python server.py")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Some tests failed. Please fix the issues before running the server.")
        sys.exit(1)
