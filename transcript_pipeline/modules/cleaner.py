import dspy
from tqdm import trange, tqdm
import pandas as pd
import numpy as np
from ..dspy_signatures import RiformulaStileNozionistico

tqdm.pandas()

class Cleaner:
    def __init__(self, config):

        self.reformulate_cleaner = dspy.Predict(RiformulaStileNozionistico)

    def riformula_chunk(self, chunk):
        """
        Helper per progress_apply: esegue la pulizia moderata su un chunk.
        """
        try:
            risultato = self.reformulate_cleaner(testo_colloquiale=chunk)
            return risultato.testo_nozionistico.strip()
        except Exception as e:
            print(f"Errore pulizia chunk: {e}")
            return chunk # Mantieni l'originale in caso di errore
    def clean_transcript(self, input_from_raw, output_file_riformulato_csv, **kwargs):
        """
        Esegue entrambe le pulizie (moderata e aggressiva) 
        lavorando a livello di CHUNK per velocità.
        """
        
        try:
            df_riformulato = pd.read_csv(input_from_raw)
        
            if "text" not in df_riformulato.columns:
                print("Errore: Il CSV deve contenere una colonna 'text'.")
                return

            # Applica la pulizia riformulata
            df_riformulato["text"] = df_riformulato["text"].progress_apply(self.riformula_chunk)
            
            # Post-processing
            df_riformulato["text"] = df_riformulato["text"].str.replace("\n", " ", regex=False)
            df_riformulato = df_riformulato[df_riformulato["text"].str.strip() != ""] 
            df_riformulato.to_csv(output_file_riformulato_csv, index=False, encoding='utf-8')
            print(f"Pulizia aggressiva salvata in {output_file_riformulato_csv}")
        except Exception as e:
            print(f"Errore lettura CSV {input_from_raw}: {e}")
            return