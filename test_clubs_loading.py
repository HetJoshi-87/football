#!/usr/bin/env python3
"""Test script to see what clubs will be loaded from step5(3-6).txt"""

def load_clubs_test():
    """Test the club loading logic"""
    CLUBS_FILE = "step5(3-6).txt"
    
    if not os.path.exists(CLUBS_FILE):
        print(f"❌ {CLUBS_FILE} not found")
        return []
    
    with open(CLUBS_FILE, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]
    
    # Find the starting point (Rossington Main)
    start_index = -1
    for i, line in enumerate(all_lines):
        if line == "Rossington Main":
            start_index = i
            break
    
    if start_index == -1:
        print("⚠️  Rossington Main not found, starting from beginning of file")
        start_index = 0
    
    # Get remaining clubs (skip comment lines starting with #)
    remaining_clubs = []
    original_names = []
    for line in all_lines[start_index:]:
        if not line.startswith('#') and line.strip():
            original_names.append(line)
            # Convert team name to URL format
            club_url = line.lower().replace(' ', '-').replace('_', '-')
            # Handle special cases
            club_url = club_url.replace('afc', 'afc').replace('fc-', 'fc-')
            remaining_clubs.append(club_url)
    
    print(f"📋 Found {len(remaining_clubs)} remaining clubs")
    print(f"🎯 Starting from: {all_lines[start_index] if start_index < len(all_lines) else 'Unknown'}")
    print("\nClubs to be processed:")
    for i, (original, url) in enumerate(zip(original_names, remaining_clubs)):
        print(f"{i+1:2d}. {original} -> {url}")
    
    return remaining_clubs

if __name__ == "__main__":
    import os
    load_clubs_test()
