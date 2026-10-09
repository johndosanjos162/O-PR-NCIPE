"""
🎨 Gestor de Investimentos B3 — Edição Premium
Streamlit + Pandas + Supabase + Brapi (cotações em tempo real)
"""

import io
from datetime import datetime, date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from supabase import create_client, Client

# ══════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gestor Premium B3",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════
# CSS CUSTOMIZADO — DESIGN PREMIUM
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    /* Reset geral */
    .main { background: radial-gradient(circle at top left, #0B1220 0%, #060B14 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }

    /* Header com gradiente */
    .hero {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 50%, #7B61FF 100%);
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(0, 229, 160, 0.15);
        display: flex; align-items: center; justify-content: space-between;
    }
    .hero h1 { color: #060B14; font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .hero p  { color: #060B14; opacity: 0.75; margin: 4px 0 0 0; font-size: 14px; font-weight: 500; }
    .hero .badge {
        background: rgba(6, 11, 20, 0.85); color: #00E5A0;
        padding: 10px 18px; border-radius: 12px; font-weight: 700;
        font-size: 13px; letter-spacing: 0.5px;
    }

    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(145deg, #131C2F 0%, #0F1729 100%);
        border: 1px solid rgba(0, 229, 160, 0.12);
        padding: 20px 22px;
        border-radius: 16px;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(180deg, #00E5A0, #00A8E8);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 229, 160, 0.35);
        box-shadow: 0 12px 28px rgba(0, 229, 160, 0.12);
    }
    .metric-card .label { color: #7A8699; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }
    .metric-card .value { color: #E6EDF7; font-size: 26px; font-weight: 800; margin-top: 6px; }
    .metric-card .delta { font-size: 13px; font-weight: 600; margin-top: 4px; }
    .delta.up   { color: #00E5A0; }
    .delta.down { color: #FF5C7A; }
    .delta.neutral { color: #7A8699; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220 0%, #060B14 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
        color: #060B14; font-weight: 700; border: none;
        border-radius: 10px; padding: 10px 16px;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 229, 160, 0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: transparent; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background: #131C2F; border-radius: 12px 12px 0 0; padding: 10px 20px;
        color: #7A8699; font-weight: 600; border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,229,160,0.15), rgba(0,168,232,0.1));
        color: #00E5A0 !important;
        border-bottom: 2px solid #00E5A0;
    }

    /* Botões gerais */
    .stButton > button {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
        color: #060B14; font-weight: 700; border: none; border-radius: 10px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 229, 160, 0.25);
    }

    /* Dataframes */
    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background: #131C2F !important; border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important; color: #E6EDF7 !important;
    }

    /* Section title */
    .section-title {
        font-size: 18px; font-weight: 700; color: #E6EDF7;
        margin: 24px 0 12px 0; padding-left: 12px;
        border-left: 3px solid #00E5A0;
    }

    /* Pills de tags */
    .pill {
        display: inline-block; padding: 4px 12px; border-radius: 999px;
        font-size: 11px; font-weight: 700; letter-spacing: 0.4px;
    }
    .pill.acao { background: rgba(0, 168, 232, 0.15); color: #00A8E8; }
    .pill.fii  { background: rgba(0, 229, 160, 0.15); color: #00E5A0; }

    /* Esconde branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════
# CONEXÃO SUPABASE
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def init_supabase() -> Client:
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])


try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"❌ Falha ao conectar ao Supabase: {e}")
    st.stop()

BRAPI_TOKEN = st.secrets["brapi"]["token"]

# ══════════════════════════════════════════════════════════════════════
# APIs (BRAPI)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def get_cotacao(ticker: str) -> float:
    if not ticker:
        return 0.0
    try:
        r = requests.get(
            f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}", timeout=15
        )
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            return float(data["results"][0].get("regularMarketPrice") or 0.0)
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=3600, show_spinner=False)
def get_dividendos(ticker: str, tipo: str = "acao") -> pd.DataFrame:
    if not ticker:
        return pd.DataFrame()
    try:
        endpoint = "stocks" if tipo == "acao" else "fii"
        r = requests.get(
            f"https://brapi.dev/api/v2/{endpoint}/dividends?ticker={ticker}&token={BRAPI_TOKEN}",
            timeout=15,
        )
        r.raise_for_status()
        df = pd.DataFrame(r.json().get("dividends", []))
        if df.empty:
            return df
        if "rate" in df.columns:
            df["rate"] = pd.to_numeric(df["rate"], errors="coerce").fillna(0)
        if "paymentDate" in df.columns:
            df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


def calcular_dy_12m(ticker: str, tipo: str) -> float:
    df = get_dividendos(ticker, tipo)
    if df.empty or "rate" not in df.columns:
        return 0.0
    corte = pd.Timestamp.now() - pd.DateOffset(months=12)
    df_12m = df[df["paymentDate"] >= corte] if "paymentDate" in df.columns else df
    total = (df_12m if not df_12m.empty else df.tail(12))["rate"].sum()
    preco = get_cotacao(ticker)
    return float(total / preco) if preco > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════
# BANCO (SUPABASE)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=15, show_spinner=False)
def carregar_ativos(tabela: str) -> pd.DataFrame:
    try:
        resp = supabase.table(tabela).select("*").order("ticker").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar {tabela}: {e}")
        return pd.DataFrame()


def salvar_ativo(tabela: str, dados: dict):
    supabase.table(tabela).insert(dados).execute()
    carregar_ativos.clear()


def atualizar_ativo(tabela: str, id_: int, dados: dict):
    dados["updated_at"] = datetime.now().isoformat()
    supabase.table(tabela).update(dados).eq("id", id_).execute()
    carregar_ativos.clear()


def deletar_ativo(tabela: str, id_: int):
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
    return {"valor_disponivel": 0.0, "meta_renda_passiva": 0.0}


def atualizar_config(valor=None, meta=None):
    payload = {"id": 1, "updated_at": datetime.now().isoformat()}
    if valor is not None:
        payload["valor_disponivel"] = float(valor)
    if meta is not None:
        payload["meta_renda_passiva"] = float(meta)
    supabase.table("config").upsert(payload).execute()
    carregar_config.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_aportes() -> pd.DataFrame:
    try:
        resp = supabase.table("aportes").select("*").order("data", desc=True).execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def registrar_aporte(ticker, tipo, qtd, preco, data_):
    supabase.table("aportes").insert(
        {
            "ticker": ticker,
            "tipo": tipo,
            "quantidade": int(qtd),
            "preco": float(preco),
            "total": float(qtd) * float(preco),
            "data": str(data_),
        }
    ).execute()
    carregar_aportes.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_watchlist() -> pd.DataFrame:
    try:
        resp = supabase.table("watchlist").select("*").order("ticker").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def salvar_watchlist(ticker, tipo, preco_alvo, obs):
    supabase.table("watchlist").insert(
        {
            "ticker": ticker,
            "tipo": tipo,
            "preco_alvo": float(preco_alvo),
            "observacao": obs,
        }
    ).execute()
    carregar_watchlist.clear()


def deletar_watchlist(id_):
    supabase.table("watchlist").delete().eq("id", id_).execute()
    carregar_watchlist.clear()


# ══════════════════════════════════════════════════════════════════════
# ENRIQUECIMENTO
# ══════════════════════════════════════════════════════════════════════
def enriquecer(df: pd.DataFrame, tipo: str = "acao") -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["cotacao_atual"] = df["ticker"].apply(get_cotacao)
    df["valor_investido"] = df["quantidade"] * df["preco_medio"]
    df["valor_atual"] = df["quantidade"] * df["cotacao_atual"]
    df["lucro_prejuizo"] = df["valor_atual"] - df["valor_investido"]
    df["rentabilidade_%"] = np.where(
        df["valor_investido"] > 0,
        (df["valor_atual"] / df["valor_investido"] - 1) * 100,
        0.0,
    )
    df["dy_12m_%"] = df["ticker"].apply(lambda t: calcular_dy_12m(t, tipo) * 100)
    # Preço teto de Bazin: preço = dividendo_anual / 0.06
    df["preco_teto"] = df.apply(
        lambda r: (r["cotacao_atual"] * r["dy_12m_%"] / 100) / 0.06
        if r["cotacao_atual"] > 0 else 0.0,
        axis=1,
    )
    df["abaixo_teto"] = df["cotacao_atual"] <= df["preco_teto"]
    return df


# ══════════════════════════════════════════════════════════════════════
# PROJEÇÕES
# ══════════════════════════════════════════════════════════════════════
def projetar(valor_inicial, dy_anual, meses, aporte_mensal, reinvestir=True):
    dy_m = (1 + dy_anual) ** (1 / 12) - 1 if dy_anual > 0 else 0
    regs, patrimonio, div_acum, inv_total = [], float(valor_inicial), 0.0, float(valor_inicial)
    for m in range(1, meses + 1):
        div = patrimonio * dy_m
        div_acum += div
        patrimonio += div if reinvestir else 0
        patrimonio += aporte_mensal
        inv_total += aporte_mensal
        regs.append(
            {
                "Mês": m,
                "Dividendos do mês": round(div, 2),
                "Dividendos acumulados": round(div_acum, 2),
                "Patrimônio": round(patrimonio, 2),
                "Total investido": round(inv_total, 2),
            }
        )
    return pd.DataFrame(regs)


# ══════════════════════════════════════════════════════════════════════
# COMPONENTES DE UI
# ══════════════════════════════════════════════════════════════════════
def metric_card(label, value, delta=None, delta_type="neutral"):
    delta_html = f'<div class="delta {delta_type}">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def pill(tipo):
    cls = "acao" if tipo == "Ação" else "fii"
    return f'<span class="pill {cls}">{tipo}</span>'


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0 20px 0;">
            <div style="font-size: 40px;">💎</div>
            <div style="font-size: 18px; font-weight: 800; color: #00E5A0; letter-spacing: 0.5px;">
                GESTOR PREMIUM
            </div>
            <div style="font-size: 11px; color: #7A8699; letter-spacing: 1px;">
                B3 · AÇÕES & FIIs
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cfg = carregar_config()

    st.markdown("### 💰 Valor disponível")
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
                    padding: 16px; border-radius: 14px; text-align: center;
                    box-shadow: 0 8px 24px rgba(0, 229, 160, 0.2); margin-bottom: 12px;">
            <div style="color: #060B14; font-size: 12px; font-weight: 700; opacity: 0.75;">
                SALDO PARA APORTE
            </div>
            <div style="color: #060B14; font-size: 26px; font-weight: 900; margin-top: 4px;">
                R$ {cfg.get('valor_disponivel', 0):,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    novo_valor = st.number_input(
        "Atualizar saldo (R$)",
        min_value=0.0,
        value=float(cfg.get("valor_disponivel", 0.0)),
        step=100.0,
        format="%.2f",
        label_visibility="collapsed",
    )
    if st.button("💾 Salvar saldo", use_container_width=True):
        atualizar_config(valor=novo_valor)
        st.success("Saldo atualizado!")
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Sincronizar cotações", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ══════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero">
        <div>
            <h1>💎 Painel de Investimentos</h1>
            <p>Ações · FIIs · Dividendos · Projeções em tempo real</p>
        </div>
        <div class="badge">● MERCADO ATIVO</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════
tabs = st.tabs(
    [
        "📊 Dashboard",
        "➕ Cadastrar",
        "✏️ Gerenciar",
        "📈 Projeções",
        "🎯 Rebalancear",
        "👁️ Watchlist",
        "📜 Aportes",
    ]
)

# ── ABA: DASHBOARD ─────────────────────────────────────────────────────
with tabs[0]:
    df_acoes = enriquecer(carregar_ativos("acoes"), "acao")
    df_fiis = enriquecer(carregar_ativos("fiis"), "fii")

    total_geral = (
        (df_acoes["valor_atual"].sum() if not df_acoes.empty else 0)
        + (df_fiis["valor_atual"].sum() if not df_fiis.empty else 0)
    )
    investido = (
        (df_acoes["valor_investido"].sum() if not df_acoes.empty else 0)
        + (df_fiis["valor_investido"].sum() if not df_fiis.empty else 0)
    )
    lucro = total_geral - investido
    rent = (lucro / investido * 100) if investido > 0 else 0

    # Estimativa de renda passiva (média DY * patrimônio)
    dys = []
    if not df_acoes.empty:
        dys += df_acoes["dy_12m_%"].tolist()
    if not df_fiis.empty:
        dys += df_fiis["dy_12m_%"].tolist()
    dy_medio = np.mean([d for d in dys if d > 0]) if any(d > 0 for d in dys) else 0
    renda_passiva_mensal = (total_geral * dy_medio / 100) / 12

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Patrimônio Total", f"R$ {total_geral:,.2f}")
    with c2:
        metric_card("Total Investido", f"R$ {investido:,.2f}")
    with c3:
        sign = "+" if lucro >= 0 else ""
        metric_card(
            "Lucro / Prejuízo",
            f"R$ {lucro:,.2f}",
            f"{sign}{rent:.2f}%",
            "up" if lucro >= 0 else "down",
        )
    with c4:
        metric_card(
            "Renda Passiva Est.",
            f"R$ {renda_passiva_mensal:,.2f}/mês",
            f"DY médio {dy_medio:.2f}%",
            "neutral",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        section("🥧 Distribuição da Carteira")
        dados = []
        for _, r in df_acoes.iterrows():
            dados.append({"Ativo": r["ticker"], "Valor": r["valor_atual"], "Tipo": "Ação"})
        for _, r in df_fiis.iterrows():
            dados.append({"Ativo": r["ticker"], "Valor": r["valor_atual"], "Tipo": "FII"})

        if dados:
            fig = px.pie(
                pd.DataFrame(dados),
                names="Ativo",
                values="Valor",
                hole=0.55,
                color="Tipo",
                color_discrete_map={"Ação": "#00A8E8", "FII": "#00E5A0"},
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cadastre ativos para visualizar.")

    with col_right:
        section("📊 Comparativo Ações vs FIIs")
        tot_a = df_acoes["valor_atual"].sum() if not df_acoes.empty else 0
        tot_f = df_fiis["valor_atual"].sum() if not df_fiis.empty else 0
        if tot_a + tot_f > 0:
            df_comp = pd.DataFrame(
                {"Classe": ["Ações", "FIIs"], "Valor": [tot_a, tot_f]}
            )
            fig = px.bar(
                df_comp,
                x="Classe",
                y="Valor",
                color="Classe",
                text_auto=".2s",
                color_discrete_map={"Ações": "#00A8E8", "FIIs": "#00E5A0"},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                height=400,
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    section("📋 Ações")
    if df_acoes.empty:
        st.info("Nenhuma ação cadastrada.")
    else:
        cols = ["ticker", "quantidade", "preco_medio", "cotacao_atual",
                "valor_atual", "rentabilidade_%", "dy_12m_%", "preco_teto"]
        st.dataframe(
            df_acoes[cols].style.format({
                "preco_medio": "R$ {:.2f}",
                "cotacao_atual": "R$ {:.2f}",
                "valor_atual": "R$ {:.2f}",
                "rentabilidade_%": "{:+.2f}%",
                "dy_12m_%": "{:.2f}%",
                "preco_teto": "R$ {:.2f}",
            }).applymap(
                lambda v: "color: #00E5A0" if isinstance(v, (int, float)) and v > 0
                else ("color: #FF5C7A" if isinstance(v, (int, float)) and v < 0 else ""),
                subset=["rentabilidade_%"],
            ),
            use_container_width=True,
            hide_index=True,
        )

    section("🏢 Fundos Imobiliários")
    if df_fiis.empty:
        st.info("Nenhum FII cadastrado.")
    else:
        cols = ["ticker", "quantidade", "preco_medio", "cotacao_atual",
                "valor_atual", "rentabilidade_%", "dy_12m_%", "preco_teto"]
        st.dataframe(
            df_fiis[cols].style.format({
                "preco_medio": "R$ {:.2f}",
                "cotacao_atual": "R$ {:.2f}",
                "valor_atual": "R$ {:.2f}",
                "rentabilidade_%": "{:+.2f}%",
                "dy_12m_%": "{:.2f}%",
                "preco_teto": "R$ {:.2f}",
            }).applymap(
                lambda v: "color: #00E5A0" if isinstance(v, (int, float)) and v > 0
                else ("color: #FF5C7A" if isinstance(v, (int, float)) and v < 0 else ""),
                subset=["rentabilidade_%"],
            ),
            use_container_width=True,
            hide_index=True,
        )

    # Exportação
    section("📥 Exportar Carteira")
    e1, e2 = st.columns(2)
    if not df_acoes.empty or not df_fiis.empty:
        df_export = pd.concat(
            [df_acoes.assign(classe="Ação"), df_fiis.assign(classe="FII")],
            ignore_index=True,
        )
        csv = df_export.to_csv(index=False).encode("utf-8")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df_export.to_excel(writer, sheet_name="Carteira", index=False)
        e1.download_button(
            "⬇️ Baixar CSV",
            csv,
            f"carteira_{date.today()}.csv",
            "text/csv",
            use_container_width=True,
        )
        e2.download_button(
            "⬇️ Baixar Excel",
            buf.getvalue(),
            f"carteira_{date.today()}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


# ── ABA: CADASTRAR ─────────────────────────────────────────────────────
with tabs[1]:
    section("➕ Novo Ativo")
    with st.form("form_novo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            tipo = st.selectbox("Tipo", ["Ação", "FII"])
            ticker = st.text_input("Ticker", placeholder="PETR4 / MXRF11").upper().strip()
        with c2:
            quantidade = st.number_input("Quantidade", min_value=1, step=1, value=100)
            preco = st.number_input("Preço médio (R$)", min_value=0.01, step=0.01, format="%.2f")
        with c3:
            data_compra = st.date_input("Data da compra", value=date.today())
            registrar = st.checkbox("Registrar no histórico de aportes", value=True)

        if st.form_submit_button("💾 Cadastrar ativo", use_container_width=True):
            if not ticker:
                st.error("Informe o ticker.")
            else:
                tabela = "acoes" if tipo == "Ação" else "fiis"
                salvar_ativo(tabela, {
                    "ticker": ticker,
                    "quantidade": int(quantidade),
                    "preco_medio": float(preco),
                    "data_compra": str(data_compra),
                })
                if registrar:
                    registrar_aporte(ticker, tipo, quantidade, preco, data_compra)
                st.success(f"✅ {tipo} {ticker} cadastrado!")
                st.rerun()


# ── ABA: GERENCIAR ─────────────────────────────────────────────────────
with tabs[2]:
    section("✏️ Editar / Excluir")
    tipo_edit = st.radio("Tabela", ["Ações", "FIIs"], horizontal=True, label_visibility="collapsed")
    tabela = "acoes" if tipo_edit == "Ações" else "fiis"
    df_edit = carregar_ativos(tabela)

    if df_edit.empty:
        st.info("Nada para editar.")
    else:
        opcoes = {f"{r['ticker']} — {r['quantidade']} un.": r["id"] for _, r in df_edit.iterrows()}
        sel = st.selectbox("Selecione o ativo", list(opcoes.keys()))
        id_sel = opcoes[sel]
        reg = df_edit[df_edit["id"] == id_sel].iloc[0]

        with st.form("form_edit"):
            c1, c2 = st.columns(2)
            with c1:
                nova_qtd = st.number_input("Quantidade", min_value=1, value=int(reg["quantidade"]))
                novo_tk = st.text_input("Ticker", value=reg["ticker"])
            with c2:
                novo_preco = st.number_input(
                    "Preço médio (R$)", min_value=0.01, value=float(reg["preco_medio"]), format="%.2f"
                )
                nova_data = st.date_input(
                    "Data da compra",
                    value=pd.to_datetime(reg.get("data_compra") or date.today()).date(),
                )
            col_a, col_b = st.columns(2)
            if col_a.form_submit_button("✏️ Atualizar", use_container_width=True):
                atualizar_ativo(tabela, id_sel, {
                    "ticker": novo_tk.upper().strip(),
                    "quantidade": int(nova_qtd),
                    "preco_medio": float(novo_preco),
                    "data_compra": str(nova_data),
                })
                st.success("Atualizado!")
                st.rerun()
            if col_b.form_submit_button("🗑️ Excluir", use_container_width=True):
                deletar_ativo(tabela, id_sel)
                st.success("Excluído!")
                st.rerun()


# ── ABA: PROJEÇÕES ────────────────────────────────────────────────────
with tabs[3]:
    section("📈 Projeção de Juros Compostos")
    cfg = carregar_config()

    c1, c2 = st.columns(2)
    with c1:
        patrimonio_ini = st.number_input(
            "Patrimônio inicial (R$)",
            min_value=0.0,
            value=float(cfg.get("valor_disponivel", 0) or 10000),
            step=1000.0,
            format="%.2f",
        )
        dy = st.slider("DY anual esperado (%)", 0.0, 25.0, 10.0, 0.25)
    with c2:
        meses = st.slider("Horizonte (meses)", 6, 360, 120, 6)
        aporte = st.number_input("Aporte mensal (R$)", min_value=0.0, value=1000.0, step=100.0)

    reinvestir = st.checkbox("♻️ Reinvestir dividendos", value=True)

    if st.button("🚀 Gerar 3 cenários", use_container_width=True):
        cenarios = {
            "Pessimista": dy * 0.6 / 100,
            "Base": dy / 100,
            "Otimista": dy * 1.4 / 100,
        }
        cores = {"Pessimista": "#FF5C7A", "Base": "#00A8E8", "Otimista": "#00E5A0"}

        fig = go.Figure()
        for nome, dy_c in cenarios.items():
            df_p = projetar(patrimonio_ini, dy_c, meses, aporte, reinvestir)
            fig.add_trace(go.Scatter(
                x=df_p["Mês"], y=df_p["Patrimônio"],
                mode="lines", name=nome,
                line=dict(color=cores[nome], width=3),
            ))

        fig.update_layout(
            title="Projeção de Patrimônio — 3 Cenários",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E6EDF7"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Mês"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="R$"),
            hovermode="x unified",
            height=480,
            legend=dict(orientation="h", y=1.05),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Cards de resumo por cenário
        cols = st.columns(3)
        for i, (nome, dy_c) in enumerate(cenarios.items()):
            df_p = projetar(patrimonio_ini, dy_c, meses, aporte, reinvestir)
            final = df_p.iloc[-1]
            with cols[i]:
                metric_card(
                    nome,
                    f"R$ {final['Patrimônio']:,.0f}",
                    f"Div. acum.: R$ {final['Dividendos acumulados']:,.0f}",
                    "up" if i == 2 else ("neutral" if i == 1 else "down"),
                )

    section("🎯 Meta de Independência Financeira")
    meta = st.number_input(
        "Renda passiva mensal desejada (R$)",
        min_value=0.0,
        value=float(cfg.get("meta_renda_passiva", 0) or 5000),
        step=500.0,
    )
    if st.button("💾 Salvar meta", use_container_width=True):
        atualizar_config(meta=meta)
        st.success("Meta salva!")

    if meta > 0 and dy > 0:
        patrimonio_meta = (meta * 12) / (dy / 100)
        st.info(
            f"📌 Com DY de {dy:.2f}% a.a., você precisa de "
            f"**R$ {patrimonio_meta:,.2f}** para gerar R$ {meta:,.2f}/mês."
        )


# ── ABA: REBALANCEAR ───────────────────────────────────────────────────
with tabs[4]:
    section("🎯 Rebalanceamento da Carteira")
    st.caption("Defina metas de alocação (%) por ativo. O sistema calcula quanto aportar.")

    df_a = carregar_ativos("acoes")
    df_f = carregar_ativos("fiis")

    if df_a.empty and df_f.empty:
        st.info("Cadastre ativos primeiro.")
    else:
        valor_aporte = st.number_input(
            "Valor disponível para aporte (R$)", min_value=0.0, value=1000.0, step=100.0
        )

        todas = []
        for _, r in df_a.iterrows():
            todas.append({"id": r["id"], "ticker": r["ticker"], "tipo": "Ação", "tabela": "acoes"})
        for _, r in df_f.iterrows():
            todas.append({"id": r["id"], "ticker": r["ticker"], "tipo": "FII", "tabela": "fiis"})

        st.markdown("**Defina a meta de alocação (%) para cada ativo:**")
        metas = {}
        cols = st.columns(min(4, len(todas)))
        for i, a in enumerate(todas):
            with cols[i % len(cols)]:
                metas[a["ticker"]] = st.number_input(
                    a["ticker"], min_value=0.0, max_value=100.0, value=0.0,
                    step=1.0, key=f"meta_{a['ticker']}",
                )

        soma_metas = sum(metas.values())
        if soma_metas == 0:
            st.warning("Defina pelo menos uma meta > 0.")
        elif abs(soma_metas - 100) > 0.5:
            st.warning(f"⚠️ Soma das metas = {soma_metas:.1f}%. Ideal: 100%.")
        else:
            df_a_e = enriquecer(df_a, "acao")
            df_f_e = enriquecer(df_f, "fii")
            tot = (
                (df_a_e["valor_atual"].sum() if not df_a_e.empty else 0)
                + (df_f_e["valor_atual"].sum() if not df_f_e.empty else 0)
            )
            novo_tot = tot + valor_aporte

            rows = []
            for a in todas:
                tk = a["ticker"]
                fonte = df_a_e if a["tipo"] == "Ação" else df_f_e
                atual = float(fonte[fonte["ticker"] == tk]["valor_atual"].iloc[0])
                alvo = novo_tot * (metas[tk] / 100)
                gap = alvo - atual
                rows.append({
                    "Ticker": tk,
                    "Tipo": a["tipo"],
                    "Atual (R$)": atual,
                    "% Atual": (atual / tot * 100) if tot > 0 else 0,
                    "Meta %": metas[tk],
                    "Alvo (R$)": alvo,
                    "Aportar (R$)": max(gap, 0),
                })
            df_reb = pd.DataFrame(rows).sort_values("Aportar (R$)", ascending=False)

            st.dataframe(
                df_reb.style.format({
                    "Atual (R$)": "R$ {:,.2f}",
                    "% Atual": "{:.1f}%",
                    "Meta %": "{:.1f}%",
                    "Alvo (R$)": "R$ {:,.2f}",
                    "Aportar (R$)": "R$ {:,.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="% Atual", x=df_reb["Ticker"], y=df_reb["% Atual"],
                marker_color="#00A8E8", text=df_reb["% Atual"].round(1), textposition="outside",
            ))
            fig.add_trace(go.Bar(
                name="Meta %", x=df_reb["Ticker"], y=df_reb["Meta %"],
                marker_color="#00E5A0", text=df_reb["Meta %"].round(1), textposition="outside",
            ))
            fig.update_layout(
                barmode="group", title="Atual vs Meta",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"), height=400,
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig, use_container_width=True)


# ── ABA: WATCHLIST ─────────────────────────────────────────────────────
with tabs[5]:
    section("👁️ Watchlist — Ativos Monitorados")

    with st.form("form_watch", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        with c1:
            w_tipo = st.selectbox("Tipo", ["Ação", "FII"])
        with c2:
            w_ticker = st.text_input("Ticker").upper().strip()
        with c3:
            w_preco = st.number_input("Preço alvo (R$)", min_value=0.0, step=0.01, format="%.2f")
        with c4:
            w_obs = st.text_input("Observação")
        if st.form_submit_button("➕ Adicionar", use_container_width=True):
            if w_ticker:
                salvar_watchlist(w_ticker, w_tipo, w_preco, w_obs)
                st.success(f"{w_ticker} adicionado!")
                st.rerun()

    df_w = carregar_watchlist()
    if df_w.empty:
        st.info("Watchlist vazia.")
    else:
        df_w["cotacao_atual"] = df_w["ticker"].apply(get_cotacao)
        df_w["dist_%"] = np.where(
            df_w["preco_alvo"] > 0,
            (df_w["cotacao_atual"] / df_w["preco_alvo"] - 1) * 100,
            0.0,
        )
        df_w["status"] = np.where(
            df_w["cotacao_atual"] <= df_w["preco_alvo"], "🎯 Alvo atingido!", "⏳ Aguardando"
        )

        st.dataframe(
            df_w[["ticker", "tipo", "cotacao_atual", "preco_alvo", "dist_%", "status", "observacao"]]
            .rename(columns={
                "ticker": "Ticker", "tipo": "Tipo", "cotacao_atual": "Preço atual",
                "preco_alvo": "Preço alvo", "dist_%": "Dist. %", "status": "Status",
                "observacao": "Obs.",
            })
            .style.format({
                "Preço atual": "R$ {:.2f}",
                "Preço alvo": "R$ {:.2f}",
                "Dist. %": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )

        del_id = st.selectbox(
            "Excluir da watchlist:",
            options=df_w["id"].tolist(),
            format_func=lambda x: df_w[df_w["id"] == x]["ticker"].iloc[0],
        )
        if st.button("🗑️ Remover", use_container_width=True):
            deletar_watchlist(del_id)
            st.success("Removido!")
            st.rerun()


# ── ABA: APORTES ───────────────────────────────────────────────────────
with tabs[6]:
    section("📜 Histórico de Aportes")
    df_ap = carregar_aportes()

    if df_ap.empty:
        st.info("Nenhum aporte registrado.")
    else:
        df_ap["data"] = pd.to_datetime(df_ap["data"])

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Total Aportado", f"R$ {df_ap['total'].sum():,.2f}")
        with c2:
            metric_card("Nº de Aportes", str(len(df_ap)))
        with c3:
            media = df_ap["total"].mean()
            metric_card("Aporte Médio", f"R$ {media:,.2f}")

        section("📈 Evolução dos Aportes")
        df_m = df_ap.copy()
        df_m["mes"] = df_m["data"].dt.to_period("M").dt.to_timestamp()
        df_mensal = df_m.groupby("mes")["total"].sum().reset_index()
        df_mensal["acumulado"] = df_mensal["total"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_mensal["mes"], y=df_mensal["total"],
            name="Aporte mensal", marker_color="#00A8E8",
        ))
        fig.add_trace(go.Scatter(
            x=df_mensal["mes"], y=df_mensal["acumulado"],
            name="Acumulado", yaxis="y2",
            line=dict(color="#00E5A0", width=3),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E6EDF7"), height=400,
            yaxis=dict(title="Aporte (R$)", gridcolor="rgba(255,255,255,0.05)"),
            yaxis2=dict(title="Acumulado (R$)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        section("📋 Todos os aportes")
        st.dataframe(
            df_ap[["data", "ticker", "tipo", "quantidade", "preco", "total"]]
            .rename(columns={
                "data": "Data", "ticker": "Ticker", "tipo": "Tipo",
                "quantidade": "Qtd", "preco": "Preço", "total": "Total",
            })
            .style.format({"Preço": "R$ {:.2f}", "Total": "R$ {:.2f}"}),
            use_container_width=True,
            hide_index=True,
            height=400,
        )
