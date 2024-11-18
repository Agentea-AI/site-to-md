"""
site-to-md package for converting websites to markdown files.
"""

from .converter import URLToMarkdownConverter, ConversionConfig

__version__ = "0.1.0"
__all__ = ["URLToMarkdownConverter", "ConversionConfig"]
