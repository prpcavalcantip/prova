import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re

# Configurações de dicas por tipo de neurodivergência
tipos_dicas = {
    "TDAH": {
        1: "Leia com calma. Destaque palavras importantes.",
        2: "Use setas ou cores para conectar ideias.",
        3: "Evite distrações: foque uma questão de cada vez.",
        4: "Grife os conceitos-chave no enunciado.",
        5: "Relacione a questão com exemplos práticos."
    },
    "Dislexia": {
        1: "Leia devagar. Palavras difíceis podem confundir.",
        2: "Separe frases longas em partes curtas.",
        3: "Use régua ou dedo para acompanhar.",
        4: "Leia em voz baixa para entender melhor.",
        5: "Marque palavras que aparecem muito."
    },
    "TEA": {
        1: "Observe a estrutura lógica da questão.",
        2: "Use imagens mentais para entender conceitos.",
        3: "Evite interpretações subjetivas: vá direto ao que é pedido.",
        4: "Releia com atenção cada alternativa.",
        5: "Destaque padrões e repetições."
    }
}

# Função para simplificar texto e adicionar dica
def simplificar_questao(texto, numero, perfil):
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Separar enunciado e alternativas
    match = re.match(r'(QUESTÃO \d+ )(.*?)([A-E]\))', texto)
    if not match:
        return {
            "numero": numero,
            "enunciado": texto,
            "alternativas": [],
            "dica": tipos_dicas.get(perfil, {}).get(numero, "Leia com atenção.")
        }

    inicio = match.start(3)
    enunciado = texto[:inicio].strip()
    alternativas = re.findall(r'([A-E]\))\s?(.*?)(?=\s[A-E]\)|$)', texto[inicio:])

    return {
        "numero": numero,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "dica": tipos_dicas.get(perfil, {}).get(numero, "Leia com atenção.")
    }

# Gerar documento .docx com formatação acessível
def gerar_docx(questoes):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(14)

    doc.add_heading("Prova Adaptada – Geografia – 3º Ano", 0)

    for q in questoes:
        doc.add_paragraph(f"QUESTÃO {q['numero']}", style='Normal')
        doc.add_paragraph(q['enunciado'], style='Normal')
        doc.add_paragraph("")  # Espaço antes das alternativas

        for letra, alt in q['alternativas']:
            doc.add_paragraph(f"{letra} {alt.strip()}", style='Normal')

        doc.add_paragraph(f"🧠 DICA: {q['dica']}", style='Normal')
        doc.add_paragraph("")

    return doc

# Interface de autenticação simulada (protótipo)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Login do Professor")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email and senha:
            st.session_state.autenticado = True
        else:
            st.warning("Preencha todos os campos.")
    st.markdown("[Entrar com Google (simulado)]")
    st.stop()

# App principal
st.title("🧠 Adaptador de Provas para Alunos Neurodivergentes")

perfil = st.selectbox("Selecione o tipo de adaptação:", ["TDAH", "Dislexia", "TEA"])

arquivo = st.file_uploader("Envie a prova em PDF", type=["pdf"])

if arquivo:
    st.success("Arquivo recebido!")
    pdf = fitz.open(stream=arquivo.read(), filetype="pdf")
    texto_completo = ""
    for pagina in pdf:
        texto_completo += pagina.get_text()

    questoes_raw = re.findall(r'QUESTÃO \d+.*?(?=QUESTÃO \d+|$)', texto_completo, flags=re.DOTALL)

    questoes_simplificadas = []
    for i, q_texto in enumerate(questoes_raw[:5], start=1):
        questoes_simplificadas.append(simplificar_questao(q_texto, i, perfil))

    doc = gerar_docx(questoes_simplificadas)

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

      
