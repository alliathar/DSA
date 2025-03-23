import tkinter as tk
from tkinter import ttk, filedialog
import random
import time
from PIL import Image, ImageTk  # You would need to install Pillow: pip install Pillow
import io
import threading

class Song:
    def __init__(self, title, artist, duration, playcount=0):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.playcount = playcount
    
    def __str__(self):
        return f"{self.title} by {self.artist} ({self.duration})"


class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None


class Playlist:
    def __init__(self, name):
        self.name = name
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0
        self.is_playing = False
    
    def store(self, song):
        """Add a song to the end of the playlist"""
        new_node = Node(song)
        
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
        return True
    
    def display(self):
        """Return a list of songs in the playlist"""
        songs = []
        current = self.head
        
        while current:
            songs.append(current.song)
            current = current.next
        
        return songs
    
    def play(self):
        """Start or resume playing current song"""
        if self.current is None:
            return False
        
        self.is_playing = True
        self.current.song.playcount += 1
        return True
    
    def pause(self):
        """Pause the current song"""
        if not self.is_playing:
            return False
        
        self.is_playing = False
        return True
    
    def next(self):
        """Move to the next song in playlist"""
        if self.current is None:
            return False
        
        if self.current.next:
            self.current = self.current.next
            return True
        else:
            return False
    
    def previous(self):
        """Move to the previous song in playlist"""
        if self.current is None:
            return False
        
        if self.current.prev:
            self.current = self.current.prev
            return True
        else:
            return False
    
    def get_current_song(self):
        """Get the current song"""
        if self.current:
            return self.current.song
        return None
    
    def shuffle(self):
        """Randomly reorder songs in the playlist"""
        if self.size <= 1:
            return False
        
        # Convert linked list to array for shuffling
        songs = []
        current = self.head
        while current:
            songs.append(current.song)
            current = current.next
            
        # Remember current song
        current_song = self.current.song if self.current else None
        
        # Shuffle the array
        random.shuffle(songs)
        
        # Rebuild the linked list
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0
        
        # Re-add all songs
        for song in songs:
            self.store(song)
            # If this was the current song, update current pointer
            if song == current_song:
                self.current = self.tail
        
        return True
    
    def sort(self, key="title"):
        """Sort the playlist by a given attribute of Song"""
        if self.size <= 1:
            return False
        
        # Convert to list
        songs = []
        current = self.head
        while current:
            songs.append(current.song)
            current = current.next
        
        # Remember current song
        current_song = self.current.song if self.current else None
        
        # Sort the list
        if key == "title":
            songs.sort(key=lambda song: song.title)
        elif key == "artist":
            songs.sort(key=lambda song: song.artist)
        elif key == "duration":
            songs.sort(key=lambda song: song.duration)
        elif key == "playcount":
            songs.sort(key=lambda song: song.playcount, reverse=True)
        
        # Rebuild linked list
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0
        
        # Re-add all songs
        for song in songs:
            self.store(song)
            # If this was the current song, update current pointer
            if song == current_song:
                self.current = self.tail
        
        return True
    
    def remove_song(self, index):
        """Remove a song at the specified index"""
        if index < 0 or index >= self.size:
            return False
        
        current = self.head
        for i in range(index):
            current = current.next
        
        # If it's the current song, move current to next or prev
        if current == self.current:
            if self.current.next:
                self.current = self.current.next
            elif self.current.prev:
                self.current = self.current.prev
            else:
                self.current = None
        
        # Update links
        if current.prev:
            current.prev.next = current.next
        else:
            self.head = current.next
            
        if current.next:
            current.next.prev = current.prev
        else:
            self.tail = current.prev
        
        self.size -= 1
        return True

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Create playlist
        self.playlist = Playlist("My Playlist")
        
        # Add some demo songs
        self.playlist.store(Song("Blinding Lights", "The Weeknd", "3:20", 0))
        self.playlist.store(Song("Dance Monkey", "Tones and I", "3:29", 0))
        self.playlist.store(Song("Watermelon Sugar", "Harry Styles", "2:54", 0))
        self.playlist.store(Song("Don't Start Now", "Dua Lipa", "3:03", 0))
        
        # Set up the main frames
        self.setup_ui()
        
        # Progress bar simulation variables
        self.duration_sec = 0
        self.current_sec = 0
        self.progress_running = False
        
        # Update display
        self.update_song_list()
        self.update_current_song_display()

    def setup_ui(self):
        # Create main frames
        self.top_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        self.top_frame.pack(fill=tk.X)
        
        self.middle_frame = tk.Frame(self.root, bg="#34495e")
        self.middle_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        self.bottom_frame.pack(fill=tk.X)
        
        # Set up top frame (current song info)
        self.now_playing_label = tk.Label(self.top_frame, text="Now Playing", 
                                         font=("Arial", 12), bg="#2c3e50", fg="white")
        self.now_playing_label.pack(pady=(10, 0))
        
        self.song_title_label = tk.Label(self.top_frame, text="", 
                                        font=("Arial", 14, "bold"), bg="#2c3e50", fg="white")
        self.song_title_label.pack()
        
        self.song_artist_label = tk.Label(self.top_frame, text="", 
                                         font=("Arial", 12), bg="#2c3e50", fg="white")
        self.song_artist_label.pack()
        
        # Set up middle frame (song list)
        self.song_listbox_frame = tk.Frame(self.middle_frame, bg="#34495e")
        self.song_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.song_listbox = tk.Listbox(self.song_listbox_frame, bg="#2c3e50", fg="white",
                                      font=("Arial", 12), selectbackground="#3498db",
                                      selectforeground="white", activestyle="none")
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.song_listbox_frame, orient=tk.VERTICAL, 
                                      command=self.song_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.song_listbox.config(yscrollcommand=self.scrollbar.set)
        
        # Button frame for playlist operations
        self.playlist_button_frame = tk.Frame(self.middle_frame, bg="#34495e")
        self.playlist_button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.add_song_button = tk.Button(self.playlist_button_frame, text="Add Song", 
                                        command=self.add_song, bg="#3498db", fg="white")
        self.add_song_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_song_button = tk.Button(self.playlist_button_frame, text="Remove Song", 
                                          command=self.remove_song, bg="#e74c3c", fg="white")
        self.remove_song_button.pack(side=tk.LEFT, padx=5)
        
        self.shuffle_button = tk.Button(self.playlist_button_frame, text="Shuffle", 
                                       command=self.shuffle_playlist, bg="#9b59b6", fg="white")
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
        self.sort_button = tk.Button(self.playlist_button_frame, text="Sort", 
                                    command=self.sort_menu, bg="#2ecc71", fg="white")
        self.sort_button.pack(side=tk.LEFT, padx=5)
        
        # Set up bottom frame (playback controls)
        self.progress_frame = tk.Frame(self.bottom_frame, bg="#2c3e50")
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.current_time_label = tk.Label(self.progress_frame, text="0:00", 
                                         bg="#2c3e50", fg="white")
        self.current_time_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, 
                                          length=450, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.total_time_label = tk.Label(self.progress_frame, text="0:00", 
                                       bg="#2c3e50", fg="white")
        self.total_time_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.control_frame = tk.Frame(self.bottom_frame, bg="#2c3e50")
        self.control_frame.pack(pady=10)
        
        self.prev_button = tk.Button(self.control_frame, text="⏮", command=self.play_previous, 
                                   font=("Arial", 16), bg="#2c3e50", fg="white", bd=0)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.play_button = tk.Button(self.control_frame, text="▶", command=self.toggle_play, 
                                    font=("Arial", 16), bg="#2c3e50", fg="white", bd=0)
        self.play_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(self.control_frame, text="⏭", command=self.play_next, 
                                   font=("Arial", 16), bg="#2c3e50", fg="white", bd=0)
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        # Double-click on song to play
        self.song_listbox.bind("<Double-1>", self.play_selected_song)

    def update_song_list(self):
        """Update the listbox with current playlist"""
        self.song_listbox.delete(0, tk.END)
        
        songs = self.playlist.display()
        for song in songs:
            self.song_listbox.insert(tk.END, f"{song.title} - {song.artist}")
        
        # Highlight current song
        if self.playlist.current:
            current_index = 0
            current = self.playlist.head
            while current:
                if current == self.playlist.current:
                    self.song_listbox.itemconfig(current_index, bg="#3498db")
                    break
                current_index += 1
                current = current.next

    def update_current_song_display(self):
        """Update the top frame with current song info"""
        current_song = self.playlist.get_current_song()
        
        if current_song:
            self.song_title_label.config(text=current_song.title)
            self.song_artist_label.config(text=current_song.artist)
            
            # Get duration in seconds for progress bar
            min_sec = current_song.duration.split(":")
            self.duration_sec = int(min_sec[0]) * 60 + int(min_sec[1])
            self.total_time_label.config(text=current_song.duration)
            
            # Reset progress bar
            self.current_sec = 0
            self.progress_bar["maximum"] = self.duration_sec
            self.progress_bar["value"] = 0
            self.current_time_label.config(text="0:00")
        else:
            self.song_title_label.config(text="No song selected")
            self.song_artist_label.config(text="")
            self.total_time_label.config(text="0:00")
            self.current_time_label.config(text="0:00")
            self.progress_bar["value"] = 0

    def toggle_play(self):
        """Play or pause the current song"""
        if not self.playlist.current:
            return
            
        if self.playlist.is_playing:
            self.playlist.pause()
            self.play_button.config(text="▶")
            self.stop_progress()
        else:
            self.playlist.play()
            self.play_button.config(text="⏸")
            self.start_progress()
            
        self.update_song_list()

    def play_next(self):
        """Play the next song"""
        if self.playlist.next():
            self.update_current_song_display()