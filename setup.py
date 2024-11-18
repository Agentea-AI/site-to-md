from setuptools import setup, find_packages

setup(
    name="site-to-md",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "readability-lxml",
        "beautifulsoup4",
        "html2text",
        "lxml",
    ],
    entry_points={
        "console_scripts": [
            "site-to-md=site_to_md.cli:main",
        ],
    },
    author="Mark Watson",
    author_email="mark@agentea.ai",
    description="Convert websites to markdown files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Agentea-AI/site-to-md",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
