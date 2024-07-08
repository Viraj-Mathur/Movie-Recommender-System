import pandas as pd
import requests
import time
from tqdm import tqdm

# Load your existing dataset
movies_df = pd.read_csv('Hindi_Movies_Dataset_with_TMDB.csv')

# Function to get TMDB ID based on movie name
def get_tmdb_id(movie_name, api_key):
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}'
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]['id']
    return None

# Add TMDB ID to your dataset
api_key = 'c6c09d114effb5caac5eba5a761473a2'
movies_df['TMDB_ID'] = movies_df['movie_name'].apply(lambda x: get_tmdb_id(x, api_key))
movies_df = movies_df.dropna(subset=['TMDB_ID'])
movies_df['TMDB_ID'] = movies_df['TMDB_ID'].astype(int)

# Function to get movie details based on TMDB ID
def get_movie_details(tmdb_id, api_key):
    details_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&append_to_response=genres'
    response = requests.get(details_url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to get user reviews based on TMDB ID
def get_user_reviews(tmdb_id, api_key):
    reviews_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/reviews?api_key={api_key}'
    response = requests.get(reviews_url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

# Collect movie details and user reviews
movies_data = []
reviews_data = []

for _, row in tqdm(movies_df.iterrows(), total=movies_df.shape[0], desc='Processing Movies'):
    movie_id = row['TMDB_ID']
    movie_name = row['movie_name']
    
    # Fetch movie details
    movie_details = get_movie_details(movie_id, api_key)
    if movie_details:
        genres = [genre['name'] for genre in movie_details.get('genres', [])]
        genres_str = ', '.join(genres)
        movies_data.append({
            'movieId': movie_id,
            'title': movie_name,
            'genres': genres_str
        })
    
    # Fetch user reviews
    reviews = get_user_reviews(movie_id, api_key)
    for review in reviews:
        reviews_data.append({
            'userId': review['author_details'].get('username', 'unknown'),
            'movieId': movie_id,
            'rating': review['author_details'].get('rating', 'N/A'),
            'timestamp': review.get('created_at', 'N/A')
        })
    
    # Respect TMDB API rate limits
    time.sleep(0.25)  # Sleep for 250ms

# Convert to DataFrames and save to CSV
movies_df_final = pd.DataFrame(movies_data)
movies_df_final.to_csv('hindi_movie.csv', index=False)

reviews_df_final = pd.DataFrame(reviews_data)
reviews_df_final.to_csv('rating_bollywood.csv', index=False)

print("Files 'hindi_movie.csv' and 'rating_bollywood.csv' have been successfully created.")
