#!/usr/bin/env python3
import os
import json
import argparse
import sys
from pathlib import Path
"""
Read all files in a directory and write their contents to a JSON file with file names as keys.
Use from terminal. Example, from /src:

scripts/generate_prompts_json.py resources/chess/raw_prompt_templates resources/chess/prompt_templates.json
"""
def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Read all files in a directory and write their contents to a JSON file with file names as keys."
    )
    parser.add_argument("input_directory", help="Path to the input directory containing text files.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    args = parser.parse_args()

    # Verify that the provided input path is a directory
    if not os.path.isdir(args.input_directory):
        print(f"Error: '{args.input_directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Dictionary to hold file names and their contents
    files_dict = {}

    # Iterate over each entry in the directory
    for entry in os.listdir(args.input_directory):
        file_path = os.path.join(args.input_directory, entry)
        # Process only files (skip subdirectories or other types)
        if os.path.isfile(file_path):
            file_name=Path(entry).stem
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    files_dict[entry] = content
            except Exception as e:
                print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Optionally, you can notify about skipping non-file entries
            print(f"Skipping non-file entry: {file_path}", file=sys.stderr)

    # Write the collected data to the output JSON file
    try:
        with open(args.output_file, "w", encoding="utf-8") as out_file:
            json.dump(files_dict, out_file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to output file '{args.output_file}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully wrote JSON to '{args.output_file}'.")

if __name__ == "__main__":
    main()
