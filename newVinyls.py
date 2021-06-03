
"""

                        New Vinyl Releases

                     Written By: Ben Morrison

Description: A program that grabs new vinyl releases and matches them to
             my Spotify artists.

"""

# IMPORTS
import argparse
import praw
from prawcore import NotFound, PrawcoreException
import json
from pymongo import MongoClient
import os
import sys
import datetime as dt
import re
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv


# FUNCTIONS

"""
Connect to the databases.
"""
def connectToDatabases():
    client = MongoClient(os.environ.get("MONGO_CONNECTION"))

    artist_db = client["artists"]
    artist_collection = artist_db["artists"]

    vinyl_db = client["vinyls"]
    vinyl_collection = vinyl_db["vinyl_releases"]

    return artist_collection, vinyl_collection

"""
Connect to Twilio (used for SMS messages).
"""
def connectToTwilio():
    return Client(os.environ.get("TWILIO_ACCOUNT_ID"), os.environ.get("TWILIO_AUTH_TOKEN"))


"""
Convert UNIX time to readable format
"""
def convertTime(object):
    return dt.datetime.fromtimestamp(object).strftime("%m-%d-%Y %H:%M:%S")


"""
Clean up the posts scraped from r/VinylReleases.
"""
def cleanPosts(posts):

    titles = ["Title","Date Created","Upvotes","ID",\
                "URL","Comment Count","Text"]

    reformatted = {}
    counter = 1
    for post in posts:
        content = [post.title, convertTime(post.created), post.score,\
                   post.id, post.url, post.num_comments, post.selftext]
        reformatted["Post "+str(counter)] = { title:value for title, value in zip(titles,content) }
        counter += 1

    return reformatted


"""
Grabs any new vinyls that were posted.
"""
def grabNewVinyls(limit):

    # grab *limit* vinyls from subreddit
    new_posts = subreddit.new(limit = limit)
    posts = cleanPosts(new_posts)
    post_ids = [post['ID'] for post in posts.values()]
    lvid = None


    for id in post_ids:
        if vinyls.count_documents({ 'post_id': id }, limit = 1):
            lvid = id
            break


    if not lvid:
        print(str(limit)+" wasn't enough...grabbing "+str(limit*2))
        return grabNewVinyls(limit*2)

    end = post_ids.index(lvid)

    slice_keys = []
    for i in range(1, end+1):
        slice_keys.append('Post '+str(i))

    return {key: posts[key] for key in posts.keys() & slice_keys}



"""
Sends a text message to my phone with a link to the URL for purchasing the record.
"""
def sendAlert(vinyl, artist):

    sms_client.messages.create(to=os.environ.get("MY_CELL_NUMBER"),
                           from_=os.environ.get("MY_TWILIO_NUMBER"),
                           body="Here's a record that you may be interested in.\nArtist: "+artist+"\nURL: "+vinyl['URL'])


"""
Checks if a vinyl artist matches a Spotify artist. If so, send me an alert.
"""
def checkAndNotify(vinyl):

    # for now, check against the MONGO artists database and
    # print if there is a match

    title = vinyl['Title']
    print("Checking post for artist match...")

    for artist in artist_names:

        if re.search(artist.lower(), title.lower()):         # --> check for artist match anywhere in title
            print("Match found - sending alert.")
            sendAlert(vinyl, artist)
            return True

    print("No match found!")
    return False




# MAIN

if __name__ == '__main__':


    print("Loading environment variables...")
    load_dotenv(find_dotenv())

    dt_current = dt.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    print("\n\nHourly Check\n\n"+dt_current+"\n\n")

    print("Connecting to databases...")
    artists, vinyls = connectToDatabases()

    print("Connecting to Twilio...")
    sms_client = connectToTwilio()

    print("Forming list of Spotify artists...")
    artist_list = artists.find({})
    artist_names = [artist['name'] for artist in artist_list]

    # Reddit Login
    print("Logging in to Reddit...")
    reddit = praw.Reddit(client_id = os.environ.get("REDDIT_CLIENT_ID"), \
                         client_secret = os.environ.get("REDDIT_CLIENT_SECRET"), \
                         user_agent = os.environ.get("REDDIT_APP_NAME"), \
                         username = os.environ.get("REDDIT_USERNAME"), \
                         password = os.environ.get("REDDIT_PASSWORD"))

    print("Accessing subreddit...")
    subreddit = reddit.subreddit("VinylReleases")

    print("Looking for new vinyl releases...")
    # Grab New Posts
    new_vinyls = grabNewVinyls(10)

    if not new_vinyls:
        print("No new vinyls found.")
        sys.exit()

    for vinyl in new_vinyls.values():
        sent_sms = checkAndNotify(vinyl)
        print("Inserting vinyl from post "+vinyl['ID']+' into database.')
        vinyls.insert_one({'post_id': vinyl['ID'], 'URL': vinyl['URL'], 'sentMessage': sent_sms})
