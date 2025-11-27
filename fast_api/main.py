import pickle
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Annotated, List
import pandas as pd
from contextlib import asynccontextmanager
from pathlib import Path
import os
from dotenv import load_dotenv
import requests

model = None
films = None

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# MODEL_PATH = os.path.join(current_dir, "child", "similarity.pkl")
MODEL_PATH = os.path.join(parent_dir, "similarity.pkl")
FILMS_PATH = os.path.join(parent_dir, "movie_list.pkl")

load_dotenv()
api_key = os.getenv('api_key')

def poster_path(id:int) -> str:
    if not api_key:
        print("Api key not loaded.")
        return ""
    response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

app = FastAPI()

@app.on_event("startup")
async def load_resources():
    global model, films
    try:
        model = pickle.load(open(MODEL_PATH, 'rb'))
        films_dict = pickle.load(open(FILMS_PATH,'rb'))
        films = pd.DataFrame(films_dict)

        print("Model Loaded successfully.")
    except FileNotFoundError:
        print(f"File not found at {MODEL_PATH}")
    except Exception as e:
        print(f"Exception Occurred: {e}")

@app.on_event("shutdown")
async def cleanup():
    print("App shutting down...")

@app.get("/movies/", response_model=List[dict])
async def get_all_movies():
    """Returns a list of all movies with their names and IDs available for recommendation."""
    if films is None:
        raise HTTPException(
            status_code=503, 
            detail="Service Unavailable: Movie data is not loaded."
        )
    
    movies_list = []
    for index, row in films.iterrows():
        movies_list.append({
            "movie_name": row['title'],
            "id": row['movie_id']
        })
    
    return movies_list

"""Verifiers"""
class MoviesInput(BaseModel):
    movie_name : str = Field(description="Name of the movie to be predicted")

class ModelOutput(BaseModel):
    recommendations: List[str] = Field(description=  "List of recommended movies.")
    poster_paths: List[str] = Field(description= "Poster paths for recommended movies.")


@ app.post("/recommend/",response_model=ModelOutput)
async def recommend(data:MoviesInput):
    """Recommend the movies as per the models suggestion"""

    if model is None or films is None:
        return {"recommendation":[],"poster_paths":[]}
    
    movies = data.movie_name
    try:
        mov_index = films[films['title'] == movies].index[0]
        similarity_row = model[mov_index]
        sorted_score = sorted(list(enumerate(similarity_row)),reverse = True, key = lambda x:x[1])[1:6]

        recommendations = []
        posters = []

        for score in sorted_score:
            movie_id = films.iloc[score[0]].movie_id  
            recommendations.append(films.iloc[score[0]].title)
            posters.append(poster_path(movie_id))

        return {"recommendations":recommendations,"poster_paths":posters}
    
    except Exception as e:
        return f"Exception occured as {e}" 

