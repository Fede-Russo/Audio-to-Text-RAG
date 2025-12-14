import os
import argparse
import torch
from pathlib import Path
from transcript_pipeline.utils.text_utils import count_tokens_with_tiktoken
from transcript_pipeline.steps import (
    step_0_download,
    step_1_audio_extraction,
    step_2_transcription,
    step_3_chunking,
    step_4_cleaner
)

class PipelineContext:
    """
    Gestisce lo stato della pipeline. Se un file non è in memoria,
    prova automaticamente a recuperarlo dal disco (Lazy Loading).
    """
    def __init__(self, folder_path: Path):
        self.folder = folder_path

        self._video_file = None
        self._audio_file = None
        self._raw_csv = None
        self._chunked_csv = None

    def _resolve(self, value, glob_pattern: str, desc: str) -> str:
        """Logica centrale: se il valore c'è, usalo. Se no, cercalo su disco."""
        if value:
            return value
        
        found = list(self.folder.glob(glob_pattern))
        if found:
            print(f"   [Context] Recuperato {desc} da disco: {found[0].name}")
            return str(found[0])
        
        raise FileNotFoundError(f"Impossibile trovare {desc} (pattern: {glob_pattern}) in {self.folder}")

    @property
    def video_file(self) -> str:
        return self._resolve(self._video_file, "*.mp4", "Video File")

    @video_file.setter
    def video_file(self, value):
        self._video_file = value

    @property
    def audio_file(self) -> str:
        return self._resolve(self._audio_file, "*.wav", "Audio File")
    
    @audio_file.setter
    def audio_file(self, value):
        self._audio_file = value

    @property
    def raw_csv(self) -> str:
        return self._resolve(self._raw_csv, "*raw_aligned.csv", "Raw CSV")
    
    @raw_csv.setter
    def raw_csv(self, value):
        self._raw_csv = value

    @property
    def chunked_csv(self) -> str:
        return self._resolve(self._chunked_csv, "*_chunked.csv", "Chunked CSV")

    @chunked_csv.setter
    def chunked_csv(self, value):
        self._chunked_csv = value


def main(args):
    if not args.url and not args.folder_name:
        raise ValueError("ERRORE: Serve --folder_name o --url.")

    base_folder = Path('.') / args.folder_name if args.folder_name else Path('.')
    ctx = PipelineContext(base_folder)

    def run_step_0(ctx):
        print("--- Step 0: Download ---")
        if not args.url: raise ValueError("URL mancante per step 0")
        video_path = step_0_download.run(args.url)
        ctx.folder = Path(os.path.dirname(video_path))
        ctx.video_file = video_path

    def run_step_1(ctx):
        print("--- Step 1: Estrazione Audio ---")
        ctx.audio_file = step_1_audio_extraction.run(ctx.video_file)

    def run_step_2(ctx):
        print("--- Step 2: Trascrizione ---")
        csv_path = step_2_transcription.run(ctx.audio_file)
        ctx.raw_csv = csv_path
        count_tokens_with_tiktoken(ctx.raw_csv)
        torch.cuda.empty_cache()

    def run_step_3(ctx):
        print("--- Step 3: Chunking ---")
        ctx.chunked_csv = step_3_chunking.run(ctx.raw_csv)
        torch.cuda.empty_cache()

    def run_step_4(ctx):
        print("--- Step 4: Pulizia ---")
        out_file = step_4_cleaner.run(ctx.chunked_csv)
        torch.cuda.empty_cache()
        print(f"Pipeline Completata. Output: {out_file}")

    pipeline_steps = [
        run_step_0,
        run_step_1,
        run_step_2,
        run_step_3,
        run_step_4
    ]

    steps_to_run = pipeline_steps[args.step:]

    if not steps_to_run:
        print(f"Nessuno step da eseguire (Step richiesto: {args.step}, Max step: {len(pipeline_steps)-1})")
        return

    for step_func in steps_to_run:
        step_func(ctx)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Esegue la pipeline di trascrizione.")
    parser.add_argument("--folder_name", type=str, default=None, help="Cartella dei file di input (necessaria se non si parte con un URL).")
    parser.add_argument("--url", type=str, default=None, help="URL del video da scaricare (solo per step 0).")
    parser.add_argument("--step", type=int, default=0, help="Step da cui iniziare la pipeline.")

    args = parser.parse_args()
    main(args)