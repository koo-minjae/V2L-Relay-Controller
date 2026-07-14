"""
Convert all markdown files in this directory to Word (.docx) using Pandoc.
Produces well-formatted documents with proper tables, code blocks, and headings.
"""

import os
import glob
import pypandoc

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_file(md_path):
    """Convert a single markdown file to docx."""
    basename = os.path.splitext(os.path.basename(md_path))[0]
    docx_path = os.path.join(os.path.dirname(md_path), f"{basename}.docx")

    print(f"  {os.path.basename(md_path)} -> {os.path.basename(docx_path)}")

    try:
        pypandoc.convert_file(
            md_path,
            'docx',
            outputfile=docx_path,
            extra_args=[
                '--standalone',
                '--columns=100',
            ]
        )
        size_kb = os.path.getsize(docx_path) / 1024
        print(f"    OK ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"    FAILED: {e}")
        return False


def main():
    md_files = sorted(glob.glob(os.path.join(SCRIPT_DIR, "*.md")))

    if not md_files:
        print("No markdown files found.")
        return

    print(f"Converting {len(md_files)} markdown file(s) to .docx:\n")

    success_count = 0
    for md_file in md_files:
        if convert_file(md_file):
            success_count += 1

    print(f"\nDone: {success_count}/{len(md_files)} converted successfully.")


if __name__ == "__main__":
    main()
