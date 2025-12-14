import re
import os
import re
import pandas as pd
import subprocess


def load_text(input_file, column_name= "text", separator=' '):
    """Carica e unisce il testo da una colonna specifica di un file CSV.

    Questa funzione legge un file CSV, estrae il contenuto di una colonna
    designata e lo concatena in un'unica stringa, utilizzando un separatore
    specificato. Gestisce gli errori comuni come file non trovato o
    colonna mancante.

    Parameters
    ----------
    input_file : str
        Il percorso del file CSV da leggere.
    column_name : str, optional
        Il nome della colonna da cui estrarre il testo. Il default è "text".
    separator : str, optional
        La stringa da utilizzare per unire le righe di testo. Il default è
        uno spazio singolo (' ').

    Returns
    -------
    str
        Una stringa contenente tutto il testo della colonna unito, oppure
        un messaggio di errore se si verifica un problema.

    """
    try:
        df = pd.read_csv(input_file)

        if column_name not in df.columns:
            return f"Error: Column '{input_file}' not found in the CSV file."
            
        merged_text = separator.join(df[column_name].astype(str))
        
        return merged_text
    
    except FileNotFoundError:
        return f"Error: The file '{input_file}' was not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}" 


###########################################################################################
################            Utilities Functions for file naming            ################
###########################################################################################

def make_output_filename(base_file, step=None, tag=None, ext="txt", folder=None):
    """
    Genera un nome di file coerente per la pipeline.

    Args:
        base_file (str): File di input o nome di riferimento (es. video/audio/transcription).
        step (int, opzionale): Numero dello step della pipeline.
        tag (str, opzionale): Etichetta descrittiva per lo step (es. "raw", "punct", "cleaned", "summary").
        ext (str, opzionale): Estensione del file di output (default "txt").
        folder (str, opzionale): Cartella in cui salvare il file. Se None, usa la cartella di base_file.

    Returns:
        str: Path completo del file generato.
    """
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    

    if step == 2:
        base_name = "transcript"
    else:
       
        parts = base_name.split("_")
        if len(parts) > 1:
            base_name = parts[0]
    

    if folder is None:
        folder = os.path.dirname(base_file) or "."


    suffix_parts = []
    if step is not None:
        suffix_parts.append(str(step))
    if tag is not None:
        suffix_parts.append(tag)

    if suffix_parts:
        suffix = "_" + "_".join(suffix_parts)
    else:
        suffix = ""

    new_name = f"{base_name}{suffix}.{ext}"
    
    return os.path.join(folder, new_name)

###########################################################################################
##########            Utilities Functions for cleaning transcriptions            ##########
###########################################################################################

def strip_punctuation(text: str) -> str:
    """
    Rimuove la punteggiatura da un testo, tranne gli apostrofi e la punteggiatura all'interno dei numeri.
    Args:
        text (str): Testo da cui rimuovere la punteggiatura.
    Returns: 
        str: Testo senza punteggiatura.
    """
    cleaned = re.sub(r"(?<!\d)[.,;:!?](?!\d)", "", text)
    cleaned = re.sub(r"[\"()\[\]{}…]", "", cleaned)
    return cleaned

def remove_hallucination_whispers(text: str) -> str:
    """
        Rimuove dalle frasi del transcript alcune frasi che il modello Whisper tende a aggiungere erroneamente.
        Queste frasi sono state prese da: https://github.com/openai/whisper/discussions/928#discussioncomment-5372187

        Args:
            text (str): Testo da cui rimuovere le frasi.

        Returns:
            str: Testo con le frasi rimosse.
    """
    hallucination = [
    "Sottotitoli creati dalla comunità Amara.org",
    "Sottotitoli di Sottotitoli di Amara.org",
    "Sottotitoli e revisione al canale di Amara.org",
    "Sottotitoli e revisione a cura di Amara.org",
    "Sottotitoli e revisione a cura di QTSS",
    "Sottotitoli e revisione a cura di QTSS.",
    "Sottotitoli a cura di QTSS",
    "Sottotitoli creati dalla comunità Amaraorg.",
    "Sottotitoli creati dalla comunità: Amaraorg"
    "Autore dei sottotitoli e revisione a cura di QTSS"
    ]

    for phrase in hallucination:
        text = text.replace(phrase, "")
    return text

def rimuovi_ripetizioni_artifact(testo: str) -> str:
    """
    Usa le espressioni regolari per trovare e rimuovere frasi corte 
    ripetute in loop (es. "iscriviti al canale iscriviti al canale...").
    """
    # Pattern: Cerca una frase da 2 a 6 parole (\b\w+(\s+\w+){1,5}\b)
    # che è seguita da se stessa per 3 o più volte (\s+\1){3,}
    pattern = re.compile(r'(\b\w+(\s+\w+){1,5}\b)(\s+\1){3,}', re.IGNORECASE)

    # Sostituisce l'intera sequenza trovata con una stringa vuota
    testo_pulito = pattern.sub('', testo)

    # Pulisce eventuali spazi doppi rimasti
    return re.sub(r'\s+', ' ', testo_pulito).strip()

def sentences_divider(raw_transcript, nlp):
    all_sentences = {"speaker": [], "sentences": []}

    current_speaker = None
    current_sentences = []

    for speaker, text in zip(raw_transcript["speaker"], raw_transcript["text"]):
        if speaker != current_speaker:
            
            if current_speaker is not None:
                all_sentences["speaker"].append(current_speaker)
                all_sentences["sentences"].append(current_sentences)
            
            current_speaker = speaker
            current_sentences = []
        
        
        doc = nlp(text)
        current_sentences.extend([sent.text.strip() for sent in doc.sents])

    if current_speaker is not None:
        all_sentences["speaker"].append(current_speaker)
        all_sentences["sentences"].append(current_sentences)
    
    return all_sentences

def sentences_selector(raw_transcript, nlp):

    speaker2id = {spk: idx for idx, spk in enumerate(dict.fromkeys(raw_transcript["speaker"]))}

    speaker_sentences = {spk: [] for spk in speaker2id}
    for spk, text in zip(raw_transcript["speaker"], raw_transcript["text"]):
        doc = nlp(text)
        speaker_sentences[spk].extend([sent.text.strip() for sent in doc.sents])

    return speaker2id, speaker_sentences

###########################################################################################
###############            Utilities Functions for chunking text            ###############
###########################################################################################


def count_tokens(text: str, tokenizer) -> int:
    return len(tokenizer.encode(text, truncation=False))


def chunk_sentences(sentences, max_tokens_chunk, tokenizer):
    chunks = []
    cur = []
    cur_tokens = 0
    for s in sentences:
        t = count_tokens(s, tokenizer)
        if t > max_tokens_chunk:
            half = len(s)//2
            s1, s2 = s[:half], s[half:]
            for piece in [s1, s2]:
                pt = count_tokens(piece, tokenizer)
                if cur_tokens + pt > max_tokens_chunk and cur:
                    chunks.append(" ".join(cur))
                    cur = []
                    cur_tokens = 0
                cur.append(piece)
                cur_tokens += pt
        else:
            if cur_tokens + t > max_tokens_chunk:
                chunks.append(" ".join(cur))
                cur = [s]
                cur_tokens = t
            else:
                cur.append(s)
                cur_tokens += t
    if cur:
        chunks.append(" ".join(cur))
    return chunks