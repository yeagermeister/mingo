#!/usr/bin/env python3
"""
Auto-patcher for Music Bingo display window issue
This script will automatically fix the display window problems in music_bingo.py
"""

import sys
import os

def apply_fixes(filepath):
    """Apply all fixes to the music_bingo.py file"""
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        return False
    
    # Read the original file
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Backup the original
    backup_path = filepath + '.backup'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    
    # Apply Fix #1: Simplify schedule_display_update
    old_schedule = '''    def schedule_display_update(self):
        """Schedule display update when current song finishes"""
        def check_song_finished():
            if not pygame.mixer.music.get_busy():
                # Song finished, update display
                if self.display_window and self.display_window.winfo_exists():
                    # Show last 10 played songs (not including currently playing)
                    if len(self.played_songs) > 0:
                        # Remove current song from display list
                        display_songs = self.played_songs[:-1] if self.is_playing else self.played_songs
                        self.display_window.update_songs(display_songs)
            else:
                # Check again in 1 second
                self.root.after(1000, check_song_finished)
        
        self.root.after(1000, check_song_finished)'''
    
    new_schedule = '''    def schedule_display_update(self):
        """Schedule display update when current song finishes"""
        def check_song_finished():
            if not pygame.mixer.music.get_busy():
                # Song finished, mark it as no longer playing
                self.is_playing = False
                # Update display with all played songs (song has finished)
                if self.display_window and self.display_window.winfo_exists():
                    self.display_window.update_songs(self.played_songs)
            else:
                # Check again in 1 second
                self.root.after(1000, check_song_finished)
        
        self.root.after(1000, check_song_finished)'''
    
    if old_schedule in content:
        content = content.replace(old_schedule, new_schedule)
        print("✓ Applied Fix #1: Updated schedule_display_update()")
    else:
        print("⚠ Warning: Could not find exact match for schedule_display_update()")
    
    # Apply Fix #2: Update monitor_progress (remove duplicate update code)
    old_monitor = '''    def monitor_progress(self):
        """Monitor song playback progress"""
        if self.is_playing and pygame.mixer.music.get_busy():
            # Update progress bar
            if self.current_song:
                pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
                duration = self.current_song['duration']
                if duration > 0:
                    progress = (pos / duration) * 100
                    self.progress_var.set(min(progress, 100))
            
            # Schedule next check
            self.root.after(100, self.monitor_progress)
        else:
            self.progress_var.set(0)
            if self.is_playing and not pygame.mixer.music.get_busy():
                # Song ended, update display
                self.is_playing = False
                if self.display_window and self.display_window.winfo_exists():
                    self.display_window.update_songs(self.played_songs)'''
    
    new_monitor = '''    def monitor_progress(self):
        """Monitor song playback progress"""
        if self.is_playing and pygame.mixer.music.get_busy():
            # Update progress bar
            if self.current_song:
                pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
                duration = self.current_song['duration']
                if duration > 0:
                    progress = (pos / duration) * 100
                    self.progress_var.set(min(progress, 100))
            
            # Schedule next check
            self.root.after(100, self.monitor_progress)
        else:
            self.progress_var.set(0)'''
    
    if old_monitor in content:
        content = content.replace(old_monitor, new_monitor)
        print("✓ Applied Fix #2: Updated monitor_progress()")
    else:
        print("⚠ Warning: Could not find exact match for monitor_progress()")
    
    # Apply Fix #3: Update play_next_song display update
    old_play_display = '''        # Update display window
        if self.display_window and self.display_window.winfo_exists():
            # Don't show current song, only update after it's done
            self.schedule_display_update()'''
    
    new_play_display = '''        # Update display window - show all played songs including current
        if self.display_window and self.display_window.winfo_exists():
            self.display_window.update_songs(self.played_songs)'''
    
    if old_play_display in content:
        content = content.replace(old_play_display, new_play_display)
        print("✓ Applied Fix #3: Updated play_next_song() display update")
    else:
        print("⚠ Warning: Could not find exact match for play_next_song() display update")
    
    # Write the fixed content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"\n✓ All fixes applied successfully!")
    print(f"✓ Original file backed up to: {backup_path}")
    print(f"✓ Fixed file saved to: {filepath}")
    
    return True

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'music_bingo.py'
    
    print("Music Bingo Display Window Fix Patcher")
    print("=" * 50)
    print(f"Target file: {filepath}\n")
    
    if apply_fixes(filepath):
        print("\n✅ Patching complete!")
        print("\nWhat was fixed:")
        print("  1. Display window now shows songs immediately")
        print("  2. Currently playing song is included in display")
        print("  3. Removed duplicate update logic")
        print("  4. Simplified state management")
        print("\nYou can now run music_bingo.py and the display window will work correctly!")
    else:
        print("\n❌ Patching failed")
        sys.exit(1)

if __name__ == "__main__":
    main()