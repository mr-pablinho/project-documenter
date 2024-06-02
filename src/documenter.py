import os
import argparse
from utils import get_directory_structure, create_markdown_from_structure

def create_markdown_for_directory(rootdir, output_file):
    """
    Creates a markdown file with the directory structure and content of all files.
    """
    structure = get_directory_structure(rootdir)
    with open(output_file, 'w') as markdown_file:
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
