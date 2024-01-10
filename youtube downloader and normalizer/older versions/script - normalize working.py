from pytube import YouTube
import ffmpeg
import tkinter as tk
import string
import os
import shutil

def format_filename(filename):
    # Determines which characters are appropiate for a filename
    valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def download_button():
    # Retrieves the video url and requested filetype and downloads the video
    url = entry_url.get()
    filetype_video = filetype_selected_video.get()
    filetype_audio = filetype_selected_audio.get()
    if filetype_video != 'none' or filetype_audio != 'none':
        download_highest_quality(url, filetype_video, filetype_audio)
    # Removes the temp directories if they exist
    try:
        os.rmdir('temp/video')
    except:
        pass
    try:
        os.rmdir('temp/audio')
    except:
        pass
    try:
        os.rmdir('temp')
    except:
        pass

# download highest quality video and audio from youtube
def download_highest_quality(url, filetype_video, filetype_audio):
    yt = YouTube(url)
    title = format_filename(yt.title)
    for stream in yt.streams:
        print(stream)
    print('---')
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
        print("exists")
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
        # Moves the audio file from temp to root
        shutil.copyfile(f'temp/audio/{filename_general}', f'{filename_final}')
    
    # Removes the downloaded video and audio file
    try:
        os.remove(f'temp/video/{filename_general}')
    except Exception as e:
        print(e)
    try:
        os.remove(f'temp/audio/{filename_general}')
    except Exception as e:
        print(e)

def normalize(audio):
    normalized_audio = ffmpeg.filter(audio, 'loudnorm')
    return normalized_audio

# Setting up the user interface
window = tk.Tk()
# Sets up the video url entry field
label_url = tk.Label(text="Video or playlist URL:")
entry_url = tk.Entry(width=50)
# Sets up video type selection
FILETYPES_VIDEO = ['mp4', 'webm', 'none']
label_filetype_video = tk.Label(text="Filetype video:")
filetype_selected_video = tk.StringVar()
filetype_selected_video.set(FILETYPES_VIDEO[0])
menu_filetype_video = tk.OptionMenu(window, filetype_selected_video, *FILETYPES_VIDEO)
# Sets up audio type selection
FILETYPES_AUDIO = ['mp4', 'webm', 'none']
label_filetype_audio = tk.Label(text="Filetype audio:")
filetype_selected_audio = tk.StringVar()
filetype_selected_audio.set(FILETYPES_AUDIO[0])
menu_filetype_audio = tk.OptionMenu(window, filetype_selected_audio, *FILETYPES_AUDIO)
# Sets up the checkbox for normalizing audio
normalize_selected = tk.IntVar()
checkbox_normalize = tk.Checkbutton(text="Normalize audio", variable=normalize_selected)
# Creates the button the download a video
button_download = tk.Button(text="Download", width=10, height=2, command=download_button)
# Finalizes the user interface
label_url.pack()
entry_url.pack()
label_filetype_video.pack()
menu_filetype_video.pack()
label_filetype_audio.pack()
menu_filetype_audio.pack()
checkbox_normalize.pack()
checkbox_normalize.select()
button_download.pack()

#url = 'https://www.youtube.com/watch?v=VcsnVJ5BFWQ'
#download_highest_quality(url, 'mp4')

window.mainloop()
