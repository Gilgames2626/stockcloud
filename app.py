import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from engine import run
from backtest import run as run_backtest
from store import clear

ROOT = Path(__file__).parent
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))

st.set_page_config(page_title='AlphaHunter', page_icon='◈', layout='wide', initial_sidebar_state='expanded')

st.markdown('''
<style>
:root {--navy:#07111f;--panel:#0d1b2e;--panel2:#101f35;--blue:#2f80ff;--cyan:#55d6ff;--text:#edf6ff;--muted:#8ea6c1;--line:#1d3553;--green:#39d98a;--red:#ff677d;}
.stApp {background:radial-gradient(circle at 15% 0%,#12335b 0,#07111f 34%,#030811 100%);color:var(--text)}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#081525,#050b14);border-right:1px solid var(--line)}
[data-testid="stHeader"] {background:transparent}
.block-container {padding-top:1.4rem;padding-bottom:3rem;max-width:1500px}
h1,h2,h3 {color:var(--text)!important;letter-spacing:-.02em}
p,span,label {color:inherit}
.hero {padding:1.4rem 1.6rem;border:1px solid #234b79;border-radius:24px;background:linear-gradient(135deg,rgba(31,85,145,.38),rgba(8,21,38,.92));box-shadow:0 20px 60px rgba(0,0,0,.28);margin-bottom:1.2rem}
.hero-kicker {color:var(--cyan);font-size:.78rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.hero-title {font-size:2.25rem;font-weight:850;margin:.2rem 0}.hero-copy {color:var(--muted);max-width:760px}
[data-testid="stMetric"] {background:linear-gradient(145deg,rgba(17,39,66,.96),rgba(8,20,35,.96));border:1px solid var(--line);padding:1rem 1.1rem;border-radius:18px;box-shadow:0 12px 35px rgba(0,0,0,.2)}
[data-testid="stMetricLabel"] {color:var(--muted)}[data-testid="stMetricValue"] {color:var(--text);font-weight:800}
.stButton>button {border-radius:14px;border:1px solid #2f68a8;background:linear-gradient(135deg,#1769e0,#2f80ff);color:white;font-weight:750;min-height:46px;box-shadow:0 10px 28px rgba(47,128,255,.25)}
.stButton>button:hover {border-color:#69c8ff;transform:translateY(-1px)}
[data-baseweb="select"]>div {background:#0d1b2e;border-color:#234565;border-radius:14px}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {border:1px solid var(--line);border-radius:18px;overflow:hidden;background:rgba(9,23,40,.75)}
.mode-card {padding:1rem;border-radius:18px;background:#0c1b2e;border:1px solid var(--line);color:var(--muted);min-height:115px}.mode-card b{color:var(--text)}
.rank-chip {display:inline-block;padding:.3rem .65rem;border-radius:99px;background:#123866;color:#75c8ff;font-weight:800;font-size:.75rem}
hr {border-color:var(--line)}

/* Global text contrast */
.stApp, .stApp p, .stApp li, .stApp label, .stApp small,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
  color:#eaf4ff !important;
}
[data-testid="stCaptionContainer"], .stCaption {color:#a9bdd2 !important;}

/* Sidebar: high contrast, including collapsed control */
[data-testid="stSidebar"] * {color:#edf6ff !important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#b9cce0 !important;}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button {
  background:#16385f !important;border:1px solid #5db8ff !important;color:#ffffff !important;
  box-shadow:0 4px 18px rgba(0,0,0,.45) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="collapsedControl"] svg {fill:#ffffff !important;color:#ffffff !important;stroke:#ffffff !important;}

/* Radio navigation */
[data-testid="stRadio"] label {
  background:#0d2037 !important;border:1px solid #244a70 !important;border-radius:12px !important;
  padding:.62rem .72rem !important;margin:.18rem 0 !important;color:#edf6ff !important;
}
[data-testid="stRadio"] label:hover {background:#15375d !important;border-color:#55b9ff !important;}
[data-testid="stRadio"] label:has(input:checked) {
  background:linear-gradient(135deg,#174f91,#1769e0) !important;border-color:#76cfff !important;
  box-shadow:0 6px 18px rgba(24,105,224,.3) !important;
}
[data-testid="stRadio"] label span {color:#ffffff !important;}

/* Selects, text inputs and dropdown menus */
[data-baseweb="select"] > div, [data-baseweb="input"] {
  background:#102640 !important;border:1px solid #37658f !important;color:#ffffff !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] input,
[data-baseweb="input"] input {color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;}
[data-baseweb="popover"], [role="listbox"], [role="option"] {
  background:#0d2037 !important;color:#ffffff !important;
}
[role="option"]:hover, [aria-selected="true"] {background:#18599d !important;color:#ffffff !important;}

/* Buttons: primary and secondary must remain visible */
.stButton > button, .stDownloadButton > button, [data-testid="stLinkButton"] a {
  color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;
}
.stButton > button[kind="secondary"], .stDownloadButton > button {
  background:#122d4d !important;border:1px solid #4d94cf !important;color:#f5fbff !important;
}
.stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover {
  background:#1b4d7d !important;border-color:#80d2ff !important;
}
.stButton svg, .stDownloadButton svg, [data-testid="stLinkButton"] svg {color:#ffffff !important;fill:#ffffff !important;}

/* Tabs */
[data-baseweb="tab-list"] {background:#091827 !important;border-radius:14px !important;padding:.25rem !important;}
[data-baseweb="tab"] {color:#bcd0e5 !important;background:transparent !important;}
[data-baseweb="tab"] p {color:#bcd0e5 !important;}
[data-baseweb="tab"][aria-selected="true"] {background:#184d82 !important;border-radius:10px !important;}
[data-baseweb="tab"][aria-selected="true"] p {color:#ffffff !important;font-weight:750 !important;}

/* Status messages and expanders */
[data-testid="stAlert"] {background:#102944 !important;border:1px solid #32658f !important;}
[data-testid="stAlert"] * {color:#f0f8ff !important;}
[data-testid="stExpander"] {background:#0c1d31 !important;border:1px solid #284d70 !important;border-radius:14px !important;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#f2f8ff !important;}

/* Metrics and dataframe contrast */
[data-testid="stMetricLabel"] p {color:#b7cbe0 !important;}
[data-testid="stMetricValue"] {color:#ffffff !important;}
[data-testid="stDataFrame"] {color:#eaf4ff !important;}
[data-testid="stDataFrame"] canvas {filter:none !important;}

/* Code and JSON panels */
code, pre, [data-testid="stJson"] {background:#071421 !important;color:#dff3ff !important;}

/* Plotly modebar visibility */
.modebar-btn path {fill:#dcecff !important;}
.modebar {background:rgba(8,24,40,.9) !important;border-radius:8px !important;}

/* Highly visible sidebar open / close control */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
  z-index:999999 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button,
button[data-testid="baseButton-headerNoPadding"] {
  background:linear-gradient(135deg,#23b7ff,#1769e0) !important;
  border:2px solid #b9ecff !important;
  border-radius:12px !important;
  min-width:38px !important;
  min-height:38px !important;
  opacity:1 !important;
  box-shadow:0 0 0 3px rgba(35,183,255,.18),0 8px 25px rgba(0,0,0,.55) !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="collapsedControl"] button:hover,
button[data-testid="baseButton-headerNoPadding"]:hover {
  background:linear-gradient(135deg,#62d3ff,#2387ff) !important;
  border-color:#ffffff !important;
  transform:scale(1.06) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="collapsedControl"] svg,
button[data-testid="baseButton-headerNoPadding"] svg {
  color:#ffffff !important;fill:#ffffff !important;stroke:#ffffff !important;
  width:23px !important;height:23px !important;
}

/* Analysis mode selector: force dark field and bright selected value */
[data-testid="stSidebar"] [data-testid="stSelectbox"] label,
[data-testid="stSidebar"] [data-testid="stSelectbox"] label p {
  color:#d9edff !important;font-weight:750 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background:linear-gradient(135deg,#102e4f,#164777) !important;
  border:2px solid #55c7ff !important;
  border-radius:14px !important;
  box-shadow:0 7px 20px rgba(0,0,0,.34) !important;
  min-height:48px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  background:linear-gradient(135deg,#16406d,#1d5f9c) !important;
  border-color:#b9ecff !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input {
  color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;
  font-weight:800 !important;text-shadow:0 1px 2px rgba(0,0,0,.65) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
  color:#74daff !important;fill:#74daff !important;
}
/* Dropdown menu remains dark even if Streamlit's base theme is light */
[data-baseweb="popover"] [role="listbox"] {
  background:#081b2d !important;border:1px solid #55c7ff !important;
  box-shadow:0 16px 45px rgba(0,0,0,.6) !important;
}
[data-baseweb="popover"] [role="option"] {background:#0d2945 !important;color:#f5fbff !important;}
[data-baseweb="popover"] [role="option"] * {color:#f5fbff !important;-webkit-text-fill-color:#f5fbff !important;}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
  background:#1769e0 !important;color:#ffffff !important;
}
</style>
''', unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#dcecff'), margin=dict(l=20,r=20,t=55,b=20),
    colorway=['#2f80ff','#55d6ff','#39d98a','#ffb84d','#a879ff','#ff677d'],
    legend=dict(orientation='h',y=1.08,x=0)
)

def badge(value, good=75, warn=55):
    return '🟢' if value >= good else ('🟡' if value >= warn else '🔴')

def radar_chart(row):
    labels=['Fundamentum','Értékeltség','Technikai','Momentum','Kockázat','Hírek']
    vals=[row.fundamental_score,row.valuation_score,row.technical_score,row.momentum_score,row.risk_score,row.news_score]
    fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=labels+[labels[0]],fill='toself',line=dict(color='#55d6ff',width=3),fillcolor='rgba(47,128,255,.23)'))
    fig.update_layout(**PLOT_LAYOUT,polar=dict(bgcolor='rgba(0,0,0,0)',radialaxis=dict(range=[0,100],gridcolor='#24415f',tickfont=dict(color='#7891aa')),angularaxis=dict(gridcolor='#24415f')),showlegend=False,height=355,title=f'{row.ticker} pontprofil')
    return fig

def ranking_chart(df):
    chart=df.sort_values('total_score').copy();chart['label']=chart['ticker']+'  '+chart['total_score'].round(1).astype(str)
    fig=px.bar(chart,x='total_score',y='label',orientation='h',color='total_score',color_continuous_scale=['#163354','#2f80ff','#55d6ff'],range_color=[0,100])
    fig.update_layout(**PLOT_LAYOUT,height=460,title='Összesített rangsor',coloraxis_showscale=False,xaxis_title='Pontszám / 100',yaxis_title='')
    fig.update_xaxes(range=[0,100],gridcolor='#18314d');fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
    return fig

def score_breakdown(df):
    cols=['fundamental_score','valuation_score','technical_score','momentum_score','risk_score','news_score']
    names=['Fundamentum','Értékeltség','Technikai','Momentum','Kockázat','Hírek']
    x=df.head(6).melt(id_vars='ticker',value_vars=cols,var_name='category',value_name='score')
    x['category']=x['category'].map(dict(zip(cols,names)))
    fig=px.bar(x,x='ticker',y='score',color='category',barmode='group')
    fig.update_layout(**PLOT_LAYOUT,height=390,title='Top 6 részpontszámai',xaxis_title='',yaxis_title='Pont / 100');fig.update_yaxes(range=[0,100],gridcolor='#18314d')
    return fig

def stats_panel(stats):
    st.markdown('### Rendszer- és Gemini-statisztikák')
    r1=st.columns(5)
    vals=[('Teljes futás',f"{stats['total_seconds']:.1f} mp"),('Cím-Gemini',stats['headline_calls']),('Deep Gemini',stats['deep_calls']),('Deep cache',stats['deep_result_cache_hits']),('Deep hibák',stats['deep_fails'])]
    for c,(k,v) in zip(r1,vals):c.metric(k,v)
    r2=st.columns(5)
    vals=[('Árfolyam cache',f"{stats['price_cache_hits']}/{stats['companies']}"),('Fundamentum cache',f"{stats['fund_cache_hits']}/{stats['companies']}"),('Hírfolyam cache',f"{stats['feed_cache_hits']}/{stats['companies']}"),('Cím-cache',f"{stats['headline_cache_hits']}/{stats['companies']}"),('Tartalom-cache',stats['deep_content_cache_hits'])]
    for c,(k,v) in zip(r2,vals):c.metric(k,v)
    r3=st.columns(4)
    vals=[('Cím input token',stats['headline_input_tokens']),('Cím output token',stats['headline_output_tokens']),('Deep input token',stats['deep_input_tokens']),('Deep output token',stats['deep_output_tokens'])]
    for c,(k,v) in zip(r3,vals):c.metric(k,v)

with st.sidebar:
    st.markdown('## ◈ AlphaHunter')
    st.caption('AI Research Terminal')
    page=st.radio('Navigáció',['Áttekintés','Rangsor és részletek','Backtest','Rendszer'],label_visibility='collapsed')
    st.markdown('---')
    analysis_label=st.selectbox('Elemzési mód',['⚡ Gyors elemzés','◆ Mély elemzés'])
    mode='quick' if 'Gyors' in analysis_label else 'deep'
    st.caption('Gyors: napi ellenőrzés. Mély: IR-források, teljes szöveg és Deep News.')
    run_clicked=st.button('Elemzés indítása',type='primary',use_container_width=True)
    if st.button('Cache törlése',use_container_width=True):st.success(f'{clear()} cache-bejegyzés törölve.')
    st.markdown('---')
    st.caption('Kutatási és döntéstámogató eszköz. Nem garantál hozamot.')

if run_clicked:
    with st.spinner('Adatok, hírek és pontszámok feldolgozása...'):
        df,news,perf,errors,stats=run(mode)
    st.session_state['analysis']=(df,news,perf,errors,stats,mode)

st.markdown('''<div class="hero"><div class="hero-kicker">AI-ALAPÚ RÉSZVÉNYKUTATÁS</div><div class="hero-title">Piaci jelekből érthető döntési kép.</div><div class="hero-copy">Fundamentumok, értékeltség, technikai trend, hírek és eseménykockázat egyetlen modern kutatási felületen.</div></div>''',unsafe_allow_html=True)

analysis=st.session_state.get('analysis')
if page in ['Áttekintés','Rangsor és részletek'] and not analysis:
    c1,c2=st.columns(2)
    c1.markdown('<div class="mode-card"><b>⚡ Gyors elemzés</b><br>Napi piaci ellenőrzés címalapú hírelemzéssel és cache-optimalizálással.</div>',unsafe_allow_html=True)
    c2.markdown('<div class="mode-card"><b>◆ Mély elemzés</b><br>Investor Relations források, teljes szöveg, Deep News és részletes eseményértelmezés.</div>',unsafe_allow_html=True)
    st.info('Válassz elemzési módot az oldalsávban, majd indítsd el az elemzést.')

if analysis:
    df,news,perf,errors,stats,last_mode=analysis
    if page=='Áttekintés':
        top=df.iloc[0];second=df.iloc[1]
        k=st.columns(4)
        k[0].metric('Top jelölt',top.ticker,f'{top.total_score:.1f}/100')
        k[1].metric('Második hely',second.ticker,f'{second.total_score:.1f}/100')
        k[2].metric('Elemzett vállalat',len(df))
        k[3].metric('Aktív mód','Mély' if last_mode=='deep' else 'Gyors')
        left,right=st.columns([1.35,1])
        left.plotly_chart(ranking_chart(df),use_container_width=True)
        right.plotly_chart(radar_chart(top),use_container_width=True)
        st.plotly_chart(score_breakdown(df),use_container_width=True)
        e=df.dropna(subset=['days_to_earnings']).sort_values('days_to_earnings').head(8)
        if not e.empty:
            fig=px.scatter(e,x='days_to_earnings',y='ticker',size='earnings_penalty',color='earnings_penalty',color_continuous_scale=['#39d98a','#ffb84d','#ff677d'],size_max=28)
            fig.update_layout(**PLOT_LAYOUT,height=320,title='Gyorsjelentési eseménykockázat',xaxis_title='Napok a jelentésig',yaxis_title='',coloraxis_colorbar_title='Pontlevonás')
            st.plotly_chart(fig,use_container_width=True)
        stats_panel(stats)
    elif page=='Rangsor és részletek':
        st.markdown('## Rangsor és vállalati részletek')
        selected=st.selectbox('Vállalat kiválasztása',df.ticker.tolist())
        row=df[df.ticker==selected].iloc[0]
        a,b=st.columns([1,1.2]);a.plotly_chart(radar_chart(row),use_container_width=True)
        with b:
            st.markdown(f'### <span class="rank-chip">#{df.index[df.ticker==selected][0]+1}</span> {selected} · {row.company}',unsafe_allow_html=True)
            m=st.columns(3);m[0].metric('Végső pont',f'{row.total_score:.1f}');m[1].metric('Aktuális ár',f'{row.price:.2f} USD');m[2].metric('Hírpont',f'{row.news_score:.1f}')
            st.write(f"**{badge(row.fundamental_score)} Fundamentum:** {row.fundamental_score:.1f}  \n**{badge(row.valuation_score)} Értékeltség:** {row.valuation_score:.1f}  \n**{badge(row.technical_score)} Technikai:** {row.technical_score:.1f}")
            st.info(f"Kutatási stop: {row.stop_loss:.2f} USD · Célár: {row.take_profit:.2f} USD · Earnings-büntetés: {row.earnings_penalty:.0f} pont")
        st.dataframe(df[['ticker','total_score','fundamental_score','valuation_score','technical_score','momentum_score','risk_score','news_score','days_to_earnings','price','stop_loss','take_profit']],use_container_width=True,height=430)
        st.markdown('### Kapcsolódó hírek és Deep News')
        for item in news.get(selected,[]):
            with st.expander(item['title']):
                st.caption(f"Forrás: {item.get('source') or item.get('source_type')} · {item.get('published','')}")
                if item.get('deep'):
                    d=item['deep'];st.success(f"{d['event_type']} · sentiment {d['sentiment']} · fontosság {d['importance']} · bizalom {d['confidence']}%")
                    st.write(d['summary']);st.caption('Kockázatok: '+', '.join(d['risk_flags']))
                elif item.get('deep_error'):st.warning('Deep News nem elérhető: '+item['deep_error'])
                st.link_button('Forrás megnyitása',item['link'])
        stats_panel(stats)

if page=='Backtest':
    st.markdown('## Historikus stratégia-teszt')
    st.caption('Csak múltban ismert árfolyam-, trend-, momentum- és volatilitási adatokkal. Mai híreket vagy fundamentumokat nem vetít vissza.')
    if st.button('Backtest futtatása',type='primary'):
        with st.spinner('Többéves havi szimuláció...'):
            series,metrics=run_backtest(CFG['watchlist'],CFG)
        st.session_state['backtest']=(series,metrics)
    if st.session_state.get('backtest'):
        series,metrics=st.session_state['backtest']
        cards=st.columns(3)
        for c,name,label in zip(cards,['strategy','benchmark','equal_weight'],['AlphaHunter','SPY benchmark','Egyenlő súly']):
            m=metrics[name];c.metric(label,f"{m['final']:,.0f} Ft",f"{m['return']*100:.1f}%")
        plot=series.melt(id_vars=['date','selected'],value_vars=['strategy','benchmark','equal_weight'],var_name='portfolio',value_name='value')
        fig=px.line(plot,x='date',y='value',color='portfolio')
        fig.update_layout(**PLOT_LAYOUT,height=500,title='Portfólióérték alakulása',xaxis_title='',yaxis_title='Virtuális portfólióérték')
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame(metrics).T.style.format({'return':'{:.2%}','cagr':'{:.2%}','drawdown':'{:.2%}','sharpe':'{:.2f}','final':'{:,.0f}'}),use_container_width=True)

if page=='Rendszer':
    st.markdown('## Rendszer és konfiguráció')
    st.json(CFG)
    if analysis:
        stats_panel(analysis[4])
        st.dataframe(pd.DataFrame.from_dict(analysis[2],orient='index'),use_container_width=True)
