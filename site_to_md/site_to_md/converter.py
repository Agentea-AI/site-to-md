"""
Core functionality for converting websites to markdown.
"""

import os
import re
import logging
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import requests
from readability import Document
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse, unquote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ConversionConfig:
    """Configuration options for the conversion process."""
    remove_elements: List[str] = None
    body_width: int = 0
    code_language_classes: List[str] = None
    base_url: Optional[str] = None
    
    def __post_init__(self):
        """Set default values if none provided."""
        if self.remove_elements is None:
            self.remove_elements = ['script', 'style', 'nav', 'footer', 'iframe', 'aside']
        if self.code_language_classes is None:
            self.code_language_classes = ['language-', 'lang-']

class URLToMarkdownConverter:
    """Converts web pages to markdown format."""
    
    def __init__(self, config: Optional[ConversionConfig] = None):
        """
        Initialize the converter with optional configuration.
        
        Args:
            config: Configuration options for the conversion process
        """
        self.config = config or ConversionConfig()
    
    def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL with proper headers.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The HTML content of the page
            
        Raises:
            requests.RequestException: If the URL cannot be fetched
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise
    
    def clean_html(self, html_content: str, url: Optional[str] = None) -> str:
        """
        Clean and process HTML content.
        
        Args:
            html_content: Raw HTML content
            url: Original URL for resolving relative links
            
        Returns:
            Cleaned HTML content
        """
        # Extract main content using readability
        doc = Document(html_content)
        content = doc.summary()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'lxml')
        
        # Remove unwanted elements
        for element in soup.find_all(self.config.remove_elements):
            element.decompose()
        
        # Process code blocks
        self._process_code_blocks(soup)
        
        # Convert relative URLs to absolute
        base_url = url or self.config.base_url
        if base_url:
            self._convert_relative_urls(soup, base_url)
        
        return str(soup)
    
    def _process_code_blocks(self, soup: BeautifulSoup) -> None:
        """
        Process code blocks to ensure proper markdown conversion.
        
        Args:
            soup: BeautifulSoup object containing the HTML
        """
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                # Get language class if it exists
                language = ''
                if code.get('class'):
                    for cls in code.get('class', []):
                        if any(cls.startswith(prefix) for prefix in self.config.code_language_classes):
                            language = cls.split('-')[1]
                            break
                
                # Create markdown code block
                code_text = code.get_text()
                new_tag = soup.new_tag('pre')
                new_tag.string = f"```{language}\n{code_text}\n```"
                pre.replace_with(new_tag)
    
    def _convert_relative_urls(self, soup: BeautifulSoup, base_url: str) -> None:
        """
        Convert relative URLs to absolute URLs.
        
        Args:
            soup: BeautifulSoup object containing the HTML
            base_url: Base URL for resolving relative links
        """
        for tag in soup.find_all(['a', 'img']):
            if tag.name == 'a' and tag.has_attr('href'):
                if not tag['href'].startswith(('http://', 'https://')):
                    tag['href'] = f"{base_url.rstrip('/')}/{tag['href'].lstrip('/')}"
            elif tag.name == 'img' and tag.has_attr('src'):
                if not tag['src'].startswith(('http://', 'https://')):
                    tag['src'] = f"{base_url.rstrip('/')}/{tag['src'].lstrip('/')}"
    
    def html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML to Markdown.
        
        Args:
            html_content: Cleaned HTML content
            
        Returns:
            Markdown formatted content
        """
        h = html2text.HTML2Text()
        h.body_width = self.config.body_width
        h.ignore_images = False
        h.ignore_links = False
        h.ignore_tables = False
        h.ignore_emphasis = False
        
        # Convert HTML to markdown
        markdown = h.handle(html_content)
        
        # Clean up any remaining [code] tags
        markdown = re.sub(r'\[code\]\s*', '', markdown)
        markdown = re.sub(r'\s*\[/code\]', '', markdown)
        
        # Ensure proper spacing around code blocks
        markdown = re.sub(r'```(\w*)\n\n', r'```\1\n', markdown)
        markdown = re.sub(r'\n\n```', r'\n```', markdown)
        
        return markdown
    
    def _get_url_path_parts(self, url: str) -> List[str]:
        """
        Get clean path parts from URL for directory structure.
        
        Args:
            url: The source URL
            
        Returns:
            List of clean path parts
        """
        parsed = urlparse(url)
        path_parts = []
        
        # Add domain
        path_parts.append(parsed.netloc)
        
        # Process path components
        if parsed.path and parsed.path != '/':
            # Clean and split path
            clean_path = unquote(parsed.path).strip('/')
            parts = [p for p in clean_path.split('/') if p]
            
            # Add all parts except the last one if it looks like a file
            if parts:
                if '.' in parts[-1]:
                    path_parts.extend(parts[:-1])
                else:
                    path_parts.extend(parts)
        
        return path_parts
    
    def _get_safe_filename(self, url: str) -> str:
        """
        Generate a safe filename from URL.
        
        Args:
            url: The source URL
            
        Returns:
            Safe filename with .md extension
        """
        parsed = urlparse(url)
        
        # Get the last part of the path or use domain
        if parsed.path and parsed.path != '/':
            clean_path = unquote(parsed.path).strip('/')
            parts = [p for p in clean_path.split('/') if p]
            if parts:
                base_name = parts[-1]
            else:
                base_name = parsed.netloc
        else:
            base_name = parsed.netloc
        
        # Remove extension if present
        base_name = os.path.splitext(base_name)[0]
        
        # Clean the filename
        safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
        
        return f"{safe_name}.md"
    
    def convert(self, url: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a URL to markdown and save to file.
        
        Args:
            url: The URL to convert
            output_dir: Optional directory to save the file
            
        Returns:
            Path to the created markdown file
            
        Raises:
            requests.RequestException: If the URL cannot be fetched
            IOError: If the file cannot be written
        """
        try:
            logger.info(f"Fetching content from {url}")
            html_content = self.fetch_url(url)
            
            logger.info("Cleaning HTML content")
            cleaned_html = self.clean_html(html_content, url)
            
            logger.info("Converting to markdown")
            markdown_content = self.html_to_markdown(cleaned_html)
            
            # Set up output path
            if output_dir:
                base_dir = Path(output_dir)
            else:
                base_dir = Path.home() / "Documents" / "website-markdown"
            
            # Create path parts for subdirectories
            path_parts = self._get_url_path_parts(url)
            output_path = base_dir.joinpath(*path_parts)
            
            # Create output directory
            logger.info(f"Creating directory: {output_path}")
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename and combine with output path
            filename = self._get_safe_filename(url)
            output_file = output_path / filename
            
            # Save to file
            logger.info(f"Saving to {output_file}")
            output_file.write_text(markdown_content, encoding='utf-8')
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error converting {url}: {e}")
            raise
