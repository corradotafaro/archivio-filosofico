import streamlit as st
import json
import random
import os
import base64
import pypdf
from streamlit_pdf_viewer import pdf_viewer

NOME_FILE_CONTATORE = "contatore_visite.json"

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Archivio Filosofico", page_icon="🏛️", layout="centered")

# --- FUNZIONE PER LEGGERE IL DATABASE ---
def carica_database():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

db = carica_database()
# --- FUNZIONE OPTIMIZZATA PER LA RESA VISIVA E I COMANDI ---
def mostra_visualizzatore_pdf(percorso_pdf):
    try:
        with open(percorso_pdf, "rb") as f:
            pdf_data = f.read()
        
        # Inseriamo un contenitore CSS per evitare che la barra dello zoom venga tagliata
        st.markdown(
            """
            <style>
            div[data-testid="stCustomComponentV1"] {
                display: flex;
                justify-content: center;
                padding-top: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Rimuovendo 'width', il componente si adatta perfettamente alla pagina
        pdf_viewer(
            input=pdf_data, 
            height=850,
            render_text=True
        )
    except Exception as e:
        st.error(f"Impossibile visualizzare il file PDF: {e}")

# --- FUNZIONE DI APPOGGIO PER IL TITOLO ESTERNO ---
def ottieni_titolo_pulito(nome_file):
    nome_pulito = nome_file.replace(".pdf", "").replace(".odt", "").replace("_", " ")
    if nome_pulito.lower().startswith("zz "):
        nome_pulito = nome_pulito[3:]
    return nome_pulito.capitalize()

# --- CARTELLA APPROFONDIMENTI ---
CARTELLA_APPROFONDIMENTI = "approfondimenti"

# --- MENU LATERALE (SIDEBAR) ---
st.sidebar.title("📚 Menu Archivio")
st.sidebar.write("Naviga tra le funzioni dell'app")
funzione_scelta = st.sidebar.radio("Seleziona un'azione:", ["Cerca nell'Archivio", "Invoca l'Oracolo", "Sfoglia Approfondimenti"])

# --- NOTA PERSONALE E PRESENTAZIONE ---
st.sidebar.divider()
st.sidebar.markdown("### 🏛️ Il Progetto")

st.sidebar.markdown("""
> *In memoria di Giusi Miccichè, compagna di vita e di studi.*
>
> *Il nostro destino ineluttabile ci costringe ad essere in questa terra solo spettatori in transito, arriviamo come ospiti inattesi e ce ne andiamo come ombre, attraversiamo la vita come una scena che non si ripete, consapevoli che ogni incontro, ogni gesto, ogni istante è già sul punto di svanire.*
""")

st.sidebar.markdown("""
La filosofia, quella dei classici Greci, intesa come amore per il sapere, ha avuto da sempre fascino e curiosità per il grande valore umanistico che ha saputo tramandare da più di 2600 anni e che a tutt’oggi è sempre attuale e prodiga di consigli preziosi che possono essere applicati in molti aspetti della vita di oggi.

I grandi pensatori come Socrate, Platone e Aristotele hanno gettato le basi per molte delle idee e dei concetti che ancora oggi formano il cuore del pensiero filosofico. La capacità di pensare in modo più profondo, critico e riflessivo ha portato ad indagare la natura, la conoscenza, l'esistenza, il bene e il male, e molti altri aspetti della realtà come la scienza, la matematica, l’etica e la politica.

**Corrado Tafaro**
""")

# --- NOTA METODOLOGICA AI ---
st.sidebar.divider()
st.sidebar.info(
    "**Nota metodologica:** I testi, le analisi e la struttura concettuale dell'archivio "
    "sono frutto del lavoro originale dell'autore. Gli strumenti di Intelligenza Artificiale "
    "vengono impiegati esclusivamente come supporto nella fase di revisione formale e correzione sintattica."
)

# --- SEZIONE 1: CERCA NELL'ARCHIVIO (Ricerca Full-Text nei PDF) ---
if funzione_scelta == "Cerca nell'Archivio":
    st.title("🔍 Cerca nell'Archivio")
    st.write("Inserisci un autore, una citazione o un concetto per consultare il database e l'interno di tutti i saggi PDF.")
    
    query = st.text_input("Cosa vuoi cercare nell'archivio?")

    if query and query.strip():
        query_pulita = query.strip().lower()
        
        # 1. Ricerca nelle schede del Database JSON
        risultati_db = []
        for chiave, info in db.items():
            info_str = str(info).lower()
            if query_pulita in chiave.lower() or query_pulita in info_str:
                risultati_db.append((chiave, info))
                
        # 2. Ricerca Full-Text nel contenuto reale dei PDF
        risultati_pdf = []
        if os.path.exists(CARTELLA_APPROFONDIMENTI):
            with st.spinner("Scansione in corso dei documenti dell'Archivio..."):
                for f_name in os.listdir(CARTELLA_APPROFONDIMENTI):
                    if f_name.endswith('.pdf'):
                        percorso_completo = os.path.join(CARTELLA_APPROFONDIMENTI, f_name)
                        try:
                            reader = pypdf.PdfReader(percorso_completo)
                            for num_pagina, pagina in enumerate(reader.pages, start=1):
                                testo_pagina = pagina.extract_text() or ""
                                if query_pulita in testo_pagina.lower():
                                    # Estrae uno snippet (contesto attorno alla parola cercata)
                                    idx = testo_pagina.lower().find(query_pulita)
                                    inizio = max(0, idx - 60)
                                    fine = min(len(testo_pagina), idx + 100)
                                    estratto = testo_pagina[inizio:fine].replace("\n", " ")
                                    
                                    risultati_pdf.append({
                                        "file_name": f_name,
                                        "percorso": percorso_completo,
                                        "pagina": num_pagina,
                                        "estratto": estratto
                                    })
                        except Exception:
                            continue

        # --- VISUALIZZAZIONE RISULTATI ---
        
        # Tab 1: Risultati nel Database / Tab 2: Occorrenze nei PDF
        tab_db, tab_pdf = st.tabs([
            f"📌 Schede Database ({len(risultati_db)})", 
            f"📄 Citazioni nei PDF ({len(risultati_pdf)})"
        ])
        
        with tab_db:
            if risultati_db:
                for nome, dettagli in risultati_db:
                    with st.expander(f"📌 {nome}"):
                        if isinstance(dettagli, dict):
                            for k, v in dettagli.items():
                                st.write(f"**{k.capitalize()}**: {v}")
                        else:
                            st.write(dettagli)
            else:
                st.info("Nessuna scheda del database corrisponde direttamente alla ricerca.")

        with tab_pdf:
            if risultati_pdf:
                st.success(f"Trovate {len(risultati_pdf)} occorrenze all'interno dei saggi:")
                for res in risultati_pdf:
                    f_name = res["file_name"]
                    pag = res["pagina"]
                    estratto = res["estratto"]
                    percorso = res["percorso"]
                    
                    with st.expander(f"📖 {ottieni_titolo_pulito(f_name)} — Pagina {pag}"):
                        st.markdown(f"**Estratto dal testo:** *« ...{estratto}... »*")
                        st.divider()
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Leggi PDF", key=f"read_ft_{f_name}_{pag}"):
                                mostra_visualizzatore_pdf(percorso)
                        with col2:
                            with open(percorso, "rb") as f:
                                st.download_button("Scarica PDF", f, file_name=f_name, key=f"dl_ft_{f_name}_{pag}")
            else:
                st.info("Nessuna occorrenza trovata all'interno dei testi PDF.")

        if not risultati_db and not risultati_pdf:
            st.warning("Nessun risultato trovato per la ricerca inserita.")
            
# --- SEZIONE 2: L'ORACOLO ---
elif funzione_scelta == "Invoca l'Oracolo":
    st.title("🔮 L'Oracolo")
    st.write("Estrai un pensiero o un autore casuale dal tuo archivio per ispirarti.")

    if st.button("Invoca l'Oracolo"):
        if db:
            autore_casuale = random.choice(list(db.keys()))
            dettagli_casuali = db[autore_casuale]
            
            st.info(f"L'Oracolo ha selezionato per te: **{autore_casuale}**")
            if isinstance(dettagli_casuali, dict):
                for k, v in dettagli_casuali.items():
                    st.write(f"*{k.capitalize()}*: {v}")
            else:
                st.write(dettagli_casuali)
        else:
            st.error("Il database sembra vuoto.")

# --- SEZIONE 3: SFOGLIA APPROFONDIMENTI ---
elif funzione_scelta == "Sfoglia Approfondimenti":
    st.title("📁 Tutti gli Approfondimenti dell'Archivio")
    st.write("Ecco la lista completa dei file presenti nella tua cartella (sono supportati sia PDF che ODT).")
    
    if os.path.exists(CARTELLA_APPROFONDIMENTI):
        # Legge sia i file PDF che i vecchi ODT
        file_presenti = [f for f in os.listdir(CARTELLA_APPROFONDIMENTI) if f.endswith('.pdf') or f.endswith('.odt')]
        
        if file_presenti:
            for file_saggio in sorted(file_presenti):
                percorso_file = os.path.join(CARTELLA_APPROFONDIMENTI, file_saggio)
                col1, col2, col3 = st.columns([2, 1, 1])
                
                mostra_testo_sfoglia = False
                
                with col1:
                    st.write(f"🔹 {file_saggio}")
                with col2:
                    if st.button("Leggi", key=f"sfoglia_read_{file_saggio}"):
                        mostra_testo_sfoglia = True
                with col3:
                    mime_type = "application/pdf" if file_saggio.endswith('.pdf') else "application/vnd.oasis.opendocument.text"
                    with open(percorso_file, "rb") as f:
                        st.download_button(
                            label="Scarica",
                            data=f,
                            file_name=file_saggio,
                            mime=mime_type,
                            key=f"sfoglia_dl_{file_saggio}"
                        )
                
                if mostra_testo_sfoglia:
                    st.write("")
                    st.info(f"--- Visualizzazione: {file_saggio} ---")
                    st.title(ottieni_titolo_pulito(file_saggio))
                    st.divider()
                    
                    if file_saggio.endswith('.pdf'):
                        mostra_visualizzatore_pdf(percorso_file)
                    else:
                        st.warning("Questo file è in formato .odt. Per visualizzarlo perfettamente senza omissioni, esportalo in formato .pdf da LibreOffice Writer e caricalo su GitHub.")
                        
                    st.info("--- Fine Contenuto ---")
                    st.write("")
        else:
            st.info("Non ci sono file validi nella cartella 'approfondimenti'.")
    else:
        st.error("La cartella 'approfondimenti' non è stata trovata.")
# --- CODICE ESISTENTE DELLA TUA APP ---
# Qui c'è la logica del tuo archivio, le schede, la lettura dei PDF, ecc.
# ...
# ------------------------------------------------------------------
# --- PIÈ DI PAGINA CON CONTATORE DI MEMORIA NATIVO ---
# ------------------------------------------------------------------

# 1. Utilizza la memoria condivisa del server Streamlit (impostata su 0 così la prima visita è 1)
@st.cache_resource
def inizializza_registro_v2():
    return {"visite": 0}

registro = inizializza_registro_v2()

# 2. Incrementa una sola volta per la sessione dell'utente corrente
if "visita_registrata" not in st.session_state:
    st.session_state["visita_registrata"] = True
    registro["visite"] += 1

totale_visite = registro["visite"]

# 3. Mostra il piè di pagina in formato testo pulito
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: #666666; font-size: 0.9em; padding: 10px;">
        Archivio Filosofico — Visite totali: <b>{totale_visite}</b>
    </div>
    """,
    unsafe_allow_html=True
)
