import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO
import re

# Dicas específicas por neurodivergência
DICAS = {
    "TDAH": "_Leia com calma e destaque palavras-chave._",
    "Dislexia": "_Leia as alternativas em voz alta._",
    "Autismo": "_Concentre-se em um passo de cada vez._",
}

# Função para identificar questões e alternativas
def extrair_questoes(texto, max_questoes=10):
    # Expressão regular para identificar questões (Ex: 1. ou 1 - ou 1º)
    questao_re = re.compile(r"(?:(?:^|\n)(\d{1,2})[.\-º]?\s+(.+?)(?=\n[A-E][)\.]|\n\n|\Z))", re.DOTALL)
    alternativa_re = re.compile(r"(^[A-E][)\.]?\s+.+)", re.MULTILINE)

    questoes = []
    for match in questao_re.finditer(texto):
        numero = match.group(1)
        enunciado = match.group(2).replace('\n', ' ').strip()
        # Buscar alternativas após o enunciado
        alternativas = alternativa_re.findall(match.group(0))
        if not alternativas:
            # Se não encontrou no bloco, busca nas linhas seguintes
            bloco_fim = match.end()
            alternativas = alternativa_re.findall(texto[bloco_fim:bloco_fim+400])
        if alternativas:
            questoes.append({'numero': numero, 'enunciado': enunciado, 'alternativas': alternativas})
        if len(questoes) >= max_questoes:
            break
    return questoes

# Função para extrair texto do PDF (unindo partes separadas por página)
def extrair_texto_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text("text") + "\n"
    return texto

# Função para encontrar e boldar palavras-chave (simples: palavras >5 letras, não comuns)
def bold_palavras_chave(paragraph, texto):
    stopwords = set(['para','com','que','dos','das','por','uma','como','onde','qual','quais','quando','sobre','entre','após','antes','de','em','ao','os','as','um','e','o','a','no','na','do','da','ou','se'])
    palavras = re.findall(r"\b\w{6,}\b", texto)
    palavras_chave = [p for p in palavras if p.lower() not in stopwords]
    if not palavras_chave:
        paragraph.add_run(texto)
        return
    cursor = 0
    for palavra in palavras_chave:
        idx = texto.lower().find(palavra.lower(), cursor)
        if idx >= cursor:
            # Adiciona texto antes da palavra-chave
            if idx > cursor:
                paragraph.add_run(texto[cursor:idx])
            # Adiciona a palavra em negrito
            run = paragraph.add_run(texto[idx:idx+len(palavra)])
            run.bold = True
            cursor = idx+len(palavra)
    if cursor < len(texto):
        paragraph.add_run(texto[cursor:])

def gerar_docx(questoes, dica, nome):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.size = Pt(14)
    for q in questoes:
        p_enunciado = doc.add_paragraph()
        bold_palavras_chave(p_enunciado, q['enunciado'])
        p_enunciado.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        for alt in q['alternativas']:
            p_alt = doc.add_paragraph(alt.strip())
            p_alt.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        p_dica = doc.add_paragraph(dica)
        for run in p_dica.runs:
            run.italic = True
        p_dica.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        doc.add_paragraph("")  # espaçamento extra
    # Salvar para BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit UI ---
st.title("Adaptador de Provas para Alunos Neurodivergentes")
st.write("Faça o upload do PDF da prova e escolha a neurodivergência para adaptar o texto.")

pdf_file = st.file_uploader("Upload da prova (PDF)", type=["pdf"])
neuro = st.selectbox("Neurodivergência do aluno", ["TDAH", "Dislexia", "Autismo"])

if pdf_file and neuro:
    st.info("Processando PDF...")
    texto = extrair_texto_pdf(pdf_file)
    questoes = extrair_questoes(texto)
    if not questoes:
        st.error("Não foi possível extrair questões. Verifique se o PDF está claro e estruturado.")
    else:
        st.success(f"{len(questoes)} questões extraídas.")
        buffer = gerar_docx(questoes, DICAS[neuro], pdf_file.name)
        st.download_button(
            label="Baixar prova adaptada (DOCX)",
            data=buffer,
            file_name="prova_adaptada.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        # Exibe prévia das questões adaptadas
        st.subheader("Prévia das questões adaptadas:")
        for i, q in enumerate(questoes, 1):
            st.markdown(f"**Questão {i}:** {q['enunciado']}")
            for alt in q['alternativas']:
                st.markdown(f"- {alt}")
            st.markdown(DICAS[neuro])