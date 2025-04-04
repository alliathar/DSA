import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from pygame import mixer, USEREVENT
from collections import deque

# Node class for doubly linked list
class SongNode:
    def __init__(self, title, artist, path):
        self.title = title
        self.artist = artist
        self.path = path
        self.play_count = 0
        self.prev = None
        self.next = None

# Doubly linked list implementation
class Playlist:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def add_song(self, title, artist, path):
        new_node = SongNode(title, artist, path)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def to_list(self):
        songs = []
        current = self.head
        while current:
            songs.append(current)
            current = current.next
        return songs

    def from_list(self, songs):
        self.head = None
        self.tail = None
        self.size = 0
        for song in songs:
            self.add_song(song.title, song.artist, song.path)

    def shuffle(self):
        songs = self.to_list()
        random.shuffle(songs)
        self.from_list(songs)

    def sort_by(self, key):
        songs = self.to_list()
        songs.sort(key=lambda x: getattr(x, key))
        self.from_list(songs)

# Music Player Application
class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Music Player")
        self.playlist = Playlist()
        self.paused = False

        # Initialize Pygame mixer
        mixer.init()

        # Set up custom event for song end
        self.SONG_END_EVENT = USEREVENT + 1
        mixer.music.set_endevent(self.SONG_END_EVENT)

        # Create GUI elements
        self.create_menu()
        self.create_playlist_box()
        self.create_buttons()
        self.create_volume_control()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add Songs", command=self.add_songs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def create_playlist_box(self):
        self.playlist_box = tk.Listbox(self.root, bg="black", fg="white", width=50, height=15)
        self.playlist_box.pack(pady=10)
        self.playlist_box.bind('<<ListboxSelect>>', self.on_song_select)

    def create_buttons(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        prev_btn = tk.Button(control_frame, text="<<", command=self.prev_song)
        play_btn = tk.Button(control_frame, text="Play", command=self.play_song)
        pause_btn = tk.Button(control_frame, text="Pause", command=self.toggle_pause)
        next_btn = tk.Button(control_frame, text=">>", command=self.next_song)
        shuffle_btn = tk.Button(control_frame, text="Shuffle", command=self.shuffle_playlist)
        sort_btn = tk.Button(control_frame, text="Sort", command=self.sort_menu)

        prev_btn.grid(row=0, column=0, padx=10)
        play_btn.grid(row=0, column=1, padx=10)
        pause_btn.grid(row=0, column=2, padx=10)
        next_btn.grid(row=0, column=3, padx=10)
        shuffle_btn.grid(row=0, column=4, padx=10)
        sort_btn.grid(row=0, column=5, padx=10)

    def create_volume_control(self):
        volume_frame = tk.Frame(self.root)
        volume_frame.pack(pady=5)
        tk.Label(volume_frame, text="Volume").grid(row=0, column=0)
        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=0, column=1)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def add_songs(self):
        directory = filedialog.askdirectory()
        if not directory:
            return

        valid_extensions = ['.mp3', '.wav', '.ogg']
        for root_dir, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in valid_extensions):
                    path = os.path.join(root_dir, file)
                    title = os.path.splitext(file)[0]
                    artist = "Unknown"  # Implement proper metadata reading if needed
                    self.playlist.add_song(title, artist, path)
                    self.playlist_box.insert(tk.END, title)

    def play_song(self, index=None):
        if not self.playlist.size:
            return

        if index is not None:
            # Find the node corresponding to the selected index
            current = self.playlist.head
            for _ in range(index):
                current = current.next
            self.playlist.current = current
        elif not self.playlist.current:
            self.playlist.current = self.playlist.head

        mixer.music.load(self.playlist.current.path)
        mixer.music.play()
        self.playlist.current.play_count += 1
        self.status_var.set(f"Now Playing: {self.playlist.current.title}")
        self.paused = False

    def toggle_pause(self):
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.status_var.set("Resumed")
        else:
            mixer.music.pause()
            self.paused = True
            self.status_var.set("Paused")

    def next_song(self):
        if self.playlist.current and self.playlist.current.next:
            self.playlist.current = self.playlist.current.next
            self.play_song()
            self.update_playlist_selection()

    def prev_song(self):
        if self.playlist.current and self.playlist.current.prev:
            self.playlist.current = self.playlist.current.prev
            self.play_song()
            self.update_playlist_selection()

    def shuffle_playlist(self):
        self.playlist.shuffle()
        self.update_playlist_display()

    def sort_menu(self):
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Sort Options")

        options = ["Title", "Artist", "Play Count"]
        var = tk.StringVar(value=options[0])

        tk.Label(sort_window, text="Sort by:").pack()
        for option in options:
            tk.Radiobutton(sort_window, text=option, variable=var, value=option).pack()

        confirm_btn = tk.Button(sort_window, text="Sort", command=lambda: self.sort_playlist(var.get(), sort_window))
        confirm_btn.pack()

    def sort_playlist(self, key, window):
        key_map = {
            "Title": "title",
            "Artist": "artist",
            "Play Count": "play_count"
        }
        self.playlist.sort_by(key_map[key])
        self.update_playlist_display()
        window.destroy()

    def update_playlist_display(self):
        self.playlist_box.delete(0, tk.END)
        current = self.playlist.head
        while current:
            self.playlist_box.insert(tk.END, current.title)
            current = current.next

    def update_playlist_selection(self):
        self.playlist_box.selection_clear(0, tk.END)
        current_node = self.playlist.current
        index = 0
        node = self.playlist.head
        while node != current_node:
            node = node.next
            index += 1
        self.playlist_box.selection_set(index)
        self.playlist_box.see(index)

    def on_song_select(self, event):
        if self.playlist.size == 0:
            return
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            self.play_song(index)

    def set_volume(self, volume):
        mixer.music.set_volume(int(volume)/100)

    def check_music_end(self):
        for event in mixer.event.get():
            if event.type == self.SONG_END_EVENT:
                self.next_song()
        self.root.after(100, self.check_music_end)

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.after(100, player.check_music_end)
    root.mainloop()