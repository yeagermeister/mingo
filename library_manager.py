#!/usr/bin/env python3
"""
Utility to manage and verify your music library for Music Bingo
Updated for 50-song games
"""

import os
import sys
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB
import argparse

SONGS_PER_GAME = 50  # Changed from 75 to 50

def scan_library(folder_path):
    """Scan and report on music library"""
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    mp3_files = []
    files_with_tags = []
    files_without_tags = []
    
    print(f"Scanning {folder_path}...")
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                filepath = os.path.join(root, file)
                mp3_files.append(filepath)
                
                try:
                    tags = ID3(filepath)
                    title = tags.get('TIT2')
                    artist = tags.get('TPE1')
                    
                    if title and artist:
                        files_with_tags.append({
                            'path': filepath,
                            'title': str(title),
                            'artist': str(artist)
                        })
                    else:
                        files_without_tags.append(filepath)
                except:
                    files_without_tags.append(filepath)
    
    print(f"\n=== Library Report (50-Song Game Mode) ===")
    print(f"Total MP3 files found: {len(mp3_files)}")
    print(f"Files with proper tags: {len(files_with_tags)}")
    print(f"Files without proper tags: {len(files_without_tags)}")
    
    if len(mp3_files) < SONGS_PER_GAME:
        print(f"\n⚠️  Warning: You need at least {SONGS_PER_GAME} songs for a game.")
        print(f"   Currently you have {len(mp3_files)} songs.")
        print(f"   Please add {SONGS_PER_GAME - len(mp3_files)} more songs.")
    else:
        print(f"\n✓ You have enough songs for {len(mp3_files) // SONGS_PER_GAME} complete games!")
        print(f"  (Each game uses {SONGS_PER_GAME} songs)")
    
    if files_without_tags:
        print(f"\n=== Files Missing Tags ===")
        for f in files_without_tags[:10]:  # Show first 10
            print(f"  - {os.path.basename(f)}")
        if len(files_without_tags) > 10:
            print(f"  ... and {len(files_without_tags) - 10} more")
    
    return files_with_tags

def fix_tags(filepath, title=None, artist=None, album=None):
    """Add or update ID3 tags for an MP3 file"""
    try:
        try:
            tags = ID3(filepath)
        except:
            # No tags exist, create them
            tags = ID3()
        
        if title:
            tags["TIT2"] = TIT2(encoding=3, text=title)
        if artist:
            tags["TPE1"] = TPE1(encoding=3, text=artist)
        if album:
            tags["TALB"] = TALB(encoding=3, text=album)
        
        tags.save(filepath)
        print(f"✓ Updated tags for {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"✗ Failed to update {os.path.basename(filepath)}: {e}")
        return False

def auto_fix_tags(folder_path):
    """Attempt to auto-fix missing tags based on filename"""
    print("Attempting to auto-fix missing tags...")
    
    fixed_count = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                filepath = os.path.join(root, file)
                
                try:
                    tags = ID3(filepath)
                    if tags.get('TIT2') and tags.get('TPE1'):
                        continue  # Already has tags
                except:
                    pass
                
                # Try to parse filename
                filename = os.path.splitext(file)[0]
                
                # Common patterns: "Artist - Title" or "Title - Artist"
                if ' - ' in filename:
                    parts = filename.split(' - ', 1)
                    # Assume "Artist - Title" format
                    if fix_tags(filepath, title=parts[1], artist=parts[0]):
                        fixed_count += 1
                else:
                    # Use filename as title
                    if fix_tags(filepath, title=filename, artist="Unknown Artist"):
                        fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

def recommend_songs(current_count):
    """Recommend how many more songs to add for optimal gameplay"""
    print("\n=== Song Recommendations ===")
    print(f"Current library size: {current_count} songs")
    print(f"Songs per game: {SONGS_PER_GAME}")
    
    if current_count < SONGS_PER_GAME:
        print(f"❌ Need {SONGS_PER_GAME - current_count} more songs to play one game")
    else:
        complete_games = current_count // SONGS_PER_GAME
        remaining = current_count % SONGS_PER_GAME
        print(f"✓ Can play {complete_games} complete game(s)")
        
        if remaining > 0:
            print(f"  Plus {remaining} extra songs")
            print(f"  Add {SONGS_PER_GAME - remaining} more songs for another complete game")
        
        # Recommend optimal library sizes
        print("\nOptimal library sizes for 50-song games:")
        print("  • 50 songs  = 1 game  (minimum)")
        print("  • 100 songs = 2 different games")
        print("  • 150 songs = 3 different games") 
        print("  • 200+ songs = 4+ games with good variety")

def main():
    parser = argparse.ArgumentParser(description='Music Bingo Library Manager (50-song games)')
    parser.add_argument('folder', help='Path to music folder')
    parser.add_argument('--fix', action='store_true', 
                       help='Attempt to auto-fix missing tags')
    parser.add_argument('--list', action='store_true',
                       help='List all songs with tags')
    
    args = parser.parse_args()
    
    songs = scan_library(args.folder)
    
    if args.fix:
        auto_fix_tags(args.folder)
        print("\nRescanning after fixes...")
        songs = scan_library(args.folder)
    
    if songs:
        recommend_songs(len(songs))
    
    if args.list and songs:
        print(f"\n=== Songs with Proper Tags ({len(songs)} total) ===")
        for i, song in enumerate(songs, 1):
            marker = "✓" if i <= SONGS_PER_GAME else "+"
            print(f"{marker} {i:3d}. {song['title'][:40]:40} | {song['artist'][:30]}")
        
        if len(songs) > SONGS_PER_GAME:
            print(f"\n✓ = In first game pool (1-{SONGS_PER_GAME})")
            print(f"+ = Additional songs for variety")

if __name__ == "__main__":
    main()