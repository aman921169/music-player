# Music Player

A simple desktop music player built with Python, CustomTkinter, and pygame.

This project was built step by step as a learning project while practicing Python, GUI development, audio playback, and event-driven programming.

## Features

- Add multiple songs to a playlist
- Play songs from the playlist
- Pause and resume playback
- Stop playback
- Next and previous song controls
- Volume control
- Display the current song name
- Display the current playback time and total duration
- Live playback progress bar
- Seek through a song using the progress bar
- Supports MP3, WAV, and OGG audio files
- shuffle
- repeat

## Technologies Used

- Python
- CustomTkinter
- pygame
- Tkinter file dialogs
- Git and GitHub

## How It Works

- **CustomTkinter** creates the graphical interface.
- **pygame.mixer.music** handles audio playback.
- A Python list stores the playlist.
- Button and slider callbacks respond to user actions.
- `app.after()` updates the playback progress periodically.

## Installation

Install the required packages:

```bash
pip install customtkinter pygame
```

Run the application:

```bash
python main.py
```

## Usage

1. Click **Add Songs**.
2. Select one or more audio files.
3. Click a song from the playlist to start playing it.
4. Use the playback controls to pause, resume, stop, or change songs.
5. Use the volume slider to control the volume.
6. Drag the progress bar to seek through the current song.

## Project Structure

```text
music-player/
│
├── main.py
├── README.md
└── ...
```

## Learning Goals

This project helped me practice:

- Python functions
- Variables and global state
- Lists and indexes
- GUI widgets
- Button callbacks
- Slider callbacks
- Mouse events
- Audio playback with pygame
- Updating GUI elements with `after()`
- File dialogs
- Git and GitHub

## Planned Improvements

- Keyboard shortcuts
- Album artwork
- Remember volume settings
- Remove songs from the playlist
- Save and load playlists
- Improved UI
- FLAC support
