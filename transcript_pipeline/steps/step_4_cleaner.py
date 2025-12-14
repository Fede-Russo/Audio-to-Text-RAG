import dspy
from transcript_pipeline.modules.cleaner import Cleaner
from transcript_pipeline.utils.file_utils import make_output_filename
import config

def run(chunked_transcript_file: str):
    """
    Esegue la pulizia semantica della trascrizione usando un LLM.
    Restituisce il percorso del file di trascrizione pulito.
    """
    print("-> Configurazione del client DSPy per Ollama...")
    lm_cleaner = dspy.LM(
        model = config.CLEANER_MODEL_OLLAMA, 
        api_base=config.OLLAMA_API_BASE, 
        api_key=config.VLLM_API_KEY, 
        max_tokens=config.MAX_TOKENS_CLEANER,
        temperature=config.TEMPERATURE_CLEANER
    )
    dspy.configure(lm=lm_cleaner)

    cleaner = Cleaner(config)


    output_file_riformulato_csv = make_output_filename(chunked_transcript_file, 5, "cleaned_riformulato", ext = "csv")
    print(f"Avvio pulizia con LLM su: {chunked_transcript_file}")
    cleaner.clean_transcript(input_from_raw = chunked_transcript_file, output_file_riformulato_csv = output_file_riformulato_csv)
    
    return output_file_riformulato_csv