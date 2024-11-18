# site-to-md

A Python package to convert websites to markdown files while preserving formatting, code blocks, tables, and other elements.

## Installation

```bash
pip install site-to-md
```

## Usage

### Command Line

```bash
# Basic usage
site-to-md https://docs.python.org/3/library/urllib.parse.html

# Specify output directory
site-to-md https://docs.python.org/3/library/urllib.parse.html --output-dir custom/path

# Get help
site-to-md --help
```

### Python Module

```python
from site_to_md import URLToMarkdownConverter, ConversionConfig

# Basic usage
converter = URLToMarkdownConverter()
converter.convert('https://docs.python.org/3/library/urllib.parse.html')

# With custom configuration
config = ConversionConfig(
    remove_elements=['nav', 'footer', 'aside'],
    body_width=0
)
converter = URLToMarkdownConverter(config)
converter.convert(
    'https://docs.python.org/3/library/urllib.parse.html',
    output_dir='custom/path'
)
```

## Features

- Extracts main content using readability
- Preserves code blocks with syntax highlighting
- Maintains tables, links, and images
- Removes unwanted elements like navigation and ads
- Configurable output directory
- Proper error handling and logging
- Type hints and comprehensive documentation

## Configuration

The `ConversionConfig` class accepts the following parameters:

- `remove_elements`: List of HTML elements to remove (default: ['script', 'style', 'nav', 'footer', 'iframe', 'aside'])
- `body_width`: Width for text wrapping (0 for no wrapping)
- `code_language_classes`: List of class prefixes for code block language detection
- `base_url`: Base URL for converting relative links to absolute

## Output Directory

By default, markdown files are saved to `~/Documents/website-markdown/` with subdirectories based on the domain. For example:

- `~/Documents/website-markdown/docs.python.org/library/urllib.parse.md`
- `~/Documents/website-markdown/github.com/python/cpython/README.md`

You can override this with the `--output-dir` option or by passing `output_dir` to the `convert()` method.

## License

MIT License
