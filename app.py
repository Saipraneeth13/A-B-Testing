"""
A/B Experiment Hub — Streamlit Cloud Entry Point Alias
Supports deployment configurations pointing to either app.py or streamlit_app.py
"""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent / "streamlit_app.py"
runpy.run_path(str(target), run_name="__main__")
