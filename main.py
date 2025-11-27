from fast_api.main import poster_path
import streamlit as st
import requests

FASTAPI_BASE_URL = "http://localhost:8000"
RECOMMEND_ENDPOINT = f"{FASTAPI_BASE_URL}/recommend/"
MOVIES_ENDPOINT = f"{FASTAPI_BASE_URL}/movies/"

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=3600)
def fetch_movie_list():
    try:
        response = requests.get(MOVIES_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Ensure FastAPI is running.")
        return []
    except Exception as e:
        st.error(f"Error fetching movie list: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_recommendations(movie_name):
    try:
        response = requests.post(RECOMMEND_ENDPOINT, json={"movie_name": movie_name})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 404:
            st.error(f"Movie '{movie_name}' not found.")
        elif status == 503:
            st.error("Model is not loaded yet. Try again shortly.")
        else:
            st.error(f"API Error {status}: {e.response.json().get('detail', 'Unknown error')}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def display_recommendations(movie_name, data):
    st.markdown(f"## Recommendations for: **{movie_name}**")
    if not data:
        return
    titles = data.get("recommendations", [])
    posters = data.get("poster_paths", [])
    cols = st.columns(len(titles))
    for i, col in enumerate(cols):
        with col:
            st.subheader(titles[i])
            poster_url = posters[i]
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown(
                    '<div style="background-color:#f0f2f6; padding:40px; text-align:center; border-radius:8px;">No Poster Available</div>',
                    unsafe_allow_html=True
                )


def recommend_page(all_movies, selected_movie=None):
    st.header("Get Recommendations")

    if selected_movie:
        data = fetch_recommendations(selected_movie)
        if data:
            display_recommendations(selected_movie, data)

    selected_movie = st.selectbox(
        "Select a movie:",
        [movie['movie_name'] for movie in all_movies],
        index=0 if all_movies else None,
        key="selector_movie"
    )

    if st.button("Recommend", key="recommend_btn"):
        with st.spinner("Fetching recommendations..."):
            data = fetch_recommendations(selected_movie)
            if data:
                display_recommendations(selected_movie, data)


def home_page(all_movies):
    st.header("Popular Movies")
    if not all_movies:
        st.info("No movie data available. Ensure backend is running.")
        return

    COLUMNS_PER_ROW = 5
    for i in range(0, len(all_movies[:10]), COLUMNS_PER_ROW):
        row = all_movies[i:i + COLUMNS_PER_ROW]
        cols = st.columns(COLUMNS_PER_ROW)
        for j, movie in enumerate(row):
            with cols[j]:
                st.markdown(f"**{movie['movie_name']}**")
                img_path = poster_path(id=movie['id'])
                st.image(img_path,use_container_width=True)
                if st.button("Recommend", key=f"rec_btn_{movie['id']}"):
                    st.session_state.selected_movie = movie['movie_name']
                    st.session_state.page = "recommend"


ALL_MOVIES = fetch_movie_list()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.page = "home"
if st.sidebar.button("Recommend a Movie"):
    st.session_state.page = "recommend"

# Render pages
if st.session_state.page == "recommend":
    recommend_page(ALL_MOVIES, st.session_state.selected_movie)
    st.session_state.selected_movie = None
elif st.session_state.page == "home":
    home_page(ALL_MOVIES)

st.sidebar.markdown("---")
