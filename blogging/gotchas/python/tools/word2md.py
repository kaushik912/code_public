import subprocess
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Convert a Word document to Markdown.")
parser.add_argument("input_file", help="Path to the input Word (.docx) file")
parser.add_argument("output_file", help="Path to the output Markdown (.md) file")

# Parse arguments
args = parser.parse_args()
input_file = args.input_file
output_file = args.output_file

# Run pandoc command
subprocess.run(["pandoc", input_file, "-t", "markdown", "-o", output_file])

print("Conversion completed!")

""" Example Usage
1. Export confluence page as a word file
2. Run this script to convert docx to markdown
3. python /Users/kkailasnath/projects/genai/agentive-workflow/kkailasnath-testing/tools/word2md.py /Users/kkailasnath/Downloads/asf.docx /Users/kkailasnath/Downloads/asf.md

"""
# Note: Ensure that pandoc is installed and available in your PATH.
# You can install pandoc using Homebrew on macOS:
# brew install pandoc   