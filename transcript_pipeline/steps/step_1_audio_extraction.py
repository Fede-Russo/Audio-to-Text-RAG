from ..utils.audio_utils import build_cmd, extract_audio_from_video
import os
import config

def run(video_file: str):
    print("-> Extrazione traccia audio dal video")
    audio_file = extract_audio_from_video(video_file, os.path.dirname(video_file), 'wav')
    return audio_file