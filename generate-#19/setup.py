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
        ('python-pptx>=0.6.21', 'pptx'),
        ('Pillow>=9.0.0', 'PIL'),
        ('opencv-python>=4.5.0,<4.10.0', 'cv2'),
        ('numpy>=1.21.0,<2.0', 'numpy'),
        ('pdf2image>=1.16.0', 'pdf2image'),
        ('PyMuPDF>=1.20.0', 'fitz'),
        ('scikit-image>=0.19.0', 'skimage'),
        ('comtypes>=1.1.0', 'comtypes'),
        ('openai>=1.12.0', 'openai')
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
    
    # Test new feedback loop dependencies
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image import successful")
    except ImportError:
        print("⚠️  pdf2image import failed (PDF conversion may not work)")
    
    try:
        import fitz
        print("✅ PyMuPDF import successful")
    except ImportError:
        print("⚠️  PyMuPDF import failed (PDF processing may not work)")
    
    try:
        from skimage.metrics import structural_similarity
        print("✅ scikit-image import successful")
    except ImportError:
        print("⚠️  scikit-image import failed (advanced image comparison may not work)")
    
    try:
        import comtypes.client
        print("✅ comtypes import successful")
    except ImportError:
        print("⚠️  comtypes import failed (Windows PowerPoint automation not available)")
    
    try:
        import openai
        from openai import OpenAI
        print("✅ OpenAI import successful")
    except ImportError:
        print("⚠️  OpenAI import failed (multimodal image comparison not available)")
    
    print("\n🎉 All core dependencies are properly installed!")
    print("⚠️  Some optional dependencies for feedback loop may not be available")
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
            print("  python multimodal_chat.py -i image.png -o output.pptx")
            print("  python multimodal_chat.py -i image.png -o output.pptx --feedback --verbose")
        else:
            print("\n❌ Setup completed but system test failed")
            sys.exit(1)
    else:
        print("\n❌ Setup failed")
        sys.exit(1)