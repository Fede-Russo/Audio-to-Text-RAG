from ..modules.vimeo_downloader import VimeoDownloader
import config

def run(url: str):
    """
    Scarica da Vimeo il video indicato dall url e lo salva come file .mp4.
    Crea la cartella dove verranno salvati tutti i file generati.
    Restituisce il percorso del file video.
    """
    print("-> Inizializzazione VimeoDownloader")
    downloader = VimeoDownloader(config)
    print("-> Donwload del video")
    video_file = downloader.download_video(url)

    return video_file