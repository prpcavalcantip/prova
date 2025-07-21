import streamlit as st
import fitz  # PyMuPDF
import re

st.title("Extrator de Questões de Prova (PDF)")

uploaded_file = st.file_uploader("Envie o arquivo PDF da prova", type="pdf")

def extrair_questoes(pdf_file):
    # Lê o PDF inteiro
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    
    # Quebra o texto em potenciais blocos de questões pelo padrão das alternativas
    questoes_brutas = re.split(r'(?=\nA\))', texto)
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
            enunciado_completo = ' '.join(enunciado)
            questao_completa = enunciado_completo + "\n" + '\n'.join(alternativas)
            # Só adiciona questões com pelo menos 5 alternativas
            if len(alternativas) >= 5:
                questoes_formatadas.append(questao_completa)
    # Retorna no máximo 10 questões
    return questoes_formatadas[:10]

if uploaded_file:
    st.info("Processando o PDF. Aguarde...")
    questoes = extrair_questoes(uploaded_file)
    if questoes:
        st.success(f"{len(questoes)} questões extraídas!")
        for i, q in enumerate(questoes, 1):
            st.markdown(f"**Questão {i}:**")
            st.markdown(q)
            st.markdown("---")
    else:
        st.warning("Não foi possível extrair questões. Verifique o arquivo PDF e o padrão das questões.")

st.caption("Desenvolvido com Streamlit e PyMuPDF")
       
