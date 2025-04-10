"""
Repository Extractor for LLM Consumption - Core Logic

This module contains the core RepoExtractor class that handles repository scanning,
file content extraction, and output formatting.
"""

import os
import json
from utils import (
    DEFAULT_IGNORED_DIRS, 
    DEFAULT_IGNORED_EXTENSIONS, 
    DEFAULT_MAX_FILE_SIZE,
    is_text_file
)

class RepoExtractor:
    def __init__(self):
        self.files_data = []
        self.ignored_dirs = DEFAULT_IGNORED_DIRS.copy()
        self.ignored_extensions = DEFAULT_IGNORED_EXTENSIONS.copy()
        self.max_file_size = DEFAULT_MAX_FILE_SIZE
        self.output_format = "markdown"
        
    def scan_repository(self, repo_path, excluded_folders=None):
        """
        Scan repository and collect file information.
        
        Args:
            repo_path (str): Path to the repository root
            excluded_folders (set, optional): Set of folder names to exclude
            
        Returns:
            list: List of dictionaries containing file information
        """
        self.files_data = []
        excluded_folders = excluded_folders or set()
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            rel_root = os.path.relpath(root, repo_path)
            if rel_root == '.':
                rel_root = ''
                
            if any(rel_root == folder or rel_root.startswith(folder + os.path.sep) for folder in excluded_folders):
                dirs[:] = []
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                _, ext = os.path.splitext(file)
                if ext.lower() in self.ignored_extensions:
                    continue
                
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.max_file_size:
                        continue
                        
                    if is_text_file(file_path):
                        self.files_data.append({
                            'path': rel_path,
                            'size': file_size,
                            'selected': True 
                        })
                except (PermissionError, OSError):
                    continue
        
        self.files_data.sort(key=lambda x: x['path'])
        return self.files_data
    
    def extract_files_content(self, repo_path, selected_files):
        """
        Extract content from selected files.
        
        Args:
            repo_path (str): Path to the repository root
            selected_files (list): List of dictionaries containing selected file information
            
        Returns:
            list: List of dictionaries containing file paths and content
        """
        contents = []
        
        for file_info in selected_files:
            file_path = os.path.join(repo_path, file_info['path'])
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    contents.append({
                        'path': file_info['path'],
                        'content': content
                    })
            except (PermissionError, OSError, UnicodeDecodeError) as e:
                print(f"Error reading file {file_path}: {e}")
                continue
                
        return contents
    
    def format_output(self, contents, format_type=None):
        """
        Format the extracted content according to the specified format.
        
        Args:
            contents (list): List of dictionaries containing file paths and content
            format_type (str, optional): Output format type (markdown, json, or plain)
            
        Returns:
            str: Formatted output content
        """
        format_type = format_type or self.output_format
        
        if format_type == "markdown":
            return self._format_markdown(contents)
        elif format_type == "json":
            return self._format_json(contents)
        elif format_type == "plain":
            return self._format_plain(contents)
        else:
            return self._format_markdown(contents)
    
    def _format_markdown(self, contents):
        """Format content as markdown."""
        result = "# Repository Code Compendium\n\n"
        
        files_by_dir = {}
        for file_data in contents:
            path = file_data['path']
            directory = os.path.dirname(path)
            if directory not in files_by_dir:
                files_by_dir[directory] = []
            files_by_dir[directory].append(file_data)
        
        for directory in sorted(files_by_dir.keys()):
            if directory:
                result += f"## Directory: {directory}\n\n"
            else:
                result += "## Root Directory\n\n"
            
            for file_data in sorted(files_by_dir[directory], key=lambda x: x['path']):
                file_name = os.path.basename(file_data['path'])
                file_ext = os.path.splitext(file_name)[1].lstrip('.')
                
                result += f"### File: {file_data['path']}\n\n"
                
                lang = file_ext if file_ext else ""
                result += f"```{lang}\n{file_data['content']}\n```\n\n"
        
        return result
    
    def _format_json(self, contents):
        """Format content as JSON."""
        result = {"repository": []}
        
        for file_data in contents:
            result["repository"].append({
                "path": file_data['path'],
                "content": file_data['content']
            })
        
        return json.dumps(result, indent=2)
    
    def _format_plain(self, contents):
        """Format content as plain text."""
        result = "REPOSITORY CODE COMPENDIUM\n\n"
        
        for file_data in contents:
            result += f"FILE: {file_data['path']}\n"
            result += "=" * (len(file_data['path']) + 6) + "\n\n"
            result += file_data['content'] + "\n\n"
            result += "-" * 80 + "\n\n"
        
        return result
    
    def save_output(self, output_content, output_path):
        """
        Save the formatted output to the specified path.
        
        Args:
            output_content (str): Formatted content to save
            output_path (str): Path to save the output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)