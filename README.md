# Movie Recommendation Project CI/CD
This project is a **Content-Based Movie Recommendation System** designed to suggest films based on metadata similarity.

* **Data & Insights:** The system is built upon the **TMDB 5000 Movies Dataset**. We performed extensive data analysis and insight generation to clean and prepare the data. *Note: Recommendations are strictly derived from this specific dataset.*
* **Algorithm:** We utilize **Cosine Similarity** to calculate the distance between movies, ensuring accurate and relevant suggestions based on the selected movie's features.
* **Architecture:** The application follows a modern client-server architecture:
    * **Frontend:** Powered by **Streamlit** for an interactive and responsive user interface.
    * **Backend:** Powered by **FastAPI** to handle requests and serve the machine learning model efficiently.

## Live Demo
- **Frontend:** p[https://movie-frontend-kzpj.onrender.com](https://movie-frontend-kzpj.onrender.com) <br>
- **Backend API:** [https://movie-backend-0fk3.onrender.com](https://movie-backend-0fk3.onrender.com)<br>

## Architecture
- **Frontend:** Streamlit (UI/UX)
- **Backend:** FastAPI (ML Inference & Data Serving)
- **Model:** Content-Based Filtering (Cosine Similarity)
- **Deployment:** Dockerized Microservices on Render

## Setup
### Repo clone
```bash
git clone https://github.com/Aashutosh347777/Karkhana-Movie-Recommendation.git
cd Karkhana-Movie-Recommendation
```

### Virtual Environment
```bash
python -m venv env_mov_recommendation
.\env_mov_recommendation\Scripts\activate
```

```bash
pip install -r requirements.txt
```

## Environment Confugiration
```bash
api_key=YOUR_TMDB_API_KEY
FASTAPI_BASE_URL=http://localhost:8000
```

## Running the system
```bash
uvicorn fast_api.main:app --reload
```
```bash
streamlit run main.py
```
<br>
while running steramlit make sure in the root directory