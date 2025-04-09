#!/usr/bin/env python3
"""
Repository Extractor for LLM Consumption

This program scans a repository, extracts file contents, and formats them
for consumption by Large Language Models (LLMs) like Claude. It provides
a user interface for selecting which files to include in the final output.
"""

import os
import argparse
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from pathlib import Path
import re


class RepoExtractor:
    def __init__(self):
        self.files_data = []
        # Default ignored directories
        self.ignored_dirs = set([
            '.git', '.github', 'node_modules', '__pycache__', 
            'venv', '.venv', 'env', '.env', 'dist', 'build',
            '.idea', '.vscode', '.gradle', 'target', 'bin',
            'obj', 'out', 'ios', 'android', 'public', 'tmp'
        ])
        # Common binary file extensions to ignore
        self.ignored_extensions = set([
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.o', '.a', '.lib', '.zip', 
            '.tar', '.gz', '.7z', '.jar', '.war', '.ear', '.class', '.log', '.bin', 
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.mp3', '.mp4', 
            '.avi', '.mov', '.flv', '.wmv', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.db', '.sqlite', '.sqlite3', '.dat', '.min.js', '.min.css',
            '.ttf', '.woff', '.woff2', '.eot', '.lock'
        ])
        # Add common config for max file size (e.g., 1MB)
        self.max_file_size = 1024 * 1024  # 1MB
        # Default output format
        self.output_format = "markdown"
        
    def scan_repository(self, repo_path, excluded_folders=None, included_folders=None):
        """Scan repository and collect file information."""
        self.files_data = []
        excluded_folders = excluded_folders or set()
        included_folders = included_folders or set()
        has_included_folders = bool(included_folders)
        
        for root, dirs, files in os.walk(repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            # Skip excluded folders or only include specified folders if included_folders is set
            rel_root = os.path.relpath(root, repo_path)
            if rel_root == '.':
                rel_root = ''
                
            # Skip this directory if it's in excluded folders
            if any(rel_root == folder or rel_root.startswith(folder + os.path.sep) for folder in excluded_folders):
                dirs[:] = []
                continue
                
            # Skip this directory if we have included folders but this one isn't in the list
            if has_included_folders and rel_root and not any(rel_root == folder or rel_root.startswith(folder + os.path.sep) for folder in included_folders):
                dirs[:] = []
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                # Skip files with ignored extensions
                _, ext = os.path.splitext(file)
                if ext.lower() in self.ignored_extensions:
                    continue
                
                # Skip files that are too large
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.max_file_size:
                        continue
                        
                    # Try to detect if it's a text file
                    if self._is_text_file(file_path):
                        self.files_data.append({
                            'path': rel_path,
                            'size': file_size,
                            'selected': True  # Default to selected
                        })
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
        
        # Sort files by path for better organization
        self.files_data.sort(key=lambda x: x['path'])
        return self.files_data
    
    def _is_text_file(self, file_path):
        """Detect if a file is a text file by reading a small sample."""
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
    
    def extract_files_content(self, repo_path, selected_files):
        """Extract content from selected files."""
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
    
    def format_output(self, contents, format_type="markdown"):
        """Format the extracted content according to the specified format."""
        if format_type == "markdown":
            return self._format_markdown(contents)
        elif format_type == "json":
            return self._format_json(contents)
        elif format_type == "plain":
            return self._format_plain(contents)
        else:
            return self._format_markdown(contents)  # Default to markdown
    
    def _format_markdown(self, contents):
        """Format content as markdown."""
        result = "# Repository Code Compendium\n\n"
        
        # Group files by directory
        files_by_dir = {}
        for file_data in contents:
            path = file_data['path']
            directory = os.path.dirname(path)
            if directory not in files_by_dir:
                files_by_dir[directory] = []
            files_by_dir[directory].append(file_data)
        
        # Process each directory
        for directory in sorted(files_by_dir.keys()):
            if directory:
                result += f"## Directory: {directory}\n\n"
            else:
                result += "## Root Directory\n\n"
            
            # Process files in this directory
            for file_data in sorted(files_by_dir[directory], key=lambda x: x['path']):
                file_name = os.path.basename(file_data['path'])
                file_ext = os.path.splitext(file_name)[1].lstrip('.')
                
                result += f"### File: {file_data['path']}\n\n"
                
                # Use appropriate language for syntax highlighting if possible
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
        """Save the formatted output to the specified path."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)


class RepoExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Repository Extractor for LLMs")
        self.root.geometry("900x800")
        
        self.repo_extractor = RepoExtractor()
        self.repo_path = None
        self.output_path = None
        self.files_data = []
        self.excluded_folders = set()
        self.included_folders = set()
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository selection frame
        repo_frame = ttk.LabelFrame(main_frame, text="Repository Selection", padding="10")
        repo_frame.pack(fill=tk.X, pady=5)
        
        self.repo_path_var = tk.StringVar()
        ttk.Label(repo_frame, text="Repository Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(repo_frame, textvariable=self.repo_path_var, width=60).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(repo_frame, text="Browse...", command=self._browse_repo).grid(row=0, column=2, pady=5)
        ttk.Button(repo_frame, text="Scan Repository", command=self._scan_repo).grid(row=0, column=3, padx=5, pady=5)
        
        # Folder inclusion/exclusion frame
        folder_frame = ttk.LabelFrame(main_frame, text="Folder Inclusion/Exclusion", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)
        
        # Include folders
        include_frame = ttk.Frame(folder_frame)
        include_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(include_frame, text="Include Folders (comma separated):").pack(side=tk.LEFT, padx=5)
        self.include_folders_var = tk.StringVar()
        ttk.Entry(include_frame, textvariable=self.include_folders_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(include_frame, text="(empty = include all)").pack(side=tk.LEFT, padx=5)
        
        # Exclude folders
        exclude_frame = ttk.Frame(folder_frame)
        exclude_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exclude_frame, text="Exclude Folders (comma separated):").pack(side=tk.LEFT, padx=5)
        self.exclude_folders_var = tk.StringVar()
        ttk.Entry(exclude_frame, textvariable=self.exclude_folders_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button to apply folder filters
        ttk.Button(folder_frame, text="Apply Folder Filters", command=self._apply_folder_filters).pack(pady=5)
        
        # Files selection frame
        files_frame = ttk.LabelFrame(main_frame, text="Select Files to Include", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Files treeview with scrollbars
        self.tree_frame = ttk.Frame(files_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for files
        self.tree = ttk.Treeview(self.tree_frame, 
                                 columns=("path", "size", "selected"),
                                 show="headings",
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        self.tree.heading("path", text="File Path")
        self.tree.heading("size", text="Size (KB)")
        self.tree.heading("selected", text="Selected")
        
        self.tree.column("path", width=500, stretch=tk.YES)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("selected", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # File selection buttons
        btn_frame = ttk.Frame(files_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Toggle Selected", command=self._toggle_selected).pack(side=tk.LEFT, padx=5)
        
        # Filter frame
        filter_frame = ttk.Frame(files_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=40)
        self.filter_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.filter_entry.bind("<KeyRelease>", self._apply_filter)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self._apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear Filter", command=self._clear_filter).pack(side=tk.LEFT, padx=5)
        
        # Output format selection
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=5)
        self.format_var = tk.StringVar(value="markdown")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                    values=["markdown", "json", "plain"],
                                    state="readonly", width=15)
        format_combo.pack(side=tk.LEFT, padx=5)
        
        # Output selection frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Selection", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        self.output_path_var = tk.StringVar()
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=60).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self._browse_output).grid(row=0, column=2, pady=5)
        
        # Generate button
        ttk.Button(main_frame, text="Generate LLM Compendium", command=self._generate_output).pack(pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click to toggle selection
        self.tree.bind("<Double-1>", self._toggle_item)
    
    def _browse_repo(self):
        """Browse for repository directory."""
        repo_path = filedialog.askdirectory(title="Select Repository Directory")
        if repo_path:
            self.repo_path = repo_path
            self.repo_path_var.set(repo_path)
            
            # Suggest output file name based on repository name
            repo_name = os.path.basename(repo_path)
            output_format = self.format_var.get()
            extension = ".md" if output_format == "markdown" else ".json" if output_format == "json" else ".txt"
            self.output_path_var.set(os.path.join(os.path.expanduser("~"), f"{repo_name}_compendium{extension}"))
            
            # Also do an immediate scan
            self._scan_repo()
    
    def _browse_output(self):
        """Browse for output file."""
        formats = {
            "markdown": [("Markdown files", "*.md"), ("Text files", "*.txt")],
            "json": [("JSON files", "*.json")],
            "plain": [("Text files", "*.txt")]
        }
        
        selected_format = self.format_var.get()
        filetypes = formats.get(selected_format, [("All files", "*.*")])
        
        output_path = filedialog.asksaveasfilename(
            title="Save Compendium As",
            filetypes=filetypes,
            defaultextension=".md" if selected_format == "markdown" else ".json" if selected_format == "json" else ".txt"
        )
        
        if output_path:
            self.output_path = output_path
            self.output_path_var.set(output_path)
    
    def _scan_repo(self):
        """Scan the repository and populate the file list."""
        repo_path = self.repo_path_var.get()
        if not repo_path:
            messagebox.showerror("Error", "Please select a repository path first.")
            return
        
        if not os.path.isdir(repo_path):
            messagebox.showerror("Error", "The selected path is not a valid directory.")
            return
        
        # Store the repository path
        self.repo_path = repo_path
        
        # Process include/exclude folders
        excluded_folders = set()
        included_folders = set()
        
        if self.exclude_folders_var.get().strip():
            excluded_folders = {folder.strip() for folder in self.exclude_folders_var.get().split(',') if folder.strip()}
        
        if self.include_folders_var.get().strip():
            included_folders = {folder.strip() for folder in self.include_folders_var.get().split(',') if folder.strip()}
        
        self.excluded_folders = excluded_folders
        self.included_folders = included_folders
        
        self.status_var.set("Scanning repository...")
        self.root.update_idletasks()
        
        try:
            self.files_data = self.repo_extractor.scan_repository(
                repo_path, 
                excluded_folders=excluded_folders,
                included_folders=included_folders
            )
            self._update_tree()
            
            # Show info about included/excluded folders in status
            status_msg = f"Found {len(self.files_data)} files in repository."
            if excluded_folders:
                status_msg += f" (Excluded {len(excluded_folders)} folders)"
            if included_folders:
                status_msg += f" (Limited to {len(included_folders)} folders)"
            
            self.status_var.set(status_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan repository: {str(e)}")
            self.status_var.set("Ready")
    
    def _apply_folder_filters(self):
        """Apply folder filters to the existing scanned repository data."""
        if not self.repo_path or not self.files_data:
            messagebox.showerror("Error", "Please scan a repository first.")
            return
            
        # Process include/exclude folders
        excluded_folders = set()
        included_folders = set()
        
        if self.exclude_folders_var.get().strip():
            excluded_folders = {folder.strip() for folder in self.exclude_folders_var.get().split(',') if folder.strip()}
        
        if self.include_folders_var.get().strip():
            included_folders = {folder.strip() for folder in self.include_folders_var.get().split(',') if folder.strip()}
        
        self.excluded_folders = excluded_folders
        self.included_folders = included_folders
        
        self.status_var.set("Applying folder filters...")
        self.root.update_idletasks()
        
        try:
            # Rescan with the new folder filters
            self.files_data = self.repo_extractor.scan_repository(
                self.repo_path, 
                excluded_folders=excluded_folders,
                included_folders=included_folders
            )
            self._update_tree()
            
            # Show info about included/excluded folders in status
            status_msg = f"Applied filters: Found {len(self.files_data)} files in repository."
            if excluded_folders:
                status_msg += f" (Excluded {len(excluded_folders)} folders)"
            if included_folders:
                status_msg += f" (Limited to {len(included_folders)} folders)"
            
            self.status_var.set(status_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply folder filters: {str(e)}")
            self.status_var.set("Ready")
    
    def _update_tree(self, filter_text=None):
        """Update the treeview with file data, optionally filtered."""
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add data to the treeview
        for file_info in self.files_data:
            # Apply filter if specified
            if filter_text and filter_text.lower() not in file_info['path'].lower():
                continue
                
            values = (
                file_info['path'],
                f"{file_info['size'] / 1024:.2f}",
                "✓" if file_info['selected'] else "✗"
            )
            self.tree.insert("", tk.END, values=values)
    
    def _toggle_item(self, event):
        """Toggle the selected state of a clicked item."""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        # Get current values
        values = self.tree.item(item, "values")
        path = values[0]
        
        # Find and toggle the corresponding file data
        for file_info in self.files_data:
            if file_info['path'] == path:
                file_info['selected'] = not file_info['selected']
                
                # Update the treeview
                new_values = (
                    path,
                    values[1],
                    "✓" if file_info['selected'] else "✗"
                )
                self.tree.item(item, values=new_values)
                break
    
    def _select_all(self):
        """Select all files."""
        for file_info in self.files_data:
            file_info['selected'] = True
        self._update_tree(self.filter_var.get())
    
    def _deselect_all(self):
        """Deselect all files."""
        for file_info in self.files_data:
            file_info['selected'] = False
        self._update_tree(self.filter_var.get())
    
    def _toggle_selected(self):
        """Toggle selection for all files."""
        for file_info in self.files_data:
            file_info['selected'] = not file_info['selected']
        self._update_tree(self.filter_var.get())
    
    def _apply_filter(self, event=None):
        """Apply filter to the file list."""
        filter_text = self.filter_var.get()
        self._update_tree(filter_text)
    
    def _clear_filter(self):
        """Clear the filter."""
        self.filter_var.set("")
        self._update_tree()
    
    def _generate_output(self):
        """Generate the output file with selected files."""
        repo_path = self.repo_path_var.get()
        output_path = self.output_path_var.get()
        
        if not repo_path:
            messagebox.showerror("Error", "Please select a repository path.")
            return
            
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file path.")
            return
        
        # Get selected files
        selected_files = [f for f in self.files_data if f['selected']]
        
        if not selected_files:
            messagebox.showerror("Error", "No files selected for inclusion.")
            return
        
        self.status_var.set("Generating compendium...")
        self.root.update_idletasks()
        
        try:
            # Extract content from selected files
            contents = self.repo_extractor.extract_files_content(repo_path, selected_files)
            
            # Format the output according to selected format
            output_format = self.format_var.get()
            output_content = self.repo_extractor.format_output(contents, output_format)
            
            # Save the output
            self.repo_extractor.save_output(output_content, output_path)
            
            self.status_var.set(f"Compendium generated successfully with {len(contents)} files.")
            messagebox.showinfo("Success", f"Compendium generated successfully at {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate compendium: {str(e)}")
            self.status_var.set("Ready")


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
    parser.add_argument("--include-folders", help="Comma-separated list of folders to include (empty = include all)")
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
        
        # Process include/exclude folders
        excluded_folders = set()
        included_folders = set()
        
        if args.exclude_folders:
            excluded_folders = {folder.strip() for folder in args.exclude_folders.split(',') if folder.strip()}
            print(f"Excluding folders: {', '.join(excluded_folders)}")
            
        if args.include_folders:
            included_folders = {folder.strip() for folder in args.include_folders.split(',') if folder.strip()}
            print(f"Including only folders: {', '.join(included_folders)}")
        
        # Scan repository with folder filters
        files_data = extractor.scan_repository(
            args.repo,
            excluded_folders=excluded_folders,
            included_folders=included_folders
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