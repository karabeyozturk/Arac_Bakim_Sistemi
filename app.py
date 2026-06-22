import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

# ─── Sayfa Konfigürasyonu ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoTrack Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS: Premium Koyu Mavi/Turkuaz Tema ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #070d1a;
    font-family: 'Inter', sans-serif;
    color: #c8dff0;
}

/* ── Animated particle background ────────────────────────────────── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(0, 180, 255, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 90%, rgba(0, 100, 200, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 70%);
    animation: ambientPulse 8s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes ambientPulse {
    0%   { opacity: 0.6; transform: scale(1); }
    50%  { opacity: 1;   transform: scale(1.03); }
    100% { opacity: 0.7; transform: scale(0.98); }
}

/* ── Top padding reset ───────────────────────────────────────────── */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px;
    position: relative;
    z-index: 1;
}

/* ── Hide Streamlit default top padding/header gap ───────────────── */
header[data-testid="stHeader"] {
    display: none !important;
}
.stMainBlockContainer {
    padding-top: 0.5rem !important;
}
div[data-testid="stToolbar"] {
    display: none !important;
}

/* ── Logo / Brand header ─────────────────────────────────────────── */
.brand-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.5rem;
}
.brand-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #00d4ff, #0066cc);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}
.brand-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00d4ff 0%, #4da6ff 50%, #a0d0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.brand-sub {
    font-size: 0.72rem;
    color: #5a8aaa;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: -4px;
}

/* ── Navigation menu override ────────────────────────────────────── */
div[data-testid="stHorizontalBlock"] > div:has(nav) {
    background: transparent;
}

/* ── Metric cards ────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1b2e 0%, #0a1422 100%);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 16px;
    padding: 20px 22px !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    animation: scanLine 3s ease-in-out infinite;
}
@keyframes scanLine {
    0%, 100% { opacity: 0; transform: translateX(-100%); }
    50%       { opacity: 1; transform: translateX(100%); }
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.12);
}
div[data-testid="metric-container"] label {
    color: #5a8aaa !important;
    font-size: 0.78rem !important;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace;
    font-size: 1.7rem !important;
    font-weight: 700;
    color: #00d4ff !important;
}

/* ── Section titles ──────────────────────────────────────────────── */
.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8f4f8;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    margin-bottom: 1.5rem;
    position: relative;
}
.section-title::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 60px; height: 2px;
    background: linear-gradient(90deg, #00d4ff, transparent);
}

/* ── Glass cards (for form wrappers & lists) ─────────────────────── */
.glass-card {
    background: linear-gradient(135deg, rgba(13,27,46,0.95) 0%, rgba(7,13,26,0.9) 100%);
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.glass-card::after {
    content: '';
    position: absolute;
    top: -50%; right: -50%;
    width: 100%; height: 100%;
    background: radial-gradient(circle, rgba(0,212,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

/* ── Vehicle grid cards ──────────────────────────────────────────── */
.vehicle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
    margin-top: 16px;
}
.vehicle-card {
    background: linear-gradient(145deg, #0d1b2e, #081424);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}
.vehicle-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(0,212,255,0.06), transparent 60%);
    opacity: 0;
    transition: opacity 0.35s;
}
.vehicle-card:hover {
    border-color: rgba(0, 212, 255, 0.55);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 180, 255, 0.18), 0 0 0 1px rgba(0,212,255,0.1);
}
.vehicle-card:hover::before { opacity: 1; }
.vehicle-plate {
    font-family: 'Orbitron', monospace;
    font-size: 1.15rem;
    font-weight: 800;
    color: #00d4ff;
    letter-spacing: 3px;
    margin-bottom: 8px;
}
.vehicle-name {
    font-size: 0.9rem;
    color: #8ab4cc;
    margin-bottom: 14px;
    font-weight: 500;
}
.vehicle-km {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    color: #5a8aaa;
}
.km-badge {
    background: rgba(0,212,255,0.1);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 20px;
    padding: 3px 10px;
    font-family: 'Orbitron', monospace;
    font-size: 0.78rem;
    color: #00d4ff;
    font-weight: 600;
}
.vehicle-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
    filter: drop-shadow(0 0 8px rgba(0,212,255,0.3));
}

/* ── Status badges ───────────────────────────────────────────────── */
.status-ok    { background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
.status-warn  { background: rgba(255,193,7,0.1);  border: 1px solid rgba(255,193,7,0.3);  color: #ffc107; border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
.status-alert { background: rgba(255,69,58,0.1);  border: 1px solid rgba(255,69,58,0.3);  color: #ff453a; border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; font-weight: 600; display: inline-block; }

/* ── Divider ─────────────────────────────────────────────────────── */
.premium-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent);
    margin: 1.5rem 0;
}

/* ── Streamlit form inputs ───────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: #0a1422 !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 10px !important;
    color: #c8dff0 !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(0, 212, 255, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.08) !important;
}
label[data-testid="stWidgetLabel"] > div > p {
    color: #5a8aaa !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.stFormSubmitButton > button,
.stButton > button {
    background: linear-gradient(135deg, #0088cc 0%, #00aad4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(0,180,255,0.3) !important;
}
.stFormSubmitButton > button:hover,
.stButton > button:hover {
    background: linear-gradient(135deg, #00aad4 0%, #00d4ff 100%) !important;
    box-shadow: 0 6px 28px rgba(0,212,255,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Dataframe ───────────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Alert / Info / Success boxes ───────────────────────────────── */
.stAlert {
    border-radius: 12px !important;
    border-left-width: 3px !important;
}

/* ── Download button ─────────────────────────────────────────────── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid rgba(0,212,255,0.35) !important;
    color: #00d4ff !important;
    border-radius: 10px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    border-color: rgba(0,212,255,0.7) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.2) !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #070d1a; }
::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
</style>
""", unsafe_allow_html=True)

# ─── Plotly Dark Theme Config ────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,20,34,0.6)",
    font=dict(family="Inter", color="#8ab4cc", size=12),
    colorway=["#00d4ff", "#0088cc", "#4da6ff", "#00ff88", "#ffc107", "#7b68ee"],
    xaxis=dict(gridcolor="rgba(0,212,255,0.07)", linecolor="rgba(0,212,255,0.15)", tickcolor="rgba(0,212,255,0.15)"),
    yaxis=dict(gridcolor="rgba(0,212,255,0.07)", linecolor="rgba(0,212,255,0.15)", tickcolor="rgba(0,212,255,0.15)"),
    margin=dict(t=30, b=30, l=10, r=10),
)

# ─── DB Bağlantısı ──────────────────────────────────────────────────────────
conn = baglanti_olustur()
cursor = conn.cursor()

# ─── Brand Header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div class="brand-icon">🚗</div>
    <div>
        <div class="brand-title">AutoTrack Pro</div>
        <div class="brand-sub">Araç Yönetim Sistemi</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Navigation ─────────────────────────────────────────────────────────────
secim = option_menu(
    menu_title=None,
    options=["Dashboard", "Araçlar", "Bakım / Masraf", "Finansal Rapor", "Uyarı Sistemi"],
    icons=["speedometer2", "car-front-fill", "tools", "wallet2", "bell-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "6px 8px",
            "background": "linear-gradient(135deg, #0d1b2e, #081424)",
            "border": "1px solid rgba(0,212,255,0.15)",
            "border-radius": "14px",
            "margin-bottom": "6px",
        },
        "icon": {"color": "#00d4ff", "font-size": "15px"},
        "nav-link": {
            "font-family": "'Orbitron', monospace",
            "font-size": "0.72rem",
            "font-weight": "600",
            "letter-spacing": "1px",
            "color": "#5a8aaa",
            "text-align": "center",
            "margin": "2px",
            "border-radius": "10px",
            "--hover-color": "rgba(0,212,255,0.08)",
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #003d66, #005580)",
            "color": "#00d4ff",
            "border": "1px solid rgba(0,212,255,0.4)",
            "box-shadow": "0 0 20px rgba(0,212,255,0.2)",
        },
    }
)

st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if secim == "Dashboard":
    st.markdown('<div class="section-title">📊 &nbsp; Sistem Özet Paneli</div>', unsafe_allow_html=True)

    cursor.execute("SELECT COUNT(*) FROM araclar")
    toplam_arac = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(maliyet) FROM bakimlar")
    toplam_maliyet = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT COUNT(*) FROM bakimlar")
    toplam_islem = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kayıtlı Araç", f"{toplam_arac}")
    col2.metric("Toplam Bakım Gideri", f"₺{toplam_maliyet:,.0f}")
    col3.metric("İşlem Sayısı", f"{toplam_islem}")
    col4.metric("Sistem Durumu", "● Aktif")

    st.markdown("<br>", unsafe_allow_html=True)

    # Araç grid'i
    cursor.execute("SELECT plaka, marka, model, kilometre FROM araclar")
    araclar = cursor.fetchall()

    if araclar:
        st.markdown('<div class="section-title">🚗 &nbsp; Araç Filosu</div>', unsafe_allow_html=True)
        icons = ["🏎️", "🚗", "🚙", "🛻", "🚐", "🚌"]
        cards_html = '<div class="vehicle-grid">'
        for i, (plaka, marka, model, km) in enumerate(araclar):
            icon = icons[i % len(icons)]
            cards_html += f"""
            <div class="vehicle-card">
                <div class="vehicle-icon">{icon}</div>
                <div class="vehicle-plate">{plaka}</div>
                <div class="vehicle-name">{marka} {model}</div>
                <div class="vehicle-km">
                    <span>Güncel KM</span>
                    <span class="km-badge">{km:,} km</span>
                </div>
            </div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Grafikler
    df_grafik = pd.read_sql_query(
        "SELECT plaka, SUM(maliyet) as toplam FROM bakimlar GROUP BY plaka", conn
    )
    if not df_grafik.empty:
        st.markdown('<div class="section-title">📈 &nbsp; Harcama Analizi</div>', unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_pie = go.Figure(go.Pie(
                labels=df_grafik["plaka"],
                values=df_grafik["toplam"],
                hole=0.55,
                textfont=dict(family="Orbitron, monospace", size=11),
                marker=dict(
                    colors=["#00d4ff", "#0088cc", "#4da6ff", "#00ff88", "#ffc107"],
                    line=dict(color="#070d1a", width=2)
                ),
            ))
            fig_pie.update_layout(
                title=dict(text="Araç Bazlı Harcama Dağılımı", font=dict(family="Orbitron, monospace", color="#c8dff0", size=13)),
                **PLOTLY_THEME,
                showlegend=True,
                legend=dict(font=dict(color="#8ab4cc")),
            )
            fig_pie.add_annotation(
                text="TOPLAM", x=0.5, y=0.55, showarrow=False,
                font=dict(family="Orbitron", size=9, color="#5a8aaa")
            )
            fig_pie.add_annotation(
                text=f"₺{df_grafik['toplam'].sum():,.0f}", x=0.5, y=0.42, showarrow=False,
                font=dict(family="Orbitron", size=14, color="#00d4ff")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g2:
            fig_bar = go.Figure(go.Bar(
                x=df_grafik["plaka"],
                y=df_grafik["toplam"],
                marker=dict(
                    color=df_grafik["toplam"],
                    colorscale=[[0, "#003d66"], [0.5, "#0088cc"], [1, "#00d4ff"]],
                    line=dict(color="rgba(0,212,255,0.4)", width=1),
                ),
                text=[f"₺{v:,.0f}" for v in df_grafik["toplam"]],
                textposition="outside",
                textfont=dict(family="Orbitron, monospace", size=10, color="#00d4ff"),
            ))
            fig_bar.update_layout(
                title=dict(text="Araç Gider Karşılaştırması", font=dict(family="Orbitron, monospace", color="#c8dff0", size=13)),
                **PLOTLY_THEME,
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Timeline (bakım tarihleri)
        df_time = pd.read_sql_query(
            "SELECT tarih, plaka, islem_turu, maliyet FROM bakimlar ORDER BY tarih", conn
        )
        if not df_time.empty and len(df_time) >= 2:
            fig_line = go.Figure()
            for plaka in df_time["plaka"].unique():
                df_p = df_time[df_time["plaka"] == plaka]
                fig_line.add_trace(go.Scatter(
                    x=df_p["tarih"], y=df_p["maliyet"],
                    mode="lines+markers",
                    name=plaka,
                    line=dict(width=2),
                    marker=dict(size=7, symbol="circle"),
                    hovertemplate="<b>%{x}</b><br>₺%{y:,.0f}<extra>" + plaka + "</extra>",
                ))
            fig_line.update_layout(
                title=dict(text="Bakım Maliyeti Zaman Çizelgesi", font=dict(family="Orbitron, monospace", color="#c8dff0", size=13)),
                **PLOTLY_THEME,
            )
            st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("📭  Grafiklerin yüklenmesi için sisteme araç ve bakım kaydı girilmesi gerekmektedir.")

# ════════════════════════════════════════════════════════════════════════════
# ARAÇLAR
# ════════════════════════════════════════════════════════════════════════════
elif secim == "Araçlar":
    st.markdown('<div class="section-title">🏎️ &nbsp; Yeni Araç Kayıt Modülü</div>', unsafe_allow_html=True)

    col_form, col_list = st.columns([1, 1.4], gap="large")

    with col_form:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("arac_ekle_form", clear_on_submit=True):
            plaka = st.text_input("Araç Plakası", placeholder="34 ABC 123").upper()
            col1, col2 = st.columns(2)
            with col1:
                marka = st.text_input("Marka", placeholder="Toyota")
            with col2:
                model = st.text_input("Model", placeholder="Corolla")
            km = st.number_input("Güncel Kilometre", min_value=0, step=500)
            submit = st.form_submit_button("Sisteme Kaydet", use_container_width=True)

            if submit:
                if plaka and marka and model:
                    try:
                        yeni_arac = Arac(plaka, marka, model, km)
                        cursor.execute(
                            "INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)",
                            (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre)
                        )
                        conn.commit()
                        st.success(f"✅  **{plaka}** plakası başarıyla kaydedildi.")
                    except sqlite3.IntegrityError:
                        st.error("⚠️  Bu plaka sistemde zaten kayıtlı.")
                else:
                    st.warning("Lütfen tüm alanları doldurunuz.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_list:
        st.markdown("#### Kayıtlı Araçlar")
        cursor.execute("SELECT plaka, marka, model, kilometre FROM araclar")
        rows = cursor.fetchall()
        if rows:
            icons = ["🏎️", "🚗", "🚙", "🛻", "🚐"]
            cards_html = '<div class="vehicle-grid">'
            for i, (plaka, marka, model, km) in enumerate(rows):
                icon = icons[i % len(icons)]
                cards_html += f"""
                <div class="vehicle-card">
                    <div class="vehicle-icon">{icon}</div>
                    <div class="vehicle-plate">{plaka}</div>
                    <div class="vehicle-name">{marka} {model}</div>
                    <div class="vehicle-km">
                        <span>Km</span>
                        <span class="km-badge">{km:,}</span>
                    </div>
                </div>"""
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        else:
            st.info("Henüz kayıtlı araç bulunmuyor.")

# ════════════════════════════════════════════════════════════════════════════
# BAKIM / MASRAF
# ════════════════════════════════════════════════════════════════════════════
elif secim == "Bakım / Masraf":
    st.markdown('<div class="section-title">🔧 &nbsp; Bakım ve Masraf Girişi</div>', unsafe_allow_html=True)

    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [r[0] for r in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde kayıtlı araç bulunmamaktadır.")
    else:
        col_form, col_hist = st.columns([1, 1.5], gap="large")

        with col_form:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("bakim_ekle_form", clear_on_submit=True):
                secilen_plaka = st.selectbox("Araç Seçiniz", plaka_listesi)
                islem_turu = st.text_input("Yapılan İşlem", placeholder="Yağ değişimi, fren, vb.")
                col1, col2 = st.columns(2)
                with col1:
                    islem_km = st.number_input("İşlem Kilometresi", min_value=0, step=500)
                with col2:
                    maliyet = st.number_input("Maliyet (₺)", min_value=0.0, step=50.0)
                submit = st.form_submit_button("Kaydı Ekle", use_container_width=True)

                if submit:
                    if islem_turu:
                        yeni_bakim = BakimKaydi(secilen_plaka, islem_turu, islem_km, maliyet)
                        cursor.execute(
                            "INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                            (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih)
                        )
                        cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (islem_km, secilen_plaka))
                        conn.commit()
                        st.success("✅  Bakım kaydı eklendi.")
                    else:
                        st.warning("İşlem türü boş bırakılamaz.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_hist:
            st.markdown("#### Son Bakım Kayıtları")
            df_hist = pd.read_sql_query(
                "SELECT tarih, plaka, islem_turu, kilometre, maliyet FROM bakimlar ORDER BY tarih DESC LIMIT 20", conn
            )
            if not df_hist.empty:
                df_hist.columns = ["Tarih", "Plaka", "İşlem", "Km", "Maliyet (₺)"]
                st.dataframe(
                    df_hist.style.format({"Maliyet (₺)": "₺{:,.0f}", "Km": "{:,}"}),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Henüz bakım kaydı bulunmuyor.")

# ════════════════════════════════════════════════════════════════════════════
# FİNANSAL RAPOR
# ════════════════════════════════════════════════════════════════════════════
elif secim == "Finansal Rapor":
    st.markdown('<div class="section-title">📋 &nbsp; Finansal Raporlama</div>', unsafe_allow_html=True)

    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [r[0] for r in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde araç bulunmuyor.")
    else:
        col_sel, col_metric = st.columns([1, 2])
        with col_sel:
            secilen_plaka = st.selectbox("Araç Seçiniz", plaka_listesi)

        df = pd.read_sql_query(
            "SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC",
            conn, params=(secilen_plaka,)
        )

        if not df.empty:
            toplam_harcama = df["maliyet"].sum()
            ort_maliyet = df["maliyet"].mean()
            max_maliyet = df["maliyet"].max()

            with col_metric:
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Toplam Gider", f"₺{toplam_harcama:,.0f}")
                mc2.metric("Ortalama İşlem", f"₺{ort_maliyet:,.0f}")
                mc3.metric("En Yüksek", f"₺{max_maliyet:,.0f}")

            st.markdown("<br>", unsafe_allow_html=True)

            df_display = df.copy()
            df_display.columns = ["Tarih", "İşlem", "Km", "Maliyet (₺)"]
            st.dataframe(
                df_display.style.format({"Maliyet (₺)": "₺{:,.0f}", "Km": "{:,}"}),
                use_container_width=True, hide_index=True
            )

            # Harcama bar chart
            fig_rapor = go.Figure(go.Bar(
                x=df["islem_turu"],
                y=df["maliyet"],
                marker=dict(
                    color=df["maliyet"],
                    colorscale=[[0, "#003d66"], [1, "#00d4ff"]],
                    line=dict(color="rgba(0,212,255,0.3)", width=1)
                ),
                text=[f"₺{v:,.0f}" for v in df["maliyet"]],
                textposition="outside",
                textfont=dict(family="Orbitron", size=10, color="#00d4ff"),
            ))
            fig_rapor.update_layout(
                title=dict(text=f"{secilen_plaka} — İşlem Maliyetleri", font=dict(family="Orbitron, monospace", color="#c8dff0", size=13)),
                **PLOTLY_THEME, showlegend=False
            )
            st.plotly_chart(fig_rapor, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥  CSV Rapor İndir",
                data=csv,
                file_name=f"{secilen_plaka}_rapor.csv",
                mime="text/csv",
            )
        else:
            st.info("Bu araca ait kayıt bulunmamaktadır.")

# ════════════════════════════════════════════════════════════════════════════
# UYARI SİSTEMİ
# ════════════════════════════════════════════════════════════════════════════
elif secim == "Uyarı Sistemi":
    st.markdown('<div class="section-title">🚨 &nbsp; Akıllı Kontrol Paneli</div>', unsafe_allow_html=True)

    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [r[0] for r in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Araç bulunamadı.")
    else:
        secilen_plaka = st.selectbox("Araç Seçiniz", plaka_listesi)

        cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (secilen_plaka,))
        guncel_km = cursor.fetchone()[0]

        cursor.execute(
            "SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1",
            (secilen_plaka,)
        )
        son_bakim = cursor.fetchone()

        if son_bakim:
            fark = guncel_km - son_bakim[0]

            # Gauge chart
            if fark >= 10000:
                gauge_color = "#ff453a"
                durum_badge = '<span class="status-alert">🚨 Bakım Gerekiyor</span>'
                durum_msg = "Periyodik bakım zamanı gelmiştir. Lütfen servise gidiniz."
            elif fark >= 5000:
                gauge_color = "#ffc107"
                durum_badge = '<span class="status-warn">⚠️ Kontrol Önerisi</span>'
                durum_msg = "Bakım tarihi yaklaşıyor. Yakında servis planlaması yapınız."
            else:
                gauge_color = "#00ff88"
                durum_badge = '<span class="status-ok">✅ Durum Güvenli</span>'
                durum_msg = "Aracınız iyi durumda. Sonraki bakıma kadar yaklaşık mesafe bilgisi aşağıdadır."

            col1, col2, col3 = st.columns(3)
            col1.metric("Güncel KM", f"{guncel_km:,} km")
            col2.metric("Son Bakım KM", f"{son_bakim[0]:,} km")
            col3.metric("Kat Edilen Yol", f"{fark:,} km")

            st.markdown(f"<br>{durum_badge}<br><br>", unsafe_allow_html=True)

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=fark,
                delta=dict(reference=10000, decreasing=dict(color="#00ff88"), increasing=dict(color="#ff453a")),
                number=dict(font=dict(family="Orbitron, monospace", color=gauge_color, size=36), suffix=" km"),
                gauge=dict(
                    axis=dict(range=[0, 12000], tickwidth=1, tickcolor="#1a3a5c", tickfont=dict(color="#5a8aaa")),
                    bar=dict(color=gauge_color, thickness=0.22),
                    bgcolor="rgba(10,20,34,0.5)",
                    borderwidth=1,
                    bordercolor="rgba(0,212,255,0.2)",
                    steps=[
                        dict(range=[0, 5000], color="rgba(0,255,136,0.08)"),
                        dict(range=[5000, 8000], color="rgba(255,193,7,0.08)"),
                        dict(range=[8000, 12000], color="rgba(255,69,58,0.08)"),
                    ],
                    threshold=dict(line=dict(color="#ff453a", width=2), thickness=0.8, value=10000),
                ),
                title=dict(text="Son Bakımdan Bu Yana Kat Edilen Yol", font=dict(family="Orbitron, monospace", color="#8ab4cc", size=13)),
            ))
            fig_gauge.update_layout(**PLOTLY_THEME, height=320)
            st.plotly_chart(fig_gauge, use_container_width=True)

            st.info(f"ℹ️  {durum_msg}")

            # Tüm araçların uyarı özeti
            st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### Filo Geneli Durum Özeti")
            cursor.execute("SELECT plaka, kilometre FROM araclar")
            tum_araclar = cursor.fetchall()
            for plaka, km in tum_araclar:
                cursor.execute(
                    "SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (plaka,)
                )
                sb = cursor.fetchone()
                if sb:
                    f = km - sb[0]
                    if f >= 10000:
                        badge = f'<span class="status-alert">🚨 {plaka} — {f:,} km</span>'
                    elif f >= 5000:
                        badge = f'<span class="status-warn">⚠️ {plaka} — {f:,} km</span>'
                    else:
                        badge = f'<span class="status-ok">✅ {plaka} — {f:,} km</span>'
                    st.markdown(badge + "<br>", unsafe_allow_html=True)
        else:
            st.info("Karşılaştırma yapılacak bakım kaydı bulunmuyor.")

conn.close()