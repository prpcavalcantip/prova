import streamlit as st
import fitz  # PyMuPDF
import re
from docx import Document
from docx.shared import Pt
from io import BytesIO

# --- TÍTULO E INSTRUÇÕES ---
st.title("Adaptador de prova inclusivo")
st.markdown("""
Bem-vindo! Este aplicativo extrai questões de provas em PDF e adapta para diferentes perfis neurodivergentes.
""")

# --- SELEÇÃO DE NEURODIVERGÊNCIA ---
opcoes_neuro = [
    "Nenhum",
    "TDAH",
    "Dislexia",
    "Autismo",
    "Deficiência visual",
    "Outro"
]
neuro = st.selectbox("Escolha o perfil neurodivergente para adaptação:", opcoes_neuro)

st.write("Após selecionar o perfil, envie o arquivo PDF da prova:")

uploaded_file = st.file_uploader("Envie o arquivo PDF da prova", type="pdf")

def limpa_numero_questao(texto):
    """
    Remove padrões do tipo 'QUESTÃO xx', 'Questão xx', ou 'QUESTÃO:'
    """
    # Remove 'QUESTÃO', 'Questão' ou variações, seguidos de número
    texto = re.sub(r'\bQUEST[ÃA]O\s*\d+\b', '', texto)
    texto = re.sub(r'\bQuest[ãa]o\s*\d+\b', '', texto)
    texto = re.sub(r'\bQUEST[ÃA]O\b', '', texto)
    texto = re.sub(r'\bQuest[ãa]o\b', '', texto)
    texto = re.sub(r'^\s*:', '', texto)
    texto = texto.strip()
    return texto

def extrair_questoes(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    questoes_brutas = re.split(r'\n(?=A\))', texto)
    questoes_formatadas = []
    for bloco in questoes_brutas:
        partes = bloco.strip().split('\n')
        enunciado = []
        alternativas = []
        for linha in partes:
            if re.match(r'^[A-E]\)', linha.strip()):
                alternativas.append(linha.strip())
            else:
                enunciado.append(linha.strip())
        if alternativas:
            # Junta o enunciado em um único parágrafo, removendo "Questão xx"
            enunciado_completo = " ".join([limpa_numero_questao(e.strip()) for e in enunciado if e])
            alternativas_formatadas = '\n'.join([alt for alt in alternativas if alt])
            questao_completa = enunciado_completo + "\n\n" + alternativas_formatadas
            if len(alternativas) >= 5 and enunciado_completo.strip():
                questoes_formatadas.append(questao_completa)
    return questoes_formatadas[:10]

def gerar_docx(questoes, neuro):
    doc = Document()
    doc.add_heading("Questões Adaptadas da Prova", 0)
    if neuro and neuro != "Nenhum":
        doc.add_paragraph(f"Perfil neurodivergente selecionado: {neuro}")
        doc.add_paragraph("")
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(14)
    for i, q in enumerate(questoes, 1):
        doc.add_heading(f"Questão {i}", level=1)
        partes = q.split('\n\n', 1)
        if len(partes) == 2:
            enunciado, alternativas = partes
            para = doc.add_paragraph(enunciado)
            para.style = style
            for alt in alternativas.split('\n'):
                para = doc.add_paragraph(alt, style='List Bullet')
                para.style = style
        else:
            para = doc.add_paragraph(q)
            para.style = style
        doc.add_paragraph("")  # Espaço entre questões
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if uploaded_file:
    st.info("Processando o PDF. Aguarde...")
    questoes = extrair_questoes(uploaded_file)
    if questoes:
        st.success(f"{len(questoes)} questões extraídas!")
        for i, q in enumerate(questoes, 1):
            partes = q.split('\n\n', 1)
            st.markdown(f"**Questão {i}:**")
            if len(partes) == 2:
                enunciado, alternativas = partes
                st.markdown(enunciado)
                st.markdown("")
                for alt in alternativas.split('\n'):
                    st.markdown(f"- {alt}")
            else:
                st.markdown(q)
            st.markdown("---")
        docx_buffer = gerar_docx(questoes, neuro)
        st.download_button(
            label="Baixar questões em DOCX",
            data=docx_buffer,
            file_name="questoes_adaptadas.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("Não foi possível extrair questões. Verifique o arquivo PDF e o padrão das questões.")

st.caption("Desenvolvido com Streamlit, PyMuPDF e python-docx")
