# AlphaHunter V1.4 Research

## Uj funkciok
- Deep News eredmenycache: tartalomhash + modell + schema verzio, 1 evig
- Gyors es mely elemzesi mod
- Hivatalos Investor Relations domainre szurt kozlemenyek
- Gyorsjelentesi kockazat: 0-3 nap -15, 4-7 nap -8, 8-14 nap -3 pont
- Ot eves, havi Top 2 backtest SPY es egyenlo sulyu benchmark ellen
- Nincs paper trading naplo

## Telepites
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## Fontos
Az IR reteget hivatalos vallalati domainekre szurt keresessel tolti fel. A teljes szoveg csak nyilvanosan hozzaferheto HTML eseteben dolgozhato fel; fizetofalat nem kerul meg. A backtest szandekosan nem hasznalja a mai fundamentalis adatokat vagy hireket, mert az look-ahead biast okozna.

## V1.4.1 statisztikai panel
Visszaállítja és kibővíti a Gemini-használat, tokenek, cache-ek, hírforrások, Deep News letöltések, hibák és futási idők kijelzését. Gyors módban a Deep mezők várhatóan nullák; mély módban külön látható az új Gemini-hívás és a Deep eredménycache találat.

## V1.5 modern felület
- sötétkék-fekete, reszponzív dashboard
- külön Gyors és Mély elemzési mód
- oldalsávos navigáció
- rangsor-, radar-, részpontszám- és earnings-kockázati grafikonok
- interaktív vállalati részletek és hírek
- modern backtest-grafikon
- teljes Gemini-, token-, cache- és teljesítménystatisztika

## V1.5.2 kontrasztjavítás
- feltűnő ciánkék oldalsávnyitó és -záró gomb
- nagyobb, fehér oldalsáv ikon
- kényszerített sötétkék elemzésimód-választó
- világos, félkövér kiválasztott érték
- sötét lenyíló menü, élénkkék kijelöléssel

---

# Final release and cloud deployment

**Stable release:** AlphaHunter V1.5.2 Final  
**Release date:** 2026-10-13

For cloud deployment, follow [`DEPLOYMENT.md`](DEPLOYMENT.md). Real API keys must only be entered in Streamlit Community Cloud Secrets and must never be committed to GitHub.
