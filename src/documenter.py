import os
import argparse
from utils import get_directory_structure, create_markdown_from_structure, parse_gitignore, build_tree_string

def create_markdown_for_directory(rootdir, output_file):
    """
    Creates a markdown file with the directory structure and content of all files.
    """
    gitignore_path = os.path.join(rootdir, '.gitignore')
    ignore_patterns = parse_gitignore(gitignore_path) if os.path.exists(gitignore_path) else []
    structure = get_directory_structure(rootdir, ignore_patterns)
    
    with open(output_file, 'w') as markdown_file:
        # Write the project tree at the beginning of the file
        tree_string = build_tree_string(structure)
        markdown_file.write("# Project Tree\n\n")
        markdown_file.write(f"```\n{tree_string}\n```\n\n")
        
        # Write the detailed contents
        create_markdown_from_structure(structure, rootdir, markdown_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a Markdown file documenting the structure and content of a directory.')
    parser.add_argument('directory', type=str, help='The root directory of the project to document.')
    parser.add_argument('output', type=str, help='The output Markdown file.')
    
    args = parser.parse_args()
    
    root_directory = args.directory
    output_markdown_file = args.output
    
    if os.path.isdir(root_directory):
        create_markdown_for_directory(root_directory, output_markdown_file)
        print(f"Markdown file created: {output_markdown_file}")
    else:
        print(f"Error: The directory '{root_directory}' does not exist.")
