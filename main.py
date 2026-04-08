import streamlit as st
import cloudscraper
import re
from datetime import datetime

# --- ASETUKSET ---
st.set_page_config(page_title="Parempi Finnkino Ghost Edition", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    div[data-testid="stColumn"] {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=600)
def get_movies_ghost_mode():
    url = "https://www.finnkino.fi/fi/v1/Events"

    try:
        # Luodaan scraper-olio, joka ohittaa suojaukset
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)

        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Virhe {response.status_code}: Finnkino hylkäsi pyynnön."
    except Exception as e:
        return None, f"Yhteysvirhe: {e}"


# --- UI ---
st.title("Parempi Finnkino 🎥 (Ghost Mode)")

movies, error = get_movies_ghost_mode()

if error:
    st.error(error)
    st.info(
        "Jos tämäkin antaa 403, Finnkino on estänyt Python-ympäristösi täysin. Silloin ainoa tie on GitHub + Deploy.")
elif movies:
    search = st.sidebar.text_input("Etsi elokuvaa", "")
    filtered = [m for m in movies if search.lower() in m.get('Title', '').lower()]

    cols = st.columns(4)
    for i, movie in enumerate(filtered[:20]):  # Näytetään 20 ekat
        with cols[i % 4]:
            images = movie.get('Images', {})
            poster = images.get('EventMediumImagePortrait', '')
            if poster:
                st.image(poster)
            st.write(f"**{movie.get('Title')}**")
            st.caption(movie.get('Genres'))
            event_id = movie.get('ID')
            st.link_button("Katso", f"https://www.finnkino.fi/event/{event_id}", use_container_width=True)