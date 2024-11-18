"""
Test script demonstrating both module and command-line usage of site-to-md.
"""

import os
from pathlib import Path
from site_to_md import URLToMarkdownConverter, ConversionConfig

def test_as_module():
    """Test using site-to-md as a Python module."""
    print("\nTesting as module:")
    
    # Create test output directory in current directory
    test_output = Path.cwd() / "test_output"
    
    # Create converter with custom config
    config = ConversionConfig(
        remove_elements=['nav', 'footer', 'aside'],
        body_width=0
    )
    converter = URLToMarkdownConverter(config)
    
    # Convert a URL
    url = "https://docs.python.org/3/library/urllib.parse.html"
    output_file = converter.convert(url, output_dir=test_output)
    print(f"File saved to: {output_file}")

def test_cli():
    """Test command-line interface."""
    print("\nTesting command-line usage:")
    
    # Create test output directory in current directory
    test_output = Path.cwd() / "test_output_cli"
    
    print(f"Try running: site-to-md https://docs.python.org/3/library/urllib.parse.html -o {test_output}")
    print("Or: site-to-md --help")

def main():
    """Run the tests."""
    print("Testing site-to-md package...")
    
    # Test as module
    test_as_module()
    
    # Test CLI
    test_cli()

if __name__ == "__main__":
    main()
