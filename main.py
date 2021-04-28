#!/usr/bin/env python3

import pylast
import spotify.sync as spotify
import requests
import time
import pickle

import secrets

API_KEY = secrets.lastfm["api_key"]
API_SECRET = secrets.lastfm["secret"]

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

spotify = spotify.Client(secrets.spotify["client_id"], secrets.spotify["client_secret"])

lastfm_top_tracks = network.get_user("chandlerswift").get_top_tracks(stream=True, limit=None)

track_data=[]

for i, lastfm_track in enumerate(lastfm_top_tracks):
    try:
        spotify_track = spotify.search(
            f"{lastfm_track.item.artist.name} {lastfm_track.item.title}", types=["track"], limit=1
        ).tracks[0]

        res = requests.get(f"http://localhost:8080/albumPlayCount?albumid={spotify_track.album.id}").json()

        found_track = None
        for spotify_disc in res['data']['discs']:
            for spotify_track_info in spotify_disc['tracks']:
                if spotify_track_info['name'].lower() == lastfm_track.item.title.lower():
                    found_track = spotify_track_info

        if found_track:
            found_track['my_playcount'] = lastfm_track.weight
            track_data.append(found_track)
            print(f"{found_track['name']}: {found_track['my_playcount']}/{found_track['playcount']} ({100*found_track['my_playcount']/found_track['playcount']:.3f}%)")
        else:
            print(f"No track {lastfm_track.item.title} found on album {spotify_track.album.name} (found {[[t['name'] for t in d['tracks']] for d in res['data']['discs']]})")

        time.sleep(2) # I don't think Spotify's going to ban me, but doesn't hurt
                    # to be a little extra careful!
    except Exception as e:
        # Sometimes things crash. This might give me a chance to continue, if I want.
        print(e)
        input("continue? ")

pickle.dump(track_data, open("track_data.pickle", "wb"))
