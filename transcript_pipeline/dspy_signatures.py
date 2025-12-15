import dspy

import dspy

#------------------------ PULIZIA MODERATA --------------------------------#

class EstraiContenutoRilevanteMantenendoStile(dspy.Signature):
    """
    Dato un chunk di testo di una trascrizione (già pre-pulito da filler e ripetizioni), 
    esegui una pulizia semantica per rimuovere solo le frasi non rilevanti, 
    mantenendo il testo rimanente il più fedele possibile all'originale.

    CONSTRAINT FONDAMENTALE: NON ALTERARE MAI i dati numerici, le percentuali, 
    i nomi propri (es. "Coca-Cola", "Nike", "Ikea"), o le informazioni fattuali. 
    Preserva integralmente il nucleo informativo del discorso.

    ISTRUZIONE CHIAVE: NON riscrivere, non parafrasare, non correggere la grammatica 
    e non cambiare lo stile delle frasi che decidi di mantenere. 
    L'output deve conservare lo stile colloquiale e la forma del parlato originale.

    Il tuo compito è CANCELLARE (rimuovere) intere frasi o locuzioni che rientrano 
    ESCLUSIVAMENTE nelle seguenti categorie:

    1.  Presentazioni personali, saluti, ringraziamenti e convenevoli 
        (es. "Buongiorno a tutti ragazzi, io sono Michela", "Grazie, grazie", "Prego, prego").
    2.  Riferimenti alla logistica del meeting o alla tecnologia 
        (es. "faccio la mia condivisione di schermo", "potete vedere il mio schermo", 
        "C'è un commento in chat", "il break in mezzo").
    3.  Istruzioni per esercizi, attività di gruppo o gestione delle breakout room 
        (es. "scannerizzate questo QR code", "Dividendovi in gruppi", 
        "L'esercizio consiste nel pensare...").
    4.  Domande retoriche o commenti rivolti al pubblico che non siano 
        contenuto informativo (es. "È tutto chiaro?", "Siete ancora con me?", 
        "Purtroppo non vi posso vedere").
    5.  Frasi di meta-discorso o transizione che non aggiungono informazione 
        (es. "Spiegherò molto brevemente...", "Spero che questa carrellata... sia utile", 
        "Ok, mi partiamo", "parliamo di come i brand vengono progettati").

    ESEMPIO:
    Input: "Sì? Ok, grazie. Allora, buongiorno a tutti ragazzi, io sono Michela. 
            Il mio ruolo, diciamo così, è strategy partner."
    Output: "Il mio ruolo, diciamo così, è strategy partner."
    (NOTA: "Sì? Ok, grazie. Allora, buongiorno a tutti ragazzi, io sono Michela." 
    è stato rimosso perché rientra nella Categoria 1. 
    La frase "Il mio ruolo, diciamo così, è strategy partner." è stata mantenuta 
    IDENTICA, senza modifiche.)
    """
    
    chunk: str = dspy.InputField(
        desc="Chunk di testo pre-pulito (Stadio 1) da cui rimuovere le frasi non rilevanti."
    )
    ragionamento: str = dspy.OutputField(
        desc="Descrivi sinteticamente quali categorie di frasi non rilevanti hai identificato e rimosso, confermando di aver mantenuto lo stile originale delle frasi conservate."
    )
    cleaned_chunk: str = dspy.OutputField(
        desc="Il chunk finale, pulito dalle frasi non necessarie ma fedele allo stile colloquiale originale."
    )


class PulisciChunkConRagionamentoSintetico(dspy.Signature):
    """Dato un chunk di testo, individua le frasi che non sono rilevanti ai fini della lezione.
    NON ALTERARE MAI i dati numerici, le percentuali, i nomi propri o le informazioni fattuali.

    Passo 1: Rimuovi errori derivanti da trascrizione automatica (es. "ehm", "mmm", "si sì" "Sottotitoli a cura di ...").
    Passo 2: Rimuovi presentazioni personali, saluti, ringraziamenti e riferimenti alla logistica del corso, Rimuovi fillers, ripetizioni, convenevoli non rilevanti, Ignora ogni riferimento a informazioni logistiche o esercizi per gli studenti
    """
    chunk: str = dspy.InputField(desc="Chunk di testo originale da pulire.")
    ragionamento: str = dspy.OutputField(desc="Descrivi in modo sintetico i passaggi che eseguirai per pulire il testo, senza mostrare i risultati intermedi.")
    cleaned_chunk: str = dspy.OutputField(desc="Il chunk finale, pulito e corretto, dopo tutti i passaggi.")

#------------------------ PULIZIA AGGRESSIVA --------------------------------#

class PulisciChunkAggressivoConTema(dspy.Signature):
    """
    Analizza il chunk di testo usando il suo tema locale.

    OBIETTIVO: Estrarre SOLO il contenuto formativo, eliminando 
    saluti, ringraziamenti, logistica, e convenevoli.

    REGOLE:
    1. Riscrivi il chunk mantenendo solo le frasi 
       direttamente rilevanti per il 'tema_locale'.
    2. ELIMINA COMPLETAMENTE frasi come "Buongiorno", "Grazie", "Avete domande?",
       "Buona Pasqua", "Ci vediamo dopo".
    3. Correggi errori di trascrizione ("ehm", "mmm") SOLO sul 
       contenuto rilevante che decidi di mantenere.
    4. Restituisci un blocco di testo pulito e coerente. 
       Se l'intero chunk è irrilevante, restituisci una stringa vuota.
    """
    tema_locale: str = dspy.InputField(desc="Il tema principale di questo chunk.")
    chunk_da_pulire: str = dspy.InputField(desc="Il chunk di testo originale.")
    chunk_pulito: str = dspy.OutputField(
        desc="Il chunk di testo pulito, contenente solo informazioni formative."
    )

class EstraiTemiLocaliChunk(dspy.Signature):
    """
    Estrai i 3-5 concetti o temi principali da questo chunk di testo.
    Sii conciso. Elenca i temi separati da virgola.
    """
    chunk: str = dspy.InputField(desc="Chunk di testo da analizzare.")
    temi_locali: str = dspy.OutputField(
        desc="Elenco di temi e concetti chiave separati da virgola."
    )

class SintetizzaTemaGenerale(dspy.Signature):
    """
    Dato un lungo elenco di temi e concetti chiave estratti da una lezione,
    sintetizza un singolo tema generale per l'intera lezione.
    Il tema deve essere conciso (5-10 parole), es. "Programmazione Python: Liste e Dizionari".
    """
    elenco_temi: str = dspy.InputField(
        desc="Elenco cumulativo di temi da tutti i chunk, separati da virgola."
    )
    tema_generale: str = dspy.OutputField(
        desc="Il singolo tema generale e conciso della lezione."
    )
# ---------------- RIFORMULAZIONE TESTO --------------------------------


class RiformulaStileNozionistico(dspy.Signature):
   """
   Sei un redattore tecnico rigoroso. Il tuo compito è convertire una trascrizione orale 
   in appunti formali, limitandoti strettamente alle informazioni fornite.

   REGOLE FONDAMENTALI:
   1. FEDELTÀ ASSOLUTA: Riformula SOLO ciò che viene detto esplicitamente. 
      Se il relatore descrive una formula a parole, NON convertirla in notazione 
      matematica LaTeX o standard se non viene dettata simbolo per simbolo. 
      Usa descrizioni discorsive (es. "sommatoria di...", "valore medio di...").
   2. NO CONOSCENZA ESTERNA: Non aggiungere definizioni, acronimi 
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

# ------------------------ ALTRO/VECCHI PROMPT ------------------------------
class PulisciFraseConContestoMultiTema(dspy.Signature):
    """
    Analizza la 'frase_da_pulire' usando il contesto.
    
    OBIETTIVO: Mantenere SOLO il contenuto formativo rilevante.
    
    REGOLE:
    1. Se la 'frase_da_pulire' è contenuto formativo rilevante per il 'contesto_tematico', 
       correggi errori di trascrizione (es. "ehm", "mmm"), punteggiatura e grammatica.
    2. Se la 'frase_da_pulire' è un saluto (es. "Buongiorno"), ringraziamento (es. "Grazie"), 
       logistica (es. "Vedete lo schermo?"), convenevole (es. "Buona Pasqua"), 
       o qualsiasi frase non direttamente formativa:
       RESTITUISCI ESATTAMENTE UNA STRINGA VUOTA ("").
    3. NON restituire MAI descrizioni delle tue azioni. 
       NON scrivere "rimossa", "stringa vuota" o "(rimossa)".
       Restituisci solo il testo pulito o una stringa vuota.
    """
    contesto_tematico: str = dspy.InputField(
        desc="Contesto tematico. Es: 'Tema Centrale: [tema].'"
    )
    contesto_precedente: str = dspy.InputField(
        desc="Le frasi che precedono quella da pulire."
    )
    frase_da_pulire: str = dspy.InputField(
        desc="La frase specifica su cui concentrare la pulizia."
    )
    contesto_successivo: str = dspy.InputField(
        desc="Le frasi che seguono quella da pulire."
    )
    
    frase_pulita: str = dspy.OutputField(
        desc="La frase pulita e corretta, OPPURE una stringa vuota ("") se la frase è irrilevante."
    )

class PulisciChunkConRagionamento(dspy.Signature):
    """Dato un chunk di testo, esegui una catena di passaggi per pulirlo. Ragiona passo dopo passo e poi fornisci il testo finale.
    NON ALTERARE MAI i dati numerici, le percentuali, i nomi propri o le informazioni fattuali.

    Passo 1: Rimuovi errori derivanti da trascrizione automatica (es. "ehm", "mmm", "si sì" "Sottotitoli a cura di ...").
    Passo 2: Correggi punteggiatura, errori grammaticali, ortografici, fonologici e fonetici del testo risultante dal passo 1.
    Passo 3: Dal testo corretto risultante dal passo 2: Rimuovi presentazioni personali, saluti, ringraziamenti e riferimenti alla logistica del corso, Rimuovi fillers, ripetizioni, convenevoli non rilevanti, Ignora ogni riferimento a informazioni logistiche o esercizi per gli studenti
    """
    chunk: str = dspy.InputField(desc="Chunk di testo originale da pulire.")
    ragionamento: str = dspy.OutputField(desc="Pensa passo dopo passo, mostrando il risultato intermedio di ogni passaggio.")
    cleaned_chunk: str = dspy.OutputField(desc="Il chunk finale, pulito e corretto, dopo tutti i passaggi.")

class RimuoviRumore(dspy.Signature):
    """
    Ti fornisco una parte del testo della trascrizione di una lezione, "chunk".
    Devi correggere la trascrizione nel seguente modo:
        * Rimuovi errori derivanti da trascrizione automatica (es. "ehm", "mmm", "si sì").
    Il campo `cleaned_chunk` deve contenere **solo** il testo finale (senza introduzioni).
    """
    chunk: str = dspy.InputField(desc="Chunk di testo da pulire.")
    cleaned_chunk: str = dspy.OutputField(desc="Chunk ripulito.")

class CorreggiGrammatica(dspy.Signature):
    """
    Ti fornisco una parte del testo della trascrizione di una lezione, "chunk".
    Devi correggere la trascrizione nel seguente modo:
        * Correggi punteggiatura, errori grammaticali, ortografici, fonologici e fonetici.
    Il campo `cleaned_chunk` deve contenere **solo** il testo finale (senza introduzioni).
    """
    chunk: str = dspy.InputField(desc="Chunk di testo da pulire.")
    cleaned_chunk: str = dspy.OutputField(desc="Chunk ripulito.")

class RimuoviPartiInutili(dspy.Signature):
    """
    Ti fornisco una parte del testo della trascrizione di una lezione, "chunk".
    Devi pulire la trascrizione nel seguente modo:
        * Rimuovi presentazioni personali, saluti, ringraziamenti e riferimenti alla logistica del corso.
        * Rimuovi fillers, ripetizioni, convenevoli non rilevanti.
        * Ignora ogni riferimento a informazioni logistiche o esercizi per gli studenti.
    Il campo `cleaned_chunk` deve contenere **solo** il testo finale (senza introduzioni).
    """
    chunk: str = dspy.InputField(desc="Chunk di testo da pulire.")
    cleaned_chunk: str = dspy.OutputField(desc="Chunk ripulito.")

class PipelineDiPulizia(dspy.Module):
    def __init__(self):
        super().__init__()
        self.rimuovi_rumore = dspy.Predict(RimuoviRumore)
        self.correggi_grammatica = dspy.Predict(CorreggiGrammatica)
        self.rimuovi_parti_inutili = dspy.Predict(RimuoviPartiInutili)

    def forward(self, chunk):
        
        testo_step1 = self.rimuovi_rumore(chunk=chunk).cleaned_chunk

        testo_step2 = self.correggi_grammatica(chunk=testo_step1).cleaned_chunk

        testo_step3 = self.rimuovi_parti_inutili(chunk=testo_step2).cleaned_chunk
        
        return dspy.Prediction(cleaned_chunk=testo_step3)

class IntegraSlides(dspy.Signature):
    """
    Sei un assistente che deve arricchire la trascrizione di una lezione con il contenuto delle slide.
    Il tuo compito è inserire, se lo ritieni opportuno, il contenuto delle slide nel punto esatto del testo "chunk" in cui vengono discusse.

    Segui queste regole in modo tassativo:
    1.  **Fedeltà al Testo Originale**: Riproduci il testo del "chunk" parola per parola, senza alterarlo.
    2.  **Traduzione e Formattazione Slide**: Traduci il contenuto delle "slides" in italiano. Se il contenuto è una lista o si presta a esserlo, formattalo usando i punti elenco di Markdown (`-`).
    3.  **Formato di Inserimento Chiaro**: Quando inserisci una slide, usa **sempre** il seguente formato Markdown a blocchi, che garantisce separazione e indentazione:
        > **[SLIDE N]**
        > Contenuto della slide tradotto e formattato...
    4.  **Uso Esclusivo delle Slide Fornite**: Devi inserire SOLAMENTE le slide presenti nel campo "slides". Non inventare, richiamare o ripetere slide viste in precedenza che non sono in questo elenco. Se il campo "slides" è vuoto, NON inserire alcuna slide.
    5.  **Rilevanza**: Inserisci una slide solo se il suo contenuto è chiaramente discusso nel testo. Se una slide non è rilevante, ignorala.
    6.  **Nessun Contenuto Aggiuntivo**: Non aggiungere riassunti, commenti, introduzioni o conclusioni. L'output deve contenere solo il testo originale e i blocchi delle slide inserite.

    Una volta che hai inserito le slide che ritieni opportuno inserire restituisci un array con i numeri delle slide inserite.
    ---
    Esempio:
    
    chunk: "SPEAKER_01 (120.1s - 125.3s): Quindi, per raggiungere i nostri obiettivi, dobbiamo concentrarci su tre aree chiave. La prima è l'acquisizione di nuovi clienti, ovviamente. Poi dobbiamo migliorare la fidelizzazione di quelli che già abbiamo e infine espandere la nostra presenza sul mercato."
    slides: "SLIDE 15: Key Growth Areas\n- New Customer Acquisition\n- Customer Retention Improvement\n- Market Expansion"
    
    cleaned_chunk:
    SPEAKER_01 (120.1s - 125.3s): Quindi, per raggiungere i nostri obiettivi, dobbiamo concentrarci su tre aree chiave. La prima è l'acquisizione di nuovi clienti, ovviamente. Poi dobbiamo migliorare la fidelizzazione di quelli che già abbiamo e infine espandere la nostra presenza sul mercato.
    > **[SLIDE 15]**
    > Aree Chiave di Crescita
    > - Acquisizione di Nuovi Clienti
    > - Miglioramento della Fidelizzazione dei Clienti
    > - Espansione del Mercato

    slide_inserted: [15]
    ---
    """
    chunk: str = dspy.InputField(desc="Testo originale della trascrizione da non modificare.")
    slides: str = dspy.InputField(desc="Contenuto testuale delle slide da tradurre e inserire nel formato corretto.")
    cleaned_chunk: str = dspy.OutputField(desc="Testo della trascrizione arricchito con le slide formattate in blocchi Markdown.")
    slide_inserted: list[int] = dspy.OutputField(desc="Indici delle slide inserite nel chunk")

class IdentificaSpeakerV2(dspy.Signature):
    """
    Analizza il testo fornito, che rappresenta tutto ciò che uno specifico speaker ha detto durante una lezione, e determina la sua identità.

    Segui questa logica in modo tassativo:
    1.  **Cerca un Nome Proprio**: Leggi attentamente il testo per trovare un'auto-presentazione (es. "Mi chiamo Mario Rossi"). Se trovi un nome, estrailo. Se non trovi un nome, lascia il campo 'nome_identificato' vuoto.
    2.  **Deduci il Ruolo**: Se NON hai trovato un nome, classifica lo speaker. Per il campo 'ruolo_dedotto', DEVI scegliere ESCLUSIVAMENTE tra le seguenti due opzioni: 'Insegnante' o 'Studente'.
        * Assegna 'Insegnante' se lo speaker spiega concetti, guida la lezione e ha turni di parola lunghi.
        * Assegna 'Studente' in tutti gli altri casi
    3.  **Fornisci la Motivazione**: Spiega brevemente perché hai fatto la tua scelta.
    ---
    
    Esempio 1:
    testo_completo_speaker: "Buongiorno, mi chiamo Luca Berboni e oggi parleremo di growth hacking, che è una disciplina affascinante..."
    
    nome_identificato: "Luca Berboni"
    ruolo_dedotto: "Insegnante"
    motivazione: "Lo speaker si presenta all'inizio come 'Luca Berboni' e introduce l'argomento della lezione, agendo chiaramente come insegnante."
    ---

    Esempio 2:
    testo_completo_speaker: "Grazie per la spiegazione. Quindi, se ho capito bene, il funnel dei pirati serve a mappare il viaggio dell'utente?"

    nome_identificato: ""
    ruolo_dedotto: "Studente"
    motivazione: "Lo speaker non si presenta e sta facendo una domanda di chiarimento su un concetto appena spiegato, un comportamento tipico di uno studente."
    ---
    """
    testo_completo_speaker: str = dspy.InputField(desc="Tutto il testo pronunciato da un singolo speaker.")
    
    nome_identificato: str = dspy.OutputField(desc="Il nome proprio dello speaker, se trovato. Altrimenti, deve essere una stringa vuota.")
    ruolo_dedotto: str = dspy.OutputField(desc="Scegli ESATTAMENTE tra 'Insegnante' o 'Studente'. Non usare altri termini.")
    motivazione: str = dspy.OutputField(desc="La breve motivazione della tua scelta.")


class ArricchisciTrascrizione(dspy.Signature):
    """
    Sei un editor professionista. Il tuo compito è arricchire un testo di trascrizione,
    integrando informazioni e concetti chiave tratti dal contenuto delle slide associate.
    L'output deve essere un testo in formato Markdown che mantiene il testo originale intatto,
    aggiunge frasi esplicative e mette in grassetto i concetti più importanti
    che si collegano alle slide. Non alterare la trascrizione originale, ma solo arricchiscila.
    """
    transcription_chunk = dspy.InputField(desc="Un chunk di testo della trascrizione.")
    slide_content = dspy.InputField(desc="Il contenuto delle slide associato a questo chunk.")
    enriched_markdown_text = dspy.OutputField(desc="Il testo arricchito in formato Markdown.")