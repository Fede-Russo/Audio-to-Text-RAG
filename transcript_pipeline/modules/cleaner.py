import dspy, spacy, os
from transformers import AutoTokenizer
from tqdm import trange, tqdm
import pandas as pd
import numpy as np
from ..utils.text_utils import sentences_divider
from ..dspy_signatures import RiformulaStileNozionistico

tqdm.pandas()

class Cleaner:
    def __init__(self, config):

        self.reformulate_cleaner = dspy.ChainOfThought(RiformulaStileNozionistico)
        
    def riformula_chunk(self, chunk):
        """
        Helper per progress_apply: esegue la pulizia moderata su un chunk.
        """
        try:
            risultato = self.reformulate_cleaner(testo_colloquiale=chunk)
            return risultato.testo_nozionistico.strip()
        except Exception as e:
            print(f"Errore pulizia chunk: {e}")
            return chunk
    
    def clean_transcript(self, input_from_raw, output_file_riformulato_csv, **kwargs):
        """
        Esegue un processo di riformulazione stilistica
        lavorando a livello di CHUNK per necessità computazionali.
        """
        
        try:
            df_input = pd.read_csv(input_from_raw)
        except Exception as e:
            print(f"Errore lettura CSV {input_from_raw}: {e}")
            return
        
        if "text" not in df_input.columns:
            print("Errore: Il CSV deve contenere una colonna 'text'.")
            return
        
        df_riformulato = df_input

        df_riformulato["text"] = df_riformulato["text"].progress_apply(self.riformula_chunk)
        
        df_riformulato["text"] = df_riformulato["text"].str.replace("\n", " ", regex=False)
        df_riformulato = df_riformulato[df_riformulato["text"].str.strip() != ""]
        
        df_riformulato.to_csv(output_file_riformulato_csv, index=False, encoding='utf-8')