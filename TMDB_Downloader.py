# from credentials import API_KEY_V3
import requests
import imdb
import os
from structured_logging import structured_log  # Import structured logging

class TMDBDownloader:
    CONFIG_URL = 'https://api.themoviedb.org/3/configuration?api_key={key}'
    IMG_URL = "https://api.themoviedb.org/3/movie/{imdbid}/images?api_key={key}"

    def __init__(self, api_key):                
        self.api_key = api_key        
        if not self.api_key:
            structured_log('error', "API key not found in environment variables")  # Using structured logging for errors
            raise ValueError("Missing API key")
        try:
            response = requests.get(self.CONFIG_URL.format(key=self.api_key))
            response.raise_for_status()
            config = response.json()
            self.base_url = config["images"]["base_url"]
            self.poster_size = config["images"]["poster_sizes"][3]
            structured_log('info', "TMDBDownloader initialized", base_url=self.base_url, poster_size=self.poster_size)  # Structured logging for initialization
        except requests.RequestException as e:
            structured_log('error', "Error fetching configuration", error=str(e))  # Structured logging for exceptions
            raise

    def _get_movie_ids(self, movie_name: str):
        ia = imdb.IMDb()
        items = ia.search_movie(movie_name)
        movies_dict = {movie.movieID: str(movie) for movie in items}
        structured_log('debug', "Movie IDs fetched", movie_name=movie_name, movie_ids=movies_dict)  # Structured logging for debug information
        return movies_dict

    def _get_poster_url(self, movie_id):
        try:
            response = requests.get(self.IMG_URL.format(key=self.api_key, imdbid=f"tt{movie_id}"))
            response.raise_for_status()
            api_response = response.json()
            poster_paths = api_response.get("posters")
            if not poster_paths:
                structured_log('warning', "No poster path found", movie_id=movie_id)  # Warning log if no poster path found
                return None
            poster_path = poster_paths[0]["file_path"]
            return poster_path
        except requests.RequestException as e:
            structured_log('error', "Error fetching poster URL", movie_id=movie_id, error=str(e))  # Structured logging for exceptions
            return None

    def download_poster(self, movie_name):
        movie_ids = self._get_movie_ids(movie_name)
        for movie_id, movie_name in movie_ids.items():
            poster_path = self._get_poster_url(movie_id)
            if not poster_path:
                continue
            try:
                response = requests.get(self.base_url + self.poster_size + poster_path)
                response.raise_for_status()
                content_type = response.headers['content-type']
                filetype = content_type.split('/')[-1] if '/' in content_type else 'jpg'
                filename = f"poster_{movie_id}.{filetype}"
                structured_log('info', "Poster downloaded", movie_name=movie_name, movie_id=movie_id, filename=filename)  # Structured logging for successful download
                return movie_id, filename, response.content
            except requests.RequestException as e:
                structured_log('error', "Error downloading poster", movie_name=movie_name, movie_id=movie_id, error=str(e))  # Structured logging for exceptions
        return None, None, None

# Usage example:
# if __name__ == "__main__":
#     downloader = TMDBDownloader(API_KEY_V3)
#     movie_id, filename, content = downloader.download_poster("Inception")
#     print(movie_id, filename)
