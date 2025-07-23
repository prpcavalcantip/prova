import streamlit as st

# Dicionário de usuários: email -> senha (adicione seus e-mails e senhas aqui)
usuarios = {
    "usuario1@email.com": "senha123",
    "usuario2@email.com": "minhasenha",
}

# Inicializa a sessão de login (importante!)
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

def login():
    st.set_page_config(
        page_title="Minha Conversa com Jesus",
        page_icon="✝️",
        layout="centered"
    )
    st.markdown(
        """
        <div style='text-align: center; font-size: 2.2em; margin-top: 40px; margin-bottom: 30px; color: #205081; font-weight:700'>
            Minha Conversa com Jesus
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Área de Login")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email in usuarios and usuarios[email] == senha:
            st.session_state["usuario_logado"] = email
            st.success("Login realizado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("E-mail ou senha incorretos.")

# Se não estiver logado, mostra tela de login e para o app
if not st.session_state["usuario_logado"]:
    login()
    st.stop()

# Daqui para baixo, coloque o código do seu app!
st.write(f"Olá, {st.session_state['usuario_logado']}! Você está autenticado.")
st.write("Seu app começa aqui.")
