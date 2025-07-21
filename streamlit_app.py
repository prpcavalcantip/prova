import streamlit as st
import fitz  # PyMuPDF
import re
from docx import Document
from io import BytesIO

st.title("Extrator de Questões de Prova (PDF)")

uploaded_file = st.file_uploader("Envie o arquivo PDF da prova", type="pdf")

def extrair_questoes(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    # Divide por padrões de alternativas (A))
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
            # Junta linhas do enunciado com espaço entre elas
            enunciado_completo = "\n".join([e for e in enunciado if e])
            # Alternativas separadas
            alternativas_formatadas = '\n'.join([alt for alt in alternativas if alt])
            questao_completa = enunciado_completo + "\n\n" + alternativas_formatadas
            # Adiciona questões com pelo menos 5 alternativas
            if len(alternativas) >= 5:
                questoes_formatadas.append(questao_completa)
    return questoes_formatadas[:10]

def gerar_docx(questoes):
    doc = Document()
    doc.add_heading("Questões Extraídas da Prova", 0)
    for i, q in enumerate(questoes, 1):
        doc.add_heading(f"Questão {i}", level=1)
        partes = q.split('\n\n', 1)
        if len(partes) == 2:
            enunciado, alternativas = partes
            for p in enunciado.split('\n'):
                doc.add_paragraph(p)
            # Adiciona cada alternativa como bullet
            for alt in alternativas.split('\n'):
                doc.add_paragraph(alt, style='List Bullet')
        else:
            doc.add_paragraph(q)
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
                for p in enunciado.split('\n'):
                    st.markdown(p)
                st.markdown("")
                for alt in alternativas.split('\n'):
                    st.markdown(f"- {alt}")
            else:
                st.markdown(q)
            st.markdown("---")
        docx_buffer = gerar_docx(questoes)
        st.download_button(
            label="Baixar questões em DOCX",
            data=docx_buffer,
            file_name="questoes_extraidas.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("Não foi possível extrair questões. Verifique o arquivo PDF e o padrão das questões.")

st.caption("Desenvolvido com Streamlit, PyMuPDF e python-docx")
