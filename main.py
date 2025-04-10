#!/usr/bin/env python3
"""
Repository Extractor for LLM Consumption - Main Entry Point

This module serves as the entry point for the Repository Extractor application.
It handles command-line argument parsing and launches either the GUI or CLI mode.
"""

import argparse
import tkinter as tk
import re
from extractor import RepoExtractor
from gui import RepoExtractorGUI

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract code from a repository for LLM consumption.")
    parser.add_argument("--no-gui", action="store_true", help="Run in command-line mode (no GUI)")
    parser.add_argument("--repo", help="Repository path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["markdown", "json", "plain"], default="markdown", 
                        help="Output format (default: markdown)")
    parser.add_argument("--include", help="Comma-separated list of file patterns to include")
    parser.add_argument("--exclude", help="Comma-separated list of file patterns to exclude")
    parser.add_argument("--exclude-folders", help="Comma-separated list of folders to exclude")
    
    args = parser.parse_args()
    
    # Run in GUI mode by default
    if not args.no_gui:
        root = tk.Tk()
        app = RepoExtractorGUI(root)
        root.mainloop()
    else:
        # Command-line mode
        if not args.repo or not args.output:
            print("Error: --repo and --output are required in command-line mode.")
            parser.print_help()
            return
        
        print(f"Scanning repository: {args.repo}")
        extractor = RepoExtractor()
        
        # Set output format
        extractor.output_format = args.format
        
        # Process exclude folders
        excluded_folders = set()
        
        if args.exclude_folders:
            excluded_folders = {folder.strip() for folder in args.exclude_folders.split(',') if folder.strip()}
            print(f"Excluding folders: {', '.join(excluded_folders)}")
        
        # Scan repository with folder exclusions
        files_data = extractor.scan_repository(
            args.repo,
            excluded_folders=excluded_folders
        )
        
        # Filter files by patterns if specified
        if args.include:
            include_patterns = [re.compile(pattern) for pattern in args.include.split(',')]
            files_data = [f for f in files_data 
                         if any(pattern.search(f['path']) for pattern in include_patterns)]
        
        if args.exclude:
            exclude_patterns = [re.compile(pattern) for pattern in args.exclude.split(',')]
            files_data = [f for f in files_data 
                         if not any(pattern.search(f['path']) for pattern in exclude_patterns)]
        
        print(f"Found {len(files_data)} files matching criteria.")
        
        # Extract content
        contents = extractor.extract_files_content(args.repo, files_data)
        
        # Format and save output
        output_content = extractor.format_output(contents, args.format)
        extractor.save_output(output_content, args.output)
        
        print(f"Compendium generated successfully at {args.output}")
        

if __name__ == "__main__":
    main()