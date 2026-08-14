# 🎵 Music Player

A desktop music player built with Python, CustomTkinter, and Pygame.

This project started as a simple Python music player and was gradually expanded with playlist management, playback controls, seeking, shuffle, repeat, album artwork, and a polished dark-themed interface.

## ✨ Features

- ▶️ Play / Pause
- ⏮️ Previous track
- ⏭️ Next track
- 🔀 Shuffle
- 🔁 Repeat
- 🎚️ Volume control
- ⏱️ Playback progress and duration
- 🎯 Seek through songs using the progress bar
- 🖼️ Embedded album artwork for supported MP3 files
- 📋 Playlist management
- ➕ Add multiple songs at once
- ❌ Remove songs from the playlist
- 🎵 Current track highlighting
- 📜 Scrollable playlist
- ▶️ Playing / Paused status indicator
- 🚫 Prevents duplicate songs from being added to the playlist
- 🌙 Dark-themed UI
- 🖥️ Windows executable available

## 🛠️ Built With

- **Python**
- **CustomTkinter** — graphical user interface
- **Pygame** — audio playback
- **Pillow** — album artwork/image handling
- **Mutagen** — MP3 metadata and album artwork
- **Tkinter** — file selection dialogs

## 🎧 Supported Audio Formats

The file picker currently supports:

- MP3
- WAV
- OGG
- FLAC

> Playback support ultimately depends on the audio formats supported by the Pygame mixer/backend on the system.
