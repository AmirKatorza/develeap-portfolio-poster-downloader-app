from pymongo import MongoClient
import gridfs
import os
from structured_logging import structured_log  # Importing structured logging utility
# import TMDB_Downloader

class MongoAPI:
    def __init__(self, db_name, collection_name, ip="localhost", port=27017):
        self.client = MongoClient(host=ip, port=port, serverSelectionTimeoutMS=10000)
        self.db = self.client[db_name]
        self.fs = gridfs.GridFS(self.db, collection_name)
        self.collection_files = f"{collection_name}.files"
        structured_log('info', 'MongoAPI initialized', db_name=db_name, collection_name=collection_name)

    def write_image(self, file_name, movie_name, imdb_id, byte_arr):
        try:
            fs_id = self.fs.put(byte_arr, movie_name=movie_name, imdb_id=imdb_id, filename=file_name)
            structured_log('info', 'Data written', file_name=file_name, movie_name=movie_name, imdb_id=imdb_id)
            return {"status": "Success", "data": {'_id': fs_id}}
        except Exception as e:
            structured_log('error', 'Error writing data', error=str(e))
            return {"status": "Error", "error": str(e), "data": None}

    def read_image(self, movie_name):
        try:
            file_id = self.db[self.collection_files].find_one({"movie_name": movie_name}, {"_id": 1})
            if file_id:
                byte_arr = self.fs.get(file_id['_id']).read()
                poster_path = f"./posters_images/{movie_name}.jpeg"
                if not os.path.exists(poster_path):
                    os.makedirs(os.path.dirname(poster_path), exist_ok=True)
                with open(poster_path, 'wb') as file:
                    file.write(byte_arr)
                structured_log('info', 'Image read and stored', movie_name=movie_name, path=poster_path)
                return {"status": "Success", "data": file_id}
            else:
                structured_log('warning', 'Image not found', movie_name=movie_name)
                return {"status": "No action needed", "data": None}
        except Exception as e:
            structured_log('error', 'Error reading image', error=str(e), movie_name=movie_name)
            return {"status": "Error", "error": str(e), "data": None}

    def get_file_id_by_name(self, movie_name):
        try:
            file_id = self.db[self.collection_files].find_one({"movie_name": movie_name}, {"_id": 1})
            return {"status": "Success", "data": file_id}
        except Exception as e:
            structured_log('error', 'Error fetching file ID', error=str(e), movie_name=movie_name)
            return {"status": "Error", "error": str(e), "data": None}

    def del_image(self, movie_name):
        try:
            file_id = self.get_file_id_by_name(movie_name)
            if file_id["data"]:
                self.fs.delete(file_id["data"]['_id'])
                structured_log('info', 'Data deleted', movie_name=movie_name)
                return {"status": "Success", "data": None}
            else:
                structured_log('warning', 'No data to delete', movie_name=movie_name)
                return {"status": "No action needed", "data": None}
        except Exception as e:
            structured_log('error', 'Error deleting data', error=str(e), movie_name=movie_name)
            return {"status": "Error", "error": str(e), "data": None}

    def update_image_file_meta_data(self, movie_name, key_to_update, val_to_update):
        try:
            file_id = self.get_file_id_by_name(movie_name)
            if file_id["data"]:
                mycol = self.db[self.collection_files]
                myquery = {"_id": file_id["data"]['_id']}
                new_values = {"$set": {key_to_update: val_to_update}}
                db_update_response = mycol.update_one(myquery, new_values)
                update_status = 'Successfully Updated' if db_update_response.modified_count > 0 else "Nothing was updated."
                return {"status": update_status, "data": None}
            else:
                return {"status": "No action needed", "data": None}
        except Exception as e:
            structured_log('error', 'Error updating metadata', error=str(e), movie_name=movie_name)
            return {"status": "Error", "error": str(e), "data": None}

# Example usage
if __name__ == '__main__':
    mdb = MongoAPI("movies", "posters")
    response = mdb.read_image("The Equalizer")
    print(response)
