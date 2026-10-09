"""
Gestor de Investimentos B3
---------------------------
Streamlit + Pandas + Supabase + Brapi (cotações em tempo real)
"""

import os
from datetime import datetime, date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dateutil.relativedelta import relativedelta
from supabase import create_client, Client

# ══════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gestor de Investimentos B3",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════
# CONEXÃO SUPABASE
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"❌ Falha ao conectar ao Supabase: {e}")
    st.stop()

BRAPI_TOKEN = st.secrets["brapi"]["token"]

# ══════════════════════════════════════════════════════════════════════
# FUNÇÕES DE API (BRAPI)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def get_cotacao(ticker: str) -> float:
    """Retorna a cotação atual do ticker via Brapi (cache 5 min)."""
    if not ticker:
        return 0.0
    try:
        url = f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if "results" in data and data["results"]:
            return float(data["results"][0].get("regularMarketPrice") or 0.0)
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=3600, show_spinner=False)
def get_dividendos(ticker: str, tipo: str = "acao") -> pd.DataFrame:
    """Retorna histórico de dividendos via Brapi (cache 1h)."""
    if not ticker:
        return pd.DataFrame()
    try:
        if tipo == "acao":
            url = (
                f"https://brapi.dev/api/v2/stocks/dividends"
                f"?ticker={ticker}&token={BRAPI_TOKEN}"
            )
        else:
            url = (
                f"https://brapi.dev/api/v2/fii/dividends"
                f"?ticker={ticker}&token={BRAPI_TOKEN}"
            )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        dividends = data.get("dividends", [])
        if not dividends:
            return pd.DataFrame()
        df = pd.DataFrame(dividends)
        # Normaliza campos possíveis
        if "rate" in df.columns:
            df["rate"] = pd.to_numeric(df["rate"], errors="coerce").fillna(0)
        if "paymentDate" in df.columns:
            df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


def calcular_dy_12m(ticker: str, tipo: str) -> float:
    """Dividend Yield dos últimos 12 meses com base no histórico real."""
    df = get_dividendos(ticker, tipo)
    if df.empty or "rate" not in df.columns:
        return 0.0

    df = df.copy()
    df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
    corte = pd.Timestamp.now() - pd.DateOffset(months=12)
    df_12m = df[df["paymentDate"] >= corte]

    total_pago = df_12m["rate"].sum() if not df_12m.empty else df["rate"].tail(12).sum()
    preco = get_cotacao(ticker)
    if preco <= 0:
        return 0.0
    return float(total_pago / preco)


# ══════════════════════════════════════════════════════════════════════
# FUNÇÕES DE BANCO (SUPABASE)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=15, show_spinner=False)
def carregar_ativos(tabela: str) -> pd.DataFrame:
    try:
        resp = supabase.table(tabela).select("*").order("ticker").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar {tabela}: {e}")
        return pd.DataFrame()


def salvar_ativo(tabela: str, dados: dict) -> None:
    supabase.table(tabela).insert(dados).execute()
    carregar_ativos.clear()


def atualizar_ativo(tabela: str, id_: int, dados: dict) -> None:
    dados["updated_at"] = datetime.now().isoformat()
    supabase.table(tabela).update(dados).eq("id", id_).execute()
    carregar_ativos.clear()


def deletar_ativo(tabela: str, id_: int) -> None:
    supabase.table(tabela).delete().eq("id", id_).execute()
    carregar_ativos.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_config() -> dict:
    try:
        resp = supabase.table("config").select("*").eq("id", 1).execute()
        if resp.data:
            return resp.data[0]
    except Exception:
        pass
    return {"valor_disponivel": 0.0}


def atualizar_config(valor: float) -> None:
    supabase.table("config").upsert(
        {
            "id": 1,
            "valor_disponivel": float(valor),
            "updated_at": datetime.now().isoformat(),
        }
    ).execute()
    carregar_config.clear()


# ══════════════════════════════════════════════════════════════════════
# ENRIQUECIMENTO COM COTAÇÕES
# ══════════════════════════════════════════════════════════════════════
def enriquecer(df: pd.DataFrame, tipo: str = "acao") -> pd.DataFrame:
    """Adiciona cotação atual, valor investido, valor atual e rentabilidade."""
    if df.empty:
        return df

    df = df.copy()
    df["cotacao_atual"] = df["ticker"].apply(get_cotacao)
    df["valor_investido"] = df["quantidade"] * df["preco_medio"]
    df["valor_atual"] = df["quantidade"] * df["cotacao_atual"]
    df["rentabilidade_%"] = np.where(
        df["valor_investido"] > 0,
        ((df["valor_atual"] / df["valor_investido"]) - 1) * 100,
        0.0,
    )
    df["lucro_prejuizo"] = df["valor_atual"] - df["valor_investido"]

    # DY individual (cacheado internamente)
    df["dy_12m_%"] = df["ticker"].apply(lambda t: calcular_dy_12m(t, tipo) * 100)

    return df


# ══════════════════════════════════════════════════════════════════════
# PROJEÇÕES DE DIVIDENDOS / JUROS COMPOSTOS
# ══════════════════════════════════════════════════════════════════════
def projetar_dividendos(
    valor_inicial: float,
    dy_anual: float,
    meses: int = 24,
    aporte_mensal: float = 0.0,
    reinvestir: bool = True,
) -> pd.DataFrame:
    """
    Projeta o patrimônio mês a mês aplicando juros compostos
    sobre o reinvestimento de dividendos.
    """
    dy_mensal = (1 + dy_anual) ** (1 / 12) - 1 if dy_anual > 0 else 0.0
    registros = []
    patrimonio = float(valor_inicial)
    dividendo_acumulado = 0.0
    total_investido = float(valor_inicial)

    for mes in range(1, meses + 1):
        dividendos = patrimonio * dy_mensal
        dividendo_acumulado += dividendos

        if reinvestir:
            patrimonio += dividendos
            patrimonio += aporte_mensal
        else:
            patrimonio += aporte_mensal

        total_investido += aporte_mensal

        registros.append(
            {
                "Mês": mes,
                "Dividendos do mês (R$)": round(dividendos, 2),
                "Dividendos acumulados (R$)": round(dividendo_acumulado, 2),
                "Patrimônio (R$)": round(patrimonio, 2),
                "Total investido (R$)": round(total_investido, 2),
            }
        )

    return pd.DataFrame(registros)


# ══════════════════════════════════════════════════════════════════════
# GRÁFICOS
# ══════════════════════════════════════════════════════════════════════
def grafico_pizza(df_acoes: pd.DataFrame, df_fiis: pd.DataFrame):
    dados = []
    if not df_acoes.empty:
        for _, r in df_acoes.iterrows():
            dados.append(
                {"Ativo": r["ticker"], "Valor": r["valor_atual"], "Tipo": "Ação"}
            )
    if not df_fiis.empty:
        for _, r in df_fiis.iterrows():
            dados.append(
                {"Ativo": r["ticker"], "Valor": r["valor_atual"], "Tipo": "FII"}
            )

    if not dados:
        st.info("Cadastre ativos para visualizar a distribuição.")
        return

    df_plot = pd.DataFrame(dados)
    fig = px.pie(
        df_plot,
        names="Ativo",
        values="Valor",
        color="Tipo",
        hole=0.45,
        title="Distribuição da Carteira por Ativo",
        color_discrete_map={"Ação": "#2E86C1", "FII": "#28B463"},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def grafico_barras(df_acoes: pd.DataFrame, df_fiis: pd.DataFrame):
    dados = []
    if not df_acoes.empty:
        for _, r in df_acoes.iterrows():
            dados.append(
                {
                    "Ativo": r["ticker"],
                    "Rentabilidade (%)": r["rentabilidade_%"],
                    "Tipo": "Ação",
                }
            )
    if not df_fiis.empty:
        for _, r in df_fiis.iterrows():
            dados.append(
                {
                    "Ativo": r["ticker"],
                    "Rentabilidade (%)": r["rentabilidade_%"],
                    "Tipo": "FII",
                }
            )
    if not dados:
        return
    df_plot = pd.DataFrame(dados)
    fig = px.bar(
        df_plot,
        x="Ativo",
        y="Rentabilidade (%)",
        color="Tipo",
        title="Rentabilidade por Ativo",
        text_auto=".2f",
        color_discrete_map={"Ação": "#2E86C1", "FII": "#28B463"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def grafico_projecao(df_proj: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_proj["Mês"],
            y=df_proj["Patrimônio (R$)"],
            mode="lines+markers",
            name="Patrimônio com reinvestimento",
            line=dict(color="#28B463", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_proj["Mês"],
            y=df_proj["Dividendos acumulados (R$)"],
            mode="lines+markers",
            name="Dividendos acumulados",
            line=dict(color="#F39C12", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_proj["Mês"],
            y=df_proj["Total investido (R$)"],
            mode="lines",
            name="Total investido",
            line=dict(color="#7F8C8D", width=1, dash="dot"),
        )
    )
    fig.update_layout(
        title="Evolução do Patrimônio com Juros Compostos",
        xaxis_title="Mês",
        yaxis_title="R$",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📊 Menu")
    st.markdown("---")

    cfg = carregar_config()
    st.metric("💰 Disponível para aporte", f"R$ {cfg.get('valor_disponivel', 0):,.2f}")

    novo_valor = st.number_input(
        "Atualizar valor disponível (R$)",
        min_value=0.0,
        value=float(cfg.get("valor_disponivel", 0.0)),
        step=100.0,
        format="%.2f",
        key="input_valor_disponivel",
    )
    if st.button("💾 Salvar valor", use_container_width=True):
        atualizar_config(novo_valor)
        st.success("Valor atualizado!")
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Atualizar cotações", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


# ══════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ══════════════════════════════════════════════════════════════════════
st.title("📊 Gestor de Investimentos – Ações e FIIs")
st.caption("Cotações em tempo real via Brapi • Persistência no Supabase")

# ══════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════
aba_carteira, aba_cadastro, aba_editar, aba_projecoes = st.tabs(
    ["📋 Carteira", "➕ Novo Ativo", "✏️ Editar / Excluir", "📈 Projeções"]
)

# ── ABA CARTEIRA ───────────────────────────────────────────────────────
with aba_carteira:
    st.subheader("Ações")
    df_acoes = enriquecer(carregar_ativos("acoes"), "acao")
    if df_acoes.empty:
        st.info("Nenhuma ação cadastrada.")
    else:
        colunas = [
            "ticker", "quantidade", "preco_medio", "cotacao_atual",
            "valor_investido", "valor_atual", "lucro_prejuizo",
            "rentabilidade_%", "dy_12m_%",
        ]
        st.dataframe(
            df_acoes[colunas].style.format(
                {
                    "preco_medio": "R$ {:.2f}",
                    "cotacao_atual": "R$ {:.2f}",
                    "valor_investido": "R$ {:.2f}",
                    "valor_atual": "R$ {:.2f}",
                    "lucro_prejuizo": "R$ {:.2f}",
                    "rentabilidade_%": "{:.2f}%",
                    "dy_12m_%": "{:.2f}%",
                }
            ),
            use_container_width=True,
        )
        total_acoes = df_acoes["valor_atual"].sum()
        st.markdown(f"**Total em ações: R$ {total_acoes:,.2f}**")

    st.markdown("---")
    st.subheader("Fundos Imobiliários")
    df_fiis = enriquecer(carregar_ativos("fiis"), "fii")
    if df_fiis.empty:
        st.info("Nenhum FII cadastrado.")
    else:
        colunas = [
            "ticker", "quantidade", "preco_medio", "cotacao_atual",
            "valor_investido", "valor_atual", "lucro_prejuizo",
            "rentabilidade_%", "dy_12m_%",
        ]
        st.dataframe(
            df_fiis[colunas].style.format(
                {
                    "preco_medio": "R$ {:.2f}",
                    "cotacao_atual": "R$ {:.2f}",
                    "valor_investido": "R$ {:.2f}",
                    "valor_atual": "R$ {:.2f}",
                    "lucro_prejuizo": "R$ {:.2f}",
                    "rentabilidade_%": "{:.2f}%",
                    "dy_12m_%": "{:.2f}%",
                }
            ),
            use_container_width=True,
        )
        total_fiis = df_fiis["valor_atual"].sum()
        st.markdown(f"**Total em FIIs: R$ {total_fiis:,.2f}**")

    st.markdown("---")
    # Totais gerais
    total_geral = (
        (df_acoes["valor_atual"].sum() if not df_acoes.empty else 0)
        + (df_fiis["valor_atual"].sum() if not df_fiis.empty else 0)
    )
    investido_geral = (
        (df_acoes["valor_investido"].sum() if not df_acoes.empty else 0)
        + (df_fiis["valor_investido"].sum() if not df_fiis.empty else 0)
    )
    lucro_geral = total_geral - investido_geral
    rent_geral = (lucro_geral / investido_geral * 100) if investido_geral > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patrimônio total", f"R$ {total_geral:,.2f}")
    c2.metric("Total investido", f"R$ {investido_geral:,.2f}")
    c3.metric("Lucro/Prejuízo", f"R$ {lucro_geral:,.2f}")
    c4.metric("Rentabilidade", f"{rent_geral:.2f}%")

    st.markdown("---")
    grafico_pizza(df_acoes, df_fiis)
    grafico_barras(df_acoes, df_fiis)


# ── ABA CADASTRO ───────────────────────────────────────────────────────
with aba_cadastro:
    st.subheader("Cadastrar novo ativo")
    with st.form("form_novo_ativo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de ativo", ["Ação", "FII"])
            ticker = st.text_input("Ticker (ex: PETR4, MXRF11)").upper().strip()
            quantidade = st.number_input("Quantidade", min_value=1, step=1, value=100)
        with c2:
            preco_medio = st.number_input(
                "Preço médio (R$)", min_value=0.01, step=0.01, format="%.2f"
            )
            data_compra = st.date_input("Data da compra", value=date.today())

        submitted = st.form_submit_button("💾 Salvar ativo", use_container_width=True)

        if submitted:
            if not ticker:
                st.error("Informe o ticker.")
            else:
                tabela = "acoes" if tipo == "Ação" else "fiis"
                try:
                    salvar_ativo(
                        tabela,
                        {
                            "ticker": ticker,
                            "quantidade": int(quantidade),
                            "preco_medio": float(preco_medio),
                            "data_compra": str(data_compra),
                        },
                    )
                    st.success(f"✅ {tipo} {ticker} cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")


# ── ABA EDITAR / EXCLUIR ───────────────────────────────────────────────
with aba_editar:
    st.subheader("Editar ou excluir ativos")
    tipo_edit = st.radio("Selecione a tabela", ["Ações", "FIIs"], horizontal=True)
    tabela = "acoes" if tipo_edit == "Ações" else "fiis"

    df_edit = carregar_ativos(tabela)
    if df_edit.empty:
        st.info("Nada para editar.")
    else:
        opcoes = {
            f"ID {row['id']} – {row['ticker']} ({row['quantidade']} un.)": row["id"]
            for _, row in df_edit.iterrows()
        }
        selecionado = st.selectbox("Escolha o ativo", list(opcoes.keys()))
        id_sel = opcoes[selecionado]
        registro = df_edit[df_edit["id"] == id_sel].iloc[0]

        with st.form("form_editar"):
            c1, c2 = st.columns(2)
            with c1:
                nova_qtd = st.number_input(
                    "Quantidade", min_value=1, step=1, value=int(registro["quantidade"])
                )
                novo_ticker = st.text_input("Ticker", value=registro["ticker"])
            with c2:
                novo_preco = st.number_input(
                    "Preço médio (R$)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    value=float(registro["preco_medio"]),
                )
                nova_data = st.date_input(
                    "Data da compra",
                    value=pd.to_datetime(registro.get("data_compra") or date.today()).date(),
                )

            col_a, col_b = st.columns(2)
            btn_atualizar = col_a.form_submit_button("✏️ Atualizar", use_container_width=True)
            btn_excluir = col_b.form_submit_button("🗑️ Excluir", use_container_width=True)

            if btn_atualizar:
                try:
                    atualizar_ativo(
                        tabela,
                        id_sel,
                        {
                            "ticker": novo_ticker.upper().strip(),
                            "quantidade": int(nova_qtd),
                            "preco_medio": float(novo_preco),
                            "data_compra": str(nova_data),
                        },
                    )
                    st.success("Atualizado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            if btn_excluir:
                try:
                    deletar_ativo(tabela, id_sel)
                    st.success("Excluído com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")


# ── ABA PROJEÇÕES ──────────────────────────────────────────────────────
with aba_projecoes:
    st.subheader("Projeção de dividendos com reinvestimento (juros compostos)")

    cfg = carregar_config()
    df_acoes_p = carregar_ativos("acoes")
    df_fiis_p = carregar_ativos("fiis")

    # Calcula DY médio ponderado da carteira (fallback)
    dy_estimado = 0.0
    try:
        dyn_acoes = [calcular_dy_12m(t, "acao") for t in df_acoes_p.get("ticker", [])]
        dyn_fiis = [calcular_dy_12m(t, "fii") for t in df_fiis_p.get("ticker", [])]
        todos = [d for d in (dyn_acoes + dyn_fiis) if d > 0]
        if todos:
            dy_estimado = sum(todos) / len(todos)
    except Exception:
        dy_estimado = 0.08

    if dy_estimado == 0:
        dy_estimado = 0.08  # fallback 8% a.a.

    c1, c2 = st.columns(2)
    with c1:
        patrimonio_inicial = st.number_input(
            "Patrimônio inicial (R$)",
            min_value=0.0,
            value=float(cfg.get("valor_disponivel", 0.0) or 10000.0),
            step=1000.0,
            format="%.2f",
        )
        dy_input = st.slider(
            "Dividend Yield anual esperado (%)",
            min_value=0.0,
            max_value=25.0,
            value=float(dy_estimado * 100),
            step=0.25,
        )
    with c2:
        meses = st.slider("Horizonte (meses)", 6, 240, 24, step=6)
        aporte_mensal = st.number_input(
            "Aporte mensal adicional (R$)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
        )

    reinvestir = st.checkbox("Reinvestir dividendos (juros compostos)", value=True)

    if st.button("🚀 Gerar projeção", use_container_width=True):
        df_proj = projetar_dividendos(
            valor_inicial=patrimonio_inicial,
            dy_anual=dy_input / 100.0,
            meses=meses,
            aporte_mensal=aporte_mensal,
            reinvestir=reinvestir,
        )

        final = df_proj.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Patrimônio final", f"R$ {final['Patrimônio (R$)']:,.2f}")
        c2.metric("Dividendos acumulados", f"R$ {final['Dividendos acumulados (R$)']:,.2f}")
        c3.metric("Total investido", f"R$ {final['Total investido (R$)']:,.2f}")
        rendimento = final["Patrimônio (R$)"] - final["Total investido (R$)"]
        c4.metric("Rendimento total", f"R$ {rendimento:,.2f}")

        grafico_projecao(df_proj)

        with st.expander("📄 Ver tabela detalhada mês a mês"):
            st.dataframe(
                df_proj.style.format(
                    {
                        "Dividendos do mês (R$)": "R$ {:.2f}",
                        "Dividendos acumulados (R$)": "R$ {:.2f}",
                        "Patrimônio (R$)": "R$ {:.2f}",
                        "Total investido (R$)": "R$ {:.2f}",
                    }
                ),
                use_container_width=True,
                height=400,
            )

    st.markdown("---")
    st.subheader("📍 Dividend Yield histórico por ativo (últimos 12 meses)")
    todos_tickers = []
    if not df_acoes_p.empty:
        todos_tickers += [("Ação", t) for t in df_acoes_p["ticker"]]
    if not df_fiis_p.empty:
        todos_tickers += [("FII", t) for t in df_fiis_p["ticker"]]

    if todos_tickers:
        with st.spinner("Consultando histórico de dividendos na Brapi..."):
            linhas = []
            for tipo_t, tk in todos_tickers:
                dy = calcular_dy_12m(tk, "acao" if tipo_t == "Ação" else "fii") * 100
                preco = get_cotacao(tk)
                linhas.append(
                    {"Ticker": tk, "Tipo": tipo_t, "Preço atual (R$)": preco, "DY 12m (%)": dy}
                )
            st.dataframe(
                pd.DataFrame(linhas).style.format(
                    {"Preço atual (R$)": "R$ {:.2f}", "DY 12m (%)": "{:.2f}%"}
                ),
                use_container_width=True,
            )
    else:
        st.info("Cadastre ativos para visualizar o DY histórico.")