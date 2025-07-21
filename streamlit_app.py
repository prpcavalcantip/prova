
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re

# Função para simplificar e adaptar a questão com dica
def simplificar_questao(texto, numero):
    texto = re.sub(r'\s+', ' ', texto).strip()

    dicas_padrao = {
        1: "Leia com calma. Procure a alternativa que está errada.",
        2: "Pense no que acontece com o movimento da Terra.",
        3: "Lembre-se: relevo é tudo que muda na paisagem com o tempo.",
        4: "Rochas mudam de forma ao longo do tempo. Pense nos processos.",
        5: "O calor e a umidade ajudam os nutrientes a voltarem ao solo.",
    }

    dica = dicas_padrao.get(numero, "Pense com calma. Use o que você aprendeu nas aulas.")

    return {
        "numero": numero,
        "enunciado": texto,
        "dica": dica
    }

# Função para gerar o .docx adaptado
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
        doc.add_paragraph(f"🧠 DICA: {q['dica']}", style='Normal')
        doc.add_paragraph("")  # espaço entre questões

    return doc

# Interface do Streamlit
st.title("🧠 Adaptador de Provas para Alunos Neurodivergentes")

arquivo = st.file_uploader("Envie a prova em PDF", type=["pdf"])

if arquivo:
    st.success("Arquivo recebido!")
    pdf = fitz.open(stream=arquivo.read(), filetype="pdf")
    texto_completo = ""
    for pagina in pdf:
        texto_completo += pagina.get_text()

    # Extrair questões a partir do padrão "QUESTÃO"
    questoes_raw = re.findall(r'QUESTÃO \d+.*?(?=QUESTÃO \d+|$)', texto_completo, flags=re.DOTALL)

    questoes_simplificadas = []
    for i, q_texto in enumerate(questoes_raw[:5], start=1):
        questoes_simplificadas.append(simplificar_questao(q_texto, i))

    doc = gerar_docx(questoes_simplificadas)

    # Salvar em memória
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

    
