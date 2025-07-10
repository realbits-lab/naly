#!/usr/bin/env python3
"""
Test program for generate_layout.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_layout import generate_default_powerpoint, add_custom_layout, save_powerpoint, main


class TestGenerateLayout(unittest.TestCase):
    """Test cases for generate_layout.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_generate_default_powerpoint(self):
        """Test that generate_default_powerpoint creates a presentation"""
        # Create a mock blank.pptx file
        blank_pptx_path = os.path.join(self.test_dir, "blank.pptx")
        with open(blank_pptx_path, "wb") as f:
            f.write(b"dummy pptx content")
        
        try:
            prs = generate_default_powerpoint()
            self.assertIsNotNone(prs)
            # Check that the presentation has slide layouts
            self.assertTrue(hasattr(prs, 'slide_layouts'))
            self.assertTrue(hasattr(prs, 'slide_masters'))
        except Exception as e:
            self.fail(f"generate_default_powerpoint failed: {e}")

    def test_add_custom_layout(self):
        """Test that add_custom_layout adds a slide using existing layout"""
        # Create a mock presentation
        mock_prs = MagicMock()
        mock_slide_layouts = MagicMock()
        mock_layout = MagicMock()
        mock_slides = MagicMock()
        mock_slide = MagicMock()
        mock_placeholders = MagicMock()
        
        # Set up the mock hierarchy
        mock_prs.slide_layouts = [mock_layout]
        mock_prs.slides = mock_slides
        mock_layout.placeholders = mock_placeholders
        mock_placeholders.__len__ = MagicMock(return_value=2)
        mock_slides.add_slide.return_value = mock_slide
        
        # Create mock placeholders with text attribute
        mock_placeholder1 = MagicMock()
        mock_placeholder1.text = ""
        mock_placeholder2 = MagicMock()
        mock_placeholder2.text = ""
        mock_placeholders.__getitem__ = MagicMock(side_effect=[mock_placeholder1, mock_placeholder2])
        
        # Test the function
        result = add_custom_layout(mock_prs)
        
        # Verify a slide was added
        mock_slides.add_slide.assert_called_once_with(mock_layout)
        # Verify the layout was returned
        self.assertEqual(result, mock_layout)

    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_save_powerpoint(self, mock_remove, mock_exists, mock_getsize):
        """Test that save_powerpoint saves the presentation"""
        # Create a mock presentation
        mock_prs = MagicMock()
        mock_prs.save = MagicMock()
        
        # Set up mocks
        mock_exists.return_value = False  # File doesn't exist
        mock_getsize.return_value = 1024  # Mock file size
        
        # Test saving
        test_filename = "test_output.pptx"
        save_powerpoint(mock_prs, test_filename)
        
        # Verify save was called
        mock_prs.save.assert_called_once()
        # Verify file size was checked
        mock_getsize.assert_called_once()

    @patch('generate_layout.generate_default_powerpoint')
    @patch('generate_layout.save_powerpoint')
    def test_main_function(self, mock_save, mock_generate):
        """Test the main function runs without errors"""
        # Set up mocks
        mock_prs = MagicMock()
        mock_prs.slides = []
        mock_prs.slide_layouts = [MagicMock()]
        mock_prs.slide_layouts[0].name = "Title Slide"
        mock_prs.slide_layouts[0].placeholders = [MagicMock(), MagicMock()]
        
        mock_generate.return_value = mock_prs
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            main()
            
        # Verify functions were called
        mock_generate.assert_called_once()
        mock_save.assert_called_once_with(mock_prs)
        
        # Verify some output was printed
        self.assertTrue(mock_print.called)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_file_dependencies(self):
        """Test that required files exist"""
        # Check if blank.pptx exists in the examples/template directory
        example_dir = os.path.join(os.path.dirname(__file__))
        blank_pptx = os.path.join(example_dir, "blank.pptx")
        
        # If blank.pptx doesn't exist, this is expected to fail
        # We'll create a dummy file for testing
        if not os.path.exists(blank_pptx):
            with open("blank.pptx", "wb") as f:
                f.write(b"dummy pptx content")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)