"""
Repository Extractor for LLM Consumption - GUI

This module contains the GUI implementation for the Repository Extractor application.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from extractor import RepoExtractor

class RepoExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Repository Extractor for LLMs")
        self.root.geometry("960x800")
        
        # Configure root grid to properly expand
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.repo_extractor = RepoExtractor()
        self.repo_path = None
        self.output_path = None
        self.files_data = []
        self.excluded_folders = set()
        
        # Define application font - same font for all components
        self.app_font = ("Arial", 10)
        
        # Apply font to root to cascade to standard widgets
        self.root.option_add("*Font", self.app_font)
        
        # Create theme configuration for consistency
        style = ttk.Style()
        style.configure(".", font=self.app_font)  # Default font for all ttk widgets
        style.configure("TButton", padding=5, font=self.app_font)
        style.configure("TFrame", padding=5)
        style.configure("TLabelframe", padding=8)
        style.configure("TLabelframe.Label", font=self.app_font)
        style.configure("Treeview", font=self.app_font)
        style.configure("Treeview.Heading", font=self.app_font)
        style.configure("TLabel", font=self.app_font)
        style.configure("TEntry", font=self.app_font)
        style.configure("TCombobox", font=self.app_font)
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container frame with padding
        main_container = ttk.Frame(self.root, padding=10)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        
        current_row = 0
        
        # Repository selection frame
        repo_frame = ttk.LabelFrame(main_container, text="Repository Selection", padding=10)
        repo_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        repo_frame.columnconfigure(1, weight=1)
        
        self.repo_path_var = tk.StringVar()
        ttk.Label(repo_frame, text="Repository Path:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        ttk.Entry(repo_frame, textvariable=self.repo_path_var, width=60).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Button frame for repository actions (aligned right)
        repo_btn_frame = ttk.Frame(repo_frame)
        repo_btn_frame.grid(row=0, column=2, sticky="e", padx=(5, 0), pady=5)
        ttk.Button(repo_btn_frame, text="Browse...", command=self._browse_repo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(repo_btn_frame, text="Scan Repository", command=self._scan_repo).pack(side=tk.LEFT)
        
        current_row += 1
        
        # Folder exclusion frame
        folder_frame = ttk.LabelFrame(main_container, text="Folder Exclusion", padding=10)
        folder_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)
        
        # Exclude folders
        ttk.Label(folder_frame, text="Exclude Folders:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        self.exclude_folders_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.exclude_folders_var, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(folder_frame, text="(comma separated)").grid(row=0, column=2, sticky="w", padx=(0, 5), pady=5)
        ttk.Button(folder_frame, text="Apply Exclusions", command=self._apply_folder_filters).grid(row=0, column=3, padx=(5, 0), pady=5)
        
        current_row += 1
        
        # Files selection frame - with the most space allocation
        files_frame = ttk.LabelFrame(main_container, text="Select Files to Include", padding=10)
        files_frame.grid(row=current_row, column=0, sticky="nsew", pady=(0, 10))
        
        # Configure files frame to expand
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        main_container.rowconfigure(current_row, weight=1)
        
        # Control buttons and filter at the top of files frame
        controls_frame = ttk.Frame(files_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        controls_frame.columnconfigure(1, weight=1)
        
        # File selection buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=0, column=0, sticky="w")
        ttk.Button(btn_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Toggle Selected", command=self._toggle_selected).pack(side=tk.LEFT)
        
        # Filter frame (aligned right)
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=30)
        self.filter_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_entry.bind("<KeyRelease>", self._apply_filter)
        
        filter_btn_frame = ttk.Frame(filter_frame)
        filter_btn_frame.pack(side=tk.LEFT)
        ttk.Button(filter_btn_frame, text="Apply", command=self._apply_filter).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_btn_frame, text="Clear", command=self._clear_filter).pack(side=tk.LEFT)
        
        # Files treeview with scrollbars inside a frame
        self.tree_frame = ttk.Frame(files_frame)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Treeview for files with modern appearance
        self.tree = ttk.Treeview(self.tree_frame, 
                                columns=("path", "size", "selected"),
                                show="headings",
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set)
        
        self.tree.heading("path", text="File Path")
        self.tree.heading("size", text="Size (KB)")
        self.tree.heading("selected", text="Selected")
        
        self.tree.column("path", width=550, stretch=tk.YES)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("selected", width=100, anchor=tk.CENTER)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        current_row += 1
        
        # Output configuration frame
        output_config_frame = ttk.Frame(main_container)
        output_config_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        output_config_frame.columnconfigure(1, weight=1)
        
        # Output format selection
        ttk.Label(output_config_frame, text="Output Format:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        self.format_var = tk.StringVar(value="markdown")
        format_combo = ttk.Combobox(output_config_frame, textvariable=self.format_var, 
                                   values=["markdown", "json", "plain"],
                                   state="readonly", width=15)
        format_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        current_row += 1
        
        # Output selection frame
        output_frame = ttk.LabelFrame(main_container, text="Output Selection", padding=10)
        output_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        self.output_path_var = tk.StringVar()
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=60).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self._browse_output).grid(row=0, column=2, sticky="e", padx=(5, 0), pady=5)
        
        current_row += 1
        
        # Generate button (centered)
        generate_frame = ttk.Frame(main_container)
        generate_frame.grid(row=current_row, column=0, pady=10)
        
        generate_btn = ttk.Button(generate_frame, text="Generate LLM Compendium", 
                               command=self._generate_output)
        # Add some padding to make the button more prominent without changing the font
        generate_btn.pack(pady=5, ipady=5, ipadx=10)
        
        # Status bar at the bottom of the window
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, 
                              anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, sticky="ew")
        
        # Bind double-click to toggle selection
        self.tree.bind("<Double-1>", self._toggle_item)
        
        # Bind format change to update output file extension
        format_combo.bind("<<ComboboxSelected>>", self._update_output_extension)
    
    def _update_output_extension(self, event=None):
        """Update the output file extension when format changes."""
        current_output = self.output_path_var.get()
        if not current_output:
            return
            
        # Get new extension based on format
        format_type = self.format_var.get()
        new_ext = ".md" if format_type == "markdown" else ".json" if format_type == "json" else ".txt"
        
        # Replace extension in current path
        path_without_ext = os.path.splitext(current_output)[0]
        new_path = path_without_ext + new_ext
        
        self.output_path_var.set(new_path)
    
    def _browse_repo(self):
        """Browse for repository directory."""
        repo_path = filedialog.askdirectory(title="Select Repository Directory")
        if repo_path:
            self.repo_path = repo_path
            self.repo_path_var.set(repo_path)
            
            # Suggest output file name and location based on repository
            repo_name = os.path.basename(repo_path)
            output_format = self.format_var.get()
            extension = ".md" if output_format == "markdown" else ".json" if output_format == "json" else ".txt"
            
            # Create output in a compendium directory inside the repository
            compendium_dir = os.path.join(repo_path, "compendium")
            os.makedirs(compendium_dir, exist_ok=True)
            
            self.output_path_var.set(os.path.join(compendium_dir, f"{repo_name}_compendium{extension}"))
            
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
        
        # Process exclude folders
        excluded_folders = set()
        
        if self.exclude_folders_var.get().strip():
            excluded_folders = {folder.strip() for folder in self.exclude_folders_var.get().split(',') if folder.strip()}
        
        self.excluded_folders = excluded_folders
        
        self.status_var.set("Scanning repository...")
        self.root.update_idletasks()
        
        try:
            self.files_data = self.repo_extractor.scan_repository(
                repo_path, 
                excluded_folders=excluded_folders
            )
            self._update_tree()
            
            # Show info about excluded folders in status
            status_msg = f"Found {len(self.files_data)} files in repository."
            if excluded_folders:
                status_msg += f" (Excluded {len(excluded_folders)} folders)"
            
            self.status_var.set(status_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan repository: {str(e)}")
            self.status_var.set("Ready")
    
    def _apply_folder_filters(self):
        """Apply folder exclusion filters to the existing scanned repository data."""
        if not self.repo_path or not self.files_data:
            messagebox.showerror("Error", "Please scan a repository first.")
            return
            
        # Process exclude folders
        excluded_folders = set()
        
        if self.exclude_folders_var.get().strip():
            excluded_folders = {folder.strip() for folder in self.exclude_folders_var.get().split(',') if folder.strip()}
        
        self.excluded_folders = excluded_folders
        
        self.status_var.set("Applying folder exclusions...")
        self.root.update_idletasks()
        
        try:
            # Rescan with the new folder exclusions
            self.files_data = self.repo_extractor.scan_repository(
                self.repo_path, 
                excluded_folders=excluded_folders
            )
            self._update_tree()
            
            # Show info about excluded folders in status
            status_msg = f"Applied exclusions: Found {len(self.files_data)} files in repository."
            if excluded_folders:
                status_msg += f" (Excluded {len(excluded_folders)} folders)"
            
            self.status_var.set(status_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply folder exclusions: {str(e)}")
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