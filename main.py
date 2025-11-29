import streamlit as st
import requests
import os
import pickle
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
RECOMMEND_ENDPOINT = f"{FASTAPI_BASE_URL}/recommend/"
TMDB_API_KEY = os.getenv('api_key')

st.set_page_config(page_title="Movie Recommender", layout="wide")


def get_poster_url(movie_id):
    if not TMDB_API_KEY:
        return "https://via.placeholder.com/500x750?text=No+API+Key"
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=2) # Short timeout for UI speed
        if response.status_code == 200:
            data = response.json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Image"

@st.cache_data(ttl=3600)
def load_local_movie_list():
    """
    Loads the movie list LOCALLY from the pickle file.
    This prevents the '429 Rate Limit' crash on startup.
    """
    try:
        # We assume movie_list.pkl is in the root directory (copied by Docker)
        movies_list = pickle.load(open('movie_list.pkl', 'rb'))
        return pd.DataFrame(movies_list)
    except Exception as e:
        st.error(f"Error loading local movie list: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_recommendations(movie_name):
    try:
        response = requests.post(RECOMMEND_ENDPOINT, json={"movie_name": movie_name}, timeout=15)
        
        if response.status_code == 429:
            st.error("Server is busy (Rate Limit). Please wait 30 seconds.")
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to Backend. It might be sleeping. Try again in 30s.")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def display_recommendations(movie_name, data):
    st.markdown(f"## Recommendations for: **{movie_name}**")
    titles = data.get("recommendations", [])
    posters = data.get("poster_paths", [])
    
    if not titles:
        st.write("No recommendations found.")
        return

    cols = st.columns(len(titles))
    for i, col in enumerate(cols):
        with col:
            st.text(titles[i])
            if i < len(posters) and posters[i]:
                st.image(posters[i], use_container_width=True) 


# Load Data (LOCALLY - No Network Crash)
movies_df = load_local_movie_list()

if "page" not in st.session_state: st.session_state.page = "home"
if "selected_movie" not in st.session_state: st.session_state.selected_movie = None

# Sidebar
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.page = "home"
    st.rerun()
if st.sidebar.button("Recommend a Movie"):
    st.session_state.page = "recommend"
    st.rerun()

# Pages
if st.session_state.page == "recommend":
    st.header("Get Recommendations")
    
    if movies_df.empty:
        st.error("Movie list could not be loaded locally.")
    else:
        # Dropdown using local data
        movie_names = movies_df['title'].values
        
        # Safe selection logic
        default_idx = 0
        if st.session_state.selected_movie in movie_names:
            default_idx = list(movie_names).index(st.session_state.selected_movie)

        selected = st.selectbox("Select a movie:", movie_names, index=default_idx)

        if st.button("Recommend"):
            with st.spinner("Asking AI for recommendations..."):
                data = fetch_recommendations(selected)
                if data:
                    display_recommendations(selected, data)
            
elif st.session_state.page == "home":
    st.header("Popular Movies")
    if movies_df.empty:
        st.warning("No movie data available.")
    else:
        # Show first 10 movies from local file
        subset = movies_df.head(10)
        cols = st.columns(5)
        
        for idx, row in subset.iterrows():
            col = cols[idx % 5]
            with col:
                st.markdown(f"**{row['title']}**")
                # Fetch poster directly from TMDB here (Frontend side)
                img_url = get_poster_url(row['movie_id'])
                st.image(img_url, use_container_width=True) 
                if st.button("Recommend", key=f"btn_{row['movie_id']}"):
                    st.session_state.selected_movie = row['title']
                    st.session_state.page = "recommend"
                    st.rerun()