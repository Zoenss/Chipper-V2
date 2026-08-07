from html import escape
from typing import Any

import streamlit as st

from services.api_service import MobileAPIError, buscar_dispositivo
from services.analysis_service import (
    estimar_analise,
    identificar_categoria_por_nome,
)


st.set_page_config(
    page_title="Chipper - Análise",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
@st.cache_data(ttl=3600, show_spinner=False)
def consultar_api(nome_aparelho: str) -> dict[str, Any]:
    """
    Consulta a MobileAPI e mantém o resultado em cache por uma hora.
    """
    return buscar_dispositivo(nome_aparelho)


def normalizar_texto(texto: str) -> str:
    """
    Normaliza textos para melhorar a comparação entre o nome digitado
    e os resultados retornados pela API.
    """
    return " ".join(texto.strip().lower().split())


def selecionar_melhor_resultado(
    consulta: dict[str, Any] | None,
    nome_pesquisado: str,
) -> dict[str, Any] | None:
    """
    Seleciona o resultado mais compatível com o nome informado.

    Prioridade:
    1. Nome exatamente igual.
    2. Nome pesquisado contido no nome retornado.
    3. Nome retornado contido no nome pesquisado.
    4. Maior percentual de confiança.
    """
    if not consulta or not consulta.get("encontrado"):
        return None

    resultados = consulta.get("resultados", {})

    if not isinstance(resultados, dict):
        return None

    dispositivos = resultados.get("devices", [])

    if not isinstance(dispositivos, list) or not dispositivos:
        return None

    nome_pesquisado_normalizado = normalizar_texto(nome_pesquisado)

    # Correspondência exata.
    for dispositivo in dispositivos:
        nome_dispositivo = normalizar_texto(
            str(dispositivo.get("name") or "")
        )

        if nome_dispositivo == nome_pesquisado_normalizado:
            return dispositivo

    # O nome pesquisado está dentro do resultado.
    for dispositivo in dispositivos:
        nome_dispositivo = normalizar_texto(
            str(dispositivo.get("name") or "")
        )

        if nome_pesquisado_normalizado in nome_dispositivo:
            return dispositivo

    # O resultado está dentro do nome pesquisado.
    for dispositivo in dispositivos:
        nome_dispositivo = normalizar_texto(
            str(dispositivo.get("name") or "")
        )

        if nome_dispositivo and nome_dispositivo in nome_pesquisado_normalizado:
            return dispositivo

    # Usa o resultado com maior confiança.
    def obter_confianca(dispositivo: dict[str, Any]) -> float:
        valor = str(dispositivo.get("match_certainty") or "0")
        valor = valor.replace("%", "").strip()

        try:
            return float(valor)
        except ValueError:
            return 0.0

    return max(
        dispositivos,
        key=obter_confianca,
        default=None,
    )


def valor_seguro(
    dados: dict[str, Any],
    chave: str,
    padrao: str = "Não informado",
) -> str:
    """
    Retorna um valor tratado para exibição em HTML.
    """
    valor = dados.get(chave)

    if valor is None or str(valor).strip() == "":
        valor = padrao

    return escape(str(valor))


def montar_lista_html(itens: list[str]) -> str:
    """
    Cria uma lista HTML segura para os cartões.
    """
    return "".join(
        (
            '<div class="list-item">'
            '<span class="list-marker">•</span>'
            f'{escape(str(item))}'
            '</div>'
        )
        for item in itens
    )


def traduzir_categoria(categoria: str) -> str:
    traducoes = {
        "phone": "Smartphone",
        "tablet": "Tablet",
        "notebook": "Notebook",
        "desktop": "Computador desktop",
        "console": "Console de videogame",
        "monitor": "Monitor",
        "desconhecido": "Equipamento eletrônico",
    }

    return traducoes.get(
        categoria.strip().lower(),
        categoria.capitalize(),
    )


# ==================================================
# ESTILO
# ==================================================
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 50% 15%,
                    #0c4a6e 0%,
                    #0f172a 35%,
                    #020617 75%
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
            max-width: 1180px;
            padding-top: 45px;
            padding-bottom: 60px;
        }

        .page-title {
            font-size: 48px;
            font-weight: 900;
            color: #38bdf8;
            text-shadow:
                0 0 14px rgba(56, 189, 248, 0.65),
                0 0 30px rgba(2, 132, 199, 0.30);
            margin-bottom: 4px;
        }

        .page-subtitle {
            color: #94a3b8;
            font-size: 17px;
            margin-bottom: 32px;
        }

        .section-title {
            color: #e2e8f0;
            font-size: 27px;
            font-weight: 850;
            margin-top: 28px;
            margin-bottom: 17px;
        }

        .card {
            background: rgba(15, 23, 42, 0.84);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 21px;
            margin-bottom: 17px;
            box-shadow: 0 0 22px rgba(2, 132, 199, 0.09);
            height: calc(100% - 17px);
        }

        .card-title {
            color: #22d3ee;
            font-size: 14px;
            font-weight: 850;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .main-value {
            color: #ffffff;
            font-size: 23px;
            font-weight: 750;
            overflow-wrap: anywhere;
        }

        .technical-value {
            color: #e2e8f0;
            font-size: 16px;
            font-weight: 650;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }

        .small-text {
            color: #94a3b8;
            font-size: 14px;
            line-height: 1.65;
            margin-top: 7px;
        }

        .source-success {
            color: #22c55e;
            font-size: 19px;
            font-weight: 750;
        }

        .source-warning {
            color: #f59e0b;
            font-size: 19px;
            font-weight: 750;
        }

        .source-error {
            color: #ef4444;
            font-size: 19px;
            font-weight: 750;
        }

        .estimated-badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.55);
            border-radius: 999px;
            color: #fbbf24;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.8px;
            padding: 5px 10px;
            margin-bottom: 14px;
        }

        .list-item {
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.65;
            padding: 3px 0;
        }

        .list-marker {
            color: #22d3ee;
            font-weight: 900;
            margin-right: 8px;
        }

        .metric-value {
            color: #38bdf8;
            font-size: 31px;
            font-weight: 900;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 14px;
            margin-top: 5px;
        }

        .notice {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.42);
            border-radius: 14px;
            color: #fcd34d;
            font-size: 14px;
            line-height: 1.65;
            padding: 17px;
            margin-top: 18px;
            margin-bottom: 20px;
        }

        div.stButton > button {
            width: 100%;
            min-height: 49px;
            border-radius: 11px;
            border: 1px solid #38bdf8;
            background: linear-gradient(90deg, #0284c7, #06b6d4);
            color: white;
            font-weight: 850;
            letter-spacing: 1px;
        }

        div.stButton > button:hover {
            border-color: #67e8f9;
            box-shadow:
                0 0 12px rgba(34, 211, 238, 0.55),
                0 0 25px rgba(2, 132, 199, 0.30);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #334155;
            border-radius: 14px;
            overflow: hidden;
        }

        .stCaption {
            color: #64748b !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# DADOS RECEBIDOS DA HOME
# ==================================================
aparelho = st.session_state.get("aparelho")
peso = st.session_state.get("peso")

if not aparelho or peso is None or float(peso) <= 0:
    st.warning("Nenhum equipamento válido foi enviado para análise.")

    if st.button("VOLTAR PARA A HOME"):
        st.switch_page("pages/01_Home.py")

    st.stop()

nome_aparelho = str(aparelho).strip()
massa_informada = float(peso)
nome_aparelho_seguro = escape(nome_aparelho)


# ==================================================
# CABEÇALHO
# ==================================================
st.markdown(
    '<div class="page-title">ANÁLISE DO EQUIPAMENTO</div>'
    '<div class="page-subtitle">'
    'Identificação técnica, estimativa de composição e apoio à '
    'decisão de logística reversa.'
    '</div>',
    unsafe_allow_html=True,
)


# ==================================================
# ENTRADA DO USUÁRIO
# ==================================================
col_aparelho, col_massa = st.columns(2)

with col_aparelho:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">EQUIPAMENTO INFORMADO</div>'
        f'<div class="main-value">{nome_aparelho_seguro}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_massa:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">MASSA MEDIDA</div>'
        f'<div class="main-value">{massa_informada:.2f} g</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# CONSULTA EXTERNA
# ==================================================
consulta = None
erro_consulta = None

with st.spinner("Consultando informações técnicas do equipamento..."):
    try:
        consulta = consultar_api(nome_aparelho)

    except (ValueError, MobileAPIError) as erro:
        erro_consulta = str(erro)

    except Exception as erro:
        erro_consulta = (
            "Ocorreu um erro inesperado durante a consulta externa: "
            f"{type(erro).__name__}"
        )

melhor_resultado = selecionar_melhor_resultado(
    consulta,
    nome_aparelho,
)


# ==================================================
# DEFINIÇÃO DA CATEGORIA
# ==================================================
if melhor_resultado:
    categoria_api = str(
        melhor_resultado.get("device_type") or ""
    ).strip()

    categoria_interna = identificar_categoria_por_nome(
        nome_aparelho
    )

    # Quando a API retorna categoria válida, ela tem prioridade.
    if categoria_api:
        categoria_analise = categoria_api
        origem_categoria = "MobileAPI"
    else:
        categoria_analise = categoria_interna
        origem_categoria = "Motor interno do CHIPPER"

else:
    categoria_analise = identificar_categoria_por_nome(
        nome_aparelho
    )
    origem_categoria = "Motor interno do CHIPPER"


# ==================================================
# MOTOR DE ANÁLISE
# ==================================================
try:
    analise_estimada = estimar_analise(
        categoria=categoria_analise,
        massa_g=massa_informada,
    )
except ValueError as erro:
    st.error(str(erro))
    st.stop()


# ==================================================
# ORIGEM DOS DADOS
# ==================================================
if erro_consulta:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-error">'
        'Consulta externa indisponível'
        '</div>'
        f'<div class="small-text">{escape(erro_consulta)}</div>'
        '<div class="small-text">'
        'A análise estimada foi mantida pelo motor interno do CHIPPER.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

elif melhor_resultado:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-success">Sistema híbrido ativo</div>'
        '<div class="small-text">'
        'Ficha técnica obtida pela MobileAPI. Componentes, materiais '
        'e recomendações calculados pelo motor interno do CHIPPER.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-warning">'
        'Equipamento não localizado na MobileAPI'
        '</div>'
        '<div class="small-text">'
        'A categoria foi identificada pelo motor interno do CHIPPER '
        'e a análise estimada continuará normalmente.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# FICHA TÉCNICA
# ==================================================
if melhor_resultado:
    st.markdown(
        '<div class="section-title">Ficha técnica</div>',
        unsafe_allow_html=True,
    )

    fabricante = valor_seguro(
        melhor_resultado,
        "manufacturer_name",
    )
    modelo = valor_seguro(
        melhor_resultado,
        "name",
    )
    categoria_api_exibicao = traduzir_categoria(
        str(melhor_resultado.get("device_type") or "")
    )
    armazenamento = valor_seguro(
        melhor_resultado,
        "storage",
    )
    tela = valor_seguro(
        melhor_resultado,
        "screen_resolution",
    )
    peso_referencia = valor_seguro(
        melhor_resultado,
        "weight",
    )
    bateria = valor_seguro(
        melhor_resultado,
        "battery_capacity",
    )
    hardware = valor_seguro(
        melhor_resultado,
        "hardware",
    )
    lancamento = valor_seguro(
        melhor_resultado,
        "release_date",
    )
    modelo_numeros = valor_seguro(
        melhor_resultado,
        "model_numbers",
    )

    ficha_1, ficha_2, ficha_3 = st.columns(3)

    with ficha_1:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">FABRICANTE</div>'
            f'<div class="technical-value">{fabricante}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with ficha_2:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">MODELO LOCALIZADO</div>'
            f'<div class="technical-value">{modelo}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with ficha_3:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">CATEGORIA</div>'
            f'<div class="technical-value">'
            f'{escape(categoria_api_exibicao)}'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    ficha_4, ficha_5, ficha_6 = st.columns(3)

    with ficha_4:
        sufixo_peso = (
            ""
            if peso_referencia.lower().endswith("g")
            else " g"
        )

        st.markdown(
            '<div class="card">'
            '<div class="card-title">PESO DE REFERÊNCIA</div>'
            f'<div class="technical-value">'
            f'{peso_referencia}{sufixo_peso}'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with ficha_5:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">BATERIA</div>'
            f'<div class="technical-value">{bateria}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with ficha_6:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">LANÇAMENTO</div>'
            f'<div class="technical-value">{lancamento}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    ficha_7, ficha_8 = st.columns(2)

    with ficha_7:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">ARMAZENAMENTO</div>'
            f'<div class="technical-value">{armazenamento}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with ficha_8:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">TELA</div>'
            f'<div class="technical-value">{tela}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">HARDWARE</div>'
        f'<div class="technical-value">{hardware}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Informações complementares do modelo"):
        st.write("Códigos e variações:", modelo_numeros)

else:
    st.markdown(
        '<div class="section-title">Identificação interna</div>',
        unsafe_allow_html=True,
    )

    categoria_exibicao = escape(
        str(
            analise_estimada.get(
                "categoria_exibicao",
                "Equipamento eletrônico",
            )
        )
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">CATEGORIA IDENTIFICADA</div>'
        f'<div class="main-value">{categoria_exibicao}</div>'
        '<div class="small-text">'
        'Categoria definida por palavras-chave e regras internas '
        'do CHIPPER.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# COMPONENTES ESTIMADOS
# ==================================================
st.markdown(
    '<div class="section-title">Componentes estimados</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="estimated-badge">RESULTADOS ESTIMADOS</div>',
    unsafe_allow_html=True,
)

componentes = analise_estimada.get("componentes", [])

if componentes:
    componentes_html = montar_lista_html(componentes)

    st.markdown(
        '<div class="card">'
        '<div class="card-title">COMPONENTES PROVÁVEIS</div>'
        f'{componentes_html}'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning(
        "Não existe um perfil de componentes para esta categoria."
    )


# ==================================================
# MATERIAIS ESTIMADOS
# ==================================================
st.markdown(
    '<div class="section-title">'
    'Materiais potencialmente recuperáveis'
    '</div>',
    unsafe_allow_html=True,
)

materiais = analise_estimada.get("materiais", [])

if materiais:
    tabela_materiais = []

    for item in materiais:
        tabela_materiais.append(
            {
                "Material": item.get(
                    "material",
                    "Não informado",
                ),
                "Massa estimada (g)": round(
                    float(item.get("massa_estimada_g", 0.0)),
                    4,
                ),
                "Participação estimada (%)": round(
                    float(
                        item.get(
                            "percentual_estimado",
                            0.0,
                        )
                    ),
                    3,
                ),
            }
        )

    st.dataframe(
        tabela_materiais,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.warning(
        "Não foi possível estimar os materiais desta categoria."
    )


# ==================================================
# POTENCIAL DE RECUPERAÇÃO
# ==================================================
st.markdown(
    '<div class="section-title">'
    'Potencial de recuperação'
    '</div>',
    unsafe_allow_html=True,
)

massa_recuperavel = float(
    analise_estimada.get(
        "massa_recuperavel_g",
        0.0,
    )
)

percentual_recuperavel = float(
    analise_estimada.get(
        "percentual_recuperavel",
        0.0,
    )
)

recuperacao_1, recuperacao_2 = st.columns(2)

with recuperacao_1:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">'
        'MASSA POTENCIALMENTE RECUPERÁVEL'
        '</div>'
        f'<div class="metric-value">'
        f'{massa_recuperavel:.2f} g'
        '</div>'
        '<div class="metric-label">'
        'Estimativa baseada na massa medida.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with recuperacao_2:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">'
        'PERCENTUAL POTENCIALMENTE RECUPERÁVEL'
        '</div>'
        f'<div class="metric-value">'
        f'{percentual_recuperavel:.2f}%'
        '</div>'
        '<div class="metric-label">'
        'Percentual aproximado do perfil da categoria.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# RECOMENDAÇÕES
# ==================================================
st.markdown(
    '<div class="section-title">'
    'Recomendação de logística reversa'
    '</div>',
    unsafe_allow_html=True,
)

recomendacoes = analise_estimada.get(
    "recomendacoes",
    [],
)

if recomendacoes:
    recomendacoes_html = montar_lista_html(recomendacoes)

    st.markdown(
        '<div class="card">'
        '<div class="card-title">DESTINO RECOMENDADO</div>'
        f'{recomendacoes_html}'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# AVISO TÉCNICO
# ==================================================
observacao = escape(
    str(
        analise_estimada.get(
            "observacao",
            "Os resultados apresentados são estimativas.",
        )
    )
)

st.markdown(
    '<div class="notice">'
    '<strong>Aviso técnico:</strong> '
    f'{observacao} '
    'A composição exata do equipamento exige desmontagem física, '
    'pesagem individual dos componentes ou análise laboratorial.'
    '</div>',
    unsafe_allow_html=True,
)


# ==================================================
# VALOR ECONÔMICO — PRÓXIMA ETAPA
# ==================================================
st.markdown(
    '<div class="section-title">'
    'Valor econômico estimado'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="card">'
    '<div class="card-title">MÓDULO ECONÔMICO</div>'
    '<div class="source-warning">Aguardando integração de preços</div>'
    '<div class="small-text">'
    'Na próxima etapa, o CHIPPER calculará o preço por grama '
    'e o valor potencial dos materiais recuperáveis.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ==================================================
# FONTE
# ==================================================
st.caption(
    "Ficha técnica: MobileAPI, quando disponível. "
    "Componentes, materiais, massas e recomendações: "
    "estimativas do motor CHIPPER."
)


# ==================================================
# BOTÕES
# ==================================================
col_voltar, col_exportar = st.columns(2)

with col_voltar:
    if st.button("NOVA ANÁLISE"):
        st.session_state.pop("aparelho", None)
        st.session_state.pop("peso", None)

        st.switch_page("pages/01_home.py")

with col_exportar:
    st.button(
        "EXPORTAR CSV",
        disabled=True,
        help=(
            "A exportação será ativada depois da integração "
            "do módulo econômico."
        ),
    )
