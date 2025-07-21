"""
Test script to check if the knowledge base has any data
"""
import sqlite3
import json

def check_knowledge_base():
    try:
        conn = sqlite3.connect('knowledge_base.db')
        cursor = conn.cursor()
        
        # Check if repositories table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Found tables: {[table[0] for table in tables]}")
        
        # Check repositories
        cursor.execute("SELECT COUNT(*) FROM repositories")
        repo_count = cursor.fetchone()[0]
        print(f"Repositories in knowledge base: {repo_count}")
        
        if repo_count > 0:
            cursor.execute("SELECT repo_name, created_at FROM repositories LIMIT 5")
            repos = cursor.fetchall()
            print("\nSample repositories:")
            for repo in repos:
                print(f"  - {repo[0]} (created: {repo[1]})")
        
        # Check features
        cursor.execute("SELECT COUNT(*) FROM features")
        feature_count = cursor.fetchone()[0]
        print(f"\nFeatures in knowledge base: {feature_count}")
        
        conn.close()
        return repo_count > 0
        
    except Exception as e:
        print(f"Error checking knowledge base: {e}")
        return False

if __name__ == "__main__":
    print("Checking knowledge base...")
    has_data = check_knowledge_base()
    
    if not has_data:
        print("\n⚠️  Knowledge base is empty!")
        print("You can add data by:")
        print("1. Uploading a repository ZIP file")
        print("2. Analyzing a GitHub repository URL")
        print("3. Using the chat interface to analyze code")
    else:
        print("\n✅ Knowledge base has data!")
        print("You can now use the Knowledge Base Visualizer to explore it.")
