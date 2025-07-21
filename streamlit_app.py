import os
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
import re

# --- Tema de cores e logo ---
PRIMARY_COLOR = "#2563eb"
SECONDARY_COLOR = "#f1f5f9"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/0/02/SVG_logo.svg"  # Troque pelo logo da instituição

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
    palavras_complexas = ['explique', 'analise', 'interprete', 'justifique', 'discuta']
    score = len(enunciado)
    for termo in palavras_complexas:
        if termo in enunciado.lower():
            score += 20
    return score

def limpar_enunciado(enunciado):
    enunciado = re.sub(r'^QUESTÃO\s*\d+\s*', '', enunciado, flags=re.IGNORECASE)
    enunciado = re.sub(r'\s+', ' ', enunciado)
    return enunciado.strip()

def simplificar_enunciado_chatgpt(enunciado):
    enunciado = limpar_enunciado(enunciado)
    enunciado = re.sub(r'[Ss]egundo o texto,? ?', '', enunciado)
    enunciado = re.sub(r'[Dd]e acordo com o autor,? ?', '', enunciado)
    enunciado = re.sub(r'\s+', ' ', enunciado)
    return enunciado.strip()

def simplificar_questao(texto, perfil):
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
        "enunciado": enunciado_simplificado,
        "alternativas": alternativas,
        "score": avaliar_enunciado(enunciado_simplificado)
    }

def gerar_docx(questoes, nome_professor, materia, perfil):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(14)

    doc.add_heading(f"Prova Adaptada – {materia} – {nome_professor}", 0)
    doc.add_paragraph(f"Professor(a): {nome_professor}", style='Normal')
    doc.add_paragraph(f"Matéria: {materia}", style='Normal')
    doc.add_paragraph("")

    for i, q in enumerate(questoes, start=1):
        doc.add_paragraph(f"QUESTÃO {i}", style='Normal')
        doc.add_paragraph(q['enunciado'], style='Normal')
        doc.add_paragraph("")  # Espaço antes das alternativas

        for letra, alt in q['alternativas']:
            doc.add_paragraph(f"{letra} {alt.strip()}", style='Normal')

        doc.add_paragraph(f"🧠 DICA: {obter_dica(perfil, i)}", style='Normal')
        doc.add_paragraph("")

    return doc

def reset_form():
    st.session_state.pop("arquivo", None)
    st.session_state.pop("perfil", None)
    st.session_state.pop("prova_processada", None)
    st.session_state.pop("download_ready", None)

def main():
    st.markdown(
        f"""
        <div style="background:{PRIMARY_COLOR};padding:1.5rem;border-radius:10px;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;">
                <img src="{LOGO_URL}" alt="Logo" style="height:54px;margin-right:1rem;">
                <div>
                    <h2 style="color:white; margin-bottom:0;">Adaptador de Provas para Alunos Neurodivergentes</h2>
                    <span style="color:white;">Ferramenta para professores - versão beta</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    with st.container():
        col1, col2 = st.columns([2,1])
        with col1:
            nome_professor = st.text_input("👤 Nome do Professor(a)")
            materia = st.text_input("📘 Matéria")

        with col2:
            st.image(LOGO_URL, width=95)

    if not nome_professor or not materia:
        st.info("Preencha nome e matéria para continuar")
        st.stop()

    st.divider()

    if "prova_processada" not in st.session_state:
        st.markdown("#### Escolha o tipo de adaptação e envie seu arquivo PDF")
        perfil = st.selectbox("💡 Tipo de adaptação:", list(TIPOS_DICAS.keys()), key="perfil")
        arquivo = st.file_uploader("📄 Envie a prova em PDF", type=["pdf"], key="arquivo")
        if arquivo:
            st.toast("Arquivo recebido!", icon="✅")
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

            questoes_avaliadas = []
            for q_texto in questoes_raw:
                questoes_avaliadas.append(simplificar_questao(q_texto, perfil))

            questoes_mais_diretas = sorted(questoes_avaliadas, key=lambda q: q['score'])[:5]

            doc = gerar_docx(questoes_mais_diretas, nome_professor, materia, perfil)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.session_state["prova_processada"] = buffer
            st.session_state["download_ready"] = True

    if st.session_state.get("download_ready", False):
        st.success("Prova adaptada gerada com sucesso! 🎉")
        st.markdown(
            """
            <div style="background:#f3f4f6;padding:1rem 2rem;border-radius:10px;">
                <b>Está pronta para download!</b> Sua prova adaptada está pronta. Se quiser adaptar outra prova, clique abaixo.
            </div>
            """, unsafe_allow_html=True
        )

        st.download_button(
            "📥 Baixar Prova Adaptada (.docx)",
            data=st.session_state["prova_processada"],
            file_name="prova_adaptada.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.divider()
        st.button("🔄 Adaptar outra prova", on_click=reset_form)

if __name__ == "__main__":
    main()
