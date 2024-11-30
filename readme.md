# Movie Recommender System

This project is a comprehensive movie recommendation system using both collaborative and content-based filtering techniques to provide personalized movie suggestions. The system encompasses a diverse dataset of over 1,000 movies, including both Hindi and English titles, sourced from IMDb and Wikipedia. It is further enriched with metadata from TMDB and OMDB APIs and is deployed as an intuitive web application using Flask.

## Features

- **Hybrid Recommendation Approach**: Combines collaborative filtering and content-based filtering to deliver tailored movie recommendations.

- **Diverse Movie Dataset**: Features a curated dataset of over 1,000 movies, encompassing both Hindi and English films, sourced from IMDb and Wikipedia.

- **Enhanced Metadata**: Integrates additional movie metadata through TMDB and OMDB APIs, enriching the dataset by 20%.

- **User-Friendly Web Application**: Offers an intuitive interface built with Flask and HTML for seamless user interaction.

## Data Collection and Preprocessing

1. **Web Scraping**: Utilized efficient web scraping techniques to gather movie data from IMDb and Wikipedia, resulting in a dataset of over 1,000 movies, including both Hindi and English titles.

2. **API Integration**: Enhanced the dataset by integrating The Movie Database (TMDB) and Open Movie Database (OMDB) APIs, adding comprehensive metadata and increasing the dataset's quality by 20%.

3. **Data Cleaning**: Performed thorough data cleaning to handle missing values, remove duplicates, and ensure consistency across the dataset.

## Recommendation System

- **Collaborative Filtering**: Analyzes user behavior and preferences to facilitate personalized movie recommendations.

- **Content-Based Filtering**: Recommends movies with similar attributes, such as genre, cast, and plot, based on user interests.

## Web Application

- **Frontend**: Developed using Flask, providing interface that allows users to input movie name and receive tailored movie recommendations.

- **Recommendation Output**: Upon providing a movie title, the system suggests approximately 9 similar movies, aiding users in discovering new films aligned with their interests.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Viraj-Mathur/Movie-Recommender-System.git
   cd Movie-Recommender-System
   ```

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python app.py
   ```

   Access the application at `http://127.0.0.1:5000/` in your web browser.

## Usage

1. **Navigate to the Web Application**: Open `http://127.0.0.1:5000/` in your browser.

2. **Input Preferences**: Enter a movie title in the search bar.

3. **Get Recommendations**: Click the "Recommend" button to receive a list of approximately 9 movies similar to the one provided, encompassing both Hindi and English films.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your proposed changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- IMDb and Wikipedia for the initial movie data.
- TMDB and OMDB APIs for additional movie metadata.
- Flask framework for facilitating the web application development.

This project was developed by Viraj Mathur as a comprehensive movie recommendation system integrating multiple data sources and recommendation techniques, catering to a diverse audience with recommendations spanning both Hindi and English movies. 
