import os 
import json 
from pathlib import Path 
from datetime import datetime
from config.settings import (
    DATA_DIR,
    UPLOADS_DIR,
    CHUNKS_DIR,
    EMBEDDINGS_DIR,
    OUTPUTS_DIR,
)


# -------------------------------------
# 1. Folder and File Management
# -------------------------------------
def ensure_data_dirs():
    """Ensure all data data folder exist."""
    for d in [DATA_DIR,UPLOADS_DIR, CHUNKS_DIR, EMBEDDINGS_DIR,OUTPUTS_DIR]:
        os.makedirs(d,exist_ok=True)
        
def get_notebook_dir(notebook_id: str):
    """Return path to the notebook-specific data folder."""
    nb_path = DATA_DIR / "notebooks" / notebook_id 
    os.makedirs(nb_path,exist_ok=True)
    os.makedirs(nb_path / "sources",exist_ok=True)
    os.makedirs(nb_path / "embeddings",exist_ok=True)
    os.makedirs(nb_path / "outputs",exist_ok=True)
    return nb_path




