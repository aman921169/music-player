#here we are importing the required libraries
import customtkinter as ctk
import pygame
from tkinter import filedialog

pygame.mixer.init()

#here we are creating the main window for the music player
app = ctk.CTk()
app.title("Music Player")
app.geometry("500x400")

playlist = []
current_song = 0
current_duration = 0
user_seek = False
seek_offset = 0  # where the current pygame play() call started from, in seconds

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

def format_duration(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"
    
def play_selected_song(file):
    global current_song
    global current_duration
    global seek_offset
    current_song = playlist.index(file)

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    seek_offset = 0

    current_duration = get_song_length(file)
    duration_label.configure(
        text=f"0:00 / {format_duration(current_duration)}"
    )

    song_label.configure(text=file.split("/")[-1])  # Update the label with the selected song name

def next_song():
    global current_song
    global current_duration
    global seek_offset
    if not playlist:
        return  # No songs in the playlist
    if current_song < len(playlist) - 1:
        current_song += 1

        file = playlist[current_song]

        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        seek_offset = 0

        current_duration = get_song_length(file)

        progress_slider.set(0)

        duration_label.configure(
            text=f"0:00 / {format_duration(current_duration)}"
        )

        song_label.configure(text=file.split("/")[-1])  # Update the label with the next song name

def previous_song():
    global current_song
    global current_duration
    global seek_offset

    if not playlist:
        return
    if current_song > 0:
        current_song -= 1

        file = playlist[current_song]

        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        seek_offset = 0

        current_duration = get_song_length(file)

        progress_slider.set(0)

        duration_label.configure(
            text=f"0:00 / {format_duration(current_duration)}"
        )
        song_label.configure(text=file.split("/")[-1])  # Update the label with the previous song name

def check_music_end():
    if playlist and not pygame.mixer.music.get_busy():
        if current_song < len(playlist) - 1:
            next_song()

    app.after(500, check_music_end)

def get_song_length(file):
    sound = pygame.mixer.Sound(file)
    return sound.get_length()



def update_progress():
    if current_duration > 0 and not user_seek:
        position = seek_offset + (pygame.mixer.music.get_pos() / 1000)

        progress = (position / current_duration) * 100

        progress_slider.set(progress)

        duration_label.configure(
            text=f"{format_duration(position)} / {format_duration(current_duration)}"
        )
    app.after(500, update_progress)

def seek_song(value):
    # Called continuously while dragging the slider. Just update the time
    # label to give live feedback -- the actual seek happens on release
    # in stop_seeking(), otherwise we'd restart playback on every pixel
    # of drag movement.
    if current_duration > 0:
        position = (float(value) / 100) * current_duration
        duration_label.configure(
            text=f"{format_duration(position)} / {format_duration(current_duration)}"
        )


def start_seeking(event):
    global user_seek
    user_seek = True


def stop_seeking(event):
    global user_seek
    global seek_offset
    user_seek = False

    if current_duration > 0:
        value = progress_slider.get()
        position = (value / 100) * current_duration
        pygame.mixer.music.play(start=position)
        seek_offset = position




song_label = ctk.CTkLabel(
    app,
    text="no song selected",
    font=("Arial", 20)
)
song_label.pack(pady=40)

duration_label = ctk.CTkLabel(
app,
    text="0:00/0:00"
)
duration_label.pack(pady=5)

progress_slider = ctk.CTkSlider(
    app,
    from_=0,
    to=100,
    width=400,
    command=seek_song
)
progress_slider.set(0)
progress_slider.pack(pady=10)

progress_slider.bind("<ButtonPress-1>", start_seeking)
progress_slider.bind("<ButtonRelease-1>", stop_seeking)

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

next_button = ctk.CTkButton(
    app,
    text = "⏭ Next" ,
    command=next_song
)
next_button.pack(pady=10)

previous_button = ctk.CTkButton(
    app,
    text = "⏮ Previous",
    command=previous_song
)
previous_button.pack(pady=10)

#check_music_end()
update_progress()
app.mainloop()
