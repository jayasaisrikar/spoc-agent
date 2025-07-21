#!/usr/bin/env python3
"""
Test script to debug file extraction issues
"""

import zipfile
import os
from typing import Dict

def debug_zip_extraction(zip_path: str) -> Dict:
    """Debug what files are being extracted from ZIP"""
    
    print(f"Debugging ZIP file: {zip_path}")
    
    # First, list all files in the ZIP
    print("\n=== FILES IN ZIP ===")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        for file_name in file_list:
            print(f"  {file_name}")
    
    print(f"\nTotal files in ZIP: {len(file_list)}")
    
    # Extract to temp directory
    extract_dir = './temp_debug_repo'
    if os.path.exists(extract_dir):
        import shutil
        shutil.rmtree(extract_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Walk through extracted files
    print(f"\n=== EXTRACTED FILES ===")
    all_files = []
    for root, dirs, files in os.walk(extract_dir):
        print(f"Directory: {root}")
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, extract_dir)
            relative_path = relative_path.replace('\\', '/')
            all_files.append(relative_path)
            print(f"  {relative_path}")
    
    print(f"\nTotal extracted files: {len(all_files)}")
    
    # Test file extension matching
    print(f"\n=== FILE EXTENSION ANALYSIS ===")
    source_extensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.go', '.rs']
    
    for file_path in all_files:
        is_source = any(file_path.lower().endswith(ext) for ext in source_extensions)
        print(f"  {file_path} -> Source file: {is_source}")
    
    # Cleanup
    import shutil
    shutil.rmtree(extract_dir)
    
    return {"files": all_files}

if __name__ == "__main__":
    # Test with the sample zip file
    test_zip = "test-project.zip"
    if os.path.exists(test_zip):
        debug_zip_extraction(test_zip)
    else:
        print(f"Test ZIP file '{test_zip}' not found")
        print("Available files:")
        for file in os.listdir('.'):
            if file.endswith('.zip'):
                print(f"  {file}")
