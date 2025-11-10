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

elif page == "Sources":
    st.header("Sources in Notebook")
    from core import utils as core_utils 
    sources = core_utils.list_notebook_sources(notebook_name)
    if not sources:
        st.info("No sources found for this notebook. Upload files on the Home page.")
    else:
        for s in sources:
            st.markdown(f"**{s.get('title','untitled')}** - `{s.get('source_type')}`")
            st.write(s.get('summary','No summary available'))
            if st.button(f"Delete {s.get('id')}",key=f"del_{s.get('id')}"):
                core_utils.delete_source(notebook_name,s.get('id'))
                st.experimental_rerun()

# ----------------------------
# Chat Page: RAG conversational interface
# ----------------------------

elif page == "Chat":
    st.header("Chat with your Notebook")
    st.write("Ask questions and get answers grounded in uploaded sources.")
    question = st.text_area("Your question",height=120)
    top_k = st.slider("Context chunks (top_k)", min_value=1, max_value=8,value=4)
    if st.button("Ask"):
        if not question.strip():
            st.warning("Write a question.")
        else:
            from core.chat_rag import answer_question 
            with st.spinner("Retrieving context and asking Gemini..."):
                answer = answer_question(question,notebook_id=notebook_name,top_k=top_k)
            st.subheader("Answer")
            st.write(answer.get("answer","No answer returned"))
            st.subheader("Citations")
            for c in answer.get("citations",[]):
                st.markdown(f"- **{c.get('source_title','unknown')}** - {c.get('meta','')}")
                st.write(c.get("text","")[:600])

# ----------------------------
# Audio/Video Page
# ----------------------------
elif page == "Audio/Video":
    st.header("Audio & Video Overviews")
    st.write("Generate narrated audio or short explainer videos from notebook summaries.")
    gen_type = st.selectbox("Type",["Audio Overview","Video Overview"])
    target_source = st.text_input("Source ID (leave empty to summarize entire notebook)")
    if st.button("Generate"):
        from core.audio_video import generate_audio_overview, generate_video_overview
        with st.spinner("Generating overview..."):
            if gen_type == "Audio Overview":
                out = generate_audio_overview(notebook_id=notebook_name, source_id=target_source or None)
                st.success("Audio generated")
                st.audio(out["file_path"])
            else:
                out = generate_video_overview(notebook_id=notebook_name, source_id=target_source or None)
                st.success("Video generated")
                st.video(out["file_path"])


# ----------------------------
# Insights Page: Auto notes and insight generator
# ----------------------------
elif page == "Insights":
    st.header("Auto Notes & Insights")
    st.write("Generate autonmatic notes, key takeaways, and insight reports for the notebook.")
    if st.button("Generate Insights"):
        from core.insights import generate_insights
        with st.spinner("Generating insights..."):
            report = generate_insights(notebook_id=notebook_name)
            st.subheader("Top Takeaways")
            for r in report.get("takeaways",[]):
                st.write(f" - {r}")
            st.subheader("Longer Report")
            st.write(report.get("report",""))

# ----------------------------
# Knowledge Graph Page
# ----------------------------
elif page == "Knowledge Graph":
    st.header("Knowledge Graph Visualization")
    st.write("Visualize extracted entities and their relationships.")
    if st.button("Build & Show Graph"):
        from core.knowledge_graph import build_and_export_graph
        graph_html_path = build_and_export_graph(notebook_id = notebook_name)
        st.components.v1.html(open(graph_html_path, 'r').read(),height=700)
        
# ----------------------------
# Settings Page
# ----------------------------
elif page == "Settings":
    st.header("Settings")
    st.write("Configurations and keys")
    st.text("GEMINI_MODEL_TEXT: "+ str(GEMINI_MODEL_TEXT))
    st.text("GEMINI_MODEL_PRO:"+ str(GEMINI_MODEL_PRO))
    if st.button("Show Enviorment keys (SANITY)"):
        st.write({k: os.getenv(k) for k in ["GEMINI_API_KEY"]if os.getenv(k)})
