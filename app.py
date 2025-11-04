import streamlit as st 
import os 
from pathlib import Path 
from config.settings import configure_gemini, GEMINI_MODEL_TEXT, GEMINI_MODEL_PRO
from core import utils 

# Lazy imports of modules that we will implement in core/
# These are called inside UI handlers to avoid import-time errors if not yet implemented.
# Example: from core.ingestion import ingest_source

#Page configuration 
st.set_page_config(page_title="NeuroDesk",page_icon="🧠",layout="wide")

utils.ensure_data_dirs()

#Header 
st.markdown("<h1 style='text-align:center'>🧠 NeuroDesk - AI Research Assistant</h1>",unsafe_allow_html=True)
st.markdown("NeuroDesk reads your documents, websites, and videos and lets you chat,summarize, and generate audio/video overviews - all using Python + Gemini.")

#SideBar: Global controls and quick Gemini test 
with st.sidebar:
    st.header("Quick Controls")
    notebook_name = st.text_input("Notebook name",value="default_notebook")
    st.markdown("---")
    st.write("Gemini configuration")
    if st.button("Configure Gemini"):
        try:
            configure_gemini()
            st.success("Gemini configured. Ready to use.")
        except Exception as e:
            st.error(f"Gemini configure failed: {e}")
    st.caption("Use the button above after setting GEMINI_API_KEY in your environment.")
    st.markdown("---")
    st.write("App Links")
    st.write("- Home: Upload files & links")
    st.write("- Sources: View uploaded content")
    st.write("- Chat: Ask questions")
    st.write("- Audio/Video: Generate overviews")
    st.write("- Insights: Auto notes & knowledge graph")
    if st.button("Open data folder"):
        data_path = Path("data").absolute()
        st.write(f"Data folder: {data_path}")

# Main Navigation 
PAGES = ["Home","Sources","Chat","Audio/Video","Insights","Knowledge Graph", "Settings"]
page = st.radio("Navigate",PAGES,index=0, horizontal=True)

# ----------------------------
# Home Page: Uploads & Links
# ----------------------------

if page == "Home":
    st.header("Upload / Import Sources")
    st.info("Upload files (PDF/DOCX/TXT), paste article URLs, or add Youtube links. Then click Ingest to process them into the notebook")
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=['pdf','docx','txt','md','csv'])
    url_input = st.text_input("Or paste a website article URL to import")
    youtub_input = st.text_input("Or paste a YouTube video URL to import transcript")
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Ingestion uploaded files"):
            if not uploaded_files:
                st.warning("Please upload at least one file")
            else:
                from core.ingestion import ingest_file 
                with st.spinner("Ingesting files....."):
                    results = []
                    for f in uploaded_files:
                        save_path = Path("data/uploads") /f.name 
                        with open(save_path,"wb") as wf:
                            wf.write(f.read())
                        res = ingest_file(str(save_path),notebook_id = notebook_name)
                        results.append(res)
                    st.success("Uploaded files queued/ingested.")
                    st.json(results)                    
    with col2:
        if st.button("Ingest URL"):
            if not url_input.strip():
                st.warning("Paste a website URL first")
            else:
                from core.ingestion import ingest_url 
                with st.spinner("Fetching and ingestiong URL....."):
                    res = ingest_url(url_input, notebook_id=notebook_name)
                    st.success("URL ingested")
                    st.write(res)
        if st.button("Ingest Youtube"):
            if not youtube_input.strip():
                st.warning("Paste  a Youtube URL first.")
            else:
                from core.ingestion import ingest_youtube
                with st.spinner("Fetching transcript and ingesting...."):
                    res = ingest_youtube(youtube_input, notebook_id=notebook_name)
                    st.success("Youtube ingested.")
                    st.write(res)

# ----------------------------
# Sources Page: Manage uploaded content
# ----------------------------

