from pytube import YouTube, Playlist
import ffmpeg
import tkinter as tk
import string
import os
import shutil
import yt_dlp
import json


def normalize_button_pressed():
    path = entry_filename.get()
    filetype_final = filetype_selected_local.get()
    # Check if it's a file
    if os.path.isfile(path):
        normalize_file('', path, filetype_final)
    # Check if it's a folder
    elif os.path.isdir(path):
        for path, dirs, files in os.walk(path):
            for file in files:
                normalize_file(path, file, filetype_final)
    else:
        print('Unknown file or folder:', path)
    print("Finished")


def normalize_file(path, filename, filetype_final):
    # Reads the file
    if path == '':
        filepath = filename
    else:
        filepath = f'{path}/{filename}'
    video = ffmpeg.input(filepath).video
    audio_original = ffmpeg.input(filepath).audio
    audio_normalized = normalize(audio_original)

    # Decide new filetype
    title, filetype = os.path.splitext(filename)
    filetype = filetype[1:]
    if filetype_final == 'unchanged':
        filetype_final = filetype

    # Check if the final file name already exists in the directory
    filename_final = f'{title}.{filetype_final}'
    title_new = title
    while os.path.exists(filename_final):
        title_new = f'{title_new} alt'
        filename_final = f'{title_new}.{filetype_final}'
    
    # Saves the new audio file and keeps the original video
    audio_new = ffmpeg.output(video, audio_normalized, f'{filename_final}', vcodec='copy')
    try:
        audio_new.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        stderr = e.stderr.decode('utf8')
        if "Invalid data found when processing input" in stderr:
            pass
        else:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', stderr)
            raise e


def download_button_pressed():
    # Retrieves the video url and requested filetype
    url = entry_url.get()
    filetype_video = filetype_selected_video.get()
    filetype_audio = filetype_selected_audio.get()
    print("URL: %s" % url)
    print("Video/audio types: %s/%s" % (filetype_video, filetype_audio))
    # Check if neither video nor audio is requested
    if filetype_video == 'none' and filetype_audio == 'none':
        print("No video/audio filetype selected.")
        return
    with yt_dlp.YoutubeDL({"keepvideo": False, "outtmpl": "%(title)s"}) as ydl:
        info = ydl.extract_info(url)
    filepath = info["requested_downloads"][0]["filepath"]
    if normalize_selected.get() == 1:
        print("Normalizing audio")
        normalize_file("", filepath, filetype_video)
    print("Finished")


# download highest quality video and audio from youtube
def download_highest_quality(url, filetype_video, filetype_audio):
    return
    yt = YouTube(url)
    title = yt.title
    # Sets a temporary filetype in which the audio/video will be downloaded
    if filetype_video != 'none':
        filetype_general = filetype_video
    else:
        filetype_general = 'mp4'
    filename_general = f'{title}.{filetype_general}'
    
    # Selects the video with the highest quality and downloads them
    if filetype_video != 'none':
        video = yt.streams.filter(adaptive=True, mime_type=f'video/{filetype_general}')[0]
        video.download('temp/video', filename=f'{filename_general}')
        # Reads the video file
        video = ffmpeg.input(f'temp/video/{filename_general}')
    
    # Selects the audio with the highest quality and downloads them
    if filetype_audio != 'none':
        # Selects the audio with the highest quality and downloads them
        audio = yt.streams.filter(adaptive=True, mime_type=f'audio/{filetype_general}')[-1]
        audio.download('temp/audio', filename=f'{filename_general}')
        # Reads the audio file
        audio = ffmpeg.input(f'temp/audio/{filename_general}')
        # Normalizes the audio if selected
        if normalize_selected.get() == 1:
            audio = normalize(audio)

    # Check if the final file name already exists in the directory
    if filetype_video != 'none':
        filetype_final = filetype_video
    else:
        filetype_final = filetype_audio
    filename_final = f'{title}.{filetype_final}'
    title_new = title
    while os.path.exists(filename_final):
        title_new = f'{title_new} alt'
        filename_final = f'{title_new}.{filetype_final}'
    
    # If both video and audio have been downloaded
    if filetype_video != 'none' and filetype_audio != 'none':
        # Merges the video and audio
        merged_video = ffmpeg.output(video, audio, f'{filename_final}', vcodec='copy')
        try:
            merged_video.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e
    # If only the video has been downloaded
    elif filetype_audio == 'none':
        # Moves the video file from temp to root
        shutil.copyfile(f'temp/video/{filename_general}', f'{filename_final}')
    # If only the audio has been downloaded
    elif filetype_video == 'none':
        # Saves the new audio file
        audio_new = ffmpeg.output(audio, f'{filename_final}')
        try:
            audio_new.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e
    
    # Removes the downloaded video and audio file
    try:
        os.remove(f'temp/video/{filename_general}')
    except Exception as e:
        pass
    try:
        os.remove(f'temp/audio/{filename_general}')
    except Exception as e:
        pass


def normalize(audio):
    normalized_audio = ffmpeg.filter(audio, 'loudnorm')
    return normalized_audio


# Setting up the user interface
window = tk.Tk()
window.geometry('400x300')
window.title('Youtube downloader and audio normalizer')
window.columnconfigure(0, minsize=400)
window.rowconfigure(1, minsize=180)
# Creates the frames
frame_source_selection = tk.Frame(window)
frame_body = tk.Frame(window)
frame_bottom = tk.Frame(window)
frame_source_selection.grid(row=0)
frame_body.grid(row=1)
frame_bottom.grid(row=2)
# Sets up the source selection for the video/audio
SOURCES = ['youtube', 'local']
label_source_selection = tk.Label(frame_source_selection, text="Media source:")
source_selection = tk.StringVar()
source_selection.set(SOURCES[0])
menu_source_selection = tk.OptionMenu(frame_source_selection, source_selection, *SOURCES)
# Sets up the folder selection entry field
label_filename = tk.Label(frame_body, text="Folder or filename in current directory:")
entry_filename = tk.Entry(frame_body, width=50)
# Sets up file type selection
FILETYPES_LOCAL = ['unchanged', 'mp4']
label_filetype_local = tk.Label(frame_body, text="New filetype:")
filetype_selected_local = tk.StringVar()
filetype_selected_local.set(FILETYPES_LOCAL[0])
menu_filetype_local = tk.OptionMenu(frame_body, filetype_selected_local, *FILETYPES_LOCAL)
# Sets up the video url entry field
label_url = tk.Label(frame_body, text="Video or playlist URL:")
entry_url = tk.Entry(frame_body, width=50)
# Sets up video type selection
FILETYPES_VIDEO = ['mp4', 'webm', 'none']
label_filetype_video = tk.Label(frame_body, text="Filetype video:")
filetype_selected_video = tk.StringVar()
filetype_selected_video.set(FILETYPES_VIDEO[0])
menu_filetype_video = tk.OptionMenu(frame_body, filetype_selected_video, *FILETYPES_VIDEO)
# Sets up audio type selection
FILETYPES_AUDIO = ['mp4', 'webm', 'mp3', 'none']
label_filetype_audio = tk.Label(frame_body, text="Filetype audio:")
filetype_selected_audio = tk.StringVar()
filetype_selected_audio.set(FILETYPES_AUDIO[0])
menu_filetype_audio = tk.OptionMenu(frame_body, filetype_selected_audio, *FILETYPES_AUDIO)
# Sets up the checkbox for normalizing audio
normalize_selected = tk.IntVar()
checkbox_normalize = tk.Checkbutton(frame_body, text="Normalize audio", variable=normalize_selected)
# Creates the button to normalize files
button_normalize = tk.Button(frame_bottom, text="Normalize audio", width=20, height=2, command=normalize_button_pressed)
# Creates the button the download a video
button_download = tk.Button(frame_bottom, text="Download", width=20, height=2, command=download_button_pressed)
# Finalizes the user interface
label_source_selection.pack()
menu_source_selection.pack()
label_url.pack()
entry_url.pack()
label_filetype_video.pack()
menu_filetype_video.pack()
label_filetype_audio.pack()
menu_filetype_audio.pack()
checkbox_normalize.select()

while True:
    if source_selection.get() == 'youtube':
        label_filename.pack_forget()
        entry_filename.pack_forget()
        label_filetype_local.pack_forget()
        menu_filetype_local.pack_forget()
        button_normalize.pack_forget()
        label_url.pack()
        entry_url.pack()
        label_filetype_video.pack()
        menu_filetype_video.pack()
        label_filetype_audio.pack()
        menu_filetype_audio.pack()
        checkbox_normalize.pack()
        button_download.pack()
    elif source_selection.get() == 'local':
        label_filename.pack()
        entry_filename.pack()
        label_filetype_local.pack()
        menu_filetype_local.pack()
        button_normalize.pack()
        label_url.pack_forget()
        entry_url.pack_forget()
        label_filetype_video.pack_forget()
        menu_filetype_video.pack_forget()
        label_filetype_audio.pack_forget()
        menu_filetype_audio.pack_forget()
        checkbox_normalize.pack_forget()
        button_download.pack_forget()
        
    window.update_idletasks()
    window.update()
