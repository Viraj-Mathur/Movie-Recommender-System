# Importing the necessary libraries and modules
from flask import Flask, request, render_template, jsonify
from flask_cors import cross_origin
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches
from tmdbv3api import TMDb, Movie
import requests
import json

# Initialising flask app
app = Flask(__name__)

# load the data
df = pd.read_csv('Data/preprocessed_data.csv')
# load cache data
df_cache = pd.read_csv('Data/cache_data.csv')
# storing movie title into list
movie_list = list(df['movie_title'])

# Load new models' data
p_df = pd.read_csv('preprocessed_movies.csv')
popular_movies = pd.read_csv('top_10_popular_movies.csv')
final_df = pd.read_csv('final_movies.csv')

# # Load Bollywood data
# cosine_sim_bollywood = np.load('cosine_sim_bollywood.npy')
# user_similarity_hindi = pd.read_pickle('user_similarity_hindi.pkl')
# item_similarity_hindi = pd.read_pickle('item_similarity_df_hindi.pkl')
# bollywood_df = pd.read_csv('final_movies_hindi.csv')  # Assuming you have this dataset for Bollywood movies

# Load Bollywood data
cosine_sim_bollywood = np.load('cosine_sim_bollywood_new.npy')
user_similarity_hindi = pd.read_pickle('user_similarity_hindi.pkl')
item_similarity_hindi = pd.read_pickle('item_similarity_df_hindi.pkl')
bollywood_df = pd.read_csv('final_movies_hindi.csv')


# Cleaning the 'Title' column to ensure no NaN or float values
final_df['Title'] = final_df['Title'].astype(str).fillna('')
bollywood_df['Title'] = bollywood_df['Title'].astype(str).fillna('').str.lower()

cosine_sim = np.load('cosine_sim.npy')
user_similarity = pd.read_pickle('user_similarity.pkl')
item_similarity_df = pd.read_pickle('item_similarity_df.pkl')

# creating TMDB Api Object
tmdb = TMDb()

tmdb.api_key = 'c6c09d114effb5caac5eba5a761473a2'

# OMDB API key
omdb_api_key = '338007de'


# This Function take movie name list and return their Poster link, Tag Line and Title into dictionary
def get_poster_link(title_list):
    """
    This Function take movie name list and return their Poster link, Tag line and Title into dictionary.
    """
    # TMDB Movie Api Object
    tmdb_movie = Movie()

    # Storing data in to dictionary
    dic_data = {"Movie_Title": [], "Poster_Links": [], "Tag_Line": []}

    for title in title_list:

        # checking given movie is present in our cache database or not.
        r_df = df_cache[df_cache['Title'] == title]
        try:
            # if given movie is found in our cache database then run this part
            if len(r_df) >= 1:
                dic_data["Movie_Title"].append(r_df['Movie_Title'].values[0])
                dic_data["Poster_Links"].append(r_df['Poster_Links'].values[0])
                dic_data["Tag_Line"].append(r_df['Tag_Line'].values[0])

            # otherwise retrieve the data from tmdbi api
            else:
                result = tmdb_movie.search(title)
                movie_id = result[0].id
                response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id, tmdb.api_key))
                data_json = response.json()

                # Fetching movie title and poster link
                movie_title = data_json['title']
                movie_poster_link = "https://image.tmdb.org/t/p/original" + data_json['poster_path']
                movie_tag_line = data_json['tagline']

                # Appending movie title and poster link into dictionary
                dic_data['Movie_Title'].append(movie_title)
                dic_data['Poster_Links'].append(movie_poster_link)
                dic_data['Tag_Line'].append(movie_tag_line)
        except Exception as e:
            print(f"Error fetching data for {title}: {e}")


    return dic_data


# # New recommendation functions


# def preprocess_bollywood_df():
#     global bollywood_df, cosine_sim_bollywood
    
#     # Convert titles to lowercase and remove leading/trailing whitespace
#     bollywood_df['Title'] = bollywood_df['Title'].str.lower().str.strip()
    
#     # Remove duplicates, keeping the first occurrence
#     bollywood_df = bollywood_df.drop_duplicates(subset='Title', keep='first')
    
#     # Reset the index
#     bollywood_df = bollywood_df.reset_index(drop=True)
    
#     # Recalculate cosine similarity matrix if necessary
#     # This step depends on how you initially calculated cosine_sim_bollywood
#     # If it's based on features in bollywood_df, you might need to recalculate it
#     # For example:
#     # from sklearn.feature_extraction.text import CountVectorizer
#     # from sklearn.metrics.pairwise import cosine_similarity
#     # 
#     # cv = CountVectorizer()
#     # count_matrix = cv.fit_transform(bollywood_df['combined_features'])
#     # cosine_sim_bollywood = cosine_similarity(count_matrix)
    
#     print(f"Processed Bollywood dataframe shape: {bollywood_df.shape}")
#     print(f"Processed cosine_sim_bollywood shape: {cosine_sim_bollywood.shape}")

# # Call this function after loading the Bollywood data
# preprocess_bollywood_df()

def get_recommendation_content_based(title, category='both'):
    title = title.lower()
    try:
        if category == 'bollywood':
            df = bollywood_df
            sim_matrix = cosine_sim_bollywood
        elif category == 'hollywood':
            df = final_df
            sim_matrix = cosine_sim
        else:  # 'both'
            df = pd.concat([final_df, bollywood_df], ignore_index=True)
            # We'll search in both datasets and combine results
            hollywood_matches = get_close_matches(title, final_df['Title'].values, n=3, cutoff=0.6)
            bollywood_matches = get_close_matches(title, bollywood_df['Title'].values, n=3, cutoff=0.6)
            
            if hollywood_matches and bollywood_matches:
                # If found in both, use the closest match
                if get_close_matches(title, hollywood_matches + bollywood_matches, n=1, cutoff=0.6)[0] in hollywood_matches:
                    df = final_df
                    sim_matrix = cosine_sim
                else:
                    df = bollywood_df
                    sim_matrix = cosine_sim_bollywood
            elif hollywood_matches:
                df = final_df
                sim_matrix = cosine_sim
            elif bollywood_matches:
                df = bollywood_df
                sim_matrix = cosine_sim_bollywood
            else:
                print(f"No close matches found for {title}")
                return []

        close_matches = get_close_matches(title, df['Title'].values, n=3, cutoff=0.6)
        if not close_matches:
            print(f"No close matches found for {title}")
            return []
        title = close_matches[0]
        idx = df['Title'][df['Title'] == title].index[0]
        sim_scores = list(enumerate(sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[0:16]
        return [df['Title'].iloc[i[0]] for i in sim_scores]
    except Exception as e:
        print(f"Error during content-based recommendation for {title}: {e}")
        return []



def get_recommendation_collaborative(movie_name, ratings, similarity_df):
    try:
        similar_score = similarity_df[movie_name] * (ratings - 2.5)
        similar_score = similar_score.sort_values(ascending=False)
        return similar_score.head(10).index.tolist()
    except Exception as e:
        print(f"Error during collaborative filtering for {movie_name}: {e}")
        return []

@app.route('/', methods=['GET'])  # route to display the Home Page
@cross_origin()
def home():
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])  # route to show the recommendation in web UI
@cross_origin()
# This function take movie name from user, and return 10 similar type of movies.


def recommendation():
    if request.method == 'POST':
        try:
            title = request.form['search'].lower()
            category = request.form.get('category', 'both').lower()
            
            suggested_movie_list = get_recommendation_content_based(title, category)
            
            if not suggested_movie_list:
                return render_template("error.html")

            poster_title_link = get_poster_link(suggested_movie_list)
            return render_template('recommended.html', output=poster_title_link)

        except Exception as e:
            print(f"Error during recommendation: {e}")
            return render_template("error.html")
        
@app.route('/popular_movies', methods=['GET'])
@cross_origin()
def get_popular_movies():
    return jsonify(popular_movies.to_dict(orient='records'))

@app.route('/collaborative_user', methods=['POST'])
@cross_origin()


def collaborative_user_recommendation():
    data = request.json
    movie_name = data['movie_name']
    ratings = data['ratings']
    category = data.get('category', 'both').lower()
    if category == 'bollywood':
        recommendations = get_recommendation_collaborative(movie_name, ratings, user_similarity_hindi)
    elif category == 'hollywood':
        recommendations = get_recommendation_collaborative(movie_name, ratings, user_similarity)
    else:  # 'both'
        recommendations_hollywood = get_recommendation_collaborative(movie_name, ratings, user_similarity)
        recommendations_bollywood = get_recommendation_collaborative(movie_name, ratings, user_similarity_hindi)
        recommendations = list(set(recommendations_hollywood + recommendations_bollywood))[:10]
    return jsonify(recommendations)

@app.route('/collaborative_item', methods=['POST'])
@cross_origin()



def collaborative_item_recommendation():
    data = request.json
    movie_name = data['movie_name']
    ratings = data['ratings']
    category = data.get('category', 'both').lower()
    if category == 'bollywood':
        recommendations = get_recommendation_collaborative(movie_name, ratings, item_similarity_hindi)
    elif category == 'hollywood':
        recommendations = get_recommendation_collaborative(movie_name, ratings, item_similarity_df)
    else:  # 'both'
        recommendations_hollywood = get_recommendation_collaborative(movie_name, ratings, item_similarity_df)
        recommendations_bollywood = get_recommendation_collaborative(movie_name, ratings, item_similarity_hindi)
        recommendations = list(set(recommendations_hollywood + recommendations_bollywood))[:10]
    return jsonify(recommendations)

if __name__ == '__main__':
    print("App is running")
    app.run(debug=True)


