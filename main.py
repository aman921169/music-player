#here we are importing the required libraries
import customtkinter as ctk
import pygame
import random
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
shuffle_enabled = False 
repeat_enabled = False
is_playing = False

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
    global is_playing
    current_song = playlist.index(file)

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    
    is_playing = True
    play_pause_button.configure(text="⏸ Pause")
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
        return

    if shuffle_enabled:
        if len(playlist) == 1:
            current_song = 0
        else:
            available_songs = list(range(len(playlist)))
            available_songs.remove(current_song)
            current_song = random.choice(available_songs)

    else:
        if current_song < len(playlist) - 1:
            current_song += 1
        elif repeat_enabled:
            current_song = 0
        else:
            return

    file = playlist[current_song]

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    is_playing = True
    play_pause_button.configure(text="⏸ Pause")
    seek_offset = 0

    current_duration = get_song_length(file)

    progress_slider.set(0)

    duration_label.configure(
        text=f"0:00 / {format_duration(current_duration)}"
    )

    song_label.configure(
        text=file.split("/")[-1]
    )

def previous_song():
    global current_song
    global current_duration
    global seek_offset
    global is_playing
    if not playlist:
        return
    if current_song > 0:
        current_song -= 1

        file = playlist[current_song]

        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        is_playing = True
        play_pause_button.configure(text="⏸ Pause")
        seek_offset = 0

        current_duration = get_song_length(file)

        progress_slider.set(0)

        duration_label.configure(
            text=f"0:00 / {format_duration(current_duration)}"
        )
        song_label.configure(text=file.split("/")[-1])  # Update the label with the previous song name

def check_music_end():
    if playlist and is_playing and not user_seek and not pygame.mixer.music.get_busy():
        
        if repeat_enabled:
            file = playlist[current_song]
            
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            
            progress_slider.set(0)
            
            duration_label.configure(
                text=f"0:00 / {format_duration(current_duration)}"
            )
        
        elif current_song < len(playlist):
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

def toggle_shuffle():
    global shuffle_enabled

    shuffle_enabled = not shuffle_enabled

    if shuffle_enabled:
        shuffle_button.configure(text="🔀 Shuffle: ON")
    else:
        shuffle_button.configure(text="🔀 Shuffle: OFF")

def toggle_repeat():
    global repeat_enabled
    repeat_enabled = not repeat_enabled
    if repeat_enabled:
        repeat_button.configure(text="🔁 Repeat: ON")
    else:
        repeat_button.configure(text="🔁 Repeat: OFF")
        
def toggle_play_pause():
    global is_playing
    if not playlist:
        return
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False
        play_pause_button.configure(text="▶ Play")
    else:
        pygame.mixer.music.unpause()
        is_playing = True
        play_pause_button.configure(text="⏸ Pause")
        
        
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

nav_frame = ctk.CTkFrame(app)
nav_frame.pack(pady=10)

secondary_frame = ctk.CTkFrame(app)
secondary_frame.pack(pady=5)

select_button = ctk.CTkButton(
    app,
    text="add Songs",
    command=select_songs
)
select_button.pack(pady=10)

play_pause_button = ctk.CTkButton(
    nav_frame,
    text="▶ Play",
    command=toggle_play_pause
)
play_pause_button.pack(side = "left",padx=5)

volume_slider = ctk.CTkSlider(
    app,
    from_=0,
    to=1,
    command=change_control
)
volume_slider.set(0.5)
volume_slider.pack(pady=10)

next_button = ctk.CTkButton(
    nav_frame,
    text = "⏭ Next" ,
    command=next_song
)
next_button.pack(side = "left",padx=5)

previous_button = ctk.CTkButton(
    nav_frame,
    text = "⏮ Previous",
    command=previous_song
)
previous_button.pack(side = "left",padx=5)

shuffle_button = ctk.CTkButton(
    secondary_frame,
    text = "🔀 Shuffle: OFF",
    command = toggle_shuffle
)
shuffle_button.pack(side = "left",padx=5)

repeat_button = ctk.CTkButton(
    secondary_frame,
    text="🔁 Repeat: OFF",
    command=toggle_repeat
)
repeat_button.pack(side = "left",padx=5)
check_music_end()
update_progress()
app.mainloop()