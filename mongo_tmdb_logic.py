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
            new_mongo_search = mongo_client.read_image(movie_name)
            new_mongo_search['status'] = "Added to DB"
            new_mongo_search['file_name'] = file_name
            structured_log('info', 'Image added to MongoDB', movie_name=movie_name, file_name=file_name)
            return new_mongo_search
        else:
            structured_log('warning', 'Image not found on TMDB', movie_name=movie_name)
            return {"status": "Not Exists", "data": None, "file_name": None}

    structured_log('info', 'Image found in MongoDB', movie_name=movie_name)
    mongo_search_result['status'] = "Found in DB"
    mongo_search_result['file_name'] = movie_name + ".jpeg"
    return mongo_search_result

# Example usage
# mongo_client = MongoAPI("movies", "posters")
# tmdb_client = TMDBDownloader()
# result = mongo_tmdb(mongo_client, tmdb_client, "The Equalizer")
# print(result)
