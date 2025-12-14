import yt_dlp
import os
from unidecode import unidecode
import shutil
import re

class VimeoDownloader:
    def __init__(self, config):
        self.cookies_path = config.COOKIES_FILE    
        if config.YDL_OPT is None:
            self.ydl_opt = {
                "outtmpl": "%(title)s.%(ext)s",
                "cookiefile": "cookies.txt"
                }
        else:
            self.ydl_opt = config.YDL_OPT
        self.ydl = yt_dlp.YoutubeDL(self.ydl_opt) 

    def download_video(self, url):
        info_dict = self.ydl.extract_info(url, download=True)
        file_path = self.ydl.prepare_filename(info_dict)
        base_name = os.path.splitext(file_path)[0]
        folder_name_decoded = unidecode(base_name)
        folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name_decoded)
        folder_name = folder_name.strip().rstrip('.')
        if not folder_name:
            folder_name = "downloaded_video"
            
        os.makedirs(folder_name, exist_ok=True)

        new_path = os.path.join(folder_name, os.path.basename(file_path))
        shutil.move(file_path, new_path)

        return new_path