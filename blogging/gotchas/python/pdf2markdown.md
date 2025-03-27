# Requirement
Assume you have a PDF file and you need to convert it to markdown.

# Steps 
1. `pip install pdfminer.six`
2. Code
```python
from pdfminer.high_level import extract_text

def pdf_to_markdown(pdf_path, md_path):
    text = extract_text(pdf_path)
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(text)

pdf_to_markdown("/Users/kkailasnath/Downloads/aider.pdf", "/Users/kkailasnath/Downloads/aider.md")
```
3. Use some AI assistant tool like Gemini or co-pilot to refine it.

Sample Prompt
```
reformat the aider.md file. Add suitable markdown headings and bullet points. Remove unnecessary white spaces and replace special character bullets with standard markdown bullets. Return result as a markdown file
```
