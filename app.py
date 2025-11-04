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

