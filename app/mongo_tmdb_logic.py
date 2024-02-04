from structured_logging import structured_log  # Importing structured logging utility

def mongo_tmdb(mongo_client, tmdb_client, movie_name):
    # Search for the image in the Mongo database
    mongo_search_result = mongo_client.read_image(movie_name)
    
    if mongo_search_result['status'] == "No action needed":
        structured_log('info', 'Image not found in MongoDB, downloading from TMDB', movie_name=movie_name)
        
        # Download the poster if not found in Mongo database
        imdb_id, file_name, byte_arr = tmdb_client.download_poster(movie_name)
        if (imdb_id != 0) and (file_name is not None) and (byte_arr != 0):
            mongo_client.write_image(file_name, movie_name, imdb_id, byte_arr)
            structured_log('info', 'Image added to MongoDB', movie_name=movie_name, file_name=file_name)
            return {"status": "Added to DB", "data": byte_arr, "file_name": file_name}
        else:
            structured_log('warning', 'Image not found on TMDB', movie_name=movie_name)
            return {"status": "Not Exists", "data": None, "file_name": None}

    elif mongo_search_result['status'] == "Success":
        structured_log('info', 'Image found in MongoDB', movie_name=movie_name)
        return {"status": "Found in DB", "data": mongo_search_result['data'], "file_name": movie_name + ".jpeg"}

    else:
        structured_log('error', 'Unexpected status from MongoDB', status=mongo_search_result['status'], movie_name=movie_name)
        return {"status": "Error", "data": None, "file_name": None}


# Example usage
if __name__ == '__main__':
    from mongodb_api import MongoAPI
    from tmdb_downloader import TMDBDownloader
    mongo_client = MongoAPI("movies", "posters")
    tmdb_client = TMDBDownloader()
    result = mongo_tmdb(mongo_client, tmdb_client, "The Equalizer")
    print(result)
