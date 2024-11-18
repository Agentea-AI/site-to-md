"""
Command-line interface for site-to-md.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
from .converter import URLToMarkdownConverter, ConversionConfig

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert websites to markdown files while preserving formatting."
    )
    
    parser.add_argument(
        "url",
        help="URL of the website to convert"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory (default: ~/Documents/website-markdown/domain/path/)",
        type=str
    )
    
    parser.add_argument(
        "--remove", "-r",
        help="HTML elements to remove (comma-separated)",
        type=str,
        default="script,style,nav,footer,iframe,aside"
    )
    
    parser.add_argument(
        "--body-width", "-w",
        help="Width to wrap text (0 for no wrapping)",
        type=int,
        default=0
    )
    
    parser.add_argument(
        "--quiet", "-q",
        help="Suppress informational output",
        action="store_true"
    )
    
    parser.add_argument(
        "--debug",
        help="Show debug information",
        action="store_true"
    )
    
    return parser.parse_args()

def setup_logging(quiet: bool, debug: bool) -> None:
    """Configure logging based on command line options."""
    if debug:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main() -> Optional[int]:
    """Main entry point for the command-line interface."""
    args = parse_args()
    
    # Set up logging
    setup_logging(args.quiet, args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Create configuration
        config = ConversionConfig(
            remove_elements=args.remove.split(','),
            body_width=args.body_width
        )
        
        # Convert the URL
        converter = URLToMarkdownConverter(config)
        output_file = converter.convert(args.url, args.output_dir)
        
        if not args.quiet:
            print(f"Content saved to {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
