#here we are importing the required libraries
import customtkinter as ctk
import pygame
from tkinter import filedialog

pygame.mixer.init()

#here we are creating the main window for the music player
app = ctk.CTk()
app.title("Music Player")
app.size = (500, 400)

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

song_label = ctk.CTkLabel(
    app,
    text="no song selected",
    font=("Arial", 20)
)
song_label.pack(pady=40)

select_button = ctk.CTkButton(
    app,
    text="Select Song",
    command=select_song
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
