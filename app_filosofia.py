import streamlit as st
import json
import random
import os

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Archivio Filosofico", page_icon="🏛️", layout="centered")

# --- FUNZIONE PER LEGGERE IL DATABASE ---
def carica_database():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

db = carica_database()

# --- FUNZIONE PER LEGGERE I FILE .ODT DI LIBREOFFICE ---
from odf import text, teletype
from odf.opendocument import load

def leggi_testo_odt(percorso_file):
    try:
        doc = load(percorso_file)
        paragrafi = doc.getElementsByType(text.P)
        testo_completo = []
        for p in paragrafi:
            testo_completo.append(teletype.extractText(p))
        return "\n".join(testo_completo)
    except Exception as e:
        return f"Errore nella lettura del file LibreOffice: {e}"
    
# --- CARTELLA APPROFONDIMENTI ---
CARTELLA_APPROFONDIMENTI = "approfondimenti"

# --- MENU LATERALE (SIDEBAR) ---
st.sidebar.title("📚 Menu Archivio")
st.sidebar.write("Naviga tra le funzioni dell'app")
funzione_scelta = st.sidebar.radio("Seleziona un'azione:", ["Cerca nell'Archivio", "Invoca l'Oracolo", "Sfoglia Approfondimenti"])

# --- NOTA PERSONALE E PRESENTAZIONE (AGGIUNTA) ---
st.sidebar.divider()
st.sidebar.markdown("### 🏛️ Il Progetto")

# Dedica in memoria
st.sidebar.markdown("""
> *In memoria di Giusi Miccichè, compagna di vita e di studi.*
>
> *Il nostro destino ineluttabile ci costringe ad essere in questa terra solo spettatori in transito, arriviamo come ospiti inattesi e ce ne andiamo come ombre, attraversiamo la vita come una scena che non si ripete, consapevoli che ogni incontro, ogni gesto, ogni istante è già sul punto di svanire.*
""")

# Presentazione del percorso e della filosofia
st.sidebar.markdown("""
La filosofia, quella dei classici Greci, intesa come amore per il sapere, ha avuto da sempre fascino e curiosità per il grande valore umanistico che ha saputo tramandare da più di 2600 anni e che a tutt’oggi è sempre attuale e prodiga di consigli preziosi che possono essere applicati in molti aspetti della vita di oggi.

I grandi pensatori come Socrate, Platone e Aristotele hanno gettato le basi per molte delle idee e dei concetti che ancora oggi formano il cuore del pensamento filosofico. La capacità di pensare in modo più profondo, critico e riflessivo ha portato ad indagare la natura, la conoscenza, l'esistenza, il bene e il male, e molti altri aspetti della realtà come la scienza, la matematica, l’etica e la politica.

**Corrado Tafaro**
""")

# --- SEZIONE 1: CERCA NELL'ARCHIVIO ---
if funzione_scelta == "Cerca nell'Archivio":
    st.title("🔍 Cerca nell'Archivio")
    st.write("Inserisci un nome o un concetto per consultare il database e i relativi documenti LibreOffice.")
    
    query = st.text_input("Inserisci il nome di un filosofo, un personaggio o un concetto:")

    if query:
        query_colore = query.lower()
        risultati = []
        
        for chiave, info in db.items():
            info_str = str(info).lower()
            if query_colore in chiave.lower() or query_colore in info_str:
                risultati.append((chiave, info))
                
        if risultati:
            st.success(f"Trovati {len(risultati)} risultati:")
            for nome, dettagli in risultati:
                with st.expander(f"📌 {nome}"):
                    # Mostra i dettagli del JSON
                    if isinstance(dettagli, dict):
                        for k, v in dettagli.items():
                            st.write(f"**{k.capitalize()}**: {v}")
                    else:
                        st.write(dettagli)
                    
                    st.divider()
                    
                    # --- RICERCA DI TUTTI I FILE .ODT CORRISPONDENTI ---
                    file_trovati = []
                    
                    if os.path.exists(CARTELLA_APPROFONDIMENTI):
                        tutti_i_file = os.listdir(CARTELLA_APPROFONDIMENTI)
                        
                        # Raccogliamo TUTTI i file che contengono il nome del filosofo
                        for f_name in tutti_i_file:
                            if f_name.endswith('.odt') and nome.lower() in f_name.lower():
                                percorso_completo = os.path.join(CARTELLA_APPROFONDIMENTI, f_name)
                                file_trovati.append((f_name, percorso_completo))
                    
                    # Mostriamo l'elenco di tutti i file trovati con opzione Leggi e Scarica
                    if file_trovati:
                        st.write(f"📄 **Approfondimenti disponibili ({len(file_trovati)}):**")
                        
                        for f_name, percorso_completo in sorted(file_trovati):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"🔹 {f_name}")
                            with col2:
                                if st.button("Leggi", key=f"read_{nome}_{f_name}"):
                                    testo_estratto = leggi_testo_odt(percorso_completo)
                                    st.info(f"--- Inizio Contenuto: {f_name} ---")
                                    st.write(testo_estratto)
                                    st.info("--- Fine Contenuto ---")
                            with col3:
                                with open(percorso_completo, "rb") as f:
                                    st.download_button(
                                        label="Scarica",
                                        data=f,
                                        file_name=f_name,
                                        mime="application/vnd.oasis.opendocument.text",
                                        key=f"dl_{nome}_{f_name}"
                                    )
                    else:
                        st.caption("Nessun file di approfondimento .odt trovato automaticamente per questo autore.")
        else:
            st.warning("Nessun elemento trovato corrispondente alla ricerca.")
            
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
    st.title("📁 Tutti gli Approfondimenti LibreOffice")
    st.write("Ecco la lista completa dei file presenti nella tua cartella.")
    
    if os.path.exists(CARTELLA_APPROFONDIMENTI):
        file_presenti = [f for f in os.listdir(CARTELLA_APPROFONDIMENTI) if f.endswith('.odt')]
        
        if file_presenti:
            for file_odt in sorted(file_presenti):
                percorso_file = os.path.join(CARTELLA_APPROFONDIMENTI, file_odt)
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"🔹 {file_odt}")
                with col2:
                    if st.button("Leggi", key=f"sfoglia_read_{file_odt}"):
                        testo_estratto = leggi_testo_odt(percorso_file)
                        st.info(f"--- Inizio Contenuto: {file_odt} ---")
                        st.write(testo_estratto)
                        st.info("--- Fine Contenuto ---")
                with col3:
                    with open(percorso_file, "rb") as f:
                        st.download_button(
                            label="Scarica",
                            data=f,
                            file_name=file_odt,
                            mime="application/vnd.oasis.opendocument.text",
                            key=f"sfoglia_dl_{file_odt}"
                        )
        else:
            st.info("Non ci sono file .odt nella cartella 'approfondimenti'.")
    else:
        st.error("La cartella 'approfondimenti' non è stata trovata.")