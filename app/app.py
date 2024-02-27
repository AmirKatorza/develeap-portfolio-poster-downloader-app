import os
import base64
from flask import Flask, request, render_template, redirect, url_for
from mongodb_api import MongoAPI
from tmdb_downloader import TMDBDownloader
from mongo_tmdb_logic import mongo_tmdb
from structured_logging import structured_log

app = Flask(__name__)

# Read the API_KEY from environment variables and initiate the TMDBDownloader class
API_KEY = os.getenv('API_KEY', '').strip()
if not API_KEY:
    raise ValueError("No API_KEY set for TMDBDownloader")
downloader = TMDBDownloader(API_KEY)

# Determine the MongoDB connection string based on environment variables
MONGODB_HOSTS = os.getenv('MONGODB_HOSTS', 'localhost').strip()
DATABASE = os.getenv('DATABASE', 'movies').strip()

if (MONGODB_HOSTS == 'localhost') or (MONGODB_HOSTS == 'db-mongo'):
    MONGO_IP = MONGODB_HOSTS
else:
    ROOT_USER = os.getenv('ROOT_USER', '').strip()
    ROOT_PASSWORD = os.getenv('ROOT_PASSWORD', '').strip()
    if (not ROOT_PASSWORD) or (not ROOT_USER):
        raise ValueError("No ROOT_USER or ROOT_PASSWORD set for MongoAPI")
    MONGO_IP = f"mongodb://{ROOT_USER}:{ROOT_PASSWORD}@{MONGODB_HOSTS}"

# Log the MONGO_IP variable and initiate the MongoAPI class
structured_log('info', 'Initializing MongoAPI', mongo_ip=MONGO_IP)
mdb = MongoAPI(DATABASE, "posters", ip=MONGO_IP)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    show_delete_button = False
    image_src = None
    movie_name = ""  # Initialize movie_name to pass to template for delete functionality

    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        result = mongo_tmdb(mdb, downloader, movie_name)
        structured_log('info', 'Movie search processed', movie_name=movie_name, status=result['status'])

        if result['status'] in ["Added to DB", "Found in DB"]:
            # Retrieve the binary data of the image
            image_binary = result['data']
            if image_binary:
                # Convert the binary data to a Base64-encoded string
                image_base64 = base64.b64encode(image_binary).decode('utf-8')
                image_src = f"data:image/jpeg;base64,{image_base64}"
                show_delete_button = True
                message = "Movie found in DB." if result['status'] == "Found in DB" else "Movie added to DB."
            else:
                message = "No poster available for this movie."
        elif result['status'] == "Not Exists":
            message = "Movie not found in TMDB."

    return render_template('search_form.html', image_src=image_src, message=message, show_delete_button=show_delete_button, movie_name=movie_name)

@app.route('/delete/<movie_name>', methods=['POST'])
def delete_movie(movie_name):
    response = mdb.del_image(movie_name)
    structured_log('info', 'Movie delete request processed', movie_name=movie_name, status=response['status'])
    return redirect(url_for('index'))

@app.after_request
def log_request_info(response):
    structured_log('info', 'Request processed', request_method=request.method, request_url=request.url, response_status=response.status_code)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
