import os
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re

# --- Configuração do Tema ---
st.set_page_config(page_title="Adaptador de Provas", layout="wide")

# --- Estilização CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        color: #64748B;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FBBF24, #F59E0B);
        color: #1E3A8A;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #F59E0B, #FBBF24);
    }
    .stTextInput > div > input {
        border-radius: 8px;
        font-family: 'Roboto', sans-serif;
        border: 2px solid #1E3A8A;
    }
    .stSelectbox > div > select {
        border-radius: 8px;
        font-family: 'Roboto', sans-serif;
        border: 2px solid #1E3A8A;
    }
    .stFileUploader > div {
        border-radius: 8px;
        border: 2px dashed #1E3A8A;
    }
    .info-box {
        background: linear-gradient(135deg, #F3F4F6, #FFFFFF);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .footer {
        text-align: center;
        color: #64748B;
        font-family: 'Roboto', sans-serif;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Dados e Funções (mantidas iguais) ---
PRIMARY_COLOR = "#1E3A8A"
SECONDARY_COLOR = "#FBBF24"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/0/02/SVG_logo.svg"  # Substitua pelo link real da logo do Colégio Êxodo

TIPOS_DICAS = {
    "TDAH": [
        "Leia com calma. Destaque palavras importantes.",
        "Use setas ou cores para conectar ideias.",
        "Evite distrações: foque uma questão de cada vez.",
        "Grife os conceitos-chave no enunciado.",
        "Relacione a questão com exemplos práticos."
    ],
    "Dislexia": [
        "Leia devagar. Palavras difíceis podem confundir.",
        "Separe frases longas em partes curtas.",
        "Use régua ou dedo para acompanhar.",
        "Leia em voz baixa para entender melhor.",
        "Marque palavras que aparecem muito."
    ],
    "TEA": [
        "Observe a estrutura lógica da questão.",
        "Use imagens mentais para entender conceitos.",
        "Evite interpretações subjetivas: vá direto ao que é pedido.",
        "Releia com atenção cada alternativa.",
        "Destaque padrões e repetições."
    ]
}

def obter_dica(perfil, numero_questao):
    dicas = TIPOS_DICAS.get(perfil, [])
    if 0 < numero
