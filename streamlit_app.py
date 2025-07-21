import os
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re
from streamlit_oauth import OAuth2Component

GOOGLE_CLIENT_ID = "145586791351-82utkvpiss4gb782a9s2g4717kbscqc4.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "https://b3asmsyoywxin6rhkia3as.streamlit.app"

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
    if 0 < numero_questao <= len(dicas):
        return dicas[numero_questao - 1]
    return "Leia com atenção."

def simplificar_questao(texto, numero, perfil):
    texto = re.sub(r'\s+', ' ', texto).strip()
    match = re.match(r'(QUESTÃO \d+ )(.*?)([A-E]\))', texto)
    if not match:
        return {
            "numero": numero,
            "enunciado": texto,
            "alternativas": [],
            "dica": obter_dica(perfil, numero)
        }
    inicio = match.start(3)
    enunciado = texto[:inicio].strip()
    alternativas = re.findall(r'([A-E]\))\s?(.*?)(?=\s[A-E]\)|$)', texto[inicio:])
    return {
        "numero": numero,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "dica": obter_dica(perfil, numero)
    }

def gerar_docx(questoes, nome_professor, materia):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(14)

    doc.add_heading(f"Prova Adaptada – {materia} – {nome_professor}", 0)
    doc.add_paragraph(f"Professor(a): {nome_professor}", style='Normal')
    doc.add_paragraph(f"Matéria: {materia}", style='Normal')
    doc.add_paragraph("")

    for q in questoes:
        doc.add_paragraph(f"QUESTÃO {q['numero']}", style='Normal')
        doc.add_paragraph(q['enunciado'], style='Normal')
        doc.add_paragraph("")  # Espaço antes das alternativas

        for letra, alt in q['alternativas']:
            doc.add_paragraph(f"{letra} {alt.strip()}", style='Normal')

        doc.add_paragraph(f"🧠 DICA: {q['dica']}", style='Normal')
        doc.add_paragraph("")

    return doc

def login_google():
    st.title("🔐 Login do Professor")
    st.write("Faça login com sua conta Google para continuar:")

    oauth2 = OAuth2Component(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        token_url="https://accounts.google.com/o/oauth2/token",
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"]
    )

    result = oauth2.authorize_button("Entrar com Google")
    if result and "userinfo" in result:
        st.session_state['login_ok'] = True
        st.session_state['nome_professor'] = result['userinfo'].get('name', '')
        st.session_state['email_professor'] = result['userinfo'].get('email', '')
        return True
    st.stop()

def main():
    if 'login_ok' not in st.session_state or not st.session_state['login_ok']:
        login_google()

    nome_professor = st.session_state.get('nome_professor', '')
    email_professor = st.session_state.get('email_professor', '')
    materia = st.session_state.get('materia', '')

    if not nome_professor:
        nome_professor = st.text_input("Digite seu nome completo")
        st.session_state['nome_professor'] = nome_professor

    if not materia:
        materia = st.text_input("Digite a matéria que você ensina")
        st.session_state['materia'] = materia

    if not nome_professor or not materia:
        st.info("Preencha nome e matéria para continuar")
        st.stop()

    st.title("🧠 Adaptador de Provas para Alunos Neurodivergentes")
    st.caption(f"Professor(a): {nome_professor} | Matéria: {materia} | Email: {email_professor}")

    perfil = st.selectbox("Selecione o tipo de adaptação:", list(TIPOS_DICAS.keys()))
    arquivo = st.file_uploader("Envie a prova em PDF", type=["pdf"])

    if arquivo:
        st.success("Arquivo recebido!")
        try:
            pdf = fitz.open(stream=arquivo.read(), filetype="pdf")
        except Exception as e:
            st.error(f"Erro ao abrir PDF: {e}")
            return

        texto_completo = ""
        for pagina in pdf:
            texto_completo += pagina.get_text()

        questoes_raw = re.findall(r'QUESTÃO \d+.*?(?=QUESTÃO \d+|$)', texto_completo, flags=re.DOTALL)
        if not questoes_raw:
            st.error("Nenhuma questão encontrada no PDF.")
            return

        questoes_simplificadas = []
        for i, q_texto in enumerate(questoes_raw[:5], start=1):
            questoes_simplificadas.append(simplificar_questao(q_texto, i, perfil))

        doc = gerar_docx(questoes_simplificadas, nome_professor, materia)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.success("Prova adaptada gerada com sucesso!")
        st.download_button(
            "📥 Baixar Prova Adaptada",
            data=buffer,
            file_name="prova_adaptada.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        if st.button("🔄 Adaptar outra prova"):
            for key in ['login_ok', 'nome_professor', 'materia', 'email_professor']:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

if __name__ == "__main__":
    main()
