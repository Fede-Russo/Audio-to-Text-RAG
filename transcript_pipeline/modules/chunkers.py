import numpy as np
import spacy
from typing import List
from sentence_transformers import SentenceTransformer
import tiktoken
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_distances
import config

class TokenAwareSemanticChunker:
    def __init__(
        self, 
        embedder_model, 
        min_chunk_tokens: int = 150, 
        max_chunk_tokens: int = 512
    ):
        self.embedder = embedder_model
        self.tokenizer = embedder_model.tokenizer
        self.min_tokens = min_chunk_tokens
        self.max_tokens = max_chunk_tokens

    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _create_contextual_sentences(self, sentences: List[str]) -> List[str]:
        n = len(sentences)
        contextualized = []
        for i in range(n):
            prev_s = sentences[i-1] if i > 0 else ""
            curr_s = sentences[i]
            next_s = sentences[i+1] if i < n - 1 else ""
            combined = f"passage: {prev_s} {curr_s} {next_s}".strip()
            contextualized.append(combined)
        return contextualized

    def split(self, sentences: List[str]) -> List[str]:
        n = len(sentences)
        if n == 0: return []

        token_counts = np.array([self._count_tokens(s) for s in sentences])
        P = np.cumsum(token_counts)
        
        def get_chunk_len(start_idx, end_idx):
            upper = P[end_idx]
            lower = P[start_idx - 1] if start_idx > 0 else 0
            return upper - lower


        context_sentences = self._create_contextual_sentences(sentences)
        embeddings = self.embedder.encode(context_sentences, normalize_embeddings=True)
        gaps = np.diag(cosine_distances(embeddings[:-1], embeddings[1:]))
        

        dp = np.full(n, -1.0)
        parent = np.full(n, -1, dtype=int)

        for i in range(n):
            len_0_to_i = get_chunk_len(0, i)
            

            is_valid_start = (self.min_tokens <= len_0_to_i <= self.max_tokens)
            is_forced_start = (i == 0 and len_0_to_i > self.max_tokens)
            
            if is_valid_start or is_forced_start:
                dp[i] = 0
                parent[i] = -1

            for j in range(i - 1, -2, -1):
                if j == -1: break

                current_len = get_chunk_len(j + 1, i)
                
                if current_len > self.max_tokens:

                    if (j + 1) == i:
                        pass 
                    else:

                        break
                
                if current_len < self.min_tokens and current_len <= self.max_tokens:
                    continue

                if dp[j] != -1.0:
                    score = dp[j] + gaps[j]
                    if current_len > self.max_tokens:
                        score -= 0.1
                    
                    if score > dp[i]:
                        dp[i] = score
                        parent[i] = j

        chunks = []
        curr_idx = n - 1
        
        if dp[curr_idx] == -1.0:
            print("Warning: DP failed optimization. Returning full text.")
            return [" ".join(sentences)]

        while curr_idx != -1:
            prev_idx = parent[curr_idx]
            chunk_sents = sentences[prev_idx+1 : curr_idx+1]
            chunks.append(" ".join(chunk_sents))
            curr_idx = prev_idx
            
        return chunks[::-1]

def chunk_text_by_tokens(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    model_name: str = "gpt-3.5"
) -> list[str]:
    """
    Divide un testo in chunk basandosi sul numero di token, con sovrapposizione.

    Utilizza il RecursiveCharacterTextSplitter di LangChain per creare chunk
    semanticamente coerenti, misurandone la dimensione in token anziché
    in caratteri.

    Parameters
    ----------
    text : str
        Il testo di input da dividere.
    chunk_size : int, optional
        Il numero massimo di token desiderato per ogni chunk.
        Il default è 512.
    chunk_overlap : int, optional
        Il numero di token da sovrapporre tra chunk consecutivi
        per mantenere il contesto. Il default è 50.
    model_name : str, optional
        Il nome del modello di riferimento per il tokenizer (via tiktoken).
        Il default è "gpt-4".

    Returns
    -------
    list[str]
        Una lista di stringhe, dove ogni stringa è un chunk di testo.

    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        print(f"Attenzione: Modello '{model_name}' non trovato. Uso 'cl100k_base'.")
        encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(text_to_count: str) -> int:
        return len(encoding.encode(text_to_count))

    # 2. Creiamo lo splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=count_tokens,
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_text(text)