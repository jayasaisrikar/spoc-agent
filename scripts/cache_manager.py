#!/usr/bin/env python3
"""
Cache management utility for clearing old or irrelevant cache entries
"""
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any


def analyze_cache_entries(cache_dir: str = "cache") -> Dict[str, Any]:
    """Analyze cache entries for relevance and age"""
    if not os.path.exists(cache_dir):
        return {"error": "Cache directory does not exist"}
    
    entries = []
    total_size = 0
    expired_count = 0
    
    for filename in os.listdir(cache_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(cache_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_size = os.path.getsize(filepath)
            total_size += file_size
            
            # Check age
            timestamp = datetime.fromisoformat(data['timestamp'])
            age_hours = (datetime.now() - timestamp).total_seconds() / 3600
            
            # Check if expired (default 24 hours)
            is_expired = age_hours > 24
            if is_expired:
                expired_count += 1
            
            entries.append({
                'filename': filename,
                'size': file_size,
                'age_hours': round(age_hours, 2),
                'model': data.get('model', 'unknown'),
                'prompt_preview': data.get('prompt', '')[:100],
                'response_length': len(data.get('response', '')),
                'is_expired': is_expired,
                'timestamp': data['timestamp']
            })
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return {
        'total_entries': len(entries),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'expired_count': expired_count,
        'entries': sorted(entries, key=lambda x: x['age_hours'], reverse=True)
    }


def clear_expired_cache(cache_dir: str = "cache", dry_run: bool = False) -> int:
    """Clear expired cache entries"""
    removed_count = 0
    
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist")
        return 0
    
    for filename in os.listdir(cache_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(cache_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = datetime.fromisoformat(data['timestamp'])
            age_hours = (datetime.now() - timestamp).total_seconds() / 3600
            
            if age_hours > 24:  # Expired
                if dry_run:
                    print(f"Would remove: {filename} (age: {age_hours:.1f}h)")
                else:
                    os.remove(filepath)
                    print(f"Removed: {filename} (age: {age_hours:.1f}h)")
                removed_count += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    return removed_count


def clear_large_cache(cache_dir: str = "cache", max_size_mb: float = 5.0, dry_run: bool = False) -> int:
    """Clear cache entries that are too large"""
    removed_count = 0
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist")
        return 0
    
    for filename in os.listdir(cache_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(cache_dir, filename)
        try:
            file_size = os.path.getsize(filepath)
            
            if file_size > max_size_bytes:
                size_mb = file_size / (1024 * 1024)
                if dry_run:
                    print(f"Would remove: {filename} (size: {size_mb:.2f}MB)")
                else:
                    os.remove(filepath)
                    print(f"Removed: {filename} (size: {size_mb:.2f}MB)")
                removed_count += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    return removed_count


def clear_all_cache(cache_dir: str = "cache", dry_run: bool = False) -> int:
    """Clear all cache entries"""
    removed_count = 0
    
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist")
        return 0
    
    for filename in os.listdir(cache_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(cache_dir, filename)
        try:
            if dry_run:
                print(f"Would remove: {filename}")
            else:
                os.remove(filepath)
                print(f"Removed: {filename}")
            removed_count += 1
                
        except Exception as e:
            print(f"Error removing {filename}: {e}")
    
    return removed_count


def main():
    parser = argparse.ArgumentParser(description="Cache management utility")
    parser.add_argument("--cache-dir", default="cache", help="Cache directory path")
    parser.add_argument("--analyze", action="store_true", help="Analyze cache entries")
    parser.add_argument("--clear-expired", action="store_true", help="Clear expired entries")
    parser.add_argument("--clear-large", action="store_true", help="Clear large entries")
    parser.add_argument("--clear-all", action="store_true", help="Clear all entries")
    parser.add_argument("--max-size-mb", type=float, default=5.0, help="Max file size in MB for --clear-large")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually doing it")
    
    args = parser.parse_args()
    
    if args.analyze:
        print("Analyzing cache entries...")
        analysis = analyze_cache_entries(args.cache_dir)
        
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        print(f"\nCache Analysis:")
        print(f"  Total entries: {analysis['total_entries']}")
        print(f"  Total size: {analysis['total_size_mb']} MB")
        print(f"  Expired entries: {analysis['expired_count']}")
        
        print(f"\nRecent entries:")
        for entry in analysis['entries'][:5]:
            print(f"  {entry['filename'][:20]}... - {entry['age_hours']}h old, {entry['size']} bytes, model: {entry['model']}")
        
        if analysis['entries']:
            print(f"  ... and {len(analysis['entries']) - 5} more")
    
    elif args.clear_expired:
        print("Clearing expired cache entries...")
        removed = clear_expired_cache(args.cache_dir, args.dry_run)
        action = "Would remove" if args.dry_run else "Removed"
        print(f"{action} {removed} expired entries")
    
    elif args.clear_large:
        print(f"Clearing cache entries larger than {args.max_size_mb}MB...")
        removed = clear_large_cache(args.cache_dir, args.max_size_mb, args.dry_run)
        action = "Would remove" if args.dry_run else "Removed"
        print(f"{action} {removed} large entries")
    
    elif args.clear_all:
        print("Clearing ALL cache entries...")
        if not args.dry_run:
            confirm = input("Are you sure? This will delete all cached responses. (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled")
                return
        
        removed = clear_all_cache(args.cache_dir, args.dry_run)
        action = "Would remove" if args.dry_run else "Removed"
        print(f"{action} {removed} entries")
    
    else:
        print("Please specify an action: --analyze, --clear-expired, --clear-large, or --clear-all")
        print("Use --help for more information")


if __name__ == "__main__":
    main()
