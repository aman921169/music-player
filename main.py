#here we are importing the required libraries
import customtkinter as ctk
import pygame
import random
import os
from tkinter import filedialog
from PIL import Image
from io import BytesIO
from mutagen.mp3 import MP3

pygame.mixer.init()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg": "#09090b",
    "surface": "#111114",
    "surface_light": "#1a1a20",
    "surface_raised": "#22222a",
    "border": "#2d2d38",
    "text": "#fafafa",
    "text_soft": "#d4d4d8",
    "text_muted": "#71717a",
    "accent": "#a78bfa",
    "accent_soft": "#c4b5fd",
    "accent_hover": "#8b5cf6",
    "active": "#2a2240",
    "active_border": "#7c3aed",
    "danger": "#3f1515",
    "danger_hover": "#7f1d1d",
    "success": "#14532d",
}

FONT_DISPLAY = ("Segoe UI", 24, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)
FONT_CAPTION = ("Segoe UI", 10, "bold")

#here we are creating the main window for the music player
app = ctk.CTk()
app.title("Music")
app.geometry("820x680")
app.minsize(760, 620)
app.configure(fg_color=COLORS["bg"])

playlist = []
playlist_buttons = {}
playlist_rows = {}
playlist_index_labels = {}
current_song = 0
current_duration = 0
user_seek = False
seek_offset = 0  # where the current pygame play() call started from, in seconds
shuffle_enabled = False 
repeat_enabled = False
is_playing = False

def song_name(file):
    return os.path.basename(file)

def set_playback_status(playing):
    if not playlist:
        status_chip.configure(text="● Ready", fg_color=COLORS["surface_raised"], text_color=COLORS["text_muted"])
        art_frame.configure(border_color=COLORS["border"])
    elif playing:
        status_chip.configure(text="● Playing", fg_color=COLORS["active"], text_color=COLORS["accent_soft"])
        art_frame.configure(border_color=COLORS["accent"])
    else:
        status_chip.configure(text="● Paused", fg_color=COLORS["surface_raised"], text_color=COLORS["text_muted"])
        art_frame.configure(border_color=COLORS["border"])

def refresh_playlist_indices():
    for index, file in enumerate(playlist):
        index_label = playlist_index_labels.get(file)
        if index_label is not None:
            index_label.configure(text=f"{index + 1:02d}")

def highlight_current_track():
    for index, file in enumerate(playlist):
        row = playlist_rows.get(file)
        button = playlist_buttons.get(file)
        index_label = playlist_index_labels.get(file)
        if row is None or button is None:
            continue
        if index == current_song:
            row.configure(fg_color=COLORS["active"], border_color=COLORS["active_border"])
            button.configure(
                text_color=COLORS["text"],
                hover_color=COLORS["active"],
            )
            if index_label is not None:
                index_label.configure(text_color=COLORS["accent_soft"])
        else:
            row.configure(fg_color=COLORS["surface_light"], border_color=COLORS["border"])
            button.configure(
                text_color=COLORS["text_soft"],
                hover_color=COLORS["surface_raised"],
            )
            if index_label is not None:
                index_label.configure(text_color=COLORS["text_muted"])

def update_queue_meta():
    count = len(playlist)
    queue_count_label.configure(text=f"{count} track{'s' if count != 1 else ''}")
    if count == 0:
        empty_queue_label.pack(pady=40)
    else:
        empty_queue_label.pack_forget()

def reset_now_playing_ui():
    global current_duration, seek_offset, is_playing
    current_duration = 0
    seek_offset = 0
    is_playing = False
    pygame.mixer.music.stop()
    song_label.configure(text="No song selected")
    elapsed_label.configure(text="0:00")
    total_label.configure(text="0:00")
    progress_slider.set(0)
    play_pause_button.configure(text="▶")
    album_art_label.configure(image=None, text="♪")
    album_art_label.image = None

def create_playlist_row(file):
    index = len(playlist)
    row = ctk.CTkFrame(
        playlist_frame,
        fg_color=COLORS["surface_light"],
        corner_radius=12,
        border_width=1,
        border_color=COLORS["border"],
    )
    row.pack(fill="x", pady=3, padx=2)

    index_label = ctk.CTkLabel(
        row,
        text=f"{index:02d}",
        width=28,
        font=FONT_SMALL,
        text_color=COLORS["text_muted"],
    )
    index_label.pack(side="left", padx=(12, 8))

    song_button = ctk.CTkButton(
        row,
        text=song_name(file),
        command=lambda song=file: play_selected_song(song),
        anchor="w",
        height=40,
        corner_radius=10,
        fg_color="transparent",
        hover_color=COLORS["surface_raised"],
        text_color=COLORS["text_soft"],
        font=FONT_BODY,
    )
    song_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

    remove_button = ctk.CTkButton(
        row,
        text="✕",
        width=34,
        height=34,
        corner_radius=10,
        font=("Segoe UI", 14),
        fg_color="transparent",
        hover_color=COLORS["danger_hover"],
        text_color=COLORS["text_muted"],
        command=lambda song=file: remove_from_playlist(song),
    )
    remove_button.pack(side="right", padx=(0, 8), pady=3)

    playlist_rows[file] = row
    playlist_buttons[file] = song_button
    playlist_index_labels[file] = index_label

def remove_from_playlist(file):
    global current_song, current_duration, is_playing, seek_offset

    if file not in playlist:
        return

    removed_index = playlist.index(file)
    was_current = removed_index == current_song
    was_playing = was_current and is_playing

    row = playlist_rows.pop(file, None)
    playlist_buttons.pop(file, None)
    playlist_index_labels.pop(file, None)
    if row is not None:
        row.destroy()

    playlist.remove(file)

    if not playlist:
        current_song = 0
        reset_now_playing_ui()
        update_queue_meta()
        set_playback_status(False)
        return

    if removed_index < current_song:
        current_song -= 1
    elif was_current:
        if current_song >= len(playlist):
            current_song = len(playlist) - 1

        next_file = playlist[current_song]
        if was_playing:
            play_selected_song(next_file)
        else:
            song_label.configure(text=song_name(next_file))
            load_album_art(next_file)
            current_duration = get_song_length(next_file)
            elapsed_label.configure(text="0:00")
            total_label.configure(text=format_duration(current_duration))
            progress_slider.set(0)
            highlight_current_track()
            set_playback_status(False)

    update_queue_meta()
    refresh_playlist_indices()
    highlight_current_track()

def change_control(value):
    pygame.mixer.music.set_volume(float(value))

def select_songs():
    files = filedialog.askopenfilenames(
        filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.flac")]
    )

    for file in files:
        if file in playlist:
            continue
        playlist.append(file)
        create_playlist_row(file)

    update_queue_meta()
    refresh_playlist_indices()
    highlight_current_track()

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
    
    load_album_art(file)
    
    is_playing = True
    play_pause_button.configure(text="⏸")
    seek_offset = 0

    current_duration = get_song_length(file)
    elapsed_label.configure(text="0:00")
    total_label.configure(text=format_duration(current_duration))

    song_label.configure(text=song_name(file))
    highlight_current_track()
    set_playback_status(True)

def next_song():
    global current_song
    global current_duration
    global seek_offset
    global is_playing

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
    play_pause_button.configure(text="⏸")
    seek_offset = 0

    load_album_art(file)
    current_duration = get_song_length(file)

    progress_slider.set(0)

    elapsed_label.configure(text="0:00")
    total_label.configure(text=format_duration(current_duration))

    song_label.configure(text=song_name(file))
    highlight_current_track()
    set_playback_status(True)

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
        play_pause_button.configure(text="⏸")
        seek_offset = 0

        load_album_art(file)
        current_duration = get_song_length(file)

        progress_slider.set(0)

        elapsed_label.configure(text="0:00")
        total_label.configure(text=format_duration(current_duration))
        song_label.configure(text=song_name(file))
        highlight_current_track()
        set_playback_status(True)

def check_music_end():
    global seek_offset
    if playlist and is_playing and not user_seek and not pygame.mixer.music.get_busy():
        
        if repeat_enabled:
            file = playlist[current_song]
            
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            seek_offset = 0  # fresh loop, wipe out any leftover offset from an earlier seek
            
            progress_slider.set(0)

            elapsed_label.configure(text="0:00")
            total_label.configure(text=format_duration(current_duration))
        
        elif current_song < len(playlist) - 1:
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

        elapsed_label.configure(text=format_duration(position))
        total_label.configure(text=format_duration(current_duration))
    app.after(500, update_progress)

def seek_song(value):
    # Called continuously while dragging the slider. Just update the time
    # label to give live feedback -- the actual seek happens on release
    # in stop_seeking(), otherwise we'd restart playback on every pixel
    # of drag movement.
    if current_duration > 0:
        position = (float(value) / 100) * current_duration
        elapsed_label.configure(text=format_duration(position))
        total_label.configure(text=format_duration(current_duration))


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
        shuffle_button.configure(
            text="Shuffle",
            fg_color=COLORS["active"],
            border_color=COLORS["active_border"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_soft"],
        )
    else:
        shuffle_button.configure(
            text="Shuffle",
            fg_color=COLORS["surface_raised"],
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_muted"],
        )

def toggle_repeat():
    global repeat_enabled
    repeat_enabled = not repeat_enabled
    if repeat_enabled:
        repeat_button.configure(
            text="Repeat",
            fg_color=COLORS["active"],
            border_color=COLORS["active_border"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_soft"],
        )
    else:
        repeat_button.configure(
            text="Repeat",
            fg_color=COLORS["surface_raised"],
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_muted"],
        )
        
def toggle_play_pause():
    global is_playing
    if not playlist:
        return
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False
        play_pause_button.configure(text="▶")
        set_playback_status(False)
    else:
        pygame.mixer.music.unpause()
        is_playing = True
        play_pause_button.configure(text="⏸")
        set_playback_status(True)

def load_album_art(file):
    try:
        audio = MP3(file)
        artwork = None

        if audio.tags:
            for tag in audio.tags.values():
                if tag.FrameID == "APIC":
                    artwork = tag.data
                    break

        if artwork:
            image = Image.open(BytesIO(artwork))
            image.thumbnail((228, 228))

            album_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )
            album_art_label.configure(image=album_image, text="")
            album_art_label.image = album_image  # keep a reference so it doesn't get garbage collected
        else:
            album_art_label.configure(image=None, text="♪")

    except Exception:
        # covers non-mp3 files (wav/ogg have no id3 tags) and anything else that goes wrong
        album_art_label.configure(image=None, text="♪")

main_container = ctk.CTkFrame(app, fg_color="transparent")
main_container.pack(fill="both", expand=True, padx=28, pady=24)

header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
header_frame.pack(fill="x", pady=(0, 18))

title_block = ctk.CTkFrame(header_frame, fg_color="transparent")
title_block.pack(side="left")

app_title = ctk.CTkLabel(
    title_block,
    text="Music",
    font=FONT_DISPLAY,
    text_color=COLORS["text"],
    anchor="w",
)
app_title.pack(anchor="w")

app_subtitle = ctk.CTkLabel(
    title_block,
    text="Your personal queue",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
    anchor="w",
)
app_subtitle.pack(anchor="w", pady=(2, 0))

status_chip = ctk.CTkLabel(
    header_frame,
    text="● Ready",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
    fg_color=COLORS["surface_raised"],
    corner_radius=14,
    width=88,
    height=28,
)
status_chip.pack(side="right")

now_playing_card = ctk.CTkFrame(
    main_container,
    fg_color=COLORS["surface"],
    corner_radius=22,
    border_width=1,
    border_color=COLORS["border"],
)
now_playing_card.pack(fill="x", pady=(0, 16))

now_playing_inner = ctk.CTkFrame(now_playing_card, fg_color="transparent")
now_playing_inner.pack(fill="x", padx=24, pady=24)

player_body = ctk.CTkFrame(now_playing_inner, fg_color="transparent")
player_body.pack(fill="x")

art_column = ctk.CTkFrame(player_body, fg_color="transparent")
art_column.pack(side="left", padx=(0, 28))

art_frame = ctk.CTkFrame(
    art_column,
    fg_color=COLORS["surface_light"],
    corner_radius=18,
    border_width=2,
    border_color=COLORS["border"],
)
art_frame.pack()

album_art_label = ctk.CTkLabel(
    art_frame,
    text="♪",
    width=228,
    height=228,
    corner_radius=16,
    fg_color=COLORS["surface_light"],
    text_color=COLORS["text_muted"],
    font=("Segoe UI", 58),
)
album_art_label.pack(padx=6, pady=6)

info_column = ctk.CTkFrame(player_body, fg_color="transparent")
info_column.pack(side="left", fill="both", expand=True)

now_playing_caption = ctk.CTkLabel(
    info_column,
    text="NOW PLAYING",
    font=FONT_CAPTION,
    text_color=COLORS["accent_soft"],
    anchor="w",
)
now_playing_caption.pack(fill="x", pady=(10, 6))

song_label = ctk.CTkLabel(
    info_column,
    text="No song selected",
    font=FONT_TITLE,
    text_color=COLORS["text"],
    anchor="w",
    justify="left",
    wraplength=380,
)
song_label.pack(fill="x", pady=(0, 22))

progress_frame = ctk.CTkFrame(info_column, fg_color="transparent")
progress_frame.pack(fill="x", pady=(0, 20))

elapsed_label = ctk.CTkLabel(
    progress_frame,
    text="0:00",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
    width=44,
    anchor="w",
)
elapsed_label.pack(side="left")

progress_slider = ctk.CTkSlider(
    progress_frame,
    from_=0,
    to=100,
    height=8,
    button_length=16,
    button_corner_radius=8,
    corner_radius=4,
    fg_color=COLORS["surface_raised"],
    progress_color=COLORS["accent"],
    button_color=COLORS["accent_soft"],
    button_hover_color=COLORS["text"],
    command=seek_song,
)
progress_slider.set(0)
progress_slider.pack(side="left", fill="x", expand=True, padx=10)

total_label = ctk.CTkLabel(
    progress_frame,
    text="0:00",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
    width=44,
    anchor="e",
)
total_label.pack(side="left")

progress_slider.bind("<ButtonPress-1>", start_seeking)
progress_slider.bind("<ButtonRelease-1>", stop_seeking)

controls_shell = ctk.CTkFrame(
    info_column,
    fg_color=COLORS["surface_light"],
    corner_radius=18,
    border_width=1,
    border_color=COLORS["border"],
)
controls_shell.pack(fill="x", pady=(0, 14))

nav_frame = ctk.CTkFrame(controls_shell, fg_color="transparent")
nav_frame.pack(pady=14)

def make_control_button(parent, text, command, primary=False):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=58 if primary else 46,
        height=58 if primary else 46,
        corner_radius=29 if primary else 23,
        font=("Segoe UI", 24 if primary else 17),
        fg_color=COLORS["accent"] if primary else "transparent",
        hover_color=COLORS["accent_hover"] if primary else COLORS["surface_raised"],
        text_color=COLORS["text"] if primary else COLORS["text_soft"],
        border_width=0 if primary else 1,
        border_color=COLORS["border"] if not primary else COLORS["accent"],
    )

previous_button = make_control_button(nav_frame, "⏮", previous_song)
previous_button.pack(side="left", padx=10)

play_pause_button = make_control_button(nav_frame, "▶", toggle_play_pause, primary=True)
play_pause_button.pack(side="left", padx=10)

next_button = make_control_button(nav_frame, "⏭", next_song)
next_button.pack(side="left", padx=10)

secondary_frame = ctk.CTkFrame(info_column, fg_color="transparent")
secondary_frame.pack(pady=(0, 12))

shuffle_button = ctk.CTkButton(
    secondary_frame,
    text="Shuffle",
    command=toggle_shuffle,
    width=108,
    height=36,
    corner_radius=18,
    font=FONT_SMALL,
    fg_color=COLORS["surface_raised"],
    hover_color=COLORS["border"],
    text_color=COLORS["text_muted"],
    border_width=1,
    border_color=COLORS["border"],
)
shuffle_button.pack(side="left", padx=(0, 8))

repeat_button = ctk.CTkButton(
    secondary_frame,
    text="Repeat",
    command=toggle_repeat,
    width=108,
    height=36,
    corner_radius=18,
    font=FONT_SMALL,
    fg_color=COLORS["surface_raised"],
    hover_color=COLORS["border"],
    text_color=COLORS["text_muted"],
    border_width=1,
    border_color=COLORS["border"],
)
repeat_button.pack(side="left")

volume_frame = ctk.CTkFrame(info_column, fg_color="transparent")
volume_frame.pack(fill="x")

volume_label = ctk.CTkLabel(
    volume_frame,
    text="🔊",
    font=("Segoe UI", 14),
    text_color=COLORS["text_muted"],
    width=28,
)
volume_label.pack(side="left")

volume_slider = ctk.CTkSlider(
    volume_frame,
    from_=0,
    to=1,
    height=8,
    button_length=14,
    button_corner_radius=7,
    corner_radius=4,
    fg_color=COLORS["surface_raised"],
    progress_color=COLORS["accent"],
    button_color=COLORS["accent_soft"],
    button_hover_color=COLORS["text"],
    command=change_control,
)
volume_slider.set(0.5)
volume_slider.pack(side="left", fill="x", expand=True, padx=(6, 0))

playlist_section = ctk.CTkFrame(
    main_container,
    fg_color=COLORS["surface"],
    corner_radius=22,
    border_width=1,
    border_color=COLORS["border"],
)
playlist_section.pack(fill="both", expand=True)

playlist_header = ctk.CTkFrame(playlist_section, fg_color="transparent")
playlist_header.pack(fill="x", padx=22, pady=(18, 10))

playlist_title_frame = ctk.CTkFrame(playlist_header, fg_color="transparent")
playlist_title_frame.pack(side="left")

playlist_title = ctk.CTkLabel(
    playlist_title_frame,
    text="Up Next",
    font=("Segoe UI", 17, "bold"),
    text_color=COLORS["text"],
    anchor="w",
)
playlist_title.pack(side="left")

queue_count_label = ctk.CTkLabel(
    playlist_title_frame,
    text="0 tracks",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
    fg_color=COLORS["surface_raised"],
    corner_radius=10,
    width=72,
    height=22,
)
queue_count_label.pack(side="left", padx=(10, 0))

select_button = ctk.CTkButton(
    playlist_header,
    text="+ Add Songs",
    command=select_songs,
    width=118,
    height=34,
    corner_radius=17,
    font=FONT_SMALL,
    fg_color=COLORS["accent"],
    hover_color=COLORS["accent_hover"],
    text_color=COLORS["text"],
)
select_button.pack(side="right")

playlist_frame = ctk.CTkScrollableFrame(
    playlist_section,
    fg_color="transparent",
    scrollbar_button_color=COLORS["surface_raised"],
    scrollbar_button_hover_color=COLORS["accent"],
)
playlist_frame.pack(fill="both", expand=True, padx=14, pady=(0, 18))

empty_queue_label = ctk.CTkFrame(
    playlist_frame,
    fg_color=COLORS["surface_light"],
    corner_radius=16,
    border_width=1,
    border_color=COLORS["border"],
)
empty_queue_label.pack(fill="x", padx=4, pady=24)

empty_icon = ctk.CTkLabel(
    empty_queue_label,
    text="♫",
    font=("Segoe UI", 34),
    text_color=COLORS["text_muted"],
)
empty_icon.pack(pady=(22, 6))

empty_text = ctk.CTkLabel(
    empty_queue_label,
    text="Your queue is empty",
    font=FONT_BODY,
    text_color=COLORS["text_soft"],
)
empty_text.pack()

empty_hint = ctk.CTkLabel(
    empty_queue_label,
    text="Add songs to start listening",
    font=FONT_SMALL,
    text_color=COLORS["text_muted"],
)
empty_hint.pack(pady=(4, 22))

update_queue_meta()
set_playback_status(False)
check_music_end()
update_progress()
app.mainloop()