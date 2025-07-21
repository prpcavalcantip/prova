import os
import streamlit as st
import fitz  # PyMuPDFhttps://github.com/copilot/c/4137c9b4-4173-40c9-b833-e8df530aa434#copilot-chat-textarea
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re

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

def avaliar_enunciado(enunciado):
    # Avalia a clareza do enunciado: quanto menor, mais direto
    # Pontuação: quanto menor o texto e menos termos complexos, mais direto
    palavras_complexas = ['explique', 'analise', 'interprete', 'justifique', 'discuta']
    score = len(enunciado)
    for termo in palavras_complexas:
        if termo in enunciado.lower():
            score += 20  # penaliza termos complexos
    return score

def simplificar_enunciado_chatgpt(enunciado):
    # Aqui você pode usar um modelo LLM via API para simplificar, mas o exemplo abaixo é local e só ilustra...
    # O ideal é substituir por uma chamada à API OpenAI com prompt de simplificação!
    # Exemplo de simplificação: remove termos complexos e deixa o texto mais direto
    enunciado = re.sub(r'[Ss]egundo o texto,? ?', '', enunciado)
    enunciado = re.sub(r'[Dd]e acordo com o autor,? ?', '', enunciado)
    enunciado = re.sub(r'\s+', ' ', enunciado)
    return enunciado.strip()

def simplificar_questao(texto, numero, perfil):
    texto = re.sub(r'\s+', ' ', texto).strip()
    match = re.match(r'(QUESTÃO \d+ )(.*?)([A-E]\))', texto)
    if not match:
        enunciado = texto
        alternativas = []
    else:
        inicio = match.start(3)
        enunciado = texto[:inicio].strip()
        alternativas = re.findall(r'([A-E]\))\s?(.*?)(?=\s[A-E]\)|$)', texto[inicio:])

    enunciado_simplificado = simplificar_enunciado_chatgpt(enunciado)
    return {
        "numero": numero,
        "enunciado": enunciado_simplificado,
        "alternativas": alternativas,
        "dica": obter_dica(perfil, numero),
        "score": avaliar_enunciado(enunciado_simplificado)
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

def main():
    nome_professor = st.text_input("Digite seu nome completo")
    materia = st.text_input("Digite a matéria que você ensina")

    if not nome_professor or not materia:
        st.info("Preencha nome e matéria para continuar")
        st.stop()

    st.title("🧠 Adaptador de Provas para Alunos Neurodivergentes")
    st.caption(f"Professor(a): {nome_professor} | Matéria: {materia}")

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

        # Avalia todas as questões e seleciona as 5 mais diretas
        questoes_avaliadas = []
        for i, q_texto in enumerate(questoes_raw, start=1):
            questoes_avaliadas.append(simplificar_questao(q_texto, i, perfil))

        # Ordena por score (menor é mais direto/compreensível)
        questoes_mais_diretas = sorted(questoes_avaliadas, key=lambda q: q['score'])[:5]

        doc = gerar_docx(questoes_mais_diretas, nome_professor, materia)
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

        # Mostra as questões escolhidas antes do download
        st.markdown("### Questões selecionadas:")
        for q in questoes_mais_diretas:
            st.markdown(f"**QUESTÃO {q['numero']}**: {q['enunciado']}")

        if st.button("🔄 Adaptar outra prova"):
            st.experimental_rerun()

if __name__ == "__main__":
    main()
