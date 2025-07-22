#!/usr/bin/env python3
"""
Debug memory storage and search
"""
import asyncio
import sys
import os
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ..ai.conversation_manager import ConversationManager

async def debug_memory_search():
    """Debug memory search with different queries"""
    print("🔍 Debugging Memory Search...")
    
    # Initialize
    conv_manager = ConversationManager()
    repo_name = "test_portfolio_app"
    user_id = f"repo_{repo_name}"
    
    if not conv_manager.memory_manager or not conv_manager.memory_manager.memory:
        print("❌ Memory system not available")
        return
    
    # Add test conversation
    print("\n1. Adding test conversation...")
    conv_manager.add_message(repo_name, 'user', 'How do I add a new project to my portfolio?')
    conv_manager.add_message(repo_name, 'assistant', 'To add a new project, you can modify the projects.json file in the data directory.')
    
    # Wait for indexing
    print("Waiting for indexing...")
    time.sleep(5)
    
    # Try different search queries
    search_queries = [
        "project",
        "portfolio",
        "add project",
        "projects.json",
        "how to add",
        "User asked",
        "Assistant responded",
        "data directory",
        "modify"
    ]
    
    print("\n2. Testing different search queries...")
    for query in search_queries:
        try:
            results = conv_manager.memory_manager.memory.search(
                query=query,
                user_id=user_id,
                limit=5
            )
            
            result_count = len(results.get("results", []))
            print(f"Query: '{query}' -> {result_count} results")
            
            if result_count > 0:
                for i, result in enumerate(results.get("results", []), 1):
                    print(f"  {i}. {result.get('memory', 'No memory')[:100]}...")
                    
        except Exception as e:
            print(f"Query: '{query}' -> Error: {e}")
    
    # Try getting all memories
    print("\n3. Trying to get all memories...")
    try:
        all_memories = conv_manager.memory_manager.memory.get_all(user_id=user_id)
        print(f"Total memories found: {len(all_memories)}")
        
        if all_memories:
            for i, memory in enumerate(all_memories[:5], 1):
                print(f"  {i}. {memory.get('memory', 'No memory')[:100]}...")
                
    except Exception as e:
        print(f"Error getting all memories: {e}")

if __name__ == "__main__":
    asyncio.run(debug_memory_search())
