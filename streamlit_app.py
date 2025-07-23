import streamlit as st
import re

# Defina o page_config logo na primeira linha após os imports!
st.set_page_config(
    page_title="Minha Conversa com Jesus",
    page_icon="✝️",
    layout="centered"
)

# BLOCO DE AUTENTICAÇÃO BÁSICA
usuarios = {
    "usuario1@email.com": "senha123",
    "usuario2@email.com": "minhasenha",
}

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def login():
    st.markdown(
        """
        <div style='text-align: center; font-size: 2.2em; margin-top: 40px; margin-bottom: 30px; color: #205081; font-weight:700'>
            Minha Conversa com Jesus
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Área de Login")
    
    email = st.text_input("E-mail", key="email_input")
    senha = st.text_input("Senha", type="password", key="senha_input")
    
    if st.button("Entrar"):
        email = email.strip().lower()
        if not email:
            st.error("Por favor, insira um e-mail.")
        elif not is_valid_email(email):
            st.error("Por favor, insira um e-mail válido.")
        elif not senha:
            st.error("Por favor, insira uma senha.")
        elif email not in usuarios:
            st.error("E-mail não encontrado.")
        elif usuarios[email] != senha:
            st.error("Senha incorreta.")
        else:
            st.session_state["usuario_logado"] = email
            st.success("Login realizado com sucesso!")
            st.rerun()

if not st.session_state["usuario_logado"]:
    login()
    st.stop()

# Restante do código...
