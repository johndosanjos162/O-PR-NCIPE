"""
🎯 Gestor de Investimentos B3 — Edição Premium Integrada com Login
Streamlit + Pandas + Supabase Auth + Brapi (cotações + Bazin + Dividendos)
"""

import io
from dataclasses import dataclass
from datetime import datetime, date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from supabase import create_client, Client

# ══════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gestor Premium B3",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

BAZIN_TAXA = 0.06

# ══════════════════════════════════════════════════════════════════════
# CSS PREMIUM
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    .main, .stApp {
        background: radial-gradient(circle at top left, #0B1220 0%, #060B14 100%);
        color: #E6EDF7;
    }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
    html, body, [class*="css"], p, span, li, h1, h2, h3, h4, h5, h6, label, div {
        color: #E6EDF7;
    }
    .hero {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 50%, #7B61FF 100%);
        padding: 28px 32px; border-radius: 20px; margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(0, 229, 160, 0.15);
        display: flex; align-items: center; justify-content: space-between;
    }
    .hero h1 { color: #060B14 !important; font-size: 32px; font-weight: 800;
               margin: 0; letter-spacing: -0.5px; }
    .hero p  { color: #060B14 !important; opacity: 0.75; margin: 4px 0 0 0;
               font-size: 14px; font-weight: 500; }
    .hero .badge {
        background: rgba(6, 11, 20, 0.85); color: #00E5A0 !important;
        padding: 10px 18px; border-radius: 12px; font-weight: 700;
        font-size: 13px; letter-spacing: 0.5px;
    }
    .metric-card {
        background: linear-gradient(145deg, #131C2F 0%, #0F1729 100%);
        border: 1px solid rgba(0, 229, 160, 0.12);
        padding: 20px 22px; border-radius: 16px;
        transition: all 0.25s ease; position: relative; overflow: hidden;
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
    .metric-card .label { color: #A0AEC0 !important; font-size: 12px; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 0.8px; }
    .metric-card .value { color: #FFFFFF !important; font-size: 26px; font-weight: 800; margin-top: 6px; }
    .metric-card .delta { font-size: 13px; font-weight: 600; margin-top: 4px; }
    .delta.up   { color: #00E5A0 !important; }
    .delta.down { color: #FF5C7A !important; }
    .delta.neutral { color: #A0AEC0 !important; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220 0%, #060B14 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] * { color: #E6EDF7 !important; }
    section[data-testid="stSidebar"] label { color: #E6EDF7 !important; }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
        color: #060B14 !important; font-weight: 700; border: none;
        border-radius: 10px; padding: 10px 16px; transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 229, 160, 0.3);
    }
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #A0AEC0 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: transparent; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background: #131C2F; border-radius: 12px 12px 0 0; padding: 10px 20px;
        color: #A0AEC0 !important; font-weight: 600; border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"] p { color: #A0AEC0 !important; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,229,160,0.15), rgba(0,168,232,0.1));
        color: #00E5A0 !important;
        border-bottom: 2px solid #00E5A0;
    }
    .stTabs [aria-selected="true"] p { color: #00E5A0 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
        color: #060B14 !important; font-weight: 700; border: none; border-radius: 10px;
        transition: all 0.2s ease; padding: 10px 16px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 229, 160, 0.25);
    }
    .stButton > button p { color: #060B14 !important; font-weight: 700 !important; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
        color: #060B14 !important; font-weight: 700; border: none;
        border-radius: 10px; padding: 10px 16px;
    }
    .stDownloadButton > button p { color: #060B14 !important; font-weight: 700 !important; }
    .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stDateInput label, .stCheckbox label, .stRadio label,
    .stTextArea label, .stSlider label, .stMultiSelect label,
    .stFileUploader label {
        color: #E6EDF7 !important;
        font-weight: 600 !important;
    }
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
        background: #1B2740 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        caret-color: #00E5A0 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        opacity: 1 !important;
    }
    .stNumberInput input:disabled,
    .stTextInput input:disabled,
    .stDateInput input:disabled,
    .stNumberInput input[disabled],
    .stTextInput input[disabled] {
        background: #24325A !important;
        color: #00E5A0 !important;
        -webkit-text-fill-color: #00E5A0 !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
        font-weight: 800 !important;
        border: 1px solid rgba(0, 229, 160, 0.35) !important;
    }
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #6B7A99 !important;
        -webkit-text-fill-color: #6B7A99 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus {
        border-color: #00E5A0 !important;
        box-shadow: 0 0 0 2px rgba(0,229,160,0.2) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .stNumberInput button {
        background: #24325A !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }
    .stNumberInput button:hover {
        background: #2E3F73 !important;
        color: #00E5A0 !important;
    }
    .stNumberInput button svg,
    .stNumberInput button svg path,
    .stNumberInput button svg line {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }
    .stNumberInput > div > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background: #1B2740 !important;
        border-radius: 10px !important;
    }
    [data-testid="stForm"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        background: #1B2740 !important;
        opacity: 1 !important;
    }
    [data-testid="stForm"] input:disabled {
        color: #00E5A0 !important;
        -webkit-text-fill-color: #00E5A0 !important;
        background: #24325A !important;
        opacity: 1 !important;
        font-weight: 800 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: #1B2740 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] div { color: #FFFFFF !important; }
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background: #131C2F !important; color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] li:hover { background: #1B2740 !important; }
    .stCheckbox div[data-testid="stMarkdownContainer"] p,
    .stRadio div[data-testid="stMarkdownContainer"] p { color: #E6EDF7 !important; }
    .stRadio div[role="radiogroup"] label { color: #E6EDF7 !important; }
    .stSlider [data-baseweb="slider"] div { color: #E6EDF7 !important; }
    .stSlider [role="slider"] { background-color: #00E5A0 !important; }
    [data-testid="stForm"] {
        background: rgba(19, 28, 47, 0.55) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 22px !important;
    }
    .stAlert { border-radius: 12px !important; }
    .stAlert div, .stAlert p, .stAlert span { color: #FFFFFF !important; }
    div[data-baseweb="notification"] { border-radius: 12px !important; }
    .stDataFrame {
        border-radius: 12px; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stDataFrame div[role="columnheader"] { color: #E6EDF7 !important; }
    .stDataFrame div[role="gridcell"] { color: #E6EDF7 !important; }
    .stCaption, [data-testid="stCaptionContainer"] { color: #A0AEC0 !important; }
    .section-title {
        font-size: 18px; font-weight: 700; color: #FFFFFF !important;
        margin: 24px 0 12px 0; padding-left: 12px;
        border-left: 3px solid #00E5A0;
    }
    .bazin-card {
        background: linear-gradient(135deg, rgba(0,229,160,0.10), rgba(0,168,232,0.06));
        border: 1px solid rgba(0,229,160,0.30); border-radius: 14px;
        padding: 14px 22px; margin: 12px 0 18px 0;
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 16px;
    }
    .bazin-card .cell { display: flex; flex-direction: column; }
    .bazin-card .cell .lbl { color: #A0AEC0 !important; font-size: 11px;
                              font-weight: 700; letter-spacing: 1px; }
    .bazin-card .cell .val { color: #FFFFFF !important; font-size: 20px;
                              font-weight: 800; margin-top: 2px; }
    .status-pill {
        display: inline-block; padding: 8px 18px; border-radius: 999px;
        font-size: 13px; font-weight: 800; letter-spacing: 0.5px;
    }
    .status-forte   { background: rgba(0,229,160,0.18); color: #00E5A0 !important;
                      border: 1px solid rgba(0,229,160,0.5); }
    .status-bom     { background: rgba(74,222,128,0.15); color: #4ADE80 !important;
                      border: 1px solid rgba(74,222,128,0.4); }
    .status-proximo { background: rgba(250,204,21,0.15); color: #FACC15 !important;
                      border: 1px solid rgba(250,204,21,0.4); }
    .status-caro    { background: rgba(255,92,122,0.15); color: #FF5C7A !important;
                      border: 1px solid rgba(255,92,122,0.4); }
    .status-sem     { background: rgba(122,134,153,0.15); color: #A0AEC0 !important;
                      border: 1px solid rgba(122,134,153,0.4); }
    .login-wrap {
        max-width: 440px; margin: 60px auto 0 auto;
        background: linear-gradient(145deg, #131C2F 0%, #0F1729 100%);
        border: 1px solid rgba(0, 229, 160, 0.18);
        border-radius: 22px; padding: 40px 36px 26px 36px;
        box-shadow: 0 24px 60px rgba(0, 229, 160, 0.12);
        text-align: center;
    }
    .login-logo { font-size: 54px; margin-bottom: 6px;
                  filter: drop-shadow(0 0 22px rgba(0, 229, 160, 0.45)); }
    .login-title { color: #FFFFFF !important; font-size: 26px; font-weight: 800;
                   letter-spacing: -0.5px; margin-bottom: 4px; }
    .login-sub { color: #A0AEC0 !important; font-size: 13px;
                 margin-bottom: 6px; letter-spacing: 0.5px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════
# SUPABASE
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
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None


def fazer_login(email: str, senha: str):
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return resp.user, None
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            return None, "❌ Email ou senha incorretos."
        if "Email not confirmed" in msg:
            return None, "📧 Confirme seu email antes de entrar."
        return None, f"❌ {msg}"


def fazer_logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        if k.startswith(("auth_", "cot_", "cfg_")):
            del st.session_state[k]
    st.rerun()


def render_login_screen():
    st.markdown(
        """
        <div class="login-wrap">
            <div class="login-logo">💎</div>
            <div class="login-title">Gestor Premium B3</div>
            <div class="login-sub">AÇÕES · FIIs · BAZIN · TEMPO REAL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            email = st.text_input("📧 Email", key="login_email")
            senha = st.text_input("🔒 Senha", type="password", key="login_senha")
            entrar = st.form_submit_button("🔓 Entrar", use_container_width=True)
            if entrar:
                if not email or not senha:
                    st.warning("Preencha email e senha.")
                else:
                    with st.spinner("Entrando..."):
                        user, err = fazer_login(email, senha)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.auth_user = {"id": user.id, "email": user.email}
                        st.success("✅ Bem-vindo!")
                        st.rerun()
        st.markdown(
            """
            <div style="text-align:center; margin-top:18px; color:#A0AEC0; font-size:12px;">
                Acesso restrito · Solicite seu cadastro ao administrador
            </div>
            """,
            unsafe_allow_html=True,
        )


if not st.session_state.get("auth_user"):
    render_login_screen()
    st.stop()

USER = st.session_state.auth_user
USER_ID = USER["id"]
USER_EMAIL = USER["email"]

# ══════════════════════════════════════════════════════════════════════
# APIs DE MERCADO
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


def _buscar_dividendos_brapi(ticker: str, tipo: str) -> pd.DataFrame:
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


def _carregar_dividendos_cache(ticker: str, tipo: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table("dividendos").select("payment_date,rate")
            .eq("ticker", ticker).eq("tipo", tipo).execute()
        )
        if not resp.data:
            return pd.DataFrame()
        df = pd.DataFrame(resp.data)
        df.columns = ["paymentDate", "rate"]
        df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce").fillna(0)
        return df
    except Exception:
        return pd.DataFrame()


def _salvar_dividendos_cache(ticker: str, tipo: str, df: pd.DataFrame):
    if df.empty or "rate" not in df.columns:
        return
    try:
        registros = []
        for _, r in df.iterrows():
            dt = r.get("paymentDate")
            dt_str = dt.date().isoformat() if pd.notna(dt) else None
            registros.append({
                "ticker": ticker, "tipo": tipo,
                "payment_date": dt_str, "rate": float(r["rate"]),
            })
        if registros:
            supabase.table("dividendos").upsert(
                registros,
                on_conflict="ticker,payment_date,rate",
                ignore_duplicates=True,
            ).execute()
    except Exception:
        pass


@st.cache_data(ttl=3600, show_spinner=False)
def get_dividendos(ticker: str, tipo: str = "acao") -> pd.DataFrame:
    if not ticker:
        return pd.DataFrame()
    df_cache = _carregar_dividendos_cache(ticker, tipo)
    if not df_cache.empty:
        corte = pd.Timestamp.now() - pd.DateOffset(months=12)
        recentes = df_cache[df_cache["paymentDate"] >= corte]
        if len(recentes) >= 3:
            return df_cache
    df_brapi = _buscar_dividendos_brapi(ticker, tipo)
    if not df_brapi.empty:
        _salvar_dividendos_cache(ticker, tipo, df_brapi)
        if not df_cache.empty:
            df_final = pd.concat([df_cache, df_brapi], ignore_index=True)
            df_final = df_final.drop_duplicates(
                subset=["paymentDate", "rate"]
            ).reset_index(drop=True)
            return df_final
        return df_brapi
    return df_cache


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
# 💵 RESUMO DE DIVIDENDOS POR COTA (NOVO)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def get_resumo_dividendos(ticker: str, tipo: str) -> dict:
    """Retorna resumo dos dividendos por cota dos últimos 12 meses."""
    vazio = {
        "ultimo": 0.0, "media": 0.0, "total_12m": 0.0,
        "n": 0, "data_ultimo": None, "df": pd.DataFrame(),
    }
    df = get_dividendos(ticker, tipo)
    if df.empty or "rate" not in df.columns:
        return vazio

    df = df.copy()
    df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
    corte = pd.Timestamp.now() - pd.DateOffset(months=12)
    df_12m = df[df["paymentDate"] >= corte].copy()
    if df_12m.empty:
        df_12m = df.copy()

    df_12m = df_12m.sort_values("paymentDate", ascending=False).reset_index(drop=True)
    total = float(df_12m["rate"].sum())
    n = len(df_12m)
    ultimo = float(df_12m.iloc[0]["rate"]) if n > 0 else 0.0
    media = total / n if n > 0 else 0.0
    data_ultimo = df_12m.iloc[0]["paymentDate"] if n > 0 else None

    return {
        "ultimo": ultimo,
        "media": media,
        "total_12m": total,
        "n": n,
        "data_ultimo": data_ultimo,
        "df": df_12m,
    }


def div_cota_resumo(ticker: str, tipo: str) -> float:
    """Atalho: retorna só o dividendo anual por cota (12m)."""
    return get_resumo_dividendos(ticker, tipo)["total_12m"]


def render_dividendo_por_cota(
    ticker: str,
    tipo: str,
    cotacao: float = 0.0,
    compacto: bool = False,
    key_prefix: str = "",
):
    """
    Renderiza o bloco de dividendo pago por cota.
    - compacto=True: mostra só os 4 cards (usado em abas resumidas)
    - compacto=False: cards + tabela + gráfico + rodapé (versão completa)
    """
    res = get_resumo_dividendos(ticker, tipo)

    if res["n"] == 0:
        st.info(f"ℹ️ Sem histórico de dividendos disponível para {ticker}.")
        return

    dy = (res["total_12m"] / cotacao) if cotacao > 0 else 0.0

    # ─── Cards ───
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        data_str = res["data_ultimo"].strftime("%d/%m/%Y") if res["data_ultimo"] is not None else "—"
        metric_card(
            "💵 Último dividendo / cota",
            f"R$ {res['ultimo']:.4f}",
            f"pago em {data_str}",
            "up",
        )
    with c2:
        metric_card(
            "📅 Média mensal / cota",
            f"R$ {res['media']:.4f}",
            f"{res['n']} pagamento(s) em 12m",
            "up",
        )
    with c3:
        metric_card(
            "📈 Total anual / cota",
            f"R$ {res['total_12m']:.4f}",
            "somando os últimos 12 meses",
            "up",
        )
    with c4:
        if cotacao > 0:
            metric_card(
                "🎯 DY real 12m",
                f"{dy * 100:.2f}%",
                f"R$ {res['total_12m']:.4f} ÷ R$ {cotacao:.2f}",
                "neutral",
            )
        else:
            metric_card(
                "🎯 DY real 12m",
                "—",
                "cotação indisponível",
                "neutral",
            )

    if compacto:
        return

    # ─── Tabela + Gráfico ───
    st.markdown("<br>", unsafe_allow_html=True)
    col_tabela, col_grafico = st.columns([1, 1.4])

    with col_tabela:
        st.markdown(
            "<div style='color:#FFFFFF; font-weight:700; "
            "font-size:14px; margin-bottom:8px;'>"
            "📋 Histórico detalhado por cota</div>",
            unsafe_allow_html=True,
        )
        df_show = res["df"][["paymentDate", "rate"]].copy()
        df_show["paymentDate"] = df_show["paymentDate"].dt.strftime("%d/%m/%Y")
        df_show.columns = ["Data do pagamento", "Dividendo / cota (R$)"]
        st.dataframe(
            df_show.style.format({"Dividendo / cota (R$)": "R$ {:.4f}"}),
            use_container_width=True,
            hide_index=True,
            height=340,
        )

    with col_grafico:
        st.markdown(
            "<div style='color:#FFFFFF; font-weight:700; "
            "font-size:14px; margin-bottom:8px;'>"
            "📊 Evolução mensal do dividendo por cota</div>",
            unsafe_allow_html=True,
        )
        df_graf = res["df"].sort_values("paymentDate").copy()
        df_graf["rotulo"] = df_graf["paymentDate"].dt.strftime("%b/%y")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_graf["rotulo"],
            y=df_graf["rate"],
            marker_color="#00E5A0",
            text=df_graf["rate"].round(4),
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=11),
            name="Dividendo por cota",
        ))
        fig.update_layout(
            title=f"{ticker} — R$ por cota",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E6EDF7"),
            height=340,
            margin=dict(t=40, b=20, l=20, r=20),
            yaxis=dict(
                title="R$ por cota",
                gridcolor="rgba(255,255,255,0.05)",
                tickformat=".2f",
            ),
            xaxis=dict(title="Mês"),
            showlegend=False,
            bargap=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div style="background: rgba(0,168,232,0.08);
                    border-left: 3px solid #00A8E8;
                    border-radius: 8px; padding: 12px 18px;
                    margin: 10px 0 20px 0;">
            <div style="color:#A0AEC0; font-size:12px; line-height:1.6;">
                ℹ️ <b style="color:#FFFFFF;">Como ler estes números:</b>
                os valores acima representam o <b style="color:#00E5A0;">dividendo pago por cada cota</b> 
                que você possui — ou seja, quanto o ativo <b>distribui em proventos</b> 
                por cota, e não o preço de negociação da cota em si.
                Ex.: se o último dividendo foi <b>R$ {res['ultimo']:.4f}</b> e você tem 
                <b>100 cotas</b>, você recebe <b style="color:#00E5A0;">R$ {res['ultimo']*100:.2f}</b> 
                naquele mês.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════
# BAZIN
# ══════════════════════════════════════════════════════════════════════
@dataclass
class AtivoInfo:
    ticker: str
    tipo: str
    cotacao: float
    dy_12m: float
    dividendo_anual: float
    preco_teto: float
    margem: float
    status: str
    status_key: str
    cor: str


@st.cache_data(ttl=300, show_spinner=False)
def get_ativo_info(ticker: str, tipo: str = "acao") -> AtivoInfo:
    cot = get_cotacao(ticker)
    dy = calcular_dy_12m(ticker, tipo)
    div_anual = cot * dy
    teto = div_anual / BAZIN_TAXA if div_anual > 0 else 0.0
    margem = ((teto - cot) / teto * 100) if teto > 0 else 0.0

    if teto <= 0:
        status, key, cor = "⚪ SEM DADOS", "sem", "#A0AEC0"
    elif cot <= teto * 0.85:
        status, key, cor = "🟢 COMPRA FORTE", "forte", "#00E5A0"
    elif cot <= teto:
        status, key, cor = "🟢 BOM MOMENTO", "bom", "#4ADE80"
    elif cot <= teto * 1.10:
        status, key, cor = "🟡 PRÓXIMO DO TETO", "proximo", "#FACC15"
    else:
        status, key, cor = "🔴 ACIMA DO TETO", "caro", "#FF5C7A"

    return AtivoInfo(ticker, tipo, cot, dy, div_anual, teto, margem, status, key, cor)


def status_pill_html(info: AtivoInfo) -> str:
    cls = {
        "forte": "status-forte", "bom": "status-bom",
        "proximo": "status-proximo", "caro": "status-caro", "sem": "status-sem",
    }[info.status_key]
    return f'<span class="status-pill {cls}">{info.status}</span>'


# ══════════════════════════════════════════════════════════════════════
# BANCO (POR USUÁRIO)
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=15, show_spinner=False)
def carregar_ativos(tabela: str, user_id: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table(tabela).select("*")
            .eq("user_id", user_id).order("ticker").execute()
        )
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar {tabela}: {e}")
        return pd.DataFrame()


def salvar_ativo(tabela: str, dados: dict, user_id: str):
    dados["user_id"] = user_id
    supabase.table(tabela).insert(dados).execute()
    carregar_ativos.clear()


def atualizar_ativo(tabela: str, id_: int, dados: dict, user_id: str):
    dados["updated_at"] = datetime.now().isoformat()
    supabase.table(tabela).update(dados).eq("id", id_).eq("user_id", user_id).execute()
    carregar_ativos.clear()


def deletar_ativo(tabela: str, id_: int, user_id: str):
    supabase.table(tabela).delete().eq("id", id_).eq("user_id", user_id).execute()
    carregar_ativos.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_config(user_id: str) -> dict:
    try:
        resp = supabase.table("config").select("*").eq("user_id", user_id).execute()
        if resp.data:
            return resp.data[0]
    except Exception:
        pass
    return {"valor_disponivel": 0.0, "meta_renda_passiva": 0.0}


def atualizar_config(user_id: str, valor=None, meta=None):
    payload = {"user_id": user_id, "updated_at": datetime.now().isoformat()}
    if valor is not None:
        payload["valor_disponivel"] = float(valor)
    if meta is not None:
        payload["meta_renda_passiva"] = float(meta)
    supabase.table("config").upsert(payload).execute()
    carregar_config.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_aportes(user_id: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table("aportes").select("*")
            .eq("user_id", user_id).order("data", desc=True).execute()
        )
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def registrar_aporte(ticker, tipo, qtd, preco, data_, user_id):
    supabase.table("aportes").insert({
        "ticker": ticker, "tipo": tipo, "quantidade": int(qtd),
        "preco": float(preco), "total": float(qtd) * float(preco),
        "data": str(data_), "user_id": user_id,
    }).execute()
    carregar_aportes.clear()


@st.cache_data(ttl=15, show_spinner=False)
def carregar_watchlist(user_id: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table("watchlist").select("*")
            .eq("user_id", user_id).order("ticker").execute()
        )
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def salvar_watchlist(ticker, tipo, preco_alvo, obs, user_id):
    supabase.table("watchlist").insert({
        "ticker": ticker, "tipo": tipo, "preco_alvo": float(preco_alvo),
        "observacao": obs, "user_id": user_id,
    }).execute()
    carregar_watchlist.clear()


def deletar_watchlist(id_, user_id):
    supabase.table("watchlist").delete().eq("id", id_).eq("user_id", user_id).execute()
    carregar_watchlist.clear()


# ══════════════════════════════════════════════════════════════════════
# PROJEÇÕES SALVAS
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=15, show_spinner=False)
def carregar_projecoes(user_id: str) -> pd.DataFrame:
    try:
        resp = (
            supabase.table("projecoes").select("*")
            .eq("user_id", user_id).order("created_at", desc=True).execute()
        )
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def salvar_projecao(dados: dict, user_id: str):
    dados["user_id"] = user_id
    supabase.table("projecoes").insert(dados).execute()
    carregar_projecoes.clear()


def deletar_projecao(id_: int, user_id: str):
    supabase.table("projecoes").delete().eq("id", id_).eq("user_id", user_id).execute()
    carregar_projecoes.clear()


# ══════════════════════════════════════════════════════════════════════
# ENRIQUECIMENTO
# ══════════════════════════════════════════════════════════════════════
def enriquecer(df: pd.DataFrame, tipo: str = "acao") -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    infos = [get_ativo_info(t, tipo) for t in df["ticker"]]

    df["cotacao_atual"] = [i.cotacao for i in infos]
    df["dy_12m_%"] = [i.dy_12m * 100 for i in infos]
    df["dividendo_anual"] = [i.dividendo_anual for i in infos]
    df["preco_teto"] = [i.preco_teto for i in infos]
    df["margem_bazin_%"] = [i.margem for i in infos]
    df["status_bazin"] = [i.status for i in infos]
    df["status_key"] = [i.status_key for i in infos]

    # 💵 Dividendo por cota (12m) — nova coluna
    df["div_cota_12m"] = [div_cota_resumo(t, tipo) for t in df["ticker"]]

    df["valor_investido"] = df["quantidade"] * df["preco_medio"]
    df["valor_atual"] = df["quantidade"] * df["cotacao_atual"]
    df["lucro_prejuizo"] = df["valor_atual"] - df["valor_investido"]
    df["rentabilidade_%"] = np.where(
        df["valor_investido"] > 0,
        (df["valor_atual"] / df["valor_investido"] - 1) * 100,
        0.0,
    )
    df["renda_mensal_est"] = df["valor_atual"] * df["dy_12m_%"] / 100 / 12
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
        regs.append({
            "Mês": m,
            "Dividendos do mês": round(div, 2),
            "Dividendos acumulados": round(div_acum, 2),
            "Patrimônio": round(patrimonio, 2),
            "Total investido": round(inv_total, 2),
        })
    return pd.DataFrame(regs)


def projetar_renda_ativo(quantidade, preco_unitario, dy_anual, meses=60, reinvestir=True):
    investimento_total = quantidade * preco_unitario
    div_cota_ano = preco_unitario * dy_anual
    div_cota_mes = div_cota_ano / 12
    renda_anual_ini = quantidade * div_cota_ano
    renda_mensal_ini = renda_anual_ini / 12
    payback_meses = (1 / dy_anual) * 12 if dy_anual > 0 else 0

    dy_mensal = (1 + dy_anual) ** (1 / 12) - 1 if dy_anual > 0 else 0
    cotas = float(quantidade)
    renda_acum = 0.0
    regs = []
    for m in range(1, meses + 1):
        div_mes = cotas * preco_unitario * dy_mensal
        renda_acum += div_mes
        if reinvestir:
            cotas += div_mes / preco_unitario
        regs.append({
            "Mês": m,
            "Renda no mês (R$)": round(div_mes, 2),
            "Renda acumulada (R$)": round(renda_acum, 2),
            "Cotas": round(cotas, 2),
            "Patrimônio (R$)": round(cotas * preco_unitario, 2),
        })

    return {
        "investimento_total": investimento_total,
        "div_cota_ano": div_cota_ano,
        "div_cota_mes": div_cota_mes,
        "renda_anual_ini": renda_anual_ini,
        "renda_mensal_ini": renda_mensal_ini,
        "payback_meses": payback_meses,
        "df": pd.DataFrame(regs),
    }


def dy_medio_carteira(df_a: pd.DataFrame, df_f: pd.DataFrame) -> float:
    pesos, dys = [], []
    for df in (df_a, df_f):
        if not df.empty:
            pesos.extend(df["valor_atual"].tolist())
            dys.extend(df["dy_12m_%"].tolist())
    if not pesos or sum(pesos) == 0:
        return 0.0
    return float(np.average(dys, weights=pesos))


# ══════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════
def metric_card(label, value, delta=None, delta_type="neutral"):
    delta_html = f'<div class="delta {delta_type}">{delta}</div>' if delta else ""
    st.markdown(
        f"""<div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        f"""
        <div style="background: rgba(0,229,160,0.06); border: 1px solid rgba(0,229,160,0.15);
                    border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
            <div style="color:#A0AEC0; font-size:10px; font-weight:700; letter-spacing:1px;">
                LOGADO COMO
            </div>
            <div style="color:#FFFFFF; font-size:13px; font-weight:700;
                        margin-top:3px; overflow:hidden; text-overflow:ellipsis;">
                {USER_EMAIL}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        fazer_logout()

    st.markdown("---")

    st.markdown(
        """<div style="text-align:center; padding: 8px 0 20px 0;">
            <div style="font-size: 40px;">💎</div>
            <div style="font-size: 18px; font-weight: 800; color: #00E5A0 !important; letter-spacing: 0.5px;">
                GESTOR PREMIUM
            </div>
            <div style="font-size: 11px; color: #A0AEC0 !important; letter-spacing: 1px;">
                B3 · BAZIN · TEMPO REAL
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    cfg = carregar_config(USER_ID)

    st.markdown("### 💰 Valor disponível")
    st.markdown(
        f"""<div style="background: linear-gradient(135deg, #00E5A0 0%, #00A8E8 100%);
                    padding: 16px; border-radius: 14px; text-align: center;
                    box-shadow: 0 8px 24px rgba(0, 229, 160, 0.2); margin-bottom: 12px;">
            <div style="color: #060B14; font-size: 12px; font-weight: 700; opacity: 0.75;">
                SALDO PARA APORTE
            </div>
            <div style="color: #060B14; font-size: 26px; font-weight: 900; margin-top: 4px;">
                R$ {cfg.get('valor_disponivel', 0):,.2f}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    novo_valor = st.number_input(
        "Atualizar saldo (R$)", min_value=0.0,
        value=float(cfg.get("valor_disponivel", 0.0)), step=100.0,
        format="%.2f", label_visibility="collapsed", key="input_saldo",
    )
    if st.button("💾 Salvar saldo", use_container_width=True):
        atualizar_config(USER_ID, valor=novo_valor)
        st.success("Saldo atualizado!")
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Sincronizar cotações", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ══════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    """<div class="hero">
        <div>
            <h1>💎 Painel de Investimentos</h1>
            <p>Cotações em tempo real · Preço Teto de Bazin · Projeções com reinvestimento</p>
        </div>
        <div class="badge">● MERCADO ATIVO</div>
    </div>""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "🎯 Radar Bazin",
    "📊 Dashboard",
    "➕ Cadastrar",
    "✏️ Gerenciar",
    "📈 Projeções",
    "💾 Projeções Salvas",
    "🎯 Rebalancear",
    "👁️ Watchlist",
    "📜 Aportes",
])

# ── ABA 0: RADAR BAZIN ─────────────────────────────────────────────────
with tabs[0]:
    section("🎯 Radar Bazin — Onde está a oportunidade?")

    df_a = carregar_ativos("acoes", USER_ID)
    df_f = carregar_ativos("fiis", USER_ID)

    with st.spinner("Consultando cotações e histórico de dividendos..."):
        df_a_e = enriquecer(df_a, "acao")
        df_f_e = enriquecer(df_f, "fii")

    if df_a_e.empty and df_f_e.empty:
        st.info("Cadastre ativos para o radar começar a funcionar.")
    else:
        df_radar = pd.concat(
            [df_a_e.assign(classe="Ação"), df_f_e.assign(classe="FII")],
            ignore_index=True,
        ).sort_values("margem_bazin_%", ascending=False)

        forte = (df_radar["status_key"] == "forte").sum()
        bom = (df_radar["status_key"] == "bom").sum()
        proximo = (df_radar["status_key"] == "proximo").sum()
        caro = (df_radar["status_key"] == "caro").sum()

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("🟢 Compra forte", str(forte), "≤ 85% do teto", "up")
        with c2: metric_card("🟢 Bom momento", str(bom), "≤ teto", "up")
        with c3: metric_card("🟡 Próximo do teto", str(proximo), "≤ 110% do teto", "neutral")
        with c4: metric_card("🔴 Acima do teto", str(caro), "> 110% do teto", "down")

        st.markdown("<br>", unsafe_allow_html=True)

        oportunidades = df_radar[df_radar["status_key"].isin(["forte", "bom"])]
        if not oportunidades.empty:
            nomes = ", ".join(oportunidades["ticker"].tolist())
            st.success(f"✨ **{len(oportunidades)} ativo(s) em zona de compra**: {nomes}")

        cols_show = ["ticker", "classe", "cotacao_atual", "div_cota_12m",
                     "preco_teto", "margem_bazin_%", "dy_12m_%", "status_bazin"]
        st.dataframe(
            df_radar[cols_show]
            .rename(columns={
                "ticker": "Ticker", "classe": "Classe",
                "cotacao_atual": "Cotação", "div_cota_12m": "Div/cota 12m (R$)",
                "preco_teto": "Teto Bazin",
                "margem_bazin_%": "Margem vs Teto", "dy_12m_%": "DY 12m",
                "status_bazin": "Status",
            })
            .style.format({
                "Cotação": "R$ {:.2f}",
                "Div/cota 12m (R$)": "R$ {:.4f}",
                "Teto Bazin": "R$ {:.2f}",
                "Margem vs Teto": "{:+.1f}%", "DY 12m": "{:.2f}%",
            }),
            use_container_width=True, hide_index=True,
        )

        df_plot = df_radar[df_radar["preco_teto"] > 0].copy()
        if not df_plot.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_plot["ticker"], y=df_plot["cotacao_atual"],
                name="Cotação atual", marker_color="#00A8E8",
                text=df_plot["cotacao_atual"].round(2), textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=df_plot["ticker"], y=df_plot["preco_teto"],
                name="Preço Teto Bazin", mode="markers+lines",
                marker=dict(color="#00E5A0", size=12, symbol="diamond"),
                line=dict(color="#00E5A0", width=2, dash="dot"),
            ))
            fig.update_layout(
                title="Cotação Atual vs Preço Teto de Bazin",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"), height=420,
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                legend=dict(orientation="h", y=1.1), hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)


# ── ABA 1: DASHBOARD ───────────────────────────────────────────────────
with tabs[1]:
    df_acoes = enriquecer(carregar_ativos("acoes", USER_ID), "acao")
    df_fiis = enriquecer(carregar_ativos("fiis", USER_ID), "fii")

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

    renda_mensal = (
        (df_acoes["renda_mensal_est"].sum() if not df_acoes.empty else 0)
        + (df_fiis["renda_mensal_est"].sum() if not df_fiis.empty else 0)
    )
    dy_medio = dy_medio_carteira(df_acoes, df_fiis)

    df_todos = pd.concat(
        [df_acoes.assign(classe="Ação"), df_fiis.assign(classe="FII")],
        ignore_index=True,
    ) if (not df_acoes.empty or not df_fiis.empty) else pd.DataFrame()

    if not df_todos.empty:
        fortes = df_todos[df_todos["status_key"] == "forte"]
        bons = df_todos[df_todos["status_key"] == "bom"]
        if not fortes.empty:
            st.success(
                f"🎯 **{len(fortes)} ativo(s) com COMPRA FORTE**: "
                f"{', '.join(fortes['ticker'].tolist())}"
            )
        if not bons.empty:
            st.info(
                f"✨ **{len(bons)} ativo(s) em BOM MOMENTO**: "
                f"{', '.join(bons['ticker'].tolist())}"
            )

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Patrimônio Total", f"R$ {total_geral:,.2f}")
    with c2: metric_card("Total Investido", f"R$ {investido:,.2f}")
    with c3:
        sign = "+" if lucro >= 0 else ""
        metric_card("Lucro / Prejuízo", f"R$ {lucro:,.2f}",
                    f"{sign}{rent:.2f}%", "up" if lucro >= 0 else "down")
    with c4:
        metric_card("Renda Passiva Est.", f"R$ {renda_mensal:,.2f}/mês",
                    f"DY médio {dy_medio:.2f}%", "neutral")

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
            fig = px.pie(pd.DataFrame(dados), names="Ativo", values="Valor",
                         hole=0.55, color="Tipo",
                         color_discrete_map={"Ação": "#00A8E8", "FII": "#00E5A0"})
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(
                showlegend=True, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6EDF7"),
                margin=dict(t=10, b=10, l=10, r=10), height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section("📊 Ações vs FIIs")
        tot_a = df_acoes["valor_atual"].sum() if not df_acoes.empty else 0
        tot_f = df_fiis["valor_atual"].sum() if not df_fiis.empty else 0
        if tot_a + tot_f > 0:
            df_comp = pd.DataFrame({"Classe": ["Ações", "FIIs"], "Valor": [tot_a, tot_f]})
            fig = px.bar(df_comp, x="Classe", y="Valor", color="Classe",
                         text_auto=".2s",
                         color_discrete_map={"Ações": "#00A8E8", "FIIs": "#00E5A0"})
            fig.update_traces(textposition="outside")
            fig.update_layout(
                showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6EDF7"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                height=400, margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Tabelas com coluna "Div/cota 12m"
    for titulo, df_ in [("📋 Ações", df_acoes), ("🏢 Fundos Imobiliários", df_fiis)]:
        section(titulo)
        if df_.empty:
            st.info("Nenhum cadastrado.")
            continue
        cols = ["ticker", "quantidade", "preco_medio", "cotacao_atual",
                "div_cota_12m", "preco_teto", "margem_bazin_%", "status_bazin",
                "valor_atual", "rentabilidade_%", "dy_12m_%"]
        st.dataframe(
            df_[cols].rename(columns={
                "ticker": "Ticker", "quantidade": "Qtd", "preco_medio": "PM",
                "cotacao_atual": "Cotação", "div_cota_12m": "Div/cota 12m (R$)",
                "preco_teto": "Teto Bazin",
                "margem_bazin_%": "Margem", "status_bazin": "Status",
                "valor_atual": "Valor Atual", "rentabilidade_%": "Rent.",
                "dy_12m_%": "DY 12m",
            }).style.format({
                "PM": "R$ {:.2f}", "Cotação": "R$ {:.2f}",
                "Div/cota 12m (R$)": "R$ {:.4f}",
                "Teto Bazin": "R$ {:.2f}",
                "Margem": "{:+.1f}%", "Valor Atual": "R$ {:.2f}",
                "Rent.": "{:+.2f}%", "DY 12m": "{:.2f}%",
            }),
            use_container_width=True, hide_index=True,
        )

    section("📥 Exportar Carteira")
    e1, e2 = st.columns(2)
    if not df_acoes.empty or not df_fiis.empty:
        df_export = pd.concat(
            [df_acoes.assign(classe="Ação"), df_fiis.assign(classe="FII")],
            ignore_index=True,
        )
        csv = df_export.to_csv(index=False).encode("utf-8")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
            df_export.to_excel(w, sheet_name="Carteira", index=False)
        e1.download_button("⬇️ Baixar CSV", csv, f"carteira_{date.today()}.csv",
                           "text/csv", use_container_width=True)
        e2.download_button("⬇️ Baixar Excel", buf.getvalue(),
                           f"carteira_{date.today()}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)


# ── ABA 2: CADASTRAR ───────────────────────────────────────────────────
with tabs[2]:
    section("➕ Novo Ativo")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        tipo = st.selectbox("Tipo", ["Ação", "FII"], key="cad_tipo")
    with c2:
        ticker = st.text_input(
            "Ticker", placeholder="PETR4 / MXRF11", key="cad_ticker",
            help="Digite e pressione Enter para buscar cotação e Bazin.",
        ).upper().strip()
    with c3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        buscar_btn = st.button("🔍 Buscar cotação + Bazin", use_container_width=True)

    assinatura_nova = f"{ticker}|{tipo}" if ticker else ""
    assinatura_antiga = st.session_state.get("cad_assinatura_ativa", "")

    if assinatura_nova != assinatura_antiga and ticker:
        for k in list(st.session_state.keys()):
            if k.startswith("proj_") or k in ("cot_info", "cot_ticker"):
                try:
                    del st.session_state[k]
                except Exception:
                    pass
        st.session_state["cad_assinatura_ativa"] = assinatura_nova

    ticker_mudou = ticker and st.session_state.get("cot_ticker") != ticker
    if (buscar_btn or ticker_mudou) and ticker:
        with st.spinner(f"Analisando {ticker}..."):
            info = get_ativo_info(ticker, "acao" if tipo == "Ação" else "fii")
        st.session_state["cot_info"] = info
        st.session_state["cot_ticker"] = ticker

    info_cad = st.session_state.get("cot_info")

    if info_cad and st.session_state.get("cot_ticker") == ticker:
        st.markdown(
            f"""<div class="bazin-card">
                <div class="cell">
                    <div class="lbl">TICKER</div>
                    <div class="val">{info_cad.ticker}</div>
                </div>
                <div class="cell">
                    <div class="lbl">COTAÇÃO ATUAL</div>
                    <div class="val" style="color:#00A8E8;">R$ {info_cad.cotacao:.2f}</div>
                </div>
                <div class="cell">
                    <div class="lbl">PREÇO TETO BAZIN</div>
                    <div class="val" style="color:#00E5A0;">R$ {info_cad.preco_teto:.2f}</div>
                </div>
                <div class="cell">
                    <div class="lbl">DY 12M</div>
                    <div class="val" style="color:#FACC15;">{info_cad.dy_12m*100:.2f}%</div>
                </div>
                <div class="cell">
                    <div class="lbl">MARGEM VS TETO</div>
                    <div class="val" style="color:{info_cad.cor};">{info_cad.margem:+.1f}%</div>
                </div>
                <div>{status_pill_html(info_cad)}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if info_cad.status_key in ("forte", "bom"):
            st.success("✅ Bom momento de compra segundo o método Bazin.")
        elif info_cad.status_key == "proximo":
            st.warning("⚠️ Próximo do teto. Avalie a margem de segurança.")
        elif info_cad.status_key == "caro":
            st.error("🚫 Acima do preço teto. Considere aguardar correção.")
        else:
            st.info("ℹ️ Sem histórico de dividendos suficiente para calcular o teto.")

    # 💵 Bloco de dividendo por cota — usa função central
    if info_cad and info_cad.dy_12m > 0:
        section("💵 Dividendo pago por cota — histórico real dos últimos 12 meses")
        render_dividendo_por_cota(
            info_cad.ticker, info_cad.tipo,
            cotacao=info_cad.cotacao,
            compacto=False,
            key_prefix="cad",
        )

    # ═══ Modo de compra ═══
    section("🛒 Como você quer registrar a compra?")
    modo = st.radio(
        "Modo de compra",
        ["🎯 Por quantidade de cotas", "💰 Por valor em R$"],
        horizontal=True, label_visibility="collapsed", key="cad_modo",
    )

    cot_disponivel = float(info_cad.cotacao) if info_cad and info_cad.cotacao > 0 else 0.0
    cfg_cad = carregar_config(USER_ID)

    valor_investir = None
    descontar_saldo = True
    if modo.startswith("💰"):
        cA, cB = st.columns([1, 2])
        with cA:
            valor_investir = st.number_input(
                "💵 Valor que quero investir (R$)",
                min_value=0.01, value=1000.0, step=100.0,
                format="%.2f", key="cad_valor_investir",
            )
            descontar_saldo = st.checkbox(
                "💳 Descontar do saldo disponível", value=True,
                help="Se marcado, o valor realmente gasto é deduzido do saldo.",
            )
            if descontar_saldo:
                st.caption(f"Saldo atual: R$ {cfg_cad.get('valor_disponivel', 0):,.2f}")
        with cB:
            if cot_disponivel > 0:
                qtd_calc = int(valor_investir // cot_disponivel)
                total_gasto = qtd_calc * cot_disponivel
                sobra = valor_investir - total_gasto
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, rgba(0,229,160,0.12), rgba(0,168,232,0.06));
                                border: 1px solid rgba(0,229,160,0.35); border-radius: 14px;
                                padding: 18px 22px; margin-top: 6px;">
                        <div style="color:#A0AEC0; font-size:11px; font-weight:700; letter-spacing:1px;">
                            CÁLCULO AUTOMÁTICO
                        </div>
                        <div style="color:#FFFFFF; font-size:22px; font-weight:900; margin-top:6px;">
                            🎯 Você consegue comprar <span style="color:#00E5A0;">{qtd_calc} cotas</span>
                        </div>
                        <div style="color:#A0AEC0; font-size:13px; margin-top:8px;">
                            💵 Orçamento: <b style="color:#FFFFFF;">R$ {valor_investir:,.2f}</b> ÷ 
                            R$ {cot_disponivel:.2f} = <b style="color:#FFFFFF;">{qtd_calc} cotas</b>
                        </div>
                        <div style="color:#A0AEC0; font-size:13px; margin-top:4px;">
                            💸 Custo real: <b style="color:#FF5C7A;">R$ {total_gasto:,.2f}</b> · 
                            🔄 Troco: <b style="color:#00E5A0;">R$ {sobra:,.2f}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("⚠️ Busque a cotação do ticker acima para calcular automaticamente.")

    # ═══ Detalhes da compra ═══
    section("📊 Detalhes da compra")
    c1, c2 = st.columns(2)
    with c1:
        if modo.startswith("🎯"):
            quantidade = st.number_input(
                "Quantidade de cotas", min_value=1, step=1, value=100,
                key="cad_qtd_preview",
            )
        else:
            if cot_disponivel > 0 and valor_investir:
                quantidade = int(valor_investir // cot_disponivel)
                st.markdown("**Quantidade calculada automaticamente**")
                st.markdown(
                    f"<div style='font-size:32px; font-weight:900; color:#00E5A0; "
                    f"padding: 8px 0; letter-spacing:-0.5px;'>{quantidade} cotas</div>",
                    unsafe_allow_html=True,
                )
            else:
                quantidade = 0
                st.markdown("**Quantidade calculada automaticamente**")
                st.markdown(
                    "<div style='color:#FF5C7A; font-weight:700; padding:8px 0; "
                    "font-size:16px;'>Informe o ticker e o valor acima</div>",
                    unsafe_allow_html=True,
                )

    with c2:
        cot_val = cot_disponivel if cot_disponivel > 0 else 10.0
        usar_auto = st.checkbox(
            "🎯 Usar cotação do mercado", value=(cot_disponivel > 0),
            help="Desmarque para digitar o preço manualmente.",
            key="cad_usar_auto",
        )
        if usar_auto:
            preco_preview = float(cot_val)
            st.markdown("**Preço (cotação do mercado)**")
            st.markdown(
                f"<div style='font-size:32px; font-weight:900; color:#00E5A0; "
                f"padding: 8px 0; letter-spacing:-0.5px;'>R$ {preco_preview:.2f}</div>",
                unsafe_allow_html=True,
            )
        else:
            preco_preview = st.number_input(
                "Preço manual (R$)", min_value=0.01, step=0.01,
                format="%.2f", value=float(cot_val), key="cad_preco_manual",
            )

    # ═══ PROJEÇÃO EDITÁVEL ═══
    if info_cad and quantidade > 0 and preco_preview > 0:
        section("💰 Projeção de lucro com dividendos — EDITÁVEL")
        st.caption(
            "🖊️ Ajuste os campos abaixo livremente — o cálculo se atualiza em tempo real. "
            "Trocar de ativo reinicia tudo automaticamente."
        )

        tag_ativo = f"{info_cad.ticker}_{info_cad.tipo}"

        e1, e2, e3, e4 = st.columns(4)
        with e1:
            qtd_proj = st.number_input(
                "Quantidade de cotas",
                min_value=1, step=1, value=int(quantidade),
                key=f"proj_qtd_{tag_ativo}",
            )
        with e2:
            preco_proj = st.number_input(
                "Preço por cota (R$)",
                min_value=0.01, step=0.01, format="%.2f",
                value=float(preco_preview),
                key=f"proj_preco_{tag_ativo}",
            )
        with e3:
            dy_base = info_cad.dy_12m * 100 if info_cad.dy_12m > 0 else 8.0
            dy_proj = st.slider(
                "DY anual (%)",
                min_value=0.0, max_value=25.0,
                value=float(round(dy_base, 2)),
                step=0.25,
                help=f"Preenchido com o DY real de 12 meses de {info_cad.ticker} ({dy_base:.2f}%).",
                key=f"proj_dy_{tag_ativo}",
            )
        with e4:
            meses_proj = st.slider(
                "Horizonte (meses)",
                min_value=6, max_value=360, value=60, step=6,
                key=f"proj_meses_{tag_ativo}",
            )

        reinvestir_proj = st.checkbox(
            "♻️ Reinvestir dividendos automaticamente (juros compostos)",
            value=True, key=f"proj_reinvest_{tag_ativo}",
        )

        proj = projetar_renda_ativo(
            quantidade=qtd_proj,
            preco_unitario=preco_proj,
            dy_anual=dy_proj / 100,
            meses=meses_proj,
            reinvestir=reinvestir_proj,
        )
        df_proj = proj["df"]

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            metric_card("💵 Investimento", f"R$ {proj['investimento_total']:,.2f}",
                        f"{qtd_proj} cotas × R$ {preco_proj:.2f}", "neutral")
        with k2:
            metric_card("📅 Dividendo por cota", f"R$ {proj['div_cota_ano']:.4f}",
                        f"ano · R$ {proj['div_cota_mes']:.4f}/mês", "up")
        with k3:
            metric_card("💸 Renda mensal est.", f"R$ {proj['renda_mensal_ini']:,.2f}",
                        f"R$ {proj['renda_anual_ini']:,.2f}/ano", "up")
        with k4:
            metric_card("⏱️ Payback", f"{proj['payback_meses']:.0f} meses",
                        f"DY {dy_proj:.2f}% a.a.", "neutral")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(0,229,160,0.15), rgba(0,168,232,0.08));
                        border: 1px solid rgba(0,229,160,0.4); border-radius: 16px;
                        padding: 22px 26px; margin: 12px 0;">
                <div style="color:#A0AEC0; font-size:11px; font-weight:700; letter-spacing:1.2px;">
                    🎯 PROJEÇÃO COM BASE NO HISTÓRICO REAL DE DIVIDENDOS
                </div>
                <div style="color:#FFFFFF; font-size:18px; margin-top:10px; line-height:1.6;">
                    Com <b style="color:#00E5A0;">{qtd_proj} cotas</b> de 
                    <b style="color:#00E5A0;">{info_cad.ticker}</b> a 
                    <b>R$ {preco_proj:.2f}</b>, você receberá aproximadamente
                    <b style="color:#00E5A0; font-size:22px;">R$ {proj['renda_anual_ini']:,.2f} por ano</b>
                    em dividendos
                    <span style="color:#A0AEC0;">(≈ R$ {proj['renda_mensal_ini']:,.2f}/mês)</span>.
                </div>
                <div style="color:#A0AEC0; font-size:13px; margin-top:10px;">
                    ⏱️ Em <b style="color:#FFFFFF;">{proj['payback_meses']:.0f} meses</b> 
                    (≈ {proj['payback_meses']/12:.1f} anos) os dividendos terão pago todo o investimento.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        marcos = [12, 24, 36, 60]
        marcos = [m for m in marcos if m <= len(df_proj)]
        cols_m = st.columns(len(marcos))
        for i, m in enumerate(marcos):
            linha = df_proj[df_proj["Mês"] == m].iloc[0]
            with cols_m[i]:
                st.markdown(
                    f"""
                    <div style="background: rgba(19,28,47,0.7); border: 1px solid rgba(255,255,255,0.08);
                                border-radius: 12px; padding: 14px 16px; text-align: center;">
                        <div style="color:#A0AEC0; font-size:11px; font-weight:700; letter-spacing:1px;">
                            EM {m} MESES
                        </div>
                        <div style="color:#00E5A0; font-size:18px; font-weight:800; margin-top:6px;">
                            R$ {linha['Renda acumulada (R$)']:,.2f}
                        </div>
                        <div style="color:#A0AEC0; font-size:11px; margin-top:2px;">
                            renda acumulada
                        </div>
                        <div style="color:#FFFFFF; font-size:13px; font-weight:700; margin-top:8px;">
                            {linha['Cotas']:.1f} cotas
                        </div>
                        <div style="color:#A0AEC0; font-size:11px;">
                            R$ {linha['Patrimônio (R$)']:,.2f} em patrimônio
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_proj["Mês"], y=df_proj["Renda acumulada (R$)"],
            mode="lines", name="💰 Renda acumulada",
            line=dict(color="#00E5A0", width=3),
            fill="tozeroy", fillcolor="rgba(0,229,160,0.12)",
        ))
        fig.add_trace(go.Scatter(
            x=df_proj["Mês"], y=df_proj["Patrimônio (R$)"],
            mode="lines", name="📈 Patrimônio",
            line=dict(color="#00A8E8", width=3, dash="dot"),
        ))
        fig.add_hline(
            y=proj["investimento_total"],
            line_dash="dash", line_color="#FF5C7A",
            annotation_text=f"Investimento: R$ {proj['investimento_total']:,.2f}",
            annotation_position="top left",
            annotation_font_color="#FF5C7A",
        )
        fig.update_layout(
            title=f"Projeção de {qtd_proj} cotas de {info_cad.ticker} — {meses_proj} meses",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E6EDF7"), height=420,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Mês"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="R$"),
            legend=dict(orientation="h", y=1.12), hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Ver projeção mês a mês"):
            st.dataframe(
                df_proj.style.format({
                    "Renda no mês (R$)": "R$ {:.2f}",
                    "Renda acumulada (R$)": "R$ {:.2f}",
                    "Cotas": "{:.2f}",
                    "Patrimônio (R$)": "R$ {:.2f}",
                }),
                use_container_width=True, hide_index=True, height=320,
            )

        section("💾 Salvar esta projeção no Supabase")
        with st.form(f"form_salvar_proj_{tag_ativo}"):
            obs_proj = st.text_input(
                "Observação (opcional)",
                placeholder="Ex: meta 2026, cenário conservador...",
                key=f"proj_obs_{tag_ativo}",
            )
            if st.form_submit_button("💾 Salvar projeção", use_container_width=True):
                dados = {
                    "ticker": info_cad.ticker,
                    "tipo": info_cad.tipo,
                    "quantidade": float(qtd_proj),
                    "preco": float(preco_proj),
                    "dy_anual": float(dy_proj / 100),
                    "meses": int(meses_proj),
                    "reinvestir": bool(reinvestir_proj),
                    "investimento_total": float(proj["investimento_total"]),
                    "renda_mensal": float(proj["renda_mensal_ini"]),
                    "renda_anual": float(proj["renda_anual_ini"]),
                    "renda_acumulada_final": float(df_proj.iloc[-1]["Renda acumulada (R$)"]),
                    "patrimonio_final": float(df_proj.iloc[-1]["Patrimônio (R$)"]),
                    "payback_meses": float(proj["payback_meses"]),
                    "observacao": obs_proj if obs_proj else None,
                }
                try:
                    salvar_projecao(dados, USER_ID)
                    st.success(
                        f"✅ Projeção de {info_cad.ticker} salva! "
                        f"Veja na aba **💾 Projeções Salvas**."
                    )
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    section("✅ Confirmar cadastro do ativo")
    with st.form("form_novo"):
        c1, c2 = st.columns(2)
        with c1:
            data_compra = st.date_input("Data da compra", value=date.today())
        with c2:
            registrar = st.checkbox("Registrar no histórico de aportes", value=True)

        submitted = st.form_submit_button("💾 Cadastrar ativo", use_container_width=True)

        if submitted:
            if not ticker:
                st.error("Informe o ticker.")
            elif usar_auto and cot_val <= 0:
                st.error("Sem cotação disponível. Desmarque 'Usar cotação do mercado'.")
            elif modo.startswith("💰") and (valor_investir is None or valor_investir <= 0):
                st.error("Informe um valor válido para investir.")
            else:
                preco_final = float(preco_preview)

                if modo.startswith("🎯"):
                    qtd_final = int(quantidade)
                    total_gasto_final = qtd_final * preco_final
                    sobra_final = 0.0
                else:
                    qtd_final = int(quantidade)
                    if qtd_final <= 0:
                        st.error("Valor insuficiente para comprar 1 cota.")
                        st.stop()
                    total_gasto_final = qtd_final * preco_final
                    sobra_final = valor_investir - total_gasto_final

                tabela = "acoes" if tipo == "Ação" else "fiis"

                try:
                    salvar_ativo(tabela, {
                        "ticker": ticker,
                        "quantidade": qtd_final,
                        "preco_medio": preco_final,
                        "data_compra": str(data_compra),
                    }, USER_ID)

                    if registrar:
                        registrar_aporte(ticker, tipo, qtd_final, preco_final, data_compra, USER_ID)

                    if modo.startswith("💰") and descontar_saldo:
                        saldo_atual = float(cfg_cad.get("valor_disponivel", 0.0))
                        novo_saldo = saldo_atual - total_gasto_final
                        atualizar_config(USER_ID, valor=novo_saldo)
                        msg_saldo = (
                            f" · 💳 Saldo: R$ {saldo_atual:,.2f} → "
                            f"R$ {novo_saldo:,.2f} (sobra: R$ {sobra_final:.2f})"
                        )
                    else:
                        msg_saldo = ""

                    origem = "mercado" if usar_auto else "manual"
                    st.success(
                        f"✅ {tipo} **{ticker}** cadastrado — "
                        f"{qtd_final} cotas × R$ {preco_final:.2f} "
                        f"= **R$ {total_gasto_final:,.2f}** ({origem}){msg_saldo}"
                    )

                    for k in ("cot_info", "cot_ticker", "cad_assinatura_ativa"):
                        st.session_state.pop(k, None)
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")


# ── ABA 3: GERENCIAR ───────────────────────────────────────────────────
with tabs[3]:
    section("✏️ Editar / Excluir")
    tipo_edit = st.radio(
        "Tabela", ["Ações", "FIIs"], horizontal=True, label_visibility="collapsed"
    )
    tabela = "acoes" if tipo_edit == "Ações" else "fiis"
    tipo_key = "acao" if tipo_edit == "Ações" else "fii"
    df_edit = carregar_ativos(tabela, USER_ID)

    if df_edit.empty:
        st.info("Nada para editar.")
    else:
        opcoes = {
            f"{r['ticker']} — {r['quantidade']} un.": r["id"]
            for _, r in df_edit.iterrows()
        }
        sel = st.selectbox("Selecione o ativo", list(opcoes.keys()))
        id_sel = opcoes[sel]
        reg = df_edit[df_edit["id"] == id_sel].iloc[0]

        with st.spinner("Consultando mercado..."):
            info_edit = get_ativo_info(reg["ticker"], tipo_key)

        st.markdown(
            f"""<div class="bazin-card">
                <div class="cell">
                    <div class="lbl">PREÇO MÉDIO PAGO</div>
                    <div class="val">R$ {reg['preco_medio']:.2f}</div>
                </div>
                <div class="cell">
                    <div class="lbl">COTAÇÃO ATUAL</div>
                    <div class="val" style="color:#00A8E8;">R$ {info_edit.cotacao:.2f}</div>
                </div>
                <div class="cell">
                    <div class="lbl">TETO BAZIN</div>
                    <div class="val" style="color:#00E5A0;">R$ {info_edit.preco_teto:.2f}</div>
                </div>
                <div class="cell">
                    <div class="lbl">MARGEM VS TETO</div>
                    <div class="val" style="color:{info_edit.cor};">{info_edit.margem:+.1f}%</div>
                </div>
                <div>{status_pill_html(info_edit)}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # 💵 Dividendo por cota do ativo selecionado
        if info_edit.dy_12m > 0:
            section(f"💵 Dividendo pago por cota — {reg['ticker']}")
            render_dividendo_por_cota(
                reg["ticker"], tipo_key,
                cotacao=info_edit.cotacao,
                compacto=False,
                key_prefix=f"edit_{id_sel}",
            )

        with st.form("form_edit"):
            c1, c2 = st.columns(2)
            with c1:
                nova_qtd = st.number_input("Quantidade", min_value=1, value=int(reg["quantidade"]))
                novo_tk = st.text_input("Ticker", value=reg["ticker"])
            with c2:
                usar_mkt = st.checkbox(
                    f"🎯 Usar cotação atual (R$ {info_edit.cotacao:.2f})",
                    value=False, key=f"usar_mkt_{id_sel}",
                )
                novo_preco = st.number_input(
                    "Preço médio (R$)", min_value=0.01,
                    value=float(info_edit.cotacao if usar_mkt else reg["preco_medio"]),
                    format="%.2f", disabled=usar_mkt,
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
                }, USER_ID)
                st.success("Atualizado!")
                st.rerun()
            if col_b.form_submit_button("🗑️ Excluir", use_container_width=True):
                deletar_ativo(tabela, id_sel, USER_ID)
                st.success("Excluído!")
                st.rerun()


# ── ABA 4: PROJEÇÕES ───────────────────────────────────────────────────
with tabs[4]:
    section("📈 Projeção de Juros Compostos da Carteira")

    df_a_proj = enriquecer(carregar_ativos("acoes", USER_ID), "acao")
    df_f_proj = enriquecer(carregar_ativos("fiis", USER_ID), "fii")

    dy_carteira = (
        dy_medio_carteira(df_a_proj, df_f_proj) / 100
        if not (df_a_proj.empty and df_f_proj.empty) else 0.10
    )
    if dy_carteira <= 0:
        dy_carteira = 0.10

    st.info(
        f"💡 DY médio ponderado da sua carteira atual: "
        f"**{dy_carteira * 100:.2f}% a.a.** (usado como base da projeção)"
    )

    cfg = carregar_config(USER_ID)
    c1, c2 = st.columns(2)
    with c1:
        patrimonio_ini = st.number_input(
            "Patrimônio inicial (R$)", min_value=0.0,
            value=float(cfg.get("valor_disponivel", 0) or 10000),
            step=1000.0, format="%.2f",
        )
        dy_input = st.slider(
            "DY anual esperado (%)", 0.0, 25.0, float(dy_carteira * 100), 0.25,
        )
    with c2:
        meses = st.slider("Horizonte (meses)", 6, 360, 120, 6)
        aporte = st.number_input(
            "Aporte mensal (R$)", min_value=0.0, value=1000.0, step=100.0
        )

    reinvestir = st.checkbox("♻️ Reinvestir dividendos", value=True)

    if st.button("🚀 Gerar 3 cenários", use_container_width=True):
        cenarios = {
            "Pessimista": dy_input * 0.6 / 100,
            "Base": dy_input / 100,
            "Otimista": dy_input * 1.4 / 100,
        }
        cores = {"Pessimista": "#FF5C7A", "Base": "#00A8E8", "Otimista": "#00E5A0"}

        fig = go.Figure()
        for nome, dy_c in cenarios.items():
            df_p = projetar(patrimonio_ini, dy_c, meses, aporte, reinvestir)
            fig.add_trace(go.Scatter(
                x=df_p["Mês"], y=df_p["Patrimônio"],
                mode="lines", name=nome, line=dict(color=cores[nome], width=3),
            ))
        fig.update_layout(
            title="Projeção de Patrimônio — 3 Cenários",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E6EDF7"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Mês"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="R$"),
            hovermode="x unified", height=480,
            legend=dict(orientation="h", y=1.05),
        )
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(3)
        for i, (nome, dy_c) in enumerate(cenarios.items()):
            df_p = projetar(patrimonio_ini, dy_c, meses, aporte, reinvestir)
            final = df_p.iloc[-1]
            with cols[i]:
                metric_card(nome, f"R$ {final['Patrimônio']:,.0f}",
                            f"Div. acum.: R$ {final['Dividendos acumulados']:,.0f}",
                            "up" if i == 2 else ("neutral" if i == 1 else "down"))

    section("🎯 Meta de Independência Financeira")
    meta = st.number_input(
        "Renda passiva mensal desejada (R$)", min_value=0.0,
        value=float(cfg.get("meta_renda_passiva", 0) or 5000), step=500.0,
    )
    if st.button("💾 Salvar meta", use_container_width=True):
        atualizar_config(USER_ID, meta=meta)
        st.success("Meta salva!")
    if meta > 0 and dy_input > 0:
        patrimonio_meta = (meta * 12) / (dy_input / 100)
        st.info(
            f"📌 Com DY de {dy_input:.2f}% a.a., você precisa de "
            f"**R$ {patrimonio_meta:,.2f}** para gerar R$ {meta:,.2f}/mês."
        )


# ── ABA 5: PROJEÇÕES SALVAS ────────────────────────────────────────────
with tabs[5]:
    section("💾 Projeções Salvas")

    df_proj_salvas = carregar_projecoes(USER_ID)

    if df_proj_salvas.empty:
        st.info(
            "Nenhuma projeção salva ainda. Vá em **➕ Cadastrar**, "
            "monte uma projeção e clique em **💾 Salvar projeção**."
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Total de projeções", str(len(df_proj_salvas)))
        with c2:
            soma_inv = df_proj_salvas["investimento_total"].sum()
            metric_card("Investimento simulado", f"R$ {soma_inv:,.2f}")
        with c3:
            soma_renda = df_proj_salvas["renda_mensal"].sum()
            metric_card("Renda mensal projetada", f"R$ {soma_renda:,.2f}")
        with c4:
            soma_patr = df_proj_salvas["patrimonio_final"].sum()
            metric_card("Patrimônio final", f"R$ {soma_patr:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        cols = ["ticker", "tipo", "quantidade", "preco", "dy_anual",
                "meses", "reinvestir", "investimento_total", "renda_mensal",
                "renda_anual", "renda_acumulada_final", "patrimonio_final",
                "payback_meses", "observacao"]
        st.dataframe(
            df_proj_salvas[cols].rename(columns={
                "ticker": "Ticker", "tipo": "Tipo", "quantidade": "Qtd",
                "preco": "Preço", "dy_anual": "DY", "meses": "Meses",
                "reinvestir": "Reinveste", "investimento_total": "Investimento",
                "renda_mensal": "Renda/mês", "renda_anual": "Renda/ano",
                "renda_acumulada_final": "Renda acum.",
                "patrimonio_final": "Patrimônio", "payback_meses": "Payback (m)",
                "observacao": "Obs.",
            }).style.format({
                "Preço": "R$ {:.2f}",
                "DY": "{:.2%}",
                "Investimento": "R$ {:,.2f}",
                "Renda/mês": "R$ {:,.2f}",
                "Renda/ano": "R$ {:,.2f}",
                "Renda acum.": "R$ {:,.2f}",
                "Patrimônio": "R$ {:,.2f}",
                "Payback (m)": "{:.0f}",
            }),
            use_container_width=True, hide_index=True,
        )

        if len(df_proj_salvas) > 0:
            df_plot = df_proj_salvas.sort_values("renda_anual", ascending=False).head(15)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_plot["ticker"], y=df_plot["renda_anual"],
                name="Renda anual",
                marker_color="#00E5A0",
                text=df_plot["renda_anual"].round(2), textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=df_plot["ticker"], y=df_plot["patrimonio_final"],
                name="Patrimônio final", mode="markers+lines", yaxis="y2",
                marker=dict(color="#00A8E8", size=10),
                line=dict(color="#00A8E8", width=2, dash="dot"),
            ))
            fig.update_layout(
                title="Comparativo das projeções salvas",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"), height=420,
                yaxis=dict(title="Renda anual (R$)",
                           gridcolor="rgba(255,255,255,0.05)"),
                yaxis2=dict(title="Patrimônio final (R$)", overlaying="y",
                            side="right", showgrid=False),
                legend=dict(orientation="h", y=1.1),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

        section("🗑️ Excluir uma projeção")
        del_id = st.selectbox(
            "Selecione a projeção para excluir:",
            options=df_proj_salvas["id"].tolist(),
            format_func=lambda x: (
                f"{df_proj_salvas[df_proj_salvas['id'] == x]['ticker'].iloc[0]} "
                f"— {df_proj_salvas[df_proj_salvas['id'] == x]['quantidade'].iloc[0]:.0f} cotas "
                f"({df_proj_salvas[df_proj_salvas['id'] == x]['meses'].iloc[0]} meses)"
            ),
            key="del_proj_sel",
        )
        if st.button("🗑️ Excluir projeção", use_container_width=True):
            try:
                deletar_projecao(del_id, USER_ID)
                st.success("Projeção excluída!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir: {e}")


# ── ABA 6: REBALANCEAR ─────────────────────────────────────────────────
with tabs[6]:
    section("🎯 Rebalanceamento Inteligente")

    df_a = carregar_ativos("acoes", USER_ID)
    df_f = carregar_ativos("fiis", USER_ID)

    if df_a.empty and df_f.empty:
        st.info("Cadastre ativos primeiro.")
    else:
        df_a_e = enriquecer(df_a, "acao")
        df_f_e = enriquecer(df_f, "fii")

        cfg_reb = carregar_config(USER_ID)
        saldo_disp_reb = float(cfg_reb.get("valor_disponivel", 0.0))

        valor_aporte = st.number_input(
            "Valor disponível para aporte (R$)", min_value=0.0,
            value=saldo_disp_reb if saldo_disp_reb > 0 else 1000.0,
            step=100.0, help="Por padrão usa o saldo disponível da barra lateral.",
        )
        priorizar_bazin = st.checkbox(
            "🎯 Priorizar ativos abaixo do Preço Teto de Bazin", value=True,
        )

        todas = []
        for _, r in df_a_e.iterrows():
            todas.append({
                "ticker": r["ticker"], "tipo": "Ação", "valor": r["valor_atual"],
                "status_key": r["status_key"], "margem": r["margem_bazin_%"],
                "teto": r["preco_teto"],
            })
        for _, r in df_f_e.iterrows():
            todas.append({
                "ticker": r["ticker"], "tipo": "FII", "valor": r["valor_atual"],
                "status_key": r["status_key"], "margem": r["margem_bazin_%"],
                "teto": r["preco_teto"],
            })

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
            tot = sum(a["valor"] for a in todas)
            novo_tot = tot + valor_aporte
            rows = []
            for a in todas:
                tk = a["ticker"]
                alvo = novo_tot * (metas[tk] / 100)
                gap = max(alvo - a["valor"], 0)
                rows.append({
                    "Ticker": tk, "Tipo": a["tipo"],
                    "Status": "🟢" if a["status_key"] in ("forte", "bom")
                              else ("🟡" if a["status_key"] == "proximo" else "🔴"),
                    "Atual (R$)": a["valor"],
                    "% Atual": (a["valor"] / tot * 100) if tot > 0 else 0,
                    "Meta %": metas[tk], "Alvo (R$)": alvo, "Gap (R$)": gap,
                    "status_key": a["status_key"],
                })
            df_reb = pd.DataFrame(rows)

            if priorizar_bazin:
                pesos = df_reb["Gap (R$)"].copy()
                pesos = pesos * np.where(
                    df_reb["status_key"].isin(["forte", "bom"]), 1.5, 1.0
                )
                pesos = pesos * np.where(df_reb["status_key"] == "caro", 0.3, 1.0)
            else:
                pesos = df_reb["Gap (R$)"]

            if pesos.sum() > 0:
                df_reb["Aportar (R$)"] = pesos / pesos.sum() * valor_aporte
            else:
                df_reb["Aportar (R$)"] = 0.0

            df_reb = df_reb.sort_values("Aportar (R$)", ascending=False).reset_index(drop=True)

            st.dataframe(
                df_reb[["Ticker", "Tipo", "Status", "Atual (R$)", "% Atual",
                        "Meta %", "Alvo (R$)", "Aportar (R$)"]]
                .style.format({
                    "Atual (R$)": "R$ {:,.2f}", "% Atual": "{:.1f}%",
                    "Meta %": "{:.1f}%", "Alvo (R$)": "R$ {:,.2f}",
                    "Aportar (R$)": "R$ {:,.2f}",
                }),
                use_container_width=True, hide_index=True,
            )

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="% Atual", x=df_reb["Ticker"], y=df_reb["% Atual"],
                marker_color="#00A8E8", text=df_reb["% Atual"].round(1),
                textposition="outside",
            ))
            fig.add_trace(go.Bar(
                name="Meta %", x=df_reb["Ticker"], y=df_reb["Meta %"],
                marker_color="#00E5A0", text=df_reb["Meta %"].round(1),
                textposition="outside",
            ))
            fig.update_layout(
                barmode="group", title="Atual vs Meta",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF7"), height=400,
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                legend=dict(orientation="h", y=1.1),
            )
            st.plotly_chart(fig, use_container_width=True)


# ── ABA 7: WATCHLIST ───────────────────────────────────────────────────
with tabs[7]:
    section("👁️ Watchlist — Distância ao Teto Bazin")

    with st.form("form_watch", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        with c1:
            w_tipo = st.selectbox("Tipo", ["Ação", "FII"])
        with c2:
            w_ticker = st.text_input("Ticker").upper().strip()
        with c3:
            w_preco = st.number_input(
                "Preço alvo (R$)", min_value=0.0, step=0.01, format="%.2f"
            )
        with c4:
            w_obs = st.text_input("Observação")
        if st.form_submit_button("➕ Adicionar", use_container_width=True):
            if w_ticker:
                salvar_watchlist(w_ticker, w_tipo, w_preco, w_obs, USER_ID)
                st.success(f"{w_ticker} adicionado!")
                st.rerun()

    df_w = carregar_watchlist(USER_ID)
    if df_w.empty:
        st.info("Watchlist vazia.")
    else:
        linhas = []
        for _, r in df_w.iterrows():
            tipo_key = "acao" if r["tipo"] == "Ação" else "fii"
            info = get_ativo_info(r["ticker"], tipo_key)
            res = get_resumo_dividendos(r["ticker"], tipo_key)
            dist_alvo = (
                (info.cotacao / r["preco_alvo"] - 1) * 100
                if r["preco_alvo"] > 0 else 0
            )
            linhas.append({
                "Ticker": r["ticker"], "Tipo": r["tipo"],
                "Cotação": info.cotacao,
                "Div/cota 12m": res["total_12m"],
                "Último div/cota": res["ultimo"],
                "Preço alvo": r["preco_alvo"],
                "Dist. alvo": dist_alvo, "Teto Bazin": info.preco_teto,
                "Margem Bazin": info.margem, "Status": info.status,
                "Obs.": r["observacao"], "id": r["id"],
            })
        df_w_show = pd.DataFrame(linhas)

        st.dataframe(
            df_w_show.drop(columns=["id"]).style.format({
                "Cotação": "R$ {:.2f}",
                "Div/cota 12m": "R$ {:.4f}",
                "Último div/cota": "R$ {:.4f}",
                "Preço alvo": "R$ {:.2f}",
                "Dist. alvo": "{:+.1f}%", "Teto Bazin": "R$ {:.2f}",
                "Margem Bazin": "{:+.1f}%",
            }),
            use_container_width=True, hide_index=True,
        )

        del_id = st.selectbox(
            "Excluir da watchlist:",
            options=df_w_show["id"].tolist(),
            format_func=lambda x: df_w_show[df_w_show["id"] == x]["Ticker"].iloc[0],
        )
        if st.button("🗑️ Remover", use_container_width=True):
            deletar_watchlist(del_id, USER_ID)
            st.success("Removido!")
            st.rerun()


# ── ABA 8: APORTES ─────────────────────────────────────────────────────
with tabs[8]:
    section("📜 Histórico de Aportes")
    df_ap = carregar_aportes(USER_ID)

    if df_ap.empty:
        st.info("Nenhum aporte registrado.")
    else:
        df_ap["data"] = pd.to_datetime(df_ap["data"])
        df_ap["cotacao_atual"] = df_ap["ticker"].apply(get_cotacao)
        df_ap["preco_teto"] = df_ap.apply(
            lambda r: get_ativo_info(
                r["ticker"], "acao" if r["tipo"] == "Ação" else "fii"
            ).preco_teto,
            axis=1,
        )
        # 💵 Dividendo por cota dos últimos 12 meses
        df_ap["div_cota_12m"] = df_ap.apply(
            lambda r: div_cota_resumo(
                r["ticker"], "acao" if r["tipo"] == "Ação" else "fii"
            ),
            axis=1,
        )
        df_ap["ganho_%"] = np.where(
            df_ap["preco"] > 0,
            (df_ap["cotacao_atual"] / df_ap["preco"] - 1) * 100, 0,
        )

        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Total Aportado", f"R$ {df_ap['total'].sum():,.2f}")
        with c2: metric_card("Nº de Aportes", str(len(df_ap)))
        with c3: metric_card("Aporte Médio", f"R$ {df_ap['total'].mean():,.2f}")

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
            yaxis2=dict(title="Acumulado (R$)", overlaying="y",
                        side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1), hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        section("📋 Detalhamento")
        st.dataframe(
            df_ap[["data", "ticker", "tipo", "quantidade", "preco",
                   "cotacao_atual", "ganho_%", "div_cota_12m",
                   "preco_teto", "total"]]
            .rename(columns={
                "data": "Data", "ticker": "Ticker", "tipo": "Tipo",
                "quantidade": "Qtd", "preco": "Preço pago",
                "cotacao_atual": "Cotação hoje", "ganho_%": "Variação",
                "div_cota_12m": "Div/cota 12m (R$)",
                "preco_teto": "Teto Bazin", "total": "Total",
            })
            .style.format({
                "Preço pago": "R$ {:.2f}", "Cotação hoje": "R$ {:.2f}",
                "Variação": "{:+.2f}%",
                "Div/cota 12m (R$)": "R$ {:.4f}",
                "Teto Bazin": "R$ {:.2f}",
                "Total": "R$ {:.2f}",
            }),
            use_container_width=True, hide_index=True, height=400,
        )
