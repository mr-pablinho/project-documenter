# Repository Extractor for LLM Consumption

This application scans a repository, extracts file contents, and formats them for consumption by Large Language Models (LLMs) like Claude. It provides a user interface for selecting which files to include in the final output.

## Features

- Repository scanning with customizable exclusions
- File filtering by patterns
- Selection of files to include in the output
- Multiple output formats (markdown, JSON, plain text)
- GUI and command-line interfaces

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/repo-extractor.git
cd repo-extractor
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### GUI Mode

To use the application with the graphical user interface:

```
python main.py
```

### Command-Line Mode

For command-line usage:

```
python main.py --no-gui --repo /path/to/repository --output /path/to/output.md
```

Additional options:
- `--format`: Output format (markdown, json, plain)
- `--include`: Comma-separated list of file patterns to include
- `--exclude`: Comma-separated list of file patterns to exclude
- `--exclude-folders`: Comma-separated list of folders to exclude

Example:
```
python main.py --no-gui --repo /path/to/repo --output output.md --format markdown --exclude-folders node_modules,dist --include "*.py,*.js"
```

## Project Structure

The application is organized into these modules:

- `main.py`: Entry point and command-line interface
- `extractor.py`: Core repository scanning and extraction logic
- `gui.py`: Graphical user interface implementation
- `utils.py`: Utility functions and constants

## Output Formats

The application supports three output formats:

1. **Markdown**: Organizes code by directory with syntax highlighting
2. **JSON**: Structured data format for programmatic consumption
3. **Plain Text**: Simple text format with clear separators between files

## License

[MIT License](LICENSE)