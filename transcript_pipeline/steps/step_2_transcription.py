from ..modules.transcriber import Transcriber
from ..modules.speaker_detector import SpeakerDetector
from ..utils.file_utils import make_output_filename, remove_hallucination_whispers
from tqdm import tqdm
import csv
import os
import config


def align_transcription_with_diarization(diarization_segments, transcription_chunks):
    """
    Allinea i chunk di trascrizione di Whisper con i segmenti di diarizzazione.

    Assegna uno speaker a ciascun chunk di testo in base alla
    sovrapposizione temporale massima.
    """
    aligned_results = []

    # diarization_segments è una lista di (turn, _, speaker)
    # transcription_chunks è una lista di {"text": "...", "timestamp": (start, end)}

    for chunk in tqdm(transcription_chunks, desc="Allineamento Speaker/Testo"):
        chunk_start, chunk_end = chunk["timestamp"]
        chunk_text = chunk["text"].strip()

        if not chunk_text:
            continue

        overlaps = {}

        for turn, _, speaker in diarization_segments:
            turn_start = turn.start
            turn_end = turn.end

            overlap_start = max(chunk_start, turn_start)
            overlap_end = min(chunk_end, turn_end)
            overlap_duration = overlap_end - overlap_start

            if overlap_duration > 0:
                if speaker not in overlaps:
                    overlaps[speaker] = 0
                overlaps[speaker] += overlap_duration

        if overlaps:
            best_speaker = max(overlaps, key=overlaps.get)
        else:
            best_speaker = "UNKNOWN" 

        aligned_results.append({
            "speaker": best_speaker,
            "start_time": round(chunk_start, 1),
            "end_time": round(chunk_end, 1),
            "text": chunk_text
        })

    return aligned_results


def run(audio_file):
    
    speaker_detector = SpeakerDetector(config)
    transcriber = Transcriber(config)

    print("Fase 1: Avvio diarizzazione (SpeakerDetector)...")
    diarization = speaker_detector.detect_speakers(audio_file)

    diarization_segments = list(diarization.itertracks(yield_label=True))
    print(f"Diarizzazione completata. Trovati {len(diarization_segments)} segmenti di parlato.")


    print("\nFase 2: Avvio trascrizione (Pipeline Transformers)...")
    print("La pipeline elaborerà l'intero file audio (potrebbe richiedere tempo)...")
    
    transcription_result = transcriber.transcribe(audio_file)

    transcription_chunks = transcription_result.get("chunks", [])
    
    if not transcription_chunks:
        print("Errore: La trascrizione non ha restituito 'chunks'.")
        print("Assicurati che 'return_timestamps=True' sia nella pipeline.")
        return None, None
        
    print("Trascrizione completata.")

    print("\nFase 3: Allineamento Trascrizione e Diarizzazione...")
    
    unmerged_results = align_transcription_with_diarization(
        diarization_segments,
        transcription_chunks
    )
    print("Allineamento completato.")

    print("\nFase 4: Elaborazione e salvataggio dei risultati...")

    csv_file_path = make_output_filename(audio_file, 2, tag="raw_aligned", ext="csv")
    with open(csv_file_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["speaker", "start_time", "end_time", "text"])
        writer.writeheader()
        writer.writerows(unmerged_results)
    print(f"Trascrizione allineata (non unita) salvata in: {csv_file_path}")

    return csv_file_path