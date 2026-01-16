import streamlit as st
import feedparser
import openai
from datetime import datetime

# --- KONFIGURÁCIÓ ---
# Itt kellene megadnod az OpenAI API kulcsodat, ha élesben használod
# openai.api_key = "A_TE_API_KULCSOD"

# Hírforrások (RSS feedek)
RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Variety": "https://variety.com/feed/",
    "Reuters (Wire)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best" 
    # Megjegyzés: A Reuters nyilvános RSS-e korlátozott, gyakran alternatív forrást kell használni.
}

# --- FÜGGVÉNYEK ---

def get_news(feed_url):
    """Hírek letöltése az RSS feedből"""
    feed = feedparser.parse(feed_url)
    return feed.entries[:5] # Csak a legfrissebb 5 hír forrásonként

def translate_and_summarize_ai(text, mode="translate"):
    """
    AI Funkció: Fordítás vagy Összefoglalás.
    Ha nincs API kulcs, csak kiírja, hogy 'AI Demo'.
    """
    if not openai.api_key:
        return f"[AI DEMO - Nincs API Kulcs] Fordítás: {text} (Ez egy szimuláció)"
    
    try:
        if mode == "translate":
            prompt = f"Fordítsd le ezt a szalagcímet magyarra profi újságírói stílusban: '{text}'"
        elif mode == "summarize":
            prompt = f"Foglald össze ezt a cikket magyarul 3 tömör pontban: '{text}'"
            
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hiba az AI hívásban: {e}"

# --- APP FELÜLET (UI) ---

st.set_page_config(page_title="Hírek Most", page_icon="📰", layout="centered")

# Mobilbarát fejléc
st.title("🌍 Globális Hírek")
st.markdown("*BBC • Variety • Reuters - Magyarul*")

# Oldalsáv (Beállítások)
with st.sidebar:
    st.header("Beállítások")
    ai_enabled = st.checkbox("AI Fordítás bekapcsolása", value=False)
    st.info("AI nélkül az eredeti angol szöveg jelenik meg.")

# Hírek megjelenítése
st.divider()

for source_name, feed_url in RSS_FEEDS.items():
    st.subheader(f"📌 {source_name}")
    news_items = get_news(feed_url)
    
    for item in news_items:
        with st.container():
            # Cím kezelése
            title = item.title
            if ai_enabled:
                # Itt hívnánk meg az AI-t a cím fordítására (API kulcs szükséges)
                # Most csak szimuláljuk a gyorsaság kedvéért, ha nincs kulcs
                pass 
            
            st.markdown(f"**{title}**")
            
            # Dátum és Link
            published = item.get("published", "Nincs dátum")[:16]
            st.caption(f"🕒 {published} | [Eredeti cikk elolvasása]({item.link})")
            
            # AI Opció Gomb (Interaktív)
            if st.button(f"🤖 AI Összefoglaló (Magyarul)", key=item.link):
                with st.spinner('Az AI olvassa és fordítja a cikket...'):
                    # Valós appnál itt a cikk teljes szövegét küldenénk be
                    summary = translate_and_summarize_ai(item.summary, mode="summarize")
                    st.success(summary)
            
            st.divider()

# Footer
st.markdown("---")
st.markdown("Developed for Android via Web • 2024")
