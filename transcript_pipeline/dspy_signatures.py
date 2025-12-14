import dspy

class RiformulaStileNozionistico(dspy.Signature):
    """
    Sei un redattore tecnico rigoroso. Il tuo compito è convertire una trascrizione orale 
    in appunti formali, limitandoti strettamente alle informazioni fornite.

    REGOLE FONDAMENTALI:
    1. FEDELTÀ ASSOLUTA: Riformula SOLO ciò che viene detto esplicitamente. 
       Se il relatore descrive una formula a parole, NON convertirla in notazione 
       matematica LaTeX o standard se non viene dettata simbolo per simbolo. 
       Usa descrizioni discorsive (es. "sommatoria di...", "valore medio di...").
    2. NO CONOSCENZA ESTERNA: Non aggiungere definizioni, acronimi (come "RL" per Reinforcement Learning) 
       o contestualizzazioni storiche che non sono presenti nel testo, anche se sai che sono corrette.
    3. GESTIONE DEL VISIVO: Se il testo fa riferimento a elementi visivi (es. "questo grafico qui"), 
       generalizza il riferimento (es. "nel diagramma citato") senza inventare descrizioni visive.
    4. STILE: Riscrivi in terza persona, stile impersonale e oggettivo. 
       Rimuovi meta-commenti, esitazioni e parti colloquiali.
    5. STRUTTURA: Organizza i concetti in paragrafi logici.
    """
    testo_colloquiale: str = dspy.InputField(
        desc="Il chunk di testo originale trascritto da un discorso."
    )
    testo_nozionistico: str = dspy.OutputField(
        desc="Il testo riscritto, formale ma strettamente fedele al contenuto informativo originale."
    )