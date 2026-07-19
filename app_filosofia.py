import streamlit as st
import json
import random
import os
import base64

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Archivio Filosofico", page_icon="🏛️", layout="centered")

# --- FUNZIONE PER LEGGERE IL DATABASE ---
def carica_database():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

db = carica_database()

# --- NUOVA FUNZIONE PER INCORPORARE IL LETTORE PDF ---
def mostra_visualizzatore_pdf(percorso_pdf):
    try:
        with open(percorso_pdf, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Riquadro HTML che incorpora il PDF nativamente nel browser
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
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

I grandi pensatori come Socrate, Platone e Aristotele hanno gettato le basi per molte delle idee e dei concetti che ancora oggi formano il cuore del pensamento filosofico. La capacità di pensare in modo più profondo, critico e riflessivo ha portato ad indagare la natura, la conoscenza, l'esistenza, il bene e il male, e molti altri aspetti della realtà come la scienza, la matematica, l’etica e la politica.

**Corrado Tafaro**
""")

# --- SEZIONE 1: CERCA NELL'ARCHIVIO ---
if funzione_scelta == "Cerca nell'Archivio":
    st.title("🔍 Cerca nell'Archivio")
    st.write("Inserisci un nome o un concetto per consultare il database e i relativi documenti PDF.")
    
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
                    if isinstance(dettagli, dict):
                        for k, v in dettagli.items():
                            st.write(f"**{k.capitalize()}**: {v}")
                    else:
                        st.write(dettagli)
                    
                    st.divider()
                    
                    # Cerca sia i nuovi file .pdf che i vecchi .odt rimasti
                    file_trovati = []
                    if os.path.exists(CARTELLA_APPROFONDIMENTI):
                        tutti_i_file = os.listdir(CARTELLA_APPROFONDIMENTI)
                        for f_name in tutti_i_file:
                            if (f_name.endswith('.pdf') or f_name.endswith('.odt')) and nome.lower() in f_name.lower():
                                percorso_completo = os.path.join(CARTELLA_APPROFONDIMENTI, f_name)
                                file_trovati.append((f_name, percorso_completo))
                    
                    if file_trovati:
                        st.write(f"📄 **Approfondimenti disponibili ({len(file_trovati)}):**")
                        for f_name, percorso_completo in sorted(file_trovati):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            mo_testo = False
                            
                            with col1:
                                st.write(f"🔹 {f_name}")
                            with col2:
                                if st.button("Leggi", key=f"read_{nome}_{f_name}"):
                                    mo_testo = True
                            with col3:
                                mime_type = "application/pdf" if f_name.endswith('.pdf') else "application/vnd.oasis.opendocument.text"
                                with open(percorso_completo, "rb") as f:
                                    st.download_button(
                                        label="Scarica",
                                        data=f,
                                        file_name=f_name,
                                        mime=mime_type,
                                        key=f"dl_{nome}_{f_name}"
                                    )
                            
                            if mo_testo:
                                st.write("")
                                st.info(f"--- Visualizzazione: {f_name} ---")
                                st.title(ottieni_titolo_pulito(f_name))
                                st.divider()
                                
                                if f_name.endswith('.pdf'):
                                    mostra_visualizzatore_pdf(percorso_completo)
                                else:
                                    st.warning("Questo file è ancora in formato .odt. Per visualizzarlo perfettamente senza errori, esportalo in .pdf su LibreOffice e caricalo su GitHub.")
                                
                                st.info("--- Fine Contenuto ---")
                                st.write("")
                    else:
                        st.caption("Nessun file di approfondimento trovato automaticamente per questo autore.")
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
