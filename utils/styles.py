import streamlit as st
import os

def load_css():
    """Загружает CSS стили для всех страниц"""
    try:
        # Пытаемся загрузить из assets/style.css
        css_path = os.path.join('assets', 'style.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        # Fallback стили
        st.markdown("""
            <style>
            .stApp { background: #0A0A1A; color: #F0F0F0; }
            h1, h2, h3 { color: #7B68EE !important; }
            .stButton > button { 
                background: #7B68EE !important; 
                color: white !important;
                border-radius: 10px !important;
                padding: 0.8rem 2rem !important;
            }
            </style>
        """, unsafe_allow_html=True)