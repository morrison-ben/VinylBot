
"""
                        My Spotify Artists

                     Written By: Ben Morrison

Description: A program that maintains a list of my Spotify artists. Updates daily
             to add new artists to the list.

"""


# IMPORTS
import spotipy
import spotipy.util as util
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv


# FUNCTIONS

"""
Connect to the database.
"""
def connectToDatabase():
    client = MongoClient(os.environ.get("MONGO_CONNECTION"))
    db = client["artists"]
    collection = db["artists"]
    dbnames = client.list_database_names()

    if 'artists' in dbnames:
        return collection, True

    return collection, False


"""
Add an artist to the local set.
"""
def addArtistToSet(results):
    for item in results['items']:
        track = item['track']
        my_artists.add(track['artists'][0]['name'])


"""
Update the database to add new artists.
"""
def updateArtists():
    ctr = 0
    for artist in my_artists:
        if not exists:
            db.insert_one({'name': artist})
            print("Added artist: "+artist)
            ctr+=1
        else:
            match = db.find_one({'name': artist})
            if not match:
                db.insert_one({'name': artist})
                print("Added artist: "+artist)
                ctr+=1

    return ctr


# MAIN
if __name__ == '__main__':

    print("Loading environment variables...")
    load_dotenv(find_dotenv())

    db, exists = connectToDatabase()

    scope = 'user-library-read'
    username = os.environ.get("SPOTIFY_USERNAME")

    # handle authentication prompt
    token = util.prompt_for_user_token(username, scope)

    # add artists to local set
    my_artists = set()
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_saved_tracks()
        addArtistToSet(results)
        while results['next']:
            results = sp.next(results)
            addArtistToSet(results)

        # update the database
        print("Running update...")
        ctr = updateArtists()
        if ctr > 0:
            print("Update finished! Added "+str(ctr)+ " new artists.")
        else:
            print("Update finished! No new artists were added.")

    else:
        print("Can't get token for", username)
