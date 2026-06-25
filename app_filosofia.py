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

# --- CARTELLA APPROFONDIMENTI ---
CARTELLA_APPROFONDIMENTI = "approfondimenti"

# --- MENU LATERALE (SIDEBAR) ---
st.sidebar.title("📚 Menu Archivio")
st.sidebar.write("Naviga tra le funzioni dell'app")
funzione_scelta = st.sidebar.radio("Seleziona un'azione:", ["Cerca nell'Archivio", "Invoca l'Oracolo", "Sfoglia Approfondimenti"])

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
                    
                    # Mostriamo l'elenco di tutti i file trovati
                    if file_trovati:
                        st.write(f"📄 **Approfondimenti disponibili ({len(file_trovati)}):**")
                        
                        # Ordiniamo i file alfabeticamente per comodità
                        for f_name, percorso_completo in sorted(file_trovati):
                            # Creiamo una riga pulita con il nome del file e il suo rispettivo bottone
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"🔹 {f_name}")
                            with col2:
                                with open(percorso_completo, "rb") as f:
                                    st.download_button(
                                        label="Scarica",
                                        data=f,
                                        file_name=f_name,
                                        mime="application/vnd.oasis.opendocument.text",
                                        key=f"dl_{nome}_{f_name}" # Chiave unica combinata per evitare conflitti
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
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🔹 {file_odt}")
                with col2:
                    with open(percorso_file, "rb") as f:
                        st.download_button(
                            label="Scarica",
                            data=f,
                            file_name=file_odt,
                            mime="application/vnd.oasis.opendocument.text",
                            key=f"sfoglia_{file_odt}"
                        )
        else:
            st.info("Non ci sono file .odt nella cartella 'approfondimenti'.")
    else:
        st.error("La cartella 'approfondimenti' non è stata trovata.")