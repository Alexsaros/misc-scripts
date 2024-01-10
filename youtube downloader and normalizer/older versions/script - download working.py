from pytube import YouTube
import ffmpeg
import tkinter as tk
import string
import os

def format_filename(filename):
    # Determines which characters are appropiate for a filename
    valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def download_button():
    # Retrieves the video url and requested filetype and downloads the video
    url = entry_url.get()
    filetype = filetype_selected.get()
    download_highest_quality(url, filetype)
    # Removes the temp directories if they exist
    try:
        os.rmdir('temp/video')
        os.rmdir('temp/audio')
        os.rmdir('temp')
    except:
        pass

# download highest quality video and audio from youtube
def download_highest_quality(url, filetype):
    yt = YouTube(url)
    title = format_filename(yt.title)
    filename = f'{title}.{filetype}'
    # Selects the video and audio with the highest quality and downloads them
    video = yt.streams.filter(adaptive=True, mime_type=f'video/{filetype}')[0]
    audio = yt.streams.filter(adaptive=True, mime_type=f'audio/{filetype}')[-1]
    video.download('temp/video', filename=f'{filename}')
    audio.download('temp/audio', filename=f'{filename}')
    # Reads the video and audio file
    video = ffmpeg.input(f'temp/video/{filename}')
    audio = ffmpeg.input(f'temp/audio/{filename}')
    # Normalizes the audio if selected
    if normalize_selected.get() == 1:
        audio = normalize(audio)
    # Merges the video and audio
    merged_video = ffmpeg.output(video, audio, f'{filename}', vcodec='copy')
    try:
        merged_video.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e
    # Removes the downloaded video and audio file
    os.remove(f'temp/video/{filename}')
    os.remove(f'temp/audio/{filename}')

def normalize(audio):
    normalized_audio = ffmpeg.filter(audio, 'loudnorm')
    return normalized_audio

#TODO add check if file already exists/overwrite

# Setting up the user interface
window = tk.Tk()
# Sets up the video url entry field
label_url = tk.Label(text="Video or playlist URL:")
entry_url = tk.Entry(width=50)
# Sets up the filetype selection
FILETYPES = ["mp4", "webm"]
label_filetype = tk.Label(text="Filetype:")
filetype_selected = tk.StringVar()
filetype_selected.set(FILETYPES[0])
menu_filetype = tk.OptionMenu(window, filetype_selected, *FILETYPES)
# Sets up the checkbox for normalizing audio
normalize_selected = tk.IntVar()
checkbox_normalize = tk.Checkbutton(text="Normalize audio", variable=normalize_selected)
# Creates the button the download a video
button_download = tk.Button(text="Download", width=10, height=2, command=download_button)
# Finalizes the user interface
label_url.pack()
entry_url.pack()
label_filetype.pack()
menu_filetype.pack()
checkbox_normalize.pack()
checkbox_normalize.select()
button_download.pack()

#url = 'https://www.youtube.com/watch?v=VcsnVJ5BFWQ'
#download_highest_quality(url, 'mp4')

window.mainloop()
