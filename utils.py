"""
Repository Extractor for LLM Consumption - Utilities

This module contains utility functions and constants for the Repository Extractor application.
"""

import os

# Default ignored directories
DEFAULT_IGNORED_DIRS = {
    '.git', '.github', 'node_modules', '__pycache__', 
    'venv', '.venv', 'env', '.env', 'dist', 'build',
    '.idea', '.vscode', '.gradle', 'target', 'bin',
    'obj', 'out', 'ios', 'android', 'public', 'tmp'
}

# Common binary file extensions to ignore
DEFAULT_IGNORED_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.o', '.a', '.lib', '.zip', 
    '.tar', '.gz', '.7z', '.jar', '.war', '.ear', '.class', '.log', '.bin', 
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.mp3', '.mp4', 
    '.avi', '.mov', '.flv', '.wmv', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.db', '.sqlite', '.sqlite3', '.dat', '.min.js', '.min.css',
    '.ttf', '.woff', '.woff2', '.eot', '.lock'
}

# Default maximum file size (1MB)
DEFAULT_MAX_FILE_SIZE = 1024 * 1024

def is_text_file(file_path):
    """
    Detect if a file is a text file by reading a small sample.
    
    Args:
        file_path (str): The path to the file to check
        
    Returns:
        bool: True if the file is likely a text file, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(1024)  # Read first 1KB
            # Check for null bytes which usually indicate binary files
            if b'\x00' in sample:
                return False
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except (PermissionError, OSError):
        return False

def get_relative_path(file_path, base_path):
    """
    Get the relative path of a file with respect to a base path.
    
    Args:
        file_path (str): The absolute path to the file
        base_path (str): The base path to make the file path relative to
        
    Returns:
        str: The relative path
    """
    return os.path.relpath(file_path, base_path)

def get_file_extension(file_path):
    """
    Get the extension of a file.
    
    Args:
        file_path (str): The path to the file
        
    Returns:
        str: The file extension (including the dot)
    """
    return os.path.splitext(file_path)[1].lower()