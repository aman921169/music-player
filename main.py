#here we are importing the required libraries
import customtkinter as ctk
import pygame
from tkinter import filedialog

pygame.mixer.init()

#here we are creating the main window for the music player
app = ctk.CTk()
app.title("Music Player")
app.geometry = (500, 400)

playlist = []
current_song = 0

#this function allows the user to select a music file from their computer
def select_song():
    file = filedialog.askopenfilename(
        filetypes=[("Audio files", "*.mp3 *.wav *.ogg")]
        )
    if file:
        pygame.mixer.music.load(file)
        song_label.configure(text=file.split("/")[-1])  # Display only the file name


def play_song():
    pygame.mixer.music.play()

def pause_song():
    pygame.mixer.music.pause()

def resume_song():
    pygame.mixer.music.unpause()

def stop_song():
    pygame.mixer.music.stop()

def change_control(value):
    pygame.mixer.music.set_volume(float(value))

def select_songs():
    files = filedialog.askopenfilenames(
        filetypes=[("Audio files", "*.mp3 *.wav *.ogg")]
    )

    for file in files:
        playlist.append(file)
        song_button = ctk.CTkButton(
            playlist_frame,
            text=file.split("/")[-1],
            command=lambda song=file: play_selected_song(song)
        )
        song_button.pack(pady=5)
    
def play_selected_song(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    song_label.configure(text=file.split("/")[-1])  # Update the label with the selected song name

song_label = ctk.CTkLabel(
    app,
    text="no song selected",
    font=("Arial", 20)
)
song_label.pack(pady=40)

playlist_frame = ctk.CTkFrame(
    app,
    width = 400,
    height = 150
    )
playlist_frame.pack(pady=10)

select_button = ctk.CTkButton(
    app,
    text="add Songs",
    command=select_songs
)
select_button.pack(pady=10)

play_button = ctk.CTkButton(
    app,
    text="▶ Play",
    command=play_song
)
play_button.pack(pady=10)

resume_button = ctk.CTkButton(
    app,
    text="⏯ Resume",
    command=resume_song
)
resume_button.pack(pady=10)

pause_button = ctk.CTkButton(
    app,
    text="⏸ Pause",
    command=pause_song
)
pause_button.pack(pady=10)

stop_button = ctk.CTkButton(
    app,
    text="⏹ Stop",
    command=stop_song
)
stop_button.pack(pady=10)

volume_slider = ctk.CTkSlider(
    app,
    from_=0,
    to=1,
    command=change_control
)
volume_slider.set(0.5)
volume_slider.pack(pady=10)


app.mainloop()
