import streamlit as st
import feedparser
import openai

# --- KONFIGURÁCIÓ ---
# Ha van titkos kulcsod a Streamlit Secrets-ben, onnan olvassa, ha nincs, demo mód.
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Variety": "https://variety.com/feed/",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best"
}

# Alapértelmezett képek, ha a cikkben nincs (placeholder)
DEFAULT_IMAGES = {
    "BBC World": "https://upload.wikimedia.org/wikipedia/commons/4/4e/BBC_News_2019.svg",
    "Variety": "https://variety.com/wp-content/uploads/2021/01/variety-logo-one-line-black.png",
    "Reuters": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Reuters_Logo.svg/1200px-Reuters_Logo.svg.png"
}

# --- SEGÉDFÜGGVÉNYEK ---

def get_image_url(entry, source):
    """Megpróbál képet találni az RSS bejegyzésben. Ha nincs, visszaadja a forrás logóját."""
    # 1. Próbálkozás: 'media_content' (gyakori szabvány)
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    
    # 2. Próbálkozás: 'media_thumbnail' (pl. BBC néha ezt használja)
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0]['url']
        
    # 3. Próbálkozás: Keresés a linkek között
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link['href']
    
    # Ha semmi nincs, akkor a forrás alapértelmezett logója
    return DEFAULT_IMAGES.get(source, "https://via.placeholder.com/150")

def get_news(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries[:6] # Most már 6 hírt kérünk le

def ai_summarize(text):
    """AI Összefoglaló hívás"""
    if not openai.api_key:
        return "⚠️ Nincs beállítva OpenAI API kulcs. Ez csak egy demó szöveg."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Foglald össze ezt a cikket magyarul maximum 2 mondatban, figyelemfelkeltően: {text}"}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hiba: {e}"

# --- APP UI TERVEZÉS (CSS TRÜKKÖK) ---

st.set_page_config(page_title="Hírek Most", page_icon="🌍", layout="centered")

# Egy kis CSS, hogy szebb legyen mobilon (eltünteti a felesleges margókat)
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 { margin-bottom: 0px; }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Fejléc
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title("🌍 Hírek Most")
with col_h2:
    if st.button("🔄"):
        st.rerun() # Frissítés gomb

st.markdown("---")

# Oldalsáv
with st.sidebar:
    st.header("Beállítások")
    filter_source = st.multiselect("Források szűrése", options=list(RSS_FEEDS.keys()), default=list(RSS_FEEDS.keys()))
    ai_mode = st.toggle("🤖 AI Összefoglaló mód")

# --- HÍRFOLYAM MEGJELENÍTÉSE ---

# Végigmegyünk a kiválasztott forrásokon
for source_name in filter_source:
    feed_url = RSS_FEEDS[source_name]
    st.subheader(source_name) # Pl. "BBC World" kiírása
    
    news_items = get_news(feed_url)
    
    for item in news_items:
        image_url = get_image_url(item, source_name)
        
        # --- ITT A LÉNYEG: A KÁRTYA ELRENDEZÉS ---
        # border=True adja a keretet a hír köré
        with st.container(border=True):
            
            # Két oszlopra bontjuk: Balra a kép, jobbra a szöveg
            # A [1, 2] arány azt jelenti, hogy a szöveg kétszer annyi helyet kap
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.image(image_url, use_container_width=True)
            
            with c2:
                st.markdown(f"**[{item.title}]({item.link})**")
                
                # Dátum formázása kicsit szebben
                published = item.get("published", "")[:16]
                st.caption(f"📅 {published}")

            # AI Gomb / Összefoglaló rész a kártya alján
            if ai_mode:
                if st.button("Magyar összefoglaló", key=item.link):
                    with st.spinner("Az AI dolgozik..."):
                        summary = ai_summarize(item.summary)
                        st.success(summary)
            else:
                # Ha nincs AI mód, egy lenyitható fülbe tesszük az eredeti szöveget
                with st.expander("Eredeti előnézet"):
                    st.write(item.get('summary', 'Nincs leírás.'))
