#!/usr/bin/env python3
"""
Quick solution to re-analyze repository with complete file access
"""
import os
from knowledge_base import KnowledgeBase

def main():
    print("🔄 Repository File Access Issue - Quick Solutions")
    print("=" * 60)
    
    kb = KnowledgeBase()
    
    print("\n📋 Current Issue:")
    print("- GitHub API is rate-limited (403 errors)")
    print("- Only 3 files were fetched instead of the complete repository")
    print("- This limits the AI's ability to provide accurate analysis")
    
    print("\n🎯 Recommended Solutions:")
    print("\n1. 📁 ZIP Upload (FASTEST - Recommended)")
    print("   - Go to https://github.com/jayasaisrikar/bi_dashboard")
    print("   - Click the green 'Code' button")
    print("   - Select 'Download ZIP'")
    print("   - Use the web interface to upload the ZIP file")
    print("   - This will give complete access to ALL files instantly")
    
    print("\n2. 🔑 GitHub Token (Alternative)")
    print("   - Create a GitHub Personal Access Token")
    print("   - Add it to your .env file as GITHUB_TOKEN")
    print("   - This increases API rate limits")
    
    print("\n3. 🕐 Wait and Retry (Slow)")
    print("   - GitHub API rate limits reset hourly")
    print("   - You could wait and try again later")
    
    print("\n💡 For now, you can:")
    print("   - Ask general questions about the repository")
    print("   - The AI will provide general guidance based on the package.json")
    print("   - For specific file analysis, use the ZIP upload method")
    
    print("\n🚀 To use ZIP upload:")
    print("   1. Download the repository as ZIP from GitHub")
    print("   2. Go to your web interface (http://localhost:8000)")
    print("   3. Use 'Upload ZIP' instead of 'Repository URL'")
    print("   4. Select the downloaded ZIP file")
    print("   5. Get complete repository analysis instantly!")
    
    # Also show what we have now
    print(f"\n📊 Current Repository Data:")
    data = kb.get_repository_knowledge('jayasaisrikar-bi_dashboard')
    if data:
        files = data.get('file_contents', {})
        print(f"   Files stored: {len(files)}")
        for file_path in files.keys():
            print(f"   - {file_path}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
