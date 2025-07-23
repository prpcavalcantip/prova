import streamlit as st
import openai
import os
import re

# Defina o page_config logo na primeira linha após os imports
st.set_page_config(
    page_title="Minha Conversa com Jesus",
    page_icon="✝️",
    layout="centered"
)

# --------------------------
# BLOCO DE AUTENTICAÇÃO BÁSICA
# --------------------------
usuarios = {
    "usuario1@email.com": "senha123",
    "usuario2@email.com": "minhasenha",
    # Adicione mais usuários conforme necessário
}

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

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
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email in usuarios and usuarios[email] == senha:
            st.session_state["usuario_logado"] = email
            st.success("Login realizado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("E-mail ou senha incorretos.")

if not st.session_state["usuario_logado"]:
    login()
    st.stop()
# --------------------------

# Paleta de cores suaves
PRIMARY_BG = "#e9f2fa"
CARD_BG = "#ffffff"
CARD_BORDER = "#b3c6e0"
PRIMARY_COLOR = "#205081"
BUTTON_BG = "#205081"
BUTTON_TEXT = "#fff"
TEXT_COLOR = "#24292f"
SUGGESTION_BG = "#f0f6fb"

# CSS customizado para interface amigável
st.markdown(f"""
    <style>
    body {{
        background-color: {PRIMARY_BG} !important;
    }}
    .main .block-container {{
        background: {PRIMARY_BG} !important;
        color: {TEXT_COLOR};
    }}
    .title-div {{
        background: {CARD_BG};
        border-radius: 18px;
        padding: 18px 10px 12px 10px;
        margin-bottom: 18px;
        border: 1.5px solid {CARD_BORDER};
        box-shadow: 0 2px 8px rgba(32,80,129,0.08);
    }}
    .input-div {{
        text-align: center;
        font-size: 1.25em;
        margin-bottom: 20px;
        color: {PRIMARY_COLOR};
        font-weight: 500;
    }}
    .custom-card {{
        background-color: {CARD_BG};
        border: 1.5px solid {CARD_BORDER};
        border-radius: 16px;
        padding: 24px;
        margin-top: 24px;
        text-align: left;
        max-width: 540px;
        margin-left: auto;
        margin-right: auto;
        font-size: 1.13em;
        line-height: 1.7;
        color: {TEXT_COLOR};
        box-shadow: 0 2px 10px rgba(32,80,129,0.06);
    }}
    .stTextInput > div > div > input {{
        font-size: 1.1em;
    }}
    .stButton button {{
        color: {BUTTON_TEXT};
        background: linear-gradient(90deg,{BUTTON_BG} 70%,#3e82c4 100%);
        border: 0px;
        border-radius: 8px;
        padding: 0.6em 1.5em;
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 10px;
        transition: 0.2s;
    }}
    .stButton button:hover {{
        filter: brightness(1.08);
        border: 1.5px solid {PRIMARY_COLOR};
    }}
    strong {{
        color: {PRIMARY_COLOR};
        font-weight: 700;
    }}
    .suggestion {{
        background: {SUGGESTION_BG};
        border-left: 4px solid {PRIMARY_COLOR};
        border-radius: 7px;
        padding: 7px 15px 7px 14px;
        margin: 6px 0 0 0;
        font-size: 1em;
    }}
    </style>
""", unsafe_allow_html=True)

# Título para usuários autenticados
st.markdown(
    f"""
    <div class='title-div'>
        <h1 style='text-align: center; font-size: 2.5em; margin-bottom: 0; color: {PRIMARY_COLOR};'>
            Minha Conversa com Jesus
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Campo de entrada
st.markdown(
    f"""
    <div class='input-div'>
        Como você está se sentindo hoje?
    </div>
    """,
    unsafe_allow_html=True
)
feeling = st.text_input("", max_chars=120)

def formatar_negrito(texto):
    # Substitui **texto** por <strong>texto</strong>
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)

def formatar_sugestoes(texto):
    # Torna sugestões práticas mais destacadas
    linhas = texto.split('\n')
    novas_linhas = []
    for linha in linhas:
        if linha.strip().startswith('•'):
            novas_linhas.append(f"<div class='suggestion'>{linha.strip()}</div>")
        else:
            novas_linhas.append(linha)
    return "\n".join(novas_linhas)

def gerar_devocional(sentimento):
    prompt = f"""
Você é um assistente espiritual cristão. Quando alguém compartilha como está se sentindo, responda com um devocional mais aprofundado, acolhedor e reflexivo. Siga esta estrutura, escrevendo sempre em português:

1. Palavra de Jesus: Escolha um versículo dito por Jesus nos Evangelhos que se relacione com o sentimento: "{sentimento}". Cite o livro e o versículo.
2. Reflexão: Escreva uma reflexão mais profunda (aprox. 2-3 parágrafos) conectando o versículo ao sentimento relatado, mostrando como as palavras de Jesus podem transformar a situação, trazendo consolo, direção e esperança.
3. Oração: Escreva uma oração personalizada, baseada no sentimento e na Palavra escolhida, convidando Jesus para a situação da pessoa.
4. Sugestões práticas para o dia: Ofereça pelo menos duas sugestões simples, concretas e atuais para a pessoa viver aquela Palavra de Jesus no dia de hoje (por exemplo: separar um tempo de silêncio, enviar uma mensagem para alguém, anotar motivos de gratidão, etc).

Formate a resposta em blocos bem separados e com títulos marcados com **, assim:

**Palavra de Jesus:**  
<versículo>

**Reflexão:**  
<reflexão>

**Oração:**  
<oração>

**Sugestões práticas para o dia:**  
• <sugestão 1>  
• <sugestão 2>

Agora gere o devocional para: "{sentimento}"
"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.7,
    )
    texto = response.choices[0].message.content.strip()
    return texto

def salvar_historico(sentimento, devocional):
    try:
        with open("historico_devocional.txt", "a", encoding="utf-8") as f:
            f.write(f"\n---\nSentimento: {sentimento}\n{devocional}\n")
    except Exception as e:
        st.warning("Não foi possível salvar o histórico.")

if st.button("Gerar Devocional") and feeling:
    with st.spinner('Gerando seu devocional...'):
        devocional = gerar_devocional(feeling)
        devocional_formatado = formatar_negrito(devocional)
        devocional_formatado = formatar_sugestoes(devocional_formatado)
        st.markdown(
            f"""
            <div class='custom-card'>
            {devocional_formatado.replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )
        salvar_historico(feeling, devocional)

st.markdown(
    """
    <div style='text-align: center; font-size: 1em; margin-top: 50px; color: #6c757d;'>
        © 2025 Minha Conversa com Jesus | Feito com Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
