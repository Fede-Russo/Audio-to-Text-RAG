import subprocess
import os

def build_cmd(template):
    if template['start_time'] and template['end_time']:
        cmd = [
            'ffmpeg', '-i', template['video_path'], 
            '-vn', 
            '-ss', str(template['start_time']), 
            '-to', str(template['end_time']),
            '-acodec', 'pcm_s16le', 
            '-ar', '16000', 
            '-ac', '1', 
            template['output_path'], 
            '-y']
    else:
        cmd = [
            'ffmpeg', '-i', template['video_path'], 
            '-vn', 
            '-acodec', 'pcm_s16le', 
            '-ar', '16000', 
            '-ac', '1', 
            template['output_path'], 
            '-y'] 
    return cmd

def extract_audio_from_video(video_path, output_path = "audio_output", output_format = 'wav', start_time = None, end_time = None):

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    if output_format not in ['wav', 'mp3', 'flac', 'aac']:
        raise ValueError("Unsupported output format. Supported formats are: 'wav', 'mp3', 'flac', 'aac'.")
    
    base_name = "extracted_audio"
    output_file = os.path.join(output_path, f"{base_name}.{output_format}")

    template = {
        'video_path': video_path,
        'output_path': output_file,
        'start_time': start_time,
        'end_time': end_time,}

    cmd = build_cmd(template)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Audio extracted to {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return None