#!/usr/bin/env python3
"""
Simple script to list all repositories in the knowledge base
"""
from knowledge_base import KnowledgeBase

def main():
    kb = KnowledgeBase()
    repos = kb.list_repositories()
    
    print('📂 Stored Repositories:')
    if repos:
        for repo in repos:
            print(f'  - {repo["name"]} (analyzed: {repo["analyzed_at"]})')
    else:
        print('  No repositories found')

if __name__ == "__main__":
    main()
