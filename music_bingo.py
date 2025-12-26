#!/usr/bin/env python3
"""
Music Bingo - A macOS application for running music bingo games
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import random
import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from datetime import datetime
import threading
import time
from pathlib import Path

class MusicBingoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Bingo Controller")
        self.root.geometry("900x700")
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Application state
        self.music_library = []
        self.current_game_songs = []
        self.played_songs = []
        self.current_song = None
        self.is_playing = False
        self.game_active = False
        self.library_folder = ""
        
        # Game parameters
        self.SONGS_PER_GAME = 75  
        
        # Display window reference
        self.display_window = None
        
        # Load settings
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        
        # Load music library if folder is set
        if self.library_folder:
            self.scan_music_folder()
    
    def setup_ui(self):
        """Setup the main controller interface"""
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Music Folder", command=self.select_music_folder)
        file_menu.add_command(label="Rescan Music Folder", command=self.scan_music_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Print Cards", command=self.print_cards)
        game_menu.add_command(label="Open Display Window", command=self.open_display_window)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Library info section
        info_frame = ttk.LabelFrame(main_frame, text="Library Info", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.library_label = ttk.Label(info_frame, text="No music folder selected")
        self.library_label.grid(row=0, column=0, sticky=tk.W)
        
        self.song_count_label = ttk.Label(info_frame, text="Total songs: 0")
        self.song_count_label.grid(row=1, column=0, sticky=tk.W)
        
        # Game control section
        control_frame = ttk.LabelFrame(main_frame, text="Game Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.new_game_btn = ttk.Button(control_frame, text="Start New Game", 
                                       command=self.new_game, width=20)
        self.new_game_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.play_btn = ttk.Button(control_frame, text="Play Next Song", 
                                   command=self.play_next_song, state="disabled", width=20)
        self.play_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause", 
                                    command=self.pause_song, state="disabled", width=20)
        self.pause_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", 
                                   command=self.stop_song, state="disabled", width=20)
        self.stop_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Current song display
        current_frame = ttk.LabelFrame(main_frame, text="Currently Playing", padding="10")
        current_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.current_song_label = ttk.Label(current_frame, text="No song playing", 
                                           font=('Arial', 16, 'bold'))
        self.current_song_label.grid(row=0, column=0, sticky=tk.W)
        
        self.current_artist_label = ttk.Label(current_frame, text="", font=('Arial', 12))
        self.current_artist_label.grid(row=1, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(current_frame, variable=self.progress_var, 
                                           length=400, mode='determinate')
        self.progress_bar.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Game playlist 
        playlist_frame = ttk.LabelFrame(main_frame, text=f"Game Playlist ({self.SONGS_PER_GAME} songs)", padding="10")
        playlist_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create treeview for playlist
        columns = ('Number', 'Title', 'Artist', 'Status')
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.playlist_tree.heading(col, text=col)
            if col == 'Number':
                self.playlist_tree.column(col, width=80)
            elif col == 'Status':
                self.playlist_tree.column(col, width=100)
            else:
                self.playlist_tree.column(col, width=250)
        
        # Scrollbar for playlist
        scrollbar = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=scrollbar.set)
        
        self.playlist_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        playlist_frame.columnconfigure(0, weight=1)
        playlist_frame.rowconfigure(0, weight=1)
    
    def select_music_folder(self):
        """Select the folder containing music files"""
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self.library_folder = folder
            self.save_settings()
            self.scan_music_folder()
    
    def scan_music_folder(self):
        """Scan the music folder for MP3 files"""
        if not self.library_folder:
            messagebox.showwarning("No Folder", "Please select a music folder first")
            return
        
        self.music_library = []
        self.status_bar.config(text="Scanning music folder...")
        
        # Scan in a separate thread to prevent UI freeze
        def scan():
            for root, dirs, files in os.walk(self.library_folder):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        filepath = os.path.join(root, file)
                        song_info = self.get_song_info(filepath)
                        if song_info:
                            self.music_library.append(song_info)
            
            # Update UI in main thread
            self.root.after(0, self.update_library_info)
        
        thread = threading.Thread(target=scan)
        thread.start()
    
    def get_song_info(self, filepath):
        """Extract song information from MP3 file"""
        try:
            audio = MP3(filepath)
            tags = ID3(filepath)
            
            title = str(tags.get('TIT2', os.path.basename(filepath)[:-4]))
            artist = str(tags.get('TPE1', 'Unknown Artist'))
            album = str(tags.get('TALB', 'Unknown Album'))
            
            return {
                'filepath': filepath,
                'title': title,
                'artist': artist,
                'album': album,
                'duration': audio.info.length
            }
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def update_library_info(self):
        """Update the library information display"""
        self.library_label.config(text=f"Music Folder: {self.library_folder}")
        self.song_count_label.config(text=f"Total songs: {len(self.music_library)}")
        self.status_bar.config(text=f"Loaded {len(self.music_library)} songs")
        
        if len(self.music_library) < self.SONGS_PER_GAME:
            messagebox.showwarning("Insufficient Songs", 
                                 f"Only {len(self.music_library)} songs found. Need at least {self.SONGS_PER_GAME} for a game.")
    
    def new_game(self):
        """Start a new bingo game"""
        if len(self.music_library) < self.SONGS_PER_GAME:
            messagebox.showwarning("Insufficient Songs", 
                                 f"Need at least {self.SONGS_PER_GAME} songs in library to start a game")
            return
        
        # Reset game state
        self.played_songs = []
        self.current_song = None
        self.game_active = True
        
        # Select  random songs for this game
        self.current_game_songs = random.sample(self.music_library, self.SONGS_PER_GAME)
        
        # Shuffle the order for playback
        random.shuffle(self.current_game_songs)
        
        # Update playlist display
        self.playlist_tree.delete(*self.playlist_tree.get_children())
        for i, song in enumerate(self.current_game_songs, 1):
            self.playlist_tree.insert('', 'end', values=(i, song['title'], 
                                                        song['artist'], 'Not Played'))
        
        # Enable game controls
        self.play_btn.config(state="normal")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        
        self.status_bar.config(text=f"New game started! {self.SONGS_PER_GAME} songs selected.")
        
        # Update display window if open
        if self.display_window and self.display_window.winfo_exists():
            # Simple: just pass all played songs to the display
            # The display will show the last 10
            self.display_window.update_songs(self.played_songs)
    
    def play_next_song(self):
        """Play the next song in the playlist"""
        if not self.game_active:
            messagebox.showinfo("No Active Game", "Please start a new game first")
            return
        
        # Find the next unplayed song
        unplayed = [s for s in self.current_game_songs if s not in self.played_songs]
        
        if not unplayed:
            messagebox.showinfo("Game Complete", f"All {self.SONGS_PER_GAME} songs have been played!")
            self.game_active = False
            return
        
        # Stop current song if playing
        if self.is_playing:
            pygame.mixer.music.stop()
        
        # Get next song
        self.current_song = unplayed[0]
        self.played_songs.append(self.current_song)
        
        # Load and play the song
        pygame.mixer.music.load(self.current_song['filepath'])
        pygame.mixer.music.play()
        self.is_playing = True
        
        # Update UI
        self.current_song_label.config(text=self.current_song['title'])
        self.current_artist_label.config(text=self.current_song['artist'])
        
        # Update playlist tree
        for item in self.playlist_tree.get_children():
            values = self.playlist_tree.item(item)['values']
            if values[1] == self.current_song['title'] and values[2] == self.current_song['artist']:
                self.playlist_tree.item(item, values=(values[0], values[1], values[2], 'Playing'))
            elif values[3] == 'Playing':
                self.playlist_tree.item(item, values=(values[0], values[1], values[2], 'Played'))
        
        # Update display window - show all played songs including current
        if self.display_window and self.display_window.winfo_exists():
            self.display_window.update_songs(self.played_songs)
        
        self.status_bar.config(text=f"Playing song {len(self.played_songs)} of {self.SONGS_PER_GAME}")
        
        # Start progress monitoring
        self.monitor_progress()
    
    def schedule_display_update(self):
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
        
        self.root.after(1000, check_song_finished)
    
    def monitor_progress(self):
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

    def pause_song(self):
        """Pause/resume the current song"""
        if self.is_playing:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.pause_btn.config(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.pause_btn.config(text="Pause")
    
    def stop_song(self):
        """Stop the current song"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_song_label.config(text="No song playing")
            self.current_artist_label.config(text="")
            self.progress_var.set(0)
            
            # Update playlist tree
            for item in self.playlist_tree.get_children():
                values = self.playlist_tree.item(item)['values']
                if values[3] == 'Playing':
                    self.playlist_tree.item(item, values=(values[0], values[1], values[2], 'Stopped'))
    
    def open_display_window(self):
        """Open the display window for casting"""
        if self.display_window and self.display_window.winfo_exists():
            self.display_window.lift()
        else:
            self.display_window = DisplayWindow(self)
    
    def print_cards(self):
        """Generate and print bingo cards"""
        if not self.current_game_songs:
            messagebox.showwarning("No Active Game", 
                                 "Please start a new game first to generate cards")
            return
        
        # Open card generator window
        CardGenerator(self.root, self.current_game_songs)
    
    def save_settings(self):
        """Save application settings"""
        settings = {
            'library_folder': self.library_folder,
            'songs_per_game': self.SONGS_PER_GAME
        }
        settings_file = Path.home() / '.music_bingo_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
    
    def load_settings(self):
        """Load application settings"""
        settings_file = Path.home() / '.music_bingo_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.library_folder = settings.get('library_folder', '')
                    self.SONGS_PER_GAME = settings.get('songs_per_game', 50)
            except:
                pass


class DisplayWindow:
    """Secondary window for displaying played songs"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Music Bingo Display")
        self.window.geometry("800x600")
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        print("✓ DisplayWindow initialized")
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the display interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="MUSIC BINGO", 
                               font=('Arial', 48, 'bold'))
        title_label.grid(row=0, column=0, pady=20)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Last 10 Songs Played", 
                                font=('Arial', 36))
        instructions.grid(row=1, column=0, pady=10)
        
        # Songs list frame
        self.songs_frame = ttk.Frame(main_frame)
        self.songs_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Initialize empty display - 10 labels
        self.song_labels = []
        for i in range(10):
            label = ttk.Label(self.songs_frame, text="", 
                            font=('Arial', 36), foreground='gray')
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            self.song_labels.append(label)
        
        print(f"✓ Created {len(self.song_labels)} song labels")
    
    def update_songs(self, songs):
        """Update the displayed songs list - show last 10 with red, white, blue colors"""
        print(f"\n>>> update_songs() called with {len(songs)} songs")
        
        # Define colors for cycling
        colors = ['red', 'white', 'blue']
        
        # Clear all labels first
        for label in self.song_labels:
            label.config(text="")
        
        # If no songs yet, nothing to display
        if not songs:
            print(">>> No songs to display yet")
            return
        
        # Get the last 10 songs (or fewer if less than 10 played)
        last_10 = songs[-10:] if len(songs) > 10 else songs
        print(f">>> Displaying last {len(last_10)} songs")
        
        # Display them in reverse order (most recent first)
        for i, song in enumerate(reversed(last_10)):
            # Calculate the actual song number from the game
            song_number = len(songs) - i
            
            # Build display text
            text = f"{song_number}. {song['title']} - {song['artist']}"
            
            # Get color for this row (cycles through red, white, blue)
            color = colors[i % 3]
            
            print(f">>>   {text} [{color}]")
            
            # Update the label with the color
            # Note: white text needs black background or dark foreground for visibility
            if color == 'white':
                # White background with black text
                self.song_labels[i].config(text=text, foreground='white')
            else:
                # Red or blue text on default background
                self.song_labels[i].config(text=text, foreground=color, background='')
        
        print(">>> Display updated!\n")
    
    def clear_display(self):
        """Clear the display for a new game"""
        print(">>> Clearing display for new game")
        for label in self.song_labels:
            label.config(text="", foreground='gray')
    
    def winfo_exists(self):
        """Check if the window still exists"""
        try:
            return self.window.winfo_exists()
        except:
            return False
class CardGenerator:
    """Window for generating and printing bingo cards"""
    
    def __init__(self, parent, songs):
        self.parent = parent
        self.songs = songs
        self.window = tk.Toplevel(parent)
        self.window.title("Bingo Card Generator")
        self.window.geometry("600x400")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the card generator interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instructions
        ttk.Label(main_frame, text="Generate Bingo Cards", 
                 font=('Arial', 18, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(main_frame, text="Number of cards to generate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.num_cards = tk.IntVar(value=10)
        ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.num_cards, 
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Card style options
        ttk.Label(main_frame, text="Card Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.card_size = tk.StringVar(value="5x5")
        ttk.Combobox(main_frame, textvariable=self.card_size, 
                    values=["5x5"], state="readonly", 
                    width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Free space option
        self.free_space = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Include FREE space in center", 
                       variable=self.free_space).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Generate HTML", 
                  command=self.generate_html).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).grid(row=0, column=1, padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Note about 50 songs
        note_label = ttk.Label(main_frame, 
                              text=f"Note: Cards will use songs from the current {len(self.songs)}-song game pool",
                              foreground='blue')
        note_label.grid(row=6, column=0, columnspan=2, pady=5)
    
    def generate_cards(self, num_cards):
        """Generate the specified number of bingo cards"""
        cards = []
        for i in range(num_cards):
            card = self.create_single_card()
            cards.append(card)
        return cards
    
    def create_single_card(self):
        """Create a single bingo card"""
        # For 50-song games, we still create 5x5 cards
        # but pull from the 50-song pool
        num_songs = 24 if self.free_space.get() else 25
        
        # Make sure we have enough songs
        if len(self.songs) < num_songs:
            messagebox.showwarning("Not Enough Songs", 
                                 f"Need at least {num_songs} songs to create cards")
            return None
        
        selected_songs = random.sample(self.songs, num_songs)
        
        # Create 5x5 grid
        card = []
        song_index = 0
        
        for row in range(5):
            card_row = []
            for col in range(5):
                if self.free_space.get() and row == 2 and col == 2:
                    # Center free space
                    card_row.append("FREE")
                else:
                    song = selected_songs[song_index]
                    # Include song number for reference (1-50 instead of 1-75)
                    card_row.append({
                        'title': song['title'],
                        'artist': song['artist']
                    })
                    song_index += 1
            card.append(card_row)
        
        return card
    
    def generate_html(self):
        """Generate HTML file with bingo cards"""
        num = self.num_cards.get()
        cards = self.generate_cards(num)
        
        if not cards or None in cards:
            return
        
        # Create HTML with updated styling for 50-song games
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Music Bingo Cards - 50 Song Game</title>
            <style>
                @media print {{
                    .page-break {{ page-break-after: always; }}
                    .no-print {{ display: none; }}
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                }}
                .game-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    color: #666;
                    font-size: 12px;
                }}
                .card {{
                    width: 7.5in;
                    margin: 0 auto 30px auto;
                    border: 3px solid black;
                    padding: 20px;
                    background: white;
                }}
                .card-title {{
                    text-align: center;
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    letter-spacing: 2px;
                }}
                .card-number {{
                    text-align: center;
                    font-size: 14px;
                    margin-bottom: 20px;
                    color: #666;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                td {{
                    border: 2px solid black;
                    padding: 8px;
                    text-align: center;
                    height: 110px;
                    width: 20%;
                    vertical-align: middle;
                    position: relative;
                }}
                .song-title {{
                    font-weight: bold;
                    font-size: 12px;
                    margin-bottom: 4px;
                }}
                .song-artist {{
                    font-size: 10px;
                    color: #333;
                }}
                .free-space {{
                    font-weight: bold;
                    font-size: 24px;
                    background: #f0f0f0;
                }}
                .header-row {{
                    background: #333;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .header-row td {{
                    height: 40px;
                    border: 2px solid #333;
                }}
                .song-list {{
                    columns: 2;
                    font-size: 11px;
                    line-height: 1.6;
                }}
                .song-list li {{
                    break-inside: avoid;
                }}
            </style>
        </head>
        <body>
        """
        
        for i, card in enumerate(cards, 1):
            if i > 1:
                html += '<div class="page-break"></div>'
            
            html += f"""
            <div class="card">
                <div class="card-title">♫ MUSIC BINGO ♫</div>
                <div class="card-number">Card #{i} • 50-Song Game</div>
                <table>
                    <tr class="header-row">
                        <td>M</td>
                        <td>U</td>
                        <td>S</td>
                        <td>I</td>
                        <td>C</td>
                    </tr>
            """
            
            for row in card:
                html += "<tr>"
                for cell in row:
                    if cell == "FREE":
                        html += '<td class="free-space">FREE<br>SPACE</td>'
                    else:
                        # Truncate long titles/artists for better fit
                        title = cell['title'][:30] + '...' if len(cell['title']) > 30 else cell['title']
                        artist = cell['artist'][:25] + '...' if len(cell['artist']) > 25 else cell['artist']
                        html += f'''<td>
                            <span class="song-number">#{cell['number']}</span>
                            <div class="song-title">{title}</div>
                            <div class="song-artist">{artist}</div>
                        </td>'''
                html += "</tr>"
            
            html += """
                </table>
            </div>
            """
        
        # Add master list at the end (50 songs)
        html += '''
        <div class="page-break"></div>
        <div class="card">
            <div class="card-title">Master Song List</div>
            <div class="game-info">50-Song Game Pool</div>
            <ol class="song-list">
        '''
        
        for i, song in enumerate(self.songs, 1):
            html += f"<li><strong>#{i}:</strong> {song['title']} - {song['artist']}</li>"
        
        html += """
            </ol>
        </div>
        </body>
        </html>
        """
        
        # Save HTML file
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile=f"music_bingo_cards_50_songs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            self.status_label.config(text=f"Generated {num} cards")
            
            # Offer to open the file
            if messagebox.askyesno("Open File", "Would you like to open the generated file?"):
                os.system(f"open '{filename}'")


def main():
    root = tk.Tk()
    app = MusicBingoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()