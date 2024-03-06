from pymongo import MongoClient
import gridfs
from flask import url_for
from structured_logging import structured_log  # Importing structured logging utility

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
                structured_log('info', 'Image read from DB', movie_name=movie_name)
                return {"status": "Success", "data": byte_arr, "_id": file_id['_id']}
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

    def get_all_posters(self):
        posters = []
        for poster in self.db[self.collection_files].find():
            movie_name = poster.get('movie_name')
            file_id = poster.get('_id')
            # Construct a URL or method to get the image by file ID
            image_src = url_for('image', file_id=str(file_id))  # Example route for serving images
            posters.append({'movie_name': movie_name, 'image_src': image_src, 'file_id': file_id})
        return posters

# Example usage
if __name__ == '__main__':
    mdb = MongoAPI("movies", "posters")
    response = mdb.read_image("The Equalizer")
    print(response)