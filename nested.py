import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pygame import mixer, USEREVENT

# Song Node
class SongNode:
    def __init__(self, title, artist, path):
        self.title = title
        self.artist = artist
        self.path = path
        self.play_count = 0
        self.prev = None
        self.next = None

# Playlist Node
class PlaylistNode:
    def __init__(self, name):
        self.name = name
        self.songs = Playlist()
        self.prev = None
        self.next = None

# Doubly linked list for playlists
class PlaylistManager:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current_playlist = None
        self.size = 0

    def add_playlist(self, name):
        new_playlist = PlaylistNode(name)
        if not self.head:
            self.head = self.tail = new_playlist
        else:
            new_playlist.prev = self.tail
            self.tail.next = new_playlist
            self.tail = new_playlist
        self.size += 1
        return new_playlist

    def get_all_songs(self):
        all_songs = []
        current = self.head
        while current:
            song_node = current.songs.head
            while song_node:
                all_songs.append(song_node)
                song_node = song_node.next
            current = current.next
        return all_songs

    def shuffle_playlists(self):
        playlists = []
        current = self.head
        while current:
            playlists.append(current)
            current = current.next
        random.shuffle(playlists)
        self._rebuild_playlists(playlists)

    def sort_playlists_by(self, key):
        playlists = []
        current = self.head
        while current:
            playlists.append(current)
            current = current.next
        playlists.sort(key=lambda x: getattr(x, key))
        self._rebuild_playlists(playlists)

    def _rebuild_playlists(self, playlists):
        self.head = None
        self.tail = None
        for pl in playlists:
            if not self.head:
                self.head = pl
            else:
                pl.prev = self.tail
                self.tail.next = pl
            self.tail = pl

# Doubly linked list for songs
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
        self.root.title("Advanced Music Player")
        self.playlists = PlaylistManager()
        self.current_playlist = None
        self.paused = False

        mixer.init()
        self.SONG_END_EVENT = USEREVENT + 1
        mixer.music.set_endevent(self.SONG_END_EVENT)

        self.create_menu()
        self.create_playlist_box()
        self.create_song_box()
        self.create_buttons()
        self.create_volume_control()
        self.create_status_bar()

        self.root.after(100, self.check_music_end)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Playlist", command=self.create_playlist)
        file_menu.add_command(label="Add Songs", command=self.add_songs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        playlist_menu = tk.Menu(menubar, tearoff=0)
        playlist_menu.add_command(label="Shuffle Playlists", command=self.shuffle_playlists)
        playlist_menu.add_command(label="Sort Playlists", command=self.sort_playlist_menu)
        playlist_menu.add_command(label="Create Top Songs", command=self.create_top_playlist)
        menubar.add_cascade(label="Playlists", menu=playlist_menu)
        
        self.root.config(menu=menubar)

    def create_playlist_box(self):
        self.playlist_frame = tk.Frame(self.root)
        self.playlist_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(self.playlist_frame, text="Playlists").pack()
        self.playlist_box = tk.Listbox(self.playlist_frame, width=20, height=15)
        self.playlist_box.pack()
        self.playlist_box.bind('<<ListboxSelect>>', self.select_playlist)

    def create_song_box(self):
        self.song_frame = tk.Frame(self.root)
        self.song_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(self.song_frame, text="Songs").pack()
        self.song_box = tk.Listbox(self.song_frame, width=40, height=15)
        self.song_box.pack()
        self.song_box.bind('<<ListboxSelect>>', self.select_song)  # Fixed method name

    def create_buttons(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        prev_btn = tk.Button(control_frame, text="<<", command=self.prev_song)
        play_btn = tk.Button(control_frame, text="Play", command=self.play_song)
        pause_btn = tk.Button(control_frame, text="Pause", command=self.toggle_pause)
        next_btn = tk.Button(control_frame, text=">>", command=self.next_song)
        shuffle_btn = tk.Button(control_frame, text="Shuffle", command=self.shuffle_songs)
        sort_btn = tk.Button(control_frame, text="Sort", command=self.sort_song_menu)

        prev_btn.grid(row=0, column=0, padx=5)
        play_btn.grid(row=0, column=1, padx=5)
        pause_btn.grid(row=0, column=2, padx=5)
        next_btn.grid(row=0, column=3, padx=5)
        shuffle_btn.grid(row=0, column=4, padx=5)
        sort_btn.grid(row=0, column=5, padx=5)

    def create_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name:
            new_pl = self.playlists.add_playlist(name)
            self.playlist_box.insert(tk.END, name)
            self.playlists.current_playlist = new_pl

    def add_songs(self):
        if not self.playlists.current_playlist:
            messagebox.showerror("Error", "No playlist selected")
            return
            
        directory = filedialog.askdirectory()
        valid_extensions = ['.mp3', '.wav', '.ogg']
        
        for root_dir, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in valid_extensions):
                    path = os.path.join(root_dir, file)
                    title = os.path.splitext(file)[0]
                    self.playlists.current_playlist.songs.add_song(title, "Unknown", path)
        
        self.update_song_display()

    def select_playlist(self, event):
        selection = self.playlist_box.curselection()
        if not selection:
            return
        index = selection[0]
        current = self.playlists.head
        for _ in range(index):
            current = current.next
        self.playlists.current_playlist = current
        self.update_song_display()

    def select_song(self, event):  # Added missing method
        if not self.playlists.current_playlist:
            return
        selection = self.song_box.curselection()
        if selection:
            index = selection[0]
            self.play_song(index)

    def update_song_display(self):
        self.song_box.delete(0, tk.END)
        if not self.playlists.current_playlist:
            return
        current = self.playlists.current_playlist.songs.head
        while current:
            self.song_box.insert(tk.END, current.title)
            current = current.next

    def play_song(self, index=None):
        if not self.playlists.current_playlist:
            return
            
        songs = self.playlists.current_playlist.songs
        if index is not None:
            current = songs.head
            for _ in range(index):
                current = current.next
            songs.current = current
        else:
            songs.current = songs.head

        if songs.current:
            mixer.music.load(songs.current.path)
            mixer.music.play()
            songs.current.play_count += 1
            self.status_var.set(f"Now Playing: {songs.current.title}")
            self.paused = False

    def create_top_playlist(self):
        all_songs = self.playlists.get_all_songs()
        all_songs.sort(key=lambda x: -x.play_count)
        top_songs = all_songs[:10]  # Top 10 songs
        
        new_pl = self.playlists.add_playlist("Top Songs")
        for song in top_songs:
            new_pl.songs.add_song(song.title, song.artist, song.path)
            
        self.playlist_box.insert(tk.END, "Top Songs")
        self.playlists.current_playlist = new_pl
        self.update_song_display()

    def shuffle_playlists(self):
        self.playlists.shuffle_playlists()
        self.update_playlist_display()

    def sort_playlist_menu(self):
        self.sort_menu_window = tk.Toplevel()
        var = tk.StringVar(value="name")
        tk.Label(self.sort_menu_window, text="Sort Playlists By:").pack()
        tk.Radiobutton(self.sort_menu_window, text="Name", variable=var, value="name").pack()
        tk.Button(self.sort_menu_window, text="Sort", command=lambda: self.sort_playlists(var.get())).pack()

    def sort_playlists(self, key):
        self.playlists.sort_playlists_by(key)
        self.update_playlist_display()
        self.sort_menu_window.destroy()

    def update_playlist_display(self):
        self.playlist_box.delete(0, tk.END)
        current = self.playlists.head
        while current:
            self.playlist_box.insert(tk.END, current.name)
            current = current.next

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
        if not self.playlists.current_playlist:
            return
        songs = self.playlists.current_playlist.songs
        if songs.current and songs.current.next:
            songs.current = songs.current.next
            self.play_song()
            self.update_song_selection()

    def prev_song(self):
        if not self.playlists.current_playlist:
            return
        songs = self.playlists.current_playlist.songs
        if songs.current and songs.current.prev:
            songs.current = songs.current.prev
            self.play_song()
            self.update_song_selection()

    def update_song_selection(self):
        self.song_box.selection_clear(0, tk.END)
        current_node = self.playlists.current_playlist.songs.current
        index = 0
        node = self.playlists.current_playlist.songs.head
        while node != current_node:
            node = node.next
            index += 1
        self.song_box.selection_set(index)
        self.song_box.see(index)

    def shuffle_songs(self):
        if self.playlists.current_playlist:
            self.playlists.current_playlist.songs.shuffle()
            self.update_song_display()

    def sort_song_menu(self):
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Sort Songs")

        options = ["Title", "Artist", "Play Count"]
        var = tk.StringVar(value=options[0])

        tk.Label(sort_window, text="Sort by:").pack()
        for option in options:
            tk.Radiobutton(sort_window, text=option, variable=var, value=option).pack()

        confirm_btn = tk.Button(sort_window, text="Sort", command=lambda: self.sort_songs(var.get(), sort_window))
        confirm_btn.pack()

    def sort_songs(self, key, window):
        key_map = {
            "Title": "title",
            "Artist": "artist",
            "Play Count": "play_count"
        }
        if self.playlists.current_playlist:
            self.playlists.current_playlist.songs.sort_by(key_map[key])
            self.update_song_display()
        window.destroy()

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
    root.mainloop()