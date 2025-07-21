import streamlit as st
import fitz  # PyMuPDF
import re
from docx import Document
from docx.shared import Pt
from io import BytesIO

st.title("Adaptador de Provas Inclusivo")
st.markdown("""
Este aplicativo extrai e adapta questões objetivas de provas em PDF para facilitar a inclusão de neurodivergentes.
""")

opcoes_neuro = [
    "Nenhum",
    "TDAH",
    "Dislexia",
    "Autismo",
    "Deficiência visual",
    "Outro"
]
neuro = st.selectbox("Escolha o perfil neurodivergente para adaptação:", opcoes_neuro)

uploaded_file = st.file_uploader("Envie o arquivo PDF da prova", type="pdf")

def limpa_numero_questao(texto):
    texto = re.sub(r'\bQUEST[ÃA]O\s*\d+\b', '', texto)
    texto = re.sub(r'\bQuest[ãa]o\s*\d+\b', '', texto)
    texto = re.sub(r'\bQUEST[ÃA]O\b', '', texto)
    texto = re.sub(r'\bQuest[ãa]o\b', '', texto)
    texto = re.sub(r'^\s*:', '', texto)
    texto = texto.strip()
    return texto

def corrige_questao_truncada(texto):
    texto = re.sub(r'\s*\.\s*\.', '. ', texto)
    texto = re.sub(r'\s*\.\s*', '. ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto)
    frases = re.split(r'(\.|\?|!)', texto)
    frases_corrigidas = []
    for i in range(0, len(frases)-1, 2):
        frase = frases[i].strip()
        pontuacao = frases[i+1] if i+1 < len(frases) else ''
        if frase:
            frase = frase[0].upper() + frase[1:]
        frases_corrigidas.append(frase + pontuacao + ' ')
    resultado = ''.join(frases_corrigidas).strip()
    return resultado

def simplifica_enunciado(enunciado):
    frases = re.split(r'(\.|\?|!)', enunciado)
    simples = []
    for f in frases:
        f2 = f.strip()
        if f2 and len(f2.split()) < 25:
            simples.append(f2)
    resultado = ' '.join(simples)
    if len(resultado.split()) < 6:
        return enunciado
    return resultado

def gera_dica(enunciado, alternativas):
    if "BRICS" in enunciado.upper():
        return "Dica: BRICS é um grupo de países emergentes. Pense no desenvolvimento econômico de cada opção."
    if "população" in enunciado.lower():
        return "Dica: Observe os dados sobre população e condições de vida no texto."
    if "geologia" in enunciado.lower():
        return "Dica: Relacione os agentes do relevo com as alternativas oferecidas."
    if "comércio" in enunciado.lower():
        return "Dica: Fique atento aos termos sobre relações comerciais entre países."
    if "história" in enunciado.lower():
        return "Dica: Preste atenção à sequência de fatos históricos."
    return "Dica: Leia com atenção e procure palavras-chave que ajudam a decidir a resposta."

def enunciado_tem_sentido(enunciado, alternativas):
    # Torne o filtro menos rígido para aceitar questões mais facilmente
    if not enunciado or len(enunciado.split()) < 5:
        return False
    # Remover obrigatoriedade das palavras chave
    padroes_excluir = [
        r'marque v para verdadeiro', r'v para verdadeiro', r'f para falso',
        r'analise as afirmações', r'assinale verdadeiro', r'correlacione',
        r'preencha', r'complete a tabela', r'numere', r'coloque', r'observe as afirmações',
        r'marque v/f', r'v/f', r'tabela abaixo', r'analise as proposições'
    ]
    texto_checagem = enunciado.lower()
    for padrao in padroes_excluir:
        if re.search(padrao, texto_checagem):
            return False
    alt_checagem = ''.join(alternativas).replace(" ", "").upper()
    if re.match(r'^[AVF]+$', alt_checagem.replace(')', '').replace('(', '')):
        return False
    if all(re.match(r'^[A-E]\)\s*[FV\s]+$', alt) for alt in alternativas):
        return False
    return True

def extrair_questoes(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    linhas = texto.split('\n')
    blocos = []
    bloco_atual = []
    for linha in linhas:
        if re.match(r'^[A-E]\)', linha.strip()):
            bloco_atual.append(linha.strip())
        elif len(bloco_atual) > 0 and not re.match(r'^[A-E]\)', linha.strip()):
            bloco_atual.append(linha.strip())
        elif len(linha.strip()) > 0:
            if bloco_atual:
                blocos.append('\n'.join(bloco_atual))
            bloco_atual = [linha.strip()]
    if bloco_atual:
        blocos.append('\n'.join(bloco_atual))
    questoes_formatadas = []
    for bloco in blocos:
        partes = bloco.strip().split('\n')
        enunciado = []
        alternativas = []
        for linha in partes:
            if re.match(r'^[A-E]\)', linha.strip()):
                alternativas.append(linha.strip())
            else:
                enunciado.append(linha.strip())
        if alternativas:
            enunciado_completo = " ".join([limpa_numero_questao(e.strip()) for e in enunciado if e])
            enunciado_corrigido = corrige_questao_truncada(enunciado_completo)
            enunciado_simples = simplifica_enunciado(enunciado_corrigido)
            # Filtro menos rígido
            if not enunciado_tem_sentido(enunciado_simples, alternativas):
                continue
            alternativas_formatadas = '\n'.join([alt for alt in alternativas if alt])
            dica = gera_dica(enunciado_simples, alternativas_formatadas)
            questao_completa = enunciado_simples + "\n\n" + alternativas_formatadas + "\n\n" + f"Dica: {dica}"
            if len(alternativas) >= 5 and enunciado_simples.strip():
                questoes_formatadas.append((questao_completa, enunciado_simples))
    questoes_formatadas.sort(key=lambda x: len(x[1]))
    return [q[0] for q in questoes_formatadas[:5]]

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
        partes = q.split('\n\n', 2)
        enunciado = partes[0] if len(partes) > 0 else ""
        alternativas = partes[1] if len(partes) > 1 else ""
        dica = partes[2] if len(partes) > 2 else ""
        para = doc.add_paragraph(enunciado)
        para.style = style
        for alt in alternativas.split('\n'):
            para = doc.add_paragraph(alt, style='List Bullet')
            para.style = style
        para = doc.add_paragraph(dica)
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
        st.success(f"{len(questoes)} questões adaptadas e simplificadas para inclusão!")
        for i, q in enumerate(questoes, 1):
            partes = q.split('\n\n', 2)
            enunciado = partes[0] if len(partes) > 0 else ""
            alternativas = partes[1] if len(partes) > 1 else ""
            dica = partes[2] if len(partes) > 2 else ""
            st.markdown(f"**Questão {i}:**")
            st.markdown(f"{enunciado}")
            st.markdown("")
            for alt in alternativas.split('\n'):
                st.markdown(f"- {alt}")
            st.markdown(f"> {dica}")
            st.markdown("---")
        docx_buffer = gerar_docx(questoes, neuro)
        st.download_button(
            label="Baixar questões em DOCX",
            data=docx_buffer,
            file_name="questoes_adaptadas.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("Não foi possível extrair questões objetivas e claras. Tente outro arquivo PDF ou envie o texto da prova aqui para que eu possa ajustar o código.")

st.caption("Desenvolvido com Streamlit, PyMuPDF e python-docx")
