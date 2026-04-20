import os
os.environ["PATH"] += os.pathsep + r"C://ffmpeg/bin"
import whisper
import re
import yt_dlp
from pathlib import Path

def get_output_mode() -> str:
    print("\nFolder structure:")
    print("1 - Create subfolder for output")
    print("2 - Use main folder")
    choice = input("Choose 1 or 2: ").strip()
    return choice

def get_base_folder():
    base_folder = Path.home() / "Desktop" / "youTube_downloads"
    base_folder.mkdir(parents=True, exist_ok=True)
    return base_folder


def get_project_name():
    project_name = input("Choose a project name: ")
    return project_name

# creates a subfolder or uses main folder according to user choice
def get_project_folder(base_folder, project_name, choice):
    if choice == "1":
        # project_name = get_project_name()
        project_folder = base_folder / project_name
        project_folder.mkdir(parents=True, exist_ok=True)
    else:
        project_folder = base_folder
    return project_folder



def download_audio(url, project_folder, base_name="download"):

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(project_folder / f"{base_name}.%(ext)s"),
        'ffmpeg_location': r'C:\ffmpeg\bin',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# get audio file for transcription based on latest audio wav download in folder
def get_latest_audio(folder):
    wav_files = list(folder.glob("*.wav"))

    if not wav_files:
        raise FileNotFoundError("No .wav audio files found")

    latest_file = max(wav_files, key=lambda x: x.stat().st_mtime)
    return latest_file

# transcribe
def transcribe_audio(file_path):
    model=whisper.load_model("base")
    result = model.transcribe(str(file_path))
    return result["text"]

def split_transcription(text):
    sentences = re.split(r'(?<=[.?!])', text)
    return sentences

def save_transcription_file(text, audio_file_path, base_name="download"):
    folder = Path(audio_file_path)

    sentences = split_transcription(text)

    output_file = folder / f"{base_name}_transcription.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        for sentence in sentences:
            f.write(f"{sentence}\n")

    return output_file

if __name__ == "__main__":
    # video to audio conversion and download
    video_url = input("Paste a YouTube video url: ")

    choice = get_output_mode()
    project_name = get_project_name()
    project_folder = get_project_folder(get_base_folder(), project_name, choice)

    print("\nDownloading audio...")
    download_audio(video_url, project_folder, project_name)

    wav_file = project_folder / f"{project_name}.wav"

    # audio transcription to txt file
    # folder = get_audio_folder()
    # audio_file = get_latest_audio(project_folder)

    print("Transcribing audio: ", wav_file)
    text = transcribe_audio(wav_file)
    output_path = save_transcription_file(text, project_folder, project_name)
    print("Saved transcription to: ", output_path)

