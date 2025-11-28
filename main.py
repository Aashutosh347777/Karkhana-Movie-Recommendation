import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
RECOMMEND_ENDPOINT = f"{FASTAPI_BASE_URL}/recommend/"
MOVIES_ENDPOINT = f"{FASTAPI_BASE_URL}/movies/"

TMDB_API_KEY = os.getenv('api_key') 

def get_poster_url(movie_id):
    if not TMDB_API_KEY:
        return "https://via.placeholder.com/500x750?text=No+API+Key"
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Image"

st.set_page_config(page_title="Movie Recommender", layout="wide")

@st.cache_data(ttl=3600)
# In main.py, replace the fetch_movie_list function with this:

@st.cache_data(ttl=3600)
def fetch_movie_list():
    try:
        response = requests.get(MOVIES_ENDPOINT, timeout=10)
        
        if response.status_code == 429:
            st.warning("Traffic high. Showing limited offline data.")
            return [] # Return empty to stop the crash loop
            
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        st.error("Backend is waking up (Free Tier). Please refresh in 30s.")
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_recommendations(movie_name):
    try:
        response = requests.post(RECOMMEND_ENDPOINT, json={"movie_name": movie_name})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
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
            st.text(titles[i]) # Use text instead of subheader for better fit
            if i < len(posters) and posters[i]:
                st.image(posters[i], use_container_width=True)

def home_page(all_movies):
    st.header("Popular Movies")
    if not all_movies:
        st.warning("Waiting for backend service to start...")
        return

    # Show first 10 movies
    subset = all_movies[:10]
    cols = st.columns(5)
    
    for idx, movie in enumerate(subset):
        col = cols[idx % 5]
        with col:
            st.markdown(f"**{movie['movie_name']}**")
            # We fetch poster here directly
            img_url = get_poster_url(movie['id'])
            st.image(img_url, use_container_width=True)
            if st.button("Recommend", key=f"btn_{movie['id']}"):
                st.session_state.selected_movie = movie['movie_name']
                st.session_state.page = "recommend"
                st.rerun()

# --- App Logic ---
ALL_MOVIES = fetch_movie_list()

if "page" not in st.session_state: st.session_state.page = "home"
if "selected_movie" not in st.session_state: st.session_state.selected_movie = None

st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.page = "home"
    st.rerun()
if st.sidebar.button("Recommend a Movie"):
    st.session_state.page = "recommend"
    st.rerun()

if st.session_state.page == "recommend":
    
    st.header("Get Recommendations")
    
    # Dropdown
    movie_names = [m['movie_name'] for m in ALL_MOVIES]
    selected = st.selectbox(
        "Select a movie:", 
        movie_names, 
        index=movie_names.index(st.session_state.selected_movie) if st.session_state.selected_movie in movie_names else 0
    )

    if st.button("Recommend"):
        data = fetch_recommendations(selected)
        if data:
            display_recommendations(selected, data)
            
elif st.session_state.page == "home":
    home_page(ALL_MOVIES)