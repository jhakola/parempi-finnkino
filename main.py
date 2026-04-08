import streamlit as st
import requests
from datetime import datetime

# --- ASETUKSET ---
st.set_page_config(page_title="Parempi Finnkino v2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    div[data-testid="stColumn"] {
        background-color: #1e293b;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        text-align: center;
    }
    .movie-title { font-size: 1.2rem; font-weight: bold; color: #f8fafc; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)


# --- DATAN HAKU (JSON) ---
@st.cache_data(ttl=600)
def get_movies_json():
    # Tämä on Finnkinon uudempi Events-rajapinta
    url = "https://www.finnkino.fi/fi/v1/Events"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"Palvelin vastasi: {response.status_code}"

        # JSON-data on suoraan lista elokuvista
        return response.json(), None
    except Exception as e:
        return None, str(e)


# --- UI ---
st.title("Parempi Finnkino 🎥 (V2 JSON)")

movies, error = get_movies_json()

if error:
    st.error(f"Haku epäonnistui: {error}")
    st.info("Finnkinon rajapinta saattaa olla huoltotauolla.")
elif movies:
    # Sivupalkin haku
    search = st.sidebar.text_input("Etsi elokuvaa", "")

    # Suodatetaan hakusanalla
    filtered_movies = [
        m for m in movies
        if search.lower() in m.get('Title', '').lower()
    ]

    if not filtered_movies:
        st.warning("Ei löytynyt elokuvia.")
    else:
        # Näytetään elokuvat ruudukossa
        cols_per_row = 4
        for i in range(0, len(filtered_movies), cols_per_row):
            batch = filtered_movies[i: i + cols_per_row]
            cols = st.columns(cols_per_row)

            for j, movie in enumerate(batch):
                with cols[j]:
                    # Kuvatiedot löytyvät usein Images-kentästä
                    images = movie.get('Images', {})
                    poster = images.get('EventMediumImagePortrait', '')

                    if poster:
                        st.image(poster, use_container_width=True)

                    st.markdown(f"<div class='movie-title'>{movie.get('Title')}</div>", unsafe_allow_html=True)

                    # Lisätiedot
                    st.write(f"🎭 {movie.get('Genres', 'Ei genreä')}")
                    st.caption(f"📅 Vuosi: {movie.get('ProductionYear', '-')}")

                    # Linkki Finnkinon sivuille
                    event_id = movie.get('ID')
                    st.link_button("Lue lisää", f"https://www.finnkino.fi/event/{event_id}", use_container_width=True)
else:
    st.warning("Elokuvia ei löytynyt.")

st.sidebar.markdown("---")
st.sidebar.caption("Tämä versio käyttää Finnkinon V1 Events -rajapintaa.")