#!/usr/bin/env python3
"""
Debug repository file fetching issue
"""
import os
from dotenv import load_dotenv
from repo_handler import RepoHandler
from knowledge_base import KnowledgeBase

def main():
    load_dotenv()
    
    # Get the repo data from knowledge base
    kb = KnowledgeBase()
    stored_data = kb.get_repository_knowledge('jayasaisrikar-bi_dashboard')
    
    print("=== CURRENT STORED DATA ===")
    if stored_data:
        file_contents = stored_data.get('file_contents', {})
        print(f"Files currently stored: {len(file_contents)}")
        for file_path, file_info in file_contents.items():
            print(f"  - {file_path} ({file_info.get('type', 'unknown')}, {file_info.get('size', 0)} bytes)")
    else:
        print("No stored data found")
    
    print("\n=== RE-FETCHING REPOSITORY ===")
    
    # Try to re-fetch the repository
    repo_handler = RepoHandler(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Fetch fresh data
        repo_url = "https://github.com/jayasaisrikar/bi_dashboard"
        print(f"Fetching: {repo_url}")
        
        fresh_data = repo_handler.fetch_github_repo(repo_url)
        
        print(f"Fresh fetch returned: {len(fresh_data)} files")
        print("Files fetched:")
        for file_path, file_info in list(fresh_data.items())[:20]:  # Show first 20 files
            print(f"  - {file_path} ({file_info.get('type', 'unknown')}, {file_info.get('size', 0)} bytes)")
        
        if len(fresh_data) > 20:
            print(f"  ... and {len(fresh_data) - 20} more files")
            
    except Exception as e:
        print(f"Error fetching repository: {e}")
        
        # Try the fallback method
        print("\nTrying fallback method...")
        try:
            fallback_data = repo_handler.fetch_github_repo_fallback(repo_url)
            print(f"Fallback returned: {len(fallback_data)} files")
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")

if __name__ == "__main__":
    main()
