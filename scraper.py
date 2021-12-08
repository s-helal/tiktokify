import requests
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# set up authentication credentials
client_id = '65580595dc324a1cb2e890e9800479c4'
client_secret = '20a9994294354eae8ef6cc4ea75e48a3'

client_credentials_manager = SpotifyClientCredentials(client_id,client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# extract all features of all (over 100) songs on a playlist into a dataframe
def playlist_to_df(username, playlist_id, file_name, tracks_exist = True):
    '''
    Scrapes a given playlist from Spotify and saves songs in a dataframe, then CSV
    Inputs: playlist creator ID, playlist ID, indictor of tracks key in JSON
    Output: none, saves songs to a csv in the ./data directory
    '''
    # format username
    username = "spotify:user:" + username
    playlist_id = "spotify:playlist:" + playlist_id
    
    # get JSON of playlist metadata for first page of songs
    spotipy_response = sp.user_playlist_tracks(username,playlist_id)
    
    if tracks_exist:
        spotipy_response = spotipy_response['tracks']
    
    # record track information
    results = spotipy_response['items']
    
    # while there is a next page of songs (100 songs per page)
    while spotipy_response['next']:
        # replace previous page information with new page
        spotipy_response = sp.next(spotipy_response)
        
        # add track information to list
        results.extend(spotipy_response['items']) 
    
    first = True
    
    # loop through tracks
    for item in results:
        try:
            track = item['track']
            
            # extract id and other features from track metadata and store in dictionary
            ids = track['id']
            
            artist_list = []
            for artist in track['artists']:
                artist_list.append(artist['name'])

            new_row = {'id':[track['id']], 'title':[track['name']], 'all_artists':[artist_list],
                       'popularity':[track['popularity']], 
                       'release_date':[track['album']['release_date']]}

            # extract given features for track and add to dictionary
            features = sp.audio_features(ids)[0]
            
            for key in features:
                new_row[key] = [features[key]]
            
            # turn dictionary into dataframe
            new_df = pd.DataFrame(new_row)
            
            # create new dataframe or add to existing dataframe
            if first:
                features_df = new_df
                first = False
            else:
                features_df = pd.concat([features_df, new_df], ignore_index = True)
                
        except:
            continue
            
    # drop unnecessary features
    features_df = features_df.drop(['speechiness', 'type', 'uri', 'track_href', 'analysis_url'], axis=1)
    
    # save dataframe with all songs and desired features to csv
    if not os.path.isdir('data'):
        os.mkdir('data')
    features_df.to_csv("data/" + file_name + ".csv", index = False)