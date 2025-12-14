import tiktoken
import re
import spacy

def count_tokens_with_tiktoken(file_path, model_name="gpt-3.5-turbo"):
    """Calcola il numero di token in un file usando tiktoken di OpenAI.

    Parameters
    ----------
    file_path : str
        Il percorso del file di testo da analizzare.
    model_name : str, optional
        Il nome del modello di riferimento per la codifica. 
        'gpt-3.5-turbo' e 'gpt-4' usano la stessa codifica ('cl100k_base').
        Il default è 'gpt-3.5-turbo'.

    Returns
    -------
    int
        Il numero totale di token nel file.
    """
    try:

        encoding = tiktoken.encoding_for_model(model_name)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            

        tokens = encoding.encode(text)
        
        return len(tokens)  
    except FileNotFoundError:
        print(f"Errore: Il file '{file_path}' non è stato trovato.")
        raise
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        raise

def clean_transcript_stage1(text: str) -> str:
    """
    Applica una pulizia rapida (Stadio 1) a una trascrizione grezza.

    Questa funzione utilizza una serie di espressioni regolari per
    rimuovere i filler (intercalari) italiani più comuni e le
    ripetizioni, per poi ripulire gli artefatti di spaziatura
    e punteggiatura risultanti.

    Parameters
    ----------
    text : str
        La stringa di testo grezzo della trascrizione.

    Returns
    -------
    str
        Il testo pre-pulito.
    """

    # 1. RIMOZIONE FILLER (Intercalari)
    # Lista ordinata dal più lungo al più corto per evitare match parziali
    # (es. "diciamo così" deve essere trovato prima di "diciamo").
    # \b = word boundary (confine di parola)
    # \bun po'\b = \b non funziona con l'apostrofo, quindi lo gestiamo manualmente
    fillers = [
        r'\bdiciamo così\b', r'\binsomma ecco\b', r'\bquindi ecco\b',
        r'\bsì vabbè ok\b', r'\bche ne so\b', r'\bcome dire\b',
        r'\bper dire\b', r'\bnel senso che\b', r'\bdiciamo che\b',
        r'\bvabbè\b', r'\binsomma\b', r'\bdiciamo\b', r'\bappunto\b',
        r'\ballora\b', r'\becco\b', r'\bcioè\b', r'\behm\b', r'\buhm\b',
        r'\bbeh\b', r'\bah\b', r'\beh\b', r'\bok\b', r"\bun po'\b"
    ]
    
    pattern_fillers = re.compile(r'|'.join(fillers), re.IGNORECASE)
    cleaned_text = pattern_fillers.sub('', text)

    # 2. RIMOZIONE REDUPLICAZIONI SEMPLICI
    # Rimuove parole identiche ripetute, anche con punteggiatura in mezzo.
    # Esempi: "Sì, sì" [cite: 22], "Prego, prego"[cite: 23], 
    # "molte, molte di più" [cite: 29]
    # \b(\w+): Gruppo 1, cattura una parola intera
    # (\s*[.,]?\s+): Gruppo 2, cattura spazi e punteggiatura opzionale
    # \1\b: Richiama il Gruppo 1 (la stessa parola)
    # Sostituiamo con \1 (la parola, una volta sola)
    pattern_reduplication = re.compile(r'\b(\w+)(\s*[.,]?\s+)\1\b', re.IGNORECASE)
    cleaned_text = pattern_reduplication.sub(r'\1', cleaned_text)

    # 3. PULIZIA ARTEFATTI (Spazi e Punteggiatura)
    
    # Normalizza tutti gli spazi (inclusi tab, newline) a un singolo spazio
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Rimuove spazi prima della punteggiatura (es. "ciao .")
    cleaned_text = re.sub(r'\s+([.,?!:;])', r'\1', cleaned_text)
    
    # Rimuove punteggiatura multipla (es. ",," -> "," o "., " -> ".")
    cleaned_text = re.sub(r'([.,?!:;]){2,}', r'\1', cleaned_text)
    
    # Rimuove la punteggiatura orfana all'inizio della stringa
    # (es. se "Allora, ciao" diventa ", ciao")
    cleaned_text = re.sub(r'^\s*[,.]\s*', '', cleaned_text)
    
    # 4. RICAPITALIZZAZIONE
    # Corregge la capitalizzazione all'inizio della stringa o dopo un punto
    # se la pulizia l'ha rotta.
    
    # Capitalizza l'inizio della stringa se è minuscolo
    if cleaned_text:
        cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]

    # Capitalizza le lettere dopo un punto/!/? seguito da spazio
    # (es. "fatto. ciao" -> "fatto. Ciao")
    cleaned_text = re.sub(r'([.!?]\s+)([a-z])', 
                          lambda m: m.group(1) + m.group(2).upper(), 
                          cleaned_text)

    return cleaned_text

def sentences_divider(text):
    """
    Divide il testo in frasi usando regex (non Spacy).
    Questo metodo è "non aggressivo" e si basa sul trovare 
    punteggiatura di fine frase seguita da uno spazio o newline.

    Parameters
    ----------
    text : str
        Il testo grezzo da dividere.

    Returns
    -------
    list[str]
        Una lista di frasi.
    """
    # Questo regex divide il testo usando un capture group ([.!?])
    # per mantenere la punteggiatura. Cerca la punteggiatura
    # seguita da uno spazio o da una fine di riga.
    parts = re.split(r'([.!?])\s+', text)
    
    sentences = []
    # Se il regex splitta correttamente, avremo ['frase1', '.', 'frase2', '!', ...]
    # Dobbiamo ri-unire la frase e la sua punteggiatura.
    if len(parts) > 1:
        for i in range(0, len(parts) - 1, 2):
            sentence = (parts[i] + parts[i+1]).strip()
            if sentence:
                sentences.append(sentence)
        
        # Aggiunge l'eventuale ultima parte se non termina con punteggiatura
        last_part = parts[-1].strip()
        if last_part:
            sentences.append(last_part)
    elif text:
        # Se non c'è stata divisione, restituisce il testo originale
        sentences.append(text.strip())
        
    return sentences

def group_short_sentences(doc: spacy.tokens.Doc, min_words: int = 10) -> list[str]:
    """
    Raggruppa le frasi brevi identificate da spaCy per formare 
    unità di senso compiuto più lunghe.

    Parameters
    ----------
    doc : spacy.tokens.Doc
        Il documento spaCy processato.
    min_words : int, optional
        La lunghezza minima approssimativa (in parole) per un gruppo 
        di frasi. Il default è 10.

    Returns
    -------
    list[str]
        Una lista di stringhe, dove ogni stringa è una frase o un 
        gruppo di frasi.
    """
    grouped_sentences = []
    current_group = []
    
    for sent in doc.sents:
        sentence_text = sent.text.strip()
        if not sentence_text:
            continue
            
        current_group.append(sentence_text)
        
        # Calcola la lunghezza approssimativa del gruppo corrente
        current_length = len(" ".join(current_group).split())
        
        # Se il gruppo ha raggiunto la lunghezza minima, lo salviamo
        if current_length >= min_words:
            grouped_sentences.append(" ".join(current_group))
            current_group = []
            
    # Non dimenticare di aggiungere l'ultimo gruppo se non è vuoto
    if current_group:
        grouped_sentences.append(" ".join(current_group))
        
    return grouped_sentences