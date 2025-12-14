# --- Impostazioni Generali ---
HF_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
COOKIES_FILE = "cookies-vimeo-com.txt"
YDL_OPT = {
    'format': 'bestvideo+bestaudio/best',

    'merge_output_format': 'mp4',
    
    'outtmpl': '%(title)s.%(ext)s',
    
    'cookiefile': COOKIES_FILE,
    'noplaylist': True
}

# --- Impostazioni Modelli ---
TOKENIZER_MODEL = "google/gemma-3-12b-it"

# Modello alternativo per la pulizia
CLEANER_MODEL_OLLAMA = "ollama_chat/gemma3:12b-it-qat"
VLLM_API_KEY = "fake-key"
OLLAMA_API_BASE = "http://localhost:11434"

# Modelli per la trascrizione e diarizzazione
TRANSCRIBER_MODEL = "openai/whisper-large-v3"
FORCED_LANGUAGE = "it"
DIARIZATION_MODEL = "pyannote/speaker-diarization"

# Modello Spacy
SPACY_MODEL = "it_core_news_lg"

# Modello Embedding
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"

# Parametri Semantic Chunking
MIN_CHUNK_SIZE = 1024
MAX_CHUNK_SIZE = 2048

MAX_TOKENS_CLEANER = 7000
TEMPERATURE_CLEANER = 0.0