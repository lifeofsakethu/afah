import json
import zipfile
import os
from pathlib import Path

def sjr_to_sb3(sjr_file_path, output_sb3_path):
    """Convert a .sjr file to .sb3 (Scratch 3.0) format"""
    
    # Read the .sjr file (typically JSON)
    with open(sjr_file_path, 'r', encoding='utf-8') as f:
        sjr_data = json.load(f)
    
    # Convert SJR to SB3 format
    sb3_project = convert_sjr_to_sb3_format(sjr_data)
    
    # Create .sb3 file (which is a ZIP archive)
    with zipfile.ZipFile(output_sb3_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write project.json
        zf.writestr('project.json', json.dumps(sb3_project, indent=2))

def convert_sjr_to_sb3_format(sjr_data):
    """Convert SJR structure to SB3 structure"""
    return {
        "targets": sjr_data.get("sprites", []),
        "monitors": sjr_data.get("monitors", []),
        "extensions": sjr_data.get("extensions", []),
        "meta": {
            "semver": "3.0.0",
            "vm": "3.0.0",
            "agent": "Decompiler"
        }
    }

if __name__ == "__main__":
    sjr_file = input("Enter .sjr file path: ")
    output_file = input("Enter output .sb3 file path: ")
    
    try:
        sjr_to_sb3(sjr_file, output_file)
        print(f"Successfully converted {sjr_file} to {output_file}")
    except Exception as e:
        print(f"Error: {e}")