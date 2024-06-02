import os

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir.
    """
    dir_structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        # Get the relative path
        folder = os.path.relpath(dirpath, rootdir)
        subdir = dir_structure
        if folder != ".":
            for part in folder.split(os.sep):
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
            with open(file_path, 'r') as file:
                content = file.read()
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
