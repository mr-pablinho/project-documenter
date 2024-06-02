import os
import fnmatch

def parse_gitignore(gitignore_path):
    """
    Parses the .gitignore file and returns a list of patterns to ignore.
    """
    with open(gitignore_path, 'r') as file:
        patterns = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return patterns

def matches_pattern(path, patterns):
    """
    Checks if the given path matches any of the ignore patterns.
    """
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, os.path.join('**', pattern)):
            return True
    return False

def get_directory_structure(rootdir, ignore_patterns=None):
    """
    Creates a nested dictionary that represents the folder structure of rootdir.
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    dir_structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        # Get the relative path
        relative_dir = os.path.relpath(dirpath, rootdir)
        
        # Filter out hidden directories and ignored directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and not matches_pattern(os.path.join(relative_dir, d), ignore_patterns)]
        # Filter out hidden files and ignored files
        filenames = [f for f in filenames if not f.startswith('.') and not matches_pattern(os.path.join(relative_dir, f), ignore_patterns)]
        
        # Build the directory structure
        subdir = dir_structure
        if relative_dir != ".":
            for part in relative_dir.split(os.sep):
                subdir = subdir.setdefault(part, {})
        subdir.update({file: None for file in filenames})
    return dir_structure

def create_markdown_from_structure(structure, rootdir, markdown_file, indent=0):
    """
    Recursively writes the folder structure and file contents to the markdown file.
    """
    for key, value in structure.items():
        if value is None:
            # It's a file, write its content
            file_path = os.path.join(rootdir, key)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue

            markdown_file.write(f"{'    ' * indent}- {key}\n\n")
            markdown_file.write(f"```{get_file_extension(key)}\n")
            markdown_file.write(content)
            markdown_file.write("\n```\n\n")
        else:
            # It's a directory, write its name and recurse
            markdown_file.write(f"{'    ' * indent}- {key}/\n\n")
            create_markdown_from_structure(value, os.path.join(rootdir, key), markdown_file, indent + 1)

def get_file_extension(filename):
    """
    Returns the file extension without the leading dot.
    """
    return filename.split('.')[-1] if '.' in filename else ''
