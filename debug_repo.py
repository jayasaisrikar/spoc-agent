#!/usr/bin/env python3
"""
Debug script to test repository processing
"""
import sys
import os
sys.path.append('.')

from repo_handler import RepoHandler

def test_zip_processing(zip_path):
    """Test ZIP file processing with detailed debugging"""
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file not found at {zip_path}")
        return
    
    print(f"Testing ZIP processing for: {zip_path}")
    print("=" * 50)
    
    # Initialize repo handler
    repo_handler = RepoHandler()
    
    # Process the ZIP
    try:
        result = repo_handler.process_repo_zip(zip_path)
        
        print(f"\nProcessing Results:")
        print(f"Total files found: {len(result)}")
        
        if result:
            print("\nFiles processed:")
            for file_path, file_info in result.items():
                print(f"  {file_path} ({file_info.get('type', 'unknown')}) - {file_info.get('size', 0)} bytes")
                if len(file_info.get('content', '')) > 0:
                    print(f"    Content preview: {file_info.get('content', '')[:100]}...")
        else:
            print("No files were processed!")
            
    except Exception as e:
        print(f"Error processing ZIP: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_repo.py <path_to_zip_file>")
        print("Example: python debug_repo.py test-project.zip")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    test_zip_processing(zip_path)
