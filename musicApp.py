import pygame
from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import os


class Song:

    def __init__(self, title, artist, duration, playcount):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.playcount = playcount

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.duration})"

class DNode:
    
    def __init__(self,song):
        self.song= song
        self.next = None
        self.previous = None

# class Playlist:
#     # shuffle
#     # sort
#     # store
#     # display
#     # next
#     # previous
#     # play
#     # pause
#     # based on doubly linked list ---> to store all the songs.


def create_sort_dropdown(root):
    frame = ctk.CTkFrame(root)
    frame.pack(pady=10)
    
    # Define the sort function
    def sort_items(option):
        print(f"Sorting by: {option}")
        # Here you would add your actual sorting logic
    
    # Create a CTkButton that will serve as our dropdown trigger
    sort_button = ctk.CTkButton(frame, text="Sort", width=80)
    sort_button.pack(side="left", padx=5)
    
    # Create the dropdown menu
    dropdown_menu = Menu(root, tearoff=0)
    dropdown_menu.add_command(label="By Artist", command=lambda: sort_items("Artist"))
    dropdown_menu.add_command(label="By Title", command=lambda: sort_items("Title"))
    dropdown_menu.add_command(label="By Play Count", command=lambda: sort_items("Play Count"))
    
    # Bind the button click to show the dropdown menu
    def show_dropdown(event):
        # Position the menu under the button
        x = sort_button.winfo_rootx()
        y = sort_button.winfo_rooty() + sort_button.winfo_height()
        dropdown_menu.post(x, y)
    
    sort_button.bind("<Button-1>", show_dropdown)
    
    return frame


songs = []
currentSong = ""
paused = False

def loadMusic():
    global currentSong
    root.directory = filedialog.askdirectory()

    for song in os.listdir(root.directory):
        song_name, extn=os.path.splitext(song)
        if extn == ".mp3" or extn == ".WAV":
            songs.append(song)

    for i in songs:
        songList.insert("end",song)


    songList.selection_set(0)
    currentSong = songs[songList.curselection()[0]]





root = ctk.CTk()
root.title("DSAfy Music App")
root.geometry("600x400")

ctk.set_appearance_mode("dark")  # Options: "dark", "light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
    


pygame.mixer.init()

menuBar = Menu(root)
root.config(menu=menuBar)

organise_menu = Menu(menuBar,tearoff=False)
organise_menu.add_command(label="Select Folder", command=loadMusic)
menuBar.add_cascade(label="Organise", menu=organise_menu)


songList = ctk.CTkTextbox(root, fg_color=("#000000", "#000000"), text_color="white", width=300, height=150, corner_radius=20)
songList.pack()

button = ctk.CTkButton(root, text="Shuffle")
button.pack(pady=20)


controlsFrame = ctk.CTkFrame(root)
controlsFrame.pack(pady=20)

prevbtn = ctk.CTkButton(controlsFrame,text="⏮",width=50,height=40, border_width=0)
prevbtn.pack(side="left",padx=10)

nextbtn = ctk.CTkButton(controlsFrame,text="⏭",width=50,height=40, border_width=0)
nextbtn.pack(side="left",padx=10)

pausebtn = ctk.CTkButton(controlsFrame,text="⏸️",width=50,height=40, border_width=0)
pausebtn.pack(side="left",padx=10)

playbtn = ctk.CTkButton(controlsFrame,text="▶️",width=50,height=40, border_width=0)
playbtn.pack(side="left",padx=10)

# playbtn = ctk.CTkButton(controlsFrame,text="▶️",command=playSongFunc,width=60,height=40) <----this is the way


sort_frame = create_sort_dropdown(root)
    

root.mainloop()