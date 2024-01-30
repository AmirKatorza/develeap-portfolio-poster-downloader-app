import os
import logging
from flask import Flask, request, render_template, redirect, url_for
from Mongodb_API import MongoAPI
from TMDB_Downloader import TMDBDownloader
from mongo_tmdb_logic import mongo_tmdb
from structured_logging import structured_log

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Read the API_KEY from environment variables and initiate the TMDBDownloader class
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("No API_KEY set for TMDBDownloader")
downloader = TMDBDownloader(API_KEY)

# Read the MONGO_IP from environment variables and initiate the MongoAPI class
MONGO_IP = os.environ.get('MONGO_IP', 'localhost')
mdb = MongoAPI("movies", "posters", ip=MONGO_IP)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    show_delete_button = False
    image_src = None

    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        result = mongo_tmdb(mdb, downloader, movie_name)
        structured_log('info', 'Movie search processed', movie_name=movie_name, status=result['status'])

        if result['status'] in ["Added to DB", "Found in DB"]:
            image_binary = result['data']
            if image_binary:
                image_src = f"data:image/jpeg;base64,{image_binary}"
                show_delete_button = True
                message = "Movie found in DB." if result['status'] == "Found in DB" else "Movie added to DB."
            else:
                message = "No poster available for this movie."
        elif result['status'] == "Not Exists":
            message = "Movie not found in TMDB."

    return render_template('search_form.html', image_src=image_src, message=message, show_delete_button=show_delete_button)

@app.route('/delete/<movie_name>', methods=['POST'])
def delete_movie(movie_name):
    response = mdb.del_image(movie_name)
    structured_log('info', 'Movie delete request processed', movie_name=movie_name, status=response['status'])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
