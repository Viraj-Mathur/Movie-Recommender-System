# api_key = 'c6c09d114effb5caac5eba5a761473a2'
import pandas as pd
import requests
import time
from tqdm.auto import tqdm
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException

# Load your existing dataset
movies_df = pd.read_csv('Hindi_Movies_Dataset_with_TMDB.csv')

# Get API key from environment variable or use the provided one
api_key = os.getenv('TMDB_API_KEY', 'c6c09d114effb5caac5eba5a761473a2')

# Function to get TMDB ID based on movie name
def get_tmdb_id(movie_name):
    try:
        search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}'
        response = requests.get(search_url)
        response.raise_for_status()
        results = response.json().get('results', [])
        return results[0]['id'] if results else None
    except RequestException as e:
        print(f"Error fetching TMDB ID for {movie_name}: {e}")
        return None

# Add TMDB ID to your dataset
print("Adding TMDB IDs to the dataset...")
movies_df['TMDB_ID'] = movies_df['movie_name'].apply(get_tmdb_id)
movies_df = movies_df.dropna(subset=['TMDB_ID'])
movies_df['TMDB_ID'] = movies_df['TMDB_ID'].astype(int)
print(f"Found TMDB IDs for {len(movies_df)} movies.")

# Function to get movie details based on TMDB ID
def get_movie_details(tmdb_id):
    try:
        details_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&append_to_response=genres'
        response = requests.get(details_url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Error fetching movie details for ID {tmdb_id}: {e}")
        return None

# Function to get user reviews based on TMDB ID
def get_user_reviews(tmdb_id):
    reviews = []
    page = 1
    try:
        while True:
            reviews_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/reviews?api_key={api_key}&page={page}'
            response = requests.get(reviews_url)
            response.raise_for_status()
            data = response.json()
            reviews.extend(data.get('results', []))
            if page >= data['total_pages']:
                break
            page += 1
        return reviews
    except RequestException as e:
        print(f"Error fetching reviews for ID {tmdb_id}: {e}")
        return reviews

# Function to process a single movie
def process_movie(row):
    movie_id = row['TMDB_ID']
    movie_name = row['movie_name']
    
    movie_data = None
    reviews_data = []
    
    # Fetch movie details
    movie_details = get_movie_details(movie_id)
    if movie_details:
        genres = [genre['name'] for genre in movie_details.get('genres', [])]
        genres_str = ', '.join(genres)
        movie_data = {
            'movieId': movie_id,
            'title': movie_name,
            'genres': genres_str
        }
    
    # Fetch user reviews
    reviews = get_user_reviews(movie_id)
    for review in reviews:
        reviews_data.append({
            'userId': review['author_details'].get('username', 'unknown'),
            'movieId': movie_id,
            'rating': review['author_details'].get('rating', 'N/A'),
            'timestamp': review.get('created_at', 'N/A')
        })
    
    time.sleep(0.25)  # Respect TMDB API rate limits
    return movie_data, reviews_data

# Process movies using ThreadPoolExecutor
movies_data = []
reviews_data = []

total_movies = len(movies_df)
completed_tasks = 0

print(f"Processing {total_movies} movies...")
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_movie, row) for _, row in movies_df.iterrows()]
    
    with tqdm(total=total_movies, desc="Processing Movies") as pbar:
        for future in as_completed(futures):
            movie_data, movie_reviews = future.result()
            if movie_data:
                movies_data.append(movie_data)
            reviews_data.extend(movie_reviews)
            
            completed_tasks += 1
            pbar.update(1)
            pbar.set_postfix({"Completed": f"{completed_tasks}/{total_movies}"})

print(f"\nProcessed {completed_tasks} out of {total_movies} movies.")

# Convert to DataFrames and save to CSV
movies_df_final = pd.DataFrame(movies_data)
movies_df_final.to_csv('hindi_movie.csv', index=False)

reviews_df_final = pd.DataFrame(reviews_data)
reviews_df_final.to_csv('rating_bollywood.csv', index=False)

print("Files 'hindi_movie.csv' and 'rating_bollywood.csv' have been successfully created.")