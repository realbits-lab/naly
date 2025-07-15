#!/usr/bin/env python3
"""Setup script to ensure all dependencies are properly installed"""

import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    """Check and install required dependencies"""
    
    dependencies = [
        ('python-pptx', 'pptx'),
        ('Pillow', 'PIL'),
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy')
    ]
    
    print("🔧 Checking dependencies...")
    
    for package_name, import_name in dependencies:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} is already installed")
        except ImportError:
            print(f"❌ {package_name} not found. Installing...")
            try:
                install_package(package_name)
                print(f"✅ {package_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package_name}: {e}")
                return False
    
    print("\n🧪 Testing imports...")
    
    # Test imports
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV import failed")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow import successful")
    except ImportError:
        print("❌ PIL/Pillow import failed")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
    except ImportError:
        print("❌ NumPy import failed")
        return False
    
    try:
        from pptx import Presentation
        print("✅ python-pptx import successful")
    except ImportError:
        print("❌ python-pptx import failed")
        return False
    
    print("\n🎉 All dependencies are properly installed!")
    return True

def test_system():
    """Test the multimodal chat system"""
    print("\n🧪 Testing multimodal chat system...")
    
    try:
        from multimodal_chat import MultimodalChatGenerator
        generator = MultimodalChatGenerator("blank.pptx")
        print("✅ System initialization successful")
        return True
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Multimodal Chat System Setup")
    print("=" * 40)
    
    if check_and_install_dependencies():
        if test_system():
            print("\n✨ Setup completed successfully!")
            print("\nYou can now run:")
            print("  python multimodal_chat.py --interactive")
        else:
            print("\n❌ Setup completed but system test failed")
            sys.exit(1)
    else:
        print("\n❌ Setup failed")
        sys.exit(1)