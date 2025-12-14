from ..utils.file_utils import make_output_filename, load_text
from ..utils.text_utils import clean_transcript_stage1, group_short_sentences
from ..modules.chunkers import TokenAwareSemanticChunker, chunk_text_by_tokens
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import config
import spacy

def run(raw_transcription_csv):

    text = load_text(raw_transcription_csv)

    nlp = spacy.load(config.SPACY_MODEL) 
    embed_model = SentenceTransformer(config.EMBEDDING_MODEL)
    simple_chunker = TokenAwareSemanticChunker(
    embedder_model=embed_model, 
    min_chunk_tokens=config.MIN_CHUNK_SIZE, 
    max_chunk_tokens=config.MAX_CHUNK_SIZE
    )

    doc = nlp(text)
    sentences = group_short_sentences(doc)

    original_chunks = simple_chunker.split(sentences)
    data_pre_regex = {
    'chunk_id': range(1, len(original_chunks) + 1),  
    'text': original_chunks                       
    }
    output_filename_original = make_output_filename(
        raw_transcription_csv, 
        step=3, 
        tag="chunked_original_pre_regex",
        ext="csv"
    )
    df_chunks_original = pd.DataFrame(data_pre_regex)
    df_chunks_original.to_csv(output_filename_original, index=False, encoding='utf-8-sig')
    processed_chunks = [clean_transcript_stage1(chunk) for chunk in original_chunks]
    data_post_regex = {
        'chunk_id': range(1, len(processed_chunks) + 1),
        'text': processed_chunks
    }
    df_chunks = pd.DataFrame(data_post_regex)
    output_filename = make_output_filename(raw_transcription_csv, step = 3, tag = "chunked", ext = "csv")
    df_chunks.to_csv(output_filename, index=False, encoding='utf-8-sig')

    return output_filename