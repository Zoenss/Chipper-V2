from textwrap import dedent

import streamlit as st


st.set_page_config(
    page_title="Chipper",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================
# ESTILO DA PÁGINA
# =========================
st.markdown(
    dedent(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(
                        circle at 50% 10%,
                        #0c4a6e 0%,
                        #0f172a 38%,
                        #020617 78%
                    );
                color: white;
            }

            [data-testid="stSidebar"] {
                display: none;
            }

            header,
            footer {
                visibility: hidden;
            }

            .block-container {
                max-width: 850px;
                padding-top: 60px;
                padding-bottom: 40px;
            }

            .hero {
                text-align: center;
                margin-bottom: 35px;
            }

            .logo {
                font-size: 68px;
                font-weight: 900;
                letter-spacing: 12px;
                color: #38bdf8;
                text-shadow:
                    0 0 12px rgba(56, 189, 248, 0.9),
                    0 0 30px rgba(2, 132, 199, 0.6);
            }

            .subtitle {
                color: #cbd5e1;
                letter-spacing: 3px;
                font-size: 17px;
            }

            .version {
                color: #64748b;
                font-family: monospace;
                margin-top: 8px;
            }

            .system-card {
                background: rgba(15, 23, 42, 0.82);
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 25px;
                box-shadow: 0 0 25px rgba(2, 132, 199, 0.12);
            }

            .system-title {
                color: #22d3ee;
                font-family: monospace;
                font-weight: bold;
                margin-bottom: 12px;
                letter-spacing: 1px;
            }

            .system-line {
                color: #94a3b8;
                font-family: monospace;
                margin: 7px 0;
            }

            .ok {
                color: #22c55e;
            }

            .assistant-title {
                color: #38bdf8;
                font-size: 18px;
                font-weight: 800;
                margin-bottom: 12px;
            }

            .assistant-text {
                color: #cbd5e1;
                font-size: 15px;
                line-height: 1.8;
            }

            .stTextInput label,
            .stNumberInput label {
                color: #cbd5e1 !important;
                font-weight: 700 !important;
            }

            .stTextInput input,
            .stNumberInput input {
                background-color: rgba(15, 23, 42, 0.95) !important;
                border: 1px solid #334155 !important;
                color: white !important;
                border-radius: 12px !important;
                min-height: 52px;
            }

            .stTextInput input:focus,
            .stNumberInput input:focus {
                border-color: #38bdf8 !important;
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                width: 100%;
                min-height: 55px;
                margin-top: 18px;
                border-radius: 12px;
                border: 1px solid #38bdf8;
                background: linear-gradient(90deg, #0284c7, #06b6d4);
                color: white;
                font-weight: 800;
                letter-spacing: 2px;
                transition: 0.25s;
            }

            div.stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                border-color: #67e8f9;
                box-shadow:
                    0 0 12px rgba(34, 211, 238, 0.7),
                    0 0 30px rgba(2, 132, 199, 0.4);
                transform: translateY(-2px);
            }

            .footer {
                text-align: center;
                color: #475569;
                font-family: monospace;
                font-size: 12px;
                margin-top: 45px;
            }
        </style>
        """
    ),
    unsafe_allow_html=True,
)


# =========================
# CABEÇALHO
# =========================
st.markdown(
    '<div class="hero">'
    '<div class="logo" translate="no">CHIPPER</div>'
    '<div class="subtitle">REVERSE LOGISTICS INTELLIGENCE</div>'
    '<div class="version">SYSTEM v2.0</div>'
    '</div>',
    unsafe_allow_html=True,
)


# =========================
# STATUS DO SISTEMA
# =========================
st.markdown(
    '<div class="system-card">'
    '<div class="system-title">STATUS DO SISTEMA</div>'
    '<div class="system-line"><span class="ok">●</span> Interface disponível</div>'
    '<div class="system-line"><span class="ok">●</span> Motor de consulta preparado</div>'
    '<div class="system-line"><span class="ok">●</span> Catálogo local disponível</div>'
    '<div class="system-line"><span class="ok">●</span> Sistema aguardando uma nova análise</div>'
    '</div>',
    unsafe_allow_html=True,
)

# =========================
# ASSISTENTE INICIAL
# =========================
with st.expander("Como utilizar o Chipper"):
    st.markdown(
        dedent(
            """
            <div class="assistant-title">
                Assistente de utilização
            </div>

            <div class="assistant-text">
                1. Informe o nome completo do equipamento eletrônico.<br>
                2. Meça a massa do equipamento utilizando uma balança.<br>
                3. Informe a massa em gramas.<br>
                4. Clique em <strong>Iniciar análise</strong>.<br>
                5. O Chipper consultará as informações técnicas e preparará
                a análise de logística reversa.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================
# FORMULÁRIO DE ANÁLISE
# =========================
with st.form("formulario_analise", clear_on_submit=False):

    aparelho = st.text_input(
        "Identifique o equipamento",
        placeholder="Ex.: Samsung Galaxy M55 5G",
    )

    peso = st.number_input(
        "Massa medida em gramas",
        min_value=0.0,
        step=1.0,
        format="%.1f",
    )

    iniciar_analise = st.form_submit_button(
        "INICIAR ANÁLISE",
        use_container_width=True,
    )


# =========================
# VALIDAÇÃO
# =========================
if iniciar_analise:

    nome_aparelho = aparelho.strip()

    if not nome_aparelho:
        st.warning("Informe o nome do equipamento.")

    elif peso <= 0:
        st.warning("Informe uma massa maior que zero.")

    else:
        st.session_state["aparelho"] = nome_aparelho
        st.session_state["peso"] = float(peso)

        st.switch_page("pages/02_Analisar.py")


# =========================
# RODAPÉ
# =========================
st.markdown(
    dedent(
        """
        <div class="footer">
            CHIPPER CORE • MATERIAL INTELLIGENCE • REVERSE LOGISTICS
        </div>
        """
    ),
    unsafe_allow_html=True,
)